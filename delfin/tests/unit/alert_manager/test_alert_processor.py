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
from delfin.common import constants
from delfin.tests.unit.alert_manager import fakes


class AlertProcessorTestCase(unittest.TestCase):
    ALERT_PROCESSOR_CLASS = 'delfin.alert_manager.alert_processor' \
                            '.AlertProcessor'

    def _get_alert_processor(self):
        alert_processor_class = importutils.import_class(
            self.ALERT_PROCESSOR_CLASS)
        alert_processor = alert_processor_class()
        return alert_processor

    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.drivers.api.API.parse_alert')
    @mock.patch('delfin.exporter.base_exporter'
                '.AlertExporterManager.dispatch')
    @mock.patch('delfin.context.get_admin_context')
    def test_process_alert_info_success(self, mock_ctxt, mock_export_model,
                                        mock_parse_alert, mock_storage):
        fake_storage_info = fakes.fake_storage_info()
        input_alert = {'storage_id': 'abcd-1234-56789',
                       'connUnitEventId': 79,
                       'connUnitName': '000192601409',
                       'connUnitEventType':
                           constants.EventType.EQUIPMENT_ALARM,
                       'connUnitEventDescr': 'Diagnostic '
                                             'event trace triggered.',
                       'connUnitEventSeverity': 'warning',
                       'connUnitType': 'storage-subsystem',
                       'asyncEventSource': 'eventsource1',
                       'asyncEventCode': '1050',
                       'asyncEventComponentType': '1051',
                       'asyncEventComponentName': 'comp1'}

        expected_alert_model = {'storage_id': fake_storage_info['id'],
                                'storage_name': fake_storage_info['name'],
                                'vendor':
                                    fake_storage_info['vendor'],
                                'model': fake_storage_info['model'],
                                'serial_number':
                                    fake_storage_info['serial_number'],
                                'location': 'Array id=000192601409,Component '
                                            'type=location1 '
                                            'Group,Component name=comp1,Event '
                                            'source=symmetrix',
                                'type': input_alert['connUnitEventType'],
                                'severity': constants.Severity.WARNING,
                                'category': constants.Category.NOT_SPECIFIED,
                                'description':
                                    input_alert['connUnitEventDescr'],
                                'resource_type':
                                    constants.DEFAULT_RESOURCE_TYPE,
                                'alert_id': input_alert['asyncEventCode'],
                                'alert_name': 'SAMPLE_ALERT_NAME',
                                'sequence_number': 79,
                                'recovery_advice': 'NA'
                                }
        mock_storage.return_value = fake_storage_info
        expected_ctxt = context.get_admin_context()
        mock_ctxt.return_value = expected_ctxt
        mock_parse_alert.return_value = fakes.fake_alert_model()
        alert_processor_inst = self._get_alert_processor()
        alert_processor_inst.process_alert_info(input_alert)

        # Verify that model returned by driver is exported
        mock_export_model.assert_called_once_with(expected_ctxt,
                                                  expected_alert_model)

    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.drivers.api.API.parse_alert',
                fakes.parse_alert_exception)
    def test_process_alert_info_exception(self, mock_storage):
        """ Mock parse alert for raising exception"""
        alert = {'storage_id': 'abcd-1234-56789',
                 'storage_name': 'storage1',
                 'vendor': 'fake vendor',
                 'model': 'fake mode',
                 'serial_number': 'serial-1234'}

        mock_storage.return_value = fakes.fake_storage_info()
        alert_processor_inst = self._get_alert_processor()
        self.assertRaisesRegex(exception.InvalidResults,
                               "Failed to fill the alert model from driver.",
                               alert_processor_inst.process_alert_info, alert)
