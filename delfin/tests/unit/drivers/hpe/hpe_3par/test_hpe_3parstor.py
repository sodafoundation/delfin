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
from delfin.drivers.hpe.hpe_3par.rest_client import RestClient
from delfin.drivers.utils.ssh_client import SSHClient

from requests import Session


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vmax",
    "rest": {
        "host": "10.0.0.1",
        "port": "8443",
        "username": "user",
        "password": "pass",
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": "22",
        "username": "user",
        "password": "pass"
    },
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
                'key': '1&2F28CA9FC1EA0B8EAB80E9D8FD137ED6&8F4C30E46031518E793E316C77E65FC3'
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

    def test_d_get_storage(self):
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
            'raw_capacity': 2097152000,
            'subscribed_capacity': 3145728000,
            'used_capacity': 1572864000,
            'free_capacity': 524288000
        }

        ret = {
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
        }

        m = mock.MagicMock(status_code=200)
        with mock.patch.object(RestClient, 'call', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = ret

            storage = driver.get_storage(context)
            self.assertDictEqual(storage, expected)

    def test_e_list_storage_pools(self):
        driver = create_driver()
        expected = [
            {
                'name': 'name110',
                'storage_id': '12345',
                'native_storage_pool_id': 11,
                'description': 'Hpe 3parStor CPG:name110',
                'status': 'normal',
                'storage_type': 'block',
                'total_capacity': 5242880000,
                'subscribed_capacity': 314572800,
                'used_capacity': 4194304000,
                'free_capacity': 1048576000
            },
            {
                'name': 'name111',
                'storage_id': '12345',
                'native_storage_pool_id': 12,
                'description': 'Hpe 3parStor CPG:name111',
                'status': 'abnormal',
                'storage_type': 'block',
                'total_capacity': 5243928576,
                'subscribed_capacity': 315621376,
                'used_capacity': 4194304000,
                'free_capacity': 1049624576
            },
            {
                'name': 'name112',
                'storage_id': '12345',
                'native_storage_pool_id': 13,
                'description': 'Hpe 3parStor CPG:name112',
                'status': 'abnormal',
                'storage_type': 'block',
                'total_capacity': 5244977152,
                'subscribed_capacity': 316669952,
                'used_capacity': 4194304000,
                'free_capacity': 1050673152
            },
            {
                'name': 'name113',
                'storage_id': '12345',
                'native_storage_pool_id': 14,
                'description': 'Hpe 3parStor CPG:name113',
                'status': 'offline',
                'storage_type': 'block',
                'total_capacity': 5246025728,
                'subscribed_capacity': 317718528,
                'used_capacity': 4194304000,
                'free_capacity': 1051721728
            },
            {
                'name': 'name114',
                'storage_id': '12345',
                'native_storage_pool_id': 15,
                'description': 'Hpe 3parStor CPG:name114',
                'status': 'offline',
                'storage_type': 'block',
                'total_capacity': 5247074304,
                'subscribed_capacity': 318767104,
                'used_capacity': 4194304000,
                'free_capacity': 1052770304
            }
        ]

        ret = [
            {
                'total': 5,
                'members': [
                    {
                        'domain': 'domain110',
                        'id': 11,
                        'name': 'name110',
                        'numFPVVs': 1100,
                        'numTDVVs': 1111,
                        'numTPVVs': 1122,
                        'SAUsage': 'SAUsage_json0',
                        'SDUsage': 'SDUsage_json0',
                        'UsrUsage': 'UsrUsage_json0',
                        'uuid': 'uuid110',
                        'warningPct': 1133,
                        'SAGrowth': 'SAGrowth_json0',
                        'SDGrowth': 'SDGrowth_json0',
                        'state': 1,
                        'failedStates': 20,
                        'degradedStates': 30,
                        'additionalStates': 40,
                        'dedupCapable': True,
                        'tdvvVersion': 1,
                        'ddsRsvdMiB': 100,
                        'privateSpaceMiB': 200,
                        'sharedSpaceMiB': 300,
                        'freeSpaceMiB': 1000,
                        'totalSpaceMiB': 5000,
                        'rawSharedSpaceMiB': 100,
                        'rawFreeSpaceMiB': 200,
                        'rawTotalSpaceMiB': 300
                    },
                    {
                        'domain': 'domain111',
                        'id': 12,
                        'name': 'name111',
                        'numFPVVs': 1101,
                        'numTDVVs': 1112,
                        'numTPVVs': 1123,
                        'SAUsage': 'SAUsage_json1',
                        'SDUsage': 'SDUsage_json1',
                        'UsrUsage': 'UsrUsage_json1',
                        'uuid': 'uuid111',
                        'warningPct': 1134,
                        'SAGrowth': 'SAGrowth_json1',
                        'SDGrowth': 'SDGrowth_json1',
                        'state': 2,
                        'failedStates': 21,
                        'degradedStates': 31,
                        'additionalStates': 41,
                        'dedupCapable': True,
                        'tdvvVersion': 2,
                        'ddsRsvdMiB': 101,
                        'privateSpaceMiB': 201,
                        'sharedSpaceMiB': 301,
                        'freeSpaceMiB': 1001,
                        'totalSpaceMiB': 5001,
                        'rawSharedSpaceMiB': 101,
                        'rawFreeSpaceMiB': 201,
                        'rawTotalSpaceMiB': 301
                    },
                    {
                        'domain': 'domain112',
                        'id': 13,
                        'name': 'name112',
                        'numFPVVs': 1102,
                        'numTDVVs': 1113,
                        'numTPVVs': 1124,
                        'SAUsage': 'SAUsage_json2',
                        'SDUsage': 'SDUsage_json2',
                        'UsrUsage': 'UsrUsage_json2',
                        'uuid': 'uuid112',
                        'warningPct': 1135,
                        'SAGrowth': 'SAGrowth_json2',
                        'SDGrowth': 'SDGrowth_json2',
                        'state': 3,
                        'failedStates': 22,
                        'degradedStates': 32,
                        'additionalStates': 42,
                        'dedupCapable': True,
                        'tdvvVersion': 3,
                        'ddsRsvdMiB': 102,
                        'privateSpaceMiB': 202,
                        'sharedSpaceMiB': 302,
                        'freeSpaceMiB': 1002,
                        'totalSpaceMiB': 5002,
                        'rawSharedSpaceMiB': 102,
                        'rawFreeSpaceMiB': 202,
                        'rawTotalSpaceMiB': 302
                    },
                    {
                        'domain': 'domain113',
                        'id': 14,
                        'name': 'name113',
                        'numFPVVs': 1103,
                        'numTDVVs': 1114,
                        'numTPVVs': 1125,
                        'SAUsage': 'SAUsage_json3',
                        'SDUsage': 'SDUsage_json3',
                        'UsrUsage': 'UsrUsage_json3',
                        'uuid': 'uuid113',
                        'warningPct': 1136,
                        'SAGrowth': 'SAGrowth_json3',
                        'SDGrowth': 'SDGrowth_json3',
                        'state': 4,
                        'failedStates': 23,
                        'degradedStates': 33,
                        'additionalStates': 43,
                        'dedupCapable': True,
                        'tdvvVersion': 4,
                        'ddsRsvdMiB': 103,
                        'privateSpaceMiB': 203,
                        'sharedSpaceMiB': 303,
                        'freeSpaceMiB': 1003,
                        'totalSpaceMiB': 5003,
                        'rawSharedSpaceMiB': 103,
                        'rawFreeSpaceMiB': 203,
                        'rawTotalSpaceMiB': 303
                    },
                    {
                        'domain': 'domain114',
                        'id': 15,
                        'name': 'name114',
                        'numFPVVs': 1104,
                        'numTDVVs': 1115,
                        'numTPVVs': 1126,
                        'SAUsage': 'SAUsage_json4',
                        'SDUsage': 'SDUsage_json4',
                        'UsrUsage': 'UsrUsage_json4',
                        'uuid': 'uuid114',
                        'warningPct': 1137,
                        'SAGrowth': 'SAGrowth_json4',
                        'SDGrowth': 'SDGrowth_json4',
                        'state': 5,
                        'failedStates': 24,
                        'degradedStates': 34,
                        'additionalStates': 44,
                        'dedupCapable': True,
                        'tdvvVersion': 5,
                        'ddsRsvdMiB': 104,
                        'privateSpaceMiB': 204,
                        'sharedSpaceMiB': 304,
                        'freeSpaceMiB': 1004,
                        'totalSpaceMiB': 5004,
                        'rawSharedSpaceMiB': 104,
                        'rawFreeSpaceMiB': 204,
                        'rawTotalSpaceMiB': 304
                    }
                ]
            }
        ]

        with mock.patch.object(RestClient, 'get_resinfo_call',
                               side_effect=ret):
            pools = driver.list_storage_pools(context)
            self.assertDictEqual(pools[0], expected[0])
            self.assertDictEqual(pools[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_pools',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_f_list_volumes(self):
        driver = create_driver()
        expected = [
            {
                'name': 'name_0',
                'storage_id': '12345',
                'description': 'Comment associated with the volume0',
                'status': 'normal',
                'native_volume_id': 1,
                'native_storage_pool_id': 'userCPG_0/snapCPG_0',
                'wwn': 'Volume WWN_0',
                'type': 'thick',
                'total_capacity': 4194304000,
                'used_capacity': 2097152000,
                'free_capacity': 2097152000,
                'compressed': True,
                'deduplicated': True
            },
            {
                'name': 'name_1',
                'storage_id': '12345',
                'description': 'Comment associated with the volume1',
                'status': 'abnormal',
                'native_volume_id': 2,
                'native_storage_pool_id': 'userCPG_1/snapCPG_1',
                'wwn': 'Volume WWN_1',
                'type': 'thin',
                'total_capacity': 4195352576,
                'used_capacity': 2098200576,
                'free_capacity': 2097152000,
                'compressed': False,
                'deduplicated': False
            },
            {
                'name': 'name_2',
                'storage_id': '12345',
                'description': 'Comment associated with the volume2',
                'status': 'abnormal',
                'native_volume_id': 3,
                'native_storage_pool_id': 'userCPG_2/snapCPG_2',
                'wwn': 'Volume WWN_2',
                'type': 'thick',
                'total_capacity': 4196401152,
                'used_capacity': 2099249152,
                'free_capacity': 2097152000,
                'compressed': False,
                'deduplicated': False
            },
            {
                'name': 'name_3',
                'storage_id': '12345',
                'description': 'Comment associated with the volume3',
                'status': 'offline',
                'native_volume_id': 4,
                'native_storage_pool_id': 'userCPG_3/snapCPG_3',
                'wwn': 'Volume WWN_3',
                'type': 'thick',
                'total_capacity': 4197449728,
                'used_capacity': 2100297728,
                'free_capacity': 2097152000,
                'compressed': False,
                'deduplicated': False
            },
            {
                'name': 'name_4',
                'storage_id': '12345',
                'description': 'Comment associated with the volume4',
                'status': 'offline',
                'native_volume_id': 5,
                'native_storage_pool_id': 'userCPG_4/snapCPG_4',
                'wwn': 'Volume WWN_4',
                'type': 'thick',
                'total_capacity': 4198498304,
                'used_capacity': 2101346304,
                'free_capacity': 2097152000,
                'compressed': False,
                'deduplicated': False
            }
        ]

        ret = [
            {
                'total': 5,
                'members': [
                    {
                        'additionalStates': 1,
                        'adminSpace': 'adminSpace_json0',
                        'baseId': 11,
                        'comment': 'Comment associated with the volume0',
                        'capacityEfficiency': 'capacityEfficiency_json0',
                        'copyOf': 'copyOf0',
                        'copyType': 1,
                        'creationTime8601': 'creationTime8601_0',
                        'creationTimeSec': 1000,
                        'degradedStates': 11,
                        'domain': 'domain_0',
                        'expirationTime8601': 'expirationTime8601_0',
                        'expirationTimeSec': 22,
                        'failedStates': 33,
                        'compressionState': 1,
                        'deduplicationState': 1,
                        'id': 1,
                        'links': 'links_0',
                        'name': 'name_0',
                        'parentId': 100,
                        'physParentId': 200,
                        'policies': 'policies_json0',
                        'provisioningType': 1,
                        'readOnly': True,
                        'hostWriteMiB': 1000,
                        'totalUsedMiB': 2000,
                        'totalReservedMiB': 3000,
                        'sizeMiB': 4000,
                        'snapCPG': 'snapCPG_0',
                        'state': 1,
                        'userCPG': 'userCPG_0',
                        'wwn': 'Volume WWN_0'
                    },
                    {
                        'additionalStates': 2,
                        'adminSpace': 'adminSpace_json1',
                        'baseId': 12,
                        'comment': 'Comment associated with the volume1',
                        'capacityEfficiency': 'capacityEfficiency_json1',
                        'copyOf': 'copyOf1',
                        'copyType': 2,
                        'creationTime8601': 'creationTime8601_1',
                        'creationTimeSec': 1001,
                        'degradedStates': 12,
                        'domain': 'domain_1',
                        'expirationTime8601': 'expirationTime8601_1',
                        'expirationTimeSec': 23,
                        'failedStates': 34,
                        'compressionState': 2,
                        'deduplicationState': 2,
                        'id': 2,
                        'links': 'links_1',
                        'name': 'name_1',
                        'parentId': 101,
                        'physParentId': 201,
                        'policies': 'policies_json1',
                        'provisioningType': 2,
                        'readOnly': True,
                        'hostWriteMiB': 1001,
                        'totalUsedMiB': 2001,
                        'totalReservedMiB': 3001,
                        'sizeMiB': 4001,
                        'snapCPG': 'snapCPG_1',
                        'state': 2,
                        'userCPG': 'userCPG_1',
                        'wwn': 'Volume WWN_1'
                    },
                    {
                        'additionalStates': 3,
                        'adminSpace': 'adminSpace_json2',
                        'baseId': 13,
                        'comment': 'Comment associated with the volume2',
                        'capacityEfficiency': 'capacityEfficiency_json2',
                        'copyOf': 'copyOf2',
                        'copyType': 3,
                        'creationTime8601': 'creationTime8601_2',
                        'creationTimeSec': 1002,
                        'degradedStates': 13,
                        'domain': 'domain_2',
                        'expirationTime8601': 'expirationTime8601_2',
                        'expirationTimeSec': 24,
                        'failedStates': 35,
                        'compressionState': 3,
                        'deduplicationState': 3,
                        'id': 3,
                        'links': 'links_2',
                        'name': 'name_2',
                        'parentId': 102,
                        'physParentId': 202,
                        'policies': 'policies_json2',
                        'provisioningType': 3,
                        'readOnly': True,
                        'hostWriteMiB': 1002,
                        'totalUsedMiB': 2002,
                        'totalReservedMiB': 3002,
                        'sizeMiB': 4002,
                        'snapCPG': 'snapCPG_2',
                        'state': 3,
                        'userCPG': 'userCPG_2',
                        'wwn': 'Volume WWN_2'
                    },
                    {
                        'additionalStates': 4,
                        'adminSpace': 'adminSpace_json3',
                        'baseId': 14,
                        'comment': 'Comment associated with the volume3',
                        'capacityEfficiency': 'capacityEfficiency_json3',
                        'copyOf': 'copyOf3',
                        'copyType': 4,
                        'creationTime8601': 'creationTime8601_3',
                        'creationTimeSec': 1003,
                        'degradedStates': 14,
                        'domain': 'domain_3',
                        'expirationTime8601': 'expirationTime8601_3',
                        'expirationTimeSec': 25,
                        'failedStates': 36,
                        'compressionState': 4,
                        'deduplicationState': 4,
                        'id': 4,
                        'links': 'links_3',
                        'name': 'name_3',
                        'parentId': 103,
                        'physParentId': 203,
                        'policies': 'policies_json3',
                        'provisioningType': 4,
                        'readOnly': True,
                        'hostWriteMiB': 1003,
                        'totalUsedMiB': 2003,
                        'totalReservedMiB': 3003,
                        'sizeMiB': 4003,
                        'snapCPG': 'snapCPG_3',
                        'state': 4,
                        'userCPG': 'userCPG_3',
                        'wwn': 'Volume WWN_3'
                    },
                    {
                        'additionalStates': 5,
                        'adminSpace': 'adminSpace_json4',
                        'baseId': 15,
                        'comment': 'Comment associated with the volume4',
                        'capacityEfficiency': 'capacityEfficiency_json4',
                        'copyOf': 'copyOf4',
                        'copyType': 5,
                        'creationTime8601': 'creationTime8601_4',
                        'creationTimeSec': 1004,
                        'degradedStates': 15,
                        'domain': 'domain_4',
                        'expirationTime8601': 'expirationTime8601_4',
                        'expirationTimeSec': 26,
                        'failedStates': 37,
                        'compressionState': 5,
                        'deduplicationState': 5,
                        'id': 5,
                        'links': 'links_4',
                        'name': 'name_4',
                        'parentId': 104,
                        'physParentId': 204,
                        'policies': 'policies_json4',
                        'provisioningType': 5,
                        'readOnly': True,
                        'hostWriteMiB': 1004,
                        'totalUsedMiB': 2004,
                        'totalReservedMiB': 3004,
                        'sizeMiB': 4004,
                        'snapCPG': 'snapCPG_4',
                        'state': 5,
                        'userCPG': 'userCPG_4',
                        'wwn': 'Volume WWN_4'
                    }],
                'links': 'links_arrays'
            }
        ]
        with mock.patch.object(RestClient, 'get_resinfo_call',
                               side_effect=ret):
            volumes = driver.list_volumes(context)
            self.assertDictEqual(volumes[0], expected[0])
            self.assertDictEqual(volumes[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_volumes',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_g_list_alerts(self):
        driver = create_driver()
        expected = [
            {
                'category': 1,
                'location': 1,
                'event_type': 'Event type_0',
                'severity': 5,
                'probable_cause': 'description_0',
                'me_category': 'storage-subsystem',
                'occur_time': 'adminSpace_json0',
                'alarm_id': '110',
                'alarm_name': 'messageCode_0',
                'device_alert_sn': '110'
            },
            {
                'category': 1,
                'location': 2,
                'event_type': 'Event type_1',
                'severity': 1,
                'probable_cause': 'description_1',
                'me_category': 'storage-subsystem',
                'occur_time': 'adminSpace_json1',
                'alarm_id': '111',
                'alarm_name': 'messageCode_1',
                'device_alert_sn': '111'
            },
            {
                'category': 1,
                'location': 3,
                'event_type': 'Event type_2',
                'severity': 2,
                'probable_cause': 'description_2',
                'me_category': 'storage-subsystem',
                'occur_time': 'adminSpace_json2',
                'alarm_id': '112',
                'alarm_name': 'messageCode_2',
                'device_alert_sn': '112'
            },
            {
                'category': 1,
                'location': 4,
                'event_type': 'Event type_3',
                'severity': 5,
                'probable_cause': 'description_3',
                'me_category': 'storage-subsystem',
                'occur_time': 'adminSpace_json3',
                'alarm_id': '113',
                'alarm_name': 'messageCode_3',
                'device_alert_sn': '113'
            },
            {
                'category': 1,
                'location': 5,
                'event_type': 'Event type_4',
                'severity': 5,
                'probable_cause': 'description_4',
                'me_category': 'storage-subsystem',
                'occur_time': 'adminSpace_json4',
                'alarm_id': '114',
                'alarm_name': 'messageCode_4',
                'device_alert_sn': '114'
            }
        ]

        ret = [
            {
                "total": 5,
                "members": [
                    {
                        "time": 1,
                        "timeSecs": "adminSpace_json0",
                        "id": 11,
                        "category": 2,
                        "class": 1,
                        "severity": 1,
                        "type": "Event type_0",
                        "resource": 1,
                        "resourceId": "resourceId_0",
                        "resourceName": "resourceName_0",
                        "isDataChanged": "True",
                        "component": 1,
                        "componentId": "componentId_0",
                        "componentName": "componentName_0",
                        "container": 1,
                        "containerId": "containerId_0",
                        "containerName": "containerName_0",
                        "description": "description_0",
                        "links": "links_0",
                        "alertInfo": {
                            "alertId": "110",
                            "messageCode": "messageCode_0"
                        }
                    },
                    {
                        "time": 2,
                        "timeSecs": "adminSpace_json1",
                        "id": 12,
                        "category": 2,
                        "class": 2,
                        "severity": 2,
                        "type": "Event type_1",
                        "resource": 2,
                        "resourceId": "resourceId_1",
                        "resourceName": "resourceName_1",
                        "isDataChanged": "True",
                        "component": 2,
                        "componentId": "componentId_1",
                        "componentName": "componentName_1",
                        "container": 2,
                        "containerId": "containerId_1",
                        "containerName": "containerName_1",
                        "description": "description_1",
                        "links": "links_1",
                        "alertInfo": {
                            "alertId": "111",
                            "messageCode": "messageCode_1"
                        }
                    },
                    {
                        "time": 3,
                        "timeSecs": "adminSpace_json2",
                        "id": 13,
                        "category": 2,
                        "class": 3,
                        "severity": 3,
                        "type": "Event type_2",
                        "resource": 3,
                        "resourceId": "resourceId_2",
                        "resourceName": "resourceName_2",
                        "isDataChanged": "True",
                        "component": 3,
                        "componentId": "componentId_2",
                        "componentName": "componentName_2",
                        "container": 3,
                        "containerId": "containerId_2",
                        "containerName": "containerName_2",
                        "description": "description_2",
                        "links": "links_2",
                        "alertInfo": {
                            "alertId": "112",
                            "messageCode": "messageCode_2"
                        }
                    },
                    {
                        "time": 4,
                        "timeSecs": "adminSpace_json3",
                        "id": 14,
                        "category": 2,
                        "class": 4,
                        "severity": 4,
                        "type": "Event type_3",
                        "resource": 4,
                        "resourceId": "resourceId_3",
                        "resourceName": "resourceName_3",
                        "isDataChanged": "True",
                        "component": 4,
                        "componentId": "componentId_3",
                        "componentName": "componentName_3",
                        "container": 4,
                        "containerId": "containerId_3",
                        "containerName": "containerName_3",
                        "description": "description_3",
                        "links": "links_3",
                        "alertInfo": {
                            "alertId": "113",
                            "messageCode": "messageCode_3"
                        }
                    },
                    {
                        "time": 5,
                        "timeSecs": "adminSpace_json4",
                        "id": 15,
                        "category": 2,
                        "class": 5,
                        "severity": 5,
                        "type": "Event type_4",
                        "resource": 5,
                        "resourceId": "resourceId_4",
                        "resourceName": "resourceName_4",
                        "isDataChanged": "True",
                        "component": 5,
                        "componentId": "componentId_4",
                        "componentName": "componentName_4",
                        "container": 5,
                        "containerId": "containerId_4",
                        "containerName": "containerName_4",
                        "description": "description_4",
                        "links": "links_4",
                        "alertInfo": {
                            "alertId": "114",
                            "messageCode": "messageCode_4"
                        }
                    }
                ]
            }
        ]
        with mock.patch.object(RestClient, 'get_resinfo_call',
                               side_effect=ret):
            alerts = driver.list_alerts(context)
            self.assertDictEqual(alerts[0], expected[0])
            self.assertDictEqual(alerts[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_alerts',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_alerts(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_h_parse_alert(self):
        """ Success flow with all necessary parameters"""
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

        expected_alert_model = {
            'me_dn': 'abcd-1234-56789',
            'me_name': 'storage1',
            'manufacturer': 'fake vendor',
            'product_name': 'fake model',
            'category': None,
            'location': 'location1',
            'event_type': 'equipmentFault',
            'severity': 'criticalAlarm',
            'probable_cause': 'This is just for testing.Please ignore it',
            'me_category': 'storage-subsystem',
            'occur_time': '2020-6-25,1:42:26.0',
            'alarm_id': '4294967294',
            'alarm_name': 'Trap Test Alarm',
            'device_alert_sn': '4294967295',
            'clear_type': '',
            'match_key': '',
            'native_me_dn': ''
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
        self.assertIn('Exception from Storage Backend', str(exc.exception))

    def test_j_restlogout(self):
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
