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

LOG = log.getLogger(__name__)

class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """
    # Storage_id's that this driver manages
    storage_ids = []

    def __init__(self, storage_id):
        super().__init__(storage_id)
        self.storage_id = storage_id

    @staticmethod
    def get_storage_registry():
        register_info = {
            "server_ip": "192.168.20.158",
            "port": 8443,
            "username": "unisphere-user",
            "password": "secret-pass",
            "u4v_version":'90',
            "verify": "unisphere-ssl-cakey-file"
        }
        LOG.info('get_storage_registry()')
        return register_info

    def register_storage(self, context, register_info):
        try:
            u4v_version = register_info['u4v_version']
            server_ip = register_info['server_ip']
            port = register_info['port']
            verify = register_info['verify']
            username = register_info['username']
            password = register_info['password']

            # Initialise PyU4V connection to Unisphere
            conn = PyU4V.U4VConn(
                u4v_version=u4v_version, server_ip=server_ip, port=port,
                verify=verify, username=username, password=password)

            # Get the Unisphere version
            version = conn.common.get_uni_version()

            # Retrieve a list of arrays managed by your instance of Unisphere
            array_list = conn.common.get_array_list()

            # Close the session
            conn.close_session()

        except:
            print('Failed to connect to storage')

        else:
            # Update storage_id's that this driver manages
            if VMAXStorageDriver.storage_ids:
                if self.storage_id in VMAXStorageDriver.storage_ids:
                    LOG.info('Storage is already registered!')
                else:
                    VMAXStorageDriver.storage_ids.append(self.storage_id)
            else:
                VMAXStorageDriver.storage_ids = [self.storage_id]
        
        print('register_storage()')
        return VMAXStorageDriver.storage_ids

    def get_storage(self, context):
        try:
            u4v_version = register_info['u4v_version']
            server_ip = register_info['server_ip']
            port = register_info['port']
            verify = register_info['verify']
            username = register_info['username']
            password = register_info['password']

            # Initialise PyU4V connection to Unisphere
            conn = PyU4V.U4VConn(
                u4v_version=u4v_version, server_ip=server_ip, port=port,
                verify=verify, username=username, password=password)


            # Get the Unisphere version
            version = conn.common.get_uni_version()

            # Retrieve a list of arrays managed by your instance of Unisphere
            array_list = conn.common.get_array_list()

            # Output results to screen
            LOG.info('version is: {ver}'.format(ver=version[0]))
            LOG.info('This instance of Unisphere instance manages the following arrays: '
                '{arr_list}'.format(arr_list=array_list))

            # GET those arrays which are local to this instance of Unisphere
            local_array_list = list()
            for array_id in array_list:
                array_details = conn.common.get_array(array_id)
                if array_details['local']:
                    local_array_list.append(array_id)

            # Output results to screen
            LOG.info('The following arrays are local to this Unisphere instance: '
                '{arr_list}'.format(arr_list=local_array_list))

            # Close the session
            conn.close_session()

        except:
            print('Failed to connect to storage')

        else:
            print('get_storage()')
            return array_list

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

