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

from delfin import context
from delfin import db
from delfin import exception
from delfin import test
from delfin.task_manager.tasks import telemetry
from delfin.task_manager.metrics_manager import MetricsTaskManager
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import JobHandler, FailedJobHandler
from apscheduler.schedulers.background import BackgroundScheduler
from delfin.task_manager.subprocess_rpcapi import SubprocessAPI


fake_storage = {
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    'name': 'fake_driver',
    'description': 'it is a fake driver.',
    'vendor': 'fake_vendor',
    'model': 'fake_model',
    'status': 'normal',
    'serial_number': '2102453JPN12KA000011',
    'firmware_version': '1.0.0',
    'location': 'HK',
    'total_capacity': 1024 * 1024,
    'used_capacity': 3126,
    'free_capacity': 1045449,
}


class TestPerformanceCollectionTask(test.TestCase):

    @mock.patch.object(db, 'storage_get',
                       mock.Mock(return_value=fake_storage))
    @mock.patch('delfin.exporter.base_exporter.PerformanceExporterManager'
                '.dispatch')
    @mock.patch('delfin.drivers.api.API.collect_perf_metrics')
    def test_performance_collection_success(self, mock_collect_perf_metrics,
                                            mock_dispatch):
        perf_task = telemetry.PerformanceCollectionTask()
        storage_id = fake_storage['id']
        mock_collect_perf_metrics.return_value = []
        perf_task.collect(context, storage_id, [], 100800, 100900)
        self.assertEqual(mock_collect_perf_metrics.call_count, 1)
        self.assertEqual(mock_dispatch.call_count, 1)

    @mock.patch.object(db, 'storage_get',
                       mock.Mock(return_value=fake_storage))
    @mock.patch('logging.LoggerAdapter.error')
    @mock.patch('delfin.exporter.base_exporter.PerformanceExporterManager'
                '.dispatch')
    @mock.patch('delfin.drivers.api.API.collect_perf_metrics')
    def test_performance_collection_failure(self, mock_collect_perf_metrics,
                                            mock_dispatch, mock_log_error):
        perf_task = telemetry.PerformanceCollectionTask()
        storage_id = fake_storage['id']
        # No alert
        mock_collect_perf_metrics.return_value = []
        mock_collect_perf_metrics.side_effect = \
            exception.Invalid('Fake exception')
        perf_task.collect(context, storage_id, [], 100800, 100900)
        # Verify that dispatch is not done and error is logged
        # when collect metric fails
        self.assertEqual(mock_dispatch.call_count, 0)
        self.assertEqual(mock_log_error.call_count, 1)

    @mock.patch.object(SubprocessAPI, 'assign_job_local')
    @mock.patch.object(db, 'task_get')
    @mock.patch.object(JobHandler, 'schedule_job')
    @mock.patch.object(MetricsTaskManager, 'schedule_boot_jobs')
    @mock.patch.object(MetricsTaskManager, 'create_process')
    def test_metric_manager_assign_job(self, mock_create, mock_boot_job,
                                       mock_job_schedule, mock_db,
                                       mock_subprocess_api):
        mock_db.return_value = {
            'storage_id': 'storage_id1',
            'args': 'args',
            'interval': 10,
        }
        mock_create.return_value = None
        mock_boot_job.return_value = None
        mock_job_schedule.return_value = None
        mock_subprocess_api.return_value = None

        mgr = MetricsTaskManager()
        mgr.enable_sub_process = False

        mgr.assign_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)

        mgr.enable_sub_process = True
        mgr.scheduler = BackgroundScheduler()
        mgr.scheduler.start()
        mgr.assign_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)
        self.assertEqual(mock_subprocess_api.call_count, 1)

    @mock.patch.object(SubprocessAPI, 'remove_job_local')
    @mock.patch.object(db, 'task_get')
    @mock.patch.object(JobHandler, 'remove_job')
    @mock.patch.object(MetricsTaskManager, 'schedule_boot_jobs')
    @mock.patch.object(MetricsTaskManager, 'create_process')
    def test_metric_manager_remove_job(self, mock_create, mock_boot_job,
                                       mock_job_schedule, mock_db,
                                       mock_subprocess_api):
        mock_db.return_value = {
            'storage_id': 'storage_id1',
            'args': 'args',
            'interval': 10,
        }
        mock_create.return_value = None
        mock_boot_job.return_value = None
        mock_job_schedule.return_value = None
        mock_subprocess_api.return_value = None

        mgr = MetricsTaskManager()
        mgr.enable_sub_process = False

        mgr.remove_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)

        mgr.enable_sub_process = True
        mgr.executor_map = {
            'host1': {
                "storages": ['storage_id1'],
            }
        }
        mgr.scheduler = BackgroundScheduler()
        mgr.scheduler.start()
        mgr.remove_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)
        self.assertEqual(mock_subprocess_api.call_count, 1)

    @mock.patch.object(SubprocessAPI, 'assign_failed_job_local')
    @mock.patch.object(db, 'failed_task_get')
    @mock.patch.object(FailedJobHandler, 'schedule_failed_job')
    @mock.patch.object(MetricsTaskManager, 'schedule_boot_jobs')
    @mock.patch.object(MetricsTaskManager, 'create_process')
    @mock.patch.object(MetricsTaskManager, 'get_local_executor')
    def test_metric_manager_assign_failed_job(self, mock_executor,
                                              mock_create,
                                              mock_boot_job,
                                              mock_job_schedule, mock_db,
                                              mock_subprocess_api):
        mock_db.return_value = {
            'storage_id': 'storage_id1',
            'args': 'args',
            'interval': 10,
        }
        mock_create.return_value = None
        mock_boot_job.return_value = None
        mock_job_schedule.return_value = None
        mock_subprocess_api.return_value = None
        mock_executor.return_value = None

        mgr = MetricsTaskManager()
        mgr.enable_sub_process = False

        mgr.assign_failed_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)

        mgr.enable_sub_process = True
        mgr.scheduler = BackgroundScheduler()
        mgr.scheduler.start()
        mgr.assign_failed_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)
        self.assertEqual(mock_subprocess_api.call_count, 1)

    @mock.patch.object(SubprocessAPI, 'remove_failed_job_local')
    @mock.patch.object(db, 'failed_task_get')
    @mock.patch.object(FailedJobHandler, 'remove_failed_job')
    @mock.patch.object(MetricsTaskManager, 'schedule_boot_jobs')
    @mock.patch.object(MetricsTaskManager, 'create_process')
    def test_metric_manager_remove_failed_job(self, mock_create,
                                              mock_boot_job,
                                              mock_job_schedule, mock_db,
                                              mock_subprocess_api):
        mock_db.return_value = {
            'storage_id': 'storage_id1',
            'args': 'args',
            'interval': 10,
        }
        mock_create.return_value = None
        mock_boot_job.return_value = None
        mock_job_schedule.return_value = None
        mock_subprocess_api.return_value = None

        mgr = MetricsTaskManager()
        mgr.enable_sub_process = False

        mgr.remove_failed_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)

        mgr.enable_sub_process = True
        mgr.executor_map = {
            'host1': {
                "storages": ['storage_id1'],
            }
        }
        mgr.scheduler = BackgroundScheduler()
        mgr.scheduler.start()
        mgr.remove_failed_job('context', 'task_id1', 'host1')
        self.assertEqual(mock_job_schedule.call_count, 1)
        self.assertEqual(mock_subprocess_api.call_count, 1)
