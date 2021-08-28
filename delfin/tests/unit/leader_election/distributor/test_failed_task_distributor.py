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
from delfin.db.sqlalchemy.models import FailedTask
from delfin.leader_election.distributor.failed_task_distributor import \
    FailedTaskDistributor

fake_executor = 'node1'
fake_failed_job = {
    FailedTask.id.name: 43,
    FailedTask.retry_count.name: 0,
    FailedTask.result.name: "Init",
    FailedTask.job_id.name: "fake_job_id",
    FailedTask.task_id.name: uuidutils.generate_uuid(),
    FailedTask.start_time.name: int(datetime.now().timestamp()),
    FailedTask.end_time.name: int(datetime.now().timestamp()) + 20,
    FailedTask.interval.name: 20,
    FailedTask.deleted.name: False,
    FailedTask.executor.name: fake_executor,
}

fake_failed_jobs = [
    fake_failed_job,
]


class TestFailedTaskDistributor(test.TestCase):

    @mock.patch.object(db, 'failed_task_get_all',
                       mock.Mock(return_value=fake_failed_jobs))
    @mock.patch.object(db, 'failed_task_update',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch.object(db, 'failed_task_get',
                       mock.Mock(return_value=fake_failed_job))
    @mock.patch(
        'delfin.task_manager.metrics_rpcapi.TaskAPI.assign_failed_job')
    def test_telemetry_failed_job_scheduling(self, mock_assign_job):
        ctx = context.get_admin_context()
        task_distributor = FailedTaskDistributor(ctx)
        # call telemetry job scheduling
        task_distributor()
        self.assertEqual(mock_assign_job.call_count, 1)
