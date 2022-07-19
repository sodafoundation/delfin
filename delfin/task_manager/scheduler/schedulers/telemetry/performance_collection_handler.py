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

from delfin import db
from delfin import exception
from delfin.common.constants import TelemetryCollection
from delfin.db.sqlalchemy.models import FailedTask
from delfin.drivers import api as driverapi
from delfin.task_manager import metrics_rpcapi as metrics_task_rpcapi
from delfin.task_manager.scheduler import schedule_manager
from delfin.task_manager.scheduler.schedulers.telemetry. \
    failed_performance_collection_handler import \
    FailedPerformanceCollectionHandler
from delfin.task_manager.tasks.telemetry import PerformanceCollectionTask

CONF = cfg.CONF
LOG = log.getLogger(__name__)
CONF = cfg.CONF


class PerformanceCollectionHandler(object):
    def __init__(self, ctx, task_id, storage_id, args, interval, executor):
        self.ctx = ctx
        self.task_id = task_id
        self.storage_id = storage_id
        self.args = args
        self.interval = interval
        self.metric_task_rpcapi = metrics_task_rpcapi.TaskAPI()
        self.driver_api = driverapi.API()
        self.executor = executor
        self.scheduler = schedule_manager.SchedulerManager().get_scheduler()

    @staticmethod
    def get_instance(ctx, task_id):
        task = db.task_get(ctx, task_id)
        return PerformanceCollectionHandler(ctx, task_id, task['storage_id'],
                                            task['args'], task['interval'],
                                            task['executor'])

    def __call__(self):
        # Upon periodic job callback, if storage is already deleted or soft
        # deleted,do not proceed with performance collection flow
        try:
            task = db.task_get(self.ctx, self.task_id)
            if task["deleted"]:
                LOG.debug('Storage %s getting deleted, ignoring performance '
                          'collection cycle for task id %s.'
                          % (self.storage_id, self.task_id))
                return
        except exception.TaskNotFound:
            LOG.debug('Storage %s already deleted, ignoring performance '
                      'collection cycle for task id %s.'
                      % (self.storage_id, self.task_id))
            return

        # Handles performance collection from driver and dispatch
        start_time = None
        end_time = None
        try:
            LOG.debug('Collecting performance metrics for task id: %s'
                      % self.task_id)
            current_time = int(datetime.now().timestamp())

            # Times are epoch time in milliseconds
            overlap = CONF.telemetry. \
                performance_timestamp_overlap
            end_time = current_time * 1000
            start_time = end_time - (self.interval * 1000) - (overlap * 1000)
            telemetry = PerformanceCollectionTask()
            status = telemetry.collect(self.ctx, self.storage_id, self.args,
                                       start_time, end_time)

            db.task_update(self.ctx, self.task_id,
                           {'last_run_time': current_time})

            if not status:
                raise exception.TelemetryTaskExecError()
        except Exception as e:
            LOG.error("Failed to collect performance metrics for "
                      "task id :{0}, reason:{1}".format(self.task_id,
                                                        six.text_type(e)))
            self._handle_task_failure(start_time, end_time)
        else:
            LOG.debug("Performance collection done for storage id :{0}"
                      ",task id :{1} and interval(in sec):{2}"
                      .format(self.storage_id, self.task_id, self.interval))

    def _handle_task_failure(self, start_time, end_time):
        failed_task_interval = TelemetryCollection.FAILED_JOB_SCHEDULE_INTERVAL

        try:
            # Fetch driver's capability for performance metric retention window
            # If driver supports it and if it is within collection  range,
            # consider it for failed task scheduling
            capabilities = self.driver_api.get_capabilities(self.ctx,
                                                            self.storage_id)
            performance_metric_retention_window \
                = capabilities.get('performance_metric_retention_window')

            if capabilities.get('failed_job_collect_interval'):
                failed_task_interval = \
                    TelemetryCollection.FAILED_JOB_SCHEDULE_INTERVAL

            if performance_metric_retention_window:
                collection_window = performance_metric_retention_window \
                    if performance_metric_retention_window <= CONF.telemetry \
                    .max_failed_task_retry_window \
                    else CONF.telemetry.max_failed_task_retry_window
                failed_task_interval = collection_window / TelemetryCollection\
                    .MAX_FAILED_JOB_RETRY_COUNT
        except Exception as e:
            LOG.error("Failed to get driver capabilities during failed task "
                      "scheduling for storage id :{0}, reason:{1}"
                      .format(self.storage_id, six.text_type(e)))

        failed_task = {FailedTask.storage_id.name: self.storage_id,
                       FailedTask.task_id.name: self.task_id,
                       FailedTask.interval.name: failed_task_interval,
                       FailedTask.end_time.name: end_time,
                       FailedTask.start_time.name: start_time,
                       FailedTask.method.name:
                           FailedPerformanceCollectionHandler.__module__ +
                           '.' + FailedPerformanceCollectionHandler.__name__,
                       FailedTask.retry_count.name: 0,
                       FailedTask.executor.name: self.executor}
        failed_task = db.failed_task_create(self.ctx, failed_task)
        self.metric_task_rpcapi.assign_failed_job(self.ctx,
                                                  failed_task['id'],
                                                  failed_task['executor'])
