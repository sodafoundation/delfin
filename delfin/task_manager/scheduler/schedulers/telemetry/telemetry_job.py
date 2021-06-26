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
from delfin.common.constants import TelemetryCollection
from delfin.task_manager.scheduler import schedule_manager

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class TelemetryJob(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.scheduler = schedule_manager.SchedulerManager().get_scheduler()

        # Reset last run time of tasks to restart scheduling and
        # start the failed task job
        task_list = db.task_get_all(ctx)
        for task in task_list:
            db.task_update(ctx, task['id'], {'last_run_time': None})

        self.stopped = False
        self.job_ids = set()

    def __call__(self):
        """ Schedule the collection tasks based on interval """

        if self.stopped:
            """If Job is stopped return immediately"""
            return

        try:
            # Remove jobs from scheduler when marked for delete
            filters = {'deleted': True}
            tasks = db.task_get_all(self.ctx, filters=filters)
            LOG.debug("Total tasks found deleted "
                      "in this cycle:%s" % len(tasks))
            for task in tasks:
                job_id = task['job_id']
                if job_id and self.scheduler.get_job(job_id):
                    self.remove_scheduled_job(job_id)
                db.task_delete(self.ctx, task['id'])
        except Exception as e:
            LOG.error("Failed to remove periodic scheduling job , reason: %s.",
                      six.text_type(e))
        try:

            filters = {'last_run_time': None}
            tasks = db.task_get_all(self.ctx, filters=filters)
            LOG.debug("Schedule performance collection triggered: total "
                      "tasks to be handled:%s" % len(tasks))
            for task in tasks:
                # Get current time in epoch format in seconds. Here method
                # indicates the specific collection task to be triggered
                current_time = int(datetime.now().timestamp())
                last_run_time = current_time
                next_collection_time = last_run_time + task['interval']
                task_id = task['id']
                job_id = uuidutils.generate_uuid()
                next_collection_time = datetime \
                    .fromtimestamp(next_collection_time) \
                    .strftime('%Y-%m-%d %H:%M:%S')

                collection_class = importutils.import_class(task['method'])
                instance = collection_class.get_instance(self.ctx, task_id)
                self.scheduler.add_job(
                    instance, 'interval', seconds=task['interval'],
                    next_run_time=next_collection_time, id=job_id,
                    misfire_grace_time=int(
                        CONF.telemetry.performance_collection_interval / 2))

                # jobs book keeping
                self.job_ids.add(job_id)

                update_task_dict = {'job_id': job_id,
                                    'last_run_time': last_run_time}
                db.task_update(self.ctx, task_id, update_task_dict)
                LOG.info('Periodic collection task triggered for for task id: '
                         '%s ' % task['id'])
        except Exception as e:
            LOG.error("Failed to trigger periodic collection, reason: %s.",
                      six.text_type(e))
        else:
            LOG.debug("Periodic collection task Scheduling completed.")

    def stop(self):
        self.stopped = True
        for job_id in self.job_ids.copy():
            self.remove_scheduled_job(job_id)
        LOG.info("Stopping telemetry jobs")

    @classmethod
    def job_interval(cls):
        return TelemetryCollection.PERIODIC_JOB_INTERVAL

    def remove_scheduled_job(self, job_id):
        if job_id in self.job_ids:
            self.job_ids.remove(job_id)
        if job_id and self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
