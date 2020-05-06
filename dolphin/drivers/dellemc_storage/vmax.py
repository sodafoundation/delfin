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

SUPPORTED_VERSION='90'

LOG = log.getLogger(__name__)

class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, storage_id=None):
        super().__init__(storage_id)
        # Initialize with defaults
        self.storage_id = storage_id
        self.univmax_version = SUPPORTED_VERSION
        self.server_ip = ''
        self.port = ''
        self.verify = False  # Valid values are True/False/<path to certificatefile>
        self.username = ''
        self.password = ''
        self.symmetrix_id = ''

    @staticmethod
    def get_storage_registry():
        # register_info dict
        extra_attributes = {
            'univmax_ver': self.univmax_version,
            'array_id': self.symmetrix_id,
            'verify': self.verify
        }
        access_info = {
            'storage_id':self.storage_id,
            'username':'',
            'password':'',
            'host':self.server_ip,
            'port':self.port,
            'extra_attributes': extra_attributes
        }
        LOG.info("get_storage_registry(), success")
        return access_info

    def register_storage(self, context, access_info):
        """ Connect to storage backend and register using access_info.

        Typical content of the access_info for connecting/registering to VMAX

        access_info = {
            "storage_id": "",           # Not used in this function
            "host": "127.0.0.1",        # IP Address of VMAX Storage
            "port": "8443",             # PORT of VMAX Storage
            "username": "user",         # Username for VMAX Storage
            "password": "pass",         # Username for VMAX Storage
            "extra_attributes" = {
                "array_id": "00012345", # Array ID
                "univmax_ver": "90",    # Version of Unishare of VMAX
                "verify": False         # True/False/Key file path for SSL verify
            }
        }
        """

        # Verify input parameters for registration exists
        try:
            self.username = access_info['username']
            self.password = access_info['password']
            self.server_ip = access_info['host']
            self.port = access_info['port']

        except KeyError as err:
            LOG.error("Invalid input access_info[" + str(err) + "]")
            return None

        try:
            # Get optional inputs
            if 'extra_attributes' in access_info:
                extra_attr = access_info['extra_attributes']

                if 'verify' in extra_attr:
                    self.verify = extra_attr['verify']
                if 'univmax_ver' in extra_attr:
                    self.univmax_version = extra_attr['univmax_ver']
                if 'array_id' in extra_attr:
                    self.symmetrix_id = extra_attr['array_id']

        except KeyError as err:
            LOG.info("Invalid input access_info[" + str(err) + "]")

        description = 'Unispere array with version '
        try:
            # Initialise PyU4V connection to Unisphere
            conn = PyU4V.U4VConn(
                u4v_version=self.univmax_version,
                server_ip=self.server_ip,
                port=self.port,
                verify=False,
                username=self.username,
                password=self.password)

            # Get the Unisphere version
            version = conn.common.get_uni_version()
            description = description + version[0]

            if self.symmetrix_id == "":
                # Retrieve a list of arrays managed by Unisphere
                array_list = conn.common.get_array_list()

                if len(array_list) == 0:
                    LOG.error("Array list from Storage backend is empty")
                    conn.close_session()
                    return None

                if len(array_list) > 1:
                    LOG.info("More than one Storage Array, first one selected")

                self.symmetrix_id = array_list[0]

            # Close the session
            conn.close_session()

        except:
            LOG.error("Failed to connect to VMAX storage")
            return None

        # Get storage details
        storage = self.get_storage(context)
        if storage:
            storage['description'] = description
            storage['serial_number'] = self.symmetrix_id

        # Return all the storage ids this driver manage
        LOG.info("register_storage(), driver successfully registered")
        return storage

    def get_storage(self, context):

        status = "Error"
        model_symmetrix = ""
        total_cap = 0
        used_cap = 0

        try:
            # Initialise PyU4V connection to Unisphere
            conn = PyU4V.U4VConn(
                u4v_version=self.univmax_version,
                server_ip=self.server_ip,
                port=self.port,
                verify=False,
                username=self.username,
                password=self.password)

            LOG.info("Successfully connected storage")
            status = "Available"

            # Get the Unisphere model
            uri = "/system/symmetrix/" + self.symmetrix_id
            model = conn.common.get_request(uri, "")
            model_symmetrix = model['symmetrix'][0]['model']
            LOG.info("Successfully retrieved storage model")

            # Get Storage details for capacity info
            uri = "/sloprovisioning/symmetrix/" + self.symmetrix_id
            storg_info = conn.common.get_request(uri, "")
            total_cap = storg_info['symmetrix'][0]['virtualCapacity']['total_capacity_gb']
            used_cap = storg_info['symmetrix'][0]['virtualCapacity']['used_capacity_gb']
            LOG.info("Successfully retrieved storage capacity")

            # Close the session
            conn.close_session()

        except:
            LOG.error("Failed to get storage details")
            return None

        storage = {
            'id': self.storage_id,
            'name': '',
            'vendor': '',
            'description': '',
            'model': model_symmetrix,
            'status': status,
            'serial_number': '',
            'location': '',
            'total_capacity': total_cap,
            'used_capacity': used_cap,
            'free_capacity': 0
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
