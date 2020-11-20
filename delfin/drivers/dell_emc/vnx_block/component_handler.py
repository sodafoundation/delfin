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

    EMCVNX_VENDOR = 'DELL EMC'
    RAID_GROUP_ID_PREFIX = 'raid_group_'

    STATUS_MAP = {'Ready': constants.StoragePoolStatus.NORMAL,
                  'Offline': constants.StoragePoolStatus.OFFLINE,
                  'Valid_luns': constants.StoragePoolStatus.NORMAL,
                  'Bound': constants.StoragePoolStatus.NORMAL}

    VOL_TYPE_MAP = {'no': constants.VolumeType.THICK,
                    'yes': constants.VolumeType.THIN}

    VOL_COMPRESSED_MAP = {'no': False,
                          'yes': True}

    def __init__(self, navi_handler=None):
        self.navi_handler = navi_handler

    def get_storage(self):
        # get storage info
        storage = self.navi_handler.get_agent()
        # default state is offline
        status = constants.StorageStatus.OFFLINE

        if storage:
            status = constants.StorageStatus.NORMAL

            used_cap = 0
            free_cap = 0
            raw_cap = 0
            try:
                free_map = self.handler_storage_free_capacity()
                print('free_map=={}'.format(free_map))
                if free_map:
                    raw_cap = free_map.get('raw_cap')
                    free_cap = free_map.get('free_cap')
                    if free_cap == 0:
                        status = constants.StorageStatus.ABNORMAL
            except Exception:
                LOG.error('Get storage free capacity and raw capacity failed!')

            try:
                used_map = self.handler_storage_used_capacity()
                print('used_map=={}'.format(used_map))
                if used_map:
                    used_cap = used_map.get('used_cap')
                    if used_cap == 0:
                        status = constants.StorageStatus.ABNORMAL
            except Exception:
                LOG.error('Get storage used capacity failed!')

            total_cap = used_cap + free_cap
            result = {
                'name': storage.get('node'),
                'vendor': ComponentHandler.EMCVNX_VENDOR,
                'model': storage.get('model'),
                'status': status,
                'serial_number': storage.get('serial_no'),
                'firmware_version': storage.get('revision'),
                'total_capacity': int(total_cap),
                'raw_capacity': int(raw_cap),
                'used_capacity': int(used_cap),
                'free_capacity': int(free_cap)
            }
        else:
            # If no data is returned, it indicates that there
            # may be a problem with the network or the device.
            # Default return OFFLINE
            result = {
                'status': status
            }
        return result

    def list_storage_pools(self, storage_id):
        try:
            # Get list of pool details
            pools = self.navi_handler.get_pools()
            pool_list = []
            if pools:
                for pool in pools:
                    if pool.get('pool_name') is not None:
                        # Get pool status  Ready=normal Offline=offline
                        status = self.STATUS_MAP.get(pool.get('state'))
                        # Get pool storage_type   default block
                        pool_type = constants.StorageType.BLOCK

                        used_cap = float(
                            pool.get("consumed_capacity_gbs")) * units.Gi
                        free_cap = float(
                            pool.get("available_capacity_gbs")) * units.Gi
                        total_cap = float(
                            pool.get("user_capacity_gbs")) * units.Gi
                        subscribed_cap = float(pool.get(
                            "total_subscribed_capacity_gbs")) * units.Gi

                        p = {
                            'name': pool.get('pool_name'),
                            'storage_id': storage_id,
                            'native_storage_pool_id': str(pool.get('pool_id')),
                            'description': pool.get('description'),
                            'status': status,
                            'storage_type': pool_type,
                            'total_capacity': int(total_cap),
                            'subscribed_capacity': int(subscribed_cap),
                            'used_capacity': int(used_cap),
                            'free_capacity': int(free_cap)
                        }
                        pool_list.append(p)
            raid_groups = self.handler_raids(storage_id)
            if raid_groups:
                pool_list.extend(raid_groups)
            return pool_list

        except Exception as e:
            err_msg = "Failed to get pool metrics from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_raids(self, storage_id):
        try:
            # Get list of raid group details
            raid_groups = self.navi_handler.get_raid_group()
            raid_list = []
            if raid_groups:
                for raid in raid_groups:
                    if raid.get('raidgroup_id') is not None:
                        # Get pool status  Ready=normal Offline=offline
                        status = self.STATUS_MAP.get(
                            raid.get('raidgroup_state'),
                            constants.StoragePoolStatus.OFFLINE)
                        # Get pool storage_type   default block
                        pool_type = constants.StorageType.BLOCK

                        free_cap = float(raid.get(
                            "free_capacity_blocks,non-contiguous")) * (
                                units.Ki / 2)
                        total_cap = float(
                            raid.get("logical_capacity_blocks")) * (
                            units.Ki / 2)
                        used_cap = total_cap - free_cap
                        subscribed_cap = float(
                            raid.get("raw_capacity_blocks")) * (units.Ki / 2)

                        p = {
                            'name': 'RAID Group %s' % raid.get('raidgroup_id'),
                            'storage_id': storage_id,
                            'native_storage_pool_id': '%s%s' % (
                                self.RAID_GROUP_ID_PREFIX,
                                raid.get('raidgroup_id')),
                            'description': 'RAID Group %s' %
                                           raid.get('raidgroup_id'),
                            'status': status,
                            'storage_type': pool_type,
                            'total_capacity': int(total_cap),
                            'subscribed_capacity': int(subscribed_cap),
                            'used_capacity': int(used_cap),
                            'free_capacity': int(free_cap)
                        }
                        raid_list.append(p)
            return raid_list

        except Exception as e:
            err_msg = "Failed to get raid group info from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_volume(self, volumes, pool_ids, storage_id):
        volume_list = []
        if volumes:
            for volume in volumes:
                if volume.get('name') is not None:
                    status = self.STATUS_MAP.get(volume.get('current_state'))
                    orig_pool_name = volume.get('pool_name')
                    vol_type = self.VOL_TYPE_MAP.get(
                        volume.get('is_thin_lun').lower())

                    volume_used_cap_str = volume.get('consumed_capacity_gbs')
                    used_cap = 0
                    if volume_used_cap_str and volume_used_cap_str != 'N/A':
                        used_cap = float(volume_used_cap_str) * units.Gi
                    total_cap = float(
                        volume.get('user_capacity_gbs')) * units.Gi
                    free_cap = total_cap - used_cap
                    if free_cap < 0:
                        free_cap = 0

                    v = {
                        'name': volume.get('name'),
                        'storage_id': storage_id,
                        'description': '%s %s' % (volume.get('lun_id'),
                                                  volume.get('name')),
                        'status': status,
                        'native_volume_id': str(volume.get('lun_id')),
                        'native_storage_pool_id': pool_ids.get(orig_pool_name,
                                                               ''),
                        'type': vol_type,
                        'total_capacity': int(total_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap),
                        'compressed': self.VOL_COMPRESSED_MAP.get(
                            volume.get('is_compressed').lower())
                    }
                    volume_list.append(v)
        raid_volumes = self.handler_raid_volume(storage_id)
        if raid_volumes:
            volume_list.extend(raid_volumes)
        return volume_list

    def handler_raid_volume(self, storage_id):
        volume_list = []
        volumes = self.navi_handler.get_all_lun()
        if volumes:
            for volume in volumes:
                if volume.get('raidgroup_id') is not None and volume.get(
                        'raidgroup_id') != 'N/A':
                    status = self.STATUS_MAP.get(
                        volume.get('state'),
                        constants.StoragePoolStatus.OFFLINE)

                    vol_type = self.VOL_TYPE_MAP.get(
                        volume.get('is_thin_lun').lower())

                    total_cap = float(
                        volume.get('lun_capacitymegabytes')) * units.Mi
                    used_cap = total_cap
                    free_cap = 0

                    v = {
                        'name': volume.get('name'),
                        'storage_id': storage_id,
                        'description': '%s %s' % (volume.get(
                            'logical_unit_number'), volume.get('name')),
                        'status': status,
                        'native_volume_id': str(
                            volume.get('logical_unit_number')),
                        'native_storage_pool_id': '%s%s' % (
                            self.RAID_GROUP_ID_PREFIX,
                            volume.get('raidgroup_id')),
                        'type': vol_type,
                        'total_capacity': int(total_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap)
                    }
                    volume_list.append(v)
        return volume_list

    def list_volumes(self, storage_id):
        try:
            volumes = self.navi_handler.get_pool_lun()

            pools = self.navi_handler.get_pools()
            pool_ids = {}
            if pools:
                for pool in pools:
                    if pool.get('pool_name') is not None:
                        pool_ids[pool.get('pool_name')] = pool.get('pool_id')

            return self.handler_volume(volumes, pool_ids, storage_id)

        except Exception as e:
            err_msg = "Failed to get list volumes from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_disk_capacity(self):
        try:
            # Get disk capacity
            objs = self.navi_handler.get_disks()
            obj_sum = 0
            obj_free = 0
            obj_model = {}
            if objs:
                for obj in objs:
                    if obj.get('disk_id') is not None:
                        # Get status Unbound
                        status = obj.get('state')
                        capacity = float(obj.get("capacity", 0))
                        obj_sum += capacity
                        if status == 'Unbound':
                            obj_free += capacity
                obj_model = {
                    'obj_sum': obj_sum * units.Mi,
                    'obj_free': obj_free * units.Mi
                }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get disk capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_pool_capacity(self):
        try:
            # Get pool capacity
            objs = self.navi_handler.get_pools()
            obj_free = 0
            obj_model = {}
            if objs:
                for obj in objs:
                    if obj.get('pool_name') is not None:
                        capacity = float(obj.get("available_capacity_gbs", 0))
                        obj_free += capacity
                obj_model = {
                    'obj_free': obj_free * units.Gi
                }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get pool capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_raid_group_capacity(self):
        try:
            # Get raid_group capacity
            objs = self.navi_handler.get_raid_group()
            obj_free = 0
            obj_model = {}
            if objs:
                for obj in objs:
                    if obj.get('raidgroup_id') is not None:
                        capacity = float(
                            obj.get("free_capacity_blocks,non-contiguous", 0))
                        obj_free += capacity
                obj_model = {
                    'obj_free': obj_free * (units.Ki / 2)
                }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get raid capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_storage_free_capacity(self):
        try:
            obj_model = {}
            # Get storage_free capacity
            free_cap = 0
            raw_cap = 0
            pool_free = 0
            raid_free = 0
            try:
                disk_map = self.handler_disk_capacity()
                if disk_map:
                    raw_cap = disk_map.get('obj_sum')
            except Exception:
                LOG.error('Get disk capacity failed!')

            try:
                pool_map = self.handler_pool_capacity()
                if pool_map:
                    pool_free = pool_map.get('obj_free')
            except Exception:
                LOG.error('Get pool capacity failed!')

            try:
                raid_group_map = self.handler_raid_group_capacity()
                if raid_group_map:
                    raid_free = raid_group_map.get('obj_free')
            except Exception:
                LOG.error('Get raid group capacity failed!')

            free_cap = pool_free + raid_free

            obj_model = {
                'raw_cap': raw_cap,
                'free_cap': free_cap
            }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get storage capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_pool_lun_capacity(self):
        try:
            # Get pool lun capacity
            objs = self.navi_handler.get_pool_lun()
            obj_used = 0
            obj_model = {}
            if objs:
                for obj in objs:
                    if obj.get('name') is not None:
                        if obj.get('current_state') == 'Ready':
                            volume_used_cap_str = obj.get(
                                'consumed_capacity_gbs')
                            if volume_used_cap_str \
                                    and volume_used_cap_str != 'N/A':
                                capacity = float(volume_used_cap_str)
                                obj_used += capacity
                obj_model = {
                    'obj_used': obj_used * units.Gi
                }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get lun capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_raid_lun_capacity(self):
        try:
            # Get raid lun capacity
            objs = self.navi_handler.get_all_lun()
            obj_used = 0
            obj_model = {}
            if objs:
                for obj in objs:
                    if obj.get('raidgroup_id') is not None and obj.get(
                            'raidgroup_id') != 'N/A':
                        if obj.get('state') == 'Bound':
                            capacity = float(obj.get('lun_capacitymegabytes'))
                            obj_used += capacity
                obj_model = {
                    'obj_used': obj_used * units.Mi
                }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get raid lun capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_storage_used_capacity(self):
        try:
            obj_model = {}
            # Get storage_used capacity
            used_cap = 0
            pool_lun_cap = 0
            raid_lun_cap = 0
            try:
                pool_lun_map = self.handler_pool_lun_capacity()
                if pool_lun_map:
                    pool_lun_cap = pool_lun_map.get('obj_used')
            except Exception:
                LOG.error('Get pool lun capacity failed!')

            try:
                raid_lun_map = self.handler_raid_lun_capacity()
                if raid_lun_map:
                    raid_lun_cap = raid_lun_map.get('obj_used')
            except Exception:
                LOG.error('Get pool lun capacity failed!')

            used_cap = pool_lun_cap + raid_lun_cap
            obj_model = {
                'used_cap': used_cap
            }
            return obj_model

        except Exception as e:
            err_msg = "Failed to get pool lun capacity from EmcVnxStor: %s" % (
                six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
