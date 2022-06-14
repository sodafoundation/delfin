# Copyright 2022 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
# http:#www.apache.org/licenses/LICENSE-2.0
#
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from oslo_log import log
from delfin.drivers import driver
from delfin.drivers.dell_emc.scaleio import rest_handler
from delfin.drivers.dell_emc.scaleio.rest_handler import RestHandler

LOG = log.getLogger(__name__)


class ScaleioStorageDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.logout()
        self.rest_handler.verify = kwargs.get('verify', False)
        self.rest_handler.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.verify = kwargs.get('verify', False)
        return self.rest_handler.login()

    def get_storage(self, context):
        return self.rest_handler.get_storage(self.storage_id)

    def list_storage_pools(self, context):
        return self.rest_handler.list_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.rest_handler.list_volumes(self.storage_id)

    def list_disks(self, context):
        return self.rest_handler.list_disks(self.storage_id)

    def list_alerts(self, context, query_para=None):
        return self.rest_handler.list_alerts(query_para)

    @staticmethod
    def parse_alert(context, alert):
        return RestHandler.parse_alert(alert)

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def list_storage_host_initiators(self, context):
        return self.rest_handler.list_storage_host_initiators(self.storage_id)

    def list_storage_hosts(self, context):
        return self.rest_handler.list_storage_hosts(self.storage_id)

    def list_masking_views(self, context):
        return self.rest_handler.list_masking_views(self.storage_id)

    @staticmethod
    def get_access_url():
        return 'https://{ip}'
