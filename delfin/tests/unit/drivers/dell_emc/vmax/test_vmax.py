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


from unittest import TestCase, mock
from delfin import exception
from delfin import context
from delfin.drivers.dell_emc.vmax.vmax import VMAXStorageDriver
from delfin.drivers.dell_emc.vmax.rest import VMaxRest


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


VMAX_STORAGE_CONF = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vmax",
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


class TestVMAXStorageDriver(TestCase):

    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'set_rest_credentials')
    def test_init(self,
                  mock_rest, mock_version, mock_array):
        kwargs = VMAX_STORAGE_CONF

        mock_rest.return_value = None
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}

        driver = VMAXStorageDriver(**kwargs)
        self.assertEqual(driver.client.uni_version, '90')
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        with self.assertRaises(Exception) as exc:
            mock_rest.side_effect = exception.StorageBackendException
            VMAXStorageDriver(**kwargs)
        self.assertIn('Exception from Storage Backend', str(exc.exception))

        with self.assertRaises(Exception) as exc:
            mock_rest.side_effect = None
            mock_version.side_effect = exception.StorageBackendException
            VMAXStorageDriver(**kwargs)
        self.assertIn('Exception from Storage Backend', str(exc.exception))

        with self.assertRaises(Exception) as exc:
            mock_rest.side_effect = None
            mock_version.side_effect = ['V9.0.2.7', '90']
            mock_array.side_effect = exception.StorageBackendException
            VMAXStorageDriver(**kwargs)
        self.assertIn('Failed to connect to VMAX', str(exc.exception))

    @mock.patch.object(VMaxRest, 'get_system_capacity')
    @mock.patch.object(VMaxRest, 'get_vmax_array_details')
    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'set_rest_credentials')
    def test_get_storage(self,
                         mock_rest, mock_version, mock_array,
                         mock_array_details, mock_capacity):
        expected = {
            'name': 'VMAX250F-00112233',
            'vendor': 'Dell EMC',
            'description': '',
            'model': 'VMAX250F',
            'firmware_version': '5978.221.221',
            'status': 'normal',
            'serial_number': '00112233',
            'location': '',
            'total_capacity': 109951162777600,
            'used_capacity': 82463372083200,
            'free_capacity': 27487790694400,
            'raw_capacity': 1610612736000,
            'subscribed_capacity': 219902325555200
        }
        system_capacity = {
            'system_capacity': {
                'usable_total_tb': 100,
                'usable_used_tb': 75,
                'subscribed_total_tb': 200
            },
            'physicalCapacity': {
                'total_capacity_gb': 1500

            }
        }
        kwargs = VMAX_STORAGE_CONF

        mock_rest.return_value = None
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_array_details.return_value = {
            'model': 'VMAX250F',
            'ucode': '5978.221.221',
            'display_name': 'VMAX250F-00112233'}
        mock_capacity.return_value = system_capacity

        driver = VMAXStorageDriver(**kwargs)

        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        ret = driver.get_storage(context)
        self.assertDictEqual(ret, expected)

        mock_array_details.side_effect = exception.StorageBackendException
        with self.assertRaises(Exception) as exc:
            driver.get_storage(context)

        self.assertIn('Failed to get array details from VMAX',
                      str(exc.exception))

        mock_array_details.side_effect = [{
            'model': 'VMAX250F',
            'ucode': '5978.221.221',
            'display_name': 'VMAX250F-00112233'}]

        mock_capacity.side_effect = exception.StorageBackendException
        with self.assertRaises(Exception) as exc:
            driver.get_storage(context)

        self.assertIn('Failed to get capacity from VMAX',
                      str(exc.exception))

    @mock.patch.object(VMaxRest, 'get_srp_by_name')
    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'set_rest_credentials')
    def test_list_storage_pools(self,
                                mock_rest, mock_version,
                                mock_array, mock_srp):
        expected = [{
            'name': 'SRP_1',
            'storage_id': '12345',
            'native_storage_pool_id': 'SRP_ID',
            'description': 'Dell EMC VMAX Pool',
            'status': 'normal',
            'storage_type': 'block',
            'total_capacity': 109951162777600,
            'used_capacity': 82463372083200,
            'free_capacity': 27487790694400,
            'subscribed_capacity': 219902325555200
        }]
        pool_info = {
            'srp_capacity': {
                'usable_total_tb': 100,
                'usable_used_tb': 75,
                'subscribed_total_tb': 200
            },
            'srpId': 'SRP_ID'
        }
        kwargs = VMAX_STORAGE_CONF
        mock_rest.return_value = None
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_srp.side_effect = [{'srpId': ['SRP_1']}, pool_info]

        driver = VMAXStorageDriver(**kwargs)
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        ret = driver.list_storage_pools(context)
        self.assertDictEqual(ret[0], expected[0])

        mock_srp.side_effect = [{'srpId': ['SRP_1']},
                                exception.StorageBackendException]
        with self.assertRaises(Exception) as exc:
            driver.list_storage_pools(context)

        self.assertIn('Failed to get pool metrics from VMAX',
                      str(exc.exception))

        mock_srp.side_effect = [exception.StorageBackendException, pool_info]
        with self.assertRaises(Exception) as exc:
            driver.list_storage_pools(context)

        self.assertIn('Failed to get pool metrics from VMAX',
                      str(exc.exception))

    @mock.patch.object(VMaxRest, 'get_system_capacity')
    @mock.patch.object(VMaxRest, 'get_storage_group')
    @mock.patch.object(VMaxRest, 'get_volume')
    @mock.patch.object(VMaxRest, 'get_volume_list')
    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'set_rest_credentials')
    def test_list_volumes(self,
                          mock_rest, mock_version, mock_array,
                          mock_vols, mock_vol, mock_sg, mock_capacity):
        expected = [{
            'name': 'volume_1',
            'storage_id': '12345',
            'description': "Dell EMC VMAX 'thin device' volume",
            'type': 'thin',
            'status': 'available',
            'native_volume_id': '00001',
            'wwn': 'wwn123',
            'total_capacity': 104857600,
            'used_capacity': 10485760,
            'free_capacity': 94371840,
            'native_storage_pool_id': 'SRP_1',
            'compressed': True
        }]
        volumes = {
            'volumeId': '00001',
            'cap_mb': 100,
            'allocated_percent': 10,
            'status': 'Ready',
            'type': 'TDEV',
            'wwn': 'wwn123',
            'num_of_storage_groups': 1,
            'storageGroupId': ['SG_001'],
            'emulation': 'FBA'
        }
        volumes1 = {
            'volumeId': '00002',
            'cap_mb': 100,
            'allocated_percent': 10,
            'status': 'Ready',
            'type': 'TDEV',
            'wwn': 'wwn1234',
            'num_of_storage_groups': 0,
            'storageGroupId': [],
            'emulation': 'FBA'
        }
        volumes2 = {
            'volumeId': '00003',
            'cap_mb': 100,
            'allocated_percent': 10,
            'status': 'Ready',
            'type': 'TDEV',
            'wwn': 'wwn1234',
            'num_of_storage_groups': 0,
            'storageGroupId': [],
            'emulation': 'CKD'
        }
        storage_group_info = {
            'srp': 'SRP_1',
            'compression': True
        }
        default_srps = {
            'default_fba_srp': 'SRP_1',
            'default_ckd_srp': 'SRP_2'
        }
        kwargs = VMAX_STORAGE_CONF
        mock_rest.return_value = None
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_vols.side_effect = [['volume_1', 'volume_2', 'volume_3']]
        mock_vol.side_effect = [volumes, volumes1, volumes2]
        mock_sg.side_effect = [storage_group_info]
        mock_capacity.return_value = default_srps

        driver = VMAXStorageDriver(**kwargs)
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")
        ret = driver.list_volumes(context)
        self.assertDictEqual(ret[0], expected[0])

        mock_vols.side_effect = [['volume_1']]
        mock_vol.side_effect = [volumes]
        mock_sg.side_effect = [exception.StorageBackendException]
        with self.assertRaises(Exception) as exc:
            driver.list_volumes(context)

        self.assertIn('Failed to get list volumes from VMAX',
                      str(exc.exception))

        mock_vols.side_effect = [['volume_1']]
        mock_vol.side_effect = [exception.StorageBackendException]
        mock_sg.side_effect = [storage_group_info]
        with self.assertRaises(Exception) as exc:
            driver.list_volumes(context)

        self.assertIn('Failed to get list volumes from VMAX',
                      str(exc.exception))

        mock_vols.side_effect = [exception.StorageBackendException]
        mock_vol.side_effect = [volumes]
        mock_sg.side_effect = [storage_group_info]
        with self.assertRaises(Exception) as exc:
            driver.list_volumes(context)

        self.assertIn('Failed to get list volumes from VMAX',
                      str(exc.exception))
