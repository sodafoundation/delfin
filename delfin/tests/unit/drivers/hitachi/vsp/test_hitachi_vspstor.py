# Copyright 2021 The SODA Authors.
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
import sys
from unittest import TestCase, mock
sys.modules['delfin.cryptor'] = mock.Mock()

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
            "svpIp": "51.10.192.90",
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
        },
        {
            "ldevId": 0,
            "emulationType": "NOT DEFINED",
        }
    ]
}
GET_ALL_DISKS = {
    "data": [
        {
            "driveLocationId": "0-0",
            "driveTypeName": "SAS",
            "driveSpeed": 10000,
            "totalCapacity": 600,
            "driveType": "DKR5D-J600SS",
            "usageType": "DATA",
            "status": "NML",
            "parityGroupId": "1-6",
            "serialNumber": "123456789012345678901"
        }, {
            "driveLocationId": "0-1",
            "driveTypeName": "SAS",
            "driveSpeed": 10000,
            "totalCapacity": 600,
            "driveType": "DKR5D-J600SS",
            "usageType": "DATA",
            "status": "NML",
            "parityGroupId": "1-6",
            "serialNumber": "123456789012345678902"
        }, {
            "driveLocationId": "0-2",
            "driveTypeName": "SAS",
            "driveSpeed": 10000,
            "totalCapacity": 600,
            "driveType": "DKR5D-J600SS",
            "usageType": "DATA",
            "status": "NML",
            "parityGroupId": "1-6",
            "serialNumber": "123456789012345678903"
        }, {
            "driveLocationId": "0-3",
            "driveTypeName": "SAS",
            "driveSpeed": 10000,
            "totalCapacity": 600,
            "driveType": "DKR5D-J600SS",
            "usageType": "DATA",
            "status": "NML",
            "parityGroupId": "1-6",
            "serialNumber": "123456789012345678904"
        }
    ]
}
GET_ALL_CONTROLLERS = {
    "system": {
        "powerConsumption": 283
    },
    "ctls": [
        {
            "location": "CTL1",
            "status": "Normal",
            "temperature": 29,
            "temperatureStatus": "Normal",
            "type": "Controller Board"
        }, {
            "location": "CTL2",
            "status": "Normal",
            "temperature": 29,
            "temperatureStatus": "Normal",
            "charge": 100,
            "type": "Controller Board"
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
    'name': 'VSP F1500_51.10.192.90',
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
        'name': '00:00:00',
        'storage_id': '12345',
        'description': 'Hitachi VSP volume',
        'status': 'normal',
        'native_volume_id': '00:00:00',
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
        'alert_id': '223232',
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
    'location': ' System Version = 7.4.0.11 ',
    'match_key': '338d811d532553557ca33be45b6bde55'
}
controller_result = [
    {
        'name': 'CTL1',
        'storage_id': '12345',
        'native_controller_id': 'CTL1',
        'status': 'normal',
        'location': 'CTL1'
    }, {
        'name': 'CTL2',
        'storage_id': '12345',
        'native_controller_id': 'CTL2',
        'status': 'normal',
        'location': 'CTL2'
    }
]
disk_result = [
    {
        'name': '0-0',
        'storage_id': '12345',
        'native_disk_id': '0-0',
        'serial_number': '123456789012345678901',
        'speed': 10000,
        'capacity': 644245094400,
        'status': 'abnormal',
        'physical_type': 'sas',
        'logical_type': 'member',
        'native_disk_group_id': '1-6',
        'location': '0-0'
    }, {
        'name': '0-1',
        'storage_id': '12345',
        'native_disk_id': '0-1',
        'serial_number': '123456789012345678902',
        'speed': 10000,
        'capacity': 644245094400,
        'status': 'abnormal',
        'physical_type': 'sas',
        'logical_type': 'member',
        'native_disk_group_id': '1-6',
        'location': '0-1'
    }, {
        'name': '0-2',
        'storage_id': '12345',
        'native_disk_id': '0-2',
        'serial_number': '123456789012345678903',
        'speed': 10000,
        'capacity': 644245094400,
        'status': 'abnormal',
        'physical_type': 'sas',
        'logical_type': 'member',
        'native_disk_group_id': '1-6',
        'location': '0-2'
    }, {
        'name': '0-3',
        'storage_id': '12345',
        'native_disk_id': '0-3',
        'serial_number': '123456789012345678904',
        'speed': 10000,
        'capacity': 644245094400,
        'status': 'abnormal',
        'physical_type': 'sas',
        'logical_type': 'member',
        'native_disk_group_id': '1-6',
        'location': '0-3'
    }
]
GET_ALL_PORTS = {
    'data': [
        {
            'portId': 'CL1-A',
            'portType': 'FIBRE',
            'portSpeed': 'AUT',
            'loopId': 'EF',
            'fabricMode': True,
            'portConnection': 'PtoP',
            'lunSecuritySetting': True,
            'wwn': '50060e80124e3b00'
        },
        {
            'portId': 'CL1-B',
            'portType': 'ISCSI',
            'portSpeed': '10G',
            'loopId': '00',
            'fabricMode': False,
            'lunSecuritySetting': True
        }]
}
GET_DETAIL_PORT = {
         'portId': 'CL1-B',
         'portType': 'ISCSI',
         'portSpeed': '10G',
         'loopId': '00',
         'fabricMode': False,
         'lunSecuritySetting': True,
         'logins': [{
                  'loginIscsiName': 'iqn.1996-04.de.suse:01:a0cada20917f'
         }],
         'tcpOption': {
                  'ipv6Mode': False,
                  'selectiveAckMode': True,
                  'delayedAckMode': True,
                  'isnsService': False,
                  'tagVLan': False
         },
         'tcpMtu': 1500,
         'iscsiWindowSize': '64KB',
         'keepAliveTimer': 60,
         'tcpPort': '3260',
         'ipv4Address': '192.168.116.19',
         'ipv4Subnetmask': '255.255.0.0',
         'ipv4GatewayAddress': '0.0.0.0',
         'ipv6LinkLocalAddress': {
                  'status': 'INV',
                  'addressingMode': 'AM',
                  'address': 'fe80::'
         },
         'ipv6GlobalAddress': {
                  'status': 'INV',
                  'addressingMode': 'AM',
                  'address': '::'
         },
         'ipv6GatewayGlobalAddress': {
                  'status': 'INV',
                  'address': '::',
                  'currentAddress': '::'
         }
}
port_result = [{
         'name': 'CL1-A',
         'storage_id': '12345',
         'native_port_id': 'CL1-A',
         'location': 'CL1-A',
         'connection_status': 'connected',
         'health_status': 'normal',
         'type': 'fc',
         'logical_type': '',
         'max_speed': 8589934592,
         'mac_address': None,
         'wwn': '50060E80124E3B00',
         'ipv4': None,
         'ipv4_mask': None,
         'ipv6': None
},
{
         'name': 'CL1-B',
         'storage_id': '12345',
         'native_port_id': 'CL1-B',
         'location': 'CL1-B',
         'connection_status': 'connected',
         'health_status': 'normal',
         'type': 'eth',
         'logical_type': '',
         'max_speed': 10737418240,
         'mac_address': None,
         'wwn': None,
         'ipv4': '192.168.116.19',
         'ipv4_mask': '255.255.0.0',
         'ipv6': None
}]


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
        with self.assertRaises(Exception) as exc:
            RestHandler.get_rest_info = mock.Mock(return_value=ALERT_INFO)
            RestHandler.get_rest_info = mock.Mock(return_value=ALERT_INFO)
            RestHandler.get_rest_info = mock.Mock(return_value=ALERT_INFO)
            self.driver.list_alerts(context)
        self.assertEqual('list_alerts is not supported in model VSP F1500',
                         str(exc.exception))

    def test_parse_queried_alerts(self):
        alert_list = []
        HitachiVspDriver.parse_queried_alerts(ALERT_INFO, alert_list)
        self.assertEqual(alert_list[0].get('alert_id'),
                         alert_result[0].get('alert_id'))

    def test_parse_alert(self):
        trap_alert = self.driver.parse_alert(context, TRAP_INFO)
        trap_alert_result['occur_time'] = trap_alert['occur_time']
        self.assertEqual(trap_alert, trap_alert_result)

    @mock.patch.object(RestHandler, 'call_with_token')
    def test_get_token(self, mock_token):
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(
                status_code=403, text='KART30005-E')
            self.driver.rest_handler.get_token()
        self.assertEqual('Exception from Storage Backend: KART30005-E.',
                         str(exc.exception))

    @mock.patch.object(RestHandler, 'get_controllers')
    def test_list_controllers(self, mock_controller):
        RestHandler.login = mock.Mock(return_value=None)
        mock_controller.return_value = GET_ALL_CONTROLLERS
        controller = HitachiVspDriver(**ACCESS_INFO).list_controllers(context)
        self.assertEqual(controller, controller_result)

    @mock.patch.object(RestHandler, 'get_disks')
    def test_list_disks(self, mock_disk):
        RestHandler.login = mock.Mock(return_value=None)
        mock_disk.return_value = GET_ALL_DISKS
        disk = HitachiVspDriver(**ACCESS_INFO).list_disks(context)
        self.assertEqual(disk, disk_result)

    @mock.patch.object(RestHandler, 'get_all_ports')
    @mock.patch.object(RestHandler, 'get_detail_ports')
    def test_list_ports(self, mock_detail, mock_all):
        RestHandler.login = mock.Mock(return_value=None)
        mock_all.return_value = GET_ALL_PORTS
        mock_detail.return_value = GET_DETAIL_PORT
        port = HitachiVspDriver(**ACCESS_INFO).list_ports(context)
        self.assertEqual(port, port_result)
