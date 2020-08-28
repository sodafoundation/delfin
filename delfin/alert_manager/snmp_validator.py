# Copyright 2020 The SODA Authors.
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
import binascii
from datetime import datetime

import six
from oslo_config import cfg
from oslo_log import log
from pyasn1.type.univ import OctetString
from pysnmp.entity.rfc3413.oneliner import cmdgen

from delfin import cryptor
from delfin import db
from delfin import exception
from delfin.common import constants
from delfin.exporter import base_exporter

CONF = cfg.CONF

LOG = log.getLogger(__name__)


class SNMPValidator(object):
    def __init__(self):
        self.exporter = base_exporter.AlertExporterManager()
        self.snmp_error_flag = {}

    def validate(self, ctxt, alert_source):
        alert_source = dict(alert_source)
        engine_id = alert_source.get('engine_id')
        try:
            alert_source = self.validate_connectivity(alert_source)

            # If protocol is snmpv3, the snmp_validator will update
            # engine id if engine id is empty. Therefore, engine id
            # should be saved in database.
            if not engine_id and alert_source.get('engine_id'):

                alert_source_dict = {
                    'engine_id': alert_source.get('engine_id')}
                db.alert_source_update(ctxt,
                                       alert_source.get('storage_id'),
                                       alert_source_dict)
            self._handle_validation_result(ctxt,
                                           alert_source.get('storage_id'),
                                           constants.Category.RECOVERY)
        except exception.SNMPConnectionFailed:
            self._handle_validation_result(ctxt,
                                           alert_source.get('storage_id'))
        except Exception as e:
            msg = six.text_type(e)
            LOG.error("Failed to check snmp config. Reason: %s", msg)

    @staticmethod
    def validate_connectivity(alert_source):
        # Fill optional parameters with default values if not set in input
        if not alert_source.get('port'):
            alert_source['port'] = constants.DEFAULT_SNMP_CONNECT_PORT

        if not alert_source.get('context_name'):
            alert_source['context_name'] = None

        if not alert_source.get('retry_num'):
            alert_source['retry_num'] = constants.DEFAULT_SNMP_RETRY_NUM

        if not alert_source.get('expiration'):
            alert_source['expiration'] = constants.DEFAULT_SNMP_EXPIRATION_TIME

        if CONF.snmp_validation_enabled is False:
            return alert_source

        cmd_gen = cmdgen.CommandGenerator()

        # Register engine observer to get engineId,
        # Code reference from: http://snmplabs.com/pysnmp/
        observer_context = {}
        cmd_gen.snmpEngine.observer.registerObserver(
            lambda e, p, v, c: c.update(
                securityEngineId=v['securityEngineId']),
            'rfc3412.prepareDataElements:internal',
            cbCtx=observer_context
        )

        version = alert_source.get('version')

        # Connect to alert source through snmp get to check the configuration
        try:
            if version.lower() == 'snmpv3':
                auth_key = cryptor.decode(alert_source['auth_key'])
                privacy_key = cryptor.decode(alert_source['privacy_key'])
                auth_protocol = None
                privacy_protocol = None
                if alert_source['auth_protocol']:
                    auth_protocol = constants.AUTH_PROTOCOL_MAP.get(
                        alert_source['auth_protocol'].lower())
                if alert_source['privacy_protocol']:
                    privacy_protocol = constants.PRIVACY_PROTOCOL_MAP.get(
                        alert_source['privacy_protocol'].lower())

                engine_id = alert_source.get('engine_id')
                if engine_id:
                    engine_id = OctetString.fromHexString(engine_id)
                error_indication, __, __, __ = cmd_gen.getCmd(
                    cmdgen.UsmUserData(alert_source['username'],
                                       authKey=auth_key,
                                       privKey=privacy_key,
                                       authProtocol=auth_protocol,
                                       privProtocol=privacy_protocol,
                                       securityEngineId=engine_id),
                    cmdgen.UdpTransportTarget((alert_source['host'],
                                               alert_source['port']),
                                              timeout=alert_source[
                                                  'expiration'],
                                              retries=alert_source[
                                                  'retry_num']),
                    constants.SNMP_QUERY_OID,
                )

                if 'securityEngineId' in observer_context:
                    engine_id = observer_context.get('securityEngineId')
                    alert_source['engine_id'] = binascii.hexlify(
                        engine_id.asOctets()).decode()
            else:
                community_string = cryptor.decode(
                    alert_source['community_string'])
                error_indication, __, __, __ = cmd_gen.getCmd(
                    cmdgen.CommunityData(
                        community_string,
                        contextName=alert_source['context_name']),
                    cmdgen.UdpTransportTarget((alert_source['host'],
                                               alert_source['port']),
                                              timeout=alert_source[
                                                  'expiration'],
                                              retries=alert_source[
                                                  'retry_num']),
                    constants.SNMP_QUERY_OID,
                )

            if not error_indication:
                return alert_source

            # Prepare exception with error_indication
            msg = six.text_type(error_indication)
        except Exception as e:
            msg = six.text_type(e)

        # Since validation occur error, raise exception
        LOG.error("Configuration validation failed with alert source for "
                  "reason: %s." % msg)
        raise exception.SNMPConnectionFailed(msg)

    def _handle_validation_result(self, ctxt, storage_id,
                                  category=constants.Category.FAULT):
        try:
            storage = db.storage_get(ctxt, storage_id)
            serial_number = storage.get('serial_number')
            if category == constants.Category.FAULT:
                self.snmp_error_flag[serial_number] = True
                self._dispatch_snmp_validation_alert(ctxt, storage, category)
            elif self.snmp_error_flag.get(serial_number, True):
                self.snmp_error_flag[serial_number] = False
                self._dispatch_snmp_validation_alert(ctxt, storage, category)
        except Exception as e:
            msg = six.text_type(e)
            LOG.error("Exception occurred when handling validation "
                      "error: %s ." % msg)

    def _dispatch_snmp_validation_alert(self, ctxt, storage, category):

        alert = {
            'storage_id': storage['id'],
            'storage_name': storage['name'],
            'vendor': storage['vendor'],
            'model': storage['model'],
            'serial_number': storage['serial_number'],
            'alert_id': constants.SNMP_CONNECTION_FAILED_ALERT_ID,
            'sequence_number': 0,
            'alert_name': 'SNMP connect failed',
            'category': category,
            'severity': constants.Severity.MAJOR,
            'type': constants.EventType.COMMUNICATIONS_ALARM,
            'location': 'NetworkEntity=%s' % storage['name'],
            'description': "SNMP connection to the storage failed. "
                           "SNMP traps from storage will not be received.",
            'recovery_advice': "1. The network connection is abnormal. "
                               "2. SNMP authentication parameters "
                               "are invalid.",
            'occur_time': int(datetime.utcnow().timestamp()) * 1000,
        }
        self.exporter.dispatch(ctxt, alert)
