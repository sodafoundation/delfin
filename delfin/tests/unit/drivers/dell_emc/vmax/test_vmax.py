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

from requests.sessions import Session

from delfin import context
from delfin import exception
from delfin.common import config  # noqa
from delfin.common import constants
from delfin.drivers.dell_emc.vmax.rest import VMaxRest
from delfin.drivers.dell_emc.vmax.vmax import VMAXStorageDriver


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
        "port": 8443,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    },
    "extra_attributes": {
        "array_id": "00112233"
    }
}


class TestVMAXStorageDriver(TestCase):

    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'get_unisphere_version')
    def test_init(self, mock_unisphere_version,
                  mock_version, mock_array):
        kwargs = VMAX_STORAGE_CONF

        mock_version.return_value = ['V9.0.2.7', '90']
        mock_unisphere_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}

        driver = VMAXStorageDriver(**kwargs)
        self.assertEqual(driver.client.uni_version, '90')
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        with self.assertRaises(Exception) as exc:
            mock_version.side_effect = exception.InvalidIpOrPort
            VMAXStorageDriver(**kwargs)
        self.assertIn('Invalid ip or port', str(exc.exception))

        with self.assertRaises(Exception) as exc:
            mock_version.side_effect = exception.InvalidUsernameOrPassword
            VMAXStorageDriver(**kwargs)
        self.assertIn('Invalid username or password.', str(exc.exception))

    @mock.patch.object(VMaxRest, 'get_system_capacity')
    @mock.patch.object(VMaxRest, 'get_vmax_array_details')
    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'get_unisphere_version')
    def test_get_storage(self, mock_unisphere_version,
                         mock_version, mock_array,
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
        system_capacity_84 = {
            'total_usable_cap_gb': 100 * 1024,
            'total_allocated_cap_gb': 75 * 1024,
            'total_subscribed_cap_gb': 200 * 1024,
            'physicalCapacity': {
                'total_capacity_gb': 1500
            }
        }
        kwargs = VMAX_STORAGE_CONF

        mock_version.return_value = ['V9.0.2.7', '90']
        mock_unisphere_version.return_value = ['V9.0.2.7', '90']
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

        driver.client.uni_version = '84'
        mock_capacity.return_value = system_capacity_84
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
    @mock.patch.object(VMaxRest, 'get_unisphere_version')
    def test_list_storage_pools(self, mock_unisphere_version,
                                mock_version,
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
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_unisphere_version.return_value = ['V9.0.2.7', '90']
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
    @mock.patch.object(VMaxRest, 'get_unisphere_version')
    def test_list_volumes(self, mock_unisphere_version,
                          mock_version, mock_array,
                          mock_vols, mock_vol, mock_sg, mock_capacity):
        expected = \
            [
                {
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
                },
                {
                    'name': 'volume_2:id',
                    'storage_id': '12345',
                    'description': "Dell EMC VMAX 'thin device' volume",
                    'type': 'thin',
                    'status': 'available',
                    'native_volume_id': '00002',
                    'wwn': 'wwn1234',
                    'total_capacity': 104857600,
                    'used_capacity': 10485760,
                    'free_capacity': 94371840,
                    'native_storage_pool_id': 'SRP_1'
                }
            ]
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
            'volume_identifier': 'id',
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
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_unisphere_version.return_value = ['V9.0.2.7', '90']
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
        self.assertDictEqual(ret[1], expected[1])

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

    @mock.patch.object(VMaxRest, 'post_request')
    @mock.patch.object(VMaxRest, 'get_vmax_array_details')
    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'get_unisphere_version')
    def test_get_storage_performance(self, mock_unisphere_version,
                                     mock_version, mock_array,
                                     mock_array_details,
                                     mock_performnace):
        vmax_array_perf_resp_historic = {
            "expirationTime": 1600172441701,
            "count": 4321,
            "maxPageSize": 1000,
            "id": "d495891f-1607-42b7-ba8d-44d0786bd335_0",
            "resultList": {
                "result": [
                    {
                        "HostIOs": 296.1,
                        "HostMBWritten": 0.31862956,
                        "ReadResponseTime": 4.4177675,
                        "HostMBReads": 0.05016927,
                        "HostReads": 14.056666,
                        "HostWrites": 25.78,
                        "WriteResponseTime": 4.7228317,
                        "timestamp": 1598875800000
                    },
                    {
                        "HostIOs": 350.22998,
                        "HostMBWritten": 0.40306965,
                        "ReadResponseTime": 4.396796,
                        "HostMBReads": 0.043291014,
                        "HostReads": 13.213333,
                        "HostWrites": 45.97333,
                        "WriteResponseTime": 4.7806735,
                        "timestamp": 1598876100000
                    },
                    {
                        "HostIOs": 297.63333,
                        "HostMBWritten": 0.25046548,
                        "ReadResponseTime": 4.3915706,
                        "HostMBReads": 0.042753905,
                        "HostReads": 13.176666,
                        "HostWrites": 28.643333,
                        "WriteResponseTime": 4.8760557,
                        "timestamp": 1598876400000
                    }
                ]
            }
        }
        vmax_array_perf_resp_real_time = {
            "expirationTime": 1600172441701,
            "count": 4321,
            "maxPageSize": 1000,
            "id": "d495891f-1607-42b7-ba8d-44d0786bd335_0",
            "resultList": {
                "result": [
                    {
                        "HostIOs": 296.1,
                        "HostMBWritten": 0.31862956,
                        "ReadResponseTime": 4.4177675,
                        "HostMBReads": 0.05016927,
                        "HostReads": 14.056666,
                        "HostWrites": 25.78,
                        "WriteResponseTime": 4.7228317,
                        "timestamp": 1598875800000
                    }
                ]
            }
        }

        expected_historic = [
            constants.metric_struct(name='responseTime',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            9.1405992,
                                        1598876400000:
                                            9.2676263,
                                        1598876100000:
                                            9.1774695}
                                    ),
            constants.metric_struct(name='throughput',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            0.36879882999999997,
                                        1598876400000:
                                            0.293219385,
                                        1598876100000:
                                            0.446360664}
                                    ),
            constants.metric_struct(name='readThroughput',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            0.05016927,
                                        1598876100000:
                                            0.043291014,
                                        1598876400000:
                                            0.042753905}
                                    ),
            constants.metric_struct(name='writeThroughput',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            0.31862956,
                                        1598876100000:
                                            0.40306965,
                                        1598876400000:
                                            0.25046548}
                                    ),
            constants.metric_struct(name='requests',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000: 296.1,
                                        1598876100000:
                                            350.22998,
                                        1598876400000:
                                            297.63333}
                                    ),
            constants.metric_struct(name='readRequests',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            14.056666,
                                        1598876100000:
                                            13.213333,
                                        1598876400000:
                                            13.176666}
                                    ),
            constants.metric_struct(name='writeRequests',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000: 25.78,
                                        1598876100000:
                                            45.97333,
                                        1598876400000:
                                            28.643333}
                                    )
        ]

        expected_realtime = [
            constants.metric_struct(name='responseTime',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            9.1405992
                                    }
                                    ),
            constants.metric_struct(name='throughput',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            0.36879882999999997
                                    }
                                    ),
            constants.metric_struct(name='readThroughput',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            0.05016927
                                    }
                                    ),
            constants.metric_struct(name='writeThroughput',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type': 'array'
                                    },
                                    values={
                                        1598875800000: 0.31862956

                                    }
                                    ),
            constants.metric_struct(name='requests',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000: 296.1
                                    }
                                    ),
            constants.metric_struct(name='readRequests',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000:
                                            14.056666
                                    }
                                    ),
            constants.metric_struct(name='writeRequests',
                                    labels={
                                        'storage_id': '12345',
                                        'resource_type':
                                            'array'},
                                    values={
                                        1598875800000: 25.78
                                    }
                                    )
        ]

        kwargs = VMAX_STORAGE_CONF
        mock_version.return_value = ['V9.0.2.7', '90']
        mock_unisphere_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_array_details.return_value = {
            'model': 'VMAX250F',
            'ucode': '5978.221.221',
            'display_name': 'VMAX250F-00112233'}
        mock_performnace.return_value = 200, vmax_array_perf_resp_historic

        driver = VMAXStorageDriver(**kwargs)
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        ret = driver.collect_perf_metrics(context, '12345', "", 10000000,
                                          10900000)
        self.assertEqual(ret, expected_historic)

        mock_performnace.return_value = 200, vmax_array_perf_resp_real_time
        ret = driver.collect_perf_metrics(context, '12345', "", 10900000,
                                          10900000)
        self.assertEqual(ret, expected_realtime)

        mock_performnace.side_effect = \
            exception.StoragePerformanceCollectionFailed
        with self.assertRaises(Exception) as exc:
            ret = driver.collect_perf_metrics(context, '12345', "", 10000000,
                                              10900000)

        self.assertIn('Failed to collect performance metrics. Reason',
                      str(exc.exception))

    @mock.patch.object(Session, 'request')
    @mock.patch.object(VMaxRest, 'get_array_detail')
    @mock.patch.object(VMaxRest, 'get_uni_version')
    @mock.patch.object(VMaxRest, 'get_unisphere_version')
    def test_rest(self, mock_unisphere_version,
                  mock_version, mock_array,
                  mock_request):
        kwargs = VMAX_STORAGE_CONF

        mock_version.return_value = ['V9.0.2.7', '90']
        mock_unisphere_version.return_value = ['V9.0.2.7', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}

        driver = VMAXStorageDriver(**kwargs)
        self.assertEqual(driver.client.uni_version, '90')
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        mock_request.return_value = mock.Mock()
        mock_request.return_value.json = mock.Mock(return_value={})
        driver.reset_connection(context, **kwargs)
        driver.client.rest.session = None
        driver.client.rest.request('/session', 'GET')
        self.assertEqual(driver.client.uni_version, '90')
