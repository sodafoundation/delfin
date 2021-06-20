# Copyright 2021 The SODA Authors.
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


def build_port_groups(port_groups):
    # Build list of port groups
    views = [build_port_group(port_group)
             for port_group in port_groups]
    return dict(port_groups=views)


def build_port_group(port_group):
    view = copy.deepcopy(port_group)
    ports = view['ports']
    view['ports'] = []
    if ports:
        view['ports'] = ports.split(',')
    return dict(view)
