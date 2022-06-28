# Copyright 2021 The SODA Authors.
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
import random
from unittest import mock

from pysnmp.entity.rfc3413.oneliner import cmdgen

from delfin import context
from delfin import db
from delfin import test
from delfin.alert_manager import snmp_validator
from delfin.common import constants
from delfin.exporter import base_exporter
from delfin.tests.unit.alert_manager import fakes


class TestSNMPValidator(test.TestCase):
    @mock.patch.object(db, 'alert_source_update',
                       mock.Mock())
    @mock.patch('delfin.alert_manager.snmp_validator.'
                'SNMPValidator.validate_connectivity')
    def test_validate(self, mock_validate_connectivity):
        validator = snmp_validator.SNMPValidator()

        mock_validate_connectivity.return_value = fakes.fake_v3_alert_source()
        v3_alert_source_without_engine_id = fakes.fake_v3_alert_source()
        v3_alert_source_without_engine_id.pop('engine_id')
        validator.validate(context, v3_alert_source_without_engine_id)
        self.assertEqual(db.alert_source_update.call_count, 1)

        mock_validate_connectivity.return_value = fakes.fake_v3_alert_source()
        validator.validate(context,
                           fakes.fake_v3_alert_source())
        self.assertEqual(db.alert_source_update.call_count, 1)

    @mock.patch.object(cmdgen.UdpTransportTarget, '_resolveAddr',
                       mock.Mock())
    @mock.patch.object(cmdgen.UdpTransportTarget, 'setLocalAddress',
                       mock.Mock())
    @mock.patch.object(cmdgen.CommandGenerator, 'getCmd',
                       fakes.mock_cmdgen_get_cmd)
    @mock.patch('delfin.db.access_info_get')
    @mock.patch('pysnmp.entity.observer.MetaObserver.registerObserver')
    @mock.patch('pysnmp.carrier.asyncore.dispatch.AbstractTransportDispatcher'
                '.closeDispatcher')
    def test_validate_connectivity(self, mock_close_dispatcher,
                                   mock_register_observer,
                                   mock_access_info_get):
        # Get a random host
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(0, 255)
        host = str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d)
        # Get a random port
        port = random.randint(1024, 65535)
        # snmpv3
        v3_alert_source = fakes.fake_v3_alert_source()
        v3_alert_source['host'] = host
        v3_alert_source['port'] = port
        mock_access_info_get.return_value = {'model': 'vsp'}
        snmp_validator.SNMPValidator.validate_connectivity(
            context.RequestContext(), v3_alert_source)
        self.assertEqual(mock_close_dispatcher.call_count, 1)
        self.assertEqual(mock_register_observer.call_count, 1)
        # snmpv2c
        v2_alert_source = fakes.fake_v2_alert_source()
        v2_alert_source['host'] = host
        v2_alert_source['port'] = port
        snmp_validator.SNMPValidator.validate_connectivity(
            context.RequestContext(), v2_alert_source)
        self.assertEqual(mock_close_dispatcher.call_count, 2)
        self.assertEqual(mock_register_observer.call_count, 1)

    @mock.patch.object(db, 'storage_get',
                       mock.Mock(return_value=fakes.FAKE_STOTRAGE))
    @mock.patch.object(snmp_validator.SNMPValidator,
                       '_dispatch_snmp_validation_alert', mock.Mock())
    def test_handle_validation_result(self):
        validator = snmp_validator.SNMPValidator()

        validator._handle_validation_result(
            context, fakes.FAKE_STOTRAGE['id'],
            constants.Category.FAULT)
        snmp_validator.SNMPValidator._dispatch_snmp_validation_alert \
            .assert_called_with(context,
                                fakes.FAKE_STOTRAGE,
                                constants.Category.FAULT)

        validator._handle_validation_result(
            context, fakes.FAKE_STOTRAGE['id'],
            constants.Category.RECOVERY)
        snmp_validator.SNMPValidator._dispatch_snmp_validation_alert \
            .assert_called_with(context,
                                fakes.FAKE_STOTRAGE,
                                constants.Category.RECOVERY)

    @mock.patch.object(base_exporter.AlertExporterManager, 'dispatch',
                       mock.Mock())
    def test_dispatch_snmp_validation_alert(self):
        validator = snmp_validator.SNMPValidator()
        storage = fakes.FAKE_STOTRAGE
        alert = {
            'storage_id': storage['id'],
            'storage_name': storage['name'],
            'vendor': storage['vendor'],
            'model': storage['model'],
            'serial_number': storage['serial_number'],
            'alert_id': constants.SNMP_CONNECTION_FAILED_ALERT_ID,
            'sequence_number': 0,
            'alert_name': 'SNMP connect failed',
            'category': constants.Category.FAULT,
            'severity': constants.Severity.MAJOR,
            'type': constants.EventType.COMMUNICATIONS_ALARM,
            'location': 'NetworkEntity=%s' % storage['name'],
            'description': "SNMP connection to the storage failed. "
                           "SNMP traps from storage will not be received.",
            'recovery_advice': "1. The network connection is abnormal. "
                               "2. SNMP authentication parameters "
                               "are invalid.",
            'occur_time': mock.ANY,
        }

        validator._dispatch_snmp_validation_alert(
            context, storage, constants.Category.FAULT)
        base_exporter.AlertExporterManager(). \
            dispatch.assert_called_once_with(context, alert)
