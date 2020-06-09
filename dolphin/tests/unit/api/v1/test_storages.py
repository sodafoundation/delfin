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

from dolphin import db
from dolphin import exception
from dolphin import test
from dolphin.api.v1.storages import StorageController
from dolphin.tests.unit.api import fakes


class TestStorageController(test.TestCase):

    def setUp(self):
        super(TestStorageController, self).setUp()
        self.task_rpcapi = mock.Mock()
        self.driver_api = mock.Mock()
        self.controller = StorageController()
        self.mock_object(self.controller, 'task_rpcapi', self.task_rpcapi)
        self.mock_object(self.controller, 'driver_api', self.driver_api)

    @mock.patch.object(db, 'storage_get',
                       mock.Mock(return_value={'id': 'fake_id'}))
    def test_delete(self):
        req = fakes.HTTPRequest.blank('/storages/fake_id')
        self.controller.delete(req, 'fake_id')
        ctxt = req.environ['dolphin.context']
        db.storage_get.assert_called_once_with(ctxt, 'fake_id')
        self.task_rpcapi.remove_storage_resource.assert_called_with(
            ctxt, 'fake_id', mock.ANY)
        self.task_rpcapi.remove_storage_in_cache.assert_called_once_with(
            ctxt, 'fake_id')

    def test_delete_with_invalid_id(self):
        self.mock_object(
            db, 'storage_get',
            mock.Mock(side_effect=exception.StorageNotFound('fake_id')))
        req = fakes.HTTPRequest.blank('/storages/fake_id')
        self.assertRaises(exception.StorageNotFound,
                          self.controller.delete,
                          req, 'fake_id')

    def test_storages_list(self):
        self.mock_object(
            db, 'storage_get_all',
            fakes.fake_storages_get_all)
        req = fakes.HTTPRequest.blank('/storages')

        res_dict = self.controller.index(req)
        expctd_dict = {
            "storages": [
                {
                    "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
                    "created_at": "2020-06-09T08:59:48.710890",
                    "free_capacity": 1045449,
                    "updated_at": "2020-06-09T08:59:48.769470",
                    "name": "fake_driver",
                    "location": "HK",
                    "firmware_version": "1.0.0",
                    "vendor": "fake_vendor",
                    "status": "normal",
                    "sync_status": "SYNCED",
                    "model": "fake_model",
                    "description": "it is a fake driver.",
                    "serial_number": "2102453JPN12KA0000113",
                    "used_capacity": 3126,
                    "total_capacity": 1048576
                },
                {
                    "id": "277a1d8f-a36e-423e-bdd9-db154f32c289",
                    "created_at": "2020-06-09T08:58:23.008821",
                    "free_capacity": 1045449,
                    "updated_at": "2020-06-09T08:58:23.033601",
                    "name": "fake_driver",
                    "location": "HK",
                    "firmware_version": "1.0.0",
                    "vendor": "fake_vendor",
                    "status": "normal",
                    "sync_status": "SYNCED",
                    "model": "fake_model",
                    "description": "it is a fake driver.",
                    "serial_number": "2102453JPN12KA0000112",
                    "used_capacity": 3126,
                    "total_capacity": 1048576
                }
            ]
        }
        self.assertEqual(expctd_dict, res_dict)

    def test_storages_list_with_filter(self):
        self.mock_object(
            db, 'storage_get_all',
            fakes.fake_storages_get_all)
        req = fakes.HTTPRequest.blank(
            '/storages/?name=fake_driver&sort=name:asc&wrongfilter=remove')

        res_dict = self.controller.index(req)
        expctd_dict = {
            "storages": [
                {
                    "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
                    "created_at": "2020-06-09T08:59:48.710890",
                    "free_capacity": 1045449,
                    "updated_at": "2020-06-09T08:59:48.769470",
                    "name": "fake_driver",
                    "location": "HK",
                    "firmware_version": "1.0.0",
                    "vendor": "fake_vendor",
                    "status": "normal",
                    "sync_status": "SYNCED",
                    "model": "fake_model",
                    "description": "it is a fake driver.",
                    "serial_number": "2102453JPN12KA0000113",
                    "used_capacity": 3126,
                    "total_capacity": 1048576
                }
            ]
        }
        self.assertEqual(expctd_dict, res_dict)

    def test_storages_show(self):
        self.mock_object(
            db, 'storage_get',
            fakes.fake_storages_show)
        req = fakes.HTTPRequest.blank(
            '/storages/12c2d52f-01bc-41f5-b73f-7abf6f38a2a6')

        res_dict = self.controller.index(req)
        expctd_dict = {
            "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
            "created_at": "2020-06-09T08:59:48.710890",
            "free_capacity": 1045449,
            "updated_at": "2020-06-09T08:59:48.769470",
            "name": "fake_driver",
            "location": "HK",
            "firmware_version": "1.0.0",
            "vendor": "fake_vendor",
            "status": "normal",
            "sync_status": "SYNCED",
            "model": "fake_model",
            "description": "it is a fake driver.",
            "serial_number": "2102453JPN12KA0000113",
            "used_capacity": 3126,
            "total_capacity": 1048576
        }
        self.assertEqual(expctd_dict, res_dict)
