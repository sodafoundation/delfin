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

    # PowerStore doesn't support clear alerts through API.
    def clear_alert(self, context, alert):
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
        ports = self.rest_handler.get_fc_ports(self.storage_id, hardware_d)
        ports.extend(
            self.rest_handler.get_eth_ports(self.storage_id, hardware_d))
        ports.extend(
            self.rest_handler.get_sas_ports(self.storage_id, hardware_d))
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
        LOG.info('The system(storage_id: %s) starts to collect performance,'
                 ' start_time: %s, end_time: %s',
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
                constants.ResourceType.PORT: consts.PORT_CAP
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

    def list_quotas(self, context):
        return []

    def list_filesystems(self, context):
        return []

    def list_qtrees(self, context):
        return []

    def list_shares(self, context):
        return []
