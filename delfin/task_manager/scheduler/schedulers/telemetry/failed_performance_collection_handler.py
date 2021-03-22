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

import six
from oslo_config import cfg
from oslo_log import log

from delfin import db
from delfin import exception
from delfin.common.constants import TelemetryJobStatus, TelemetryCollection
from delfin.db.sqlalchemy.models import FailedTask
from delfin.db.sqlalchemy.models import Task
from delfin.i18n import _
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.scheduler import scheduler
from delfin.task_manager.tasks.telemetry import PerformanceCollectionTask

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class FailedPerformanceCollectionHandler(object):
    def __init__(self, ctx, filed_task_id, storage_id, args, job_id,
                 retry_count, start_time, end_time):
        self.ctx = ctx
        self.filed_task_id = filed_task_id
        self.retry_count = retry_count
        self.storage_id = storage_id
        self.job_id = job_id
        self.args = args
        self.start_time = start_time
        self.end_time = end_time
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.scheduler_instance = scheduler.Scheduler.get_instance()
        self.result = TelemetryJobStatus.FAILED_JOB_STATUS_INIT

    @staticmethod
    def get_instance(ctx, failed_task_id):
        # fetch failed task info
        failed_task = db.failed_task_get(ctx, failed_task_id)
        # fetched task info
        task = db.task_get(ctx, failed_task[FailedTask.task_id.name])
        return FailedPerformanceCollectionHandler(
            ctx,
            failed_task[FailedTask.id.name],
            task[Task.storage_id.name],
            task[Task.args.name],
            failed_task[FailedTask.job_id.name],
            failed_task[FailedTask.retry_count.name],
            failed_task[FailedTask.start_time.name],
            failed_task[FailedTask.end_time.name],
        )

    def __call__(self):
        # pull performance collection info
        self.retry_count = self.retry_count + 1
        try:
            status = self.task_rpcapi.collect_telemetry(
                self.ctx, self.storage_id,
                PerformanceCollectionTask.__module__ + '.' +
                PerformanceCollectionTask.__name__,
                self.args, self.start_time, self.end_time)

            if not status:
                raise exception.TelemetryTaskExecError()
        except Exception as e:
            LOG.error(e)
            msg = _("Failed to collect performance metrics for storage "
                    "id:{0}, reason:{1}".format(self.storage_id,
                                                six.text_type(e)))
            LOG.error(msg)
        else:
            LOG.info("Successfully completed Performance metrics collection "
                     "for storage id :{0} ".format(self.storage_id))
            self.result = TelemetryJobStatus.FAILED_JOB_STATUS_SUCCESS
            self._stop_task()
            return

        if self.retry_count >= TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT:
            msg = _(
                "Failed to collect performance metrics of task instance "
                "id:{0} for start time:{1} and end time:{2} with "
                "maximum retry. Giving up on "
                "retry".format(self.filed_task_id, self.start_time,
                               self.end_time))
            LOG.error(msg)
            self._stop_task()
            return

        self.result = TelemetryJobStatus.FAILED_JOB_STATUS_STARTED
        db.failed_task_update(self.ctx, self.filed_task_id,
                              {FailedTask.retry_count.name: self.retry_count,
                               FailedTask.result.name: self.result})

    def _stop_task(self):
        db.failed_task_update(self.ctx, self.filed_task_id,
                              {FailedTask.retry_count.name: self.retry_count,
                               FailedTask.result.name: self.result})
        self.scheduler_instance.pause_job(self.job_id)
