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
from dolphin.common import constants
from dolphin.drivers.huawei.oceanstor import rest_client, consts
from dolphin.drivers import driver
from dolphin import exception

LOG = log.getLogger(__name__)


class OceanStorDriver(driver.StorageDriver):
    """OceanStorDriver implement Huawei OceanStor driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = rest_client.RestClient(**kwargs)
        self.client.login()

    def get_storage(self, context):

        storg_info = self.client.get_storage()

        status = constants.StorageStatus.NORMAL
        if storg_info['HEALTHSTATUS'] != '1':
            status = constants.StorageStatus.ABNORMAL

        storage = {
            'name': 'OceanStor',
            'vendor': 'Huawei',
            'description': 'Huawei OceanStor Storage',
            'model': storg_info['NAME'],
            'status': status,
            'serial_number': storg_info['ID'],
            'firmware_version': '',
            'location': storg_info['LOCATION'],
            'total_capacity': storg_info['TOTALCAPACITY'],
            'used_capacity': storg_info['USEDCAPACITY'],
            'free_capacity': storg_info['FREEDISKSCAPACITY']
        }
        LOG.info("get_storage(), successfully retrieved storage details")
        return storage

    def list_pools(self, context):
        try:
            # Get list of OceanStor pool details
            pools = self.client.get_all_pools()

            pool_list = []
            for pool in pools:
                storage_type = None
                if pool.get('USAGETYPE') == consts.BLOCK_STORAGE_POOL_TYPE:
                    storage_type = constants.StorageType.BLOCK
                if pool.get('USAGETYPE') == consts.FILE_SYSTEM_POOL_TYPE:
                    storage_type = constants.StorageType.FILE
                p = {
                    "name": pool["NAME"],
                    "storage_id": self.storage_id,
                    "original_id": pool["ID"],
                    "description": "Huawei OceanStor Pool",
                    "status": constants.PoolStatus.NORMAL,
                    "storage_type": storage_type,
                    "total_capacity": int(pool["USERTOTALCAPACITY"]),
                    "used_capacity": int(pool["USERCONSUMEDCAPACITY"]),
                    "free_capacity": int(pool["USERFREECAPACITY"]),
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from OceanStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from OceanStor')

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
