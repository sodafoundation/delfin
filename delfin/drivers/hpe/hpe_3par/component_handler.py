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
import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants

LOG = log.getLogger(__name__)


class ComponentHandler():
    COMPONENT_HEALTH = 'The following components are healthy'
    SYSTEM_HEALTH = 'System is healthy'
    HPE3PAR_VERSION = 'Superclass'

    HPE3PAR_VENDOR = 'HPE'

    STATUS_MAP = {1: constants.StoragePoolStatus.NORMAL,
                  2: constants.StoragePoolStatus.ABNORMAL,
                  3: constants.StoragePoolStatus.ABNORMAL,
                  99: constants.StoragePoolStatus.OFFLINE}

    VOL_TYPE_MAP = {1: constants.VolumeType.THICK,
                    2: constants.VolumeType.THIN,
                    3: constants.VolumeType.THIN,
                    4: constants.VolumeType.THICK,
                    5: constants.VolumeType.THICK,
                    6: constants.VolumeType.THIN,
                    7: constants.VolumeType.THICK}

    def __init__(self, rest_handler=None, ssh_handler=None):
        self.rest_handler = rest_handler
        self.ssh_handler = ssh_handler

    def set_storage_id(self, storage_id):
        self.storage_id = storage_id

    def get_storage(self, context):
        # get storage info
        storage = self.rest_handler.get_storage()
        # default state is offline
        status = constants.StorageStatus.OFFLINE

        if storage:
            try:
                # Check the hardware and software health
                # status of the storage system
                re_str = self.ssh_handler.get_health_state()
                if ComponentHandler.COMPONENT_HEALTH in re_str \
                        or ComponentHandler.SYSTEM_HEALTH in re_str:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
            except Exception:
                status = constants.StorageStatus.ABNORMAL
                LOG.error('SSH check health Failed!')

            free_cap = int(storage.get('freeCapacityMiB')) * units.Mi
            used_cap = int(storage.get('allocatedCapacityMiB')) * units.Mi
            total_cap = free_cap + used_cap
            raw_cap = int(storage.get('totalCapacityMiB')) * units.Mi
            result = {
                'name': storage.get('name'),
                'vendor': ComponentHandler.HPE3PAR_VENDOR,
                'model': storage.get('model'),
                'status': status,
                'serial_number': storage.get('serialNumber'),
                'firmware_version': storage.get('systemVersion'),
                'location': storage.get('location'),
                'total_capacity': total_cap,
                'raw_capacity': raw_cap,
                'used_capacity': used_cap,
                'free_capacity': free_cap
            }
        else:
            # If no data is returned, it indicates that there
            # may be a problem with the network or the device.
            # Default return OFFLINE
            result = {
                'status': status
            }
        return result

    def list_storage_pools(self, context):
        try:
            # Get list of Hpe3parStor pool details
            pools = self.rest_handler.get_all_pools()
            pool_list = []

            if pools is not None:
                members = pools.get('members')
                for pool in members:
                    # Get pool status  1=normal 2,3=abnormal 99=offline
                    status = self.STATUS_MAP.get(pool.get('state'))

                    # Get pool storage_type   default block
                    pool_type = constants.StorageType.BLOCK
                    usr_used = int(pool['UsrUsage']['usedMiB']) * units.Mi
                    sa_used = int(pool['SAUsage']['usedMiB']) * units.Mi
                    sd_used = int(pool['SDUsage']['usedMiB']) * units.Mi
                    usr_total = int(pool['UsrUsage']['totalMiB']) * units.Mi
                    sa_total = int(pool['SAUsage']['totalMiB']) * units.Mi
                    sd_total = int(pool['SDUsage']['totalMiB']) * units.Mi
                    total_cap = usr_total + sa_total + sd_total
                    used_cap = usr_used + sa_used + sd_used
                    free_cap = total_cap - used_cap
                    usr_subcap = int(
                        pool['UsrUsage']['rawTotalMiB']) * units.Mi
                    sa_subcap = int(pool['SAUsage']['rawTotalMiB']) * units.Mi
                    sd_subcap = int(pool['SDUsage']['rawTotalMiB']) * units.Mi
                    subscribed_cap = usr_subcap + sa_subcap + sd_subcap

                    p = {
                        'name': pool.get('name'),
                        'storage_id': self.storage_id,
                        'native_storage_pool_id': str(pool.get('id')),
                        'description': 'Hpe 3par CPG:%s' % pool.get('name'),
                        'status': status,
                        'storage_type': pool_type,
                        'total_capacity': total_cap,
                        'subscribed_capacity': subscribed_cap,
                        'used_capacity': used_cap,
                        'free_capacity': free_cap
                    }
                    pool_list.append(p)
            return pool_list

        except exception.DelfinException as e:
            err_msg = "Failed to get pool metrics from Hpe3parStor: %s" % \
                      (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Failed to get pool metrics from Hpe3parStor: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handle_pool_name(self, volume):
        orig_pool_name = ''
        if 'userCPG' in volume:
            orig_pool_name = volume.get('userCPG')
        if 'snapCPG' in volume:
            if orig_pool_name == '':
                orig_pool_name = volume.get('snapCPG')
            elif volume.get('snapCPG') != orig_pool_name:
                orig_pool_name = '%s/%s' % (orig_pool_name, volume
                                            .get('snapCPG'))
        return orig_pool_name

    def handler_volume(self, volumes, pool_ids):
        volume_list = []
        if volumes is None:
            return
        else:
            members = volumes.get('members')
            for volume in members:
                status = self.STATUS_MAP.get(volume.get('state'))
                orig_pool_name = self.handle_pool_name(volume)

                compressed = True
                deduplicated = True

                vol_type = self.VOL_TYPE_MAP.get(
                    volume.get('provisioningType'))

                # Virtual size of volume in MiB (10242bytes).
                usr_used = int(
                    volume['userSpace']['usedMiB']) * units.Mi
                total_cap = int(volume['sizeMiB']) * units.Mi
                used_cap = usr_used
                free_cap = total_cap - used_cap

                v = {
                    'name': volume.get('name'),
                    'storage_id': self.storage_id,
                    'description': volume.get('comment'),
                    'status': status,
                    'native_volume_id': str(volume.get('id')),
                    'native_storage_pool_id': pool_ids.get(orig_pool_name,
                                                           ''),
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

    def list_volumes(self, context):
        try:
            volumes = self.rest_handler.get_all_volumes()

            pools = self.rest_handler.get_all_pools()
            pool_ids = {}
            if pools is not None:
                members = pools.get('members')
                for pool in members:
                    pool_ids[pool.get('name')] = pool.get('id')

            return self.handler_volume(volumes, pool_ids)

        except exception.DelfinException as e:
            err_msg = "Failed to get list volumes from Hpe3parStor: %s" % \
                      (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Failed to get list volumes from Hpe3parStor: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
