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

from delfin.api.validation import parameter_types

# engineId is in range (5-32) octet which is 10-64 hex characters
# If it is odd length, 0 will be prefixed to last octet, so minimum length is 9
put = {
    'type': 'object',
    'properties': {
        'host': parameter_types.hostname_or_ip_address,
        'version': parameter_types.snmp_version,
        'community_string': {'type': 'string',
                             'minLength': 1,
                             'maxLength': 32},
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 32},
        'security_level': parameter_types.snmp_security_level,
        'auth_key': {'type': 'string', 'minLength': 8, 'maxLength': 65535},
        'auth_protocol': parameter_types.snmp_auth_protocol,
        'privacy_protocol': parameter_types.snmp_privacy_protocol,
        'privacy_key': {'type': 'string', 'minLength': 8, 'maxLength': 65535},
        'engine_id': {'type': 'string', 'minLength': 9, 'maxLength': 64},
        'context_name': {'type': 'string', 'minLength': 0, 'maxLength': 32},
        'retry_num': {'type': 'integer'},
        'expiration': {'type': 'integer'},
        'port': parameter_types.tcp_udp_port
    },
    'required': ['host', 'version'],
    'additionalProperties': False,
}
