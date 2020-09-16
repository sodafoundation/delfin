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


def fake_alert_list():
    return [{
        'alert_id': '19660818',
        'sequence_number': 10,
        'alert_name': 'SNMP connect failed',
        'category': 'Fault',
        'severity': 'Major',
        'type': 'OperationalViolation',
        'location': 'NetworkEntity=storage1',
        'description': "SNMP connection to the storage failed. "
                       "SNMP traps from storage will not be received.",
        'recovery_advice': "1. The network connection is abnormal. "
                           "2. SNMP authentication parameters "
                           "are invalid.",
        'occur_time': 13445566900
    }]


def fake_storage_info():
    return {
        'id': 'abcd-1234-56789',
        'name': 'storage1',
        'vendor': 'fake vendor',
        'model': 'fake model',
        'serial_number': 'serial-1234'
    }


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
    @mock.patch('delfin.task_manager.rpcapi.TaskAPI', mock.Mock())
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
    @mock.patch('delfin.task_manager.rpcapi.TaskAPI', mock.Mock())
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

    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.drivers.api.API.list_alerts')
    @mock.patch('delfin.task_manager.rpcapi.TaskAPI', mock.Mock())
    @mock.patch('delfin.api.views.alerts.build_alerts')
    def test_list_alert_success(self, mock_build_alerts, mock_fake_alerts,
                                mock_fake_storage):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alerts')
        req.GET['begin_time'] = '123400000'
        req.GET['end_time'] = '123500000'
        fake_storage_id = 'abcd-1234-5678'

        expected_alert_output = {
            'alert_id': '19660818',
            'sequence_number': 10,
            'alert_name': 'SNMP connect failed',
            'category': 'Fault',
            'severity': 'Major',
            'type': 'OperationalViolation',
            'location': 'NetworkEntity=storage1',
            'description': "SNMP connection to the storage failed. "
                           "SNMP traps from storage will not be received.",
            'recovery_advice': "1. The network connection is abnormal. "
                               "2. SNMP authentication parameters "
                               "are invalid.",
            'occur_time': 13445566900,
            'storage_id': fake_storage_id,
            'storage_name': 'storage1',
            'vendor': 'fake vendor',
            'model': 'fake model',
            'serial_number': 'serial-1234'
        }
        mock_fake_alerts.return_value = fake_alert_list()
        mock_fake_storage.return_value = fake_storage_info()

        alert_controller_inst = self._get_alert_controller()
        alert_controller_inst.show(req, fake_storage_id)
        self.assertTrue(mock_build_alerts.called_with(expected_alert_output))

    @mock.patch('delfin.task_manager.rpcapi.TaskAPI', mock.Mock())
    def test_list_alert_invalid_querypara(self):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alerts')
        req.GET['begin_time'] = '123400000'
        req.GET['end_time'] = '120400000'
        fake_storage_id = 'abcd-1234-5678'
        alert_controller_inst = self._get_alert_controller()
        self.assertRaisesRegex(exception.InvalidInput, "end_time should be "
                                                       "greater than "
                                                       "begin_time",
                               alert_controller_inst.show, req,
                               fake_storage_id)
