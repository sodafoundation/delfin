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
from dolphin.api.v1.storage_pools import StoragePoolController
from dolphin.tests.unit.api import fakes


class TestStoragePoolController(test.TestCase):

    def setUp(self):
        super(TestStoragePoolController, self).setUp()
        self.controller = StoragePoolController()

    def test_list(self):
        self.mock_object(
            db, 'storage_pool_get_all',
            fakes.fake_storage_pool_get_all)
        req = fakes.HTTPRequest.blank('/storage-pools')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "storage_pools": [
                {
                    "created_at": "2020-06-10T07:17:08.707356",
                    "updated_at": "2020-06-10T07:17:08.707356",
                    "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
                    "name": "SRP_1",
                    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
                    "original_id": "SRP_1",
                    "description": "Dell EMC VMAX Pool",
                    "status": "normal",
                    "storage_type": "block",
                    "total_capacity": 26300318136401,
                    "used_capacity": 19054536509358,
                    "free_capacity": 7245781627043
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_list_with_filter(self):
        self.mock_object(
            db, 'storage_pool_get_all',
            fakes.fake_storage_pool_get_all)
        req = fakes.HTTPRequest.blank(
            '/storage-pools/'
            '?storage_id=12c2d52f-01bc-41f5-b73f-7abf6f38a2a6'
            '&sort=name:asc&wrongfilter=remove')
        res_dict = self.controller.index(req)
        expctd_dict = {
            "storage_pools": [
                {
                    "created_at": "2020-06-10T07:17:08.707356",
                    "updated_at": "2020-06-10T07:17:08.707356",
                    "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
                    "name": "SRP_1",
                    "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
                    "original_id": "SRP_1",
                    "description": "Dell EMC VMAX Pool",
                    "status": "normal",
                    "storage_type": "block",
                    "total_capacity": 26300318136401,
                    "used_capacity": 19054536509358,
                    "free_capacity": 7245781627043
                }
            ]
        }

        self.assertDictEqual(expctd_dict, res_dict)

    def test_show(self):
        self.mock_object(
            db, 'storage_pool_get',
            fakes.fake_storage_pool_show)
        req = fakes.HTTPRequest.blank(
            '/storage-pools/14155a1f-f053-4ccb-a846-ed67e4387428')

        res_dict = self.controller.show(
            req, '14155a1f-f053-4ccb-a846-ed67e4387428')
        expctd_dict = {
            "created_at": "2020-06-10T07:17:08.707356",
            "updated_at": "2020-06-10T07:17:08.707356",
            "id": "14155a1f-f053-4ccb-a846-ed67e4387428",
            "name": "SRP_1",
            "storage_id": '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
            "original_id": "SRP_1",
            "description": "Dell EMC VMAX Pool",
            "status": "normal",
            "storage_type": "block",
            "total_capacity": 26300318136401,
            "used_capacity": 19054536509358,
            "free_capacity": 7245781627043
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_show_with_invalid_id(self):
        self.mock_object(
            db, 'storage_pool_get',
            mock.Mock(side_effect=exception.StoragePoolNotFound('fake_id')))
        req = fakes.HTTPRequest.blank('/storage-pools/fake_id')
        self.assertRaises(exception.StoragePoolNotFound,
                          self.controller.show,
                          req, 'fake_id')
