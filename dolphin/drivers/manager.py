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

DRIVER_MAPPING = {
    "fake_storage": "dolphin.drivers.fake_storage.FakeStorageDriver"
}


class DriverManager(object):

    def __init__(self):
        self.driver_factory = dict()

    @staticmethod
    def get_storage_registry():
        pass

    def register_storage(self, context, register_info):
        pass

    def remove_storage(self, context, storage_info):
        """Needs to clear driver from driver factory"""
        pass

    def get_storage(self, context, storage_info):
        pass

    def list_pools(self, context, storage_info):
        pass

    def list_volumes(self, context, storage_info):
        pass

    def parse_alert(self, context, storage_info, alert):
        pass

    def clear_alert(self, context, storage_info, alert):
        pass
