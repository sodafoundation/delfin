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
from oslo_log import log
from oslo_config import cfg

from delfin import db
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.scheduler.schedulers.\
    telemetry.failed_performance_collection_handler import \
    FailedPerformanceCollectionHandler
from delfin.task_manager.tasks import telemetry
from oslo_utils import uuidutils
from delfin.task_manager.scheduler import scheduler

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
CONF.register_opts(telemetry_opts)

LOG = log.getLogger(__name__)


class PerformanceCollectionHandler(object):
    def __init__(self):
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.scheduler_instance = scheduler.Scheduler.get_instance()

    def __call__(self, ctx, task_id):
        # Handles performance collection from driver and dispatch
        try:
            task = db.task_get(ctx, task_id)
            LOG.debug('Collecting performance metrics for task id: %s'
                      % task['id'])
            current_time = int(datetime.utcnow().timestamp())
            db.task_update(ctx, task_id, {'last_run_time': current_time})

            # collect the performance metrics from driver and push to
            # prometheus exporter api
            # starttime and endtime are epoch time in mili seconds
            start_time = current_time * 1000
            end_time = start_time + task['interval'] * 10000
            self.task_rpcapi.collect_telemetry(ctx, task['storage_id'],
                                               telemetry.TelemetryTask.
                                               __module__ + '.' +
                                               'PerformanceCollectionTask',
                                               task['args'],
                                               start_time, end_time)
        except Exception as e:
            LOG.error("Failed to collect performance metrics for "
                      "task id :{0}, reason:{1}".format(task_id,
                                                        six.text_type(e)))
            # Add this entry to failed task for the retry process
            self._start_failed_task_handling(task['storage_id'], task['args'],
                                             task_id, start_time, end_time)

        else:
            LOG.info("Performance metrics collection done for storage id :{0} "
                     "and task id:{1}".format(task['storage_id'], task_id))

    def _start_failed_task_handling(self, ctx, storage_id, args, task_id,
                                    start_time, end_time):
        current_time = int(datetime.now().timestamp())
        next_time = current_time + CONF.TELEMETRY.failed_task_schedule_interval
        next_time = datetime \
            .fromtimestamp(next_time) \
            .strftime('%Y-%m-%d %H:%M:%S')

        job_id = uuidutils.generate_uuid()
        self.scheduler_instance.add_job(
            FailedPerformanceCollectionHandler(storage_id, args, job_id,
                                               task_id, start_time, end_time),
            'interval',
            args=[ctx], seconds=CONF.TELEMETRY.failed_task_schedule_interval,
            next_run_time=next_time, id=job_id)
