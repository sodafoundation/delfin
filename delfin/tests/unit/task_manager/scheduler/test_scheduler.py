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

from apscheduler.schedulers.background import BackgroundScheduler

from delfin import test
from delfin.task_manager.scheduler import scheduler


class TestScheduler(test.TestCase):

    def test_scheduler_singleton(self):
        first_instance = scheduler.Scheduler.get_instance()
        self.assertIsInstance(first_instance, BackgroundScheduler)

        second_instance = scheduler.Scheduler.get_instance()
        self.assertIsInstance(second_instance, BackgroundScheduler)

        self.assertEqual(first_instance, second_instance)
