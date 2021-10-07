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
from delfin.api.v1.port_groups import PortGroupController
from delfin.tests.unit.api import fakes


class TestPortGroupController(test.TestCase):

    def setUp(self):
        super(TestPortGroupController, self).setUp()
        self.controller = PortGroupController()

    def test_show(self):
        self.mock_object(
            db, 'port_groups_get_all',
            fakes.fake_port_groups_get_all)
        req = fakes.HTTPRequest.blank('/v1/storages/fakeid/port-groups')

        res_dict = self.controller.show(req, "aaaaa")

        expctd_dict = {
            "port_groups": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "description": 'fake port group',
                    "native_port_group_id": "PG_1",
                    'ports': [],
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_storage_host_group_id": 'hg1',
                    "description": 'fake port group',
                    "native_port_group_id": "PG_2",
                    'ports': [],
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)
