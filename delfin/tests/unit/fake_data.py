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

from delfin.db.sqlalchemy import models


def fake_storage_pool_create():
    fake_storage_pools = [models.StoragePool(), models.StoragePool()]

    fake_storage_pools[0] = {'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
                             'storage_id': '12c2d52f-01bc-41f5-b73f'
                                           '-7abf6f38a2a6',
                             'name': 'SRP_1',
                             'status': 'normal',
                             'created_at': '2020-06-10T07:17:08.707356',
                             'updated_at': '2020-06-10T07:17:08.707356',
                             'native_storage_pool_id': 'SRP_1',
                             'storage_type': 'block',
                             'total_capacity': 26300318136401,
                             'used_capacity': 19054536509358,
                             'free_capacity': 7245781627043,
                             'subscribed_capacity': 219902325555200,
                             "description": "fake storage Pool", }

    fake_storage_pools[1] = {'id': "95f7b7ed-bd7f-426e-b05f-f1ffeb4f09df",
                             'storage_id': "84d0c5f7-2349-401c-8672"
                                           "-f76214d13cab",
                             'name': "SRP_2",
                             'status': "normal",
                             'created_at': "2020-06-10T07:17:08.707356",
                             'updated_at': "2020-06-10T07:17:08.707356",
                             'native_storage_pool_id': "SRP_2",
                             'extra': "extra attrib",  # invalid key
                             'storage_type': "block",
                             'total_capacity': 26300318136401,
                             'used_capacity': 19054536509358,
                             'free_capacity': 7245781627043,
                             'subscribed_capacity': 219902325555200,
                             'description': "fake storage Pool", }

    return fake_storage_pools


def fake_expected_storage_pool_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "SRP_1",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_storage_pool_id": "SRP_1",
            "description": "fake storage Pool",
            "status": "normal",
            "storage_type": "block",
            "total_capacity": 26300318136401,
            "used_capacity": 19054536509358,
            "free_capacity": 7245781627043,
            'subscribed_capacity': 219902325555200
        },
        {
            "created_at": "2020-06-10T07:17:08.707359",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "95f7b7ed-bd7f-426e-b05f-f1ffeb4f09df",
            "name": "SRP_2",
            "storage_id": '84d0c5f7-2349-401c-8672-f76214d13cab',
            "native_storage_pool_id": "SRP_2",
            "description": "fake storage Pool",
            "status": "normal",
            "storage_type": "block",
            "total_capacity": 26300318136401,
            "used_capacity": 19054536509358,
            "free_capacity": 7245781627043,
            'subscribed_capacity': 219902325555200,
        }
    ]
    return expected


def fake_storage_host_initiator_create():
    fake_storage_host_initiators = [models.StorageHostInitiator()]

    fake_storage_host_initiators[0] = {
        'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
        'storage_id': '12c2d52f-01bc-41f5-b73f'
                      '-7abf6f38a2a6',
        'name': 'storage_host_initiator_1',
        'description': 'storage_host_initiator_1',
        'alias': 'storage_host_initiator_1',
        'status': 'normal',
        'created_at': '2020-06-10T07:17:08.707356',
        'updated_at': '2020-06-10T07:17:08.707356',
        'native_storage_host_initiator_id': 'storage_host_initiator_1',
        'native_storage_host_id': 'storage_host_1',
        'wwn': 'wwn1', 'type': 'fcinitiator'}
    return fake_storage_host_initiators


def fake_expected_storage_host_initiator_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "storage_host_initiator_1",
            "description": "storage_host_initiator_1",
            "alias": "storage_host_initiator_1",
            "status": "normal",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_storage_host_initiator_id": "storage_host_initiator_1",
            "native_storage_host_id": "storage_host_1",
            "wwn": "wwn1",
            "type": "fcinitiator"

        },
    ]
    return expected


def fake_storage_host_create():
    fake_storage_hosts = [models.StorageHost()]

    fake_storage_hosts[0] = {
        'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
        'storage_id': '12c2d52f-01bc-41f5-b73f'
                      '-7abf6f38a2a6',
        'name': 'storage_host_1',
        'description': 'storage_host_1',
        'ip_address': '1.2.3.4',
        'status': 'normal',
        'os_type': 'linux',
        'created_at': '2020-06-10T07:17:08.707356',
        'updated_at': '2020-06-10T07:17:08.707356',
        'native_storage_host_id': 'storage_host_1', }
    return fake_storage_hosts


def fake_expected_storage_host_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "storage_host_1",
            "description": "storage_host_1",
            "ip_address": "1.2.3.4",
            "os_type": "linux",
            "status": "normal",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_storage_host_id": "storage_host_1",
        },
    ]
    return expected


def fake_storage_host_group_create():
    fake_storage_host_groups = [models.StorageHostGroup()]

    fake_storage_host_groups[0] = {
        'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
        'storage_id': '12c2d52f-01bc-41f5-b73f'
                      '-7abf6f38a2a6',
        'name': 'storage_host_group_1',
        'description': 'storage_host_group_1',
        'created_at': '2020-06-10T07:17:08.707356',
        'updated_at': '2020-06-10T07:17:08.707356',
        'native_storage_host_group_id': 'storage_host_group_1', }
    return fake_storage_host_groups


def fake_expected_storage_host_group_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "storage_host_group_1",
            "description": "storage_host_group_1",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_storage_host_group_id": "storage_host_group_1",
        },
    ]
    return expected


def fake_port_group_create():
    fake_port_groups = [models.PortGroup()]

    fake_port_groups[0] = {
        'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
        'storage_id': '12c2d52f-01bc-41f5-b73f'
                      '-7abf6f38a2a6',
        'name': 'port_group_1',
        'description': 'port_group_1',
        'created_at': '2020-06-10T07:17:08.707356',
        'updated_at': '2020-06-10T07:17:08.707356',
        'native_port_group_id': 'port_group_1', }
    return fake_port_groups


def fake_expected_port_group_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "port_group_1",
            "description": "port_group_1",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_port_group_id": "port_group_1",
        },
    ]
    return expected


def fake_volume_group_create():
    fake_volume_groups = [models.VolumeGroup()]

    fake_volume_groups[0] = {
        'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
        'storage_id': '12c2d52f-01bc-41f5-b73f'
                      '-7abf6f38a2a6',
        'name': 'volume_group_1',
        'description': 'volume_group_1',
        'created_at': '2020-06-10T07:17:08.707356',
        'updated_at': '2020-06-10T07:17:08.707356',
        'native_volume_group_id': 'volume_group_1', }
    return fake_volume_groups


def fake_expected_volume_groups_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "volume_group_1",
            "description": "volume_group_1",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_volume_group_id": "volume_group_1",
        },
    ]
    return expected


def fake_masking_view_create():
    fake_masking_views = [models.MaskingView()]

    fake_masking_views[0] = {
        'id': '14155a1f-f053-4ccb-a846-ed67e4387428',
        'storage_id': '12c2d52f-01bc-41f5-b73f'
                      '-7abf6f38a2a6',
        'name': 'masking_view_1',
        'description': 'masking_view_1',
        'created_at': '2020-06-10T07:17:08.707356',
        'updated_at': '2020-06-10T07:17:08.707356',
        'native_storage_host_id': 'storage_host_1',
        'native_volume_id': 'volume_1',
        'native_masking_view_id': 'masking_view_1', }
    return fake_masking_views


def fake_expected_masking_views_create():
    expected = [
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "masking_view_1",
            "description": "masking_view_1",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "native_storage_host_id": "storage_host_1",
            "native_volume_id": "volume_1",
            "native_storage_host_group_id": None,
            "native_port_group_id": None,
            "native_volume_group_id": None,
            "native_masking_view_id": "masking_view_1",
        },
    ]
    return expected
