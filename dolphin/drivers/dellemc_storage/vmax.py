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

import PyU4V
from PyU4V import U4VConn

from oslo_log import log
from dolphin.drivers import driver
from dolphin import exception

SUPPORTED_VERSION='90'

LOG = log.getLogger(__name__)

class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, storage_id=None):
        super().__init__(storage_id)
        # Initialize with defaults
        self.storage_id = storage_id
        self.conn = None
        self.symmetrix_id = None

    def __del__(self):
        # De-initialize session
        self.close_session()

    @staticmethod
    def get_storage_registry():
        required_register_attributes = super.get_storage_registry()
        extra_attributes = {
            'array_id': "The storage id in unisphere system.",
        }
        required_register_attributes['extra_attributes'] = extra_attributes

        return  required_register_attributes

    def register_storage(self, context, access_info):
        """ Connect to storage backend and register using access_info.
        """

        array_id = access_info.get('extra_attributes', {}).\
                                get('array_id', None)
        if not array_id:
            raise exception.InvalidInput(reason='Invalid array_id')

        try:
            # Initialise PyU4V connection to Unisphere
            self.conn = PyU4V.U4VConn(
                u4v_version=SUPPORTED_VERSION,
                server_ip=access_info['host'],
                port=access_info['port'],
                verify=False,
                array_id=array_id,
                username=access_info['username'],
                password=access_info['password'])

        except Exception as err:
            LOG.error("Failed to connect to Unisphere: {}".format(err))
            self.conn = None
            raise

        try:
            # Get the Unisphere version
            version = self.conn.common.get_uni_version()

        except Exception as err:
            LOG.error("Failed to get version from vmax: {}".format(err))
            raise

        # Get storage details
        self.symmetrix_id = array_id
        return self.get_storage(context)

    def get_storage(self, context):

        status = "Error"
        model_symmetrix = ""
        total_cap = 0
        used_cap = 0

        try:
            # Initialise PyU4V connection to Unisphere
            status = "Available"

            # Get the Unisphere model
            uri = "/system/symmetrix/" + self.symmetrix_id
            model = self.conn.common.get_request(uri, "")
            model_symmetrix = model['symmetrix'][0]['model']
            LOG.info("Successfully retrieved storage model")

            # Get Storage details for capacity info
            uri = "/" + SUPPORTED_VERSION + "/sloprovisioning/symmetrix/" + self.symmetrix_id
            storg_info = self.conn.common.get_request(uri, "")
            total_cap = storg_info['system_capacity']['usable_total_tb']
            used_cap = storg_info['system_capacity']['usable_used_tb']
            LOG.info("Successfully retrieved storage capacity")

        except Exception as err:
            LOG.error("Failed to get storage details: {}".format(err))
            raise

        tera_bytes = 1000 * 1000 * 1000 * 1000          # Rounded TB to bytes 1024 * 1024 * 1024 * 1024
        storage = {
            'id': self.storage_id,
            'name': '',
            'vendor': 'Dell EMC',
            'description': '',
            'model': model_symmetrix,
            'status': status,
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
