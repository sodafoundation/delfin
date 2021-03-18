# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from oslo_log import log

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.dell_emc.unity import rest_handler, alert_handler
from delfin.drivers.dell_emc.unity.alert_handler import AlertHandler

LOG = log.getLogger(__name__)


class UnityStorDriver(driver.StorageDriver):
    """UnityStorDriver implement the DELL EMC Storage driver"""
    HEALTH_OK = (5, 7)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.verify = kwargs.get('verify', False)
        self.rest_handler.login()

    def close_connection(self):
        self.rest_handler.logout()

    def get_storage(self, context):
        system_info = self.rest_handler.get_storage()
        capacity = self.rest_handler.get_capacity()
        version_info = self.rest_handler.get_soft_version()
        status = constants.StorageStatus.OFFLINE
        if system_info is not None and capacity is not None:
            system_entries = system_info.get('entries')
            for system in system_entries:
                content = system.get('content', {})
                name = content.get('name')
                model = content.get('model')
                serial_number = content.get('serialNumber')
                health_value = content.get('health').get('value')
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                break
            capacity_info = capacity.get('entries')
            for per_capacity in capacity_info:
                content = per_capacity.get('content', {})
                free = content.get('sizeFree')
                total = content.get('sizeTotal')
                used = content.get('sizeUsed')
                subs = content.get('sizeSubscribed')
                break
            soft_version = version_info.get('entries')
            for soft_info in soft_version:
                content = soft_info.get('content', {})
                version = content.get('id')
                break
            system_result = {
                'name': name,
                'vendor': 'DELL EMC',
                'model': model,
                'status': status,
                'serial_number': serial_number,
                'firmware_version': version,
                'location': '',
                'subscribed_capacity': int(subs),
                'total_capacity': int(total),
                'raw_capacity': int(total),
                'used_capacity': int(used),
                'free_capacity': int(free)
            }
        return system_result

    def list_storage_pools(self, context):
        pool_info = self.rest_handler.get_all_pools()
        pool_list = []
        pool_type = constants.StorageType.UNIFIED
        if pool_info is not None:
            pool_entries = pool_info.get('entries')
            for pool in pool_entries:
                content = pool.get('content', {})
                health_value = content.get('health').get('value')
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                pool_result = {
                    'name': content.get('name'),
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': str(content.get('id')),
                    'description': content.get('description'),
                    'status': status,
                    'storage_type': pool_type,
                    'total_capacity': int(content.get('sizeTotal')),
                    'subscribed_capacity': int(content.get('sizeSubscribed')),
                    'used_capacity': int(content.get('sizeUsed')),
                    'free_capacity': int(content.get('sizeFree'))
                }
                pool_list.append(pool_result)
        return pool_list

    def volume_handler(self, volumes, volume_list):
        if volumes is not None:
            vol_entries = volumes.get('entries')
            for volume in vol_entries:
                content = volume.get('content', {})
                total = content.get('sizeTotal')
                used = content.get('sizeAllocated')
                vol_type = constants.VolumeType.THICK
                if content.get('isThinEnabled') is True:
                    vol_type = constants.VolumeType.THIN
                health_value = content.get('health').get('value')
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                volume_result = {
                    'name': content.get('name'),
                    'storage_id': self.storage_id,
                    'description': content.get('description'),
                    'status': status,
                    'native_volume_id': str(content.get('id')),
                    'native_storage_pool_id': content.get('pool').get('id'),
                    'wwn': content.get('wwn'),
                    'type': vol_type,
                    'total_capacity': int(total),
                    'used_capacity': int(used),
                    'free_capacity': int(total - used)
                }
                volume_list.append(volume_result)

    def list_volumes(self, context):
        page_number = 1
        volume_list = []
        while True:
            luns = self.rest_handler.get_all_luns(page_number)
            if 'entries' not in luns:
                break
            if len(luns['entries']) < 1:
                break
            self.volume_handler(luns, volume_list)
            page_number = page_number + 1

        return volume_list

    def list_alerts(self, context, query_para=None):
        page_number = 1
        alert_model_list = []
        while True:
            alert_list = self.rest_handler.get_all_alerts(page_number)
            if 'entries' not in alert_list:
                break
            if len(alert_list['entries']) < 1:
                break
            alert_handler.AlertHandler() \
                .parse_queried_alerts(alert_model_list, alert_list, query_para)
            page_number = page_number + 1

        return alert_model_list

    def list_controllers(self, context):
        pass

    def list_ports(self, context):
        pass

    def list_disks(self, context):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return AlertHandler.parse_alert(context, alert)

    def clear_alert(self, context, alert):
        return self.rest_handler.remove_alert(alert)

    @staticmethod
    def get_access_url():
        return 'https://{ip}'
