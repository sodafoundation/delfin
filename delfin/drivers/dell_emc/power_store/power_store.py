# Copyright 2022 The SODA Authors.
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
from delfin.common import constants
from delfin.drivers import driver
from oslo_log import log

from delfin.drivers.dell_emc.power_store import rest_handler, consts

LOG = log.getLogger(__name__)


class PowerStoreDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def get_storage(self, context):
        return self.rest_handler.get_storage(self.storage_id)

    def list_storage_pools(self, context):
        return self.rest_handler.get_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.rest_handler.get_volumes(self.storage_id)

    def list_alerts(self, context, query_para=None):
        return self.rest_handler.list_alerts(query_para)

    def clear_alert(self, context, alert):
        """
        PowerStore doesn't support clear alerts through API.
        :param context:
        :param alert:
        :return:
        """
        pass

    @staticmethod
    def parse_alert(context, alert):
        return rest_handler.RestHandler.get_parse_alerts(alert)

    def get_alert_sources(self, context):
        return self.rest_handler.get_alert_sources(self.storage_id)

    def list_controllers(self, context):
        return self.rest_handler.get_controllers(self.storage_id)

    def list_disks(self, context):
        return self.rest_handler.get_disks(self.storage_id)

    def list_ports(self, context):
        hardware_d = self.rest_handler.get_port_hardware()
        appliance_name_dict = self.rest_handler.get_appliance_name()
        ports = self.rest_handler.get_fc_ports(
            self.storage_id, hardware_d, appliance_name_dict)
        ports.extend(
            self.rest_handler.get_eth_ports(
                self.storage_id, hardware_d, appliance_name_dict))
        ports.extend(
            self.rest_handler.get_sas_ports(
                self.storage_id, hardware_d, appliance_name_dict))
        return ports

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.login()

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def get_access_url():
        return 'https://{ip}:{port}'

    def collect_perf_metrics(self, context, storage_id, resource_metrics,
                             start_time, end_time):
        LOG.info('The system(storage_id: %s) starts to collect powerstore '
                 'performance, start_time: %s, end_time: %s',
                 storage_id, start_time, end_time)
        metrics = []
        if resource_metrics.get(constants.ResourceType.STORAGE):
            storage_metrics = self.rest_handler.get_storage_metrics(
                storage_id,
                resource_metrics.get(constants.ResourceType.STORAGE),
                start_time, end_time)
            metrics.extend(storage_metrics)
            LOG.info('The system(storage_id: %s) stop to collect storage'
                     ' performance, The length is: %s',
                     storage_id, len(storage_metrics))
        if resource_metrics.get(constants.ResourceType.STORAGE_POOL):
            pool_metrics = self.rest_handler.get_pool_metrics(
                storage_id,
                resource_metrics.get(constants.ResourceType.STORAGE_POOL),
                start_time, end_time)
            metrics.extend(pool_metrics)
            LOG.info('The system(storage_id: %s) stop to collect pool'
                     ' performance, The length is: %s',
                     storage_id, len(pool_metrics))
        if resource_metrics.get(constants.ResourceType.VOLUME):
            volume_metrics = self.rest_handler.get_volume_metrics(
                storage_id,
                resource_metrics.get(constants.ResourceType.VOLUME),
                start_time, end_time)
            metrics.extend(volume_metrics)
            LOG.info('The system(storage_id: %s) stop to collect volume'
                     ' performance, The length is: %s',
                     storage_id, len(volume_metrics))
        if resource_metrics.get(constants.ResourceType.CONTROLLER):
            controller_metrics = self.rest_handler.get_controllers_metrics(
                storage_id,
                resource_metrics.get(constants.ResourceType.CONTROLLER),
                start_time, end_time)
            metrics.extend(controller_metrics)
            LOG.info('The system(storage_id: %s) stop to collect controller'
                     ' performance, The length is: %s',
                     storage_id, len(controller_metrics))
        if resource_metrics.get(constants.ResourceType.PORT):
            fc_port_metrics = self.rest_handler.get_fc_port_metrics(
                storage_id,
                resource_metrics.get(constants.ResourceType.PORT),
                start_time, end_time)
            metrics.extend(fc_port_metrics)
            LOG.info('The system(storage_id: %s) stop to collect port'
                     ' performance, The length is: %s',
                     storage_id, len(fc_port_metrics))
        if resource_metrics.get(constants.ResourceType.FILESYSTEM):
            file_system_metrics = self.rest_handler.get_file_system_metrics(
                storage_id,
                resource_metrics.get(constants.ResourceType.FILESYSTEM),
                start_time, end_time)
            metrics.extend(file_system_metrics)
            LOG.info('The system(storage_id: %s) stop to collect file_system '
                     'performance, The length is: %s',
                     storage_id, len(file_system_metrics))
        return metrics

    @staticmethod
    def get_capabilities(context, filters=None):
        return {
            'is_historic': True,
            'resource_metrics': {
                constants.ResourceType.STORAGE: consts.STORAGE_CAP,
                constants.ResourceType.STORAGE_POOL: consts.STORAGE_POOL_CAP,
                constants.ResourceType.VOLUME: consts.VOLUME_CAP,
                constants.ResourceType.CONTROLLER: consts.CONTROLLER_CAP,
                constants.ResourceType.PORT: consts.PORT_CAP,
                constants.ResourceType.FILESYSTEM: consts.FILE_SYSTEM_CAP
            }
        }

    def get_latest_perf_timestamp(self, context):
        return self.rest_handler.get_system_time()

    def list_storage_host_initiators(self, context):
        return self.rest_handler.list_storage_host_initiators(self.storage_id)

    def list_storage_hosts(self, context):
        return self.rest_handler.list_storage_hosts(self.storage_id)

    def list_storage_host_groups(self, context):
        return self.rest_handler.list_storage_host_groups(self.storage_id)

    def list_volume_groups(self, context):
        return self.rest_handler.list_volume_groups(self.storage_id)

    def list_masking_views(self, context):
        return self.rest_handler.list_masking_views(self.storage_id)

    def list_filesystems(self, context):
        return self.rest_handler.list_filesystems(self.storage_id)

    def list_quotas(self, context):
        return self.rest_handler.list_quotas(self.storage_id)

    def list_qtrees(self, context):
        return self.rest_handler.list_qtrees(self.storage_id)

    def list_shares(self, context):
        return self.rest_handler.list_shares(self.storage_id)
