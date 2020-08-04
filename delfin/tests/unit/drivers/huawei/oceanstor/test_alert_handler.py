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
    ALERT_HANDLER_CLASS = 'delfin.drivers.huawei.oceanstor.alert_handler' \
                          '.AlertHandler'

    def _get_alert_handler(self):
        alert_handler_class = importutils.import_class(
            self.ALERT_HANDLER_CLASS)
        alert_handler = alert_handler_class()
        return alert_handler

    def _get_fake_alert_info(self):
        alert_info = {'hwIsmReportingAlarmLocationInfo': 'location=location1',
                      'hwIsmReportingAlarmFaultTitle': 'Trap Test Alarm',
                      'hwIsmReportingAlarmFaultType': 'equipmentFault',
                      'hwIsmReportingAlarmFaultLevel': 'criticalAlarm',
                      'hwIsmReportingAlarmAlarmID': '4294967294',
                      'hwIsmReportingAlarmSerialNo': '4294967295',
                      'hwIsmReportingAlarmAdditionInfo': 'This is just for '
                                                         'testing.Please '
                                                         'ignore it',
                      'hwIsmReportingAlarmFaultCategory': 'faultAlarm',
                      'hwIsmReportingAlarmLocationAlarmID': '230584300921369',
                      'hwIsmReportingAlarmRestoreAdvice': 'Sample advice',
                      'hwIsmReportingAlarmNodeCode': 'Array',
                      'hwIsmReportingAlarmFaultTime': '2020-6-25,1:42:26.0'}

        return alert_info

    def _get_fake_incomplete_alert_info(self):
        # hwIsmReportingAlarmFaultCategory is missing here
        alert_info = {'hwIsmReportingAlarmLocationInfo': 'location=location1',
                      'hwIsmReportingAlarmFaultTitle': 'Trap Test Alarm',
                      'hwIsmReportingAlarmFaultType': 'equipmentFault',
                      'hwIsmReportingAlarmFaultLevel': 'criticalAlarm',
                      'hwIsmReportingAlarmAlarmID': '4294967294',
                      'hwIsmReportingAlarmSerialNo': '4294967295',
                      'hwIsmReportingAlarmAdditionInfo': 'This is just for '
                                                         'testing.Please '
                                                         'ignore it',
                      'hwIsmReportingAlarmLocationAlarmID': '230584300921369',
                      'hwIsmReportingAlarmFaultTime': '2020-6-25,1:42:26.0'}

        return alert_info

    def test_parse_alert_with_all_necessary_info(self):
        """ Success flow with all necessary parameters"""
        alert_handler_inst = self._get_alert_handler()
        alert = self._get_fake_alert_info()

        expected_alert_model = {
            'alert_id': alert['hwIsmReportingAlarmAlarmID'],
            'alert_name': alert[
                'hwIsmReportingAlarmFaultTitle'],
            'severity': constants.Severity.CRITICAL,
            'category': constants.Category.FAULT,
            'type': alert['hwIsmReportingAlarmFaultType'],
            'sequence_number': alert['hwIsmReportingAlarmSerialNo'],
            'description': alert[
                'hwIsmReportingAlarmAdditionInfo'],
            'recovery_advice': alert['hwIsmReportingAlarmRestoreAdvice'],
            'resource_type': constants.DEFAULT_RESOURCE_TYPE,
            'occur_time': 1593029546,
            'location': 'Node code=' + alert['hwIsmReportingAlarmNodeCode']
                        + ',' + alert['hwIsmReportingAlarmLocationInfo']
        }
        context = {}
        alert_model = alert_handler_inst.parse_alert(context, alert)

        # Verify that all other fields are matching
        self.assertDictEqual(expected_alert_model, alert_model)

    def test_parse_alert_without_mandatory_info(self):
        """ Error flow with some mandatory parameters missing"""
        alert_handler_inst = self._get_alert_handler()
        context = {}
        alert = self._get_fake_incomplete_alert_info()
        self.assertRaisesRegex(exception.InvalidInput,
                               "Mandatory information "
                               "hwIsmReportingAlarmNodeCode missing in alert "
                               "message.",
                               alert_handler_inst.parse_alert, context, alert)
