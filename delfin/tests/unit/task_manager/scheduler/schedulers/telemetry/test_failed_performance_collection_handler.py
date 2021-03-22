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
from delfin.common.constants import TelemetryTaskStatus, TelemetryJobStatus

fake_failed_job_id = 43

fake_failed_job = {
    FailedTask.id.name: fake_failed_job_id,
    FailedTask.retry_count.name: 0,
    FailedTask.result.name: "Init",
    FailedTask.job_id.name: uuidutils.generate_uuid(),
    FailedTask.task_id.name: uuidutils.generate_uuid(),
    FailedTask.method.name: FailedPerformanceCollectionHandler.__module__ +
                            '.' +
                            FailedPerformanceCollectionHandler.__name__,
    FailedTask.start_time.name: int(datetime.now().timestamp()),
    FailedTask.end_time.name: int(datetime.now().timestamp()) + 20,
    FailedTask.interval.name: 20,
}

fake_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
}


class TestFailedPerformanceCollectionHandler(test.TestCase):

    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'failed_task_get',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.pause_job')
    @mock.patch('delfin.db.failed_task_update')
    @mock.patch('delfin.task_manager.rpcapi.TaskAPI.collect_telemetry')
    def test_failed_job_success(self, mock_collect_telemetry,
                                mock_failed_task_update, mock_pause_job):
        mock_collect_telemetry.return_value = TelemetryTaskStatus. \
            TASK_EXEC_STATUS_SUCCESS
        ctx = context.get_admin_context()
        failed_job_handler = FailedPerformanceCollectionHandler.get_instance(
            ctx, fake_failed_job_id)
        # call failed job
        failed_job_handler()

        self.assertEqual(mock_pause_job.call_count, 1)
        mock_failed_task_update.assert_called_once_with(
            ctx,
            fake_failed_job_id,
            {
                FailedTask.retry_count.name: 1,
                FailedTask.result.name:
                    TelemetryJobStatus.FAILED_JOB_STATUS_SUCCESS})

    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'failed_task_get',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.pause_job')
    @mock.patch('delfin.db.failed_task_update')
    @mock.patch('delfin.task_manager.rpcapi.TaskAPI.collect_telemetry')
    def test_failed_job_failure(self, mock_collect_telemetry,
                                mock_failed_task_update, mock_pause_job):
        mock_collect_telemetry.return_value = TelemetryTaskStatus. \
            TASK_EXEC_STATUS_FAILURE
        ctx = context.get_admin_context()
        failed_job_handler = FailedPerformanceCollectionHandler.get_instance(
            ctx, fake_failed_job_id)
        # retry
        # call failed job
        failed_job_handler()

        self.assertEqual(mock_pause_job.call_count, 0)
        mock_failed_task_update.assert_called_once_with(
            ctx,
            fake_failed_job_id,
            {
                FailedTask.retry_count.name: 1,
                FailedTask.result.name:
                    TelemetryJobStatus.FAILED_JOB_STATUS_STARTED})

    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch.object(db, 'failed_task_get')
    @mock.patch(
        'apscheduler.schedulers.background.BackgroundScheduler.pause_job')
    @mock.patch('delfin.db.failed_task_update')
    @mock.patch('delfin.task_manager.rpcapi.TaskAPI.collect_telemetry')
    def test_failed_job_fail_max_times(self, mock_collect_telemetry,
                                       mock_failed_task_update, mock_pause_job,
                                       mock_failed_task_get):
        mock_collect_telemetry.return_value = TelemetryTaskStatus. \
            TASK_EXEC_STATUS_FAILURE

        failed_job = fake_failed_job.copy()
        failed_job[
            FailedTask.retry_count.name] = \
            TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT - 1
        # return with maximum retry count
        mock_failed_task_get.return_value = failed_job

        ctx = context.get_admin_context()
        failed_job_handler = FailedPerformanceCollectionHandler.get_instance(
            ctx, fake_failed_job_id)
        # call failed job
        failed_job_handler()

        self.assertEqual(mock_pause_job.call_count, 1)
        mock_failed_task_update.assert_called_once_with(
            ctx,
            fake_failed_job_id,
            {
                FailedTask.retry_count.name:
                    TelemetryCollection.MAX_FAILED_JOB_RETRY_COUNT,
                FailedTask.result.name:
                    TelemetryJobStatus.FAILED_JOB_STATUS_INIT})
