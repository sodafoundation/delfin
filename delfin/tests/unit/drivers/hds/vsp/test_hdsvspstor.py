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
import unittest
from unittest import TestCase, mock
from delfin import exception
from delfin import context
from delfin.drivers.hds.vsp.vspstor import HdsVspDriver
from delfin.drivers.hds.vsp.rest_client import RestClient
from requests import Session

from delfin.drivers.utils.ssh_client import SSHClient


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "10.0.0.1",
        "port": "8443",
        "username": "username",
        "password": "password"
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": "22",
        "username": "username",
        "password": "password",
        "host_key": "weqewrerwerwerwe"
    },
    "vendor": "dell_emc",
    "model": "vmax",
    "extra_attributes": {
        "array_id": "00112233"
    }
}


def create_driver():
    kwargs = ACCESS_INFO

    SSHClient.login = mock.Mock(
        return_value={"result": "success", "reason": "null"})

    m = mock.MagicMock(status_code=201)
    with mock.patch.object(Session, 'put', return_value=m):
        m.raise_for_status.return_value = 201
        m.json.return_value = {
            "token": "97c13b8082444b36bc2103026205fa64",
            "sessionId": 9
        }
        return HdsVspDriver(**kwargs)


class TestHdsVspStorStorageDriver(TestCase):

    def test_a_init(self):
        m = mock.MagicMock(status_code=100)
        with mock.patch.object(Session, 'put', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = {
                "token": "97c13b8082444b36bc2103026205fa64",
                "sessionId": 9
            }
            kwargs = ACCESS_INFO
            with self.assertRaises(Exception) as exc:
                HdsVspDriver(**kwargs)
            self.assertIn('Unacceptable parameters', str(exc.exception))

    def test_b_initrest(self):
        m = mock.MagicMock()
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = {
                'token':
                '1&2F28CA9FC1EA0B8EAB80E9D8FD137E'
                'D6&8F4C30E46031518E793E316C77E65FC3',
                'sessionId': 10
            }
            kwargs = ACCESS_INFO
            with self.assertRaises(Exception) as exc:
                rc = RestClient(**kwargs)
                rc.login()
            self.assertIn('connect timeout', str(exc.exception))

    def test_c_initssh(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            commandStr = 'ls -l'
            driver.sshclient.doexec(context, commandStr)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))
    """
    def test_get_storage(self):
        driver = create_driver()
        expected = {
            'name': 'System name',
            'vendor': 'Owner of the system',
            'description': 'Any comment about the system',
            'model': 'System model',
            'status': 'abnormal',
            'serial_number': 'System serial number',
            'firmware_version': 'Storage system software version number',
            'location': 'Location of the system',
            'total_capacity': 2097152000,
            'used_capacity': 1572864000,
            'free_capacity': 524288000
        }

        ret = [{
            'id': 1234,
            'name': 'System name',
            'IPv4Addr': 'IPv4Addr123',
            'IPv6Addr': 'IPv6Addr123',
            'model': 'System model',
            'serialNumber': 'System serial number',
            'systemVersion': 'Storage system software version number',
            'patches': 'patches123',
            'totalNodes': 3,
            'masterNode': 111222,
            'onlineNodes': '[1,2,3]',
            'clusterNodes': '[11,12,13]',
            'chunkletSizeMiB': 1000,
            'totalCapacityMiB': 2000,
            'allocatedCapacityMiB': 3000,
            'freeCapacityMiB': 500,
            'failedCapacityMiB': 100,
            'location': 'Location of the system',
            'owner': 'Owner of the system',
            'contact': 'Contact of the system',
            'comment': 'Any comment about the system',
            'timeZone': 'Time zone where the system is located',
            'flashCachePolicy': 1,
            'licenseInfo': 'licenseInfo_Json',
            'parameters': 'parameters_Json',
            'readOnlyParameters': 'readOnlyParameters_Json'
        }]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            storage = driver.get_storage(context)
            self.assertDictEqual(storage, expected)
    """
    def test_d_list_storage_pools(self):
        driver = create_driver()
        """
        expected = {
            'name': 'pool_5',
            'storage_id': '12345',
            'native_storage_pool_id': 5,
            'description': 'Hitachi VSP Pool',
            'status': 'normal',
            'storage_type': 'file',
            'subscribed_capacity': 79951368,
            'total_capacity': 0,
            'used_capacity': 0.0,
            'free_capacity': 0.0,
        }
        """
        ret = [
            {
                "data": [
                    {
                        "poolId": 5,
                        "poolStatus": "POLN",
                        "usedCapacityRate": 0,
                        "usedPhysicalCapacityRate": 1,
                        "snapshotCount": 0,
                        "poolName": "pool_5",
                        "availableVolumeCapacity": 32042850,
                        "availablePhysicalVolumeCapacity": 20006364,
                        "totalPoolCapacity": 0,
                        "totalPhysicalCapacity": 20009724,
                        "numOfLdevs": 11,
                        "firstLdevId": 2304,
                        "warningThreshold": 70,
                        "depletionThreshold": 80,
                        "virtualVolumeCapacityRate": -1,
                        "isMainframe": 'false',
                        "isShrinking": 'false',
                        "locatedVolumeCount": 13,
                        "totalLocatedCapacity": 79951368,
                        "blockingMode": "NB",
                        "totalReservedCapacity": 0,
                        "reservedVolumeCount": 0,
                        "poolType": "HDP",
                        "duplicationLdevIds":
                        [65269, 65268, 65267,
                         65266, 65265, 65264, 65263, 65262],
                        "duplicationNumber": 8,
                        "dataReductionAccelerateCompCapacity": 206783585,
                        "dataReductionCapacity": 205901472,
                        "dataReductionBeforeCapacity": 210117216,
                        "dataReductionAccelerateCompRate": 87,
                        "duplicationRate": 42,
                        "compressionRate": 44,
                        "dataReductionRate": 97,
                        "dataReductionAccelerateCompIncludingSystemData":
                        {
                            "isReductionCapacityAvailable": 'true',
                            "reductionCapacity": 228372480,
                            "isReductionRateAvailable": 'true',
                            "reductionRate": 97
                        },
                        "dataReductionIncludingSystemData":
                        {
                            "isReductionCapacityAvailable": 'true',
                            "reductionCapacity": 186826752,
                            "isReductionRateAvailable": 'true',
                            "reductionRate": 79
                        },
                        "snapshotUsedCapacity": 0,
                        "suspendSnapshot": 'true',
                        "capacitiesExcludingSystemData":
                        {
                            "usedVirtualVolumeCapacity": 235253760,
                            "compressedCapacity": 0,
                            "dedupedCapacity": 101035296,
                            "reclaimedCapacity": 129142560,
                            "systemDataCapacity": 43351104,
                            "preUsedCapacity": 234393600,
                            "preCompressedCapacity": 0,
                            "preDedupredCapacity": 105247408
                        }
                    }
                ]
            }
        ]
        with mock.patch.object(RestClient, 'get_resinfo_call',
                               side_effect=ret):
            driver.list_storage_pools(context)
#            print("pool is %s" %(pools[0]))
#            self.assertDictEqual(pools[0], expected)
#            self.assertDictEqual(pools[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_pools',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_e_list_volumes(self):
        driver = create_driver()
        expected = [
            {
                'name': 'JH-26216_DP',
                'storage_id': '12345',
                'description': 'Hitachi VSP volume',
                'status': 'normal',
                'native_volume_id': 0,
                'native_storage_pool_id': 63,
                'wwn': '',
                'type': 'thick',
                'total_capacity': 1073741824,
                'used_capacity': 44040192,
                'free_capacity': 1029701632,
                'compressed': True,
                'deduplicated': True
            },
            {
                'name': 'JH-26216_DP',
                'storage_id': '12345',
                'description': 'Hitachi VSP volume',
                'status': 'normal',
                'native_volume_id': 1,
                'native_storage_pool_id': 63,
                'wwn': '',
                'type': 'thick',
                'total_capacity': 1073741824,
                'used_capacity': 0,
                'free_capacity': 1073741824,
                'compressed': False,
                'deduplicated': False
            }

        ]

        ret = [
            {
                "data": [
                    {
                        "ldevId": 0,
                        "clprId": 0,
                        "emulationType": "OPEN-V-CVS",
                        "byteFormatCapacity": "1.00 G",
                        "blockCapacity": 2097152,
                        "numOfPorts": 2,
                        "ports": [
                            {
                                "portId": "CL1-A",
                                "hostGroupNumber": 0,
                                "hostGroupName": "1A-G00",
                                "lun": 1
                            },
                            {
                                "portId": "CL2-A",
                                "hostGroupNumber": 0,
                                "hostGroupName": "2A-G00",
                                "lun": 1
                            }
                        ],
                        "attributes": [
                            "CVS",
                            "HDP"
                        ],
                        "label": "JH-26216_DP",
                        "status": "NML",
                        "mpBladeId": 2,
                        "ssid": "0012",
                        "poolId": 63,
                        "numOfUsedBlock": 86016,
                        "isFullAllocationEnabled": 'false',
                        "resourceGroupId": 0,
                        "dataReductionStatus": "ENABLED",
                        "dataReductionMode": "compression_deduplication",
                        "isAluaEnabled": 'false'
                    },
                    {
                        "ldevId": 1,
                        "clprId": 0,
                        "emulationType": "OPEN-V-CVS",
                        "byteFormatCapacity": "1.00 G",
                        "blockCapacity": 2097152,
                        "numOfPorts": 2,
                        "ports": [
                            {
                                "portId": "CL1-A",
                                "hostGroupNumber": 0,
                                "hostGroupName": "1A-G00",
                                "lun": 2
                            },
                            {
                                "portId": "CL2-A",
                                "hostGroupNumber": 0,
                                "hostGroupName": "2A-G00",
                                "lun": 2
                            }
                        ],
                        "attributes": [
                            "CVS",
                            "HDP"
                        ],
                        "label": "JH-26216_DP",
                        "status": "NML",
                        "mpBladeId": 0,
                        "ssid": "0012",
                        "poolId": 63,
                        "numOfUsedBlock": 0,
                        "isFullAllocationEnabled": 'false',
                        "resourceGroupId": 0,
                        "dataReductionStatus": "DISABLED",
                        "dataReductionMode": "disabled",
                        "isAluaEnabled": 'false'
                    }
                ]
            }
        ]
        with mock.patch.object(RestClient, 'get_resinfo_call',
                               side_effect=ret):
            volumes = driver.list_volumes(context)
#            print("volumes1 is %s" % (volumes[0]))
#            print("volumes2 is %s" % (volumes[1]))
            self.assertDictEqual(volumes[0], expected[0])
            self.assertDictEqual(volumes[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_volumes',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_g_clear_alert(self):
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
        self.assertIn('Exception from Storage Backend', str(exc.exception))

    def test_h_restlogout(self):
        m = mock.MagicMock()
        with mock.patch.object(Session, 'delete', return_value=m):
            m.raise_for_status.return_value = None
            m.json.return_value = None
            kwargs = ACCESS_INFO

            rc = RestClient(**kwargs)
            re = rc.logout()
            self.assertIsNone(re)


if __name__ == '__main__':
    unittest.main()
