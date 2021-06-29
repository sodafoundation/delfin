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


def build_storage_hosts(storage_hosts):
    # Build list of storage hosts
    views = [build_storage_host(storage_host)
             for storage_host in storage_hosts]
    return dict(storage_hosts=views)


def build_storage_host(storage_host):
    view = copy.deepcopy(storage_host)
    return dict(view)
