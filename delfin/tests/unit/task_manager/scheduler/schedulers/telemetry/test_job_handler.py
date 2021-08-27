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

from unittest import mock
from datetime import datetime
from oslo_utils import uuidutils

from delfin import context
from delfin import db
from delfin import test
from delfin.common import constants
from delfin.db.sqlalchemy.models import Task
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler import \
    JobHandler
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler import \
    FailedJobHandler
from delfin.db.sqlalchemy.models import FailedTask
from delfin.task_manager.scheduler.schedulers.telemetry. \
    failed_performance_collection_handler import \
    FailedPerformanceCollectionHandler
from delfin.common.constants import TelemetryCollection

fake_executor = 'node1'
fake_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
    Task.interval.name: 10,
    Task.job_id.name: None,
    Task.method.name: constants.TelemetryCollection.PERFORMANCE_TASK_METHOD,
    Task.last_run_time.name: None,
    Task.executor.name: fake_executor,
}

fake_telemetry_jobs = [
    fake_telemetry_job,
]

fake_telemetry_job_deleted = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
    Task.interval.name: 10,
    Task.method.name: constants.TelemetryCollection.PERFORMANCE_TASK_METHOD,
    Task.last_run_time.name: None,
    Task.deleted.name: True,
    Task.executor.name: fake_executor,
}

fake_telemetry_jobs_deleted = [
    fake_telemetry_job_deleted,
]
# With method name as None
Incorrect_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
    Task.interval.name: 10,
    Task.method.name: None,
    Task.last_run_time.name: None,
    Task.executor.name: None,
}

Incorrect_telemetry_jobs = [
    Incorrect_telemetry_job,
]
fake_failed_job = {
    FailedTask.id.name: 43,
    FailedTask.retry_count.name: 0,
    FailedTask.result.name: "Init",
    FailedTask.job_id.name: "fake_job_id",
    FailedTask.task_id.name: uuidutils.generate_uuid(),
    FailedTask.method.name: FailedPerformanceCollectionHandler.__module__ +
                            '.' +
                            FailedPerformanceCollectionHandler.__name__,
    FailedTask.start_time.name: int(datetime.now().timestamp()),
    FailedTask.end_time.name: int(datetime.now().timestamp()) + 20,
    FailedTask.interval.name: 20,
    FailedTask.deleted.name: False,
    FailedTask.executor.name: fake_executor,
}

fake_failed_jobs = [
    fake_failed_job,
]


class TestTelemetryJob(test.TestCase):

    @mock.patch.object(db, 'task_get_all',
                       mock.Mock(return_value=fake_telemetry_jobs))
    @mock.patch.object(db, 'task_update',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.add_job')
    def test_telemetry_job_scheduling(self, mock_add_job):
        ctx = context.get_admin_context()
        telemetry_job = JobHandler(ctx, fake_telemetry_job['id'],
                                   fake_telemetry_job['storage_id'],
                                   fake_telemetry_job['args'],
                                   fake_telemetry_job['interval'])
        # call telemetry job scheduling
        telemetry_job.schedule_job(fake_telemetry_job['id'])
        self.assertEqual(mock_add_job.call_count, 1)

    @mock.patch.object(db, 'task_delete',
                       mock.Mock())
    @mock.patch.object(db, 'task_get_all',
                       mock.Mock(return_value=fake_telemetry_jobs_deleted))
    @mock.patch.object(db, 'task_update',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.add_job',
        mock.Mock())
    @mock.patch('logging.LoggerAdapter.error')
    def test_telemetry_removal_success(self, mock_log_error):
        ctx = context.get_admin_context()
        telemetry_job = JobHandler(ctx, fake_telemetry_job['id'],
                                   fake_telemetry_job['storage_id'],
                                   fake_telemetry_job['args'],
                                   fake_telemetry_job['interval'])
        # call telemetry job scheduling
        telemetry_job.remove_job(fake_telemetry_job['id'])
        self.assertEqual(mock_log_error.call_count, 0)

    @mock.patch.object(db, 'task_get_all',
                       mock.Mock(return_value=fake_telemetry_jobs))
    @mock.patch.object(db, 'task_update',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.add_job')
    def test_schedule_boot_jobs(self, mock_add_job):
        JobHandler.schedule_boot_jobs()
        self.assertEqual(mock_add_job.call_count, 1)


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
        failed_job = FailedJobHandler(context.get_admin_context())
        # call failed job scheduling
        failed_job.schedule_failed_job(fake_failed_job['id'])
        self.assertEqual(mock_add_job.call_count, 1)

    @mock.patch.object(db, 'failed_task_get',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.remove_job')
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.get_job')
    @mock.patch.object(db, 'failed_task_delete')
    @mock.patch.object(db, 'failed_task_get_all')
    def test_failed_job_with_max_retry(self, mock_failed_get_all,
                                       mock_failed_task_delete,
                                       mock_get_job,
                                       mock_remove_job):
        # configure to return entry with max retry count
        failed_jobs = fake_failed_jobs.copy()
        failed_jobs[0][FailedTask.retry_count.name] = \
            TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT
        mock_failed_get_all.return_value = failed_jobs

        failed_job = FailedJobHandler(context.get_admin_context())
        # call failed job scheduling
        failed_job.schedule_failed_job(failed_jobs[0])

        mock_get_job.return_value = True

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

        failed_job = FailedJobHandler(context.get_admin_context())
        # call failed job scheduling
        failed_job.remove_failed_job(fake_failed_job['id'])

        # the job will not be scheduled
        self.assertEqual(mock_add_job.call_count, 0)

    @mock.patch.object(db, 'failed_task_get',
                       mock.Mock(return_value=fake_failed_job))
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

        failed_job = FailedJobHandler(context.get_admin_context())
        # call failed job scheduling
        failed_job.remove_failed_job(fake_failed_job)

        # entry get deleted and job get removed
        self.assertEqual(mock_failed_task_delete.call_count, 1)
        self.assertEqual(mock_remove_job.call_count, 0)
