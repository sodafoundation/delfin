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
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.dell_emc.vmax import rest

LOG = log.getLogger(__name__)

EMBEDDED_UNISPHERE_ARRAY_COUNT = 1


class VMAXClient(object):
    """ Client class for communicating with VMAX storage """

    def __init__(self, **kwargs):
        self.uni_version = None
        self.array_id = None
        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        self.rest_host = rest_access.get('host')
        self.rest_port = rest_access.get('port')
        self.rest_username = rest_access.get('username')
        self.rest_password = rest_access.get('password')
        self.rest = rest.VMaxRest()
        self.rest.set_rest_credentials(rest_access)
        self.reset_connection(**kwargs)

    def reset_connection(self, **kwargs):
        """ Reset connection to VMAX storage with new configs """
        self.rest.verify = kwargs.get('verify', False)
        self.rest.establish_rest_session()

    def init_connection(self, access_info):
        """ Given the access_info get a connection to VMAX storage """
        try:
            ver, self.uni_version = self.rest.get_uni_version()
            LOG.info('Connected to Unisphere Version: {0}'.format(ver))
        except exception.InvalidCredential as e:
            msg = "Failed to connect VMAX. Reason: {}".format(e.msg)
            LOG.error(msg)
            raise e
        except Exception as err:
            msg = ("Failed to connect to VMAX. Host or Port is not correct: "
                   "{}".format(err))
            LOG.error(msg)
            raise exception.HTTPConnectionTimeout(msg)

        if not self.uni_version:
            msg = "Invalid input. Failed to get vmax unisphere version"
            raise exception.InvalidInput(msg)

        self.array_id = access_info.get('extra_attributes', {}). \
            get('array_id', None)

        try:
            # Get array details from unisphere
            array = self.rest.get_array_detail(version=self.uni_version)
            if not array:
                msg = "Failed to get array details"
                raise exception.InvalidInput(msg)

            if len(array['symmetrixId']) == EMBEDDED_UNISPHERE_ARRAY_COUNT:
                if not self.array_id:
                    self.array_id = array['symmetrixId'][0]
                elif self.array_id != array['symmetrixId'][0]:
                    msg = "Invalid array_id. Expected id: {}". \
                        format(array['symmetrixId'])
                    raise exception.InvalidInput(msg)
        except Exception as err:
            msg = "Failed to get array details from VMAX: {}".format(err)
            raise exception.StorageBackendException(msg)

        if not self.array_id:
            msg = "Input array_id is missing. Supported ids: {}". \
                format(array['symmetrixId'])
            raise exception.InvalidInput(msg)

    def get_array_details(self):
        try:
            # Get the VMAX array properties
            return self.rest.get_vmax_array_details(version=self.uni_version,
                                                    array=self.array_id)
        except Exception as err:
            msg = "Failed to get array details from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def get_storage_capacity(self):
        try:
            storage_info = self.rest.get_system_capacity(
                self.array_id, self.uni_version)
            return storage_info
        except Exception as err:
            msg = "Failed to get capacity from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def list_storage_pools(self, storage_id):

        try:
            # Get list of SRP pool names
            pools = self.rest.get_srp_by_name(
                self.array_id, self.uni_version, srp='')['srpId']

            pool_list = []
            for pool in pools:
                pool_info = self.rest.get_srp_by_name(
                    self.array_id, self.uni_version, srp=pool)

                srp_cap = pool_info['srp_capacity']
                total_cap = srp_cap['usable_total_tb'] * units.Ti
                used_cap = srp_cap['usable_used_tb'] * units.Ti
                subscribed_cap = srp_cap['subscribed_total_tb'] * units.Ti
                p = {
                    "name": pool,
                    "storage_id": storage_id,
                    "native_storage_pool_id": pool_info["srpId"],
                    "description": "Dell EMC VMAX Pool",
                    "status": constants.StoragePoolStatus.NORMAL,
                    "storage_type": constants.StorageType.BLOCK,
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(total_cap - used_cap),
                    "subscribed_capacity": int(subscribed_cap),
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            msg = "Failed to get pool metrics from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def list_volumes(self, storage_id):

        try:
            # Get default SRPs assigned for the array
            default_srps = self.rest.get_default_srps(
                self.array_id, version=self.uni_version)
            # List all volumes except data volumes
            volumes = self.rest.get_volume_list(
                self.array_id, version=self.uni_version,
                params={'data_volume': 'false'})

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
                vol = self.rest.get_volume(self.array_id,
                                           self.uni_version, volume)

                emulation_type = vol['emulation']
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
                    "native_volume_id": vol['volumeId'],
                    "wwn": vol['wwn'],
                    "type": constants.VolumeType.THIN,
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(free_cap),
                }

                if vol['num_of_storage_groups'] == 1:
                    sg = vol['storageGroupId'][0]
                    sg_info = self.rest.get_storage_group(
                        self.array_id, self.uni_version, sg)
                    v['native_storage_pool_id'] = sg_info['srp']
                    v['compressed'] = sg_info['compression']
                else:
                    v['native_storage_pool_id'] = default_srps[emulation_type]

                volume_list.append(v)

            return volume_list

        except Exception as err:
            msg = "Failed to get list volumes from VMAX: {}".format(err)
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

    def list_alerts(self):
        """Get all alerts from an array."""
        return self.rest.get_alerts(version=self.uni_version,
                                    array=self.array_id)

    def clear_alert(self, sequence_number):
        """Clear alert for given sequence number."""
        return self.rest.clear_alert(sequence_number, version=self.uni_version,
                                     array=self.array_id)
