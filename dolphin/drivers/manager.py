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
import stevedore

from oslo_log import log
from oslo_utils import uuidutils

from dolphin import exception
from dolphin.i18n import _
from dolphin import utils

LOG = log.getLogger(__name__)


class DriverManager(metaclass=utils.Singleton):
    NAMESPACE = 'dolphin.storage.drivers'

    def __init__(self):
        # The driver_factory will keep the driver instance for
        # each of storage systems so that the session between driver
        # and storage system is effectively used.
        self.driver_factory = dict()

    @staticmethod
    def get_storage_registry():
        """Show register parameters which the driver needs."""
        pass

    def register_storage(self, context, access_info):
        """Discovery a storage system with access information."""
        try:
            driver = stevedore.driver.DriverManager(
                namespace=self.NAMESPACE,
                name='%s %s' % (access_info['vendor'],
                                access_info['model']),
                invoke_on_load=True
            ).driver
        except Exception as e:
            msg = (_("Storage driver '%s %s' could not be found.") % (access_info['vendor'],
                                                                      access_info['model']))
            LOG.error(msg)
            raise exception.StorageDriverNotFound(message=msg)

        storage = driver.register_storage(context,
                                          access_info)
        if storage:
            storage['id'] = six.text_type(uuidutils.generate_uuid())
            self.driver_factory[storage['id']] = driver

        LOG.info("Storage was found successfully.")
        return storage

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
        pass

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
