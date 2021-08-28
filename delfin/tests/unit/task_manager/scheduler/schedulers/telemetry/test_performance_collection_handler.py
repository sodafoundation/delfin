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

from oslo_utils import uuidutils

from delfin import context
from delfin import db
from delfin import exception
from delfin import test
from delfin.common import constants
from delfin.common.constants import TelemetryTaskStatus
from delfin.db.sqlalchemy.models import Task
from delfin.task_manager.scheduler.schedulers.telemetry. \
    performance_collection_handler import \
    PerformanceCollectionHandler

fake_task_id = 43
fake_executor = 'node1'
fake_storage_id = '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6'
fake_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
    Task.interval.name: 10,
    Task.deleted.name: False,
    Task.method.name: constants.TelemetryCollection.PERFORMANCE_TASK_METHOD,
    Task.executor.name: fake_executor
}

fake_deleted_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
    Task.interval.name: 10,
    Task.deleted.name: True,
    Task.method.name: constants.TelemetryCollection.PERFORMANCE_TASK_METHOD,
    Task.executor.name: fake_executor
}


def task_not_found_exception(ctx, task_id):
    raise exception.TaskNotFound("Task not found.")


class TestPerformanceCollectionHandler(test.TestCase):

    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch('delfin.db.task_update')
    @mock.patch('delfin.task_manager.tasks.telemetry'
                '.PerformanceCollectionTask.collect')
    def test_performance_collection_success(self, mock_collect_telemetry,
                                            mock_task_update):
        mock_collect_telemetry.return_value = TelemetryTaskStatus. \
            TASK_EXEC_STATUS_SUCCESS
        ctx = context.get_admin_context()
        perf_collection_handler = PerformanceCollectionHandler.get_instance(
            ctx, fake_task_id)
        # call performance collection handler
        perf_collection_handler()

        self.assertEqual(mock_collect_telemetry.call_count, 1)
        self.assertEqual(mock_task_update.call_count, 1)

    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_telemetry_job))
    @mock.patch('delfin.db.failed_task_create')
    @mock.patch('delfin.task_manager.tasks.telemetry'
                '.PerformanceCollectionTask.collect')
    def test_performance_collection_failure(self, mock_collect_telemetry,
                                            mock_failed_task_create):
        mock_collect_telemetry.return_value = TelemetryTaskStatus. \
            TASK_EXEC_STATUS_FAILURE
        ctx = context.get_admin_context()
        perf_collection_handler = PerformanceCollectionHandler.get_instance(
            ctx, fake_task_id)
        # call performance collection handler
        perf_collection_handler()

        # Verify that failed task create is called if collect telemetry fails
        self.assertEqual(mock_failed_task_create.call_count, 1)

    @mock.patch.object(db, 'task_get',
                       mock.Mock(return_value=fake_deleted_telemetry_job))
    @mock.patch('delfin.db.task_update')
    @mock.patch('delfin.task_manager.tasks.telemetry'
                '.PerformanceCollectionTask.collect')
    def test_performance_collection_deleted_storage(self,
                                                    mock_collect_telemetry,
                                                    mock_task_update):
        mock_collect_telemetry.return_value = TelemetryTaskStatus. \
            TASK_EXEC_STATUS_SUCCESS
        ctx = context.get_admin_context()
        perf_collection_handler = PerformanceCollectionHandler.get_instance(
            ctx, fake_task_id)
        perf_collection_handler()

        # Verify that collect telemetry and db updated is not called
        # for deleted storage
        self.assertEqual(mock_collect_telemetry.call_count, 0)
        self.assertEqual(mock_task_update.call_count, 0)

    @mock.patch('delfin.db.task_get', task_not_found_exception)
    @mock.patch('delfin.task_manager.tasks.telemetry'
                '.PerformanceCollectionTask.collect')
    def test_deleted_storage_exception(self,
                                       mock_collect_telemetry):
        ctx = context.get_admin_context()
        perf_collection_handler = PerformanceCollectionHandler(ctx,
                                                               fake_task_id,
                                                               fake_storage_id,
                                                               "", 100,
                                                               fake_executor)
        perf_collection_handler()

        # Verify that collect telemetry for deleted storage
        self.assertEqual(mock_collect_telemetry.call_count, 0)
