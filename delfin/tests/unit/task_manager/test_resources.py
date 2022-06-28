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
from delfin.common import config # noqa
from delfin.drivers import fake_storage
from delfin.task_manager.tasks import resources
from delfin.task_manager.tasks.resources import StorageDeviceTask

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

ports_list = [{
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "name": "fake_pool_" + str(id),
    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "native_port_id": "fake_original_id_" + str(id),
    "location": "location_25",
    "connection_status": "disconnected",
    "health_status": "normal",
    "type": "iscsi",
    "logical_type": "service",
    "speed": 1000,
    "max_speed": 7200,
    "native_parent_id": "parent_id",
    "wwn": "wwn",
    "mac_address": "mac_352",
    "ipv4": "127.0.0.1",
    "ipv4_mask": "255.255.255.0",
    "ipv6": "",
    "ipv6_mask": ""
}
]

controllers_list = [{
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a222',
    "name": "fake_controller_" + str(id),
    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "native_controller_id": "fake_original_id_" + str(id),
    "status": "normal",
    "location": "loc_100",
    "soft_version": "ver_321",
    "cpu_info": "Intel Xenon",
    "memory_size": 200000,
}
]

disks_list = [{
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "name": "fake_pool_" + str(id),
    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    "native_disk_id": "fake_original_id_" + str(id),
    "serial_number": "serial_3299",
    "manufacturer": "Intel",
    "model": "model_4565",
    "firmware": "firmware_9541",
    "speed": 751,
    "capacity": 1074,
    "status": "offline",
    "physical_type": "sata",
    "logical_type": "cache",
    "health_score": 34,
    "native_disk_group_id": "",
}
]


quotas_list = [{
    "id": "251594c5-aac4-46ad-842f-3daca9176938",
    "native_quota_id": "fake_original_id_" + str(id),
    "name": "fake_qutoa_" + str(id),
    "storage_id": "793b26f9-6f16-4fd5-a6a2-d7453f050a41",
    "native_filesystem_id": "fake_filesystem_id_" + str(id),
    "native_qtree_id": "fake_qtree_id_" + str(id),
    "capacity_hard_limit": 1000,
    "capacity_soft_limit": 100,
    "file_hard_limit": 1000,
    "file_soft_limit": 100,
    "file_count": 10000,
    "used_capacity": 10000,
    "type": "user"
}
]


filesystems_list = [{
    "id": "fe760f5c-7b4c-42b2-b1ed-ecb4f0b6d6bc",
    "name": "fake_filesystem_" + str(id),
    "storage_id": "793b26f9-6f16-4fd5-a6a2-d7453f050a41",
    "native_filesystem_id": "fake_original_id_" + str(id),
    "status": "normal",
    "type": "thin",
    "security_mode": "unix",
    "total_capacity": 1055,
    "used_capacity": 812,
    "free_capacity": 243,
    "compressed": True,
    "deduplicated": False,
    "worm": "non_worm"
}
]


qtrees_list = [{
    "id": "251594c5-aac4-46ad-842f-3daca9176938",
    "name": "fake_qtree_" + str(id),
    "storage_id": "793b26f9-6f16-4fd5-a6a2-d7453f050a41",
    "native_qtree_id": "fake_original_id_" + str(id),
    "native_filesystem_id": "fake_filesystem_id_" + str(id),
    "path": "/",
    "security_mode": "native"
}
]


shares_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "fake_share_" + str(id),
    "storage_id": "793b26f9-6f16-4fd5-a6a2-d7453f050a41",
    "native_share_id": "fake_original_id_" + str(id),
    "native_filesystem_id": "fake_filesystem_id_" + str(id),
    "native_qtree_id": "859",
    "protocol": "nfs",
    "path": "/"
}
]

storage_host_initiators_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "storage_host_initiator_" + str(id),
    "description": "storage_host_initiator_" + str(id),
    "alias": "storage_host_initiator_" + str(id),
    "storage_id": "c5c91c98-91aa-40e6-85ac-37a1d3b32bda",
    "native_storage_host_initiator_id": "storage_host_initiator_" + str(id),
    "wwn": "wwn_" + str(id),
    "status": "Normal",
    "native_storage_host_id": "storage_host_" + str(id),
}
]

storage_hosts_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "storage_host_" + str(id),
    "description": "storage_host_" + str(id),
    "storage_id": "c5c91c98-91aa-40e6-85ac-37a1d3b32bda",
    "native_storage_host_id": "storage_host_" + str(id),
    "os_type": "linux",
    "status": "Normal",
    "ip_address": "1.2.3.4"
}
]

storage_hg_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "storage_host_group_" + str(id),
    "description": "storage_host_group_" + str(id),
    "storage_id": "c5c91c98-91aa-40e6-85ac-37a1d3b32bda",
    "native_storage_host_group_id": "storage_host_group_" + str(id),
}
]

storage_host_groups_list = {
    'storage_host_groups': storage_hg_list,
    'storage_host_grp_host_rels': ''
}
empty_shgs_list = {
    'storage_host_groups': list(),
    'storage_host_grp_host_rels': ''
}

pg_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "port_group_" + str(id),
    "description": "port_group_" + str(id),
    "storage_id": "c5c91c98-91aa-40e6-85ac-37a1d3b32bda",
    "native_port_group_id": "port_group_" + str(id),
}
]

port_groups_list = {
    "port_groups": pg_list,
    "port_grp_port_rels": '',
}

empty_port_groups_list = {
    "port_groups": list(),
    "port_grp_port_rels": '',
}

vg_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "volume_group_" + str(id),
    "description": "volume_group_" + str(id),
    "storage_id": "c5c91c98-91aa-40e6-85ac-37a1d3b32bda",
    "native_volume_group_id": "volume_group_" + str(id),
}
]

volume_groups_list = {
    'volume_groups': vg_list,
    'vol_grp_vol_rels': ''
}

empty_volume_groups_list = {
    'volume_groups': list(),
    'vol_grp_vol_rels': ''
}

masking_views_list = [{
    "id": "4e62c66a-39ef-43f2-9690-e936ca876574",
    "name": "masking_view_" + str(id),
    "description": "masking_view_" + str(id),
    "storage_id": "c5c91c98-91aa-40e6-85ac-37a1d3b32bda",
    "native_masking_view_id": "masking_view_" + str(id),
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
        storage_obj = resources.StorageDeviceTask(
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
        storage_obj = resources.StorageDeviceTask(
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
        pool_obj = resources.StoragePoolTask(
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
        pool_obj = resources.StoragePoolTask(
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
        vol_obj = resources.StorageVolumeTask(
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
        vol_obj = resources.StorageVolumeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        vol_obj.remove()
        self.assertTrue(mock_vol_del.called)


class TestStoragecontrollerTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_controllers')
    @mock.patch('delfin.db.controller_get_all')
    @mock.patch('delfin.db.controllers_delete')
    @mock.patch('delfin.db.controllers_update')
    @mock.patch('delfin.db.controllers_create')
    def test_sync_successful(self,
                             mock_controller_create, mock_controller_update,
                             mock_controller_del, mock_controller_get_all,
                             mock_list_controllers, get_lock):
        controller_obj = resources.StorageControllerTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        controller_obj.sync()

        self.assertTrue(mock_list_controllers.called)
        self.assertTrue(mock_controller_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the controllers from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the new controller to DB
        mock_list_controllers.return_value = \
            fake_storage_obj.list_controllers(context)
        mock_controller_get_all.return_value = list()
        controller_obj.sync()
        self.assertTrue(mock_controller_create.called)

        # update the new controller of DB
        mock_list_controllers.return_value = controllers_list
        mock_controller_get_all.return_value = controllers_list
        controller_obj.sync()
        self.assertTrue(mock_controller_update.called)

        # delete the new controller to DB
        mock_list_controllers.return_value = list()
        mock_controller_get_all.return_value = controllers_list
        controller_obj.sync()
        self.assertTrue(mock_controller_del.called)

    @mock.patch('delfin.db.controller_delete_by_storage')
    def test_remove(self, mock_controller_del):
        controller_obj = resources.StorageControllerTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        controller_obj.remove()
        self.assertTrue(mock_controller_del.called)


class TestStoragePortTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_ports')
    @mock.patch('delfin.db.port_get_all')
    @mock.patch('delfin.db.ports_delete')
    @mock.patch('delfin.db.ports_update')
    @mock.patch('delfin.db.ports_create')
    def test_sync_successful(self, mock_port_create, mock_port_update,
                             mock_port_del, mock_port_get_all, mock_list_ports,
                             get_lock):
        port_obj = resources.StoragePortTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        port_obj.sync()
        self.assertTrue(mock_list_ports.called)
        self.assertTrue(mock_port_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the ports from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the ports to DB
        mock_list_ports.return_value = fake_storage_obj.list_ports(context)
        mock_port_get_all.return_value = list()
        port_obj.sync()
        self.assertTrue(mock_port_create.called)

        # update the ports to DB
        mock_list_ports.return_value = ports_list
        mock_port_get_all.return_value = ports_list
        port_obj.sync()
        self.assertTrue(mock_port_update.called)

        # delete the ports to DB
        mock_list_ports.return_value = list()
        mock_port_get_all.return_value = ports_list
        port_obj.sync()
        self.assertTrue(mock_port_del.called)

    @mock.patch('delfin.db.port_delete_by_storage')
    def test_remove(self, mock_port_del):
        port_obj = resources.StoragePortTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        port_obj.remove()
        self.assertTrue(mock_port_del.called)


class TestStorageDiskTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_disks')
    @mock.patch('delfin.db.disk_get_all')
    @mock.patch('delfin.db.disks_delete')
    @mock.patch('delfin.db.disks_update')
    @mock.patch('delfin.db.disks_create')
    def test_sync_successful(self, mock_disk_create, mock_disk_update,
                             mock_disk_del, mock_disk_get_all, mock_list_disks,
                             get_lock):
        disk_obj = resources.StorageDiskTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        disk_obj.sync()
        self.assertTrue(mock_list_disks.called)
        self.assertTrue(mock_disk_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the disks from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the disks to DB
        mock_list_disks.return_value = fake_storage_obj.list_disks(context)
        mock_disk_get_all.return_value = list()
        disk_obj.sync()
        self.assertTrue(mock_disk_create.called)

        # update the disks to DB
        mock_list_disks.return_value = disks_list
        mock_disk_get_all.return_value = disks_list
        disk_obj.sync()
        self.assertTrue(mock_disk_update.called)

        # delete the disks to DB
        mock_list_disks.return_value = list()
        mock_disk_get_all.return_value = disks_list
        disk_obj.sync()
        self.assertTrue(mock_disk_del.called)

    @mock.patch('delfin.db.disk_delete_by_storage')
    def test_remove(self, mock_disk_del):
        disk_obj = resources.StorageDiskTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        disk_obj.remove()
        self.assertTrue(mock_disk_del.called)


class TestStorageQuotaTask(test.TestCase):
    # @mock.patch('delfin.drivers.api.API.list_quotas', 'get_lock')
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_quotas')
    @mock.patch('delfin.db.quota_get_all')
    @mock.patch('delfin.db.quotas_delete')
    @mock.patch('delfin.db.quotas_update')
    @mock.patch('delfin.db.quotas_create')
    def test_sync_successful(self, mock_quota_create,
                             mock_quota_update,
                             mock_quota_del, mock_quota_get_all,
                             mock_list_quotas,
                             get_lock):
        quota_obj = resources.StorageQuotaTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        quota_obj.sync()
        self.assertTrue(mock_list_quotas.called)
        self.assertTrue(mock_quota_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the quotas from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the quotas to DB
        mock_list_quotas.return_value =\
            fake_storage_obj.list_quotas(context)
        mock_quota_get_all.return_value = list()
        quota_obj.sync()
        self.assertTrue(mock_quota_create.called)

        # update the quotas to DB
        mock_list_quotas.return_value = quotas_list
        mock_quota_get_all.return_value = quotas_list
        quota_obj.sync()
        self.assertTrue(mock_quota_update.called)

        # delete the quotas to DB
        mock_list_quotas.return_value = list()
        mock_quota_get_all.return_value = quotas_list
        quota_obj.sync()
        self.assertTrue(mock_quota_del.called)

    @mock.patch('delfin.db.quota_delete_by_storage')
    def test_remove(self, mock_quota_del):
        quota_obj = resources.StorageQuotaTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        quota_obj.remove()
        self.assertTrue(mock_quota_del.called)


class TestStorageFilesystemTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_filesystems')
    @mock.patch('delfin.db.filesystem_get_all')
    @mock.patch('delfin.db.filesystems_delete')
    @mock.patch('delfin.db.filesystems_update')
    @mock.patch('delfin.db.filesystems_create')
    def test_sync_successful(self, mock_filesystem_create,
                             mock_filesystem_update,
                             mock_filesystem_del, mock_filesystem_get_all,
                             mock_list_filesystems,
                             get_lock):
        filesystem_obj = resources.StorageFilesystemTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        filesystem_obj.sync()
        self.assertTrue(mock_list_filesystems.called)
        self.assertTrue(mock_filesystem_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the filesystems from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the filesystems to DB
        mock_list_filesystems.return_value =\
            fake_storage_obj.list_filesystems(context)
        mock_filesystem_get_all.return_value = list()
        filesystem_obj.sync()
        self.assertTrue(mock_filesystem_create.called)

        # update the filesystems to DB
        mock_list_filesystems.return_value = filesystems_list
        mock_filesystem_get_all.return_value = filesystems_list
        filesystem_obj.sync()
        self.assertTrue(mock_filesystem_update.called)

        # delete the filesystems to DB
        mock_list_filesystems.return_value = list()
        mock_filesystem_get_all.return_value = filesystems_list
        filesystem_obj.sync()
        self.assertTrue(mock_filesystem_del.called)

    @mock.patch('delfin.db.filesystem_delete_by_storage')
    def test_remove(self, mock_filesystem_del):
        filesystem_obj = resources.StorageFilesystemTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        filesystem_obj.remove()
        self.assertTrue(mock_filesystem_del.called)


class TestStorageQtreeTask(test.TestCase):
    # @mock.patch('delfin.drivers.api.API.list_qtrees', 'get_lock')
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_qtrees')
    @mock.patch('delfin.db.qtree_get_all')
    @mock.patch('delfin.db.qtrees_delete')
    @mock.patch('delfin.db.qtrees_update')
    @mock.patch('delfin.db.qtrees_create')
    def test_sync_successful(self, mock_qtree_create,
                             mock_qtree_update,
                             mock_qtree_del, mock_qtree_get_all,
                             mock_list_qtrees,
                             get_lock):
        qtree_obj = resources.StorageQtreeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        qtree_obj.sync()
        self.assertTrue(mock_list_qtrees.called)
        self.assertTrue(mock_qtree_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the qtrees from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the qtrees to DB
        mock_list_qtrees.return_value =\
            fake_storage_obj.list_qtrees(context)
        mock_qtree_get_all.return_value = list()
        qtree_obj.sync()
        self.assertTrue(mock_qtree_create.called)

        # update the qtrees to DB
        mock_list_qtrees.return_value = qtrees_list
        mock_qtree_get_all.return_value = qtrees_list
        qtree_obj.sync()
        self.assertTrue(mock_qtree_update.called)

        # delete the qtrees to DB
        mock_list_qtrees.return_value = list()
        mock_qtree_get_all.return_value = qtrees_list
        qtree_obj.sync()
        self.assertTrue(mock_qtree_del.called)

    @mock.patch('delfin.db.qtree_delete_by_storage')
    def test_remove(self, mock_qtree_del):
        qtree_obj = resources.StorageQtreeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        qtree_obj.remove()
        self.assertTrue(mock_qtree_del.called)


class TestStorageShareTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_shares')
    @mock.patch('delfin.db.share_get_all')
    @mock.patch('delfin.db.shares_delete')
    @mock.patch('delfin.db.shares_update')
    @mock.patch('delfin.db.shares_create')
    def test_sync_successful(self, mock_share_create, mock_share_update,
                             mock_share_del, mock_share_get_all,
                             mock_list_shares, get_lock):
        share_obj = resources.StorageShareTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        share_obj.sync()
        self.assertTrue(mock_list_shares.called)
        self.assertTrue(mock_share_get_all.called)
        self.assertTrue(get_lock.called)

        # collect the shares from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # add the shares to DB
        mock_list_shares.return_value = fake_storage_obj.list_shares(context)
        mock_share_get_all.return_value = list()
        share_obj.sync()
        self.assertTrue(mock_share_create.called)

        # update the shares to DB
        mock_list_shares.return_value = shares_list
        mock_share_get_all.return_value = shares_list
        share_obj.sync()
        self.assertTrue(mock_share_update.called)

        # delete the shares to DB
        mock_list_shares.return_value = list()
        mock_share_get_all.return_value = shares_list
        share_obj.sync()
        self.assertTrue(mock_share_del.called)

    @mock.patch('delfin.db.share_delete_by_storage')
    def test_remove(self, mock_share_del):
        share_obj = resources.StorageShareTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        share_obj.remove()
        self.assertTrue(mock_share_del.called)


class TestStorageHostInitiatorTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_storage_host_initiators')
    @mock.patch('delfin.db.storage_host_initiators_delete_by_storage')
    @mock.patch('delfin.db.storage_host_initiators_create')
    def test_sync_successful(self, mock_storage_host_initiator_create,
                             mock_storage_host_initiator_delete_by_storage,
                             mock_list_storage_host_initiators, get_lock):
        storage_host_initiator_obj = resources.StorageHostInitiatorTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')

        # Collect the storage host initiators from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # Add the storage host initiators to DB
        mock_list_storage_host_initiators.return_value \
            = fake_storage_obj.list_storage_host_initiators(context)
        storage_host_initiator_obj.sync()
        self.assertTrue(mock_storage_host_initiator_delete_by_storage.called)
        self.assertTrue(mock_storage_host_initiator_create.called)

    @mock.patch('delfin.db.storage_host_initiators_delete_by_storage')
    def test_remove(self, mock_storage_host_initiators_del):
        storage_host_initiator_obj = resources.StorageHostInitiatorTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_host_initiator_obj.remove()
        self.assertTrue(mock_storage_host_initiators_del.called)


class TestStorageHostTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_storage_hosts')
    @mock.patch('delfin.db.storage_hosts_get_all')
    @mock.patch('delfin.db.storage_hosts_delete')
    @mock.patch('delfin.db.storage_hosts_update')
    @mock.patch('delfin.db.storage_hosts_create')
    def test_sync_successful(self, mock_storage_host_create,
                             mock_storage_host_update,
                             mock_storage_host_del,
                             mock_storage_hosts_get_all,
                             mock_list_storage_hosts, get_lock):
        storage_host_obj = resources.StorageHostTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_host_obj.sync()
        self.assertTrue(mock_list_storage_hosts.called)
        self.assertTrue(mock_storage_hosts_get_all.called)
        self.assertTrue(get_lock.called)

        # Collect the storage hosts from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # Add the storage hosts to DB
        mock_list_storage_hosts.return_value \
            = fake_storage_obj.list_storage_hosts(context)
        mock_storage_hosts_get_all.return_value = list()
        storage_host_obj.sync()
        self.assertTrue(mock_storage_host_create.called)

        # Update the storage hosts to DB
        mock_list_storage_hosts.return_value \
            = storage_hosts_list
        mock_storage_hosts_get_all.return_value \
            = storage_hosts_list
        storage_host_obj.sync()
        self.assertTrue(mock_storage_host_update.called)

        # Delete the storage hosts to DB
        mock_list_storage_hosts.return_value = list()
        mock_storage_hosts_get_all.return_value \
            = storage_hosts_list
        storage_host_obj.sync()
        self.assertTrue(mock_storage_host_del.called)

    @mock.patch('delfin.db.storage_hosts_delete_by_storage')
    def test_remove(self, mock_storage_hosts_del):
        storage_host_obj = resources.StorageHostTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_host_obj.remove()
        self.assertTrue(mock_storage_hosts_del.called)


class TestStorageHostGroupTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_storage_host_groups')
    @mock.patch('delfin.db.storage_host_groups_get_all')
    @mock.patch('delfin.db.storage_host_groups_delete')
    @mock.patch('delfin.db.storage_host_groups_update')
    @mock.patch('delfin.db.storage_host_groups_create')
    def test_sync_successful(self, mock_storage_host_group_create,
                             mock_storage_host_group_update,
                             mock_storage_host_group_del,
                             mock_storage_host_groups_get_all,
                             mock_list_storage_host_groups, get_lock):
        storage_host_group_obj = resources.StorageHostGroupTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_host_group_obj.sync()
        self.assertTrue(mock_list_storage_host_groups.called)
        self.assertTrue(mock_storage_host_groups_get_all.called)
        self.assertTrue(get_lock.called)

        # Collect the storage host groups from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # Add the storage host groups to DB
        mock_list_storage_host_groups.return_value \
            = fake_storage_obj.list_storage_host_groups(context)
        mock_storage_host_groups_get_all.return_value = list()
        storage_host_group_obj.sync()
        self.assertTrue(mock_storage_host_group_create.called)

        # Update the storage host groups to DB
        mock_list_storage_host_groups.return_value \
            = storage_host_groups_list
        mock_storage_host_groups_get_all.return_value \
            = storage_hg_list
        storage_host_group_obj.sync()
        self.assertTrue(mock_storage_host_group_update.called)

        # Delete the storage host groups to DB
        mock_list_storage_host_groups.return_value = empty_shgs_list
        mock_storage_host_groups_get_all.return_value \
            = storage_hg_list
        storage_host_group_obj.sync()
        self.assertTrue(mock_storage_host_group_del.called)

    @mock.patch('delfin.db.storage_host_groups_delete_by_storage')
    def test_remove(self, mock_storage_host_groups_del):
        storage_host_group_obj = resources.StorageHostGroupTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_host_group_obj.remove()
        self.assertTrue(mock_storage_host_groups_del.called)


class TestVolumeGroupTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_volume_groups')
    @mock.patch('delfin.db.volume_groups_get_all')
    @mock.patch('delfin.db.volume_groups_delete')
    @mock.patch('delfin.db.volume_groups_update')
    @mock.patch('delfin.db.volume_groups_create')
    def test_sync_successful(self, mock_volume_group_create,
                             mock_volume_group_update,
                             mock_volume_group_del,
                             mock_volume_groups_get_all,
                             mock_list_volume_groups, get_lock):
        volume_group_obj = resources.VolumeGroupTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        volume_group_obj.sync()
        self.assertTrue(mock_list_volume_groups.called)
        self.assertTrue(mock_volume_groups_get_all.called)
        self.assertTrue(get_lock.called)

        # Collect the volume groups from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # Add the volume groups to DB
        mock_list_volume_groups.return_value \
            = fake_storage_obj.list_volume_groups(context)
        mock_volume_groups_get_all.return_value = list()
        volume_group_obj.sync()
        self.assertTrue(mock_volume_group_create.called)

        # Update the volume groups to DB
        mock_list_volume_groups.return_value \
            = volume_groups_list
        mock_volume_groups_get_all.return_value \
            = vg_list
        volume_group_obj.sync()
        self.assertTrue(mock_volume_group_update.called)

        # Delete the volume groups to DB
        mock_list_volume_groups.return_value = empty_volume_groups_list
        mock_volume_groups_get_all.return_value \
            = vg_list
        volume_group_obj.sync()
        self.assertTrue(mock_volume_group_del.called)

    @mock.patch('delfin.db.volume_groups_delete_by_storage')
    def test_remove(self, mock_volume_groups_del):
        volume_group_obj = resources.VolumeGroupTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        volume_group_obj.remove()
        self.assertTrue(mock_volume_groups_del.called)


class TestPortGroupTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_port_groups')
    @mock.patch('delfin.db.port_groups_get_all')
    @mock.patch('delfin.db.port_groups_delete')
    @mock.patch('delfin.db.port_groups_update')
    @mock.patch('delfin.db.port_groups_create')
    def test_sync_successful(self, mock_port_group_create,
                             mock_port_group_update,
                             mock_port_group_del,
                             mock_port_groups_get_all,
                             mock_list_port_groups, get_lock):
        ctxt = context.get_admin_context()
        port_group_obj = resources.PortGroupTask(
            ctxt, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        port_group_obj.sync()
        self.assertTrue(mock_list_port_groups.called)
        self.assertTrue(mock_port_groups_get_all.called)
        self.assertTrue(get_lock.called)

        # Collect the storage host groups from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # Add the storage host groups to DB
        mock_list_port_groups.return_value \
            = fake_storage_obj.list_port_groups(context)
        mock_port_groups_get_all.return_value = list()
        port_group_obj.sync()
        self.assertTrue(mock_port_group_create.called)

        # Update the storage host groups to DB
        mock_list_port_groups.return_value \
            = port_groups_list
        mock_port_groups_get_all.return_value \
            = pg_list
        port_group_obj.sync()
        self.assertTrue(mock_port_group_update.called)

        # Delete the storage host groups to DB
        mock_list_port_groups.return_value = empty_port_groups_list
        mock_port_groups_get_all.return_value \
            = pg_list
        port_group_obj.sync()
        self.assertTrue(mock_port_group_del.called)

    @mock.patch('delfin.db.port_groups_delete_by_storage')
    def test_remove(self, mock_port_groups_del):
        port_group_obj = resources.PortGroupTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        port_group_obj.remove()
        self.assertTrue(mock_port_groups_del.called)


class TestMaskingViewTask(test.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('delfin.drivers.api.API.list_masking_views')
    @mock.patch('delfin.db.masking_views_get_all')
    @mock.patch('delfin.db.masking_views_delete')
    @mock.patch('delfin.db.masking_views_update')
    @mock.patch('delfin.db.masking_views_create')
    def test_sync_successful(self, mock_masking_view_create,
                             mock_masking_view_update,
                             mock_masking_view_del,
                             mock_masking_views_get_all,
                             mock_list_masking_views, get_lock):
        cntxt = context.get_admin_context()
        masking_view_obj = resources.MaskingViewTask(
            cntxt, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        masking_view_obj.sync()
        self.assertTrue(mock_list_masking_views.called)
        self.assertTrue(mock_masking_views_get_all.called)
        self.assertTrue(get_lock.called)

        # Collect the volume groups from fake_storage
        fake_storage_obj = fake_storage.FakeStorageDriver()

        # Add the volume groups to DB
        mock_list_masking_views.return_value \
            = fake_storage_obj.list_masking_views(context)
        mock_masking_views_get_all.return_value = list()
        masking_view_obj.sync()
        self.assertTrue(mock_masking_view_create.called)

        # Update the volume groups to DB
        mock_list_masking_views.return_value \
            = masking_views_list
        mock_masking_views_get_all.return_value \
            = masking_views_list
        masking_view_obj.sync()
        self.assertTrue(mock_masking_view_update.called)

        # Delete the volume groups to DB
        mock_list_masking_views.return_value = list()
        mock_masking_views_get_all.return_value \
            = masking_views_list
        masking_view_obj.sync()
        self.assertTrue(mock_masking_view_del.called)

    @mock.patch('delfin.db.masking_views_delete_by_storage')
    def test_remove(self, mock_masking_views_del):
        masking_view_obj = resources.MaskingViewTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        masking_view_obj.remove()
        self.assertTrue(mock_masking_views_del.called)
