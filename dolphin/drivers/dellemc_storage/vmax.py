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
from dolphin.drivers import driver
from dolphin.drivers import helper
from dolphin.drivers.dellemc_storage import client
from dolphin import exception

LOG = log.getLogger(__name__)

class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_vmax(kwargs)

    def __del__(self):
        # De-initialize session
        self.close_session()

    def _init_vmax(self, access_info):
        self.conn = client.get_connection(access_info)

        # Get the Unisphere version to check connection
        version = client.get_version(self.conn)

        # Get storage details
        self.symmetrix_id = access_info.get('extra_attributes', {}).\
                                get('array_id', None)

    def _check_connection(self):
        if not self.storage_id:
            raise exception.InvalidDriverMode(driver_mode='Driver is not initialized')

        if not self.conn:
            access_info = helper.get_access_info(self.storage_id)
            self._init_vmax(access_info)

    @staticmethod
    def get_storage_registry():
        required_register_attributes = super.get_storage_registry()
        extra_attributes = {
            'array_id': "The storage id in unisphere system.",
        }
        required_register_attributes['extra_attributes'] = extra_attributes

        return  required_register_attributes

    def register_storage(self, context):
        """ Connect to storage backend and register.
        """
        return self.get_storage(context)

    def get_storage(self, context):

        self._check_connection()
        # Get the Unisphere model
        model = client.get_model(self.conn, self.symmetrix_id)

        # Get Storage details for capacity info
        storg_info = client.get_storage_capacity(self.conn, self.symmetrix_id)
        total_cap = storg_info['usable_total_tb']
        used_cap = storg_info['usable_used_tb']

        tera_bytes = 1000 * 1000 * 1000 * 1000          # Rounded TB to bytes 1024 * 1024 * 1024 * 1024
        storage = {
            'id': self.storage_id,
            'name': '',
            'vendor': 'Dell EMC',
            'description': '',
            'model': model,
            'status': 'Available',
            'serial_number': self.symmetrix_id,
            'location': '',
            'total_capacity': int(total_cap * tera_bytes),
            'used_capacity': int(used_cap * tera_bytes),
            'free_capacity': int((total_cap - used_cap) * tera_bytes)
        }
        LOG.info("get_storage(), successfully retrieved storage details")
        return storage

    def list_pools(self, context):
        pass

    def list_volumes(self, context):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        pass

    def clear_alert(self, context, alert):
        pass

    def close_session(self):
        if self.conn:
            self.conn.close_session()
            self.conn = None
