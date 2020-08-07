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

from pyasn1.type.univ import OctetString
from pysnmp.entity import config
from pysnmp.entity.rfc3413.oneliner import cmdgen

from delfin import exception
from delfin.common import constants
from delfin.i18n import _

AUTH_PROTOCOL_MAP = {"sha": config.usmHMACSHAAuthProtocol,
                     "md5": config.usmHMACMD5AuthProtocol,
                     "none": "None"}

PRIVACY_PROTOCOL_MAP = {"aes": config.usmAesCfb128Protocol,
                        "des": config.usmDESPrivProtocol,
                        "3des": config.usm3DESEDEPrivProtocol,
                        "none": "None"}


def validate_engine_id(engine_id):
    # Validates the engine_id format
    try:
        OctetString.fromHexString(engine_id)
    except ValueError:
        msg = "engine_id should be a set of octets in " \
              "hexadecimal format."
        raise exception.InvalidInput(msg)


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

    version = alert_source.get('version')

    if version.lower() == 'snmpv3':
        cmd_gen = cmdgen.CommandGenerator(
            snmpEngine=OctetString(hexValue=alert_source['engine_id']))
        auth_protocol = alert_source['auth_protocol']
        auth_protocol = AUTH_PROTOCOL_MAP.get(auth_protocol.lower())
        privacy_protocol = alert_source['privacy_protocol']
        privacy_protocol = PRIVACY_PROTOCOL_MAP.get(privacy_protocol.lower())
        security_model = cmdgen.UsmUserData(alert_source['username'],
                                            authKey=alert_source[
                                                'auth_key'],
                                            privKey=alert_source[
                                                'privacy_key'],
                                            authProtocol=auth_protocol,
                                            privProtocol=privacy_protocol),
    else:
        cmd_gen = cmdgen.CommandGenerator()
        security_model = cmdgen.CommunityData(
            alert_source['community_string'],
            contextName=alert_source['context_name'])

    error_indication, __, __, __ = cmd_gen.getCmd(
        security_model,
        cmdgen.UdpTransportTarget((alert_source['host'],
                                   alert_source['port']),
                                  timeout=alert_source['expiration'],
                                  retries=alert_source['retry_num']),
        constants.SNMP_QUERY_OID,
    )

    if error_indication:
        msg = (_("configuration validation failed with alert source for "
                 "reason: %s.") % error_indication)
        raise exception.InvalidResults(msg)

    return alert_source
