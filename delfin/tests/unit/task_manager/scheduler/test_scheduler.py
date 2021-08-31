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

from apscheduler.schedulers.background import BackgroundScheduler

from delfin import db
from delfin import test
from delfin.coordination import ConsistentHashing
from delfin.leader_election.distributor.task_distributor \
    import TaskDistributor
from delfin.task_manager.metrics_rpcapi import TaskAPI
from delfin.task_manager.scheduler import schedule_manager

FAKE_TASKS = [
    {
        'id': 1,
        'executor': 'node1'
    },
    {
        'id': 2,
        'executor': 'node2'
    },
    {
        'id': 3,
        'executor': 'node1'
    }
]


class TestScheduler(test.TestCase):

    def test_scheduler_manager_singleton(self):
        first_instance = schedule_manager.SchedulerManager().get_scheduler()
        self.assertIsInstance(first_instance, BackgroundScheduler)

        second_instance = schedule_manager.SchedulerManager().get_scheduler()
        self.assertIsInstance(second_instance, BackgroundScheduler)

        self.assertEqual(first_instance, second_instance)

    @mock.patch.object(BackgroundScheduler, 'start')
    def test_start(self, mock_scheduler_start):
        manager = schedule_manager.SchedulerManager()
        manager.start()
        self.assertEqual(mock_scheduler_start.call_count, 1)
        manager.start()
        self.assertEqual(mock_scheduler_start.call_count, 1)

    @mock.patch('tooz.coordination.get_coordinator', mock.Mock())
    @mock.patch.object(ConsistentHashing, 'get_task_executor')
    @mock.patch.object(TaskAPI, 'remove_job')
    @mock.patch.object(TaskDistributor, 'distribute_new_job')
    @mock.patch.object(db, 'task_get_all')
    def test_on_node_join(self, mock_task_get_all, mock_distribute_new_job,
                          mock_remove_job, mock_get_task_executor):
        node1_job_count = 0
        node2_job_count = 0
        for job in FAKE_TASKS:
            if job['executor'] == 'node1':
                node1_job_count += 1
            elif job['executor'] == 'node2':
                node2_job_count += 1
        mock_task_get_all.return_value = FAKE_TASKS
        mock_get_task_executor.return_value = 'node1'
        manager = schedule_manager.SchedulerManager()
        manager.on_node_join(mock.Mock(member_id=b'fake_member_id',
                                       group_id='node1'))
        self.assertEqual(mock_task_get_all.call_count, 1)
        self.assertEqual(mock_distribute_new_job.call_count,
                         node1_job_count + node2_job_count)
        self.assertEqual(mock_remove_job.call_count, node2_job_count)
        self.assertEqual(mock_get_task_executor.call_count,
                         node1_job_count + node2_job_count)

    @mock.patch.object(TaskDistributor, 'distribute_new_job')
    @mock.patch.object(db, 'task_get_all')
    def test_on_node_leave(self, mock_task_get_all, mock_distribute_new_job):
        mock_task_get_all.return_value = FAKE_TASKS
        manager = schedule_manager.SchedulerManager()
        manager.on_node_leave(mock.Mock(member_id=b'fake_member_id',
                                        group_id='fake_group_id'))
        self.assertEqual(mock_task_get_all.call_count, 1)
        self.assertEqual(mock_distribute_new_job.call_count, len(FAKE_TASKS))

    @mock.patch.object(TaskDistributor, 'distribute_new_job')
    @mock.patch.object(db, 'task_get_all')
    def test_recover_job(self, mock_task_get_all, mock_distribute_new_job):
        mock_task_get_all.return_value = FAKE_TASKS
        manager = schedule_manager.SchedulerManager()
        manager.recover_job()
        self.assertEqual(mock_task_get_all.call_count, 1)
        self.assertEqual(mock_distribute_new_job.call_count, len(FAKE_TASKS))
