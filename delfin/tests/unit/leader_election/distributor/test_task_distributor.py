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
from delfin import test
from delfin.common import constants
from delfin.db.sqlalchemy.models import Task
from delfin.leader_election.distributor.task_distributor import TaskDistributor

fake_telemetry_job = {
    Task.id.name: 2,
    Task.storage_id.name: uuidutils.generate_uuid(),
    Task.args.name: {},
    Task.interval.name: 10,
    Task.method.name: constants.TelemetryCollection.PERFORMANCE_TASK_METHOD,
    Task.last_run_time.name: None,
    Task.deleted.name: 0,
}

fake_telemetry_jobs = [
    fake_telemetry_job,
]


class TestTaskDistributor(test.TestCase):

    @mock.patch.object(db, 'task_update')
    @mock.patch(
        'delfin.task_manager.metrics_rpcapi.TaskAPI.assign_job')
    def test_distribute_new_job(self, mock_task_update, mock_assign_job):
        ctx = context.get_admin_context()
        task_distributor = TaskDistributor(ctx)
        task_distributor.distribute_new_job('fake_task_id')
        self.assertEqual(mock_assign_job.call_count, 1)
        self.assertEqual(mock_task_update.call_count, 1)
