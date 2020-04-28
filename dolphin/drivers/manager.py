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
import six
import stevedore

from oslo_log import log
from oslo_utils import uuidutils

from dolphin import utils
from dolphin import coordination
from dolphin import db
# from dolphin import cryptor
from dolphin import exception
from dolphin.i18n import _

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

    @coordination.synchronized('driver-{register_info[vendor]}-'
                               '{register_info[model]}')
    def register_storage(self, context, register_info):
        """Discovery a storage system with access information."""
        # Check same access info from DB
        access_info = copy.deepcopy(register_info)
        vendor, model = access_info.pop('vendor'), access_info.pop('model')
        db_access_info = db.access_info_get_all(context, sort_keys=['host'],
                                                filters=access_info)
        if db_access_info:
            msg = _("Storage device has been registered.")
            raise exception.Conflict(msg)

        # Load and initialize a driver
        # todo: add exception handler
        driver = stevedore.driver.DriverManager(
            namespace=self.NAMESPACE,
            name='%s %s' % (vendor, model),
            invoke_on_load=True
        ).driver

        storage = driver.register_storage(context,
                                          register_info)
        if storage:
            storage_id = six.text_type(uuidutils.generate_uuid())
            access_info['storage_id'] = storage_id
            # todo
            # access_info['password'] = cryptor.encode(
            #     access_info['password'])
            db.access_info_create(context, access_info)

            storage['id'] = storage_id
            storage = db.storage_create(context, storage)

            driver.storage_id = storage_id
            self.driver_factory[storage_id] = driver

        LOG.info("Storage was registered successfully.")
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
