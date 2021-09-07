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
from oslo_utils import uuidutils

from delfin import context
from delfin import db
from delfin import service
from delfin import utils
from delfin.coordination import ConsistentHashing
from delfin.leader_election.distributor.task_distributor \
    import TaskDistributor
from delfin.task_manager import metrics_rpcapi as task_rpcapi

LOG = log.getLogger(__name__)


@six.add_metaclass(utils.Singleton)
class SchedulerManager(object):

    GROUP_CHANGE_DETECT_INTERVAL_SEC = 30

    def __init__(self, scheduler=None):
        if not scheduler:
            scheduler = BackgroundScheduler()
        self.scheduler = scheduler
        self.scheduler_started = False
        self.ctx = context.get_admin_context()
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.watch_job_id = None

    def start(self):
        """ Initialise the schedulers for periodic job creation
        """
        if not self.scheduler_started:
            self.scheduler.start()
            self.scheduler_started = True

    def on_node_join(self, event):
        # A new node joined the group, all the job would be re-distributed.
        # If the job is already on the node, it would be ignore and would
        # not be scheduled again
        LOG.info('Member %s joined the group %s' % (event.member_id,
                                                    event.group_id))
        # Get all the jobs
        tasks = db.task_get_all(self.ctx)
        distributor = TaskDistributor(self.ctx)
        partitioner = ConsistentHashing()
        partitioner.start()
        for task in tasks:
            # Get the specific executor
            origin_executor = task['executor']
            # If the target executor is different from current executor,
            # remove the job from old executor and add it to new executor
            new_executor = partitioner.get_task_executor(task['id'])
            if new_executor != origin_executor:
                LOG.info('Re-distribute job %s from %s to %s' %
                         (task['id'], origin_executor, new_executor))
                self.task_rpcapi.remove_job(self.ctx, task['id'],
                                            task['executor'])
            distributor.distribute_new_job(task['id'])
        partitioner.stop()

    def on_node_leave(self, event):
        LOG.info('Member %s left the group %s' % (event.member_id,
                                                  event.group_id))
        filters = {'executor': event.member_id.decode('utf-8')}
        re_distribute_tasks = db.task_get_all(self.ctx, filters=filters)
        distributor = TaskDistributor(self.ctx)
        for task in re_distribute_tasks:
            distributor.distribute_new_job(task['id'])

    def schedule_boot_jobs(self):
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
        partitioner = ConsistentHashing()
        partitioner.start()
        partitioner.register_watcher_func(self.on_node_join,
                                          self.on_node_leave)
        self.watch_job_id = uuidutils.generate_uuid()
        self.scheduler.add_job(partitioner.watch_group_change, 'interval',
                               seconds=self.GROUP_CHANGE_DETECT_INTERVAL_SEC,
                               next_run_time=datetime.now(),
                               id=self.watch_job_id)

    def stop(self):
        """Cleanup periodic jobs"""
        if self.watch_job_id:
            self.scheduler.remove_job(self.watch_job_id)

    def get_scheduler(self):
        return self.scheduler

    def recover_job(self):
        all_tasks = db.task_get_all(self.ctx)
        distributor = TaskDistributor(self.ctx)
        for task in all_tasks:
            distributor.distribute_new_job(task['id'])
