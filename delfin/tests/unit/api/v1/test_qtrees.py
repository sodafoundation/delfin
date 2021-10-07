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
from delfin.api.v1.qtrees import QtreeController
from delfin.tests.unit.api import fakes


class TestQtreeController(test.TestCase):

    def setUp(self):
        super(TestQtreeController, self).setUp()
        self.controller = QtreeController()

    def test_list(self):
        self.mock_object(
            db, 'qtree_get_all',
            fakes.fake_qtree_get_all)
        req = fakes.HTTPRequest.blank('/v1/qtrees')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "qtrees": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "native_qtree_id": "QT_ID_1",
                    "name": "004DF",
                    "path": "path_1",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_filesystem_id": "NF_ID_1",
                    "security_mode": "S_M_1",
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "native_qtree_id": "QT_ID_1",
                    "name": "004DF",
                    "path": "path_1",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_filesystem_id": "NF_ID_1",
                    "security_mode": "S_M_1",
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_show(self):
        self.mock_object(
            db, 'qtree_get',
            fakes.fake_qtree_show)
        req = fakes.HTTPRequest.blank(
            '/v1/qtrees/d7fe425b-fddc-4ba4-accb-4343c142dc47')

        res_dict = self.controller.show(
            req, 'd7fe425b-fddc-4ba4-accb-4343c142dc47')

        expctd_dict = {
            "created_at": "2020-06-10T07:17:31.157079",
            "updated_at": "2020-06-10T07:17:31.157079",
            "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
            "native_qtree_id": "QT_ID_1",
            "name": "004DF",
            "path": "path_1",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "native_filesystem_id": "NF_ID_1",
            "security_mode": "S_M_1",
        }

        self.assertDictEqual(expctd_dict, res_dict)
