import hashlib

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception, utils
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.fujitsu.eternus import cli_handler, consts
from delfin.drivers.fujitsu.eternus.consts import DIGITAL_CONSTANT
from delfin.drivers.utils.tools import Tools
from delfin.i18n import _

LOG = log.getLogger(__name__)


class EternusDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cli_handler = cli_handler.CliHandler(**kwargs)
        self.login = self.cli_handler.login()

    def list_volumes(self, context):
        list_volumes = self.get_volumes()
        if not list_volumes:
            list_volumes = self.get_volumes_old()
        return list_volumes

    def get_volumes(self):
        list_volumes = []
        volumes = self.cli_handler.get_volumes_or_pool(
            consts.GET_LIST_VOLUMES_CSV, consts.VOLUME_TITLE_PATTERN)
        volume_id_dict = self.cli_handler.get_volumes_type(
            command=consts.GET_LIST_VOLUMES_TYPE_TPV)
        volume_id_dict = self.cli_handler.get_volumes_type(
            volume_id_dict, consts.GET_LIST_VOLUMES_TYPE_TPV)
        for volume_dict in (volumes or []):
            volume_native_volume_id = volume_dict.get('volumeno.')
            total_capacity = int(
                volume_dict.get('size(mb)')) * units.Mi
            volume_type = constants.VolumeType.THICK
            used_capacity = DIGITAL_CONSTANT.ZERO_INT
            if volume_dict.get('type'):
                type_capacity = volume_id_dict.get(volume_native_volume_id, {})
                volume_type = type_capacity.get('type',
                                                constants.VolumeType.THICK)
                used_capacity = type_capacity.get('used_capacity',
                                                  DIGITAL_CONSTANT.ZERO_INT)
            volume = {
                'name': volume_dict.get('volumename'),
                'storage_id': self.storage_id,
                'status': consts.LIST_VOLUMES_STATUS_MAP.get(
                    volume_dict.get('status')),
                'native_volume_id': volume_native_volume_id,
                'native_storage_pool_id': volume_dict.get('rgortpporftrpno.'),
                'type': volume_type,
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'free_capacity': total_capacity - used_capacity
            }
            list_volumes.append(volume)
        return list_volumes

    def get_volumes_old(self):
        list_volumes = []
        volumes_str = self.cli_handler.exec_command(consts.GET_LIST_VOLUMES)
        volumes_arr = volumes_str.split('\n')
        if len(volumes_arr) < consts.VOLUMES_LENGTH:
            return list_volumes
        for volumes_num in range(consts.VOLUMES_CYCLE, len(volumes_arr)):
            volumes_row_str = volumes_arr[volumes_num]
            if not volumes_row_str or \
                    consts.CLI_STR in volumes_row_str.strip():
                continue
            volumes_row_arr = volumes_row_str.split()
            volume_id = volumes_row_arr[consts.VOLUME_ID_COUNT]
            volume_name = volumes_row_arr[consts.VOLUME_NAME_COUNT]
            volume_status = volumes_row_arr[consts.VOLUME_STATUS_COUNT]
            volume_type = volumes_row_arr[consts.VOLUME_TYPE_COUNT]
            pool_id = volumes_row_arr[consts.NATIVE_STORAGE_POOL_ID_COUNT]
            total_capacity = volumes_row_arr[consts.TOTAL_CAPACITY_COUNT]
            volume_results = {
                'name': volume_name,
                'storage_id': self.storage_id,
                'status': consts.LIST_VOLUMES_STATUS_MAP.get(
                    volume_status),
                'native_volume_id': volume_id,
                'native_storage_pool_id': pool_id,
                'type': constants.VolumeType.THIN if
                volume_type and consts.VOLUME_TYPE_OPEN in volume_type else
                constants.VolumeType.THICK,
                'total_capacity': int(total_capacity) * units.Mi,
                'used_capacity': consts.DEFAULT_USED_CAPACITY,
                'free_capacity': consts.DEFAULT_FREE_CAPACITY
            }
            list_volumes.append(volume_results)
        return list_volumes

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
            error = six.text_type(e)
            LOG.error("Failed to get disk from fujitsu eternus %s" % error)
            raise exception.InvalidResults(error)

    def list_ports(self, context):
        port_list = self.cli_handler.format_data(
            consts.GET_PORT_FC_PARAMETERS, self.storage_id,
            self.cli_handler.format_fc_ports, True)
        ports_status = self.cli_handler.get_ports_status()
        for port in port_list:
            name = port.get('name')
            status_dict = ports_status.get(name, {})
            if status_dict:
                link_status = status_dict.get('Link Status')
                connection_status = constants.PortConnectionStatus.UNKNOWN
                if 'Gbit/s' in link_status:
                    reality = link_status.split()[0].replace('Gbit/s', '')
                    speed = int(reality) * units.G
                    port['speed'] = speed
                if 'Link Up' in link_status:
                    connection_status =\
                        constants.PortConnectionStatus.CONNECTED
                if 'Link Down' in link_status:
                    connection_status =\
                        constants.PortConnectionStatus.DISCONNECTED

                status_keys = status_dict.keys()
                status_dicts = {}
                for status_key in status_keys:
                    if status_key and 'Status/Status Code' in status_key:
                        status_dicts['Status/Status Code'] = status_dict.get(
                            status_key)
                    if status_key and status_key in 'Port WWN':
                        status_dicts['WWN'] = status_dict.get(status_key)
                status = status_dicts.get('Status/Status Code')
                health_status = constants.PortHealthStatus.UNKNOWN
                if 'Normal' in status or 'normal' in status:
                    health_status = constants.PortHealthStatus.NORMAL
                elif 'Unconnected' in status or 'unconnected' in status:
                    health_status = constants.PortHealthStatus.ABNORMAL
                port['connection_status'] = connection_status
                port['wwn'] = status_dicts.get('WWN')
                port['health_status'] = health_status
        return port_list

    def list_storage_pools(self, context):
        pool_list = self.get_list_pools()
        if not pool_list:
            pool_list = self.get_list_pools_old(pool_list)
        return pool_list

    def get_list_pools_old(self, pool_list):
        pools_str = self.cli_handler.exec_command(consts.GET_STORAGE_POOL)
        if not pools_str:
            return pool_list
        pools_row_str = pools_str.split('\n')
        if len(pools_row_str) < consts.POOL_LENGTH:
            return pool_list
        for pools_row_num in range(consts.POOL_CYCLE, len(pools_row_str)):
            pools_row_arr = pools_row_str[pools_row_num].strip()
            if pools_row_arr in consts.CLI_STR or \
                    pools_row_arr in consts.SPECIAL_CHARACTERS_ONE:
                continue
            pools_arr = pools_row_arr.split()
            pool_id = pools_arr[consts.POOL_ID_COUNT]
            pool_name = pools_arr[consts.POOL_NAME_COUNT]
            pool_status = consts.STORAGE_POOL_STATUS_MAP.get(
                pools_arr[consts.POOL_STATUS_COUNT],
                constants.StoragePoolStatus.ABNORMAL)
            try:
                total_capacity = int(
                    pools_arr[consts.POOL_TOTAL_CAPACITY_COUNT]) * units.Mi
                free_capacity = int(
                    pools_arr[consts.POOL_FREE_CAPACITY_COUNT]) * units.Mi
            except Exception as e:
                LOG.info('Conversion digital exception:%s' % six.text_type(e))
                return pool_list
            pool_model = {
                'name': pool_name,
                'storage_id': self.storage_id,
                'native_storage_pool_id': str(pool_id),
                'status': pool_status,
                'storage_type': constants.StorageType.BLOCK,
                'total_capacity': total_capacity,
                'used_capacity': total_capacity - free_capacity,
                'free_capacity': free_capacity
            }
            pool_list.append(pool_model)
        return pool_list

    def get_list_pools(self):
        pool_list = []
        pools = self.cli_handler.get_volumes_or_pool(
            consts.GET_STORAGE_POOL_CSV, consts.POOL_TITLE_PATTERN)
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

    def list_alerts(self, context, query_para=None):
        list_alert = self.cli_handler.get_alerts(
            consts.SHOW_EVENTS_SEVERITY_WARNING, query_para)
        list_alert = self.cli_handler.get_alerts(
            consts.SHOW_EVENTS_SEVERITY_ERROR, query_para, list_alert)
        if not list_alert:
            list_alert = self.cli_handler.get_alerts(
                consts.SHOW_EVENTS_LEVEL_WARNING, query_para)
            list_alert = self.cli_handler.get_alerts(
                consts.SHOW_EVENTS_LEVEL_ERROR, query_para, list_alert)
        return list_alert

    @staticmethod
    def parse_alert(context, alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = alert.get(consts.PARSE_ALERT_ALERT_ID)
            alert_model['severity'] = consts.PARSE_ALERT_SEVERITY_MAP.get(
                alert.get(consts.PARSE_ALERT_SEVERITY),
                constants.Severity.NOT_SPECIFIED)
            alert_model['category'] = constants.Category.FAULT
            alert_model['occur_time'] = utils.utcnow_ms()
            alert_model['description'] = alert.get(
                consts.PARSE_ALERT_DESCRIPTION)
            alert_model['location'] = '{}{}'.format(alert.get(
                consts.PARSE_ALERT_LOCATION),
                alert.get(consts.PARSE_ALERT_COMPONENT))
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['alert_name'] = alert.get(
                consts.PARSE_ALERT_DESCRIPTION)
            alert_model['match_key'] = hashlib.md5(str(alert.get(
                consts.PARSE_ALERT_ALERT_ID)).encode()).hexdigest()
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing"))
            raise exception.InvalidResults(msg)

    @staticmethod
    def get_access_url():
        return 'https://{ip}'
