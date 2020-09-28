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
import copy
from delfin import cryptor


def build_alert_source(value):
    view = copy.deepcopy(value)
    view.pop("auth_key")
    view.pop("privacy_key")
    version = view['version']
    if version.lower() == 'snmpv2c':
        view['community_string'] = cryptor.decode(view['community_string'])
        # Remove the key not belong to snmpv2c
        view.pop('username')
        view.pop('security_level')
        view.pop('auth_protocol')
        view.pop('privacy_protocol')
        view.pop('engine_id')
        view.pop('context_name')
    elif version.lower() == 'snmpv3':
        # Remove the key not belong to snmpv3
        view.pop('community_string')
    return dict(view)
