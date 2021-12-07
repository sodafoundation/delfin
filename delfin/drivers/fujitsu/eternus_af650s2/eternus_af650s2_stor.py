import six
from oslo_log import log
from oslo_utils import units

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.fujitsu.eternus_af650s2 import cli_handler, consts
from delfin.drivers.fujitsu.eternus_af650s2.consts import DIGITAL_CONSTANT
from delfin.drivers.utils.tools import Tools

LOG = log.getLogger(__name__)


class EternusAf650s2Driver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cli_handler = cli_handler.CliHandler(**kwargs)
        self.login = self.cli_handler.login()

    def list_volumes(self, context):
        volumes = []
        volume_id_dict = self.cli_handler.get_volumes_type(
            command=consts.GET_LIST_VOLUMES_TYPE_TPV)
        volume_id_dict = self.cli_handler.get_volumes_type(
            volume_id_dict, consts.GET_LIST_VOLUMES_TYPE_FTV)
        volumes_str = self.cli_handler.exec_command(consts.GET_LIST_VOLUMES)
        volumes_arr = volumes_str.split('\n')
        for row_num in range(DIGITAL_CONSTANT.THREE_INT, len(volumes_arr)):
            volumes_row_arr = volumes_arr[row_num].split()
            if volumes_row_arr:
                volume_name = volumes_row_arr[consts.VOLUME_NAME_COUNT]
                volume_status = volumes_row_arr[consts.VOLUME_STATUS_COUNT]
                volume_native_volume_id = volumes_row_arr[
                    consts.VOLUME_ID_COUNT]
                native_storage_pool_id = volumes_row_arr[
                    consts.NATIVE_STORAGE_POOL_ID_COUNT]
                total_capacity = int(
                    volumes_row_arr[consts.TOTAL_CAPACITY_COUNT]) * units.Mi
                type_capacity = volume_id_dict.get(volume_native_volume_id, {})
                volume_type = type_capacity.get('type',
                                                constants.VolumeType.THICK)
                used_capacity = type_capacity.get('used_capacity',
                                                  DIGITAL_CONSTANT.ZERO_INT)
                volume = {
                    'name': volume_name,
                    'storage_id': self.storage_id,
                    'status': consts.LIST_VOLUMES_STATUS_MAP.get(
                        volume_status),
                    'native_volume_id': volume_native_volume_id,
                    'native_storage_pool_id': native_storage_pool_id,
                    'type': volume_type,
                    'total_capacity': total_capacity,
                    'used_capacity': used_capacity,
                    'free_capacity': total_capacity - used_capacity
                }
                volumes.append(volume)
        return volumes

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        pass

    def get_storage(self, context):
        storage_name_dict = self.cli_handler.common_data_encapsulation(
            consts.GET_STORAGE_NAME)
        storage_name = storage_name_dict.get('Name')
        storage_description = storage_name_dict.get('Description')
        storage_location = storage_name_dict.get('Installation Site')

        enclosure_status = self.cli_handler.common_data_encapsulation(
            consts.GET_ENCLOSURE_STATUS)
        storage_model = enclosure_status.get('Model Name')
        storage_serial_number = enclosure_status.get('Serial Number')
        storage_firmware_version = enclosure_status.get('Firmware Version')

        storage_status_dict = self.cli_handler.common_data_encapsulation(
            consts.GET_STORAGE_STATUS)
        storage_status = consts.STORAGE_STATUS_MAP.get(
            storage_status_dict.get('Summary Status'))

        raw_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        list_disks = self.list_disks(context)
        if list_disks:
            for disks in list_disks:
                raw_capacity += disks.get('capacity',
                                          consts.DIGITAL_CONSTANT.ZERO_INT)
        total_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        used_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        free_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        list_storage_pools = self.list_storage_pools(context)
        if list_storage_pools:
            for pools in list_storage_pools:
                total_capacity += pools.get('total_capacity')
                used_capacity += pools.get('used_capacity')
                free_capacity += pools.get('free_capacity')
        storage = {
            'name': storage_name,
            'vendor': consts.GET_STORAGE_VENDOR,
            'description': storage_description,
            'model': storage_model,
            'status': storage_status,
            'serial_number': storage_serial_number,
            'firmware_version': storage_firmware_version,
            'location': storage_location,
            'raw_capacity': raw_capacity,
            'total_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': free_capacity
        }
        return storage

    def list_controllers(self, context):
        controllers = self.cli_handler.get_controllers()
        controllers_status = self.cli_handler.common_data_encapsulation(
            consts.GET_STORAGE_CONTROLLER_STATUS)
        controller_list = []
        for controller in (controllers or []):
            name = controller.get('name')
            status = constants.ControllerStatus.FAULT
            if controllers_status and controllers_status.get(name):
                status_value = controllers_status.get(name)
                if status_value and \
                        consts.CONTROLLER_STATUS_NORMAL_KEY in status_value:
                    status = constants.ControllerStatus.NORMAL
            controller_model = {
                'name': controller.get('name'),
                'storage_id': self.storage_id,
                'native_controller_id': controller.get('Serial Number'),
                'status': status,
                'location': controller.get('name'),
                'soft_version': controller.get('Hard Revision'),
                'cpu_info': controller.get('CPU Clock'),
                'memory_size': str(int(
                    Tools.get_capacity_size(controller.get('Memory Size'))))
            }
            controller_list.append(controller_model)
        return controller_list

    def list_disks(self, context):
        try:
            disk_list = \
                self.cli_handler.format_data(
                    consts.GET_DISK_COMMAND,
                    self.storage_id,
                    self.cli_handler.format_disks,
                    False)
            return disk_list
        except Exception as e:
            LOG.error("Failed to get disk from fujitsu eternus %s" %
                      (six.text_type(e)))
            raise e

    def list_ports(self, context):
        try:
            port_list = \
                self.cli_handler.format_data(
                    consts.GET_PORT_COMMAND,
                    self.storage_id,
                    self.cli_handler.format_fc_ports,
                    True)
            port_list.extend(self.cli_handler.format_data(
                consts.GET_PORT_COMMAND,
                self.storage_id,
                self.cli_handler.format_fcoe_ports,
                True))
            return port_list
        except Exception as e:
            LOG.error("Failed to get ports from fujitsu eternus %s" %
                      (six.text_type(e)))
            raise e

    def list_storage_pools(self, context):
        pools = self.cli_handler.get_pools()
        pool_list = []
        for pool in (pools or []):
            free_cap = float(
                pool.get("freecapacity(mb)")) * units.Mi
            total_cap = float(
                pool.get("totalcapacity(mb)")) * units.Mi
            used_cap = total_cap - free_cap
            status = consts.STORAGE_POOL_STATUS_MAP.get(
                pool.get('status'),
                constants.StoragePoolStatus.ABNORMAL)
            pool_model = {
                'name': pool.get('raidgroupname'),
                'storage_id': self.storage_id,
                'native_storage_pool_id': str(pool.get('raidgroupno.')),
                'status': status,
                'storage_type': constants.StorageType.BLOCK,
                'total_capacity': int(total_cap),
                'used_capacity': int(used_cap),
                'free_capacity': int(free_cap)
            }
            pool_list.append(pool_model)
        return pool_list

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        pass

    def list_quotas(self, context):
        pass

    def list_filesystems(self, context):
        pass

    def list_qtrees(self, context):
        pass

    def list_shares(self, context):
        pass

    def list_alerts(self, context, query_para=None):
        list_alert = self.cli_handler.get_alerts(
            consts.SHOW_EVENTS_SEVERITY_WARNING, query_para)
        list_alert = self.cli_handler.get_alerts(
            consts.SHOW_EVENTS_SEVERITY_ERROR, query_para, list_alert)
        return list_alert

    @staticmethod
    def parse_alert(context, alert):
        pass
