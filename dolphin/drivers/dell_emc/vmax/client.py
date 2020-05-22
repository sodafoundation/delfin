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

import json
import PyU4V

from dolphin import exception
from dolphin.common import constants
from oslo_log import log
from oslo_utils import units

LOG = log.getLogger(__name__)

SUPPORTED_VERSION='90'


class VMAXClient(object):
    """ Client class for communicating with VMAX storage """
    def __init__(self):
        self.conn = None
        self.array_id = None

    def __del__(self):
        # De-initialize session
        if self.conn:
            self.conn.close_session()
            self.conn = None

    def init_connection(self, access_info):
        """ Given the access_info get a connection to VMAX storage """
        self.array_id = access_info.get('extra_attributes', {}).\
                                get('array_id', None)
        if not self.array_id:
            raise exception.InvalidInput(reason='Input array_id is missing')

        try:
            # Initialise PyU4V connection to VMAX
            self.conn = PyU4V.U4VConn(
                u4v_version=SUPPORTED_VERSION,
                server_ip=access_info['host'],
                port=access_info['port'],
                verify=False,
                array_id=self.array_id,
                username=access_info['username'],
                password=access_info['password'])

        except Exception as err:
            LOG.error("Failed to connect to VMAX: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to connect to VMAX storage')

    def get_version(self):
        try:
            # Get the VMAX version
            return self.conn.common.get_uni_version()

        except Exception as err:
            LOG.error("Failed to get version from VMAX: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get version from VMAX')

    def get_model(self):
        try:
            # Get the VMAX model
            uri = "/system/symmetrix/" + self.array_id
            model = self.conn.common.get_request(uri, "")
            return model['symmetrix'][0]['model']
        except Exception as err:
            LOG.error("Failed to get model from VMAX: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get model from VMAX')

    def get_storage_capacity(self):
        try:
            uri = "/" + SUPPORTED_VERSION + "/sloprovisioning/symmetrix/" + self.array_id
            storage_info = self.conn.common.get_request(uri, "")
            return storage_info['system_capacity']
        except Exception as err:
            LOG.error("Failed to get model from VMAX: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get capacity from VMAX')

    def list_pools(self):

        try:
            # Get list of SRP pool names
            pools = self.conn.provisioning.get_srp_list()

            pool_list = []
            for pool in pools:
                pool_info = self.conn.provisioning.get_srp(pool)

                srp_cap = pool_info['srp_capacity']
                total_cap = srp_cap['usable_total_tb'] * units.Ti
                used_cap = srp_cap['usable_used_tb'] * units.Ti

                p = {
                    "name": pool,
                    "original_id": pool_info["srpId"],
                    "description": "Dell EMC VMAX Pool",
                    "status": constants.PoolStatus.NORMAL,
                    "storage_type": constants.StorageType.BLOCK,
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(total_cap - used_cap),
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            LOG.error("Failed to get pool metrics from VMAX: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from VMAX')
