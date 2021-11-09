# Copyright 2021 The SODA Authors.
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

from delfin.drivers import driver
from delfin.drivers.hitachi.hnas import nas_handler


class HitachiHNasDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nas_handler = nas_handler.NasHandler(**kwargs)
        self.nas_handler.login()

    def reset_connection(self, context, **kwargs):
        self.nas_handler.login()

    def get_storage(self, context):
        return self.nas_handler.get_storage()

    def list_storage_pools(self, context):
        return self.nas_handler.get_pool(self.storage_id)

    def list_volumes(self, context):
        pass

    def list_controllers(self, context):
        return self.nas_handler.list_controllers(self.storage_id)

    def list_ports(self, context):
        return self.nas_handler.list_ports(self.storage_id)

    def list_disks(self, context):
        return self.nas_handler.get_disk(self.storage_id)

    def list_alerts(self, context, query_para=None):
        return self.nas_handler.list_alerts(query_para)

    def list_qtrees(self, context):
        return self.nas_handler.list_qtrees(self.storage_id)

    def list_quotas(self, context):
        return self.nas_handler.list_quotas(self.storage_id)

    def list_filesystems(self, context):
        return self.nas_handler.list_filesystems(self.storage_id)

    def list_shares(self, context):
        return self.nas_handler.list_shares(self.storage_id)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return nas_handler.NasHandler.parse_alert(alert)

    def clear_alert(self, context, alert):
        pass

    @staticmethod
    def get_access_url():
        return 'https://{ip}'
