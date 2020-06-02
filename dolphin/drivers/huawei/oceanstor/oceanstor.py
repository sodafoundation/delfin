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
from dolphin.drivers.huawei.oceanstor import rest_client
from dolphin.drivers import driver

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
        print(storg_info)

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
