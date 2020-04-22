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

from oslo_log import log

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c
from pysnmp.smi import builder, view, rfc1902, error

from dolphin.alert_manager import constants

LOG = log.getLogger(__name__)

# Currently static mib file list is loaded, logic to be changed to load all mib file
MIB_LOAD_LIST = ['SNMPv2-MIB','IF_MIB']

class TrapReceiver(object):
    """Trap listening and processing functions"""

    def __init__(self, trap_receiver_address, trap_receiver_port,
                 snmp_mib_path, mib_view_controller=None, snmp_engine=None):
        self.mib_view_controller = mib_view_controller
        self.snmp_engine = snmp_engine
        self.trap_receiver_address = trap_receiver_address
        self.trap_receiver_port = trap_receiver_port
        self.snmp_mib_path = snmp_mib_path

    def _mib_builder(self):
        """Loads given set of mib files from given path."""
        mib_builder = builder.MibBuilder()
        try:
            self.mib_view_controller = view.MibViewController(mib_builder)

            # set mib path to mib_builder object and load mibs
            mib_path = builder.DirMibSource(self.snmp_mib_path),
            mib_builder.setMibSources(*mib_path)
            if len(MIB_LOAD_LIST) > 0:
                mib_builder.loadModules(*MIB_LOAD_LIST)
        except error.MibNotFoundError:
            LOG.error("Mib load failed.")

    def _add_transport(self):
        """Configures the transport parameters for the snmp engine."""
        try:
            config.addTransport(
                self.snmp_engine,
                udp.domainName,
                udp.UdpTransport().openServerMode((self.trap_receiver_address, int(self.trap_receiver_port)))
            )
        except Exception:
            LOG.error("Port binding failed the provided port is in use.")

    def _cb_fun(self, state_reference, context_engine_id, context_name,
              var_binds, cb_ctx):
        """Callback function to process the incoming trap."""
        exec_context = self.snmp_engine.observer.getExecutionContext('rfc3412.receiveMessage:request')
        LOG.info(
            '#Notification from %s \n#ContextEngineId: "%s" \n#ContextName: "%s" \n#SNMPVER "%s" \n#SecurityName "%s"' % (
            '@'.join([str(x) for x in exec_context['transportAddress']]), context_engine_id.prettyPrint(),
            context_name.prettyPrint(), exec_context['securityModel'], exec_context['securityName']))
        for oid, val in var_binds:
            output = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolveWithMib(
                self.mib_view_controller).prettyPrint()
            LOG.info(output)

    def _snmp_v2v3_config(self):
        """Configures snmp v2 and v3 user parameters."""
        community_str = constants.SNMP_COMMUNITY_STR
        config.addV1System(self.snmp_engine, community_str, community_str)
        auth_priv_protocols = {
            'usmHMACMD5AuthProtocol': config.usmHMACMD5AuthProtocol,
            'usmHMACSHAAuthProtocol': config.usmHMACSHAAuthProtocol,
            'usmAesCfb128Protocol': config.usmAesCfb128Protocol,
            'usmAesCfb256Protocol': config.usmAesCfb256Protocol,
            'usmAesCfb192Protocol': config.usmAesCfb192Protocol,
            'usmDESPrivProtocol': config.usmDESPrivProtocol,
            'usmNoAuthProtocol': config.usmNoAuthProtocol,
            'usmNoPrivProtocol': config.usmNoPrivProtocol
        }
        config.addV3User(
            self.snmp_engine, userName=constants.SNMP_USM_USER,
            authKey=constants.SNMP_V3_AUTHKEY, privKey=constants.SNMP_V3_PRIVKEY,
            authProtocol=auth_priv_protocols.get(
                constants.SNMP_V3_AUTH_PROTOCOL, config.usmNoAuthProtocol),
            privProtocol=auth_priv_protocols.get(
                constants.SNMP_V3_PRIV_PROTOCOL, config.usmNoPrivProtocol),
            securityEngineId=v2c.OctetString(
                hexValue=constants.SNMP_ENGINE_ID))

        return

    def start(self):
        """Starts the snmp trap receiver with necessary prerequisites."""
        snmp_engine = engine.SnmpEngine()
        self.snmp_engine = snmp_engine

        # Load all the mibs and do snmp config
        self._mib_builder()

        self._snmp_v2v3_config()

        # Register callback for notification receiver
        ntfrcv.NotificationReceiver(snmp_engine, self._cb_fun)

        # Add transport info(ip, port) and start the listener
        self._add_transport()

        snmp_engine.transportDispatcher.jobStarted(constants.SNMP_DISPATCHER_JOB_ID)
        try:
            LOG.info("Starting trap receiver.")
            snmp_engine.transportDispatcher.runDispatcher()

        except Exception:
            LOG.error("Failed to start trap listener.")
            snmp_engine.transportDispatcher.closeDispatcher()

    def stop(self):
        """Brings down the snmp trap receiver."""
        # Go ahead with shutdown, ignore if any errors happening during the process as it is shutdown
        if self.snmp_engine:
            self.snmp_engine.transportDispatcher.closeDispatcher()
        LOG.info("Trap receiver stopped.")
