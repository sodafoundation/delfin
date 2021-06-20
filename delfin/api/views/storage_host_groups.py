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


def build_storage_host_groups(storage_host_groups):
    # Build list of storage host groups
    views = [build_storage_host_group(storage_host_group)
             for storage_host_group in storage_host_groups]
    return dict(storage_host_groups=views)


def build_storage_host_group(storage_host_group):
    view = copy.deepcopy(storage_host_group)
    storage_hosts = view['storage_hosts']
    view['storage_hosts'] = []
    if storage_hosts:
        view['storage_hosts'] = storage_hosts.split(',')
    return dict(view)
