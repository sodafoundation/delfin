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

from oslo_utils import importutils

from dolphin import exception


class AlertHandlerTestCase(unittest.TestCase):
    ALERT_HANDLER_CLASS = 'dolphin.drivers.dell_emc.vmax.alert_handler' \
                          '.AlertHandler'

    def _get_alert_handler(self):
        alert_handler_class = importutils.import_class(
            self.ALERT_HANDLER_CLASS)
        alert_handler = alert_handler_class()
        return alert_handler

    def _get_fake_alert_info(self):
        alert_info = {'storage_id': 'abcd-1234-56789',
                      'storage_name': 'storage1', 'vendor': 'fake vendor',
                      'model': 'fake model', 'connUnitEventId': 79,
                      'connUnitName': '000192601409',
                      'connUnitEventType': 'topology',
                      'connUnitEventDescr': 'Symmetrix 000192601409 FastSRP '
                                            'SRP_1 : Remote (SRDF) diagnostic '
                                            'event trace triggered.',
                      'connUnitEventSeverity': 'warning',
                      'connUnitType': 'storage-subsystem',
                      'emcAsyncEventSource': 'symmetrix',
                      'emcAsyncEventCode': '1050',
                      'emcAsyncEventComponentType': '1051',
                      'emcAsyncEventComponentName': 'SRP_1'}

        return alert_info

    def test_parse_alert_with_all_necessary_info(self):
        """ Success flow with all necessary parameters"""
        alert_handler_inst = self._get_alert_handler()
        alert = self._get_fake_alert_info()

        expected_alert_model = {'me_dn': alert['storage_id'],
                                'me_name': alert['storage_name'],
                                'manufacturer': alert['vendor'],
                                'product_name': alert['model'],
                                'category': 'New',
                                'location': 'Component type: Symmetrix Disk '
                                            'Group,Component name: SRP_1',
                                'event_type': alert['connUnitEventType'],
                                'severity': alert['connUnitEventSeverity'],
                                'probable_cause': alert['connUnitEventDescr'],
                                'me_category': alert['connUnitType'],
                                'native_me_dn': alert['connUnitName'],
                                'alarm_id': alert['emcAsyncEventCode'],
                                'alarm_name':
                                    'SYMAPI_AEVENT2_UID_MOD_DIAG_TRACE_TRIG',
                                'clear_type': '',
                                'device_alert_sn': '',
                                'match_key': '',
                                }
        context = {}
        alert_model = alert_handler_inst.parse_alert(context, alert)

        # occur_time depends on current time
        # Verify that all other fields are matching
        expected_alert_model['occur_time'] = alert_model['occur_time']
        self.assertDictEqual(expected_alert_model, alert_model)

    def test_parse_alert_without_mandatory_info(self):
        """ Error flow with some mandatory parameters missing"""
        alert_handler_inst = self._get_alert_handler()
        context = {}
        alert = self._get_fake_alert_info()
        alert['storage_id'] = ''
        self.assertRaisesRegex(exception.InvalidInput, "Mandatory information "
                                                       "storage_id missing",
                               alert_handler_inst.parse_alert, context, alert)
