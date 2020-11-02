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

from delfin.drivers import driver
from delfin.drivers.dell_emc.unity import rest_handler, alert_handler
from delfin.drivers.utils.rest_client import RestClient
from delfin.common import constants

LOG = log.getLogger(__name__)


class UNITYStorDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rest_client = RestClient(**kwargs)
        self.rest_client.verify = kwargs.get('verify', False)
        self.rest_handler = rest_handler.RestHandler(self.rest_client)
        self.rest_handler.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_client.verify = kwargs.get('verify', False)
        self.rest_handler.login()

    def close_connection(self):
        self.rest_handler.logout()

    def set_storage_id(self, storage_id):
        self.storage_id = storage_id

    def get_storage(self, context):
        system_info = self.rest_handler.get_storage(context)
        capacity = self.rest_handler.get_capacity(context)
        status = constants.StorageStatus.OFFLINE
        if system_info is not None and capacity is not None:
            system_entries = system_info.get('entries')
            for system in system_entries:
                name = system.get('content').get('name')
                model = system.get('content').get('model')
                serialNumber = system.get('content').get('serialNumber')
                health_value = system.get('content').get('health').get('value')
                if health_value == 5:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
            capacity_info = capacity.get('entries')
            for per_capacity in capacity_info:
                free = per_capacity.get('content').get('sizeFree')
                total = per_capacity.get('content').get('sizeTotal')
                used = per_capacity.get('content').get('sizeUsed')
                raw = per_capacity.get('content').get('sizePreallocated')
            result = {
                'name': name,
                'vendor': 'dell',
                'model': model,
                'status': status,
                'serial_number': serialNumber,
                'firmware_version': '',
                'location': '',
                'total_capacity': total,
                'raw_capacity': raw,
                'used_capacity': used,
                'free_capacity': free
            }
        return result

    def list_storage_pools(self, context):
        self.set_storage_id(self.storage_id)
        pool_info = self.rest_handler.get_all_pools(context)
        pool_list = []
        pool_type = constants.StorageType.BLOCK
        if pool_info is not None:
            pool_entries = pool_info.get('entries')
            for pool in pool_entries:
                health_value = pool.get('content').get('health').get('value')
                if health_value == 5:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                p = {
                    'name': pool.get('content').get('name'),
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': str(
                        pool.get('content').get('id')),
                    'description': pool.get('content').get('description'),
                    'status': status,
                    'storage_type': pool_type,
                    'total_capacity': pool.get('content').get('sizeTotal'),
                    'subscribed_capacity': pool.get('content').get(
                        'sizeSubscribed'),
                    'used_capacity': pool.get('content').get('sizeUsed'),
                    'free_capacity': pool.get('content').get('sizeFree')
                }
                pool_list.append(p)
        return pool_list

    def volume_handler(self, volumes, volume_list):
        if volumes is not None:
            vol_entries = volumes.get('entries')
            for volume in vol_entries:
                total = volume.get('content').get('sizeTotal')
                used = volume.get('content').get('sizeAllocated')
                vol_type = constants.VolumeType.THICK
                if volume.get('content').get('isThinEnabled') == 'true':
                    vol_type = constants.VolumeType.THIN
                compressed = True
                deduplicated = volume.get('content').\
                    get('isAdvancedDedupEnabled')
                health_value = volume.get('content').get('health').get('value')
                if health_value == 5:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                v = {
                    'name': volume.get('content').get('name'),
                    'storage_id': self.storage_id,
                    'description': volume.get('content').get('description'),
                    'status': status,
                    'native_volume_id': str(volume.get('content').get('id')),
                    'native_storage_pool_id':
                        volume.get('content').get('pool'.get('id')),
                    'wwn': volume.get('content').get('wwn'),
                    'type': vol_type,
                    'total_capacity': total,
                    'used_capacity': used,
                    'free_capacity': total - used,
                    'compressed': compressed,
                    'deduplicated': deduplicated
                }
                volume_list.append(v)

    # def filesystem_handler(self, files, volume_list):
    #     if files is not None:
    #         file_entries = files.get('entries')
    #         for file in file_entries:
    #             total = file.get('content').get('sizeTotal')
    #             used = file.get('content').get('sizeAllocated')
    #             vol_type = constants.VolumeType.THICK
    #             if file.get('content').get('isThinEnabled') == 'true':
    #                 vol_type = constants.VolumeType.THIN
    #             compressed = True
    #             deduplicated = file.get('content').get(
    #                     'isAdvancedDedupEnabled')
    #             health_value = file.get('content').get('health').get('value')
    #             if health_value == 5:
    #                 status = constants.StorageStatus.NORMAL
    #             else:
    #                 status = constants.StorageStatus.ABNORMAL
    #             v = {
    #                 'name': file.get('content').get('name'),
    #                 'storage_id': self.storage_id,
    #                 'description': file.get('content').get('description'),
    #                 'status': status,
    #                 'native_volume_id': str(file.get('content').get('id')),
    #                 'native_storage_pool_id':
    #                     file.get('content').get('pool'.get('id')),
    #                 'wwn': file.get('content').get('wwn'),
    #                 'type': vol_type,
    #                 'total_capacity': total,
    #                 'used_capacity': used,
    #                 'free_capacity': total - used,
    #                 'compressed': compressed,
    #                 'deduplicated': deduplicated
    #             }
    #             volume_list.append(v)

    def list_volumes(self, context):
        self.set_storage_id(self.storage_id)
        volume_list = []
        luns = self.rest_handler.get_all_luns(context)
        filesystems = self.rest_handler.get_all_filesystem(context)
        self.volume_handler(luns, volume_list)
        self.volume_handler(filesystems, volume_list)

        return volume_list

    def list_alerts(self, context, query_para=None):
        alert_list = self.rest_handler.get_all_alerts(context)
        alert_model_list = alert_handler.AlertHandler() \
            .parse_queried_alerts(alert_list, query_para)
        return alert_model_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, alert):
        return self.rest_handler.remove_alert(context, alert)
