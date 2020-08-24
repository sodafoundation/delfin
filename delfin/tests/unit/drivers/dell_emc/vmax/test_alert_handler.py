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

from delfin import exception
from delfin.common import constants


class AlertHandlerTestCase(unittest.TestCase):
    ALERT_HANDLER_CLASS = 'delfin.drivers.dell_emc.vmax.alert_handler' \
                          '.snmp_alerts.AlertHandler'

    def _get_alert_handler(self):
        alert_handler_class = importutils.import_class(
            self.ALERT_HANDLER_CLASS)
        alert_handler = alert_handler_class()
        return alert_handler

    def _get_fake_alert_info(self):
        alert_info = {
            '1.3.6.1.3.94.1.11.1.3.0': 79,
            '1.3.6.1.3.94.1.6.1.20.0': '000192601409',
            '1.3.6.1.3.94.1.11.1.7.0': 'topology',
            '1.3.6.1.3.94.1.11.1.9.0': 'Symmetrix 000192601409 FastSRP '
                                       'SRP_1 : Remote (SRDF) diagnostic '
                                       'event trace triggered.',
            '1.3.6.1.3.94.1.11.1.6.0': '6',
            '1.3.6.1.3.94.1.6.1.3.0': 'storage-subsystem',
            '1.3.6.1.4.1.1139.3.8888.1.0.0': 'symmetrix',
            '1.3.6.1.4.1.1139.3.8888.2.0.0': '1050',
            '1.3.6.1.4.1.1139.3.8888.3.0.0': '1051',
            '1.3.6.1.4.1.1139.3.8888.4.0.0': 'SRP_1'}

        return alert_info

    def test_parse_alert_with_all_necessary_info(self):
        """ Success flow with all necessary parameters"""
        alert_handler_inst = self._get_alert_handler()
        alert = self._get_fake_alert_info()

        expected_alert_model = {
            'alert_id': alert['1.3.6.1.4.1.1139.3.8888.2.0.0'],
            'alert_name': 'SYMAPI_AEVENT2_UID_MOD_DIAG_TRACE_TRIG',
            'severity': constants.Severity.WARNING,
            'category': constants.Category.NOT_SPECIFIED,
            'type': constants.EventType.EQUIPMENT_ALARM,
            'sequence_number': alert['1.3.6.1.3.94.1.11.1.3.0'],
            'description': alert['1.3.6.1.3.94.1.11.1.9.0'],
            'recovery_advice': 'None',
            'resource_type': alert['1.3.6.1.3.94.1.6.1.3.0'],
            'location': 'Array id=000192601409,'
                        'Component type=Symmetrix Disk '
                        'Group,'
                        'Component name=SRP_1,'
                        'Event source=symmetrix',
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
        alert['1.3.6.1.3.94.1.11.1.6.0'] = ''
        self.assertRaisesRegex(exception.InvalidInput, "Mandatory information "
                                                       "connUnitEventSeverity"
                                                       " missing",
                               alert_handler_inst.parse_alert, context, alert)
