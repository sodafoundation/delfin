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
from oslo_utils import uuidutils, importutils

from delfin import db
from delfin.common.constants import TelemetryCollection, TelemetryJobStatus
from delfin.exception import TaskNotFound
from delfin.i18n import _
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.scheduler import schedule_manager
from delfin.task_manager.tasks.telemetry import PerformanceCollectionTask

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class JobHandler(object):
    def __init__(self, ctx, task_id, storage_id, args, interval):
        # create an object of periodic task scheduler
        self.ctx = ctx
        self.task_id = task_id
        self.storage_id = storage_id
        self.args = args
        self.interval = interval
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.scheduler = schedule_manager.SchedulerManager().get_scheduler()
        self.stopped = False
        self.job_ids = set()

    @staticmethod
    def get_instance(ctx, task_id):
        task = db.task_get(ctx, task_id)
        return JobHandler(ctx, task_id, task['storage_id'],
                          task['args'], task['interval'])

    def perform_history_collection(self, start_time, end_time, last_run_time):
        # Trigger one historic collection to make sure we do not
        # miss any Data points due to reschedule
        LOG.debug('Triggering one historic collection for task %s',
                  self.task_id)
        try:
            telemetry = PerformanceCollectionTask()
            ret = telemetry.collect(self.ctx, self.storage_id, self.args,
                                    start_time, end_time)
            LOG.debug('Historic collection performed for task %s with '
                      'result %s' % (self.task_id, ret))
            db.task_update(self.ctx, self.task_id,
                           {'last_run_time': last_run_time})
        except Exception as e:
            msg = _("Failed to collect performance metrics during history "
                    "collection for storage id:{0}, reason:{1}"
                    .format(self.storage_id, six.text_type(e)))
            LOG.error(msg)

    def schedule_job(self, task_id):

        if self.stopped:
            # If Job is stopped return immediately
            return

        LOG.info("JobHandler received A job %s to schedule" % task_id)
        job = db.task_get(self.ctx, task_id)
        # Check delete status of the task
        deleted = job['deleted']
        if deleted:
            return
        collection_class = importutils.import_class(
            job['method'])
        instance = collection_class.get_instance(self.ctx, self.task_id)
        current_time = int(datetime.now().timestamp())
        last_run_time = current_time
        next_collection_time = last_run_time + job['interval']
        job_id = uuidutils.generate_uuid()
        next_collection_time = datetime \
            .fromtimestamp(next_collection_time) \
            .strftime('%Y-%m-%d %H:%M:%S')

        existing_job_id = job['job_id']

        scheduler_job = self.scheduler.get_job(existing_job_id)

        if not (existing_job_id and scheduler_job):
            LOG.info('JobHandler scheduling a new job')
            self.scheduler.add_job(
                instance, 'interval', seconds=job['interval'],
                next_run_time=next_collection_time, id=job_id,
                misfire_grace_time=int(job['interval'] / 2))

            update_task_dict = {'job_id': job_id}
            db.task_update(self.ctx, self.task_id, update_task_dict)
            self.job_ids.add(job_id)
            LOG.info('Periodic collection tasks scheduled for for job id: '
                     '%s ' % self.task_id)

            # Check if historic collection is needed for this task.
            # If the last run time is already set, adjust start_time based on
            # last run time or history_on_reschedule which is smaller
            # If jod id is created but last run time is not yet set, then
            # adjust start_time based on interval or history_on_reschedule
            # whichever is smaller

            end_time = current_time * 1000
            # Maximum supported history duration on restart
            history_on_reschedule = CONF.telemetry. \
                performance_history_on_reschedule
            if job['last_run_time']:
                start_time = job['last_run_time'] * 1000 \
                    if current_time - job['last_run_time'] < \
                    history_on_reschedule \
                    else (end_time - history_on_reschedule * 1000)
                self.perform_history_collection(start_time, end_time,
                                                last_run_time)
            elif existing_job_id:
                interval_in_sec = job['interval']
                start_time = (end_time - interval_in_sec * 1000) \
                    if interval_in_sec < history_on_reschedule \
                    else (end_time - history_on_reschedule * 1000)
                self.perform_history_collection(start_time, end_time,
                                                last_run_time)
        else:
            LOG.info('Job already exists with this scheduler')

    def stop(self):
        self.stopped = True
        for job_id in self.job_ids.copy():
            self.remove_scheduled_job(job_id)
        LOG.info("Stopping telemetry jobs")

    def remove_scheduled_job(self, job_id):
        if job_id in self.job_ids:
            self.job_ids.remove(job_id)
        if job_id and self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def remove_job(self, task_id):
        try:
            LOG.info("Received job %s to remove", task_id)
            job = db.task_get(self.ctx, task_id)
            job_id = job['job_id']
            self.remove_scheduled_job(job_id)
        except Exception as e:
            LOG.error("Failed to remove periodic scheduling job , reason: %s.",
                      six.text_type(e))


class FailedJobHandler(object):
    def __init__(self, ctx):
        # create an object of periodic failed task scheduler
        self.scheduler = schedule_manager.SchedulerManager().get_scheduler()
        self.ctx = ctx
        self.stopped = False
        self.job_ids = set()

    @staticmethod
    def get_instance(ctx, failed_task_id):
        return FailedJobHandler(ctx)

    def schedule_failed_job(self, failed_task_id):

        if self.stopped:
            return

        try:
            job = db.failed_task_get(self.ctx, failed_task_id)
            retry_count = job['retry_count']
            result = job['result']
            job_id = job['job_id']
            if retry_count >= \
                    TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT or \
                    result == TelemetryJobStatus.FAILED_JOB_STATUS_SUCCESS:
                LOG.info("Exiting Failure task processing for task [%d] "
                         "with result [%s] and retry count [%d] "
                         % (job['id'], result, retry_count))
                self._teardown_task(self.ctx, job['id'], job_id)
                return
            # If job already scheduled, skip
            if job_id and self.scheduler.get_job(job_id):
                return

            try:
                db.task_get(self.ctx, job['task_id'])
            except TaskNotFound as e:
                LOG.info("Removing failed telemetry job as parent job "
                         "do not exist: %s", six.text_type(e))
                # tear down if original task is not available
                self._teardown_task(self.ctx, job['id'],
                                    job_id)
                return

            if not (job_id and self.scheduler.get_job(job_id)):
                job_id = uuidutils.generate_uuid()
                db.failed_task_update(self.ctx, job['id'],
                                      {'job_id': job_id})

                collection_class = importutils.import_class(
                    job['method'])
                instance = \
                    collection_class.get_instance(self.ctx, job['id'])
                self.scheduler.add_job(
                    instance, 'interval',
                    seconds=job['interval'],
                    next_run_time=datetime.now(), id=job_id,
                    misfire_grace_time=int(job['interval'] / 2))
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

    def remove_failed_job(self, failed_task_id):
        try:
            LOG.info("Received failed job %s to remove", failed_task_id)
            job = db.failed_task_get(self.ctx, failed_task_id)
            job_id = job['job_id']
            self.remove_scheduled_job(job_id)
            db.failed_task_delete(self.ctx, job['id'])
            LOG.info("Removed failed_task entry  %s ", job['id'])
        except Exception as e:
            LOG.error("Failed to remove periodic scheduling job , reason: %s.",
                      six.text_type(e))

    @classmethod
    def job_interval(cls):
        return TelemetryCollection.FAILED_JOB_SCHEDULE_INTERVAL
