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
    fake_storage_pools = [models.StoragePool(), models.StoragePool(),
                          models.StoragePool()]
    fake_storage_pools[0].id = "14155a1f-f053-4ccb-a846-ed67e4387428"
    fake_storage_pools[0].storage_id = "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6"
    fake_storage_pools[0].name = "SRP_1"
    fake_storage_pools[0].status = "normal"
    fake_storage_pools[0].created_at = "2020-06-10T07:17:08.707356"
    fake_storage_pools[0].updated_at = "2020-06-10T07:17:08.707356"
    fake_storage_pools[0].native_storage_pool_id = "SRP_1"
    fake_storage_pools[0].storage_type = "block"
    fake_storage_pools[0].total_capacity = 26300318136401
    fake_storage_pools[0].used_capacity = 19054536509358
    fake_storage_pools[0].free_capacity = 7245781627043
    fake_storage_pools[0].subscribed_capacity = 219902325555200
    fake_storage_pools[0].description = "fake storage Pool"

    fake_storage_pools[1].id = "95f7b7ed-bd7f-426e-b05f-f1ffeb4f09df"
    fake_storage_pools[1].storage_id = "84d0c5f7-2349-401c-8672-f76214d13cab"
    fake_storage_pools[1].name = "SRP_2"
    fake_storage_pools[1].status = "normal1"  # invalid input value
    fake_storage_pools[1].created_at = "2020-06-10T07:17:08.707356"
    fake_storage_pools[1].updated_at = "2020-06-10T07:17:08.707356"
    fake_storage_pools[1].native_storage_pool_id = "SRP_2"
    fake_storage_pools[1].storage_type = "block"
    fake_storage_pools[1].total_capacity = 26300318136401
    fake_storage_pools[1].used_capacity = 19054536509358
    fake_storage_pools[1].free_capacity = 7245781627043
    fake_storage_pools[1].subscribed_capacity = 219902325555200
    fake_storage_pools[1].description = "fake storage Pool"

    fake_storage_pools[2].id = "1e2ab152-44f0-11e6-819f-000c29d19d848"
    fake_storage_pools[2].storage_id = "25406d50-e645-4e62-a9ef-1f53f9cba13f"
    fake_storage_pools[2].name = "SRP_3"
    fake_storage_pools[2].status = "normal"
    fake_storage_pools[2].created_at = "2020-06-10T07:17:08.707356"
    fake_storage_pools[2].updated_at = "2020-06-10T07:17:08.707356"
    fake_storage_pools[2].native_storage_pool_id = "SRP_3"
    # unknown attribute to test the schema model
    fake_storage_pools[2].extra = "extra attrib"
    fake_storage_pools[2].storage_type = "block"
    fake_storage_pools[2].total_capacity = 26300318136401
    fake_storage_pools[2].used_capacity = 19054536509358
    fake_storage_pools[2].free_capacity = 7245781627043
    fake_storage_pools[2].subscribed_capacity = 219902325555200
    fake_storage_pools[2].description = "fake storage Pool"
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
            "created_at": "2020-06-10T07:17:08.707356",
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
            'subscribed_capacity': 219902325555200
        },
        {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "1e2ab152-44f0-11e6-819f-000c29d19d84",
            "name": "SRP_3",
            "storage_id": '25406d50-e645-4e62-a9ef-1f53f9cba13f',
            "native_storage_pool_id": "SRP_3",
            "description": "fake storage Pool",
            "status": "normal",
            "storage_type": "block",
            "total_capacity": 26300318136401,
            "used_capacity": 19054536509358,
            "free_capacity": 7245781627043,
            'subscribed_capacity': 219902325555200
        }
    ]
    return expected
