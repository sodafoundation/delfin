# Copyright (c) 2014 NetApp Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""

**trap receiver**

"""
from oslo_log import log

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c
from pysnmp.smi import builder, view, rfc1902, error

from dolphin import manager
from dolphin.alert_manager import constants

LOG = log.getLogger(__name__)

#Currently one mib file is loaded, All files to be loaded
LOAD_MIB_MODULE = 'SNMPv2-MIB'

class TrapReceiver(manager.Manager):
    """Trap receiver functions"""

    def __init__(self,receiverIpAddr=None, *args, **kwargs):
        super(TrapReceiver, self).__init__(*args, **kwargs)

    def _mib_builder(self, load_mibs_list):
        mibBuilder = builder.MibBuilder()
        try:
            global mibViewController
            mibViewController = view.MibViewController(mibBuilder)
            if load_mibs_list:
                _mibs = LOAD_MIB_MODULE.split(",")
                mibBuilder.loadModules(*_mibs)
        except error.MibNotFoundError as excep:
            LOG.info(" {} Mib Not Found!".format(excep))

    def _add_transport(self):
        """
        :return:
        """
        try:
            config.addTransport(
                self.snmpEngine,
                udp.domainName,
                udp.UdpTransport().openServerMode((constants.DEF_TRAP_RECV_ADDR, int(constants.DEF_TRAP_RECV_PORT)))
            )
        except Exception as e:
            LOG.info("{} Port Binding Failed the Provided Port {} is in Use".format(e, self.receiverPort))

    def _cbFun(self, stateReference, contextEngineId, contextName,
              varBinds, cbCtx):
        global mibViewController
        LOG.info("####################### NEW Notification #######################")
        execContext = self.snmpEngine.observer.getExecutionContext('rfc3412.receiveMessage:request')
        LOG.info(
            '#Notification from %s \n#ContextEngineId: "%s" \n#ContextName: "%s" \n#SNMPVER "%s" \n#SecurityName "%s"' % (
            '@'.join([str(x) for x in execContext['transportAddress']]), contextEngineId.prettyPrint(),
            contextName.prettyPrint(), execContext['securityModel'], execContext['securityName']))
        for oid, val in varBinds:
            output = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolveWithMib(
                mibViewController).prettyPrint()
            LOG.info(output)

    def _configure_snmp_userpara(self):
        """
        :return:
        """

        COMMUNITYSTRING = constants.SNMP_COMMUNITY_STR
        config.addV1System(self.snmpEngine, COMMUNITYSTRING, COMMUNITYSTRING)
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
            self.snmpEngine, userName=constants.SNMP_USM_USER,
            authKey=constants.SNMP_V3_AUTHKEY, privKey=constants.SNMP_V3_PRIVKEY,
            authProtocol=__authProtocol.get(
                constants.SNMP_V3_AUTH_PROTOCOL, config.usmNoAuthProtocol),
            privProtocol=__authProtocol.get(
                constants.SNMP_V3_PRIV_PROTOCOL, config.usmNoPrivProtocol),
            securityEngineId=v2c.OctetString(
                hexValue=constants.SNMP_ENGINE_ID))

        return

    def start_trap_receiver(self):
        snmpEngine = engine.SnmpEngine()
        self.snmpEngine = snmpEngine

        # Load all the mibs
        self._mib_builder(LOAD_MIB_MODULE)

        self._configure_snmp_userpara()

        # Register callback for notification receiver
        ntfrcv.NotificationReceiver(snmpEngine, self._cbFun)

        # Add transport info(ip, port) and start the listener
        self._add_transport()

        snmpEngine.transportDispatcher.jobStarted(1)
        try:
            LOG.info("Trap Listener started .....")
            snmpEngine.transportDispatcher.runDispatcher()
        except:
            snmpEngine.transportDispatcher.closeDispatcher()
            raise

    def stop_trap_receiver(self):
        if self.snmpEngine:
            self.snmpEngine.transportDispatcher.closeDispatcher()
        LOG.info("Trap Listener stopped .....")