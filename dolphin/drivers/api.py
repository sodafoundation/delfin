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

from dolphin.drivers import manager

LOG = log.getLogger(__name__)


class API(object):
    def __init__(self):
        self.driver_manager = manager.DriverManager()

    def register_storage(self, context, access_info):
        """Discovery a storage system with access information."""
        access_info['storage_id'] = six.text_type(uuidutils.generate_uuid())
        driver = self.driver_manager.get_driver(context, **access_info)

        storage = driver.register_storage(context, access_info)
        if storage:
            storage['id'] = six.text_type(access_info['storage_id'])
        else:
            self.driver_manager.remove_driver(context, access_info['storage_id'])

        LOG.info("Storage was found successfully.")
        return storage

    def remove_storage(self, context, storage_id):
        """Clear driver instance from driver factory."""
        driver = self.driver_manager.get_driver()
        driver.remove_driver(context, storage_id)

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
        driver = self.driver_manager.get_driver(context, **{'storage_id': storage_id})
        driver.parse_alert(context, alert)

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
