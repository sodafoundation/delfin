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
from delfin import db
from delfin import test
from delfin.tests.unit.api import fakes
from delfin.api.v1.filesystems import FilesystemController


class TestFileSystemController(test.TestCase):
    def setUp(self):
        super(TestFileSystemController, self).setUp()
        self.controller = FilesystemController()

    def test_index(self):
        self.mock_object(
            db, 'filesystem_get_all',
            fakes.fake_filesystems_get_all)
        req = fakes.HTTPRequest.blank('/filesystems')
        res_dict = self.controller.index(req)
        expctd_dict = {
            "filesystems": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "native_filesystem_id": "5f5c806d-2e65-473c",
                    "type": "type_d",
                    "status": "connected",
                    "storage_id": "5f5c806d-2e65-473c-b612",
                    "native_pool_id": "parent_d",
                    "security_mode": "SM",
                    "total_capacity": "200000",
                    "used_capacity": 100000,
                    "free_capacity": 100000,
                    "compressed": True,
                    "deduplicated": False,
                    "worm": "W",
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "native_filesystem_id": "5f5c806d-2e65-473c",
                    "type": "type_dD",
                    "status": "connected",
                    "storage_id": "5f5c806d-2e65-473c-b612",
                    "native_pool_id": "parent_d",
                    "security_mode": "SM",
                    "total_capacity": "200000",
                    "used_capacity": 100000,
                    "free_capacity": 100000,
                    "compressed": True,
                    "deduplicated": False,
                    "worm": "W",
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)
