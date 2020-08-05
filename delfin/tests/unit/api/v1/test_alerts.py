# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest import mock

from oslo_utils import importutils

from delfin import context
from delfin import exception
from delfin.tests.unit.api import fakes


class AlertControllerTestCase(unittest.TestCase):
    ALERT_CONTROLLER_CLASS = 'delfin.api.v1.alerts.AlertController'

    @mock.patch('delfin.alert_manager.rpcapi.AlertAPI', mock.Mock())
    def _get_alert_controller(self):
        alert_controller_class = importutils.import_class(
            self.ALERT_CONTROLLER_CLASS)
        alert_controller = alert_controller_class()
        return alert_controller

    @mock.patch('delfin.db.storage_get', fakes.fake_storages_get_all)
    @mock.patch('delfin.drivers.api.API.clear_alert')
    def test_delete_alert_success(self, mock_clear_alert):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alerts'
                                      '/fake_sequence_number')
        fake_storage_id = 'abcd-1234-5678'
        fake_sequence_number = 'abcd-1234'

        alert_controller_inst = self._get_alert_controller()
        alert_controller_inst.delete(req, fake_storage_id,
                                     fake_sequence_number)
        self.assertTrue(mock_clear_alert.called_with(context, fake_storage_id,
                                                     fake_sequence_number))

    @mock.patch('delfin.db.storage_get', fakes.fake_storage_get_exception)
    @mock.patch('delfin.drivers.api.API.clear_alert', mock.Mock())
    def test_delete_alert_failure_storage_not_found(self):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alerts'
                                      '/fake_sequence_number')
        fake_storage_id = 'abcd-1234-5678'
        fake_sequence_number = 'abcd-1234'

        alert_controller_inst = self._get_alert_controller()
        self.assertRaisesRegex(exception.StorageNotFound, "Storage "
                                                          "abcd-1234-5678 "
                                                          "could not be "
                                                          "found",
                               alert_controller_inst.delete, req,
                               fake_storage_id, fake_sequence_number)
