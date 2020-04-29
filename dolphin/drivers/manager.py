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
        # The driver_factory will keep the driver instance for
        # each of storage systems so that the session between driver
        # and storage system is effectively used.
        self.driver_factory = dict()

    @staticmethod
    def get_storage_registry():
        """Show register parameters which the driver needs."""
        pass

    def register_storage(self, context, register_info):
        """Discovery a storage system with register parameters."""
        pass

    def remove_storage(self, context, storage_id):
        """Clear driver instance from driver factory."""
        self.driver_factory.pop(storage_id, None)

    def get_storage(self, context, storage_id):
        """Get storage device information from storage system"""
        pass

    def list_pools(self, context, storage_id):
        """List all storage pools from storage system."""
        pass

    def list_volumes(self, context, storage_id):
        """List all storage volumes from storage system."""
        pass

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def parse_alert(self, context, storage_id, alert):
        """Parse alert data got from snmp trap server."""
        # TBD: Identify driver and driver instance and invoke parse_alert
        pass

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
