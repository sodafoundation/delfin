# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import TestCase, mock

from delfin import context
from delfin.drivers.dell_emc.vplex.rest_handler import RestHandler
from delfin.drivers.dell_emc.vplex.vplex_stor import VplexStorageDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vplex",
    "rest": {
        "host": "8.44.162.250",
        "port": 443,
        "username": "service",
        "password": "Abcdef@123"
    }
}
TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.21.0',
    '1.3.6.1.4.1.1139.21.1.5.0': 'this is test',
    '1.3.6.1.4.1.1139.21.1.3.0': '123321'
}
trap_result = {
    'alert_id': '123321',
    'alert_name': 'this is test',
    'severity': 'Informational',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1614067724000,
    'description': 'this is test',
    'resource_type': 'Storage',
    'location': '',
    'match_key': '8c6d115258631625b625486f81b09532'
}
GET_ALL_CLUSTER = {
    "context": [{
        "children": [{
            "name": "cluster-1",
            "type": "cluster"
        }
        ]
    }
    ]
}
GET_ALL_LUNS = {
    "context": [
        {
            "children": [
                {
                    "name": "device_VPLEX_LUN0_1_vol",
                    "type": "virtual-volume"
                }
            ]
        }
    ]
}
GET_LUN = {
    "context": [
        {
            "attributes": [
                {
                    "name": "capacity",
                    "value": "644245094400B"
                },
                {
                    "name": "health-state",
                    "value": "ok"
                },
                {
                    "name": "operational-status",
                    "value": "ok"
                },
                {
                    "name": "supporting-device",
                    "value": "device__VPLEX_LUN0_1"
                },
                {
                    "name": "thin-enabled",
                    "value": "unavailable"
                },
                {
                    "name": "vpd-id",
                    "value": "VPD83T3:60000000000000000000000000000000"
                }
            ]
        }
    ]
}
volume_result = [{
    'name': 'device_VPLEX_LUN0_1_vol',
    'storage_id': '12345',
    'description': 'EMC VPlex volume',
    'status': 'normal',
    'native_volume_id': 'VPD83T3:60000000000000000000000000000000',
    'native_storage_pool_id': 'device__VPLEX_LUN0_1',
    'type': 'thick',
    'total_capacity': 644245094400,
    'used_capacity': 644245094400,
    'free_capacity': 0,
    'wwn': '60000000000000000000000000000000'
}
]
GET_ALL_POOLS = {
    "context": [
        {
            "children": [
                {
                    "name": "Device_KLM_test01",
                    "type": "local-device"
                }
            ]
        }
    ]
}
GET_POOL = {
    "context": [
        {
            "attributes": [
                {
                    "name": "capacity",
                    "value": "732212254720B"
                },
                {
                    "name": "health-state",
                    "value": "ok"
                },
                {
                    "name": "operational-status",
                    "value": "ok"
                },
                {
                    "name": "system-id",
                    "value": "Device_KLM_test01"
                },
                {
                    "name": "virtual-volume",
                    "value": "Volume_CLARiiON0041_KLM_test01"
                }
            ]
        }
    ]
}
pool_result = [
    {
        'name': 'Device_KLM_test01',
        'storage_id': '12345',
        'native_storage_pool_id': 'Device_KLM_test01',
        'description': 'EMC VPlex Pool',
        'status': 'normal',
        'storage_type': 'block',
        'total_capacity': 732212254720,
        'used_capacity': 732212254720,
        'free_capacity': 0
    }
]
GET_HEALH_CHECK = {
    "context": None,
    "message": "health-check -l",
    "exception": None,
    "custom-data": "Product Version: 6.1.0.01.00.13\n"
                   "Product Type: Local\n"
}
GET_CLUSTER = {
    "context": [
        {
            "type": "cluster",
            "parent": "/clusters",
            "attributes": [
                {
                    "name": "health-state",
                    "value": "major-failure"
                },
                {
                    "name": "operational-status",
                    "value": "degraded"
                },
                {
                    "name": "top-level-assembly",
                    "value": "FNM00000000000"
                }
            ],
        }
    ]
}
storage_result = {
    'name': 'cluster-1',
    'vendor': 'DELL EMC',
    'description': 'EMC VPlex Storage',
    'status': 'abnormal',
    'serial_number': 'FNM00000000000',
    'firmware_version': ' 6.1.0.01.00.13',
    'model': 'EMC VPLEX  Local',
    'location': '',
    'raw_capacity': 12754334882201,
    'total_capacity': 11654823254425,
    'used_capacity': 8983009998929,
    'free_capacity': 2671813255496,
    'subscribed_capacity': 0
}
GET_ALL_STORAGE_VOLUME_SUMMARY = {
    "custom-data": "Capacity                total         11.6T\n\n"
}
GET_ALL_POOLS_SUMMARY = {
    "custom-data": "total capacity    1.88T  total capacity    "
                   "8.68T  total capacity    10.6T\n\n"
}
GET_ALL_LUNS_SUMMARY = {
    "custom-data": "Total virtual-volume capacity is 8.17T."
}


class TestVplexStorDriver(TestCase):
    RestHandler.login = mock.Mock(return_value=None)

    def test_parse_alert(self):
        trap = VplexStorageDriver(**ACCESS_INFO).parse_alert(context,
                                                             TRAP_INFO)
        trap_result['occur_time'] = trap['occur_time']
        self.assertDictEqual(trap, trap_result)

    @mock.patch.object(RestHandler, 'get_cluster_resp')
    @mock.patch.object(RestHandler, 'get_virtual_volume_resp')
    @mock.patch.object(RestHandler, 'get_virtual_volume_by_name_resp')
    def test_list_volumes(self, mock_name, mock_volume, mock_cluster):
        mock_cluster.return_value = GET_ALL_CLUSTER
        mock_volume.return_value = GET_ALL_LUNS
        mock_name.return_value = GET_LUN
        volume = VplexStorageDriver(**ACCESS_INFO).list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    @mock.patch.object(RestHandler, 'get_cluster_resp')
    @mock.patch.object(RestHandler, 'get_devcie_resp')
    @mock.patch.object(RestHandler, 'get_device_by_name_resp')
    def test_list_storage_pools(self, mock_name, mock_device, mock_cluster):
        mock_cluster.return_value = GET_ALL_CLUSTER
        mock_device.return_value = GET_ALL_POOLS
        mock_name.return_value = GET_POOL
        pool = VplexStorageDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])

    def test_get_storage(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[GET_HEALH_CHECK, GET_ALL_CLUSTER, GET_CLUSTER,
                         GET_ALL_STORAGE_VOLUME_SUMMARY, GET_ALL_POOLS_SUMMARY,
                         GET_ALL_LUNS_SUMMARY])
        storage = VplexStorageDriver(**ACCESS_INFO).get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_alerts(self):
        with self.assertRaises(Exception) as exc:
            VplexStorageDriver(**ACCESS_INFO).list_alerts(context)
        self.assertEqual('list_alerts is not supported in model VPLEX',
                         str(exc.exception))
