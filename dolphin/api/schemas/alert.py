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

from dolphin.api.validation import parameter_types


update = {
    'type': 'object',
    'properties': {
        'host': parameter_types.hostname_or_ip_address,
        'version': parameter_types.snmp_version,
        'community_string': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'password': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'auth_enable': parameter_types.boolean,
        'auth_protocol': parameter_types.snmp_auth_protocol,
        'encryption_enable': parameter_types.boolean,
        'encryption_protocol': parameter_types.snmp_encryption_protocol,
        'encryption_password': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'engine_id': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['host', 'version'],
    'additionalProperties': False,
}

