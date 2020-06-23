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

from unittest import mock

from delfin import db
from delfin import exception
from delfin import test
from delfin.api.v1.volumes import VolumeController
from delfin.tests.unit.api import fakes


class TestVolumeController(test.TestCase):

    def setUp(self):
        super(TestVolumeController, self).setUp()
        self.controller = VolumeController()

    def test_list(self):
        self.mock_object(
            db, 'volume_get_all',
            fakes.fake_volume_get_all)
        req = fakes.HTTPRequest.blank('/volumes')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "volumes": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_storage_pool_id": "SRP_1",
                    "description": "fake_storage 'thin device' volume",
                    "status": "available",
                    "native_volume_id": "004DF",
                    "wwn": "60000970000297801855533030344446",
                    "type": 'thin',
                    "total_capacity": 1075838976,
                    "used_capacity": 0,
                    "free_capacity": 1075838976,
                    "compressed": True,
                    "deduplicated": False
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "dad84a1f-db8d-49ab-af40-048fc3544c12",
                    "name": "004E0",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_storage_pool_id": "SRP_1",
                    "description": "fake_storage 'thin device' volume",
                    "status": "available",
                    "native_volume_id": "004E0",
                    "wwn": "60000970000297801855533030344530",
                    "type": 'thin',
                    "total_capacity": 1075838976,
                    "used_capacity": 0,
                    "free_capacity": 1075838976,
                    "compressed": True,
                    "deduplicated": False
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_list_with_filter(self):
        self.mock_object(
            db, 'volume_get_all',
            fakes.fake_volume_get_all)
        req = fakes.HTTPRequest.blank(
            '/volumes/'
            '?storage_id=12c2d52f-01bc-41f5-b73f-7abf6f38a2a6'
            '&sort=name:asc&wrongfilter=remove')
        res_dict = self.controller.index(req)
        expctd_dict = {
            "volumes": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "name": "004DF",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_storage_pool_id": "SRP_1",
                    "description": "fake_storage 'thin device' volume",
                    "status": "available",
                    "native_volume_id": "004DF",
                    "wwn": "60000970000297801855533030344446",
                    "type": 'thin',
                    "total_capacity": 1075838976,
                    "used_capacity": 0,
                    "free_capacity": 1075838976,
                    "compressed": True,
                    "deduplicated": False
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "dad84a1f-db8d-49ab-af40-048fc3544c12",
                    "name": "004E0",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_storage_pool_id": "SRP_1",
                    "description": "fake_storage 'thin device' volume",
                    "status": "available",
                    "native_volume_id": "004E0",
                    "wwn": "60000970000297801855533030344530",
                    "type": 'thin',
                    "total_capacity": 1075838976,
                    "used_capacity": 0,
                    "free_capacity": 1075838976,
                    "compressed": True,
                    "deduplicated": False
                }
            ]
        }

        self.assertDictEqual(expctd_dict, res_dict)

    def test_show(self):
        self.mock_object(
            db, 'volume_get',
            fakes.fake_volume_show)
        req = fakes.HTTPRequest.blank(
            '/volumes/d7fe425b-fddc-4ba4-accb-4343c142dc47')

        res_dict = self.controller.show(
            req, 'd7fe425b-fddc-4ba4-accb-4343c142dc47')
        expctd_dict = {
            "created_at": "2020-06-10T07:17:31.157079",
            "updated_at": "2020-06-10T07:17:31.157079",
            "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
            "name": "004DF",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "native_storage_pool_id": "SRP_1",
            "description": "fake_storage 'thin device' volume",
            "status": "available",
            "native_volume_id": "004DF",
            "wwn": "60000970000297801855533030344446",
            "type": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        }

        self.assertDictEqual(expctd_dict, res_dict)

    def test_show_with_invalid_id(self):
        self.mock_object(
            db, 'volume_get',
            mock.Mock(side_effect=exception.VolumeNotFound('fake_id')))
        req = fakes.HTTPRequest.blank('/volumes/fake_id')
        self.assertRaises(exception.VolumeNotFound,
                          self.controller.show,
                          req, 'fake_id')
