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

import six

from oslo_log import log
from oslo_utils import uuidutils

from delfin.drivers import helper
from delfin.drivers import manager

LOG = log.getLogger(__name__)


class API(object):
    def __init__(self):
        self.driver_manager = manager.DriverManager()

    def discover_storage(self, context, access_info):
        """Discover a storage system with access information."""
        if 'storage_id' not in access_info:
            access_info['storage_id'] = six.text_type(
                uuidutils.generate_uuid())

        driver = self.driver_manager.get_driver(context,
                                                cache_on_load=False,
                                                **access_info)
        storage = driver.get_storage(context)

        # Need to validate storage response from driver
        helper.check_storage_repetition(context, storage)
        access_info = helper.create_access_info(context, access_info)
        storage['id'] = access_info['storage_id']
        storage = helper.create_storage(context, storage)
        self.driver_manager.update_driver(storage['id'], driver)

        LOG.info("Storage found successfully.")
        return storage

    def update_access_info(self, context, access_info):
        """Validate and update access information."""
        driver = self.driver_manager.get_driver(context,
                                                cache_on_load=False,
                                                **access_info)
        storage_new = driver.get_storage(context)

        # Need to validate storage response from driver
        storage_id = access_info['storage_id']
        helper.check_storage_consistency(context, storage_id, storage_new)
        access_info = helper.update_access_info(context,
                                                storage_id, access_info)
        helper.update_storage(context, storage_id, storage_new)
        self.driver_manager.update_driver(storage_id, driver)

        LOG.info("Access information updated successfully.")
        return access_info

    def remove_storage(self, context, storage_id):
        """Clear driver instance from driver factory."""
        self.driver_manager.remove_driver(storage_id)

    def get_storage(self, context, storage_id):
        """Get storage device information from storage system"""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.get_storage(context)

    def list_storage_pools(self, context, storage_id):
        """List all storage pools from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_storage_pools(context)

    def list_volumes(self, context, storage_id):
        """List all storage volumes from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_volumes(context)

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def parse_alert(self, context, storage_id, alert):
        """Parse alert data got from snmp trap server."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.parse_alert(context, alert)

    def clear_alert(self, context, storage_id, sequence_number):
        """Clear alert from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.clear_alert(context, sequence_number)

    def list_alerts(self, context, storage_id):
        """List alert from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_alerts(context)
