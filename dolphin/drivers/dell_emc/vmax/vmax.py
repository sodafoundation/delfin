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
from dolphin.common import constants
from dolphin.drivers.dell_emc.vmax import alert_handler
from dolphin.drivers.dell_emc.vmax import client
from dolphin.drivers import driver

LOG = log.getLogger(__name__)


class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = client.VMAXClient()
        self._init_vmax(kwargs)

    def _init_vmax(self, access_info):
        self.client.init_connection(access_info)

    def get_storage(self, context):

        # Get the VMAX model
        model = self.client.get_model()

        # Get Storage details for capacity info
        storg_info = self.client.get_storage_capacity()
        total_cap = storg_info.get('usable_total_tb')
        used_cap = storg_info.get('usable_used_tb')
        free_cap = total_cap - used_cap

        storage = {
            'name': '',
            'vendor': 'Dell EMC',
            'description': '',
            'model': model,
            'status': constants.StorageStatus.NORMAL,
            'serial_number': self.client.array_id,
            'location': '',
            'total_capacity': int(total_cap * units.Ti),
            'used_capacity': int(used_cap * units.Ti),
            'free_capacity': int(free_cap * units.Ti)
        }
        LOG.info("get_storage(), successfully retrieved storage details")
        return storage

    def list_storage_pools(self, context):
        return self.client.list_storage_pools()

    def list_volumes(self, context):
        return self.client.list_volumes(self.storage_id)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, alert):
        pass
