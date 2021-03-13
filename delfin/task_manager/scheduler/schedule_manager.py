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
from oslo_config import cfg
from oslo_log import log
from oslo_utils import uuidutils

from delfin import context
from delfin.task_manager.scheduler import scheduler
from delfin.task_manager.scheduler.schedulers.telemetry import \
    failed_telemetry_job
from delfin.task_manager.scheduler.schedulers.telemetry import telemetry_job

LOG = log.getLogger(__name__)
CONF = cfg.CONF

telemetry_opts = [
    cfg.IntOpt('periodic_task_schedule_interval', default=180,
               help='default interval (in sec) for the periodic scan for '
                    'failed task scheduling'),
    cfg.IntOpt('failed_task_schedule_interval', default=240,
               help='default interval (in sec) interval in sec for periodic '
                    'scan for failed task scheduling'),
    cfg.IntOpt('max_failed_task_retry_count', default=5,
               help='default value (in integer) for maximum number of retries '
                    'for failed task execution'),
]
CONF.register_opts(telemetry_opts, "TELEMETRY")
telemetry = CONF.TELEMETRY


class SchedulerManager(object):
    def __init__(self):
        self.schedule = scheduler.Scheduler.get_instance()

    def start(self):
        """ Initialise the schedulers for collection and failed tasks
        """
        ctxt = context.get_admin_context()
        try:
            # # While initiating scheduler, delete failed task list already
            # # in db as those jobs would not be meaningful due to restart
            # failed_task_list = db.failed_task_get_all(ctxt)
            # for failed_task in failed_task_list:
            #     db.failed_task_delete(ctxt, failed_task['id'])

            # # Reset last run time of tasks to restart scheduling
            # task_list = db.task_get_all(ctxt)
            # for task in task_list:
            #     db.task_update(ctxt, task['id'], {'last_run_time': None})

            # Create a job for periodic scheduling
            
            periodic_scheduler_job_id = uuidutils.generate_uuid()
            self.schedule.add_job(
                telemetry_job.TelemetryJob(), 'interval', args=[ctxt],
                seconds=telemetry.periodic_task_schedule_interval,
                next_run_time=datetime.now(),
                id=periodic_scheduler_job_id)

            # Create a job for failed task scheduling
            periodic_failed_task_schedule_id = uuidutils.generate_uuid()
            self.schedule.add_job(
                failed_telemetry_job.ScheduleFailedTask(), 'interval',
                args=[ctxt], seconds=telemetry.failed_task_schedule_interval,
                next_run_time=datetime.now(),
                id=periodic_failed_task_schedule_id)
        except Exception as e:
            LOG.error("Failed to initialize periodic tasks for performance "
                      "collection, reason: %s.", six.text_type(e))
        else:
            # start the scheduler
            self.schedule.start()