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

update = {
    'type': 'object',
    'properties': {
        'host': parameter_types.hostname_or_ip_address,
        'port': parameter_types.tcp_udp_port,
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'password': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'extra_attributes': {
            'type': 'object',
            'patternProperties': {
                '^[a-zA-Z0-9-_:. ]{1,255}$': {
                    'type': 'string', 'maxLength': 255
                }
            }
        }
    },
    'required': ['username', 'password'],
    'additionalProperties': False
}
