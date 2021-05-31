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
import sys
from unittest import TestCase, mock

import paramiko

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import exception
from delfin import context
from delfin.drivers.hpe.hpe_3par.hpe_3parstor import Hpe3parStorDriver
from delfin.drivers.hpe.hpe_3par.alert_handler import AlertHandler
from delfin.drivers.hpe.hpe_3par.rest_handler import RestHandler
from delfin.drivers.hpe.hpe_3par.ssh_handler import SSHHandler
from delfin.drivers.utils.rest_client import RestClient
from delfin.drivers.utils.ssh_client import SSHPool

from requests import Session


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "hpe",
    "model": "3par",
    "rest": {
        "host": "10.0.0.1",
        "port": 8443,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    }
}

NODE_DATAS = """
                                  Control    Data        Cache
Node --Name--- -State-- Master IC SLED LED Mem(MB) Mem(MB) Available(%)
   0 1307327-0 Degraded Yes Yes unknown AmberBlnk    4096    6144            0
   1 1307327-1 Degraded No  Yes unknown AmberBlnk    4096    6144            0
"""
NODE_CPU_DATAS = """
----------------------------CPUs----------------------------
Node CPU -Manufacturer- -Serial- CPUSpeed(MHz) BusSpeed(MHz)
   0   0 GenuineIntel   --                2327       1334.57
   0   1 GenuineIntel   --                2327       1334.57
   0   2 GenuineIntel   --                2327       1334.57
   0   3 GenuineIntel   --                2327       1334.57
   1   0 GenuineIntel   --                2327       1332.19
   1   1 GenuineIntel   --                2327       1332.19
   1   2 GenuineIntel   --                2327       1332.19
   1   3 GenuineIntel   --                2327       1332.19
"""
NODE_VERSION = """
Node: 0
--------
System serial: 1000183
BIOS version: 4.8.34
OS version: 3.2.2.204
Reset reason: Unknown

Node: 1
--------
BIOS version: 4.8.34
OS version: 3.2.2.204
Reset reason: Unknown
"""
DISK_DATAS = """
                           ---Size(MB)--- ----Ports----
Id CagePos Type RPM State      Total   Free A      B      Cap(GB)
 0 0:14:0  FC    15 degraded  571904  83968 0:2:2* -----      600
 1 0:1:0   FC    15 degraded  571904  62720 0:2:2* -----      600
-----------------------------------------------------------------
16 total                     9150464 912896

"""
DISK_I_DATAS = """
Id CagePos State Node_WWN MFR Model Serial FW_Rev Protocol MediaType AdminTime
0 0:14:0  degraded WWN11  MFR111 Model11  Serial111 FW_Rev111 Pl  MT1 600
1 0:1:0   degraded WWN22  MFR2222  Model22  Serial222 FW_Rev222 P2   MT2 600

"""
PORT_DATAS = """
N:S:P Mode State -Node_WWN- -Port_WWN/HW_Addr- Type Protocol Label Ptner FState
0:0:1 target ready 2FF70002AC001C9F 20010002AC001C9F host FC - 1:0:1 none
0:0:2 target loss_sync 2FF70002AC001C9F 20020002AC001C9F  free FC - - -
0:2:2 target loss_sync 2FF70002AC001C9F 20020002AC001C9F  free FC - - -
0:6:1 target loss_sync 2FF70002AC001C9F 20020002AC001C9F  free FC - - -
--------------------------------------------------------------------------
   18
"""
PORT_I_DATAS = """
N:S:P Brand Model Rev Firmware Serial HWType
0:0:1 LSI 9205-8e 01 17.11.00.00 SP12430085 SAS
0:0:2 LSI 9205-8e 01 17.11.00.00 SP12430085 FC
0:1:1 QLOGIC QLE2672 02 8.1.1 RFE1228G50820 FC
0:1:2 QLOGIC QLE2672 02 8.1.1 RFE1228G50820 FC
0:2:1 QLOGIC QLE8242 58 4.15.2 PCGLTX0RC1G3PX CNA
"""
PORT_PER_DATAS = """
N:S:P Connmode ConnType CfgRate MaxRate Class2 UniqNodeWwn VCN Il TMWO SSAN
0:0:1 disk point 6Gbps 6Gbps n/a n/a n/a enabled n/a n/a
0:0:2 disk point 6Gbps 6Gbps n/a n/a n/a enabled n/a n/a
0:1:1 host point auto 16Gbps disabled disabled disabled enabled disabled n/a
0:1:2 host point auto 16Gbps disabled disabled disabled enabled disabled n/a
"""
PORT_ISCSI_DATAS = """
N:S:P State IPAddr Netmask/PrefixLen Gateway TPGT MTU Rate iAddr iPort ST VLAN
0:2:1 ready 1df9:7b7b:790::21 64 :: 21 1500 10Gbps :: 3205 21 Y
0:2:2 ready 10.99.1.3 255.255.255.0 0.0.0.0 22 1500 10Gbps 0.0.0.0 3205 22 Y
"""
PORT_RCIP_DATAS = """
N:S:P State ---HwAddr--- IPAddr Netmask Gateway  MTU Rate Duplex AutoNeg
0:6:1 loss_sync 0002AC684AAD 10.11.35.10 255.255.0.0 10.11.0.1 900 n/a n/a n/a
1:6:1   offline 0002AC6A3A0F              -           - - -  n/a n/a n/a
-----------------------------------------------------------------------------
    2
"""
PORT_C_DATAS = """
N:S:P      Mode Device Pos Config Topology   Rate Cls Mode_change
0:0:1    target RedHat_196   0  valid fabric  8Gbps   3     allowed
                 RedHat_196   0  valid fabric  8Gbps   3     allowe
0:0:2    target Dorado5000V3_F1   0  valid fabric  8Gbps   3     allowed
                Dorado5000V3_F1   0  valid fabric  8Gbps   3     allowed
--------------------------------------------------------------------------
  108
"""

CONTROLLER_RESULT = [
    {
        'name': '1307327-0',
        'storage_id': '12345',
        'native_controller_id': '0',
        'status': 'offline',
        'location': None,
        'soft_version': '3.2.2.204',
        'cpu_info': '4 * 2327 MHz',
        'memory_size': '10737418240'
    }]
DISK_RESULT = [
    {
        'name': '0:14:0',
        'storage_id': '12345',
        'native_disk_id': '0',
        'serial_number': 'Serial111',
        'manufacturer': 'MFR111',
        'model': 'Model11',
        'firmware': 'FW_Rev111',
        'speed': 15000,
        'capacity': 599684808704,
        'status': 'abnormal',
        'physical_type': 'fc',
        'logical_type': None,
        'health_score': None,
        'native_disk_group_id': None,
        'location': '0:14:0'
    }]
PORT_RESULT = [
    {
        'name': '0:0:1',
        'storage_id': '12345',
        'native_port_id': '0:0:1',
        'location': '0:0:1',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'sas',
        'logical_type': None,
        'speed': 8000000000,
        'max_speed': 6000000000,
        'native_parent_id': None,
        'wwn': '20010002AC001C9F',
        'mac_address': None,
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }]


def create_driver():
    kwargs = ACCESS_INFO

    SSHHandler.login = mock.Mock(
        return_value={"result": "success", "reason": "null"})

    m = mock.MagicMock(status_code=201)
    with mock.patch.object(Session, 'post', return_value=m):
        m.raise_for_status.return_value = 201
        m.json.return_value = {
            'key': 'deviceid123ABC456'
        }
        return Hpe3parStorDriver(**kwargs)


class TestHpe3parStorageDriver(TestCase):

    def test_a_init(self):
        kwargs = ACCESS_INFO
        SSHHandler.login = mock.Mock(
            return_value={""})
        RestHandler.login = mock.Mock(
            return_value={""})
        Hpe3parStorDriver(**kwargs)

    def test_b_initrest(self):
        m = mock.MagicMock()
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 201
            m.json.return_value = {
                'key': '1&2F28CA9FC1EA0B8EAB80E9D8FD'
            }
            kwargs = ACCESS_INFO
            rc = RestClient(**kwargs)
            RestHandler(rc)

    def test_d_get_storage(self):
        driver = create_driver()
        expected = {
            'name': 'hp3parf200',
            'vendor': 'HPE',
            'model': 'InServ F200',
            'status': 'abnormal',
            'serial_number': '1307327',
            'firmware_version': '3.1.2.484',
            'location': None,
            'total_capacity': 7793486594048,
            'raw_capacity': 9594956939264,
            'used_capacity': 6087847706624,
            'free_capacity': 1705638887424
        }

        ret = {
            "id": 7327,
            "name": "hp3parf200",
            "systemVersion": "3.1.2.484",
            "IPv4Addr": "100.157.92.213",
            "model": "InServ F200",
            "serialNumber": "1307327",
            "totalNodes": 2,
            "masterNode": 0,
            "onlineNodes": [
                0,
                1
            ],
            "clusterNodes": [
                0,
                1
            ],
            "chunkletSizeMiB": 256,
            "totalCapacityMiB": 9150464,
            "allocatedCapacityMiB": 5805824,
            "freeCapacityMiB": 1626624,
            "failedCapacityMiB": 1718016,
            "timeZone": "Asia/Shanghai"
        }

        RestHandler.get_capacity = mock.Mock(
            return_value={
                "allCapacity": {
                    "totalMiB": 9150464,
                    "allocated": {
                        "system": {
                            "totalSystemMiB": 1232384,
                            "internalMiB": 303104,
                            "spareMiB": 929280,
                            "spareUsedMiB": 307456,
                            "spareUnusedMiB": 621824
                        }
                    }
                }
            }
        )
        health_state = 'PDs that are degraded'
        SSHHandler.get_health_state = mock.Mock(return_value=health_state)
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(RestHandler, 'call', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = ret

            storage = driver.get_storage(context)
            self.assertDictEqual(storage, expected)

    def test_e_list_storage_pools(self):
        driver = create_driver()
        expected = [
            {
                'name': 'test',
                'storage_id': '12345',
                'native_storage_pool_id': '0',
                'description': 'Hpe 3par CPG:test',
                'status': 'normal',
                'storage_type': 'block',
                'total_capacity': 2003870679040,
                'subscribed_capacity': 2917892358144,
                'used_capacity': 1448343502848,
                'free_capacity': 555527176192
            }, {
                'name': 'cxd',
                'storage_id': '12345',
                'native_storage_pool_id': '1',
                'description': 'Hpe 3par CPG:cxd',
                'status': 'normal',
                'storage_type': 'block',
                'total_capacity': 1744025157632,
                'subscribed_capacity': 2200095948800,
                'used_capacity': 1696512081920,
                'free_capacity': 47513075712
            }
        ]

        ret = [
            {
                "total": 2,
                "members": [
                    {
                        "id": 0,
                        "uuid": "aa43f218-d3dd-4626-948f-8a160b0eac1d",
                        "name": "test",
                        "numFPVVs": 21,
                        "numTPVVs": 25,
                        "UsrUsage": {
                            "totalMiB": 1381504,
                            "rawTotalMiB": 1842004,
                            "usedMiB": 1376128,
                            "rawUsedMiB": 712703
                        },
                        "SAUsage": {
                            "totalMiB": 140800,
                            "rawTotalMiB": 422400,
                            "usedMiB": 5120,
                            "rawUsedMiB": 15360
                        },
                        "SDUsage": {
                            "totalMiB": 388736,
                            "rawTotalMiB": 518315,
                            "usedMiB": 0,
                            "rawUsedMiB": 0
                        },
                        "SAGrowth": {
                            "incrementMiB": 8192,
                            "LDLayout": {
                                "HA": 3,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "SDGrowth": {
                            "incrementMiB": 32768,
                            "LDLayout": {
                                "RAIDType": 3,
                                "HA": 3,
                                "setSize": 4,
                                "chunkletPosPref": 1,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": []
                    },
                    {
                        "id": 1,
                        "uuid": "c392910e-7648-4972-b594-47dd3d28f3ec",
                        "name": "cxd",
                        "numFPVVs": 14,
                        "numTPVVs": 319,
                        "UsrUsage": {
                            "totalMiB": 1418752,
                            "rawTotalMiB": 1702500,
                            "usedMiB": 1417984,
                            "rawUsedMiB": 568934
                        },
                        "SAUsage": {
                            "totalMiB": 56832,
                            "rawTotalMiB": 170496,
                            "usedMiB": 42752,
                            "rawUsedMiB": 128256
                        },
                        "SDUsage": {
                            "totalMiB": 187648,
                            "rawTotalMiB": 225179,
                            "usedMiB": 157184,
                            "rawUsedMiB": 188620
                        },
                        "SAGrowth": {
                            "incrementMiB": 8192,
                            "LDLayout": {
                                "HA": 3,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "SDGrowth": {
                            "incrementMiB": 32768,
                            "LDLayout": {
                                "RAIDType": 3,
                                "HA": 3,
                                "setSize": 6,
                                "chunkletPosPref": 1,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": []
                    }
                ]
            }
        ]

        with mock.patch.object(RestHandler, 'get_resinfo_call',
                               side_effect=ret):
            pools = driver.list_storage_pools(context)
            self.assertDictEqual(pools[0], expected[0])
            self.assertDictEqual(pools[1], expected[1])

        with mock.patch.object(RestHandler, 'get_all_pools',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

    def test_f_list_volumes(self):
        driver = create_driver()
        expected = [{
            'name': 'admin',
            'storage_id': '12345',
            'description': None,
            'status': 'normal',
            'native_volume_id': '0',
            'native_storage_pool_id': '',
            'wwn': '50002AC000001C9F',
            'type': 'thick',
            'total_capacity': 10737418240,
            'used_capacity': 10737418240,
            'free_capacity': 0,
            'compressed': True,
            'deduplicated': True
        }]
        ret = [{
            "members": [{
                "id": 0,
                "name": "admin",
                "provisioningType": 1,
                "copyType": 1,
                "baseId": 0,
                "readOnly": False,
                "state": 1,
                "userSpace": {
                    "reservedMiB": 10240,
                    "rawReservedMiB": 20480,
                    "usedMiB": 10240,
                    "freeMiB": 0
                },
                "sizeMiB": 10240,
                "wwn": "50002AC000001C9F"
            }]
        }]
        pool_ret = {
            "members": [{
                "id": 0,
                "uuid": "aa43f218-d3dd-4626-948f-8a160b0eac1d",
                "name": "test"
            }]
        }
        RestHandler.get_all_pools = mock.Mock(return_value=pool_ret)
        with mock.patch.object(RestHandler, 'get_resinfo_call',
                               side_effect=ret):
            volumes = driver.list_volumes(context)
            self.assertDictEqual(volumes[0], expected[0])

    def test_h_parse_alert(self):
        """ Success flow with all necessary parameters"""
        driver = create_driver()
        alert = {
            'sysUpTime': '1399844806',
            'snmpTrapOID': 'alertNotify',
            '1.3.6.1.4.1.12925.1.7.1.5.1': 'test_trap',
            '1.3.6.1.4.1.12925.1.7.1.6.1': 'This is a test trap',
            'nodeID': '0',
            '1.3.6.1.4.1.12925.1.7.1.2.1': '6',
            '1.3.6.1.4.1.12925.1.7.1.3.1': 'test time',
            '1.3.6.1.4.1.12925.1.7.1.7.1': '89',
            '1.3.6.1.4.1.12925.1.7.1.8.1': '2555934',
            '1.3.6.1.4.1.12925.1.7.1.9.1': '5',
            'serialNumber': '1307327',
            'transport_address': '100.118.18.100',
            'storage_id': '1c094309-70f2-4da3-ac47-e87cc1492ad5'
        }

        expected_alert_model = {
            'alert_id': '0x027001e',
            'alert_name': 'CPG growth non admin limit',
            'severity': 'NotSpecified',
            'category': 'Recovery',
            'type': 'EquipmentAlarm',
            'sequence_number': '89',
            'description': 'This is a test trap',
            'resource_type': 'Storage',
            'location': 'test_trap',
            'occur_time': '',
            'clear_category': 'Automatic'
        }
        context = {}
        alert_model = driver.parse_alert(context, alert)

        # Verify that all other fields are matching
        self.assertDictEqual(expected_alert_model, alert_model)

    def test_list_alert(self):
        """ Success flow with all necessary parameters"""
        driver = create_driver()
        alert = """
        Id : 1
        State : New
        MessageCode : 0x2200de
        Time : 2015-07-17 20:14:29 PDT
        Severity : Degraded
        Type : Component state change
        Message : Node 0, Power Supply 1, Battery 0 Degraded
        Component: 100.118.18.100

        """

        expected_alert = [{
            'alert_id': '0x2200de',
            'alert_name': 'Component state change',
            'severity': 'Warning',
            'category': 'Fault',
            'type': 'EquipmentAlarm',
            'sequence_number': '1',
            'occur_time': 1437135269000,
            'description': 'Node 0, Power Supply 1, Battery 0 Degraded',
            'resource_type': 'Storage',
            'location': '100.118.18.100'
        }]
        SSHHandler.get_all_alerts = mock.Mock(return_value=alert)
        alert_list = driver.list_alerts(context, None)
        expected_alert[0]['occur_time'] = alert_list[0]['occur_time']
        self.assertDictEqual(alert_list[0], expected_alert[0])

    @mock.patch.object(AlertHandler, 'clear_alert')
    def test_clear_alert(self, mock_clear_alert):
        driver = create_driver()
        alert_id = '230584300921369'
        driver.clear_alert(context, alert_id)
        self.assertEqual(mock_clear_alert.call_count, 1)

    def test_get_controllers(self):
        driver = create_driver()
        SSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        SSHHandler.do_exec = mock.Mock(
            side_effect=[NODE_DATAS, NODE_CPU_DATAS, NODE_VERSION])
        controllers = driver.list_controllers(context)
        self.assertDictEqual(controllers[0], CONTROLLER_RESULT[0])

    def test_get_disks(self):
        driver = create_driver()
        SSHHandler.do_exec = mock.Mock(side_effect=[DISK_DATAS, DISK_I_DATAS])
        disks = driver.list_disks(context)
        self.assertDictEqual(disks[0], DISK_RESULT[0])

    def test_get_ports(self):
        driver = create_driver()
        SSHHandler.do_exec = mock.Mock(
            side_effect=[PORT_DATAS, PORT_I_DATAS, PORT_PER_DATAS,
                         PORT_ISCSI_DATAS, PORT_RCIP_DATAS, PORT_C_DATAS,
                         PORT_RCIP_DATAS, PORT_RCIP_DATAS])
        ports = driver.list_ports(context)
        self.assertDictEqual(ports[0], PORT_RESULT[0])
