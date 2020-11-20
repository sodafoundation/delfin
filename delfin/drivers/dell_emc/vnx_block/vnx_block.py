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
from delfin.drivers.dell_emc.vnx_block.alert_handler import AlertHandler
from delfin.drivers.dell_emc.vnx_block.component_handler import \
    ComponentHandler
from delfin.drivers.dell_emc.vnx_block.navi_handler import NaviHandler

LOG = log.getLogger(__name__)


class VnxBlockStorDriver(driver.StorageDriver):
    """VnxBlockStorDriver implement EMC VNX Stor driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.navi_handler = NaviHandler(**kwargs)
        self.version = self.navi_handler.login()

        self.comhandler = ComponentHandler(navi_handler=self.navi_handler)
        self.alert_handler = AlertHandler(navi_handler=self.navi_handler)

    def reset_connection(self, context, **kwargs):
        pass

    def close_connection(self):
        pass

    def get_storage(self, context):
        return self.comhandler.get_storage(context)

    def list_storage_pools(self, context):
        self.comhandler.set_storage_id(self.storage_id)
        return self.comhandler.list_storage_pools(context)

    def list_volumes(self, context):
        self.comhandler.set_storage_id(self.storage_id)
        return self.comhandler.list_volumes(context)

    def list_alerts(self, context, query_para=None):
        return self.alert_handler.list_alerts(context, query_para)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        return self.alert_handler.parse_alert(context, alert)

    def clear_alert(self, context, alert):
        pass
