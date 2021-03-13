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

class FailedTelemetryJob(object):
    def __init__(self, start_time, end_time):

        self.start_time = start_time
        self.end_time = end_time


    def __call__(self, ctx):
        """
        :return:
        """
        try:
            # create the object of periodic scheduler
            schedule = config.Scheduler.getInstance()
            failed_tasks = db.failed_task_get_all(ctx)

            LOG.info(
                "***********************************************************")

            if not len(failed_tasks):
                LOG.info("No failed task found for performance collection")
                LOG.info(
                    "*******************************************************")
                return

            LOG.info("Schedule performance collection triggered: total "
                     "failed tasks:%s" % len(failed_tasks))
            LOG.info(
                "***********************************************************")
            for task in failed_tasks:
                # Get current time in epoch format
                LOG.info("Processing failed task : %s" % task['id'])
                task_id = task['id']

                if task['retry_count'] \
                        >= telemetry.max_failed_task_retry_count:
                    LOG.info("Failure task processing for task [%d] reached "
                             "max retry count" % task_id)
                    # task ID is same as job id
                    self._clean_failed_task(ctx)
                    continue

                # check if job already scheduled
                job_id = task['job_id']
                if job_id and schedule.get_job(job_id):
                    # skip if job already exist
                    continue

                if not job_id:
                    job_id = uuidutils.generate_uuid()
                    db.failed_task_update(ctx, task_id, {'job_id': job_id})

                # fetch storage_id and args from task table
                task_template = db.task_get(ctx, task['task_id'])
                if not task_template:
                    # failed task if original task is not available
                    db.failed_task_delete(ctx, task_id)

                # Create failed task collection
                schedule.add_job(
                    PerformanceCollectionFailedTask(
                        task_id, job_id, task_template['storage_id'],
                        task_template['args']),
                    'interval', args=[ctx], seconds=task['interval'],
                    next_run_time=datetime.now(), id=job_id)
        except Exception as e:
            LOG.error("Failed to schedule retry tasks for performance "
                      "collection, reason: %s", six.text_type(e))
        else:
            # start the scheduler
            LOG.info("Schedule collection completed")
