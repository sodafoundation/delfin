import hashlib
import re
import threading

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.fujitsu.eternus import consts
from delfin.drivers.fujitsu.eternus.consts import DIGITAL_CONSTANT
from delfin.drivers.fujitsu.eternus.eternus_ssh_client import \
    EternusSSHPool
from delfin.drivers.utils.tools import Tools

LOG = log.getLogger(__name__)


class CliHandler(object):
    lock = None

    def __init__(self, **kwargs):
        self.lock = threading.RLock()
        self.kwargs = kwargs
        self.ssh_pool = EternusSSHPool(**kwargs)

    def login(self):
        """Test SSH connection """
        try:
            self.exec_command(consts.GET_STORAGE_STATUS)
        except Exception as e:
            error = six.text_type(e)
            LOG.error("Login error: %s", error)
            raise exception.SSHException(error)

    def exec_command(self, command):
        res = ''
        try:
            self.lock.acquire()
            res = self.ssh_pool.do_exec_shell([command])
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
        finally:
            self.lock.release()
        if res:
            if 'Error: ' in res:
                LOG.info(res)
                return None
            elif res.strip() in '^':
                LOG.info(res)
                return None
        return res

    def common_data_encapsulation(self, command):
        common_data_str = self.exec_command(command)
        common_data_dict = dict()
        if common_data_str:
            common_data_arr = common_data_str.split('\n')
            for common_data_row in common_data_arr:
                if '[' in common_data_row and ']' in common_data_row:
                    name_start_index = common_data_row.index('[')
                    name_end_index = common_data_row.index(']')
                    key = common_data_row[:name_start_index].strip()
                    value = common_data_row[name_start_index
                                            + 1:name_end_index]
                    common_data_dict[key] = value
        return common_data_dict

    def get_controllers(self):
        controller_data_str = self.exec_command(consts.GET_STORAGE_CONTROLLER)
        controller_info_list = []
        try:
            if controller_data_str:
                result_data_arr = controller_data_str.split('\n')
                controller_info_map = {}
                for common_data_row in result_data_arr:
                    row_pattern = re.compile(consts.CONTROLLER_NEWLINE_PATTERN)
                    row_search_obj = row_pattern.search(common_data_row)
                    if row_search_obj:
                        name = row_search_obj.group().split(' ')[0]
                        if controller_info_map:
                            controller_info_list.append(controller_info_map)
                            controller_info_map = {}
                        controller_info_map['name'] = name
                    pattern = re.compile(consts.COMMON_VALUE_PATTERN)
                    search_obj = pattern.search(common_data_row)
                    if search_obj:
                        self.analysis_data_to_map(common_data_row,
                                                  consts.COMMON_VALUE_PATTERN,
                                                  controller_info_map)
                if controller_info_map:
                    controller_info_list.append(controller_info_map)
        except Exception as e:
            err_msg = "get controller info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return controller_info_list

    def analysis_data_to_map(self, source_info, pattern_str, obj_map):
        """Get the contents in brackets through regular expressions.
           source_info：Source data, example: "Memory Size   [4.0GB]"
           pattern_str: regular expression. example："\\[.*\\]"
        """
        object_info = ''
        object_infos = re.findall(pattern_str, source_info)
        if object_infos:
            object_info = object_infos[0]
            key = source_info.replace(object_info, '').strip()
            value = object_info.replace('[', '').replace(']', '')
            obj_map[key] = value
        return object_info

    def get_pools(self, command):
        pool_data_str = self.exec_command(command)
        pool_info_list = []
        try:
            if pool_data_str:
                result_data_arr = pool_data_str.split('\n')
                titles = []
                for common_data_row in result_data_arr:
                    title_pattern = re.compile(consts.POOL_TITLE_PATTERN)
                    title_search_obj = title_pattern.search(common_data_row)
                    if title_search_obj:
                        titles = common_data_row.split(",")
                    else:
                        if common_data_row:
                            values = common_data_row.split(",")
                            if values:
                                if len(values) == len(titles):
                                    obj_model = {}
                                    for i in range(len(values)):
                                        key = titles[i].lower() \
                                            .replace(' ', '') \
                                            .replace('[', '') \
                                            .replace(']', '')
                                        obj_model[key] = values[i]
                                    if obj_model:
                                        pool_info_list.append(obj_model)
        except Exception as e:
            err_msg = "get pool info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return pool_info_list

    def get_volumes_type(self, volume_id_dict=None, command=None):
        if volume_id_dict is None:
            volume_id_dict = {}
        try:
            volumes_type_str = self.exec_command(command)
        except Exception as e:
            LOG.error("Get %s info error: %s" % (command, six.text_type(e)))
            return volume_id_dict
        if volumes_type_str:
            volumes_type_arr = volumes_type_str.split('\n')
            for row_num in range(DIGITAL_CONSTANT.THREE_INT,
                                 len(volumes_type_arr)):
                volume_type_dict = {}
                volumes_type_row_arr = volumes_type_arr[row_num].split()
                if not volumes_type_row_arr or \
                        consts.CLI_STR in volumes_type_row_arr:
                    continue
                volume_id = volumes_type_row_arr[DIGITAL_CONSTANT.ZERO_INT]
                volume_type = volumes_type_row_arr[
                    DIGITAL_CONSTANT.MINUS_SIX_INT]
                volume_type_dict['type'] = volume_type.lower() if \
                    volume_type else constants.VolumeType.THICK
                volume_type_dict['used_capacity'] = int(
                    volumes_type_row_arr[DIGITAL_CONSTANT.MINUS_ONE_INT])
                volume_id_dict[volume_id] = volume_type_dict
        return volume_id_dict

    def get_alerts(self, command, query_para, list_alert=None):
        if not list_alert:
            list_alert = []
        events_error_str = self.exec_command(command)
        if not events_error_str:
            return list_alert
        events_error_dict = self.get_event(events_error_str, query_para)
        for events_error_dict_values in events_error_dict.values():
            alerts_model = dict()
            description = events_error_dict_values.get('description')
            alerts_model['alert_id'] = events_error_dict_values.get('code')
            severity = events_error_dict_values.get('severity')
            alerts_model['severity'] = consts.SEVERITY_MAP.get(
                events_error_dict_values.get('severity'),
                constants.Severity.NOT_SPECIFIED)
            alerts_model['category'] = constants.Category.FAULT
            occur_time = events_error_dict_values.get('occur_time')
            alerts_model['occur_time'] = occur_time
            alerts_model['description'] = description
            alerts_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alerts_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alerts_model['alert_name'] = description
            alerts_model['match_key'] = hashlib.md5('{}{}{}'.format(
                occur_time, severity, description).encode()).hexdigest()
            list_alert.append(alerts_model)
        return list_alert

    @staticmethod
    def get_event(events_error_str, query_para):
        events_error_dict = dict()
        events_error_arr = events_error_str.split('\n')
        for events_error_row_str in events_error_arr:
            if events_error_row_str.strip() in consts.CLI_STR:
                continue
            error_description_dict = dict()
            time_stamp = Tools().time_str_to_timestamp(
                events_error_row_str[:consts.OCCUR_TIME_RANGE].strip(),
                consts.TIME_PATTERN)
            if query_para is not None:
                try:
                    if time_stamp is None or time_stamp \
                            < int(query_para.get('begin_time')) or \
                            time_stamp > int(query_para.get('end_time')):
                        continue
                except Exception as e:
                    LOG.error(e)
            severity = events_error_row_str[consts.SEVERITY_RANGE_BEGIN:
                                            consts.SEVERITY_RANGE_END].strip()
            code = events_error_row_str[consts.CODE_RANGE_BEGIN:
                                        consts.CODE_RANGE_END].strip()
            description = events_error_row_str[consts.DESCRIPTION_RANGE:] \
                .strip()
            key = '{}{}{}'.format(severity, code, description)
            if events_error_dict.get(key):
                continue
            error_description_dict['severity'] = severity
            error_description_dict['code'] = code
            error_description_dict['description'] = description
            error_description_dict['occur_time'] = time_stamp
            events_error_dict[key] = error_description_dict
        return events_error_dict

    def format_data(self, command, storage_id, method, is_port=False):
        data_info = self.exec_command(command)
        data_list = []
        if not data_info:
            return data_list
        try:
            data_array = data_info.split('\n')
            data_map = {}
            for data in data_array:
                if data:
                    temp_data = data.split('  ')
                    temp_data = list(
                        filter(lambda s: s and s.strip(), temp_data))
                    if len(temp_data) >= consts.DATA_VALUE_INDEX:
                        data_length = consts.DATA_VALUE_INDEX
                        if is_port:
                            data_length = len(temp_data)
                        for i in range(consts.DATA_KEY_INDEX, data_length):
                            key = temp_data[0].strip()
                            value = temp_data[i].replace('[', '').replace(']',
                                                                          '')
                            value = value.strip()
                            if data_map.get(i):
                                data_map[i][key] = value
                            else:
                                data_map[i] = {
                                    key: value
                                }
                if not data:
                    data_list.extend(method(data_map, storage_id))
                    data_map = {}
            if data_map:
                data_list.extend(method(data_map, storage_id))
        except Exception as e:
            err_msg = "Failed: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return data_list

    @staticmethod
    def format_fc_ports(port_map, storage_id):
        port_list = []
        for key in port_map:
            connection_status = \
                constants.PortConnectionStatus.CONNECTED
            health_status = constants.PortHealthStatus.NORMAL
            if port_map[key].get('Connection') != 'FC-AL' or 'Fabric':
                connection_status = \
                    constants.PortConnectionStatus.DISCONNECTED
                health_status = \
                    constants.PortHealthStatus.ABNORMAL
            speed = 0
            if port_map[key].get('Transfer Rate') and (
                    'Gbit/s' in port_map[key].get('Transfer Rate')):
                speed = port_map[key].get('Transfer Rate').split()[0]
                speed = int(speed) * units.G
            port_model = {
                'name': port_map[key].get('Port'),
                'storage_id': storage_id,
                'native_port_id':
                    '%s-%s' % (constants.PortType.FC,
                               port_map[key].get('Port')),
                'location': port_map[key].get('Port'),
                'connection_status': connection_status,
                'health_status': health_status,
                'type': constants.PortType.FC,
                'speed': speed,
                'wwn': port_map[key].get('WWPN'),
            }
            port_list.append(port_model)
        return port_list

    @staticmethod
    def format_fcoe_ports(port_map, storage_id):
        port_list = []
        for key in port_map:
            connection_status = \
                constants.PortConnectionStatus.CONNECTED
            health_status = constants.PortHealthStatus.NORMAL
            speed = None
            if 'Gbit/s' in port_map[key].get('Transfer Rate'):
                speed = port_map[key].get('Transfer Rate').replace('Gbit/s',
                                                                   '')
                speed = int(speed) * units.G
            port_model = {
                'name': port_map[key].get('Port'),
                'storage_id': storage_id,
                'native_port_id':
                    '%s-%s' % (constants.PortType.FCOE,
                               port_map[key].get('Port')),
                'connection_status': connection_status,
                'health_status': health_status,
                'type': constants.PortType.FCOE,
                'speed': speed,
                'mac_address': port_map[key].get('MAC Address')
            }
            port_list.append(port_model)
        return port_list

    @staticmethod
    def format_disks(disk_map, storage_id):
        disk_list = []
        for key in disk_map:
            speed = None
            if 'rpm' in disk_map[key].get('Speed'):
                speed = int(disk_map[key].get('Speed').replace('rpm', ''))
            size = Tools.get_capacity_size(disk_map[key].get('Size'))
            physical_type = constants.DiskPhysicalType.UNKNOWN
            if 'SSD' in disk_map[key].get('Type'):
                physical_type = consts.DiskPhysicalTypeMap['SSD']
            elif 'Nearline' in disk_map[key].get('Type'):
                physical_type = consts.DiskPhysicalTypeMap['Nearline']
            elif 'Online' in disk_map[key].get('Type'):
                physical_type = consts.DiskPhysicalTypeMap['Online']
            logical_type = \
                consts.DiskLogicalTypeMap.get(
                    disk_map[key].get('Usage'),
                    constants.DiskLogicalType.UNKNOWN
                )
            status = None
            if disk_map[key].get('Status').split('('):
                status = disk_map[key].get('Status').split('(')[0]
                status = \
                    consts.DISK_STATUS_MAP.get(
                        status.strip(),
                        constants.DiskStatus.OFFLINE)
            disk_model = {
                'name': disk_map[key].get('Location'),
                'storage_id': storage_id,
                'native_disk_id': disk_map[key].get('Location'),
                'serial_number': disk_map[key].get('Serial Number'),
                'manufacturer': disk_map[key].get('Vendor ID'),
                'model': disk_map[key].get('Type'),
                'firmware': disk_map[key].get('Firmware Revision'),
                'location': disk_map[key].get('Location'),
                'speed': speed,
                'capacity': size,
                'status': status,
                'physical_type': physical_type,
                'logical_type': logical_type
            }
            disk_list.append(disk_model)
        return disk_list

    def get_volumes_or_pool(self, command, str_pattern):
        data_str = self.exec_command(command)
        pool_info_list = []
        try:
            if data_str:
                result_data_arr = data_str.split('\n')
                titles = []
                for common_data_row in result_data_arr:
                    title_pattern = re.compile(str_pattern)
                    title_search_obj = title_pattern.search(common_data_row)
                    if title_search_obj:
                        titles = common_data_row.split(",")
                    else:
                        if common_data_row:
                            values = common_data_row.split(",")
                            if values:
                                if len(values) == len(titles):
                                    obj_model = {}
                                    for i in range(len(values)):
                                        key = titles[i].lower() \
                                            .replace(' ', '') \
                                            .replace('[', '') \
                                            .replace(']', '')
                                        obj_model[key] = values[i]
                                    if obj_model:
                                        pool_info_list.append(obj_model)
        except Exception as e:
            err_msg = "execution {}: error: {}".format(command,
                                                       six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return pool_info_list
