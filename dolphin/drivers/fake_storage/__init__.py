# Copyright 2020 The SODA Authors.
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

from dolphin.drivers import driver


class FakeStorageDriver(driver.StorageDriver):
    """FakeStorageDriver shows how to implement the StorageDriver,
    it also plays a role as faker to fake data for being tested by clients.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_storage_registry():
        pass

    def register_storage(self, context):
        # Do something here
        return {
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

    def get_storage(self, context):
        # Do something here
        return {
            'name': 'fake_driver',
            'description': 'it is a fake driver.',
            'vendor': 'fake_storage',
            'model': 'fake_driver',
            'status': 'normal',
            'serial_number': '2102453JPN12KA000011',
            'firmware_version': '1.0.0',
            'location': 'HK',
            'total_capacity': 1024 * 1024,
            'used_capacity': 3126,
            'free_capacity': 1045449,
        }

    def list_pools(self, context):
        pass

    def list_volumes(self, context):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        pass

    def clear_alert(self, context, alert):
        pass
