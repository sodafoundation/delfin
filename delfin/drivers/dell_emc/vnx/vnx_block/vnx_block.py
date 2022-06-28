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
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.dell_emc.vnx.vnx_block.alert_handler import AlertHandler
from delfin.drivers.dell_emc.vnx.vnx_block.component_handler import \
    ComponentHandler
from delfin.drivers.dell_emc.vnx.vnx_block.navi_handler import NaviHandler

LOG = log.getLogger(__name__)


class VnxBlockStorDriver(driver.StorageDriver):
    """VnxBlockStorDriver implement EMC VNX Stor driver"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.navi_handler = NaviHandler(**kwargs)
        self.version = self.navi_handler.login()
        self.com_handler = ComponentHandler(self.navi_handler)

    def reset_connection(self, context, **kwargs):
        self.navi_handler.remove_cer()
        self.navi_handler.verify = kwargs.get('verify', False)
        self.navi_handler.login()

    def close_connection(self):
        pass

    def get_storage(self, context):
        return self.com_handler.get_storage()

    def list_storage_pools(self, context):
        return self.com_handler.list_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.com_handler.list_volumes(self.storage_id)

    def list_alerts(self, context, query_para=None):
        raise NotImplementedError(
            "Driver API list_alerts() is not Implemented")

    def list_controllers(self, context):
        return self.com_handler.list_controllers(self.storage_id)

    def list_ports(self, context):
        return self.com_handler.list_ports(self.storage_id)

    def list_disks(self, context):
        return self.com_handler.list_disks(self.storage_id)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return AlertHandler.parse_alert(alert)

    def clear_alert(self, context, sequence_number):
        pass

    @staticmethod
    def get_access_url():
        return 'https://{ip}'

    def list_storage_host_initiators(self, context):
        return self.com_handler.list_storage_host_initiators(self.storage_id)

    def list_storage_hosts(self, context):
        return self.com_handler.list_storage_hosts(self.storage_id)

    def list_masking_views(self, context):
        return self.com_handler.list_masking_views(self.storage_id)

    def collect_perf_metrics(self, context, storage_id, resource_metrics,
                             start_time, end_time):
        return self.com_handler.collect_perf_metrics(storage_id,
                                                     resource_metrics,
                                                     start_time, end_time)

    @staticmethod
    def get_capabilities(context, filters=None):
        """Get capability of supported driver"""
        return {
            'is_historic': True,
            'resource_metrics': {
                constants.ResourceType.CONTROLLER: consts.CONTROLLER_CAP,
                constants.ResourceType.VOLUME: consts.VOLUME_CAP,
                constants.ResourceType.PORT: consts.PORT_CAP,
                constants.ResourceType.DISK: consts.DISK_CAP
            }
        }

    def get_latest_perf_timestamp(self, context):
        return self.com_handler.get_latest_perf_timestamp(self.storage_id)
