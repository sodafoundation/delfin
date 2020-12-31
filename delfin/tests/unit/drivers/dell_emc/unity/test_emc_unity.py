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

from requests import Session

from delfin import context
from delfin.drivers.dell_emc.unity.rest_handler import RestHandler
from delfin.drivers.dell_emc.unity.unity import UNITYStorDriver


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "110.143.132.231",
        "port": "8443",
        "username": "username",
        "password": "cGFzc3dvcmQ="
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": "22",
        "username": "username",
        "password": "password",
        "host_key": "weqewrerwerwerwe"
    },
    "vendor": "dell_emc",
    "model": "Unity 350F",
    "extra_attributes": {
        "array_id": "00112233"
    }
}
GET_STORAGE = {
    "@base": "https://8.44.162.244/api/types/system/instances?fields=name,"
             "model,serialNumber,health&per_page=2000",
    "updated": "2020-10-19T08:38:21.009Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances/system",
            "updated": "2020-10-19T08:38:21.009Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/0"
                }
            ],
            "content": {
                "id": "0",
                "health": {
                    "value": 20,
                    "descriptionIds": [
                        "ALRT_SYSTEM_MAJOR_FAILURE"
                    ],
                    "descriptions": [
                        "The system has experienced one or more major failures"
                    ],
                    "resolutionIds": [
                        "fix_problems"
                    ],
                    "resolutions": [
                        "/help/webhelp/en_US/index.html?#unity_t_fix_"
                    ]
                },
                "name": "CETV3182000026",
                "model": "Unity 350F",
                "serialNumber": "CETV3182000026"
            }
        }
    ]
}
GET_CAPACITY = {
    "@base": "https://8.44.162.244/api/types/systemCapacity/instances",
    "updated": "2020-10-19T08:42:43.788Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances/systemCapacity",
            "updated": "2020-10-19T08:42:43.788Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/0"
                }
            ],
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
    "@base": "https://8.44.162.244/api/types/installedSoftwareVersion",
    "updated": "2020-10-19T08:42:43.788Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances",
            "updated": "2020-10-19T08:42:43.788Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/0"
                }
            ],
            "content": {
                "id": "4.7.1"
            }
        }
    ]
}
GET_DISK_INFO = {
    "@base": "https://8.44.162.244/api/types/disk/instances?fields=rawSize",
    "updated": "2020-10-19T08:42:43.788Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances/disk",
            "updated": "2020-10-19T08:42:43.788Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/0"
                }
            ],
            "content": {
                "id": "0",
                "rawSize": 2311766147072
            }
        }
    ]
}
GET_ALL_POOLS = {
    "@base": "https://8.44.162.244/api/types/pool/instances",
    "updated": "2020-10-19T08:45:43.217Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances/pool",
            "updated": "2020-10-19T08:45:43.217Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/pool_1"
                }
            ],
            "content": {
                "id": "pool_1",
                "type": 2,
                "health": {
                    "value": 7,
                    "descriptionIds": [
                        "ALRT_POOL_USER_THRESH",
                        "ALRT_POOL_DISK_EOL_SEVERE",
                        "ALRT_POOL_DRIVE_EOL_IN_60_DAYS"
                    ],
                    "descriptions": [
                        "This storage pool has exceeded the capacity",
                    ],
                    "resolutionIds": [
                        "pool_add_space"
                    ],
                    "resolutions": [
                        "/help/webhelp/en_US/index.html"
                    ]
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
GET_ALL_LUNS = {
    "@base": "https://8.44.162.244/api/types/lun/instances",
    "updated": "2020-10-19T08:55:15.776Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances/lun",
            "updated": "2020-10-19T08:55:15.776Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/sv_1"
                }
            ],
            "content": {
                "id": "sv_1",
                "type": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_VOL_OK"
                    ],
                    "descriptions": [
                        "The LUN is operating normally. No action is required."
                    ]
                },
                "name": "LUN-00",
                "sizeTotal": 107374182400,
                "sizeAllocated": 0,
                "wwn": "60:06:01:60:0B:00:49:00:BE:CE:6C:5C:56:C1:9D:D2",
                "pool": {
                    "id": "pool_1"
                }
            }
        },
        {
            "@base": "https://8.44.162.244/api/instances/lun",
            "updated": "2020-10-19T08:55:15.776Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/sv_2"
                }
            ],
            "content": {
                "id": "sv_2",
                "type": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_VOL_OK"
                    ],
                    "descriptions": [
                        "The LUN is operating normally. No action is required."
                    ]
                },
                "name": "LUN-01",
                "sizeTotal": 107374182400,
                "sizeAllocated": 0,
                "wwn": "60:06:01:60:0B:00:49:00:BE:CE:6C:5C:9B:86:B5:71",
                "pool": {
                    "id": "pool_1"
                }
            }
        }
    ]
}
GET_ALL_LUNS_NULL = {
    "@base": "https://8.44.162.244/api/types/alert/instances",
    "updated": "2020-10-19T09:02:57.980Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        },
        {
            "rel": "next",
            "href": "&page=2"
        }
    ],
    "entries": []
}
GET_ALL_ALERTS = {
    "@base": "https://8.44.162.244/api/types/alert/instances",
    "updated": "2020-10-19T09:02:57.980Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        },
        {
            "rel": "next",
            "href": "&page=2"
        }
    ],
    "entries": [
        {
            "@base": "https://8.44.162.244/api/instances/alert",
            "updated": "2020-10-19T09:02:57.980Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/alert_31523"
                }
            ],
            "content": {
                "id": "alert_31523",
                "severity": 4,
                "timestamp": "2020-10-12T09:09:52.609Z",
                "component": {
                    "id": "Host_87",
                    "resource": "host"
                },
                "messageId": "14:608fe",
                "message": "Host hpux11iv2 does not have any initiators"
                           " logged into the storage system.",
                "descriptionId": "ALRT_HOST_NO_LOGGED_IN_INITIATORS",
                "description": "The host does not have any initiators.",
                "resolutionId": "AddIntrWiz",
                "resolution": "/help/webhelp/en_US/index.html"
            }
        },
        {
            "@base": "https://8.44.162.244/api/instances/alert",
            "updated": "2020-10-19T09:02:57.980Z",
            "links": [
                {
                    "rel": "self",
                    "href": "/alert_31524"
                }
            ],
            "content": {
                "id": "alert_31524",
                "severity": 6,
                "timestamp": "2020-10-12T09:10:54.936Z",
                "component": {
                    "id": "Host_87",
                    "resource": "host"
                },
                "messageId": "14:608fc",
                "message": "Host hpux11iv2 is operating normally.",
                "descriptionId": "ALRT_COMPONENT_OK",
                "description": "The component is operating normally.",
                "resolutionId": "0",
                "resolution": "0"
            }
        }
    ]
}
GET_ALL_ALERTS_NULL = {
    "@base": "https://8.44.162.244/api/types/alert/instances",
    "updated": "2020-10-19T09:02:57.980Z",
    "links": [
        {
            "rel": "self",
            "href": "&page=1"
        },
        {
            "rel": "next",
            "href": "&page=2"
        }
    ],
    "entries": []
}
TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.103.1.18.2.0',
    '1.3.6.1.4.1.1139.103.1.18.1.1': 'eeeeeeeee',
    '1.3.6.1.4.1.1139.103.1.18.1.3': 'ddddddd',
    '1.3.6.1.4.1.1139.103.1.18.1.4': 'this is test',
    '1.3.6.1.4.1.1139.103.1.18.1.5': '2020/11/20 14:10:10',
    '1.3.6.1.4.1.1139.103.1.18.1.2': 'test'
}
ALERT_INFO = [
    {
        'location': "test",
        'alertId': '223232',
        'alertIndex': '1111111',
        'errorDetail': 'test alert',
        'errorSection': 'someting wrong',
        'occurenceTime': '2020-11-20T10:10:10',
        'errorLevel': 'Serious'
    }
]

storage_result = {
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
    'raw_capacity': 2311766147072,
    'firmware_version': '4.7.1'
}
pool_result = [
    {
        'native_storage_pool_id': 'pool_1',
        'status': 'normal',
        'free_capacity': 2311766147072,
        'name': 'pool1',
        'storage_type': 'block',
        'total_capacity': 8838774259712,
        'description': None,
        'subscribed_capacity': 310896039559168,
        'used_capacity': 6527008112640,
        'storage_id': '12345'
    }
]
volume_result = [
    {
        'used_capacity': 0,
        'free_capacity': 107374182400,
        'native_storage_pool_id': 'pool_1',
        'description': None,
        'deduplicated': None,
        'native_volume_id': 'sv_1',
        'total_capacity': 107374182400,
        'storage_id': '12345',
        'wwn': '60:06:01:60:0B:00:49:00:BE:CE:6C:5C:56:C1:9D:D2',
        'type': 'thick',
        'compressed': True,
        'name': 'LUN-00',
        'status': 'normal'
    }, {
        'used_capacity': 0,
        'free_capacity': 107374182400,
        'native_storage_pool_id': 'pool_1',
        'description': None,
        'deduplicated': None,
        'native_volume_id': 'sv_2',
        'total_capacity': 107374182400,
        'storage_id': '12345',
        'wwn': '60:06:01:60:0B:00:49:00:BE:CE:6C:5C:9B:86:B5:71',
        'type': 'thick',
        'compressed': True,
        'name': 'LUN-01',
        'status': 'normal'
    }
]
alert_result = [
    {
        'severity': 'Warning',
        'location': '',
        'occur_time': 1602464992000,
        'type': 'EquipmentAlarm',
        'sequence_number': 'alert_31523',
        'alert_name': 'Host hpux11iv2 does not have any initiators '
                      'logged into the storage system.',
        'resource_type': 'Storage',
        'alert_id': '14:608fe',
        'description': 'The host does not have any initiators.',
        'category': 'Fault'
    }, {
        'severity': 'Informational',
        'location': '',
        'occur_time': 1602465054000,
        'type': 'EquipmentAlarm',
        'sequence_number': 'alert_31524',
        'alert_name': 'Host hpux11iv2 is operating normally.',
        'resource_type': 'Storage',
        'alert_id': '14:608fc',
        'description': 'The component is operating normally.',
        'category': 'Fault'
    }
]
trap_result = {
    'alert_id': 'ddddddd',
    'alert_name': 'test',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'this is test',
    'resource_type': 'Storage',
    'location': 'eeeeeeeee'
}


def create_driver():
    kwargs = ACCESS_INFO
    m = mock.MagicMock(status_code=200)
    with mock.patch.object(Session, 'get', return_value=m):
        m.raise_for_status.return_value = 200
        m.json.return_value = {
            "EMC-CSRF-TOKEN": "97c13b8082444b36bc2103026205fa64"
        }
        return UNITYStorDriver(**kwargs)


class TestUNITYStorDriver(TestCase):
    driver = create_driver()

    def test_initrest(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'get', return_value=m):
            m.raise_for_status.return_value = 200
            kwargs = ACCESS_INFO
            re = RestHandler(**kwargs)
            self.assertIsNotNone(re)

    def test_get_storage(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[GET_STORAGE, GET_CAPACITY, GET_SOFT_VERSION,
                         GET_DISK_INFO])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_storage_pools(self):
        RestHandler.get_rest_info = mock.Mock(return_value=GET_ALL_POOLS)
        pool = self.driver.list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])

    def test_list_volumes(self):
        RestHandler.get_rest_info = mock.Mock(side_effect=[
            GET_ALL_LUNS, GET_ALL_LUNS_NULL])
        volume = self.driver.list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])
        self.assertDictEqual(volume[1], volume_result[1])

    def test_list_alerts(self):
        RestHandler.get_rest_info = mock.Mock(side_effect=[
            GET_ALL_ALERTS, GET_ALL_ALERTS_NULL])
        alert = self.driver.list_alerts(context)
        self.assertEqual(alert[0].get('alert_id'),
                         alert_result[0].get('alert_id'))
        self.assertEqual(alert[1].get('alert_id'),
                         alert_result[1].get('alert_id'))

    def test_parse_alert(self):
        trap = self.driver.parse_alert(context, TRAP_INFO)
        self.assertEqual(trap.get('alert_id'), trap_result.get('alert_id'))

    def test_rest_close_connection(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = None
            re = self.driver.close_connection()
            self.assertIsNone(re)

    def test_rest_handler_call(self):
        m = mock.MagicMock(status_code=403)
        with self.assertRaises(Exception) as exc:
            with mock.patch.object(Session, 'get', return_value=m):
                m.raise_for_status.return_value = 403
                m.json.return_value = None
                url = 'http://test'
                self.driver.rest_handler.call(url, '', 'GET')
        self.assertIn('Bad response from server', str(exc.exception))

    def test_reset_connection(self):
        RestHandler.logout = mock.Mock(return_value={})
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'get', return_value=m):
            m.raise_for_status.return_value = 201
            m.json.return_value = {
                "EMC-CSRF-TOKEN": "97c13b8082444b36bc2103026205fa64"
            }
            kwargs = ACCESS_INFO
            re = self.driver.reset_connection(context, **kwargs)
            self.assertIsNone(re)

    def test_err_storage_pools(self):
        with self.assertRaises(Exception) as exc:
            self.driver.list_storage_pools(context)
        self.assertIn('Bad response from server',
                      str(exc.exception))
