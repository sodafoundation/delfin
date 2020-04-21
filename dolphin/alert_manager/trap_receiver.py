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

"""
**trap receiver**
"""
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
    """Trap receiver functions."""

    def __init__(self, trap_receiver_address, trap_receiver_port,
                 snmp_mib_path, mib_view_controller=None, snmp_engine=None):
        self.mib_view_controller = mib_view_controller
        self.snmp_engine = snmp_engine
        self.trap_receiver_address = trap_receiver_address
        self.trap_receiver_port = trap_receiver_port
        self.snmp_mib_path = snmp_mib_path

    # Loads the list of mib files provided
    def _mib_builder(self):
        mib_builder = builder.MibBuilder()
        try:
            self.mib_view_controller = view.MibViewController(mib_builder)

            # set mib path to mib_builder object and load mibs
            mib_path = builder.DirMibSource(self.snmp_mib_path),
            mib_builder.setMibSources(*mib_path)
            mib_list = MIB_LOAD_LIST
            if len(mib_list) > 0:
                mib_builder.loadModules_new(*mib_list)

        except error.MibNotFoundError:
            LOG.exception("Mib load failed")

    # Configures the transport parameters for the snmp engine
    def _add_transport(self):
        try:
            config.addTransport(
                self.snmp_engine,
                udp.domainName,
                udp.UdpTransport().openServerMode((self.trap_receiver_address, int(self.trap_receiver_port)))
            )
        except Exception:
            LOG.exception("Port binding failed the provided port is in use")

    # Callback function to process the incoming trap
    def _cbFun(self, state_reference, context_engine_id, context_name,
              var_binds, cb_ctx):
        execContext = self.snmp_engine.observer.getExecutionContext('rfc3412.receiveMessage:request')
        LOG.info(
            '#Notification from %s \n#ContextEngineId: "%s" \n#ContextName: "%s" \n#SNMPVER "%s" \n#SecurityName "%s"' % (
            '@'.join([str(x) for x in execContext['transportAddress']]), context_engine_id.prettyPrint(),
            context_name.prettyPrint(), execContext['securityModel'], execContext['securityName']))
        for oid, val in var_binds:
            output = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolveWithMib(
                self.mib_view_controller).prettyPrint()
            LOG.info(output)

    # Configures snmp v2 and v3 user parameters
    def _snmp_v2v3_config(self):
        community_str = constants.SNMP_COMMUNITY_STR
        config.addV1System(self.snmp_engine, community_str, community_str)
        __authProtocol = {
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
            authProtocol=__authProtocol.get(
                constants.SNMP_V3_AUTH_PROTOCOL, config.usmNoAuthProtocol),
            privProtocol=__authProtocol.get(
                constants.SNMP_V3_PRIV_PROTOCOL, config.usmNoPrivProtocol),
            securityEngineId=v2c.OctetString(
                hexValue=constants.SNMP_ENGINE_ID))

        return

    # Triggers the snmp trap receiver
    def start_trap_receiver(self):
        snmp_engine = engine.SnmpEngine()
        self.snmp_engine = snmp_engine

        # Load all the mibs and do snmp config
        self._mib_builder()

        self._snmp_v2v3_config()

        # Register callback for notification receiver
        ntfrcv.NotificationReceiver(snmp_engine, self._cbFun)

        # Add transport info(ip, port) and start the listener
        self._add_transport()

        snmp_engine.transportDispatcher.jobStarted(constants.SNMP_DISPATCHER_JOB_ID)
        try:
            LOG.info("Trap Listener started .....")
            snmp_engine.transportDispatcher.runDispatcher()
        except Exception as e:
            snmp_engine.transportDispatcher.closeDispatcher()

    # Stops the snmp trap receiver
    def stop_trap_receiver(self):
        if self.snmp_engine:
            self.snmp_engine.transportDispatcher.closeDispatcher()
        LOG.info("Trap Listener stopped .....")