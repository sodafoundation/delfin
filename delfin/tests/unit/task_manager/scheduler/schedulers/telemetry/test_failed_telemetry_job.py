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
from unittest import mock

from oslo_utils import uuidutils

from delfin import context
from delfin import db
from delfin import test
from delfin.common.constants import TelemetryCollection
from delfin.db.sqlalchemy.models import FailedTask
from delfin.db.sqlalchemy.models import Task
from delfin.task_manager.scheduler.schedulers.telemetry. \
    failed_performance_collection_handler import \
    FailedPerformanceCollectionHandler
from delfin.task_manager.scheduler.schedulers.telemetry.failed_telemetry_job \
    import FailedTelemetryJob

fake_failed_job = {
    FailedTask.id.name: 43,
    FailedTask.retry_count.name: 0,
    FailedTask.result.name: "Init",
    FailedTask.job_id.name: None,
    FailedTask.task_id.name: uuidutils.generate_uuid(),
    FailedTask.method.name: FailedPerformanceCollectionHandler.__module__ +
                            '.' +
                            FailedPerformanceCollectionHandler.__name__,
    FailedTask.start_time.name: int(datetime.now().timestamp()),
    FailedTask.end_time.name: int(datetime.now().timestamp()) + 20,
    FailedTask.interval.name: 20,
}

fake_failed_jobs = [
    fake_failed_job,
]

fake_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
}


class TestFailedTelemetryJob(test.TestCase):

    @mock.patch.object(db, 'failed_task_get_all',
                       mock.Mock(return_value=fake_failed_jobs))
    @mock.patch.object(db, 'failed_task_update',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'failed_task_get',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.add_job')
    def test_failed_job_scheduling(self, mock_add_job):
        failed_job = FailedTelemetryJob(context.get_admin_context())
        # call failed job scheduling
        failed_job()
        self.assertEqual(mock_add_job.call_count, 1)

    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.remove_job')
    @mock.patch.object(db, 'failed_task_delete')
    @mock.patch.object(db, 'failed_task_get_all')
    def test_failed_job_with_max_retry(self, mock_failed_get_all,
                                       mock_failed_task_delete,
                                       mock_remove_job):
        # configure to return entry with max retry count
        failed_jobs = fake_failed_jobs.copy()
        failed_jobs[0][FailedTask.retry_count.name] = \
            TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT
        mock_failed_get_all.return_value = failed_jobs

        failed_job = FailedTelemetryJob(context.get_admin_context())
        # call failed job scheduling
        failed_job()

        # entry get deleted and job get removed
        self.assertEqual(mock_failed_task_delete.call_count, 1)
        self.assertEqual(mock_remove_job.call_count, 1)

    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.get_job')
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.add_job')
    @mock.patch.object(db, 'failed_task_get_all')
    def test_failed_job_with_job_already_scheduled(self, mock_failed_get_all,
                                                   mock_add_job,
                                                   mock_get_job):
        # configure to return entry with job id
        failed_jobs = fake_failed_jobs.copy()
        failed_jobs[0][FailedTask.job_id.name] = uuidutils.generate_uuid()
        mock_failed_get_all.return_value = failed_jobs
        # configure to have job in scheduler
        mock_get_job.return_value = failed_jobs

        failed_job = FailedTelemetryJob(context.get_admin_context())
        # call failed job scheduling
        failed_job()

        # the job will not be scheduled
        self.assertEqual(mock_add_job.call_count, 0)

    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.remove_job')
    @mock.patch.object(db, 'failed_task_delete')
    @mock.patch.object(db, 'failed_task_get_all')
    def test_failed_job_scheduling_with_no_task(self, mock_failed_get_all,
                                                mock_failed_task_delete,
                                                mock_remove_job):
        # configure to return entry with max retry count
        failed_jobs = fake_failed_jobs.copy()
        failed_jobs[0][FailedTask.job_id.name] = uuidutils.generate_uuid()
        mock_failed_get_all.return_value = failed_jobs

        failed_job = FailedTelemetryJob(context.get_admin_context())
        # call failed job scheduling
        failed_job()

        # entry get deleted and job get removed
        self.assertEqual(mock_failed_task_delete.call_count, 1)
        self.assertEqual(mock_remove_job.call_count, 1)
