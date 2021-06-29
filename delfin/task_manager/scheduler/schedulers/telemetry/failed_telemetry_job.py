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
from oslo_utils import importutils
from oslo_utils import uuidutils

from delfin import db
from delfin.common.constants import TelemetryJobStatus, TelemetryCollection
from delfin.db.sqlalchemy.models import FailedTask
from delfin.exception import TaskNotFound
from delfin.task_manager.scheduler import schedule_manager

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class FailedTelemetryJob(object):
    def __init__(self, ctx):
        # create the object of periodic scheduler
        self.scheduler = schedule_manager.SchedulerManager().get_scheduler()
        self.ctx = ctx
        self.stopped = False
        self.job_ids = set()

    def __call__(self):
        """
        :return:
        """

        if self.stopped:
            return

        try:
            # Remove jobs from scheduler when marked for delete
            filters = {'deleted': True}
            failed_tasks = db.failed_task_get_all(self.ctx, filters=filters)
            LOG.debug("Total failed_tasks found deleted "
                      "in this cycle:%s" % len(failed_tasks))
            for failed_task in failed_tasks:
                job_id = failed_task['job_id']
                self.remove_scheduled_job(job_id)
                db.failed_task_delete(self.ctx, failed_task['id'])
        except Exception as e:
            LOG.error("Failed to remove periodic scheduling job , reason: %s.",
                      six.text_type(e))
        try:
            # Create the object of periodic scheduler
            failed_tasks = db.failed_task_get_all(self.ctx)

            if not len(failed_tasks):
                LOG.info("No failed task found for performance collection")
                return

            LOG.debug("Schedule performance collection triggered: total "
                      "failed tasks:%s" % len(failed_tasks))

            for failed_task in failed_tasks:
                failed_task_id = failed_task[FailedTask.id.name]
                LOG.info("Processing failed task : %s" % failed_task_id)

                # Get failed jobs, if retry count has reached max,
                # remove job and delete db entry
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

                # If job already scheduled, skip
                if job_id and self.scheduler.get_job(job_id):
                    continue

                try:
                    db.task_get(self.ctx,
                                failed_task[FailedTask.task_id.name])
                except TaskNotFound as e:
                    LOG.info("Removing failed telemetry job as parent job "
                             "do not exist: %s", six.text_type(e))
                    # tear down if original task is not available
                    self._teardown_task(self.ctx, failed_task_id,
                                        job_id)
                    continue

                if not job_id:
                    job_id = uuidutils.generate_uuid()
                    db.failed_task_update(self.ctx, failed_task_id,
                                          {FailedTask.job_id.name: job_id})

                collection_class = importutils.import_class(
                    failed_task[FailedTask.method.name])
                instance = \
                    collection_class.get_instance(self.ctx, failed_task_id)
                self.scheduler.add_job(
                    instance, 'interval',
                    seconds=failed_task[FailedTask.interval.name],
                    next_run_time=datetime.now(), id=job_id,
                    misfire_grace_time=int(
                        CONF.telemetry.performance_collection_interval / 2)
                )
                self.job_ids.add(job_id)

        except Exception as e:
            LOG.error("Failed to schedule retry tasks for performance "
                      "collection, reason: %s", six.text_type(e))
        else:
            LOG.info("Schedule collection completed")

    def _teardown_task(self, ctx, failed_task_id, job_id):
        db.failed_task_delete(ctx, failed_task_id)
        self.remove_scheduled_job(job_id)

    def remove_scheduled_job(self, job_id):
        if job_id in self.job_ids:
            self.job_ids.remove(job_id)
        if job_id and self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def stop(self):
        self.stopped = True
        for job_id in self.job_ids.copy():
            self.remove_scheduled_job(job_id)

    @classmethod
    def job_interval(cls):
        return TelemetryCollection.FAILED_JOB_SCHEDULE_INTERVAL
