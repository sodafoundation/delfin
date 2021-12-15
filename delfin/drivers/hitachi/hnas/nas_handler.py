# Copyright 2021 The SODA Authors.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WarrayANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import hashlib
import time

import eventlet
import six

from oslo_log import log as logging

from oslo_utils import units
from delfin import exception, utils
from delfin.common import constants
from delfin.drivers.utils import ssh_client
from delfin.drivers.hitachi.hnas import constants as constant
from delfin.drivers.utils.tools import Tools

LOG = logging.getLogger(__name__)


class NasHandler(object):

    def __init__(self, **kwargs):
        self.ssh_pool = ssh_client.SSHPool(**kwargs)
        self.evs_list = []

    def ssh_do_exec(self, command_list):
        res = None
        with eventlet.Timeout(60, False):
            res = self.ssh_pool.do_exec_shell(command_list)
            while 'Failed to establish SSC connection' in res:
                res = self.ssh_pool.do_exec_shell(command_list)
        if res:
            return res
        else:
            raise exception.\
                ConnectTimeout('Failed to establish SSC connection')

    def login(self):
        try:
            result = self.ssh_do_exec(['cluster-show -y'])
            if 'EVS' not in result:
                raise exception.InvalidIpOrPort()
        except Exception as e:
            LOG.error("Failed to login hnas %s" %
                      (six.text_type(e)))
            raise e

    @staticmethod
    def format_data_to_map(
            value_info,
            value_key,
            line='\r\n',
            split=":",
            split_key=None):
        map_list = []
        detail_array = value_info.split(line)
        value_map = {}
        for detail in detail_array:
            if detail:
                string_info = detail.split(split)
                key = string_info[0].replace(' ', '')
                value = ''
                if len(string_info) > 1:
                    for string in string_info[1:]:
                        value += string.\
                            replace('""', '').\
                            replace('\'', '').\
                            replace(' ', '')
                if value_map.get(key):
                    value_map[key + '1'] = value
                else:
                    value_map[key] = value
            else:
                if value_key in value_map:
                    map_list.append(value_map)
                value_map = {}
            if split_key and split_key in detail:
                if value_key in value_map:
                    map_list.append(value_map)
                value_map = {}
        if value_key in value_map:
            map_list.append(value_map)
        return map_list

    @staticmethod
    def get_table_data(values, is_alert=False):
        header_index = 0
        table = values.split('\r\n')
        for i in range(len(table)):
            if constant.DATA_HEAD_PATTERN.search(table[i]):
                header_index = i
            if is_alert and constant.ALERT_HEAD_PATTERN.search(table[i]):
                header_index = i
                return table[(header_index + 1):]
        return table[(header_index + 1):]

    def format_storage_info(self, storage_map_list,
                            model_map_list, version_map_list,
                            location_map_list, serial_map_list):
        if not storage_map_list:
            raise exception.StorageBackendException(
                'Failed to get HNAS storage')
        model_map = model_map_list[-1] if model_map_list else {}
        model = model_map.get('Model')
        model = model.replace('HNAS', 'HNAS ')
        version_map = version_map_list[-1] if version_map_list else {}
        location_map = location_map_list[-1] if location_map_list else {}
        serial_map = serial_map_list[-1] if serial_map_list else {}
        version = version_map.get("Software").split('(')
        serial_number = serial_map.get("Hardware").split('(')[-1]
        storage_map = storage_map_list[-1]
        disk_list = self.get_disk(None)
        total_capacity = \
            raw_capacity = \
            used_capacity = \
            free_capacity = 0
        for disk in disk_list:
            raw_capacity += disk['capacity']
        status = \
            constant.CLUSTER_STATUS.get(storage_map['ClusterHealth'])
        pool_list = self.get_pool(None)
        for pool in pool_list:
            total_capacity += pool['total_capacity']
            used_capacity += pool['used_capacity']
            free_capacity += pool['free_capacity']
        storage_model = {
            "name": storage_map['ClusterName'],
            "vendor": constant.STORAGE_VENDOR,
            "model": model,
            "status": status,
            "serial_number": serial_number.replace(')', ''),
            "firmware_version": version[0],
            "location": location_map['Location'],
            "total_capacity": total_capacity,
            "raw_capacity": raw_capacity,
            "used_capacity": used_capacity,
            "free_capacity": free_capacity
        }
        return storage_model

    def get_storage(self):
        try:
            storage_info = self.ssh_do_exec([constant.STORAGE_INFO_COMMAND])
            model_info = self.ssh_do_exec([constant.STORAGE_MODEL_COMMAND])
            location_info = self.ssh_do_exec(([constant.LOCATION_COMMAND]))
            model_map_list = \
                self.format_data_to_map(model_info, 'Model')
            storage_map_list = \
                self.format_data_to_map(
                    storage_info, 'ClusterName', split="=")
            version_map_list = \
                self.format_data_to_map(model_info, 'Software')
            location_map_list = \
                self.format_data_to_map(location_info, 'Location')
            serial_map_list =\
                self.format_data_to_map(model_info, 'Hardware')
            storage_model = \
                self.format_storage_info(
                    storage_map_list, model_map_list, version_map_list,
                    location_map_list, serial_map_list)
            return storage_model
        except exception.DelfinException as e:
            err_msg = "Failed to get storage from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_disk(self, storage_id):
        try:
            disk_info = self.ssh_do_exec([constant.DISK_INFO_COMMAND])
            disk_map_list = \
                self.format_data_to_map(disk_info, 'Capacity')
            disks_list = []
            for disk_map in disk_map_list:
                if 'Status' in disk_map:
                    size = disk_map['Capacity'].split('GiB')[0] + "GB"
                    status = constants.DiskStatus.NORMAL \
                        if disk_map['Status'] == 'OK' \
                        else constants.DiskStatus.ABNORMAL
                    disk_type = disk_map['Type']
                    type_array = disk_type.split(';')
                    model = vendor = version = None
                    if len(type_array) > constant.DISK_INDEX['type_len']:
                        model = \
                            type_array[constant.DISK_INDEX[
                                'model_index']].replace('Model', '')
                        vendor = \
                            type_array[constant.DISK_INDEX[
                                'vendor_index']].replace('Make', '')
                        version = \
                            type_array[constant.DISK_INDEX[
                                'version_index']].replace('Revision', '')
                    pool_id = disk_map.get('Usedinspan')
                    serial_number = disk_map['Luid'].split(']')[-1]
                    if pool_id:
                        pool_id = pool_id.split('(')[0]
                    disk_model = {
                        'name': disk_map['HDSdevname'],
                        'storage_id': storage_id,
                        'native_disk_id': disk_map['DeviceID'],
                        'serial_number': serial_number,
                        'manufacturer': vendor,
                        'model': model,
                        'firmware': version,
                        'capacity': int(Tools.get_capacity_size(size)),
                        'status': status,
                        'native_disk_group_id': pool_id
                    }
                    disks_list.append(disk_model)
            return disks_list
        except exception.DelfinException as e:
            err_msg = "Failed to get disk from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get disk from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_pool_size(self):
        size_info = self.ssh_do_exec([constant.POOL_SIZE_COMMAND])
        size_array = size_info.split('\r\n')
        size_map = {}
        pool_name = None
        for size in size_array:
            if 'Span ' in size:
                pool_name = size.split()[-1].replace(':', '')
                size_map[pool_name] = 0
            if '[Free space]' in size:
                free_array = size.split()
                if len(free_array) > 2:
                    free_size = free_array[0].replace('GiB', 'GB')
                    size_map[pool_name] += Tools.get_capacity_size(free_size)
        return size_map

    def get_pool(self, storage_id):
        try:
            pool_info = self.ssh_do_exec([constant.POOL_INFO_COMMAND])
            pool_list = []
            pool_array = self.get_table_data(pool_info)
            size_map = self.get_pool_size()
            for pool in pool_array:
                value_array = pool.split()
                if len(value_array) == constant.POOL_INDEX['pool_len']:
                    total_capacity = \
                        Tools.get_capacity_size(
                            value_array[constant.POOL_INDEX['total_index']] +
                            'GB')
                    free_capacity = \
                        size_map.get(
                            value_array[constant.POOL_INDEX['free_index']],
                            total_capacity)
                    status = constants.StoragePoolStatus.NORMAL \
                        if value_array[
                            constant.POOL_INDEX['status_index']] == 'Yes' \
                        else constants.StoragePoolStatus.ABNORMAL
                    pool_model = {
                        'name': value_array[constant.POOL_INDEX['name_index']],
                        'storage_id': storage_id,
                        'native_storage_pool_id': value_array[
                            constant.POOL_INDEX['name_index']],
                        'status': status,
                        'storage_type': constants.StorageType.FILE,
                        'total_capacity': total_capacity,
                        'used_capacity': total_capacity - free_capacity,
                        'free_capacity': free_capacity,
                    }
                    pool_list.append(pool_model)
            return pool_list
        except exception.DelfinException as e:
            err_msg = "Failed to get pool from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get pool from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_controllers(self, storage_id):
        try:
            controller_list = []
            node_info = self.ssh_do_exec([constant.CONTROLLER_INFO_COMMAND])
            nodes_array = self.get_table_data(node_info)
            for nodes in nodes_array:
                node = nodes.split()
                if len(node) > constant.NODE_INDEX['node_len']:
                    status = constants.ControllerStatus.NORMAL \
                        if node[
                            constant.NODE_INDEX[
                                'status_index']] == 'ONLINE' \
                        else constants.ControllerStatus.OFFLINE
                    controller_model = {
                        'name': node[constant.NODE_INDEX['name_index']],
                        'storage_id': storage_id,
                        'native_controller_id': node[
                            constant.NODE_INDEX['id_index']],
                        'status': status
                    }
                    controller_list.append(controller_model)
            return controller_list
        except exception.DelfinException as e:
            err_msg = "Failed to get controllers from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get controllers from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def format_alert_list(alert_array, query_para):
        alert_list = []
        alert_model = {}
        for alert in alert_array:
            if alert and 'CAUSE' not in alert:
                alert_data = alert.split()
                if len(alert_data) > constant.ALERT_INDEX['alert_len'] \
                        and alert_data[
                    constant.ALERT_INDEX['severity_index']] \
                        in constant.SEVERITY_MAP:
                    occur_time = \
                        alert_data[constant.ALERT_INDEX['year_index']] + \
                        ' ' + alert_data[constant.ALERT_INDEX[
                            'time_index']].split("+")[0]
                    occur_time = \
                        int(time.mktime(time.strptime(
                            occur_time, constant.TIME_TYPE))) * 1000
                    if not query_para or \
                            (int(query_para['begin_time'])
                             <= occur_time
                             <= int(query_para['end_time'])):
                        description = ''
                        for i in range(4, len(alert_data)):
                            description += alert_data[i] + ' '
                        severity = \
                            constant.SEVERITY_MAP.get(
                                alert_data[constant.ALERT_INDEX[
                                    'severity_index']])
                        alert_model['alert_id'] = \
                            alert_data[constant.ALERT_INDEX['id_index']]
                        alert_model['alert_name'] = \
                            alert_data[constant.ALERT_INDEX['id_index']]
                        alert_model['severity'] = severity
                        alert_model['category'] = constants.Category.FAULT
                        alert_model['type'] = \
                            constants.EventType.EQUIPMENT_ALARM
                        alert_model['occur_time'] = occur_time
                        alert_model['description'] = description.lstrip()
                        alert_model['match_key'] = \
                            hashlib.md5(
                                (alert_data[constant.ALERT_INDEX['id_index']]
                                    + severity
                                    + description).encode()).hexdigest()
                        alert_model['resource_type'] = \
                            constants.DEFAULT_RESOURCE_TYPE
            if alert and alert_model and 'CAUSE' in alert:
                alert_data = alert.split(':')
                alert_model['location'] = alert_data[-1]
            if not alert:
                alert_list.append(alert_model)
                alert_model = {}
        return alert_list

    def list_alerts(self, query_para):
        try:
            command = constant.ALERT_INFO_COMMAND
            if query_para and 'begin_time' in query_para:
                timeArray = time.gmtime(int(query_para['begin_time']) / 1000)
                begin_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                command += constant.ALERT_TIME % begin_time
            alert_info = self.ssh_do_exec([command])
            alert_array = self.get_table_data(alert_info, True)
            alert_list = self.format_alert_list(alert_array, query_para)
            alert_list = \
                sorted(alert_list,
                       key=lambda x: x['occur_time'], reverse=True)
            return alert_list
        except exception.DelfinException as e:
            err_msg = "Failed to get alerts from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get alerts from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def parse_alert(alert):
        try:
            alert_info = alert.get(constant.OID_TRAP_DATA)
            alert_array = alert_info.split(':')
            if len(alert_array) > 1:
                description = alert_array[1]
                alert = alert_array[0].split()
                if len(alert) > 1:
                    alert_id = alert[0]
                    severity = constant.SEVERITY_MAP.get(alert[1])
                    if severity == constant.SEVERITY_MAP.get('Information'):
                        return
                    alert_model = {
                        'alert_id': alert_id,
                        'alert_name': alert_id,
                        'severity': severity,
                        'category': constants.Category.FAULT,
                        'type': constants.EventType.EQUIPMENT_ALARM,
                        'occur_time': utils.utcnow_ms(),
                        'description': description,
                        'match_key': hashlib.md5(
                            (alert_id + severity +
                             description).encode()).hexdigest(),
                        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                        'location': ''
                    }
                    return alert_model
        except exception.DelfinException as e:
            err_msg = "Failed to parse alert from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to parse alert from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_ports(self, storage_id):
        try:
            ports_list = self.get_fc_port(storage_id)
            return ports_list
        except exception.DelfinException as e:
            err_msg = "Failed to get ports from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get ports from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_fc_port(self, storage_id):
        try:
            fc_info = self.ssh_do_exec([constant.FC_PORT_COMMAND])
            fc_map_list = \
                self.format_data_to_map(fc_info, 'Portname')
            fc_list = []
            speed_info = self.ssh_do_exec([constant.FC_SPEED_COMMAND])
            speed_map_list = \
                self.format_data_to_map(speed_info, 'FC1')
            speed_map = speed_map_list[-1]
            for value_map in fc_map_list:
                if 'Portname' in value_map:
                    status = value_map.get('Status')
                    health = constants.PortHealthStatus.ABNORMAL
                    if status == 'Good':
                        health = constants.PortHealthStatus.NORMAL
                    connection_status = \
                        constants.PortConnectionStatus.DISCONNECTED
                    if 'FCLinkisup' in value_map:
                        connection_status = \
                            constants.PortConnectionStatus.CONNECTED
                    port_id = ''
                    for key in value_map.keys():
                        if 'HostPort' in key:
                            port_id = key.replace('HostPort', '')
                            break
                    speed = \
                        int(speed_map.get('FC' + port_id).replace('Gbps', ''))
                    fc_model = {
                        'name': 'FC' + port_id,
                        'storage_id': storage_id,
                        'native_port_id': port_id,
                        'connection_status': connection_status,
                        'health_status': health,
                        'type': constants.PortType.FC,
                        'speed': speed * units.G,
                        'max_speed': 8 * units.G,
                        'wwn': value_map.get('Portname'),
                    }
                    fc_list.append(fc_model)
            return fc_list
        except exception.DelfinException as e:
            err_msg = "Failed to get fc ports from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get fc ports from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_filesystems(self, storage_id):
        try:
            fs_list = []
            fs_info = self.ssh_do_exec([constant.FS_INFO_COMMAND])
            fs_array = self.get_table_data(fs_info)
            status_info = self.ssh_do_exec([constant.FS_STATUS_COMMAND])
            status_array = self.get_table_data(status_info)
            status_map = {}
            for status in status_array:
                status_info = status.split()
                if len(status_info) > constant.FS_INDEX['status_len']:
                    status_map[status_info[constant.FS_INDEX['id_index']]] = \
                        [status_info[constant.FS_INDEX['pool_index']],
                         status_info[constant.FS_INDEX['status_index']]]
            for fs in fs_array:
                fs_info = list(filter(None, fs.split('  ')))
                if len(fs_info) > constant.FS_INDEX['detail_len']:
                    total_capacity = \
                        fs_info[constant.FS_INDEX['total_index']].replace(
                            ' ', '')
                    used_capacity = \
                        fs_info[constant.FS_INDEX['used_index']].replace(
                            ' ', '').split('(')[0]
                    free_capacity = \
                        fs_info[constant.FS_INDEX['free_index']].replace(
                            ' ', '').split('(')[0]
                    total_capacity = Tools.get_capacity_size(total_capacity)
                    used_capacity = Tools.get_capacity_size(used_capacity)
                    free_capacity = Tools.get_capacity_size(free_capacity)
                    volume_type = constants.VolumeType.THICK \
                        if fs_info[constant.FS_INDEX['type_index']] == 'No' \
                        else constants.VolumeType.THIN
                    pool_id = status_map.get(fs_info[0])[0] \
                        if status_map.get(fs_info[0]) else None
                    status = status_map.get(fs_info[0])[1] \
                        if status_map.get(fs_info[0]) else None
                    fs_model = {
                        'name': fs_info[1],
                        'storage_id': storage_id,
                        'native_filesystem_id': fs_info[1],
                        'native_pool_id': pool_id,
                        'status': constant.FS_STATUS_MAP[status],
                        'type': volume_type,
                        'total_capacity': total_capacity,
                        'used_capacity': used_capacity,
                        'free_capacity': free_capacity
                    }
                    fs_list.append(fs_model)
            return fs_list
        except exception.DelfinException as e:
            err_msg = "Failed to get filesystem from " \
                      "hitachi nas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get filesystem from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_fs_evs(self):
        fs_info = self.ssh_do_exec([constant.FS_STATUS_COMMAND])
        fs_array = self.get_table_data(fs_info)
        evs_list = []
        for fs in fs_array:
            fs_info_array = fs.split()
            if len(fs_info_array) > 6:
                evs_list.append([fs_info_array[0], fs_info_array[4]])
        return evs_list

    def list_quotas(self, storage_id):
        try:
            evs_list = self.get_fs_evs()
            quota_list = []
            for evs in evs_list:
                quota_info = self.ssh_do_exec([
                    constant.CHECK_EVS % evs[1],
                    constant.QUOTA_INFO_COMMAND % evs[0]])
                quota_map_list = \
                    self.format_data_to_map(quota_info, 'Usage')
                for quota_map in quota_map_list:
                    quota_type = None
                    user_group_name = None
                    qtree_id = None
                    if 'Target' in quota_map:
                        if 'Group' in quota_map.get('Target'):
                            quota_type = constants.QuotaType.GROUP
                            user_group_name = \
                                quota_map.get('Target').replace('Group', '')
                        elif 'User' in quota_map.get('Target'):
                            quota_type = constants.QuotaType.USER
                            user_group_name = \
                                quota_map.get('Target').replace('User', '')
                        elif 'ViVol' in quota_map.get('Target'):
                            quota_type = constants.QuotaType.TREE
                            user_group_name = \
                                quota_map.get('Target').replace('ViVol', '')
                            qtree_id = evs[0] + '-' + user_group_name
                    quota_id = \
                        evs[0] + '-' + quota_type + '-' + user_group_name
                    capacity_hard_limit, capacity_soft_limit = None, None
                    file_soft_limit, file_hard_limit = None, None
                    if 'Soft' in quota_map.get('Limit'):
                        capacity_soft_limit = \
                            quota_map.get('Limit').replace('(Soft)', '')
                    elif 'Hard' in quota_map.get('Limit'):
                        capacity_hard_limit = capacity_soft_limit = \
                            quota_map.get('Limit').replace('(Hard)', '')
                    if 'Soft' in quota_map.get('Limit1'):
                        file_soft_limit = \
                            quota_map.get('Limit1').replace('(Soft)', '')
                    elif 'Hard' in quota_map.get('Limit1'):
                        file_soft_limit = file_hard_limit = \
                            quota_map.get('Limit1').replace('(Hard)', '')
                    quota = {
                        'native_quota_id': quota_id,
                        'type': quota_type,
                        'storage_id': storage_id,
                        'native_filesystem_id': evs[0],
                        'native_qtree_id': qtree_id,
                        "capacity_hard_limit": capacity_hard_limit,
                        'capacity_soft_limit':
                            Tools.get_capacity_size(capacity_soft_limit),
                        "file_hard_limit": file_hard_limit,
                        'file_soft_limit': file_soft_limit,
                        'file_count': quota_map.get('FileCount'),
                        'used_capacity':
                            Tools.get_capacity_size(quota_map.get('Usage')),
                        'user_group_name': user_group_name
                    }
                    quota_list.append(quota)
            return quota_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage quota from " \
                      "hitachi nas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage quota from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_qtrees(self, storage_id):
        try:
            evs_list = self.get_fs_evs()
            return self.get_qtree(evs_list, storage_id)
        except exception.DelfinException as e:
            err_msg = "Failed to get storage qtree from " \
                      "hitachi nas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage qtree from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_qtree(self, evs_list, storage_id):
        qtree_list = []
        for evs in evs_list:
            tree_info = self.ssh_do_exec([
                constant.CHECK_EVS % evs[1],
                constant.TREE_INFO_COMMAND % evs[0]])
            tree_map_list = \
                self.format_data_to_map(
                    tree_info, 'root', split_key='last modified')
            for qt_map in tree_map_list:
                qt_name = ''
                for key in qt_map:
                    if qt_map[key] == '' and key != 'email':
                        qt_name = key
                qt_id = evs[0] + '-' + qt_name
                qt_model = {
                    'name': qt_name,
                    'storage_id': storage_id,
                    'native_qtree_id': qt_id,
                    'path': qt_map.get('root'),
                    'native_filesystem_id': evs[0],
                }
                qtree_list.append(qt_model)
        return qtree_list

    def get_cifs_share(self, evs_list, storage_id):
        share_list = []
        evs_array = []
        for evs in evs_list:
            if evs[1] not in evs_array:
                evs_array.append(evs[1])
        for evs in evs_array:
            cifs_share = self.ssh_do_exec([
                constant.CHECK_EVS % evs,
                constant.CIFS_SHARE_COMMAND])
            cifs_map_list = \
                self.format_data_to_map(cifs_share, 'Sharename')
            for cifs in cifs_map_list:
                qtree_id = None
                if 'VirtualVolume' in cifs.get('Sharecomment'):
                    qtree = cifs.get('Sharecomment').split('Volume')
                    if cifs.get('Filesystemlabel'):
                        qtree_id = \
                            cifs.get('Filesystemlabel') + '-' + qtree[1]
                if cifs.get('Filesystemlabel'):
                    native_share_id = \
                        '%s-%s-%s' % (cifs.get('Filesystemlabel'),
                                      cifs.get('Sharename'),
                                      constants.ShareProtocol.CIFS),
                else:
                    native_share_id = \
                        cifs.get('Sharename') + '-' + \
                        constants.ShareProtocol.CIFS,
                share = {
                    'name': cifs.get('Sharename'),
                    'storage_id': storage_id,
                    'native_share_id': native_share_id,
                    'native_qtree_id': qtree_id,
                    'native_filesystem_id': cifs.get('Filesystemlabel'),
                    'path': cifs.get('Sharepath'),
                    'protocol': constants.ShareProtocol.CIFS
                }
                share_list.append(share)
        return share_list

    def get_nfs_share(self, evs_list, storage_id):
        share_list = []
        evs_array = []
        for evs in evs_list:
            if evs[1] not in evs_array:
                evs_array.append(evs[1])
        for evs in evs_array:
            nfs_share = self.ssh_do_exec([
                constant.CHECK_EVS % evs,
                constant.NFS_SHARE_COMMAND])
            nfs_map_list = \
                self.format_data_to_map(nfs_share, 'Exportname')
            qtree_list = self.get_qtree(evs_list, None)
            for nfs in nfs_map_list:
                qtree_id = None
                for qtree in qtree_list:
                    if nfs.get('Exportpath') == qtree['path'] \
                            and qtree['native_filesystem_id'] \
                            == nfs.get('Filesystemlabel'):
                        qtree_id = qtree['native_qtree_id']
                if nfs.get('Filesystemlabel'):
                    native_share_id = \
                        nfs.get('Filesystemlabel') \
                        + '-' + nfs.get('Exportname') \
                        + '-' + constants.ShareProtocol.NFS,
                else:
                    native_share_id = \
                        nfs.get('Exportname') + '-' +\
                        constants.ShareProtocol.NFS,
                share = {
                    'name': nfs.get('Exportname'),
                    'storage_id': storage_id,
                    'native_share_id': native_share_id,
                    'native_qtree_id': qtree_id,
                    'native_filesystem_id': nfs.get('Filesystemlabel'),
                    'path': nfs.get('Exportpath'),
                    'protocol': constants.ShareProtocol.NFS
                }
                share_list.append(share)
        return share_list

    def list_shares(self, storage_id):
        try:
            evs_list = self.get_fs_evs()
            share_list = []
            share_list.extend(self.get_cifs_share(evs_list, storage_id))
            share_list.extend(self.get_nfs_share(evs_list, storage_id))
            return share_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage share from " \
                      "hitachi nas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage share from " \
                      "hitachi nas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
