# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime

import six
from apscheduler.schedulers.background import BackgroundScheduler
from oslo_log import log
from oslo_utils import importutils
from oslo_utils import uuidutils

from delfin import context
from delfin import service
from delfin import utils
from delfin.leader_election.distributor.failed_task_distributor\
    import FailedTaskDistributor
from delfin.leader_election.distributor.task_distributor \
    import TaskDistributor

LOG = log.getLogger(__name__)

SCHEDULER_BOOT_JOBS = [
    TaskDistributor.__module__ + '.' + TaskDistributor.__name__,
    FailedTaskDistributor.__module__ + '.' + FailedTaskDistributor.__name__
]


@six.add_metaclass(utils.Singleton)
class SchedulerManager(object):
    def __init__(self, scheduler=None):
        if not scheduler:
            scheduler = BackgroundScheduler()
        self.scheduler = scheduler
        self.scheduler_started = False

        self.boot_jobs = dict()
        self.boot_jobs_scheduled = False
        self.ctx = context.get_admin_context()

    def start(self):
        """ Initialise the schedulers for periodic job creation
        """
        if not self.scheduler_started:
            self.scheduler.start()
            self.scheduler_started = True

    def schedule_boot_jobs(self):
        if not self.boot_jobs_scheduled:
            try:
                for job in SCHEDULER_BOOT_JOBS:
                    job_class = importutils.import_class(job)
                    job_instance = job_class(self.ctx)

                    # Create a jobs for periodic scheduling
                    job_id = uuidutils.generate_uuid()
                    self.scheduler.add_job(job_instance, 'interval',
                                           seconds=job_class.job_interval(),
                                           next_run_time=datetime.now(),
                                           id=job_id)
                    # book keeping of jobs
                    self.boot_jobs[job_id] = job_instance

            except Exception as e:
                # TODO: Currently failure of scheduler is failing task manager
                #  start flow, it is logged and ignored.
                LOG.error("Failed to initialize periodic tasks, reason: %s.",
                          six.text_type(e))
                raise e
        # Recover the job in db
        self.recover_job()
        # Start the consumer of job creation message
        job_generator = service. \
            TaskService.create(binary='delfin-task',
                               topic='JobGenerator',
                               manager='delfin.'
                                       'leader_election.'
                                       'distributor.'
                                       'perf_job_manager.'
                                       'PerfJobManager',
                               coordination=True)
        service.serve(job_generator)

    def stop(self):
        """Cleanup periodic jobs"""

        for job_id, job in self.boot_jobs.items():
            self.scheduler.remove_job(job_id)
            job.stop()
        self.boot_jobs.clear()
        self.boot_jobs_scheduled = False

    def get_scheduler(self):
        return self.scheduler

    def recover_job(self):
        # TODO: would be implement when implement the consistent hashing
        pass
