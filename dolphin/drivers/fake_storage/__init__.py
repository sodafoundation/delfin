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

from dolphin.drivers import driver


class FakeStorageDriver(driver.StorageDriver):
    """FakeStorageDriver shows how to implement the StorageDriver,
    it also plays a role as faker to fake data for being tested by clients.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_storage(self, context):
        # Do something here
        return {

            "id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "name": "",
            "vendor": "Dell EMC",
            "description": "",
            "model": "VMAX250F",
            "status": "normal",
            "serial_number": "0001234567891",
            "firmware_version": '5979.352',
            "location": "",
            "total_capacity": 26300318136401,
            "used_capacity": 19054536509358,
            "free_capacity": 7245781627043

        }

    def list_storage_pools(self, context):
        return [{

            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "SRP_1",
            "storage_id": '5f5c806d-2e65-473c-b612-345ef43f0642',
            "original_id": "SRP_1",
            "description": "Dell EMC VMAX Pool",
            "status": "normal",
            "storage_type": "block",
            "total_capacity": 26300318136401,
            "used_capacity": 19054536509358,
            "free_capacity": 7245781627043
        }]

    def list_volumes(self, context):
        return [{
            
            
            "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
            "name": "004DF",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004DF",
            "wwn": "60000970000297801855533030344446",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "dad84a1f-db8d-49ab-af40-048fc3544c12",
            "name": "004E0",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E0",
            "wwn": "60000970000297801855533030344530",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "2c8afe15-92b7-4717-b667-a4f4f2d0bf99",
            "name": "004E1",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E1",
            "wwn": "60000970000297801855533030344531",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "3a66da0c-2c21-4dba-b5d1-0a6307178426",
            "name": "004E2",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E2",
            "wwn": "60000970000297801855533030344532",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "a04e6123-2576-4277-828e-e509057a766f",
            "name": "004E3",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E3",
            "wwn": "60000970000297801855533030344533",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 1075838976,
            "free_capacity": 0,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "ec869d3e-1a60-44a9-9292-6e315fb7ea28",
            "name": "004E4",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E4",
            "wwn": "60000970000297801855533030344534",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "c2327232-38ec-48e2-8a32-3621b0a976d9",
            "name": "004E5",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E5",
            "wwn": "60000970000297801855533030344535",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 1075838976,
            "free_capacity": 0,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "faf6e5f6-2d87-4d07-9756-389ef0a15a71",
            "name": "004E6",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E6",
            "wwn": "60000970000297801855533030344536",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "1bbb37ce-bc58-4ee2-81e8-bcccfe9017bf",
            "name": "004E7",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E7",
            "wwn": "60000970000297801855533030344537",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "22912687-1f31-4e81-8d8a-762842dd05ff",
            "name": "004E8",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E8",
            "wwn": "60000970000297801855533030344538",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "9b3cc41a-5883-40fe-8037-64c853c26d29",
            "name": "004E9",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004E9",
            "wwn": "60000970000297801855533030344539",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "8cf95a54-824f-425e-9a38-be0ff6ffd310",
            "name": "004EA",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004EA",
            "wwn": "60000970000297801855533030344541",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "8aeeeb2e-bb4d-49ca-9a22-9601c921bdd9",
            "name": "004EB",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004EB",
            "wwn": "60000970000297801855533030344542",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "213f05c6-045c-4a20-ac39-7556e67ab1cd",
            "name": "004EC",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004EC",
            "wwn": "60000970000297801855533030344543",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "8c2a1db6-e630-48b5-8ee1-0e3b2608c0ba",
            "name": "004ED",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004ED",
            "wwn": "60000970000297801855533030344544",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "1508cf32-ed09-46b8-812f-a7d4ed650ec6",
            "name": "004EE",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004EE",
            "wwn": "60000970000297801855533030344545",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "8c9de067-7a3e-41bf-ba4e-ffa0d44257e0",
            "name": "004EF",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004EF",
            "wwn": "60000970000297801855533030344546",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "b557a996-02ea-400e-ad5a-5641f1bb4be9",
            "name": "004F0",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004F0",
            "wwn": "60000970000297801855533030344630",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "ecc61fa9-dce8-4109-bad6-cdb271769791",
            "name": "004F1",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004F1",
            "wwn": "60000970000297801855533030344631",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            
            
            "id": "7a932d24-0e2f-4118-abf4-35539036fb38",
            "name": "004F2",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "Dell EMC VMAX 'thin device' volume",
            "status": "available",
            "original_id": "004F2",
            "wwn": "60000970000297801855533030344632",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        }]

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        pass

    def clear_alert(self, context, alert):
        pass
