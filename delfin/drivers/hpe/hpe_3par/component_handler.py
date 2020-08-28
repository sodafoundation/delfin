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

from delfin import exception
from delfin.common import constants
from delfin.drivers.hpe.hpe_3par import consts

LOG = log.getLogger(__name__)


class ComponentHandler():
    """Hpe3par's Component handler，Superclass,
    """
    COMPONENT_HEALTH = 'The following components are healthy'
    SYSTEM_HEALTH = 'System is healthy'
    HPE3PAR_VERSION = 'Superclass'

    HPE3PAR_VENDOR = 'HPE'

    def __init__(self, resthanlder=None, sshhanlder=None):
        self.resthanlder = resthanlder
        self.sshhanlder = sshhanlder

    def set_storage_id(self, storage_id):
        self.storage_id = storage_id

    def get_storage(self, context):
        # get storage info
        storage = self.resthanlder.get_storage()
        # get capacity
        capacity = self.resthanlder.get_capacity()
        # default state is offline
        status = constants.StorageStatus.OFFLINE

        if storage is not None:
            try:
                # Check the hardware and software health
                # status of the storage system
                # return: System is healthy
                re_str = self.sshhanlder.get_health_state(context)
                if ComponentHandler.COMPONENT_HEALTH in re_str \
                        or ComponentHandler.SYSTEM_HEALTH in re_str:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
            except Exception:
                status = constants.StorageStatus.ABNORMAL
                LOG.error('SSH check health Failed!')
            # "Total capacity (MiB) in the system."
            total_cap = int(
                storage.get('totalCapacityMiB')) * consts.MiB_TO_Bytes
            internal_cap = int(
                capacity.get('allCapacity').get('allocated').get('system').get(
                    'internalMiB')) * consts.MiB_TO_Bytes
            spare_cap = int(
                capacity.get('allCapacity').get('allocated').get('system').get(
                    'spareMiB')) * consts.MiB_TO_Bytes
            total_cap = total_cap - internal_cap - spare_cap
            # Free capacity (MiB) in the system
            free_cap = int(
                storage.get('freeCapacityMiB')) * consts.MiB_TO_Bytes
            used_cap = total_cap - free_cap

            # raw_capacity
            raw_cap = int(
                storage.get('totalCapacityMiB')) * consts.MiB_TO_Bytes
            # subscribed_capacity
            subscribed_cap = int(
                storage.get('allocatedCapacityMiB')) * consts.MiB_TO_Bytes
            s = {
                'name': storage.get('name'),
                'vendor': ComponentHandler.HPE3PAR_VENDOR,
                'model': storage.get('model'),
                'status': status,
                'serial_number': storage.get('serialNumber'),
                'firmware_version': storage.get('systemVersion'),
                'location': storage.get('location'),
                'total_capacity': total_cap,
                'raw_capacity': raw_cap,  # raw_capacity
                'subscribed_capacity': subscribed_cap,  # subscribed_capacity
                'used_capacity': used_cap,
                'free_capacity': free_cap
            }
        else:
            # If no data is returned, it indicates that there
            # may be a problem with the network or the device.
            # Default return OFFLINE
            s = {
                'status': status
            }
        return s

    def list_storage_pools(self, context):
        try:
            # Get list of Hpe3parStor pool details
            pools = self.resthanlder.get_all_pools()
            pool_list = []

            if pools is not None:
                members = pools.get('members')
                for pool in members:
                    # Get pool status  1=normal 2,3=abnormal 99=offline
                    status = constants.StoragePoolStatus.OFFLINE
                    if pool.get('state') == consts.STATUS_POOL_NORMAL:
                        status = constants.StoragePoolStatus.NORMAL
                    elif (pool.get('state') == consts.STATUS_POOL_DEGRADED
                          or pool.get('state') == consts.STATUS_POOL_FAILED):
                        status = constants.StoragePoolStatus.ABNORMAL

                    # Get pool storage_type   default block
                    pool_type = constants.StorageType.BLOCK
                    usr_used = int(
                        pool['UsrUsage']['usedMiB']) * consts.MiB_TO_Bytes
                    sa_used = int(
                        pool['SAUsage']['usedMiB']) * consts.MiB_TO_Bytes
                    sd_used = int(
                        pool['SDUsage']['usedMiB']) * consts.MiB_TO_Bytes
                    usr_total = int(
                        pool['UsrUsage']['totalMiB']) * consts.MiB_TO_Bytes
                    sa_total = int(
                        pool['SAUsage']['totalMiB']) * consts.MiB_TO_Bytes
                    sd_total = int(
                        pool['SDUsage']['totalMiB']) * consts.MiB_TO_Bytes
                    total_cap = usr_total + sa_total + sd_total
                    used_cap = usr_used + sa_used + sd_used
                    free_cap = total_cap - used_cap
                    usr_subcap = int(
                        pool['UsrUsage']['rawTotalMiB']) * consts.MiB_TO_Bytes
                    sa_subcap = int(
                        pool['SAUsage']['rawTotalMiB']) * consts.MiB_TO_Bytes
                    sd_subcap = int(
                        pool['SDUsage']['rawTotalMiB']) * consts.MiB_TO_Bytes
                    subscribed_cap = usr_subcap + sa_subcap + sd_subcap

                    p = {
                        'name': pool.get('name'),
                        'storage_id': self.storage_id,
                        'native_storage_pool_id': str(pool.get('id')),
                        'description': 'Hpe 3parStor CPG:' + pool.get('name'),
                        'status': status,
                        'storage_type': pool_type,
                        'total_capacity': total_cap,
                        'subscribed_capacity': subscribed_cap,
                        # rawTotalSpaceMiB
                        'used_capacity': used_cap,
                        'free_capacity': free_cap
                    }
                    pool_list.append(p)
            return pool_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from Hpe3parStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from Hpe3parStor')

    def list_volumes(self, context):
        try:
            # Get all volumes in Hpe3parStor
            volumes = self.resthanlder.get_all_volumes()
            volume_list = []

            if volumes is not None:
                members = volumes.get('members')
                for volume in members:
                    status = constants.StoragePoolStatus.OFFLINE
                    if volume.get('state') == consts.STATUS_VOLUME_NORMAL:
                        status = constants.StoragePoolStatus.NORMAL
                    elif (volume.get('state') == consts.STATUS_VOLUME_DEGRADED
                          or volume.get('state') ==
                          consts.STATUS_VOLUME_FAILED):
                        status = constants.StoragePoolStatus.ABNORMAL

                    # Get CPG name CPG name from which
                    # the user space is allocated.
                    # /CPG name from which the snapshot
                    # (snap and admin) space is allocated.
                    # userCPG snapCPG maybe not exist
                    orig_pool_id = ''
                    if 'userCPG' in volume:
                        orig_pool_id = volume.get('userCPG')
                    if 'snapCPG' in volume:
                        if orig_pool_id == '':
                            orig_pool_id = volume.get('snapCPG')
                        elif volume.get('snapCPG') != orig_pool_id:
                            orig_pool_id = orig_pool_id + '/' + \
                                volume.get('snapCPG')

                    compressed = True
                    deduplicated = True

                    vol_type = constants.VolumeType.THICK
                    if volume.get('provisioningType') == consts.THIN_LUNTYPE:
                        vol_type = constants.VolumeType.THIN

                    # Virtual size of volume in MiB (10242bytes).
                    usr_used = int(volume['userSpace']['reservedMiB']) * \
                        consts.MiB_TO_Bytes
                    admin_used = int(volume['adminSpace']['reservedMiB']) * \
                        consts.MiB_TO_Bytes
                    snap_used = int(volume['snapshotSpace']['reservedMiB']) \
                        * consts.MiB_TO_Bytes
                    total_cap = int(volume['sizeMiB']) * \
                        consts.MiB_TO_Bytes
                    used_cap = usr_used + admin_used + snap_used
                    free_cap = total_cap - used_cap

                    v = {
                        'name': volume.get('name'),
                        'storage_id': self.storage_id,
                        'description': volume.get('comment'),  # none in 1.2
                        'status': status,
                        'native_volume_id': volume.get('id'),
                        'native_storage_pool_id': orig_pool_id,
                        'wwn': volume.get('wwn'),
                        'type': vol_type,
                        'total_capacity': total_cap,
                        'used_capacity': used_cap,
                        'free_capacity': free_cap,
                        'compressed': compressed,
                        'deduplicated': deduplicated
                    }
                    volume_list.append(v)
            return volume_list

        except Exception as err:
            LOG.error(
                "Failed to get list volumes from Hpe3parStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get list volumes from Hpe3parStor')
