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

from oslo_log import log

LOG = log.getLogger(__name__)


class StoragePoolTask:
    def __init__(self, context, storage_id):
        self.storage_id = storage_id
        self.context = context

    def sync(self):
        LOG.info('Pool sync func...')
        # TODO:
        # 1. call the driver.list_storage_pools(context)
        # 2. update the list_storage_pools info to DB
        pass

    def remove(self):
        pass


class StorageVolumeTask:
    def __init__(self, context, storage_id):
        self.storage_id = storage_id
        self.context = context

    def sync(self):
        LOG.info('Volume sync func...')
        # TODO:
        # 1. call the driver.list_volumes(context)
        # 2. update the list_storage_pools info to DB
        pass

    def remove(self):
        pass
