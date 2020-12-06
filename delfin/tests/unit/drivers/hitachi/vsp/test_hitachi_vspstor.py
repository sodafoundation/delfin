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
from delfin.drivers.hitachi.vsp.rest_handler import RestHandler
from delfin.drivers.hitachi.vsp.vsp_stor import HitachiVspDriver


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
    "vendor": "hitachi",
    "model": "vsp",
    "extra_attributes": {
        "array_id": "00112233"
    }
}
GET_DEVICE_ID = {
    "data": [
        {
            "storageDeviceId": "800000011633",
            "model": "VSP F1500",
            "serialNumber": 11633,
            "svpIp": "110.143.132.231",
        }
    ]
}
GET_ALL_POOLS = {
    "data": [
        {
            "poolId": 0,
            "poolStatus": "POLN",
            "usedCapacityRate": 56,
            "snapshotCount": 0,
            "poolName": "p3-1",
            "availableVolumeCapacity": 7796586,
            "totalPoolCapacity": 17821524,
            "numOfLdevs": 8,
            "firstLdevId": 4,
            "warningThreshold": 70,
            "depletionThreshold": 80,
            "virtualVolumeCapacityRate": -1,
            "isMainframe": False,
            "isShrinking": False,
            "locatedVolumeCount": 65,
            "totalLocatedCapacity": 15694896,
            "blockingMode": "NB",
            "totalReservedCapacity": 0,
            "reservedVolumeCount": 0,
            "poolType": "HDP",
            "duplicationNumber": 0,
            "dataReductionAccelerateCompCapacity": 0,
            "dataReductionCapacity": 0,
            "dataReductionBeforeCapacity": 0,
            "dataReductionAccelerateCompRate": 0,
            "duplicationRate": 0,
            "compressionRate": 0,
            "dataReductionRate": 0,
            "snapshotUsedCapacity": 0,
            "suspendSnapshot": True
        }
    ]
}
GET_SPECIFIC_STORAGE = {
    "storageDeviceId": "800000011633",
    "model": "VSP G350",
    "serialNumber": 11633,
    "svpIp": "51.10.192.90",
    "rmiPort": 1099,
    "dkcMicroVersion": "80-06-70/00",
    "communicationModes": [
        {
            "communicationMode": "lanConnectionMode"
        }
    ],
    "isSecure": False
}
GET_ALL_VOLUMES = {
    "data": [
        {
            "ldevId": 0,
            "clprId": 0,
            "emulationType": "OPEN-V",
            "byteFormatCapacity": "2.57 T",
            "blockCapacity": 5538459648,
            "composingPoolId": 1,
            "attributes": [
                "POOL"
            ],
            "raidLevel": "RAID5",
            "raidType": "3D+1P",
            "numOfParityGroups": 1,
            "parityGroupIds": [
                "5-1"
            ],
            "driveType": "SLB5E-M1R9SS",
            "driveByteFormatCapacity": "1.74 T",
            "driveBlockCapacity": 3750000030,
            "status": "NML",
            "mpBladeId": 1,
            "ssid": "0004",
            "resourceGroupId": 0,
            "isAluaEnabled": False
        }
    ]
}
TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.116.3.11.4.1.1.0.1',
    '1.3.6.1.4.1.116.5.11.4.2.3': 'eeeeeeeee',
    '1.3.6.1.4.1.116.5.11.4.2.7': 'ddddddd',
    '1.3.6.1.4.1.116.5.11.4.2.6': '14:10:10',
    '1.3.6.1.4.1.116.5.11.4.2.5': '2020/11/20',
    '1.3.6.1.4.1.116.5.11.4.2.2': ' System Version = 7.4.0.11 ',
    '1.3.6.1.4.1.116.5.11.4.2.4': '# FRU = None '
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
    'name': 'VSP F1500_110.143.132.231',
    'vendor': 'Hitachi',
    'description': 'Hitachi VSP Storage',
    'model': 'VSP F1500',
    'status': 'normal',
    'serial_number': '11633',
    'firmware_version': '80-06-70/00',
    'location': '',
    'raw_capacity': 18687222349824,
    'total_capacity': 18687222349824,
    'used_capacity': 10511909388288,
    'free_capacity': 8175312961536
}

volume_result = [
    {
        'name': 'ldev_0',
        'storage_id': '12345',
        'description': 'Hitachi VSP volume',
        'status': 'normal',
        'native_volume_id': '0',
        'native_storage_pool_id': None,
        'type': 'thick',
        'total_capacity': 2835691339776,
        'used_capacity': 2835691339776,
        'free_capacity': 0,
        'compressed': False,
        'deduplicated': False,
    }
]

pool_result = [
    {
        'name': 'p3-1',
        'storage_id': '12345',
        'native_storage_pool_id': '0',
        'description': 'Hitachi VSP Pool',
        'status': 'normal',
        'storage_type': 'block',
        'total_capacity': 18687222349824,
        'used_capacity': 10511909388288,
        'free_capacity': 8175312961536,
    }
]

alert_result = [
    {
        'location': 'test',
        'alarm_id': '223232',
        'sequence_number': '1111111',
        'description': 'test alert',
        'alert_name': 'someting wrong',
        'resource_type': 'Storage',
        'occur_time': 1605838210000,
        'category': 'Fault',
        'type': 'EquipmentAlarm',
        'severity': 'Major',
    }
]

trap_alert_result = {
    'alert_id': 'eeeeeeeee',
    'alert_name': 'ddddddd',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'ddddddd',
    'resource_type': 'Storage',
    'location': ' System Version = 7.4.0.11 '
}


def create_driver():
    kwargs = ACCESS_INFO

    RestHandler.get_system_info = mock.Mock(return_value=GET_DEVICE_ID)

    m = mock.MagicMock(status_code=200)
    with mock.patch.object(Session, 'post', return_value=m):
        m.raise_for_status.return_value = 201
        m.json.return_value = {
            "token": "97c13b8082444b36bc2103026205fa64",
            "sessionId": 9
        }
        return HitachiVspDriver(**kwargs)


class TestHitachiVspStorStorageDriver(TestCase):
    driver = create_driver()

    def test_initrest(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'get', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = GET_DEVICE_ID
            kwargs = ACCESS_INFO
            rh = RestHandler(**kwargs)
            rh.get_device_id()

    def test_get_storage(self):
        RestHandler.get_system_info = mock.Mock(return_value=GET_DEVICE_ID)
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[GET_ALL_POOLS, GET_SPECIFIC_STORAGE])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_storage_pools(self):
        RestHandler.get_rest_info = mock.Mock(return_value=GET_ALL_POOLS)
        pool = self.driver.list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])

    def test_list_volumes(self):
        RestHandler.get_rest_info = mock.Mock(return_value=GET_ALL_VOLUMES)
        volume = self.driver.list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    def test_list_alerts(self):
        result_list = []
        RestHandler.get_rest_info = mock.Mock(return_value=ALERT_INFO)
        RestHandler.get_rest_info = mock.Mock(return_value=ALERT_INFO)
        RestHandler.get_rest_info = mock.Mock(return_value=ALERT_INFO)
        alert_list = self.driver.list_alerts(context)
        self.assertEqual(alert_list, result_list)

    def test_parse_queried_alerts(self):
        alert_list = []
        HitachiVspDriver.parse_queried_alerts(ALERT_INFO, alert_list)
        self.assertDictEqual(alert_list[0], alert_result[0])

    def test_parse_alert(self):
        trap_alert = self.driver.parse_alert(context, TRAP_INFO)
        self.assertDictEqual(trap_alert, trap_alert_result)

    def test_rest_close_connection(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'delete', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = None
            re = self.driver.close_connection()
            self.assertIsNone(re)

    def test_rest_handler_cal(self):
        m = mock.MagicMock(status_code=403)
        with self.assertRaises(Exception) as exc:
            with mock.patch.object(Session, 'get', return_value=m):
                m.raise_for_status.return_value = 403
                m.json.return_value = None
                url = 'http://test'
                self.driver.rest_handler.call(url, '', 'GET')
        self.assertIn('Invalid ip or port', str(exc.exception))

    def test_reset_connection(self):
        RestHandler.logout = mock.Mock(return_value={})
        RestHandler.get_system_info = mock.Mock(return_value=GET_DEVICE_ID)
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 201
            m.json.return_value = {
                "token": "97c13b8082444b36bc2103026205fa64",
                "sessionId": 9
            }
            kwargs = ACCESS_INFO
            re = self.driver.reset_connection(context, **kwargs)
            self.assertIsNone(re)

    def test_err_storage_pools_err(self):
        with self.assertRaises(Exception) as exc:
            self.driver.list_storage_pools(context)
        self.assertIn('Invalid ip or port',
                      str(exc.exception))

    def test_err_volumes(self):
        with self.assertRaises(Exception) as exc:
            self.driver.list_volumes(context)
        self.assertIn('Invalid ip or port',
                      str(exc.exception))

    def test_list_volumes_call(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'get', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = GET_ALL_VOLUMES
            self.driver.list_volumes(context)
