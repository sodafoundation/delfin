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

from oslo_log import log
from oslo_utils import units

from dolphin import exception
from dolphin.common import constants

LOG = log.getLogger(__name__)

SUPPORTED_VERSION = '90'


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
        self.array_id = access_info.get('extra_attributes', {}). \
            get('array_id', None)
        if not self.array_id:
            raise exception.InvalidInput('Input array_id is missing')

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
            msg = "Failed to connect to VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def get_version(self):
        try:
            # Get the VMAX version
            return self.conn.common.get_uni_version()

        except Exception as err:
            msg = "Failed to get version from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def get_model(self):
        try:
            # Get the VMAX model
            uri = "/system/symmetrix/" + self.array_id
            model = self.conn.common.get_request(uri, "")
            return model['symmetrix'][0]['model']
        except Exception as err:
            msg = "Failed to get model from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def get_storage_capacity(self):
        try:
            uri = "/" + SUPPORTED_VERSION \
                  + "/sloprovisioning/symmetrix/" + self.array_id
            storage_info = self.conn.common.get_request(uri, "")
            return storage_info['system_capacity']
        except Exception as err:
            msg = "Failed to get capacity from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def list_storage_pools(self):

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
                    "status": constants.StoragePoolStatus.NORMAL,
                    "storage_type": constants.StorageType.BLOCK,
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(total_cap - used_cap),
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            msg = "Failed to get pool metrics from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def list_volumes(self, storage_id):

        try:
            # List all volumes except data volumes
            volumes = self.conn.provisioning.get_volume_list(
                filters={'data_volume': 'false'})

            # TODO: Update constants.VolumeStatus to make mapping more precise
            switcher = {
                'Ready': constants.VolumeStatus.AVAILABLE,
                'Not Ready': constants.VolumeStatus.ERROR,
                'Mixed': constants.VolumeStatus.ERROR,
                'Write Disabled': constants.VolumeStatus.ERROR,
                'N/A': constants.VolumeStatus.ERROR,
            }

            volume_list = []
            for volume in volumes:
                # Get volume details
                vol = self.conn.provisioning.get_volume(volume)

                total_cap = vol['cap_mb'] * units.Mi
                used_cap = (total_cap * vol['allocated_percent']) / 100.0
                free_cap = total_cap - used_cap

                status = switcher.get(vol['status'],
                                      constants.VolumeStatus.ERROR)

                description = "Dell EMC VMAX volume"
                if vol['type'] == 'TDEV':
                    description = "Dell EMC VMAX 'thin device' volume"

                v = {
                    "name": volume,
                    "storage_id": storage_id,
                    "description": description,
                    "status": status,
                    "original_id": vol['volumeId'],
                    "wwn": vol['wwn'],
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(free_cap),
                }

                if vol['num_of_storage_groups'] == 1:
                    sg = vol['storageGroupId'][0]
                    sg_info = self.conn.provisioning.get_storage_group(sg)
                    v['original_pool_id'] = sg_info['srp']
                    v['compressed'] = sg_info['compression']

                # TODO: Workaround when SG is, not available/not unique

                volume_list.append(v)

            return volume_list

        except Exception as err:
            msg = "Failed to get list volumes from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)
