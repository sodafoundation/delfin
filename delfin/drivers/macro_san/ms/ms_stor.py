# Copyright 2022 The SODA Authors.
# Copyright (c) 2022 Huawei Technologies Co., Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from oslo_log import log
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.macro_san.ms import ms_handler, consts
from delfin.drivers.macro_san.ms.ms_handler import MsHandler

LOG = log.getLogger(__name__)


class MacroSanDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ms_handler = ms_handler.MsHandler(**kwargs)
        self.login = self.ms_handler.login()

    def get_storage(self, context):
        return self.ms_handler.get_storage(self.storage_id)

    def list_storage_pools(self, context):
        return self.ms_handler.list_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.ms_handler.list_volumes(self.storage_id)

    def list_controllers(self, context):
        return self.ms_handler.list_controllers(self.storage_id)

    def list_disks(self, context):
        return self.ms_handler.list_disks(self.storage_id)

    def list_ports(self, context):
        return self.ms_handler.list_ports(self.storage_id)

    def list_alerts(self, context, query_para=None):
        raise NotImplementedError(
            "Macro_SAN Driver SSH list_alerts() is not Implemented")

    @staticmethod
    def parse_alert(context, alert):
        return MsHandler.parse_alert(alert)

    def clear_alert(self, context, alert):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        pass

    def collect_perf_metrics(self, context, storage_id,
                             resource_metrics, start_time, end_time):
        return self.ms_handler.collect_perf_metrics(
            self.storage_id, resource_metrics, start_time, end_time)

    @staticmethod
    def get_capabilities(context, filters=None):
        return {
            'is_historic': True,
            'resource_metrics': {
                constants.ResourceType.STORAGE: consts.STORAGE_CAP,
                constants.ResourceType.VOLUME: consts.VOLUME_CAP,
                constants.ResourceType.STORAGE_POOL: consts.POOL_CAP,
                constants.ResourceType.PORT: consts.PORT_CAP,
                constants.ResourceType.DISK: consts.DISK_CAP,
            }
        }

    def get_latest_perf_timestamp(self, context):
        return self.ms_handler.get_latest_perf_timestamp()

    def list_storage_host_initiators(self, context):
        return self.ms_handler.list_storage_host_initiators(self.storage_id)

    def list_storage_hosts(self, context):
        host_list = self.ms_handler.list_storage_hosts_new(self.storage_id)
        if not host_list:
            host_list = self.ms_handler.list_storage_hosts_old(self.storage_id)
        return host_list

    def list_storage_host_groups(self, context):
        return self.ms_handler.list_storage_host_groups(self.storage_id)

    def list_volume_groups(self, context):
        return self.ms_handler.list_volume_groups(self.storage_id)

    def list_masking_views(self, context):
        views = self.ms_handler.list_masking_views_new(self.storage_id)
        if not views:
            views = self.ms_handler.list_masking_views_old(self.storage_id)
        return views
