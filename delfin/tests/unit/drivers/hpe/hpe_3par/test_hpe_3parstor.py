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
import unittest

from delfin import exception
from delfin import context
from delfin.drivers.hpe.hpe_3par.hpe_3parstor import Hpe3parStorDriver
from delfin.drivers.hpe.hpe_3par.rest_handler import RestHandler
from delfin.drivers.hpe.hpe_3par.ssh_handler import SSHHandler
from delfin.drivers.utils.rest_client import RestClient

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
        "password": "pass"
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "pass"
    }
}


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
        m = mock.MagicMock(status_code=100)
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 201
            m.json.return_value = {
                'key': 'deviceid123ABC456'
            }
            kwargs = ACCESS_INFO
            with self.assertRaises(Exception) as exc:
                Hpe3parStorDriver(**kwargs)
            self.assertIn('Unacceptable parameters', str(exc.exception))

    def test_b_initrest(self):
        m = mock.MagicMock()
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 201
            m.json.return_value = {
                'key': '1&2F28CA9FC1EA0B8EAB80E9D8FD'
            }
            kwargs = ACCESS_INFO
            with self.assertRaises(Exception) as exc:
                rc = RestClient(**kwargs)
                rh = RestHandler(rc)
                rh.login()
            self.assertIn('Unacceptable parameters', str(exc.exception))

    def test_c_initssh(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            command_str = 'ls -l'
            driver.sshhanlder.sshclient.doexec(context, command_str)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))

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
            'total_capacity': 8302708654080,
            'raw_capacity': 9594956939264,
            'subscribed_capacity': 6087847706624,
            'used_capacity': 6597069766656,
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
                'description': 'Hpe 3parStor CPG:test',
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
                'description': 'Hpe 3parStor CPG:cxd',
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
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_f_list_volumes(self):
        driver = create_driver()
        expected = [
            {
                'name': 'admin',
                'storage_id': '12345',
                'description': None,
                'status': 'normal',
                'native_volume_id': 0,
                'native_storage_pool_id': '',
                'wwn': '50002AC000001C9F',
                'type': 'thick',
                'total_capacity': 10737418240,
                'used_capacity': 10737418240,
                'free_capacity': 0,
                'compressed': True,
                'deduplicated': True
            }, {
                'name': 'C61.277',
                'storage_id': '12345',
                'description': None,
                'status': 'normal',
                'native_volume_id': 5115,
                'native_storage_pool_id': 'cxd',
                'wwn': '50002AC193FB1C9F',
                'type': 'thin',
                'total_capacity': 268435456,
                'used_capacity': 1207959552,
                'free_capacity': -939524096,
                'compressed': True,
                'deduplicated': True
            }, {
                'name': 'C61.278',
                'storage_id': '12345',
                'description': None,
                'status': 'normal',
                'native_volume_id': 5116,
                'native_storage_pool_id': 'cxd',
                'wwn': '50002AC193FC1C9F',
                'type': 'thin',
                'total_capacity': 268435456,
                'used_capacity': 1207959552,
                'free_capacity': -939524096,
                'compressed': True,
                'deduplicated': True
            }
        ]

        ret = [
            {
                "total": 380,
                "members": [
                    {
                        "id": 0,
                        "name": "admin",
                        "provisioningType": 1,
                        "copyType": 1,
                        "baseId": 0,
                        "readOnly": False,
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": [],
                        "adminSpace": {
                            "reservedMiB": 0,
                            "rawReservedMiB": 0,
                            "usedMiB": 0,
                            "freeMiB": 0
                        },
                        "snapshotSpace": {
                            "reservedMiB": 0,
                            "rawReservedMiB": 0,
                            "usedMiB": 0,
                            "freeMiB": 0
                        },
                        "userSpace": {
                            "reservedMiB": 10240,
                            "rawReservedMiB": 20480,
                            "usedMiB": 10240,
                            "freeMiB": 0
                        },
                        "sizeMiB": 10240,
                        "wwn": "50002AC000001C9F",
                        "creationTimeSec": 1400743667,
                        "creationTime8601": "2014-05-22T15:27:47+08:00",
                        "ssSpcAllocWarningPct": 0,
                        "ssSpcAllocLimitPct": 0,
                        "usrSpcAllocWarningPct": 0,
                        "usrSpcAllocLimitPct": 0,
                        "policies": {
                            "staleSS": True,
                            "oneHost": False,
                            "zeroDetect": False,
                            "system": True,
                            "caching": True
                        },
                        "uuid": "d88e03b7-79c6-4541-8506-bc5d56697cae"
                    },
                    {
                        "id": 5115,
                        "name": "C61.277",
                        "provisioningType": 2,
                        "copyType": 1,
                        "baseId": 5115,
                        "readOnly": False,
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": [],
                        "adminSpace": {
                            "reservedMiB": 128,
                            "rawReservedMiB": 384,
                            "usedMiB": 128,
                            "freeMiB": 0
                        },
                        "snapshotSpace": {
                            "reservedMiB": 512,
                            "rawReservedMiB": 614,
                            "usedMiB": 512,
                            "freeMiB": 0
                        },
                        "userSpace": {
                            "reservedMiB": 512,
                            "rawReservedMiB": 614,
                            "usedMiB": 512,
                            "freeMiB": 0
                        },
                        "sizeMiB": 256,
                        "wwn": "50002AC193FB1C9F",
                        "creationTimeSec": 1595299510,
                        "creationTime8601": "2020-07-21T10:45:10+08:00",
                        "ssSpcAllocWarningPct": 0,
                        "ssSpcAllocLimitPct": 0,
                        "usrSpcAllocWarningPct": 0,
                        "usrSpcAllocLimitPct": 0,
                        "policies": {
                            "staleSS": True,
                            "oneHost": False,
                            "zeroDetect": True,
                            "system": False,
                            "caching": True
                        },
                        "userCPG": "cxd",
                        "snapCPG": "cxd",
                        "uuid": "99669ae8-3c4b-4ceb-bb10-9e46e1da1eba"
                    },
                    {
                        "id": 5116,
                        "name": "C61.278",
                        "provisioningType": 2,
                        "copyType": 1,
                        "baseId": 5116,
                        "readOnly": False,
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": [],
                        "adminSpace": {
                            "reservedMiB": 128,
                            "rawReservedMiB": 384,
                            "usedMiB": 128,
                            "freeMiB": 0
                        },
                        "snapshotSpace": {
                            "reservedMiB": 512,
                            "rawReservedMiB": 614,
                            "usedMiB": 512,
                            "freeMiB": 0
                        },
                        "userSpace": {
                            "reservedMiB": 512,
                            "rawReservedMiB": 614,
                            "usedMiB": 512,
                            "freeMiB": 0
                        },
                        "sizeMiB": 256,
                        "wwn": "50002AC193FC1C9F",
                        "creationTimeSec": 1595299510,
                        "creationTime8601": "2020-07-21T10:45:10+08:00",
                        "ssSpcAllocWarningPct": 0,
                        "ssSpcAllocLimitPct": 0,
                        "usrSpcAllocWarningPct": 0,
                        "usrSpcAllocLimitPct": 0,
                        "policies": {
                            "staleSS": True,
                            "oneHost": False,
                            "zeroDetect": True,
                            "system": False,
                            "caching": True
                        },
                        "userCPG": "cxd",
                        "snapCPG": "cxd",
                        "uuid": "8575071b-163e-49ae-90dd-770f1fede25c"
                    }
                ]
            }
        ]
        with mock.patch.object(RestHandler, 'get_resinfo_call',
                               side_effect=ret):
            volumes = driver.list_volumes(context)
            self.assertDictEqual(volumes[0], expected[0])
            self.assertDictEqual(volumes[1], expected[1])

        with mock.patch.object(RestHandler, 'get_all_volumes',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

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
            'alert_id': '2555934',
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

    def test_i_clear_alert(self):
        driver = create_driver()
        alert = {'storage_id': 'abcd-1234-56789',
                 'storage_name': 'storage1', 'vendor': 'fake vendor',
                 'model': 'fake model',
                 'hwIsmReportingAlarmLocationInfo': 'location1',
                 'hwIsmReportingAlarmFaultTitle': 'Trap Test Alarm',
                 'hwIsmReportingAlarmFaultType': 'equipmentFault',
                 'hwIsmReportingAlarmFaultLevel': 'criticalAlarm',
                 'hwIsmReportingAlarmAlarmID': '4294967294',
                 'hwIsmReportingAlarmSerialNo': '4294967295',
                 'hwIsmReportingAlarmAdditionInfo': 'This is just for '
                                                    'testing.Please '
                                                    'ignore it',
                 'hwIsmReportingAlarmLocationAlarmID': '230584300921369',
                 'hwIsmReportingAlarmFaultTime': '2020-6-25,1:42:26.0'
                 }

        with self.assertRaises(Exception) as exc:
            driver.clear_alert(context, alert)
        self.assertIn('Exception in SSH protocol', str(exc.exception))

    def test_j_restlogout(self):
        m = mock.MagicMock()
        with mock.patch.object(Session, 'delete', return_value=m):
            m.raise_for_status.return_value = None
            m.json.return_value = None
            kwargs = ACCESS_INFO

            rc = RestClient(**kwargs)
            rh = RestHandler(rc)
            re = rh.logout()
            self.assertIsNone(re)


if __name__ == '__main__':
    unittest.main()
