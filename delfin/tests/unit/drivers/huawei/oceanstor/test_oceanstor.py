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
from delfin import exception
from delfin import context
from delfin.common import config # noqa
from delfin.drivers.huawei.oceanstor.oceanstor import OceanStorDriver, consts
from delfin.drivers.huawei.oceanstor.rest_client import RestClient
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
        "password": "cGFzc3dvcmQ=",
    },
    "extra_attributes": {
        "array_id": "00112233"
    }
}


def create_driver():
    kwargs = ACCESS_INFO

    m = mock.MagicMock()
    with mock.patch.object(Session, 'post', return_value=m):
        m.raise_for_status.return_value = None
        m.json.return_value = {
            'data': {
                'deviceid': '123ABC456',
                'iBaseToken': 'FFFF0000',
                'accountstate': 1
            },
            'error': {
                'code': 0,
                'description': '0'
            }
        }
        return OceanStorDriver(**kwargs)


class TestOceanStorStorageDriver(TestCase):

    def test_init(self):
        driver = create_driver()
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.sector_size, consts.SECTORS_SIZE)
        self.assertEqual(driver.client.device_id, '123ABC456')

        m = mock.MagicMock()
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = None
            m.json.return_value = {
                'data': {
                    'deviceid': '123ABC456',
                    'iBaseToken': 'FFFF0000',
                    'accountstate': 1
                },
                'error': {
                    'code': 123,
                    'description': '0'
                }
            }
            kwargs = ACCESS_INFO
            with self.assertRaises(Exception) as exc:
                OceanStorDriver(**kwargs)
            self.assertIn('The credentials are invalid', str(exc.exception))

    def test_get_storage(self):
        driver = create_driver()
        expected = {
            'name': 'OceanStor',
            'vendor': 'Huawei',
            'description': 'Huawei OceanStor Storage',
            'model': 'OceanStor_1',
            'status': 'normal',
            'serial_number': '012345',
            'firmware_version': '1000',
            'location': 'Location1',
            'total_capacity': 51200,
            'used_capacity': 38400,
            'free_capacity': 20480,
            'raw_capacity': 76800
        }

        ret = [
            # Storage 1
            {
                'data': {
                    'RUNNINGSTATUS': '1',
                    'SECTORSIZE': '512',
                    'TOTALCAPACITY': '100',
                    'USEDCAPACITY': '75',
                    'MEMBERDISKSCAPACITY': '150',
                    'userFreeCapacity': '40',
                    'NAME': 'OceanStor_1',
                    'ID': '012345',
                    'LOCATION': 'Location1'
                },
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'SOFTVER': '1000',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            storage = driver.get_storage(context)
            self.assertDictEqual(storage, expected)

    def test_list_storage_pools(self):
        driver = create_driver()
        expected = [
            {
                'name': 'OceanStor_1',
                'storage_id': '12345',
                'native_storage_pool_id': '012345',
                'description': 'Huawei OceanStor Pool',
                'status': 'normal',
                'storage_type': 'block',
                'total_capacity': 51200,
                'used_capacity': 38400,
                'free_capacity': 20480
            },
            {
                'name': 'OceanStor_1',
                'storage_id': '12345',
                'native_storage_pool_id': '012345',
                'description': 'Huawei OceanStor Pool',
                'status': 'offline',
                'storage_type': 'file',
                'total_capacity': 51200,
                'used_capacity': 38400,
                'free_capacity': 20480
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'RUNNINGSTATUS': '27',
                        'USAGETYPE': '1',
                        'USERTOTALCAPACITY': '100',
                        'USERCONSUMEDCAPACITY': '75',
                        'USERFREECAPACITY': '40',
                        'NAME': 'OceanStor_1',
                        'ID': '012345',
                        'LOCATION': 'Location1'
                    },
                    {
                        'RUNNINGSTATUS': '28',
                        'USAGETYPE': '2',
                        'USERTOTALCAPACITY': '100',
                        'USERCONSUMEDCAPACITY': '75',
                        'USERFREECAPACITY': '40',
                        'NAME': 'OceanStor_1',
                        'ID': '012345',
                        'LOCATION': 'Location1'
                    }
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'SOFTVER': '1000',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            pools = driver.list_storage_pools(context)
            self.assertDictEqual(pools[0], expected[0])
            self.assertDictEqual(pools[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_pools',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_list_volumes(self):
        driver = create_driver()
        expected = [
            {
                'name': 'Volume_1',
                'storage_id': '12345',
                'description': 'Huawei OceanStor volume',
                'status': 'available',
                'native_volume_id': '0001',
                'native_storage_pool_id': '012345',
                'wwn': 'wwn12345',
                'type': 'thin',
                'total_capacity': 51200,
                'used_capacity': 38400,
                'free_capacity': None,
                'compressed': False,
                'deduplicated': False
            },
            {
                'name': 'Volume_1',
                'storage_id': '12345',
                'description': 'Huawei OceanStor volume',
                'status': 'error',
                'native_volume_id': '0001',
                'native_storage_pool_id': '012345',
                'wwn': 'wwn12345',
                'type': 'thick',
                'total_capacity': 51200,
                'used_capacity': 38400,
                'free_capacity': None,
                'compressed': True,
                'deduplicated': True
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'RUNNINGSTATUS': '27',
                        'USAGETYPE': '1',
                        'CAPACITY': '100',
                        'ALLOCCAPACITY': '75',
                        'WWN': 'wwn12345',
                        'NAME': 'Volume_1',
                        'ID': '0001',
                        'LOCATION': 'Location1',
                        'PARENTNAME': 'OceanStor_1',
                        'ENABLECOMPRESSION': 'false',
                        'ENABLEDEDUP': 'false',
                        'ALLOCTYPE': '1',
                        'SECTORSIZE': '512',

                    },
                    {
                        'RUNNINGSTATUS': '28',
                        'USAGETYPE': '1',
                        'CAPACITY': '100',
                        'ALLOCCAPACITY': '75',
                        'WWN': 'wwn12345',
                        'NAME': 'Volume_1',
                        'ID': '0001',
                        'LOCATION': 'Location1',
                        'PARENTNAME': 'OceanStor_1',
                        'ENABLECOMPRESSION': 'true',
                        'ENABLEDEDUP': 'true',
                        'ALLOCTYPE': '0',
                        'SECTORSIZE': '512',

                    }
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'NAME': 'OceanStor_1',
                    'ID': '012345'
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'SOFTVER': '1000',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            volumes = driver.list_volumes(context)
            self.assertDictEqual(volumes[0], expected[0])
            self.assertDictEqual(volumes[1], expected[1])

        with mock.patch.object(RestClient, 'get_all_volumes',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)
            self.assertIn('Exception from Storage Backend',
                          str(exc.exception))

    def test_list_ports(self):
        driver = create_driver()
        expected = [
            {
                'name': 'TEST_FC_PORT',
                'storage_id': '12345',
                'connection_status': 'disconnected',
                'health_status': 'unknown',
                'location': 'Location1',
                'logical_type': 'service',
                'max_speed': '16000',
                'native_port_id': '012345',
                'native_parent_id': '0B.0',
                'wwn': 'WWN_123000',
                'type': 'fc',
                'speed': None,
                'mac_address': None,
                'ipv4': None,
                'ipv4_mask': None,
                'ipv6': None,
                'ipv6_mask': None,
            },
            {
                'name': 'TEST_FCOE_PORT',
                'storage_id': '12345',
                'connection_status': 'disconnected',
                'health_status': 'unknown',
                'location': 'Location2',
                'logical_type': 'service',
                'max_speed': '12000',
                'native_port_id': '22222',
                'native_parent_id': '0B.2',
                'wwn': '2210',
                'type': 'fcoe',
                'speed': None,
                'mac_address': None,
                'ipv4': None,
                'ipv4_mask': None,
                'ipv6': None,
                'ipv6_mask': None,
            },
            {
                'name': 'TEST_ETH_PORT',
                'storage_id': '12345',
                'connection_status': 'disconnected',
                'health_status': 'unknown',
                'location': 'Location3',
                'logical_type': 'service',
                'max_speed': '1000',
                'native_port_id': '11111',
                'native_parent_id': '0B.0',
                'wwn': None,
                'type': 'eth',
                'speed': '-1',
                'mac_address': 'MAC_1:ff:00',
                'ipv4': None,
                'ipv4_mask': None,
                'ipv6': None,
                'ipv6_mask': None,
            },
            {
                'name': 'TEST_PCIE_PORT',
                'storage_id': '12345',
                'connection_status': 'disconnected',
                'health_status': 'unknown',
                'location': 'Location4',
                'logical_type': 'other',
                'max_speed': '8000',
                'native_port_id': '33333',
                'native_parent_id': '1090',
                'wwn': None,
                'type': 'other',
                'speed': '5000',
                'mac_address': None,
                'ipv4': None,
                'ipv4_mask': None,
                'ipv6': None,
                'ipv6_mask': None,
            },
            {
                'name': 'TEST_BOND_PORT',
                'storage_id': '12345',
                'connection_status': 'connected',
                'health_status': 'unknown',
                'location': 'Location5',
                'logical_type': 'other',
                'max_speed': None,
                'native_port_id': '44444',
                'native_parent_id': None,
                'wwn': None,
                'type': 'other',
                'speed': None,
                'mac_address': None,
                'ipv4': None,
                'ipv4_mask': None,
                'ipv6': None,
                'ipv6_mask': None,
            },
            {
                'name': 'TEST_SAS_PORT',
                'storage_id': '12345',
                'connection_status': 'unknown',
                'health_status': 'unknown',
                'location': 'Location6',
                'logical_type': 'other',
                'max_speed': '12000',
                'native_port_id': '55555',
                'native_parent_id': '0A',
                'wwn': None,
                'type': 'sas',
                'speed': '12000',
                'mac_address': None,
                'ipv4': None,
                'ipv4_mask': None,
                'ipv6': None,
                'ipv6_mask': None,
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'TYPE': '212',
                        'NAME': 'TEST_FC_PORT',
                        'RUNNINGSTATUS': '11',
                        'HEALTHSTATUS': '1',
                        'ID': '012345',
                        'LOCATION': 'Location1',
                        'MAXSPEED': '16000',
                        'MAXSUPPORTSPEED': '16000',
                        'LOGICTYPE': '0',
                        'RUNSPEED': '-1',
                        'PARENTID': '0B.0',
                        'WWN': 'WWN_123000',
                    },
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'TYPE': '252',
                    'NAME': 'TEST_FCOE_PORT',
                    'RUNNINGSTATUS': '11',
                    'HEALTHSTATUS': '1',
                    'ID': '22222',
                    'LOCATION': 'Location2',
                    'MAXSPEED': '12000',
                    'LOGICTYPE': '0',
                    'RUNSPEED': '-1',
                    'PARENTID': '0B.2',
                    'WWN': '2210',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'TYPE': '213',
                    'NAME': 'TEST_ETH_PORT',
                    'RUNNINGSTATUS': '11',
                    'HEALTHSTATUS': '1',
                    'ID': '11111',
                    'LOCATION': 'Location3',
                    'SPEED': '-1',
                    'maxSpeed': '1000',
                    'LOGICTYPE': '0',
                    'RUNSPEED': '-1',
                    'PARENTID': '0B.0',
                    'MACADDRESS': 'MAC_1:ff:00',
                    'IP4ADDR': '',
                    'IP4MASK': '',
                    'IP6ADDR': '',
                    'IP6MASK': '',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'TYPE': '233',
                    'NAME': 'TEST_PCIE_PORT',
                    'RUNNINGSTATUS': '11',
                    'HEALTHSTATUS': '1',
                    'ID': '33333',
                    'LOCATION': 'Location4',
                    'PCIESPEED': '5000',
                    'MAXSPEED': '8000',
                    'PARENTID': '1090',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'TYPE': '235',
                    'NAME': 'TEST_BOND_PORT',
                    'RUNNINGSTATUS': '10',
                    'HEALTHSTATUS': '1',
                    'ID': '44444',
                    'LOCATION': 'Location5',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'TYPE': '214',
                    'NAME': 'TEST_SAS_PORT',
                    'RUNNINGSTATUS': '0',
                    'HEALTHSTATUS': '0',
                    'ID': '55555',
                    'LOCATION': 'Location6',
                    'RUNSPEED': '12000',
                    'MAXSPEED': '12000',
                    'PARENTID': '0A',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'TYPE': '210',
                    'ID': '012345',
                    'NAME': 'Name100',
                    'RUNNINGSTATUS': '27',
                    'HEALTHSTATUS': '0',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            ports = driver.list_ports(context)

            self.assertDictEqual(ports[0], expected[0])
            self.assertDictEqual(ports[1], expected[1])
            self.assertDictEqual(ports[2], expected[2])
            self.assertDictEqual(ports[3], expected[3])
            self.assertDictEqual(ports[4], expected[4])
            self.assertDictEqual(ports[5], expected[5])

        with mock.patch.object(RestClient, 'get_all_ports',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_ports(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

        with mock.patch.object(RestClient, 'get_all_ports',
                               side_effect=TypeError):
            with self.assertRaises(Exception) as exc:
                driver.list_ports(context)
            self.assertIn('The results are invalid',
                          str(exc.exception))

    def test_list_controllers(self):
        driver = create_driver()
        expected = [
            {
                'name': 'Controller-1',
                'storage_id': '12345',
                'native_controller_id': '0A',
                'status': 'normal',
                'location': 'Location1',
                'soft_version': 'Ver123',
                'cpu_info': 'Intel Xenon',
                'memory_size': '100000',
            },
            {
                'name': 'Controller-2',
                'storage_id': '12345',
                'native_controller_id': '0B',
                'status': 'offline',
                'location': 'Location2',
                'soft_version': 'VerABC',
                'cpu_info': 'ARM64',
                'memory_size': '500000',
            },
            {
                'name': 'Controller-3',
                'storage_id': '12345',
                'native_controller_id': '0B',
                'status': 'unknown',
                'location': 'Location3',
                'soft_version': 'VerABC',
                'cpu_info': 'ARM64',
                'memory_size': '500000',
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'RUNNINGSTATUS': '27',
                        'NAME': 'Controller-1',
                        'SOFTVER': 'Ver123',
                        'CPUINFO': 'Intel Xenon',
                        'MEMORYSIZE': '100000',
                        'ID': '0A',
                        'LOCATION': 'Location1'
                    },
                    {
                        'RUNNINGSTATUS': '28',
                        'NAME': 'Controller-2',
                        'SOFTVER': 'VerABC',
                        'CPUINFO': 'ARM64',
                        'MEMORYSIZE': '500000',
                        'ID': '0B',
                        'LOCATION': 'Location2'
                    },
                    {
                        'RUNNINGSTATUS': '0',
                        'NAME': 'Controller-3',
                        'SOFTVER': 'VerABC',
                        'CPUINFO': 'ARM64',
                        'MEMORYSIZE': '500000',
                        'ID': '0B',
                        'LOCATION': 'Location3'
                    },
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'SOFTVER': '1000',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            controller = driver.list_controllers(context)
            self.assertDictEqual(controller[0], expected[0])
            self.assertDictEqual(controller[1], expected[1])
            self.assertDictEqual(controller[2], expected[2])

        with mock.patch.object(RestClient, 'get_all_controllers',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_controllers(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

        with mock.patch.object(RestClient, 'get_all_controllers',
                               side_effect=TypeError):
            with self.assertRaises(Exception) as exc:
                driver.list_controllers(context)
            self.assertIn('The results are invalid',
                          str(exc.exception))

    def test_list_disks(self):
        driver = create_driver()
        expected = [
            {
                'name': 'ST200:1234',
                'storage_id': '12345',
                'native_disk_id': '0A',
                'serial_number': '1234',
                'manufacturer': 'Segate',
                'model': 'ST200',
                'firmware': '0003',
                'speed': 7200,
                'capacity': 1000000,
                'status': 'normal',
                'physical_type': 'unknown',
                'logical_type': 'free',
                'health_score': '255',
                'native_disk_group_id': None,
                'location': 'Location1',
            },
            {
                'name': 'WD00:1111',
                'storage_id': '12345',
                'native_disk_id': '0B',
                'serial_number': '1111',
                'manufacturer': 'WesterDigital',
                'model': 'WD00',
                'firmware': '123',
                'speed': 10000,
                'capacity': 5000000,
                'status': 'offline',
                'physical_type': 'ssd',
                'logical_type': 'free',
                'health_score': '255',
                'native_disk_group_id': None,
                'location': 'Location2',
            },
            {
                'name': 'ST200:1234',
                'storage_id': '12345',
                'native_disk_id': '0A',
                'serial_number': '1234',
                'manufacturer': 'Segate',
                'model': 'ST200',
                'firmware': '0003',
                'speed': 7200,
                'capacity': 1000000,
                'status': 'abnormal',
                'physical_type': 'unknown',
                'logical_type': 'free',
                'health_score': '255',
                'native_disk_group_id': None,
                'location': 'Location1',
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'RUNNINGSTATUS': '27',
                        'DISKTYPE': '4',
                        'LOGICTYPE': '1',
                        'HEALTHMARK': '255',
                        'MODEL': 'ST200',
                        'SERIALNUMBER': '1234',
                        'MANUFACTURER': 'Segate',
                        'FIRMWAREVER': '0003',
                        'SPEEDRPM': '7200',
                        'SECTORS': '10000',
                        'SECTORSIZE': '100',
                        'ID': '0A',
                        'LOCATION': 'Location1'
                    },
                    {
                        'RUNNINGSTATUS': '28',
                        'DISKTYPE': '3',
                        'LOGICTYPE': '1',
                        'HEALTHMARK': '255',
                        'MODEL': 'WD00',
                        'SERIALNUMBER': '1111',
                        'MANUFACTURER': 'WesterDigital',
                        'FIRMWAREVER': '123',
                        'SPEEDRPM': '10000',
                        'SECTORS': '50000',
                        'SECTORSIZE': '100',
                        'ID': '0B',
                        'LOCATION': 'Location2'
                    },
                    {
                        'RUNNINGSTATUS': '0',
                        'DISKTYPE': '4',
                        'LOGICTYPE': '1',
                        'HEALTHMARK': '255',
                        'MODEL': 'ST200',
                        'SERIALNUMBER': '1234',
                        'MANUFACTURER': 'Segate',
                        'FIRMWAREVER': '0003',
                        'SPEEDRPM': '7200',
                        'SECTORS': '10000',
                        'SECTORSIZE': '100',
                        'ID': '0A',
                        'LOCATION': 'Location1'
                    }
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'SOFTVER': '1000',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            disk = driver.list_disks(context)
            self.assertDictEqual(disk[0], expected[0])
            self.assertDictEqual(disk[1], expected[1])
            self.assertDictEqual(disk[2], expected[2])

        with mock.patch.object(RestClient, 'get_all_disks',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_disks(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

        with mock.patch.object(RestClient, 'get_all_disks',
                               side_effect=TypeError):
            with self.assertRaises(Exception) as exc:
                driver.list_disks(context)
            self.assertIn('The results are invalid',
                          str(exc.exception))

    def test_list_filesystems(self):
        driver = create_driver()
        expected = [
            {
                'name': 'fs1',
                'storage_id': '12345',
                'native_filesystem_id': '123',
                'native_pool_id': '123',
                'compressed': True,
                'deduplicated': True,
                'worm': 'non_worm',
                'status': 'normal',
                'type': 'thin',
                'total_capacity': 81920,
                'used_capacity': 8192,
                'free_capacity': 8192,
            },
            {
                'name': 'fs2',
                'storage_id': '12345',
                'native_filesystem_id': '123',
                'native_pool_id': '123',
                'compressed': False,
                'deduplicated': False,
                'worm': 'compliance',
                'status': 'normal',
                'type': 'thin',
                'total_capacity': 81920,
                'used_capacity': 81920,
                'free_capacity': 8192,
            },
            {
                'name': 'fs3',
                'storage_id': '12345',
                'native_filesystem_id': '123',
                'native_pool_id': '123',
                'compressed': True,
                'deduplicated': True,
                'worm': 'audit_log',
                'status': 'normal',
                'type': 'thin',
                'total_capacity': 81920,
                'used_capacity': 8192,
                'free_capacity': 8192,
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'HEALTHSTATUS': '1',
                        'ALLOCTYPE': '1',
                        'SECTORSIZE': '8192',
                        'CAPACITY': '10',
                        'ALLOCCAPACITY': '1',
                        'AVAILABLECAPCITY': '1',
                        'ENABLECOMPRESSION': 'true',
                        'ENABLEDEDUP': 'true',
                        'NAME': 'fs1',
                        'ID': '123',
                        'PARENTTYPE': 216,
                        'PARENTID': '123',
                        'WORMTYPE': '0'
                    },
                    {
                        'HEALTHSTATUS': '1',
                        'ALLOCTYPE': '1',
                        'SECTORSIZE': '8192',
                        'CAPACITY': '10',
                        'ALLOCCAPACITY': '10',
                        'AVAILABLECAPCITY': '1',
                        'ENABLECOMPRESSION': 'false',
                        'ENABLEDEDUP': 'false',
                        'NAME': 'fs2',
                        'ID': '123',
                        'PARENTTYPE': 216,
                        'PARENTID': '123',
                        'WORMTYPE': '1'
                    },
                    {
                        'HEALTHSTATUS': '1',
                        'ALLOCTYPE': '1',
                        'SECTORSIZE': '8192',
                        'CAPACITY': '10',
                        'ALLOCCAPACITY': '1',
                        'AVAILABLECAPCITY': '1',
                        'ENABLECOMPRESSION': 'true',
                        'ENABLEDEDUP': 'true',
                        'NAME': 'fs3',
                        'ID': '123',
                        'PARENTTYPE': 216,
                        'PARENTID': '123',
                        'WORMTYPE': '2'
                    }
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'SOFTVER': '1000',
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            fs = driver.list_filesystems(context)
            self.assertDictEqual(fs[0], expected[0])
            self.assertDictEqual(fs[1], expected[1])
            self.assertDictEqual(fs[2], expected[2])

        with mock.patch.object(RestClient, 'get_all_filesystems',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_filesystems(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

        with mock.patch.object(RestClient, 'get_all_filesystems',
                               side_effect=TypeError):
            with self.assertRaises(Exception) as exc:
                driver.list_filesystems(context)
            self.assertIn('The results are invalid',
                          str(exc.exception))

    def test_list_qtrees(self):
        driver = create_driver()
        expected = [
            {
                'name': 'qtree1',
                'storage_id': '12345',
                'native_qtree_id': '123',
                'native_filesystem_id': '123',
                'security_mode': 'mixed',
            },
            {
                'name': 'WD00:1111',
                'storage_id': '12345',
                'native_disk_id': '0B',
                'serial_number': '1111',
                'manufacturer': 'WesterDigital',
                'model': 'WD00',
                'firmware': '123',
                'speed': 10000,
                'capacity': 5000000,
                'status': 'offline',
                'physical_type': 'ssd',
                'logical_type': 'free',
                'health_score': '255',
                'native_disk_group_id': None,
                'location': 'Location2',
            },
            {
                'name': 'ST200:1234',
                'storage_id': '12345',
                'native_disk_id': '0A',
                'serial_number': '1234',
                'manufacturer': 'Segate',
                'model': 'ST200',
                'firmware': '0003',
                'speed': 7200,
                'capacity': 1000000,
                'status': 'abnormal',
                'physical_type': 'unknown',
                'logical_type': 'free',
                'health_score': '255',
                'native_disk_group_id': None,
                'location': 'Location1',
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'NAME': 'qtree1',
                        'ID': '123',
                        'securityStyle': '0',
                        'PARENTTYPE': 40,
                        'PARENTID': '123',
                    },
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'get_all_filesystems',
                               side_effect=[[{"ID": "1"}]]):
            with mock.patch.object(RestClient, 'do_call', side_effect=ret):
                qtree = driver.list_qtrees(context)
            self.assertDictEqual(qtree[0], expected[0])

        with mock.patch.object(RestClient, 'get_all_filesystems',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_qtrees(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

        with mock.patch.object(RestClient, 'get_all_filesystems',
                               side_effect=TypeError):
            with self.assertRaises(Exception) as exc:
                driver.list_qtrees(context)
            self.assertIn('The results are invalid',
                          str(exc.exception))

    def test_list_shares(self):
        driver = create_driver()
        expected = [
            {
                'name': 'CIFS',
                'storage_id': '12345',
                'native_share_id': '111',
                'native_filesystem_id': 'FS111',
                'path': '/filesystem0001/',
                'protocol': 'cifs'
            },
            {
                'name': 'NFS',
                'storage_id': '12345',
                'native_share_id': '222',
                'native_filesystem_id': 'FS222',
                'path': '/filesystem0002/',
                'protocol': 'nfs'
            },
            {
                'name': 'FTP',
                'storage_id': '12345',
                'native_share_id': '333',
                'native_filesystem_id': 'FS333',
                'path': '/filesystem0003/',
                'protocol': 'ftp'
            }

        ]

        ret = [
            {
                'data': [
                    {
                        'subType': '0',
                        'NAME': 'CIFS',
                        'SHAREPATH': '/filesystem0001/',
                        'ID': '111',
                        'FSID': 'FS111'
                    },
                ],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'type': '16401',
                    'NAME': 'NFS',
                    'SHAREPATH': '/filesystem0002/',
                    'ID': '222',
                    'FSID': 'FS222'
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            },
            {
                'data': [{
                    'ACCESSNAME': 'test',
                    'NAME': 'FTP',
                    'SHAREPATH': '/filesystem0003/',
                    'ID': '333',
                    'FSID': 'FS333'
                }],
                'error': {
                    'code': 0,
                    'description': '0'
                }
            }
        ]
        with mock.patch.object(RestClient, 'do_call', side_effect=ret):
            share = driver.list_shares(context)
            self.assertDictEqual(share[0], expected[0])
            self.assertDictEqual(share[1], expected[1])
            self.assertDictEqual(share[2], expected[2])

        with mock.patch.object(RestClient, 'get_all_shares',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_shares(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

        with mock.patch.object(RestClient, 'get_all_shares',
                               side_effect=TypeError):
            with self.assertRaises(Exception) as exc:
                driver.list_shares(context)
            self.assertIn('The results are invalid',
                          str(exc.exception))
