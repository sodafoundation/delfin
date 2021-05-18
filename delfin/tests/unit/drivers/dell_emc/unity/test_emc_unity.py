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
from delfin.drivers.dell_emc.unity.rest_handler import RestHandler
from delfin.drivers.dell_emc.unity.unity import UnityStorDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "110.143.132.231",
        "port": "8443",
        "username": "username",
        "password": "cGFzc3dvcmQ="
    }
}
GET_STORAGE_NORMAL = {
    "entries": [
        {
            "content": {
                "id": "0",
                "health": {
                    "value": 5,
                },
                "name": "CETV3182000026",
                "model": "Unity 350F",
                "serialNumber": "CETV3182000026"
            }
        }
    ]
}
GET_STORAGE_ABNORMAL = {
    "entries": [
        {
            "content": {
                "id": "0",
                "health": {
                    "value": 20,
                },
                "name": "CETV3182000026",
                "model": "Unity 350F",
                "serialNumber": "CETV3182000026"
            }
        }
    ]
}
GET_CAPACITY = {
    "entries": [
        {
            "content": {
                "id": "0",
                "sizeFree": 2311766147072,
                "sizeTotal": 8838774259712,
                "sizeUsed": 6527008112640,
                "sizeSubscribed": 307567976775680,
                "totalLogicalSize": 307542206971904
            }
        }
    ]
}
GET_SOFT_VERSION = {
    "entries": [
        {
            "content": {
                "id": "4.7.1"
            }
        }
    ]
}
storage_normal_result = {
    'free_capacity': 2311766147072,
    'serial_number': 'CETV3182000026',
    'subscribed_capacity': 307567976775680,
    'used_capacity': 6527008112640,
    'vendor': 'DELL EMC',
    'location': '',
    'total_capacity': 8838774259712,
    'status': 'normal',
    'name': 'CETV3182000026',
    'model': 'Unity 350F',
    'raw_capacity': 8838774259712,
    'firmware_version': '4.7.1'
}
storage_abnormal_result = {
    'free_capacity': 2311766147072,
    'serial_number': 'CETV3182000026',
    'subscribed_capacity': 307567976775680,
    'used_capacity': 6527008112640,
    'vendor': 'DELL EMC',
    'location': '',
    'total_capacity': 8838774259712,
    'status': 'abnormal',
    'name': 'CETV3182000026',
    'model': 'Unity 350F',
    'raw_capacity': 8838774259712,
    'firmware_version': '4.7.1'
}
GET_ALL_POOLS = {
    "entries": [
        {
            "content": {
                "id": "pool_1",
                "health": {
                    "value": 7
                },
                "name": "pool1",
                "sizeFree": 2311766147072,
                "sizeTotal": 8838774259712,
                "sizeUsed": 6527008112640,
                "sizeSubscribed": 310896039559168
            }
        }
    ]
}
GET_ALL_ABNORMAL_POOLS = {
    "entries": [
        {
            "content": {
                "id": "pool_1",
                "health": {
                    "value": 20
                },
                "name": "pool1",
                "sizeFree": 2311766147072,
                "sizeTotal": 8838774259712,
                "sizeUsed": 6527008112640,
                "sizeSubscribed": 310896039559168
            }
        }
    ]
}
pool_result = [
    {
        'native_storage_pool_id': 'pool_1',
        'status': 'normal',
        'free_capacity': 2311766147072,
        'name': 'pool1',
        'storage_type': 'unified',
        'total_capacity': 8838774259712,
        'description': None,
        'subscribed_capacity': 310896039559168,
        'used_capacity': 6527008112640,
        'storage_id': '12345'
    }
]
pool_abnormal_result = [
    {
        'native_storage_pool_id': 'pool_1',
        'status': 'abnormal',
        'free_capacity': 2311766147072,
        'name': 'pool1',
        'storage_type': 'unified',
        'total_capacity': 8838774259712,
        'description': None,
        'subscribed_capacity': 310896039559168,
        'used_capacity': 6527008112640,
        'storage_id': '12345'
    }
]
GET_ALL_LUNS = {
    "entries": [
        {
            "content": {
                "id": "sv_1",
                "type": 2,
                "health": {
                    "value": 5
                },
                "name": "LUN-00",
                "sizeTotal": 107374182400,
                "sizeAllocated": 0,
                "wwn": "60:06:01:60:0B:00:49:00:BE:CE:6C:5C:56:C1:9D:D2",
                "pool": {
                    "id": "pool_1"
                }
            }
        }
    ]
}
GET_ALL_LUNS_NULL = {
    "entries": []
}
volume_result = [
    {
        'used_capacity': 0,
        'free_capacity': 107374182400,
        'native_storage_pool_id': 'pool_1',
        'description': None,
        'native_volume_id': 'sv_1',
        'total_capacity': 107374182400,
        'storage_id': '12345',
        'wwn': '60:06:01:60:0B:00:49:00:BE:CE:6C:5C:56:C1:9D:D2',
        'type': 'thick',
        'name': 'LUN-00',
        'status': 'normal'
    }
]
TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.103.1.18.2.0',
    '1.3.6.1.4.1.1139.103.1.18.1.1': 'eeeeeeeee',
    '1.3.6.1.4.1.1139.103.1.18.1.3': '14:60bba',
    '1.3.6.1.4.1.1139.103.1.18.1.4': 'this is test',
    '1.3.6.1.4.1.1139.103.1.18.1.5': '2020/11/20 14:10:10',
    '1.3.6.1.4.1.1139.103.1.18.1.2': 'test'
}
TRAP_NOT_IN_MAPPPING_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.103.1.18.2.0',
    '1.3.6.1.4.1.1139.103.1.18.1.1': 'eeeeeeeee',
    '1.3.6.1.4.1.1139.103.1.18.1.3': '14:60bba1',
    '1.3.6.1.4.1.1139.103.1.18.1.4': 'this is test',
    '1.3.6.1.4.1.1139.103.1.18.1.5': '2020/11/20 14:10:10',
    '1.3.6.1.4.1.1139.103.1.18.1.2': 'test'
}
trap_result = {
    'alert_id': '14:60bba',
    'alert_name': 'this is test',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'Storage resource allocation from one of the pools has '
                   'exceed the 85% threshold. Allocate more storage space '
                   'from the pool to the storage resource.',
    'resource_type': 'Storage',
    'location': 'eeeeeeeee',
    'match_key': '8c6d115258631625b625486f81b09532'
}
trap_not_in_mapping_result = {
    'alert_id': '14:60bba1',
    'alert_name': 'this is test',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'this is test',
    'resource_type': 'Storage',
    'location': 'eeeeeeeee',
    'match_key': '8c6d115258631625b625486f81b09532'
}
GET_ALL_ALERTS = {
    "entries": [
        {
            "content": {
                "id": "alert_31523",
                "severity": 4,
                "timestamp": "2020-10-12T09:09:52.609Z",
                "component": {
                    "id": "Host_87",
                    "resource": "host"
                },
                "messageId": "14:608fe",
                "message": "Host hpux11iv2 does not have any initiators",
                "description": "The host does not have any initiators."
            }
        }
    ]
}
GET_ALL_ALERTS_NULL = {
    "entries": []
}
alert_result = [
    {
        'severity': 'Warning',
        'location': 'Host_87',
        'occur_time': 1602464992000,
        'type': 'EquipmentAlarm',
        'alert_name': 'Host hpux11iv2 does not have any initiators',
        'resource_type': 'Storage',
        'alert_id': '14:608fe',
        'description': 'The host does not have any initiators.',
        'category': 'Fault',
        'sequence_number': 'alert_31523',
        'match_key': 'de23e7c25b5a46f029cb2f84f15a4a3a'
    }
]


class TestUNITYStorDriver(TestCase):

    @mock.patch.object(RestHandler, 'get_all_pools')
    def test_list_storage_pools(self, mock_pool):
        RestHandler.login = mock.Mock(return_value=None)
        mock_pool.return_value = GET_ALL_POOLS
        pool = UnityStorDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])
        mock_pool.return_value = GET_ALL_ABNORMAL_POOLS
        pool = UnityStorDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_abnormal_result[0])

    @mock.patch.object(RestHandler, 'get_storage')
    @mock.patch.object(RestHandler, 'get_capacity')
    @mock.patch.object(RestHandler, 'get_soft_version')
    def test_get_storage(self, mock_version, mock_capa, mock_base):
        RestHandler.login = mock.Mock(return_value=None)
        mock_version.return_value = GET_SOFT_VERSION
        mock_capa.return_value = GET_CAPACITY
        mock_base.return_value = GET_STORAGE_ABNORMAL
        storage = UnityStorDriver(**ACCESS_INFO).get_storage(context)
        self.assertDictEqual(storage, storage_abnormal_result)
        mock_base.return_value = GET_STORAGE_NORMAL
        storage = UnityStorDriver(**ACCESS_INFO).get_storage(context)
        self.assertDictEqual(storage, storage_normal_result)

    @mock.patch.object(RestHandler, 'get_all_luns')
    def test_list_volumes(self, mock_lun):
        RestHandler.login = mock.Mock(return_value=None)
        mock_lun.side_effect = [GET_ALL_LUNS, GET_ALL_LUNS_NULL]
        volume = UnityStorDriver(**ACCESS_INFO).list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    def test_parse_alert(self):
        RestHandler.login = mock.Mock(return_value=None)
        trap = UnityStorDriver(**ACCESS_INFO).parse_alert(context, TRAP_INFO)
        trap['occur_time'] = int(1605852610000)
        self.assertEqual(trap, trap_result)
        trap = UnityStorDriver(**ACCESS_INFO).parse_alert(
            context, TRAP_NOT_IN_MAPPPING_INFO)
        trap['occur_time'] = int(1605852610000)
        self.assertEqual(trap, trap_not_in_mapping_result)

    @mock.patch.object(RestHandler, 'remove_alert')
    def test_clear_alert(self, mock_remove):
        RestHandler.login = mock.Mock(return_value=None)
        alert_id = 101
        UnityStorDriver(**ACCESS_INFO).clear_alert(context, alert_id)
        self.assertEqual(mock_remove.call_count, 1)

    @mock.patch.object(RestHandler, 'get_all_alerts')
    def test_list_alerts(self, mock_alert):
        RestHandler.login = mock.Mock(return_value=None)
        mock_alert.side_effect = [GET_ALL_ALERTS, GET_ALL_ALERTS_NULL]
        alert = UnityStorDriver(**ACCESS_INFO).list_alerts(context)
        alert_result[0]['occur_time'] = alert[0]['occur_time']
        self.assertEqual(alert[0], alert_result[0])

    @mock.patch.object(RestHandler, 'call_with_token')
    def test_call_and_login(self, mock_token):
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(status_code=401,
                                                     text='Unauthorized')
            UnityStorDriver(**ACCESS_INFO).rest_handler.login()
        self.assertEqual('Invalid username or password.', str(exc.exception))
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(status_code=401,
                                                     text='Forbidden')
            UnityStorDriver(**ACCESS_INFO).rest_handler.login()
        self.assertEqual('Invalid ip or port.', str(exc.exception))
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(status_code=503)
            UnityStorDriver(**ACCESS_INFO).rest_handler.call('')
        self.assertIn('Exception from Storage Backend', str(exc.exception))
        RestHandler.login = mock.Mock(return_value=None)
        mock_token.return_value = mock.MagicMock(status_code=401)
        UnityStorDriver(**ACCESS_INFO).rest_handler.call('')

    @mock.patch.object(RestHandler, 'call')
    def test_get_rest_info(self, mock_rest):
        RestHandler.login = mock.Mock(return_value=None)
        mock_rest.return_value = mock.MagicMock(status_code=200)
        UnityStorDriver(**ACCESS_INFO).rest_handler.get_rest_info('')
        self.assertEqual(mock_rest.call_count, 1)
