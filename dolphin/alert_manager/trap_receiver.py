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

import re

from oslo_log import log
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c
from pysnmp.smi import builder, view, rfc1902

from dolphin import context, cryptor
from dolphin import exception
from dolphin.alert_manager import alert_processor
from dolphin.alert_manager import constants
from dolphin.db import api as db_api

LOG = log.getLogger(__name__)

# Currently static mib file list is loaded
# Mechanism to be changed to load all mib file
MIB_LOAD_LIST = ['SNMPv2-MIB', 'IF_MIB', 'EMCGATEWAY-MIB', 'FCMGMT-MIB']


class TrapReceiver(object):
    """Trap listening and processing functions"""

    def __init__(self, trap_receiver_address, trap_receiver_port,
                 snmp_mib_path, mib_view_controller=None, snmp_engine=None):
        self.mib_view_controller = mib_view_controller
        self.snmp_engine = snmp_engine
        self.trap_receiver_address = trap_receiver_address
        self.trap_receiver_port = trap_receiver_port
        self.snmp_mib_path = snmp_mib_path

    def sync_snmp_config(self, ctxt, snmp_config_to_del=None,
                         snmp_config_to_add=None):
        if snmp_config_to_del is not None:
            self._delete_snmp_config(ctxt, snmp_config_to_del)

        if snmp_config_to_add is not None:
            self._add_snmp_config(ctxt, snmp_config_to_add)

    def _add_snmp_config(self, ctxt, new_config):
        LOG.info("Add snmp config:%s" % new_config)
        storage_id = new_config["storage_id"]
        version_int = self._get_snmp_version_int(ctxt, new_config["version"])
        if version_int == 1 or version_int == 2:
            community_string = new_config["community_string"]
            community_index = self._get_community_index(storage_id)
            config.addV1System(self.snmp_engine, community_index,
                               community_string, contextName=community_string)
        else:
            username = new_config["username"]
            engine_id = new_config["engine_id"]
            auth_key = new_config.get("auth_key", None)
            auth_protocol = new_config.get("auth_protocol", None)
            privacy_key = new_config.get("privacy_key", None)
            privacy_protocol = new_config.get("privacy_protocol", None)
            if auth_key is not None:
                auth_key = cryptor.decode(auth_key)
            if privacy_key is not None:
                privacy_key = cryptor.decode(privacy_key)
            config.addV3User(
                self.snmp_engine,
                userName=username,
                authKey=auth_key,
                privKey=privacy_key,
                authProtocol=self._get_usm_auth_protocol(ctxt,
                                                         auth_protocol),
                privProtocol=self._get_usm_priv_protocol(ctxt,
                                                         privacy_protocol),
                securityEngineId=v2c.OctetString(hexValue=engine_id))

    def _delete_snmp_config(self, ctxt, snmp_config):
        LOG.info("Delete snmp config:%s" % snmp_config)
        version_int = self._get_snmp_version_int(ctxt, snmp_config["version"])
        if version_int == 3:
            username = snmp_config['username']
            engine_id = snmp_config['engine_id']
            config.delV3User(self.snmp_engine, userName=username,
                             securityEngineId=v2c.OctetString(
                                 hexValue=engine_id))
        else:
            storage_id = snmp_config['storage_id']
            community_index = self._get_community_index(storage_id)
            config.delV1System(self.snmp_engine, community_index)

    def _get_community_index(self, storage_id):
        return storage_id.replace('-', '')

    def _get_snmp_version_int(self, ctxt, version):
        _version = version.lower()
        if _version == "snmpv1":
            version_int = 1
        elif _version == "snmpv2c":
            version_int = 2
        elif _version == "snmpv3":
            version_int = 3
        else:
            msg = "Invalid snmp version %s." % version
            raise exception.InvalidSNMPConfig(detail=msg)

        return version_int

    def _get_usm_auth_protocol(self, ctxt, auth_protocol):
        usm_auth_protocol = config.usmNoAuthProtocol
        if auth_protocol is not None:
            auth_protocol = auth_protocol.lower()
            if auth_protocol == "sha":
                usm_auth_protocol = config.usmHMACSHAAuthProtocol
            elif auth_protocol == "md5":
                usm_auth_protocol = config.usmHMACMD5AuthProtocol
            else:
                msg = "Invalid auth_protocol %s." % auth_protocol
                raise exception.InvalidSNMPConfig(detail=msg)

        return usm_auth_protocol

    def _get_usm_priv_protocol(self, ctxt, privacy_protocol):
        usm_priv_protocol = config.usmNoPrivProtocol
        if privacy_protocol is not None:
            privacy_protocol = privacy_protocol.lower()
            if privacy_protocol == "aes":
                usm_priv_protocol = config.usmAesCfb128Protocol
            elif privacy_protocol == "des":
                usm_priv_protocol = config.usmDESPrivProtocol
            elif privacy_protocol == "3des":
                usm_priv_protocol = config.usm3DESEDEPrivProtocol
            else:
                msg = "Invalid privacy_protocol %s." % privacy_protocol
                raise exception.InvalidSNMPConfig(detail=msg)

        return usm_priv_protocol

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
        except Exception:
            raise ValueError("Mib load failed.")

    def _add_transport(self):
        """Configures the transport parameters for the snmp engine."""
        try:
            config.addTransport(
                self.snmp_engine,
                udp.domainName,
                udp.UdpTransport().openServerMode(
                    (self.trap_receiver_address, int(self.trap_receiver_port)))
            )
        except Exception:
            raise ValueError("Port binding failed: Port is in use.")

    @staticmethod
    def _extract_oid_value(var_bind):
        """Extracts oid and value from var binds.
        ex: varbind = (SNMPv2-MIB::snmpTrapOID.0 = SNMPv2-MIB::coldStart)
        oid = snmpTrapOID
        val = coldStart
        """

        # Separate out oid and value strings
        var_bind_info = var_bind.prettyPrint()
        var_bind_info = var_bind_info.split("=", 1)
        oid = var_bind_info[0]
        val = var_bind_info[1]

        # Extract oid from oid string
        # Example: get snmpTrapOID from SNMPv2-MIB::snmpTrapOID.0
        oid = re.split('[::.]', oid)[2]

        # Value can contain mib name also, if so, extract value from it
        # Ex: get coldStart from SNMPv2-MIB::coldStart
        if "::" in val:
            val = re.split('[::]', val)[2]
        val = val.strip()

        return oid, val

    def _cb_fun(self, state_reference, context_engine_id, context_name,
                var_binds, cb_ctx):
        """Callback function to process the incoming trap."""
        exec_context = self.snmp_engine.observer.getExecutionContext(
            'rfc3412.receiveMessage:request')
        LOG.info('#Notification from %s \n#ContextEngineId: "%s" '
                 '\n#ContextName: ''"%s" \n#SNMPVER "%s" \n#SecurityName "%s" '
                 % (
                     '@'.join(
                         [str(x) for x in exec_context['transportAddress']]),
                     context_engine_id.prettyPrint(),
                     context_name.prettyPrint(), exec_context['securityModel'],
                     exec_context['securityName']))

        var_binds = [rfc1902.ObjectType(
            rfc1902.ObjectIdentity(x[0]),
            x[1]).resolveWithMib(self.mib_view_controller)
            for x in var_binds]
        alert = {}

        for var_bind in var_binds:
            oid, value = self._extract_oid_value(var_bind)
            alert[oid] = value

        # Fill additional info to alert_info
        # transportAddress contains both ip and port, extract ip address
        alert['transport_address'] = exec_context['transportAddress'][0]

        # Handover trap info to alert processor for model
        # translation and export
        try:
            alert_processor.AlertProcessor().process_alert_info(alert)
        except (exception.AccessInfoNotFound,
                exception.StorageNotFound,
                exception.InvalidResults) as e:
            # Log and end the trap processing error flow
            LOG.error(e)
        except Exception as e:
            # Unexpected exception occurred
            LOG.error(e)

    def _load_snmp_config(self):
        """Load snmp config from database when service start."""
        ctxt = context.get_admin_context()
        marker = None
        finish = False
        while not finish:
            alert_sources = db_api.alert_source_get_all(ctxt, marker=marker,
                                                        limit=1000)
            for alert_source in alert_sources:
                snmp_config = dict()
                snmp_config.update(alert_source)
                self._add_snmp_config(ctxt, snmp_config)
                marker = alert_source['storage_id']
            if len(alert_sources) < 1000:
                finish = True

    def start(self):
        """Starts the snmp trap receiver with necessary prerequisites."""
        snmp_engine = engine.SnmpEngine()
        self.snmp_engine = snmp_engine

        try:
            # Load all the mibs and do snmp config
            self._mib_builder()

            self._load_snmp_config()

            # Register callback for notification receiver
            ntfrcv.NotificationReceiver(snmp_engine, self._cb_fun)

            # Add transport info(ip, port) and start the listener
            self._add_transport()

            snmp_engine.transportDispatcher.jobStarted(
                constants.SNMP_DISPATCHER_JOB_ID)
        except Exception as e:
            LOG.error(e)
            raise ValueError("Failed to setup for trap listener.")

        try:
            LOG.info("Starting trap receiver.")
            snmp_engine.transportDispatcher.runDispatcher()
        except Exception:
            snmp_engine.transportDispatcher.closeDispatcher()
            raise ValueError("Failed to start trap listener.")

    def stop(self):
        """Brings down the snmp trap receiver."""
        # Go ahead with shutdown, ignore if any errors happening during the
        # process as it is shutdown
        if self.snmp_engine:
            self.snmp_engine.transportDispatcher.closeDispatcher()
        LOG.info("Trap receiver stopped.")
