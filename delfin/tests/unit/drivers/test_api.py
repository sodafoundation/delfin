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


import copy
from unittest import TestCase, mock

import sys

from delfin import context
from delfin import exception
from delfin.common import config, constants  # noqa
from delfin.drivers.api import API
from delfin.drivers.fake_storage import FakeStorageDriver

sys.modules['delfin.cryptor'] = mock.Mock()


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "fake_storage",
    "model": "fake_driver",
    "rest": {
        "host": "10.0.0.1",
        "port": "8443",
        "username": "user",
        "password": "pass"
    },
    "extra_attributes": {
        "array_id": "00112233"
    }
}

STORAGE = {
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


class TestDriverAPI(TestCase):

    def test_init(self):
        api = API()
        self.assertIsNotNone(api.driver_manager)

    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.db.storage_create')
    @mock.patch('delfin.db.access_info_create')
    @mock.patch('delfin.db.storage_get_all')
    def test_discover_storage(self, mock_storage, mock_access_info,
                              mock_storage_create, mock_get_storage):
        # Case: Positive scenario for fake driver discovery
        storage = copy.deepcopy(STORAGE)
        storage['id'] = '12345'
        mock_storage.return_value = None
        mock_access_info.return_value = ACCESS_INFO
        mock_storage_create.return_value = storage
        api = API()
        api.discover_storage(context, ACCESS_INFO)
        mock_storage.assert_called()
        mock_access_info.assert_called_with(context, ACCESS_INFO)
        mock_storage_create.assert_called()
        mock_get_storage.return_value = None

        # Case: Register already existing storage
        with self.assertRaises(exception.StorageAlreadyExists) as exc:
            mock_storage.return_value = storage
            api.discover_storage(context, ACCESS_INFO)
        self.assertIn('Storage already exists', str(exc.exception))
        mock_storage.return_value = None

        # Case: Storage without serial number
        wrong_storage = copy.deepcopy(STORAGE)
        wrong_storage.pop('serial_number')
        wrong_storage['id'] = '12345'
        m = mock.Mock()
        with mock.patch.object(FakeStorageDriver, 'get_storage') as m:
            with self.assertRaises(exception.InvalidResults) as exc:
                m.return_value = wrong_storage
                api.discover_storage(context, ACCESS_INFO)
            self.assertIn('Serial number should be provided by storage',
                          str(exc.exception))

            # Case: No Storage found
            with self.assertRaises(exception.StorageBackendNotFound) as exc:
                m.return_value = None
                api.discover_storage(context, ACCESS_INFO)
            self.assertIn('Storage backend could not be found',
                          str(exc.exception))

        # Case: Test access info without 'storage_id' for driver
        test_access_info = copy.deepcopy(ACCESS_INFO)
        test_access_info.pop('storage_id')

        s = api.discover_storage(context, ACCESS_INFO)
        self.assertDictEqual(s, storage)

        # Case: Wrong access info (model) for driver
        wrong_access_info = copy.deepcopy(ACCESS_INFO)
        wrong_access_info['model'] = 'wrong_model'
        with self.assertRaises(exception.StorageDriverNotFound) as exc:
            api.discover_storage(context, wrong_access_info)

        msg = "Storage driver 'fake_storage wrong_model'could not be found"
        self.assertIn(msg, str(exc.exception))

    @mock.patch.object(FakeStorageDriver, 'get_storage')
    @mock.patch('delfin.db.storage_update')
    @mock.patch('delfin.db.access_info_update')
    @mock.patch('delfin.db.storage_get')
    def test_update_access_info(self, mock_storage_get,
                                mock_access_info_update,
                                mock_storage_update,
                                mock_storage):
        storage = copy.deepcopy(STORAGE)
        access_info_new = copy.deepcopy(ACCESS_INFO)
        access_info_new['rest']['username'] = 'new_user'

        mock_storage_get.return_value = storage
        mock_access_info_update.return_value = access_info_new
        mock_storage_update.return_value = None
        mock_storage.return_value = storage
        api = API()
        updated = api.update_access_info(context, access_info_new)

        storage_id = '12345'
        mock_storage_get.assert_called_with(
            context, storage_id)

        mock_access_info_update.assert_called_with(
            context, storage_id, access_info_new)

        mock_storage_update.assert_called_with(
            context, storage_id, storage)

        access_info_new['rest']['password'] = "cGFzc3dvcmQ="
        self.assertDictEqual(access_info_new, updated)

        # Case: Wrong storage serial number
        wrong_storage = copy.deepcopy(STORAGE)
        wrong_storage['serial_number'] = '00000'
        mock_storage.return_value = wrong_storage
        with self.assertRaises(exception.StorageSerialNumberMismatch) as exc:
            api.update_access_info(context, access_info_new)

        msg = "Serial number 00000 does not match " \
              "the existing storage serial number"
        self.assertIn(msg, str(exc.exception))

        # Case: No storage serial number
        wrong_storage.pop('serial_number')
        mock_storage.return_value = wrong_storage
        with self.assertRaises(exception.InvalidResults) as exc:
            api.update_access_info(context, access_info_new)

        msg = "Serial number should be provided by storage"
        self.assertIn(msg, str(exc.exception))

        # Case: No storage
        mock_storage.return_value = None
        with self.assertRaises(exception.StorageBackendNotFound) as exc:
            api.update_access_info(context, access_info_new)

        msg = "Storage backend could not be found"
        self.assertIn(msg, str(exc.exception))

    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.db.storage_create')
    @mock.patch('delfin.db.access_info_create')
    @mock.patch('delfin.db.storage_get_all')
    def test_remove_storage(self, mock_storage, mock_access_info,
                            mock_storage_create, mock_get_storage,
                            mock_dm):
        storage = copy.deepcopy(STORAGE)
        storage['id'] = '12345'
        mock_storage.return_value = None
        mock_access_info.return_value = ACCESS_INFO
        mock_storage_create.return_value = storage
        api = API()
        api.discover_storage(context, ACCESS_INFO)
        mock_get_storage.return_value = None
        mock_dm.return_value = FakeStorageDriver()

        storage_id = '12345'

        # Verify that driver instance not added to factory
        driver = api.driver_manager.driver_factory.get(storage_id, None)
        self.assertIsNone(driver)

        api.remove_storage(context, storage_id)

        driver = api.driver_manager.driver_factory.get(storage_id, None)
        self.assertIsNone(driver)

    @mock.patch.object(FakeStorageDriver, 'get_storage')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_get_storage(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        storage = copy.deepcopy(STORAGE)
        storage['id'] = '12345'
        mock_fake.return_value = storage
        api = API()

        storage_id = '12345'

        api.get_storage(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called()

    @mock.patch.object(FakeStorageDriver, 'list_storage_pools')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_storage_pools(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()

        storage_id = '12345'

        api.list_storage_pools(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_volumes')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_volumes(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_volumes(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_controllers')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_controllers(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_controllers(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_disks')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_disks(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_disks(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_ports')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_ports(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_ports(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_filesystems')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_filesystems(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_filesystems(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_qtrees')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_qtrees(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_qtrees(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_shares')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_shares(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_shares(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'parse_alert')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    @mock.patch('delfin.db.access_info_get')
    def test_parse_alert(self, mock_access_info,
                         driver_manager, mock_fake):
        mock_access_info.return_value = ACCESS_INFO
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()

        storage_id = '12345'

        api.parse_alert(context, storage_id, 'alert')
        mock_access_info.assert_called_once()
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_get_capabilities(self, driver_manager):
        driver_manager.return_value = FakeStorageDriver()
        storage_id = '12345'
        capabilities = API().get_capabilities(context, storage_id)

        self.assertTrue('resource_metrics' in capabilities)
        driver_manager.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_storage_host_initiators')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_storage_host_initiators(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_storage_host_initiators(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_storage_hosts')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_storage_hosts(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_storage_hosts(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_storage_host_groups')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_storage_host_groups(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_storage_host_groups(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_port_groups')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_port_groups(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_port_groups(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_volume_groups')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_volume_groups(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_volume_groups(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch.object(FakeStorageDriver, 'list_masking_views')
    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_list_masking_views(self, driver_manager, mock_fake):
        driver_manager.return_value = FakeStorageDriver()
        mock_fake.return_value = []
        api = API()
        storage_id = '12345'

        api.list_masking_views(context, storage_id)
        driver_manager.assert_called_once()
        mock_fake.assert_called_once()

    @mock.patch('delfin.drivers.manager.DriverManager.get_driver')
    def test_collect_perf_metrics(self, driver_manager):
        driver_manager.return_value = FakeStorageDriver()
        storage_id = '12345'
        capabilities = API().get_capabilities(context, storage_id)

        metrics = API().collect_perf_metrics(context, storage_id,
                                             capabilities['resource_metrics'],
                                             1622808000000, 1622808000001)
        self.assertTrue('resource_metrics' in capabilities)
        self.assertTrue(True, isinstance(metrics[0], constants.metric_struct))
        self.assertEqual(driver_manager.call_count, 2)
