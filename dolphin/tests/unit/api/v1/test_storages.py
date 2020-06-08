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
