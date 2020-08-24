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

import six
from oslo_log import log
from oslo_service import periodic_task
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c
from pysnmp.smi import builder, view

from delfin import context, cryptor
from delfin import db
from delfin import exception
from delfin import manager
from delfin.alert_manager import alert_processor
from delfin.alert_manager import constants
from delfin.alert_manager import rpcapi
from delfin.alert_manager import snmp_validator
from delfin.common import constants as common_constants
from delfin.db import api as db_api
from delfin.i18n import _

LOG = log.getLogger(__name__)


class TrapReceiver(manager.Manager):
    """Trap listening and processing functions"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        self.mib_view_controller = kwargs.get('mib_view_controller')
        self.snmp_engine = kwargs.get('snmp_engine')
        self.trap_receiver_address = kwargs.get('trap_receiver_address')
        self.trap_receiver_port = kwargs.get('trap_receiver_port')
        self.alert_processor = alert_processor.AlertProcessor()
        self.snmp_validator = snmp_validator.SNMPValidator()
        self.alert_rpc_api = rpcapi.AlertAPI()
        super(TrapReceiver, self).__init__(host=kwargs.get('host'))

    def sync_snmp_config(self, ctxt, snmp_config_to_del=None,
                         snmp_config_to_add=None):
        if snmp_config_to_del:
            self._delete_snmp_config(ctxt, snmp_config_to_del)

        if snmp_config_to_add:
            self.snmp_validator.validate(ctxt, snmp_config_to_add)
            self._add_snmp_config(ctxt, snmp_config_to_add)

    def _add_snmp_config(self, ctxt, new_config):
        LOG.info("Start to add snmp trap config.")
        storage_id = new_config.get("storage_id")
        version_int = self._get_snmp_version_int(ctxt,
                                                 new_config.get("version"))
        if version_int == constants.SNMP_V2_INT or \
                version_int == constants.SNMP_V1_INT:
            community_string = cryptor.decode(
                new_config.get("community_string"))
            community_index = self._get_community_index(storage_id)
            config.addV1System(self.snmp_engine, community_index,
                               community_string, contextName=community_string)
        else:
            username = new_config.get("username")
            engine_id = new_config.get("engine_id")
            if engine_id:
                engine_id = v2c.OctetString(hexValue=engine_id)

            auth_key = new_config.get("auth_key")
            auth_protocol = new_config.get("auth_protocol")
            privacy_key = new_config.get("privacy_key")
            privacy_protocol = new_config.get("privacy_protocol")
            if auth_key:
                auth_key = cryptor.decode(auth_key)
            if privacy_key:
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
                securityEngineId=engine_id)

    def _delete_snmp_config(self, ctxt, snmp_config):
        LOG.info("Start to remove snmp trap config.")
        version_int = self._get_snmp_version_int(ctxt,
                                                 snmp_config.get("version"))
        if version_int == constants.SNMP_V3_INT:
            username = snmp_config.get('username')
            engine_id = snmp_config.get('engine_id')
            if engine_id:
                engine_id = v2c.OctetString(hexValue=engine_id)
            config.delV3User(self.snmp_engine, userName=username,
                             securityEngineId=engine_id)
        else:
            storage_id = snmp_config.get('storage_id')
            community_index = self._get_community_index(storage_id)
            config.delV1System(self.snmp_engine, community_index)

    def _get_community_index(self, storage_id):
        return storage_id.replace('-', '')

    def _get_snmp_version_int(self, ctxt, version):
        _version = version.lower()
        version_int = constants.VALID_SNMP_VERSIONS.get(_version)
        if version_int is None:
            msg = "Invalid snmp version %s." % version
            raise exception.InvalidSNMPConfig(msg)

        return version_int

    def _get_usm_auth_protocol(self, ctxt, auth_protocol):
        if auth_protocol:
            usm_auth_protocol = common_constants.AUTH_PROTOCOL_MAP \
                .get(auth_protocol.lower())
            if usm_auth_protocol:
                return usm_auth_protocol
            else:
                msg = "Invalid auth_protocol %s." % auth_protocol
                raise exception.InvalidSNMPConfig(msg)
        else:
            return config.usmNoAuthProtocol

    def _get_usm_priv_protocol(self, ctxt, privacy_protocol):
        if privacy_protocol:
            usm_priv_protocol = common_constants.PRIVACY_PROTOCOL_MAP.get(
                privacy_protocol.lower())
            if usm_priv_protocol:
                return usm_priv_protocol
            else:
                msg = "Invalid privacy_protocol %s." % privacy_protocol
                raise exception.InvalidSNMPConfig(msg)

        return config.usmNoPrivProtocol

    def _mib_builder(self):
        """Loads given set of mib files from given path."""
        mib_builder = builder.MibBuilder()
        self.mib_view_controller = view.MibViewController(mib_builder)

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
    def _get_alert_source_by_host(source_ip):
        """Gets alert source for given source ip address."""
        filters = {'host': source_ip}
        ctxt = context.RequestContext()

        # Using the known filter and db exceptions are handled by api
        alert_source = db.alert_source_get_all(ctxt, filters=filters)
        if not alert_source:
            raise exception.AlertSourceNotFoundWithHost(source_ip)

        # This is to make sure unique host is configured each alert source
        if len(alert_source) > 1:
            msg = (_("Failed to get unique alert source with host %s.")
                   % source_ip)
            raise exception.InvalidResults(msg)

        return alert_source[0]

    def _cb_fun(self, state_reference, context_engine_id, context_name,
                var_binds, cb_ctx):
        """Callback function to process the incoming trap."""
        exec_context = self.snmp_engine.observer.getExecutionContext(
            'rfc3412.receiveMessage:request')
        LOG.debug("Get notification from: %s" %
                  "#".join([str(x) for x in exec_context['transportAddress']]))
        alert = {}

        try:
            # transportAddress contains both ip and port, extract ip address
            source_ip = exec_context['transportAddress'][0]
            alert_source = self._get_alert_source_by_host(source_ip)

            # In case of non v3 version, community string is used to map the
            # trap. Pysnmp library helps to filter traps whose community string
            # are not configured. But if a given community name x is configured
            # for storage1, if the trap is received with x from storage 2,
            # library will allow the trap. So for non v3 version, we need to
            # verify that community name is configured at alert source db for
            # the storage which is sending traps.
            # context_name contains the incoming community string value
            if exec_context['securityModel'] != constants.SNMP_V3_INT \
                    and cryptor.decode(alert_source['community_string']) \
                    != str(context_name):
                msg = (_("Community string not matching with alert source %s, "
                         "dropping it.") % source_ip)
                raise exception.InvalidResults(msg)

            for oid, val in var_binds:
                # Fill raw oid and values
                oid_str = str(oid)
                alert[oid_str] = str(val)

            # Fill additional info to alert info
            alert['transport_address'] = source_ip
            alert['storage_id'] = alert_source['storage_id']

            # Handover to alert processor for model translation and export
            self.alert_processor.process_alert_info(alert)
        except exception.DelfinException as e:
            # Log and end the trap processing error flow
            err_msg = _("Failed to process alert report (%s).") % e.msg
            LOG.exception(err_msg)
        except Exception as e:
            err_msg = six.text_type(e)
            LOG.exception(err_msg)

    def _load_snmp_config(self):
        """Load snmp config from database when service start."""
        ctxt = context.get_admin_context()
        marker = None
        finished = False
        limit = constants.DEFAULT_LIMIT
        while not finished:
            alert_sources = db_api.alert_source_get_all(ctxt, marker=marker,
                                                        limit=limit)
            for alert_source in alert_sources:
                snmp_config = dict()
                snmp_config.update(alert_source)
                self._add_snmp_config(ctxt, snmp_config)
                marker = alert_source['storage_id']
            if len(alert_sources) < limit:
                finished = True

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

    @periodic_task.periodic_task(spacing=1800, run_immediately=True)
    def heart_beat_task_spawn(self, ctxt):
        """Periodical task to spawn snmp heart beat check."""
        LOG.info("Spawn the snmp heart beat check task.")
        alert_source_list = db.alert_source_get_all(ctxt)
        for alert_source in alert_source_list:
            self.alert_rpc_api.check_snmp_config(ctxt, alert_source)

    def check_snmp_config(self, ctxt, snmp_config):
        LOG.info("Received snmp config checking request for "
                 "storage: %s", snmp_config['storage_id'])
        self.snmp_validator.validate(ctxt, snmp_config)
