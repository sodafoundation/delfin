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
import six
from oslo_config import cfg
from pyasn1.type.univ import OctetString
from pysnmp.entity.rfc3413.oneliner import cmdgen

from delfin import exception
from delfin.common import constants
from delfin.i18n import _

CONF = cfg.CONF


def validate_engine_id(engine_id):
    # Validate engine_id, check octet string can be formed from it
    try:
        OctetString.fromHexString(engine_id)
    except ValueError:
        msg = "engine_id should be a set of octets in " \
              "hexadecimal format."
        raise exception.InvalidInput(msg)


def validate_connectivity(alert_source, plain_auth_key, plain_priv_key):
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

    version = alert_source.get('version')
    error_indication = None

    # Connect to alert source through snmp get to check the configuration
    try:
        if version.lower() == 'snmpv3':
            auth_protocol = None
            privacy_protocol = None
            if alert_source['auth_protocol'] is not None:
                auth_protocol = constants.AUTH_PROTOCOL_MAP.get(
                    alert_source['auth_protocol'].lower())
            if alert_source['privacy_protocol'] is not None:
                privacy_protocol = constants.PRIVACY_PROTOCOL_MAP.get(
                    alert_source['privacy_protocol'].lower())

            error_indication, __, __, __ = cmd_gen.getCmd(
                cmdgen.UsmUserData(alert_source['username'],
                                   authKey=plain_auth_key,
                                   privKey=plain_priv_key,
                                   authProtocol=auth_protocol,
                                   privProtocol=privacy_protocol),
                cmdgen.UdpTransportTarget((alert_source['host'],
                                           alert_source['port']),
                                          timeout=alert_source[
                                              'expiration'],
                                          retries=alert_source[
                                              'retry_num']),
                constants.SNMP_QUERY_OID,
            )
        else:
            error_indication, __, __, __ = cmd_gen.getCmd(
                cmdgen.CommunityData(alert_source['community_string'],
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
        msg = (_("configuration validation failed with alert source for "
                 "reason: %s.") % error_indication)
    except Exception as e:
        msg = (_("configuration validation failed with alert source for "
                 "reason: %s.") % six.text_type(e))

    # Since validation occur error, raise exception
    raise exception.InvalidResults(msg)
