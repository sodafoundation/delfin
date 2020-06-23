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


from unittest import mock

from delfin.drivers import fake_storage
from delfin.task_manager.tasks import task
from delfin.task_manager.tasks.task import StorageDeviceTask

from delfin import test, context, coordination

storage = {
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

pools_list = [{
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "name": "fake_pool_" + str(id),
    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "native_storage_pool_id": "fake_original_id_" + str(id),
    "description": "Fake Pool",
    "status": "normal",
    "total_capacity": 1024 * 1024,
    "used_capacity": 3126,
    "free_capacity": 1045449,
}
]

vols_list = [{
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a340',
    "name": "fake_vol_" + str(id),
    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "description": "Fake Volume",
    "status": "normal",
    "native_volume_id": "fake_original_id_" + str(id),
    "wwn": "fake_wwn_" + str(id),
    "total_capacity": 1024 * 1024,
    "used_capacity": 3126,
    "free_capacity": 1045449,
}
]


class TestStorageDeviceTask(test.TestCase):
    def setUp(self):
        super(TestStorageDeviceTask, self).setUp()
        self.driver_api = mock.Mock()
        self.task_manager = StorageDeviceTask(
            context, "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6")
        self.mock_object(self.task_manager, 'driver_api', self.driver_api)

    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.get_storage')
    @mock.patch('delfin.db.storage_update')
    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.db.storage_delete')
    @mock.patch('delfin.db.access_info_delete')
    @mock.patch('delfin.db.alert_source_delete')
    def test_sync_successful(self, alert_source_delete, access_info_delete,
                             mock_storage_delete, mock_storage_get,
                             mock_storage_update, mock_get_storage, get_lock):
        storage_obj = task.StorageDeviceTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')

        storage_obj.sync()
        self.assertTrue(get_lock.called)
        self.assertTrue(mock_storage_get.called)
        self.assertTrue(mock_storage_delete.called)
        self.assertTrue(access_info_delete.called)
        self.assertTrue(alert_source_delete.called)
        self.assertTrue(mock_storage_update.called)
        mock_get_storage.assert_called_with(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')

        fake_storage_obj = fake_storage.FakeStorageDriver()
        mock_get_storage.return_value = fake_storage_obj.get_storage(context)
        storage_obj.sync()

    @mock.patch('delfin.db.storage_delete')
    @mock.patch('delfin.db.alert_source_delete')
    def test_successful_remove(self, mock_alert_del, mock_strg_del):
        storage_obj = task.StorageDeviceTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_obj.remove()

        mock_strg_del.assert_called_with(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        mock_alert_del.assert_called_with(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')


class TestStoragePoolTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_storage_pools')
    @mock.patch('delfin.db.storage_pool_get_all')
    @mock.patch('delfin.db.storage_pools_delete')
    @mock.patch('delfin.db.storage_pools_update')
    @mock.patch('delfin.db.storage_pools_create')
    def test_sync_successful(self, mock_pool_create, mock_pool_update,
                             mock_pool_del, mock_pool_get_all,
                             mock_list_pools, get_lock):
        pool_obj = task.StoragePoolTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        pool_obj.sync()

        self.assertTrue(mock_list_pools.called)
        self.assertTrue(mock_pool_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the pools from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the new pool to DB
        mock_list_pools.return_value = fake_storage_obj.list_storage_pools(
            context)
        mock_pool_get_all.return_value = list()
        pool_obj.sync()
        self.assertTrue(mock_pool_create.called)

        # update the new pool of DB
        mock_list_pools.return_value = pools_list
        mock_pool_get_all.return_value = pools_list
        pool_obj.sync()
        self.assertTrue(mock_pool_update.called)

        # delete the new pool to DB
        mock_list_pools.return_value = list()
        mock_pool_get_all.return_value = pools_list
        pool_obj.sync()
        self.assertTrue(mock_pool_del.called)

    @mock.patch('delfin.db.storage_pool_delete_by_storage')
    def test_remove(self, mock_pool_del):
        pool_obj = task.StoragePoolTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        pool_obj.remove()
        self.assertTrue(mock_pool_del.called)


class TestStorageVolumeTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_volumes')
    @mock.patch('delfin.db.volume_get_all')
    @mock.patch('delfin.db.volumes_delete')
    @mock.patch('delfin.db.volumes_update')
    @mock.patch('delfin.db.volumes_create')
    def test_sync_successful(self, mock_vol_create, mock_vol_update,
                             mock_vol_del, mock_vol_get_all, mock_list_vols,
                             get_lock):
        vol_obj = task.StorageVolumeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        vol_obj.sync()
        self.assertTrue(mock_list_vols.called)
        self.assertTrue(mock_vol_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the volumes from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the volumes to DB
        mock_list_vols.return_value = fake_storage_obj.list_volumes(context)
        mock_vol_get_all.return_value = list()
        vol_obj.sync()
        self.assertTrue(mock_vol_create.called)

        # update the volumes to DB
        mock_list_vols.return_value = vols_list
        mock_vol_get_all.return_value = vols_list
        vol_obj.sync()
        self.assertTrue(mock_vol_update.called)

        # delete the volumes to DB
        mock_list_vols.return_value = list()
        mock_vol_get_all.return_value = vols_list
        vol_obj.sync()
        self.assertTrue(mock_vol_del.called)

    @mock.patch('delfin.db.volume_delete_by_storage')
    def test_remove(self, mock_vol_del):
        vol_obj = task.StorageVolumeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        vol_obj.remove()
        self.assertTrue(mock_vol_del.called)
