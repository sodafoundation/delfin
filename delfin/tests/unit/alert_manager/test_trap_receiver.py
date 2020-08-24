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

from unittest import mock

from oslo_utils import importutils
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config

from delfin import exception
from delfin import test
from delfin.tests.unit.alert_manager import fakes


class TrapReceiverTestCase(test.TestCase):
    TRAP_RECEIVER_CLASS = 'delfin.alert_manager.trap_receiver' \
                          '.TrapReceiver'
    DEF_TRAP_RECV_ADDR = '127.0.0.1'
    DEF_TRAP_RECV_PORT = '162'

    def setUp(self):
        super(TrapReceiverTestCase, self).setUp()
        self.alert_rpc_api = mock.Mock()
        trap_receiver_class = importutils.import_class(
            self.TRAP_RECEIVER_CLASS)
        self.trap_receiver = trap_receiver_class(self.DEF_TRAP_RECV_ADDR,
                                                 self.DEF_TRAP_RECV_PORT)
        self.mock_object(self.trap_receiver,
                         'alert_rpc_api', self.alert_rpc_api)

    def _get_trap_receiver(self):
        return self.trap_receiver

    @mock.patch('pysnmp.carrier.asyncore.dispatch.AbstractTransportDispatcher'
                '.jobStarted')
    @mock.patch('delfin.db.api.alert_source_get_all')
    @mock.patch('pysnmp.carrier.asyncore.dgram.udp.UdpTransport'
                '.openServerMode', mock.Mock())
    @mock.patch('delfin.alert_manager.trap_receiver.TrapReceiver'
                '._mib_builder', mock.Mock())
    def test_start_success(self, mock_alert_source, mock_dispatcher):
        mock_alert_source.return_value = {}
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.trap_receiver_address = self.DEF_TRAP_RECV_ADDR
        trap_receiver_inst.trap_receiver_port = self.DEF_TRAP_RECV_PORT
        trap_receiver_inst.start()

        # Verify that snmp engine is initialised and transport config is set
        self.assertTrue(trap_receiver_inst.snmp_engine is not None)

    @mock.patch('pysnmp.carrier.asyncore.dispatch.AbstractTransportDispatcher'
                '.jobStarted')
    @mock.patch('delfin.db.api.alert_source_get_all')
    @mock.patch('delfin.alert_manager.trap_receiver.TrapReceiver'
                '._load_snmp_config', fakes.load_config_exception)
    def test_start_with_exception(self, mock_alert_source, mock_dispatcher):
        mock_alert_source.return_value = {}
        trap_receiver_inst = self._get_trap_receiver()

        # Mock load config to raise exception
        self.assertRaisesRegex(ValueError, "Failed to setup for trap listener",
                               trap_receiver_inst.start)

    @mock.patch('pysnmp.carrier.asyncore.dgram.udp.UdpTransport'
                '.openServerMode', mock.Mock())
    def test_add_transport_successful(self):
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        trap_receiver_inst.trap_receiver_address = self.DEF_TRAP_RECV_ADDR
        trap_receiver_inst.trap_receiver_port = self.DEF_TRAP_RECV_PORT
        trap_receiver_inst._add_transport()
        get_transport = config.getTransport(trap_receiver_inst.snmp_engine,
                                            udp.domainName)
        # Verify that snmp engine transport config is set after _add_transport
        self.assertTrue(get_transport is not None)

    def test_add_transport_exception(self):
        trap_receiver_inst = self._get_trap_receiver()

        # Mock exception by not initialising snmp engine
        self.assertRaisesRegex(ValueError,
                               "Port binding failed: Port is in use",
                               trap_receiver_inst._add_transport)

    @mock.patch('pysnmp.carrier.asyncore.dispatch.AbstractTransportDispatcher'
                '.jobStarted')
    @mock.patch('pysnmp.carrier.asyncore.dispatch.AbstractTransportDispatcher'
                '.closeDispatcher')
    @mock.patch('delfin.db.api.alert_source_get_all')
    @mock.patch('pysnmp.carrier.asyncore.dgram.udp.UdpTransport'
                '.openServerMode', mock.Mock())
    @mock.patch('pysnmp.entity.config.addTransport', fakes.mock_add_transport)
    @mock.patch('delfin.alert_manager.trap_receiver.TrapReceiver'
                '._mib_builder', mock.Mock())
    def test_stop_with_snmp_engine(self, mock_alert_source,
                                   mock_close_dispatcher, mock_dispatcher):
        mock_alert_source.return_value = {}
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.trap_receiver_address = self.DEF_TRAP_RECV_ADDR
        trap_receiver_inst.trap_receiver_port = self.DEF_TRAP_RECV_PORT
        trap_receiver_inst.start()
        trap_receiver_inst.stop()

        # Verify that close dispatcher is called during alert manager stop
        self.assertTrue(mock_close_dispatcher.called)

    @mock.patch('pysnmp.carrier.asyncore.dispatch.AbstractTransportDispatcher'
                '.closeDispatcher')
    def test_stop_without_snmp_engine(self, mock_close_dispatcher):
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.stop()

        # Verify that close dispatcher is not called when engine is not
        # initialised
        self.assertFalse(mock_close_dispatcher.called)

    @mock.patch('delfin.cryptor.decode', mock.Mock(return_value='public'))
    @mock.patch('delfin.alert_manager.snmp_validator.SNMPValidator.validate')
    @mock.patch('pysnmp.entity.config.addV1System')
    def test_sync_snmp_config_add_v2_version(self, mock_add_config,
                                             mock_validator):
        ctxt = {}
        alert_config = {'storage_id': 'abcd-1234-5678',
                        'version': 'snmpv2c',
                        'community_string': 'public'}
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        trap_receiver_inst.sync_snmp_config(ctxt,
                                            snmp_config_to_add=alert_config)

        # Verify that config is added to snmp engine
        # Storage_id is internally modified to remove '-' while adding
        mock_add_config.assert_called_once_with(trap_receiver_inst.snmp_engine,
                                                'abcd12345678',
                                                alert_config[
                                                    'community_string'],
                                                contextName=alert_config[
                                                    'community_string'])
        mock_validator.assert_called_once_with(ctxt, alert_config)

    @mock.patch('pysnmp.entity.config.delV1System')
    def test_sync_snmp_config_del_v2_version(self, mock_del_config):
        ctxt = {}
        alert_config = {'storage_id': 'abcd-1234-5678',
                        'version': 'snmpv2c',
                        'community_string': 'public'}
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        trap_receiver_inst.sync_snmp_config(ctxt,
                                            snmp_config_to_del=alert_config)

        # Verify that config is deleted from snmp engine
        # Storage_id is internally modified to remove '-' while deleting
        mock_del_config.assert_called_once_with(trap_receiver_inst.snmp_engine,
                                                'abcd12345678')

    def test_sync_snmp_config_add_invalid_version(self):
        ctxt = {}
        alert_source_config = {'storage_id': 'abcd-1234-5678',
                               'version': 'snmpv4',
                               'community_string': 'public'}
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        self.assertRaisesRegex(exception.InvalidSNMPConfig, "Invalid snmp "
                                                            "version",
                               trap_receiver_inst.sync_snmp_config, ctxt,
                               snmp_config_to_add=alert_source_config)

    @mock.patch('pysnmp.entity.config.addV3User')
    def test_sync_snmp_config_add_v3_version(self, mock_add_config):
        ctxt = {}
        alert_config = fakes.fake_v3_alert_source()
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        trap_receiver_inst.sync_snmp_config(ctxt,
                                            snmp_config_to_add=alert_config)

        # Verify that addV3User to add config to engine
        self.assertTrue(mock_add_config.called)

    @mock.patch('pysnmp.entity.config.delV3User')
    def test_sync_snmp_config_del_v3_version(self, mock_del_config):
        ctxt = {}
        alert_config = fakes.fake_v3_alert_source()
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        trap_receiver_inst.sync_snmp_config(ctxt,
                                            snmp_config_to_add=alert_config)
        trap_receiver_inst.sync_snmp_config(ctxt,
                                            snmp_config_to_del=alert_config)

        # Verify that delV3User to del config from engine
        self.assertTrue(mock_del_config.called)

    def test_sync_snmp_config_invalid_auth_protocol(self):
        ctxt = {}
        alert_source_config = fakes.fake_v3_alert_source()
        alert_source_config['auth_protocol'] = 'invalid_auth'
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        self.assertRaisesRegex(exception.InvalidSNMPConfig, "Invalid "
                                                            "auth_protocol",
                               trap_receiver_inst.sync_snmp_config, ctxt,
                               snmp_config_to_add=alert_source_config)

    def test_sync_snmp_config_invalid_priv_protocol(self):
        ctxt = {}
        alert_source_config = fakes.fake_v3_alert_source()
        alert_source_config['privacy_protocol'] = 'invalid_priv'
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        self.assertRaisesRegex(exception.InvalidSNMPConfig, "Invalid "
                                                            "privacy_protocol",
                               trap_receiver_inst.sync_snmp_config, ctxt,
                               snmp_config_to_add=alert_source_config)

    @mock.patch('pysnmp.entity.config.addV3User')
    @mock.patch('delfin.db.api.alert_source_get_all')
    def test_load_snmp_config(self, mock_alert_source_list, mock_add_config):
        mock_alert_source_list.return_value = fakes.fake_v3_alert_source_list()
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        trap_receiver_inst._load_snmp_config()

        # Verify that config is added to engine
        self.assertTrue(mock_add_config.called)

    @mock.patch('delfin.db.alert_source_get_all')
    def test_get_alert_source_by_host_success(self, mock_alert_source_list):
        # alert_source_config = fakes.fake_v3_alert_source()
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'version': 'snmpv3',
                                 'engine_id': '800000d30300000e112245',
                                 'username': 'test1',
                                 'auth_key': 'YWJjZDEyMzQ1Njc=',
                                 'auth_protocol': 'HMACMD5',
                                 'privacy_key': 'YWJjZDEyMzQ1Njc=',
                                 'privacy_protocol': 'DES'
                                 }
        mock_alert_source_list.return_value = fakes. \
            fake_v3_alert_source_list_with_one()
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        alert_source = trap_receiver_inst. \
            _get_alert_source_by_host('127.0.0.1')
        self.assertDictEqual(expected_alert_source, alert_source)

    @mock.patch('delfin.db.alert_source_get_all')
    def test_get_alert_source_by_host_without_storage(self,
                                                      mock_alert_source_list):
        # alert_source_config = fakes.fake_v3_alert_source()
        mock_alert_source_list.return_value = fakes.null_alert_source_list()
        trap_receiver_inst = self._get_trap_receiver()
        trap_receiver_inst.snmp_engine = engine.SnmpEngine()
        self.assertRaisesRegex(exception.AlertSourceNotFoundWithHost, "",
                               trap_receiver_inst._get_alert_source_by_host,
                               '127.0.0.1')
