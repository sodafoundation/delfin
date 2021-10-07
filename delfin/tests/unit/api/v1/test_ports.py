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
from delfin.api.v1.ports import PortController
from delfin.tests.unit.api import fakes


class TestPortController(test.TestCase):

    def setUp(self):
        super(TestPortController, self).setUp()
        self.controller = PortController()

    def test_list(self):
        self.mock_object(
            db, 'port_get_all',
            fakes.fake_ports_get_all)
        req = fakes.HTTPRequest.blank('/v1/ports/fakeid')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "ports": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "native_port_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "location": "lh",
                    "type": "type_d",
                    "logical_type": "logi_type_d",
                    "connection_status": "successfully connected",
                    "health_status": "hs_12",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_parent_id": "parent_d",
                    "speed": 200000,
                    "max_speed": 200000,
                    "wwn": "wwnd",
                    "mac_address": "5b-65-89-90-b3-f6",
                    "ipv4": "127.0.0.1",
                    "ipv4_mask": "255.255.255.0",
                    "ipv6": "192.168.159.130",
                    "ipv6_mask": "255.255.255.255.255.0",
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "native_port_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "location": "lh2",
                    "type": "type_d2",
                    "logical_type": "logi_type_d2",
                    "connection_status": "successfully connected",
                    "health_status": "hs_122",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_parent_id": "parent_d2",
                    "speed": 200000,
                    "max_speed": 200000,
                    "wwn": "wwnd",
                    "mac_address": "5b-65-89-90-b3-f6",
                    "ipv4": "127.0.0.1",
                    "ipv4_mask": "255.255.255.0",
                    "ipv6": "192.168.159.130",
                    "ipv6_mask": "255.255.255.255.255.0",
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_show(self):
        self.mock_object(
            db, 'port_get',
            fakes.fake_port_show)
        req = fakes.HTTPRequest.blank(
            '/v1/ports/d7fe425b-fddc-4ba4-accb-4343c142dc47')

        res_dict = self.controller.show(
            req, 'd7fe425b-fddc-4ba4-accb-4343c142dc47')

        expctd_dict = {
            "created_at": "2020-06-10T07:17:31.157079",
            "updated_at": "2020-06-10T07:17:31.157079",
            "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
            "name": "004DF",
            "native_port_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "location": "lh",
            "type": "type_d",
            "logical_type": "logi_type_d",
            "connection_status": "successfully connected",
            "health_status": "hs_12",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "native_parent_id": "parent_d",
            "speed": 200000,
            "max_speed": 200000,
            "wwn": "wwnd",
            "mac_address": "5b-65-89-90-b3-f6",
            "ipv4": "127.0.0.1",
            "ipv4_mask": "255.255.255.0",
            "ipv6": "192.168.159.130",
            "ipv6_mask": "255.255.255.255.255.0",
        }

        self.assertDictEqual(expctd_dict, res_dict)
