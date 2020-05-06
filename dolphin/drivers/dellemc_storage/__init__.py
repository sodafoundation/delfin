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

from dolphin.drivers import driver

# TODO: Add below configurations to config file
conf_univmax_version = '90'
conf_symmetrix_id = '000297801895'
conf_server_ip = '127.0.0.1'
conf_port = '8443'

class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """

    # Storage_id's that this driver manages
    storage_ids = []

    def __init__(self, storage_id=None):
        super().__init__(storage_id)
        # Initialize with defaults
        self.storage_id = storage_id
        self.univmax_version = conf_univmax_version
        self.server_ip = conf_server_ip
        self.port = conf_port
        self.verify = False  # Valid values are True/False/<path to certificatefile>
        self.username = ''
        self.password = ''
        self.symmetrix_id = conf_symmetrix_id

    @staticmethod
    def get_storage_registry():
        # register_info dict
        extra_attributes = {
            'symmetrix_id':self.symmetrix_id,
            'univmax_version': self.univmax_version,
            'server_ip': self.server_ip,
            'port': self.port,
            'verify': self.verify
        }
        register_info = {
            'storage_id':self.storage_id,
            'username':'',
            'password':'',
            'hostname':'',
            'extra_attributes': extra_attributes
        }
        LOG.info('get_storage_registry(), typical input dictionary is', register_info)
        return register_info

    def register_storage(self, context, access_info):
        storage = {
            'name': '',
            'description': '',
            'vendor': access_info['vendor'],
            'model': access_info['model'],
            'status': 'not registered',
            'serial_number': '',
            'firmware_version': '',
            'location': '',
            'total_capacity':0,
            'used_capacity': 0,
            'free_capacity': 0,
        }
        # Check if the storage is already registered
        if self.storage_id in VMAXStorageDriver.storage_ids:
            LOG.info('Storage is already registered!')
            return storage

        # Verify input parameters for registration exists
        try:
            self.username = access_info['username']
            self.password = access_info['password']
        except KeyError as err:
            LOG.error('ERROR: Invalid input register_info[' + str(err) + ']')
            return storage

        try:
            # Initialise PyU4V connection to Unisphere
            conn = PyU4V.U4VConn(
                univmax_version=self.univmax_version,
                server_ip=self.server_ip,
                port=self.port,
                verify=self.verify,
                username=self.username,
                password=self.password)

            # Get the Unisphere version
            version = conn.common.get_uni_version()

            # Retrieve a list of arrays managed by your instance of Unisphere
            array_list = conn.common.get_array_list()

            # Close the session
            conn.close_session()

            if (version != self.univmax_version):
                LOG.error('Storage version is different from supported version')

            if (self.symmetrix_id not in array_list):
                LOG.error('ERROR: Array list do not contain storage id')
                return storage

        except:
            LOG.error('ERROR: Failed to connect to VMAX storage')
            return storage

        # Update storage_id's that this driver manages
        if VMAXStorageDriver.storage_ids:
            VMAXStorageDriver.storage_ids.append(self.storage_id)
        else:
            VMAXStorageDriver.storage_ids = [self.storage_id]
        
        storage = get_storage(self, context)

        # Return all the storage ids this driver manage
        LOG.info('register_storage(), driver successfully registered')
        return storage

    def get_storage(self, context):
        Storage = {
            'id': self.storage_id,
            'name': 'VMAX',
            'vendor': 'Dell EMC',
            'description': '',
            'model': '',
            'status': '',
            'serial_number': self.symmetrix_id,
            'location': '',
            'total_capacity': 0,
            'used_capacity': 0,
            'free_capacity': 0
        }

        try:
            # Initialise PyU4V connection to Unisphere
            conn = PyU4V.U4VConn(
                univmax_version=self.univmax_version,
                server_ip=self.server_ip,
                port=self.port,
                verify=self.verify,
                username=self.username,
                password=self.password)

            LOG.info('Successfully connected storage')
            Storage.status = 'Available'

            # Get the Unisphere model
            uri = '/system/symmetrix/' + self.symmetrix_id
            model = conn.common.get_request(uri, '')
            Storage.model = model['symmetrix'][0]['model']
            LOG.info('Successfully retrieved storage model')

            # Get first SRP
            uri = '/sloprovisioning/symmetrix/' + self.symmetrix_id + '/srp'
            srp = conn.common.get_request(uri, '')
            srp_id = srp['srpId'][0]

            # Get first SRP details for capacity info
            uri = '/sloprovisioning/symmetrix/' + self.symmetrix_id + '/srp/' + srp_id
            srp_info = conn.common.get_request(uri, '')
            Storage.total_capacity = srp_info['srp'][0]['total_usable_cap_gb']
            Storage.used_capacity = srp_info['srp'][0]['total_allocated_cap_gb']
            LOG.info('Successfully retrieved storage capacity')

            # Close the session
            conn.close_session()

        except:
            LOG.error('ERROR: Failed to get storage details')
            return Storage

        LOG.info('get_storage(), successfully retrieved storage details')
        return Storage

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
