# Copyright 2021 The SODA Authors.
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
from delfin.api.v1.disks import DiskController
from delfin.tests.unit.api import fakes


class TestDiskController(test.TestCase):

    def setUp(self):
        super(TestDiskController, self).setUp()
        self.controller = DiskController()

    def test_list(self):
        self.mock_object(
            db, 'disk_get_all',
            fakes.fake_disk_get_all)
        req = fakes.HTTPRequest.blank('/v1/disks')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "disks": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "Nam",
                    "native_disk_id": "5f5c806d-2e65-473c-b612",
                    "physical_type": "P",
                    "logical_type": "L",
                    "status": "Connected",
                    "location": "Lo",
                    "storage_id": "3b-3f-4f-5f-5f",
                    "native_disk_group_id": "NDG",
                    "serial_number": "234-fgh",
                    "manufacturer": "Man",
                    "model": "GA4",
                    "firmware": "Firm",
                    "speed": 5000,
                    "capacity": 2000000,
                    "health_score": 89,
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "Nam",
                    "native_disk_id": "5f5c806d-2e65-473c-b612",
                    "physical_type": "P2",
                    "logical_type": "L2",
                    "status": "Connected2",
                    "location": "Lo2",
                    "storage_id": "3b-3f-4f-5f-5f2",
                    "native_disk_group_id": "NDG2",
                    "serial_number": "234-fgh2",
                    "manufacturer": "Man2",
                    "model": "GA42",
                    "firmware": "Firm2",
                    "speed": 50003,
                    "capacity": 20000003,
                    "health_score": 893,
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_show(self):
        self.mock_object(
            db, 'disk_get',
            fakes.fake_disk_show)
        req = fakes.HTTPRequest.blank(
            '/v1/shares/d7fe425b-fddc-4ba4-accb-4343c142dc47')

        res_dict = self.controller.show(
            req, 'd7fe425b-fddc-4ba4-accb-4343c142dc47')

        expctd_dict = {
            "created_at": "2020-06-10T07:17:31.157079",
            "updated_at": "2020-06-10T07:17:31.157079",
            "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
            "name": "Nam",
            "native_disk_id": "5f5c806d-2e65-473c-b612",
            "physical_type": "P",
            "logical_type": "L",
            "status": "Connected",
            "location": "Lo",
            "storage_id": "3b-3f-4f-5f-5f",
            "native_disk_group_id": "NDG",
            "serial_number": "234-fgh",
            "manufacturer": "Man",
            "model": "GA4",
            "firmware": "Firm",
            "speed": 5000,
            "capacity": 2000000,
            "health_score": 89,
        }

        self.assertDictEqual(expctd_dict, res_dict)
