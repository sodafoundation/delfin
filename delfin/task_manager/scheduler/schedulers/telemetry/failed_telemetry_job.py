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
from oslo_utils import importutils
from oslo_utils import uuidutils

from delfin import db
from delfin import utils
from delfin.common.constants import TelemetryJobStatus, TelemetryCollection
from delfin.db.sqlalchemy.models import FailedTask
from delfin.task_manager.scheduler import scheduler

LOG = log.getLogger(__name__)


@six.add_metaclass(utils.Singleton)
class FailedTelemetryJob(object):
    def __init__(self, ctx):
        # create the object of periodic scheduler
        self.schedule = scheduler.Scheduler.get_instance()
        self.ctx = ctx

    def __call__(self):
        """
        :return:
        """
        try:
            # create the object of periodic scheduler
            failed_tasks = db.failed_task_get_all(self.ctx)

            if not len(failed_tasks):
                LOG.info("No failed task found for performance collection")
                return

            LOG.info("Schedule performance collection triggered: total "
                     "failed tasks:%s" % len(failed_tasks))

            for failed_task in failed_tasks:
                # Get current time in epoch format
                failed_task_id = failed_task[FailedTask.id.name]
                LOG.info("Processing failed task : %s" % failed_task_id)

                retry_count = failed_task[FailedTask.retry_count.name]
                result = failed_task[FailedTask.result.name]
                job_id = failed_task[FailedTask.job_id.name]
                if retry_count >= \
                        TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT or \
                        result == TelemetryJobStatus.FAILED_JOB_STATUS_SUCCESS:
                    LOG.info("Exiting Failure task processing for task [%d] "
                             "with result [%s] and retry count [%d] "
                             % (failed_task_id, result, retry_count))
                    # task ID is same as job id
                    self._teardown_task(self.ctx, failed_task_id, job_id)
                    continue

                # check if job already scheduled
                if job_id and self.schedule.get_job(job_id):
                    # skip if job already exist
                    continue

                # fetch storage_id and args from task table
                telemetry_task = db.task_get(
                    self.ctx, failed_task[FailedTask.task_id.name])
                if not telemetry_task:
                    # failed task if original task is not available
                    db.failed_task_delete(self.ctx, failed_task_id)

                if not job_id:
                    job_id = uuidutils.generate_uuid()
                    db.failed_task_update(self.ctx, failed_task_id,
                                          {FailedTask.job_id.name: job_id})

                # method indicates the specific collection task to be
                # triggered
                collection_class = importutils.import_class(
                    failed_task[FailedTask.method.name])
                instance = \
                    collection_class.get_instance(self.ctx, failed_task_id)
                # Create failed task collection
                self.schedule.add_job(
                    instance, 'interval',
                    seconds=failed_task[FailedTask.interval.name],
                    next_run_time=datetime.now(), id=job_id)

        except Exception as e:
            LOG.error("Failed to schedule retry tasks for performance "
                      "collection, reason: %s", six.text_type(e))
        else:
            # start the scheduler
            LOG.info("Schedule collection completed")

    def _teardown_task(self, ctx, failed_task_id, job_id):
        db.failed_task_delete(ctx, failed_task_id)
        self.schedule.remove_job(job_id)
