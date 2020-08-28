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
        "password": "pass",
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
