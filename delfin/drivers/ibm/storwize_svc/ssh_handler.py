# Copyright 2020 The SODA Authors.
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
import os
import re
import time
from itertools import islice

import paramiko
import six
from oslo_log import log as logging
from oslo_utils import units

from delfin import exception, utils
from delfin.common import constants, alert_util
from delfin.drivers.ibm.storwize_svc import consts
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools

LOG = logging.getLogger(__name__)


class SSHHandler(object):
    OID_ERR_ID = '1.3.6.1.4.1.2.6.190.4.3'
    OID_SEQ_NUMBER = '1.3.6.1.4.1.2.6.190.4.9'
    OID_LAST_TIME = '1.3.6.1.4.1.2.6.190.4.10'
    OID_OBJ_TYPE = '1.3.6.1.4.1.2.6.190.4.11'
    OID_OBJ_NAME = '1.3.6.1.4.1.2.6.190.4.17'
    OID_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'

    TRAP_SEVERITY_MAP = {
        '1.3.6.1.4.1.2.6.190.1': constants.Severity.CRITICAL,
        '1.3.6.1.4.1.2.6.190.2': constants.Severity.WARNING,
        '1.3.6.1.4.1.2.6.190.3': constants.Severity.INFORMATIONAL,
    }

    SEVERITY_MAP = {"warning": "Warning",
                    "informational": "Informational",
                    "error": "Major"
                    }
    CONTRL_STATUS_MAP = {"online": constants.ControllerStatus.NORMAL,
                         "offline": constants.ControllerStatus.OFFLINE,
                         "service": constants.ControllerStatus.NORMAL,
                         "flushing": constants.ControllerStatus.UNKNOWN,
                         "pending": constants.ControllerStatus.UNKNOWN,
                         "adding": constants.ControllerStatus.UNKNOWN,
                         "deleting": constants.ControllerStatus.UNKNOWN
                         }

    DISK_PHYSICAL_TYPE = {
        'fc': constants.DiskPhysicalType.FC,
        'sas_direct': constants.DiskPhysicalType.SAS
    }
    VOLUME_PERF_METRICS = {
        'readIops': 'ro',
        'writeIops': 'wo',
        'readThroughput': 'rb',
        'writeThroughput': 'wb',
        'readIoSize': 'rb',
        'writeIoSize': 'wb',
        'responseTime': 'res_time',
        'throughput': 'tb',
        'iops': 'to',
        'ioSize': 'tb',
        'cacheHitRatio': 'hrt',
        'readCacheHitRatio': 'rhr',
        'writeCacheHitRatio': 'whr'
    }
    DISK_PERF_METRICS = {
        'readIops': 'ro',
        'writeIops': 'wo',
        'readThroughput': 'rb',
        'writeThroughput': 'wb',
        'responseTime': 'res_time',
        'throughput': 'tb',
        'iops': 'to'
    }
    CONTROLLER_PERF_METRICS = {
        'readIops': 'ro',
        'writeIops': 'wo',
        'readThroughput': 'rb',
        'writeThroughput': 'wb',
        'responseTime': 'res_time',
        'throughput': 'tb',
        'iops': 'to'
    }
    PORT_PERF_METRICS = {
        'readIops': 'ro',
        'writeIops': 'wo',
        'readThroughput': 'rb',
        'writeThroughput': 'wb',
        'throughput': 'tb',
        'responseTime': 'res_time',
        'iops': 'to'
    }
    TARGET_RESOURCE_RELATION = {
        constants.ResourceType.DISK: 'mdsk',
        constants.ResourceType.VOLUME: 'vdsk',
        constants.ResourceType.PORT: 'port',
        constants.ResourceType.CONTROLLER: 'node'
    }
    RESOURCE_PERF_MAP = {
        constants.ResourceType.DISK: DISK_PERF_METRICS,
        constants.ResourceType.VOLUME: VOLUME_PERF_METRICS,
        constants.ResourceType.PORT: PORT_PERF_METRICS,
        constants.ResourceType.CONTROLLER: CONTROLLER_PERF_METRICS
    }
    SECONDS_TO_MS = 1000
    ALERT_NOT_FOUND_CODE = 'CMMVC8275E'
    BLOCK_SIZE = 512
    BYTES_TO_BIT = 8
    OS_TYPE_MAP = {'generic': constants.HostOSTypes.UNKNOWN,
                   'hpux': constants.HostOSTypes.HP_UX,
                   'openvms': constants.HostOSTypes.OPEN_VMS,
                   'tpgs': constants.HostOSTypes.UNKNOWN,
                   'vvol': constants.HostOSTypes.UNKNOWN
                   }
    INITIATOR_STATUS_MAP = {'active': constants.InitiatorStatus.ONLINE,
                            'offline': constants.InitiatorStatus.OFFLINE,
                            'inactive': constants.InitiatorStatus.ONLINE
                            }
    HOST_STATUS_MAP = {'online': constants.HostStatus.NORMAL,
                       'offline': constants.HostStatus.OFFLINE,
                       'degraded': constants.HostStatus.DEGRADED,
                       'mask': constants.HostStatus.NORMAL,
                       }

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    @staticmethod
    def handle_split(split_str, split_char, arr_number):
        split_value = ''
        if split_str is not None and split_str != '':
            tmp_value = split_str.split(split_char, 1)
            if arr_number == 1 and len(tmp_value) > 1:
                split_value = tmp_value[arr_number].strip()
            elif arr_number == 0:
                split_value = tmp_value[arr_number].strip()
        return split_value

    @staticmethod
    def parse_alert(alert):
        try:
            alert_model = dict()
            alert_name = SSHHandler.handle_split(alert.get(
                SSHHandler.OID_ERR_ID), ':', 1)
            error_info = SSHHandler.handle_split(alert.get(
                SSHHandler.OID_ERR_ID), ':', 0)
            alert_id = SSHHandler.handle_split(error_info, '=', 1)
            severity = SSHHandler.TRAP_SEVERITY_MAP.get(
                alert.get(SSHHandler.OID_SEVERITY),
                constants.Severity.INFORMATIONAL
            )
            alert_model['alert_id'] = str(alert_id)
            alert_model['alert_name'] = alert_name
            alert_model['severity'] = severity
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['sequence_number'] = SSHHandler. \
                handle_split(alert.get(SSHHandler.OID_SEQ_NUMBER), '=', 1)
            timestamp = SSHHandler. \
                handle_split(alert.get(SSHHandler.OID_LAST_TIME), '=', 1)
            time_type = '%a %b %d %H:%M:%S %Y'
            occur_time = int(time.mktime(time.strptime(
                timestamp,
                time_type)))
            alert_model['occur_time'] = int(occur_time * SSHHandler.
                                            SECONDS_TO_MS)
            alert_model['description'] = alert_name
            alert_model['resource_type'] = SSHHandler.handle_split(
                alert.get(SSHHandler.OID_OBJ_TYPE), '=', 1)
            alert_model['location'] = SSHHandler.handle_split(alert.get(
                SSHHandler.OID_OBJ_NAME), '=', 1)
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = ("Failed to build alert model as some attributes missing "
                   "in alert message:%s.") % (six.text_type(e))
            raise exception.InvalidResults(msg)

    def login(self):
        try:
            with self.ssh_pool.item() as ssh:
                result = SSHHandler.do_exec('lssystem', ssh)
                if 'is not a recognized command' in result:
                    raise exception.InvalidIpOrPort()
        except Exception as e:
            LOG.error("Failed to login ibm storwize_svc %s" %
                      (six.text_type(e)))
            raise e

    @staticmethod
    def do_exec(command_str, ssh):
        """Execute command"""
        try:
            utils.check_ssh_injection(command_str.split())
            if command_str is not None and ssh is not None:
                stdin, stdout, stderr = ssh.exec_command(command_str)
                res, err = stdout.read(), stderr.read()
                re = res if res else err
                result = re.decode()
        except paramiko.AuthenticationException as ae:
            LOG.error('doexec Authentication error:{}'.format(ae))
            raise exception.InvalidUsernameOrPassword()
        except Exception as e:
            err = six.text_type(e)
            LOG.error('doexec InvalidUsernameOrPassword error')
            if 'timed out' in err:
                raise exception.SSHConnectTimeout()
            elif 'No authentication methods available' in err \
                    or 'Authentication failed' in err:
                raise exception.InvalidUsernameOrPassword()
            elif 'not a valid RSA private key file' in err:
                raise exception.InvalidPrivateKey()
            else:
                raise exception.SSHException(err)
        return result

    def exec_ssh_command(self, command):
        try:
            with self.ssh_pool.item() as ssh:
                ssh_info = SSHHandler.do_exec(command, ssh)
            return ssh_info
        except Exception as e:
            msg = "Failed to ssh ibm storwize_svc %s: %s" % \
                  (command, six.text_type(e))
            raise exception.SSHException(msg)

    def change_capacity_to_bytes(self, unit):
        unit = unit.upper()
        if unit == 'TB':
            result = units.Ti
        elif unit == 'GB':
            result = units.Gi
        elif unit == 'MB':
            result = units.Mi
        elif unit == 'KB':
            result = units.Ki
        else:
            result = 1
        return int(result)

    def parse_string(self, value):
        capacity = 0
        if value:
            if value.isdigit():
                capacity = float(value)
            else:
                unit = value[-2:]
                capacity = float(value[:-2]) * int(
                    self.change_capacity_to_bytes(unit))
        return capacity

    def get_storage(self):
        try:
            system_info = self.exec_ssh_command('lssystem')
            storage_map = {}
            self.handle_detail(system_info, storage_map, split=' ')
            serial_number = storage_map.get('id')
            status = 'normal' if storage_map.get('statistics_status') == 'on' \
                else 'offline'
            location = storage_map.get('location')
            free_capacity = self.parse_string(storage_map.get(
                'total_free_space'))
            used_capacity = self.parse_string(storage_map.get(
                'total_used_capacity'))
            raw_capacity = self.parse_string(storage_map.get(
                'total_mdisk_capacity'))
            subscribed_capacity = self.parse_string(storage_map.get(
                'virtual_capacity'))
            firmware_version = ''
            if storage_map.get('code_level') is not None:
                firmware_version = storage_map.get('code_level').split(' ')[0]
            s = {
                'name': storage_map.get('name'),
                'vendor': 'IBM',
                'model': storage_map.get('product_name'),
                'status': status,
                'serial_number': serial_number,
                'firmware_version': firmware_version,
                'location': location,
                'total_capacity': int(free_capacity + used_capacity),
                'raw_capacity': int(raw_capacity),
                'subscribed_capacity': int(subscribed_capacity),
                'used_capacity': int(used_capacity),
                'free_capacity': int(free_capacity)
            }
            return s
        except exception.DelfinException as e:
            err_msg = "Failed to get storage: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handle_detail(self, deltail_info, detail_map, split):
        detail_arr = deltail_info.split('\n')
        for detail in detail_arr:
            if detail is not None and detail != '':
                strinfo = detail.split(split, 1)
                key = strinfo[0]
                value = ''
                if len(strinfo) > 1:
                    value = strinfo[1]
                detail_map[key] = value

    def list_storage_pools(self, storage_id):
        try:
            pool_list = []
            pool_info = self.exec_ssh_command('lsmdiskgrp')
            pool_res = pool_info.split('\n')
            for i in range(1, len(pool_res)):
                if pool_res[i] is None or pool_res[i] == '':
                    continue

                pool_str = ' '.join(pool_res[i].split())
                strinfo = pool_str.split(' ')
                detail_command = 'lsmdiskgrp %s' % strinfo[0]
                deltail_info = self.exec_ssh_command(detail_command)
                pool_map = {}
                self.handle_detail(deltail_info, pool_map, split=' ')
                status = 'normal' if pool_map.get('status') == 'online' \
                    else 'offline'
                total_cap = self.parse_string(pool_map.get('capacity'))
                free_cap = self.parse_string(pool_map.get('free_capacity'))
                used_cap = self.parse_string(pool_map.get('used_capacity'))
                subscribed_capacity = self.parse_string(pool_map.get(
                    'virtual_capacity'))
                p = {
                    'name': pool_map.get('name'),
                    'storage_id': storage_id,
                    'native_storage_pool_id': pool_map.get('id'),
                    'description': '',
                    'status': status,
                    'storage_type': constants.StorageType.BLOCK,
                    'subscribed_capacity': int(subscribed_capacity),
                    'total_capacity': int(total_cap),
                    'used_capacity': int(used_cap),
                    'free_capacity': int(free_cap)
                }
                pool_list.append(p)

            return pool_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage pool: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage pool: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_volumes(self, storage_id):
        try:
            volume_list = []
            volume_info = self.exec_ssh_command('lsvdisk')
            volume_res = volume_info.split('\n')
            for i in range(1, len(volume_res)):
                if volume_res[i] is None or volume_res[i] == '':
                    continue
                volume_str = ' '.join(volume_res[i].split())
                strinfo = volume_str.split(' ')
                volume_id = strinfo[0]
                detail_command = 'lsvdisk -delim : %s' % volume_id
                deltail_info = self.exec_ssh_command(detail_command)
                volume_map = {}
                self.handle_detail(deltail_info, volume_map, split=':')
                status = 'normal' if volume_map.get('status') == 'online' \
                    else 'offline'
                volume_type = 'thin' if volume_map.get('se_copy') == 'yes' \
                    else 'thick'
                total_capacity = self.parse_string(volume_map.get('capacity'))
                free_capacity = self.parse_string(volume_map.
                                                  get('free_capacity'))
                used_capacity = self.parse_string(volume_map.
                                                  get('used_capacity'))
                compressed = True
                deduplicated = True
                if volume_map.get('compressed_copy') == 'no':
                    compressed = False
                if volume_map.get('deduplicated_copy') == 'no':
                    deduplicated = False

                v = {
                    'name': volume_map.get('name'),
                    'storage_id': storage_id,
                    'description': '',
                    'status': status,
                    'native_volume_id': str(volume_map.get('id')),
                    'native_storage_pool_id': volume_map.get('mdisk_grp_id'),
                    'wwn': str(volume_map.get('vdisk_UID')),
                    'type': volume_type,
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': int(free_capacity),
                    'compressed': compressed,
                    'deduplicated': deduplicated
                }
                volume_list.append(v)
            return volume_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage volume: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage volume: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_alerts(self, query_para):
        try:
            alert_list = []
            alert_info = self.exec_ssh_command('lseventlog -monitoring yes '
                                               '-message no')
            alert_res = alert_info.split('\n')
            for i in range(1, len(alert_res)):
                if alert_res[i] is None or alert_res[i] == '':
                    continue
                alert_str = ' '.join(alert_res[i].split())
                strinfo = alert_str.split(' ', 1)
                detail_command = 'lseventlog %s' % strinfo[0]
                deltail_info = self.exec_ssh_command(detail_command)
                alert_map = {}
                self.handle_detail(deltail_info, alert_map, split=' ')
                occur_time = int(alert_map.get('last_timestamp_epoch')) * \
                    self.SECONDS_TO_MS
                if not alert_util.is_alert_in_time_range(query_para,
                                                         occur_time):
                    continue
                alert_name = alert_map.get('event_id_text', '')
                event_id = alert_map.get('event_id')
                location = alert_map.get('object_name', '')
                resource_type = alert_map.get('object_type', '')
                severity = self.SEVERITY_MAP.get(alert_map.
                                                 get('notification_type'))
                if severity == 'Informational' or severity is None:
                    continue
                alert_model = {
                    'alert_id': event_id,
                    'alert_name': alert_name,
                    'severity': severity,
                    'category': constants.Category.FAULT,
                    'type': 'EquipmentAlarm',
                    'sequence_number': alert_map.get('sequence_number'),
                    'occur_time': occur_time,
                    'description': alert_name,
                    'resource_type': resource_type,
                    'location': location
                }
                alert_list.append(alert_model)

            return alert_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage alert: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage alert: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def fix_alert(self, alert):
        command_line = 'cheventlog -fix %s' % alert
        result = self.exec_ssh_command(command_line)
        if result:
            if self.ALERT_NOT_FOUND_CODE not in result:
                raise exception.InvalidResults(six.text_type(result))
            LOG.warning("Alert %s doesn't exist.", alert)

    def list_controllers(self, storage_id):
        try:
            controller_list = []
            controller_cmd = 'lsnode'
            control_info = self.exec_ssh_command(controller_cmd)
            if 'command not found' in control_info:
                controller_cmd = 'lsnodecanister'
                control_info = self.exec_ssh_command(controller_cmd)
            control_res = control_info.split('\n')
            for i in range(1, len(control_res)):
                if control_res[i] is None or control_res[i] == '':
                    continue
                control_str = ' '.join(control_res[i].split())
                str_info = control_str.split(' ')
                control_id = str_info[0]
                detail_command = '%s %s' % (controller_cmd, control_id)
                deltail_info = self.exec_ssh_command(detail_command)
                control_map = {}
                self.handle_detail(deltail_info, control_map, split=' ')
                cpu_map = {}
                cpu_cmd = 'lsnodehw -delim , %s' % control_id
                cpu_info = self.exec_ssh_command(cpu_cmd)
                if 'command not found' in cpu_info:
                    cpu_cmd = 'lsnodecanisterhw -delim , %s' % control_id
                    cpu_info = self.exec_ssh_command(cpu_cmd)
                self.handle_detail(cpu_info, cpu_map, split=',')
                cpu_actual = cpu_map.get('cpu_actual')
                status = SSHHandler.CONTRL_STATUS_MAP.get(
                    control_map.get('status'),
                    constants.ControllerStatus.UNKNOWN)
                controller_result = {
                    'name': control_map.get('name'),
                    'storage_id': storage_id,
                    'native_controller_id': control_map.get('id'),
                    'status': status,
                    'soft_version':
                        control_map.get('code_level', '').split(' ')[0],
                    'location': control_map.get('name'),
                    'cpu_info': cpu_actual
                }
                controller_list.append(controller_result)
            return controller_list
        except Exception as err:
            err_msg = "Failed to get controller attributes from Storwize: %s"\
                      % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_disks(self, storage_id):
        try:
            disk_list = []
            disk_info = self.exec_ssh_command('lsmdisk')
            disk_res = disk_info.split('\n')
            for i in range(1, len(disk_res)):
                if disk_res[i] is None or disk_res[i] == '':
                    continue
                control_str = ' '.join(disk_res[i].split())
                str_info = control_str.split(' ')
                disk_id = str_info[0]
                detail_command = 'lsmdisk %s' % disk_id
                deltail_info = self.exec_ssh_command(detail_command)
                disk_map = {}
                self.handle_detail(deltail_info, disk_map, split=' ')
                status = constants.DiskStatus.NORMAL
                if disk_map.get('status') == 'offline':
                    status = constants.DiskStatus.OFFLINE
                physical_type = SSHHandler.DISK_PHYSICAL_TYPE.get(
                    disk_map.get('fabric_type'),
                    constants.DiskPhysicalType.UNKNOWN)
                location = '%s_%s' % (disk_map.get('controller_name'),
                                      disk_map.get('name'))
                disk_result = {
                    'name': disk_map.get('name'),
                    'storage_id': storage_id,
                    'native_disk_id': disk_map.get('id'),
                    'capacity': int(self.parse_string(
                        disk_map.get('capacity'))),
                    'status': status,
                    'physical_type': physical_type,
                    'native_disk_group_id': disk_map.get('mdisk_grp_name'),
                    'location': location
                }
                disk_list.append(disk_result)
            return disk_list
        except Exception as err:
            err_msg = "Failed to get disk attributes from Storwize: %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def get_fc_port(self, storage_id):
        port_list = []
        fc_info = self.exec_ssh_command('lsportfc')
        fc_res = fc_info.split('\n')
        for i in range(1, len(fc_res)):
            if fc_res[i] is None or fc_res[i] == '':
                continue
            control_str = ' '.join(fc_res[i].split())
            str_info = control_str.split(' ')
            port_id = str_info[0]
            detail_command = 'lsportfc %s' % port_id
            deltail_info = self.exec_ssh_command(detail_command)
            port_map = {}
            self.handle_detail(deltail_info, port_map, split=' ')
            status = constants.PortHealthStatus.NORMAL
            conn_status = constants.PortConnectionStatus.CONNECTED
            if port_map.get('status') != 'active':
                status = constants.PortHealthStatus.ABNORMAL
                conn_status = constants.PortConnectionStatus.DISCONNECTED
            port_type = constants.PortType.FC
            if port_map.get('type') == 'ethernet':
                port_type = constants.PortType.ETH
            location = '%s_%s' % (port_map.get('node_name'),
                                  port_map.get('id'))
            speed = None
            if port_map.get('port_speed')[:-2].isdigit():
                speed = int(self.handle_port_bps(
                    port_map.get('port_speed'), 'fc'))
            port_result = {
                'name': location,
                'storage_id': storage_id,
                'native_port_id': port_map.get('id'),
                'location': location,
                'connection_status': conn_status,
                'health_status': status,
                'type': port_type,
                'speed': speed,
                'native_parent_id': port_map.get('node_name'),
                'wwn': port_map.get('WWPN')
            }
            port_list.append(port_result)
        return port_list

    def get_iscsi_port(self, storage_id):
        port_list = []
        for i in range(1, 3):
            port_array = []
            port_command = 'lsportip %s' % i
            port_info = self.exec_ssh_command(port_command)
            port_arr = port_info.split('\n')
            port_map = {}
            for detail in port_arr:
                if detail is not None and detail != '':
                    strinfo = detail.split(' ', 1)
                    key = strinfo[0]
                    value = ''
                    if len(strinfo) > 1:
                        value = strinfo[1]
                    port_map[key] = value
                else:
                    if len(port_map) > 1:
                        port_array.append(port_map)
                        port_map = {}
                        continue
            for port in port_array:
                if port.get('failover') == 'yes':
                    continue
                status = constants.PortHealthStatus.ABNORMAL
                if port.get('state') == 'online':
                    status = constants.PortHealthStatus.NORMAL
                conn_status = constants.PortConnectionStatus.DISCONNECTED
                if port.get('link_state') == 'active':
                    conn_status = constants.PortConnectionStatus.CONNECTED
                port_type = constants.PortType.ETH
                location = '%s_%s' % (port.get('node_name'),
                                      port.get('id'))
                port_result = {
                    'name': location,
                    'storage_id': storage_id,
                    'native_port_id': location,
                    'location': location,
                    'connection_status': conn_status,
                    'health_status': status,
                    'type': port_type,
                    'speed': int(self.handle_port_bps(
                        port.get('speed'), 'eth')),
                    'native_parent_id': port.get('node_name'),
                    'mac_address': port.get('MAC'),
                    'ipv4': port.get('IP_address'),
                    'ipv4_mask': port.get('mask'),
                    'ipv6': port.get('IP_address_6')
                }
                port_list.append(port_result)
        return port_list

    @staticmethod
    def change_speed_to_bytes(unit):
        unit = unit.upper()
        if unit == 'TB':
            result = units.T
        elif unit == 'GB':
            result = units.G
        elif unit == 'MB':
            result = units.M
        elif unit == 'KB':
            result = units.k
        else:
            result = 1
        return int(result)

    def handle_port_bps(self, value, port_type):
        speed = 0
        if value:
            if value.isdigit():
                speed = float(value)
            else:
                if port_type == 'fc':
                    unit = value[-2:]
                    speed = float(value[:-2]) * int(
                        self.change_speed_to_bytes(unit))
                else:
                    unit = value[-4:-2]
                    speed = float(value[:-4]) * int(
                        self.change_speed_to_bytes(unit))
        return speed

    def list_ports(self, storage_id):
        try:
            port_list = []
            port_list.extend(self.get_fc_port(storage_id))
            port_list.extend(self.get_iscsi_port(storage_id))
            return port_list
        except Exception as err:
            err_msg = "Failed to get ports attributes from Storwize: %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def handle_stats_filename(file_name, file_map):
        name_arr = file_name.split('_')
        file_type = '%s_%s_%s' % (name_arr[0], name_arr[1], name_arr[2])
        file_time = '20%s%s' % (name_arr[3], name_arr[4])
        time_pattern = '%Y%m%d%H%M%S'
        tools = Tools()
        occur_time = tools.time_str_to_timestamp(file_time, time_pattern)
        if file_map.get(file_type):
            file_map[file_type][occur_time] = file_name
        else:
            file_map[file_type] = {occur_time: file_name}

    def get_stats_filelist(self, file_map):
        stats_file_command = 'lsdumps -prefix /dumps/iostats'
        file_list = self.exec_ssh_command(stats_file_command)
        file_line = file_list.split('\n')
        for file in islice(file_line, 1, None):
            if file:
                file_arr = ' '.join(file.split()).split(' ')
                if len(file_arr) > 1:
                    file_name = file_arr[1]
                    SSHHandler.handle_stats_filename(file_name, file_map)
        for file_stats in file_map:
            file_map[file_stats] = sorted(file_map.get(file_stats).items(),
                                          key=lambda x: x[0], reverse=False)

    def packege_data(self, storage_id, resource_type, metrics, metric_map):
        resource_id = None
        resource_name = None
        unit = None
        for resource_info in metric_map:
            if resource_type == constants.ResourceType.PORT:
                port_info = self.get_fc_port(storage_id)
                if port_info:
                    for fc_port in port_info:
                        if resource_info.strip('0x').upper() == fc_port.get(
                                'wwn').upper():
                            resource_id = fc_port.get('native_port_id')
                            resource_name = fc_port.get('name')
                            break
            else:
                resource_arr = resource_info.split('_')
                resource_id = resource_arr[0]
                resource_name = resource_arr[1]
            for target in metric_map.get(resource_info):
                if resource_type == constants.ResourceType.PORT:
                    unit = consts.PORT_CAP[target]['unit']
                elif resource_type == constants.ResourceType.VOLUME:
                    unit = consts.VOLUME_CAP[target]['unit']
                elif resource_type == constants.ResourceType.DISK:
                    unit = consts.DISK_CAP[target]['unit']
                elif resource_type == constants.ResourceType.CONTROLLER:
                    unit = consts.CONTROLLER_CAP[target]['unit']
                if 'responseTime' == target:
                    for res_time in metric_map.get(resource_info).get(target):
                        for iops_time in metric_map.get(resource_info).get(
                                'iops'):
                            if res_time == iops_time:
                                res_value = metric_map.get(resource_info).get(
                                    target).get(res_time)
                                iops_value = metric_map.get(
                                    resource_info).get('iops').get(iops_time)
                                res_value = \
                                    res_value / iops_value if iops_value else 0
                                res_value = round(res_value, 3)
                                metric_map[resource_info][target][res_time] = \
                                    res_value
                                break
                labels = {
                    'storage_id': storage_id,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'resource_name': resource_name,
                    'type': 'RAW',
                    'unit': unit
                }
                metric_value = constants.metric_struct(name=target,
                                                       labels=labels,
                                                       values=metric_map.get(
                                                           resource_info).get(
                                                           target))
                metrics.append(metric_value)

    @staticmethod
    def count_metric_data(last_data, now_data, interval, target, metric_type,
                          metric_map, res_id):
        if not target:
            return
        if 'CACHEHITRATIO' not in metric_type.upper():
            value = SSHHandler.count_difference(now_data.get(target),
                                                last_data.get(target))
        else:
            value = now_data.get(
                SSHHandler.VOLUME_PERF_METRICS.get(metric_type))
        if 'THROUGHPUT' in metric_type.upper():
            value = value / interval / units.Mi
        elif 'IOSIZE' in metric_type.upper():
            value = value / units.Ki
        elif 'IOPS' in metric_type.upper() or 'RESPONSETIME' \
                in metric_type.upper():
            value = value / interval
        value = round(value, 3)
        if metric_map.get(res_id):
            if metric_map.get(res_id).get(metric_type):
                if metric_map.get(res_id).get(metric_type).get(
                        now_data.get('time')):
                    metric_map[res_id][metric_type][now_data.get('time')] \
                        += value
                else:
                    metric_map[res_id][metric_type][now_data.get('time')] \
                        = value
            else:
                metric_map[res_id][metric_type] = {now_data.get('time'): value}
        else:
            metric_map[res_id] = {metric_type: {now_data.get('time'): value}}

    @staticmethod
    def count_difference(now_value, last_value):
        return now_value if now_value < last_value else now_value - last_value

    @staticmethod
    def handle_volume_cach_hit(now_data, last_data):
        rh = SSHHandler.count_difference(now_data.get('rh'),
                                         last_data.get('rh'))
        wh = SSHHandler.count_difference(now_data.get('wh'),
                                         last_data.get('wh'))
        rht = SSHHandler.count_difference(now_data.get('rht'),
                                          last_data.get('rht'))
        wht = SSHHandler.count_difference(now_data.get('wht'),
                                          last_data.get('wht'))
        rhr = rh * 100 / rht if rht > 0 else 0
        whr = wh * 100 / wht if wht > 0 else 0
        hrt = rhr + whr
        now_data['rhr'] = rhr
        now_data['whr'] = whr
        now_data['hrt'] = hrt

    def get_date_from_each_file(self, file, metric_map, target_list,
                                resource_type, last_data):
        with self.ssh_pool.item() as ssh:
            local_path = '%s/%s' % (
                os.path.abspath(os.path.join(os.getcwd())),
                consts.LOCAL_FILE_PATH)
            file_xml = Tools.get_remote_file_to_xml(
                ssh, file[1], local_path,
                consts.REMOTE_FILE_PATH)
            if not file_xml:
                return
            for data in file_xml:
                if re.sub(u"\\{.*?}", "", data.tag) == \
                        SSHHandler.TARGET_RESOURCE_RELATION.get(
                            resource_type):
                    if resource_type == constants.ResourceType.PORT:
                        if data.attrib.get('fc_wwpn'):
                            resource_info = data.attrib.get('fc_wwpn')
                        else:
                            continue
                    elif resource_type == constants. \
                            ResourceType.CONTROLLER:
                        resource_info = '%s_%s' % (
                            int(data.attrib.get('node_id'), 16),
                            data.attrib.get('id'))
                    else:
                        resource_info = '%s_%s' % (data.attrib.get('idx'),
                                                   data.attrib.get('id'))
                    now_data = SSHHandler.package_xml_data(data.attrib,
                                                           file[0],
                                                           resource_type)
                    if last_data.get(resource_info):
                        interval = (int(file[0]) - last_data.get(
                            resource_info).get('time')) / units.k
                        if interval <= 0:
                            break
                        if resource_type == constants.ResourceType.VOLUME:
                            SSHHandler.handle_volume_cach_hit(
                                now_data, last_data.get(resource_info))
                        for target in target_list:
                            device_target = SSHHandler. \
                                RESOURCE_PERF_MAP.get(resource_type)
                            SSHHandler.count_metric_data(
                                last_data.get(resource_info),
                                now_data, interval,
                                device_target.get(target),
                                target, metric_map, resource_info)
                        last_data[resource_info] = now_data
                    else:
                        last_data[resource_info] = now_data

    def get_stats_from_file(self, file_list, metric_map, target_list,
                            resource_type, start_time, end_time):
        if not file_list:
            return
        find_first_file = False
        recent_file = None
        last_data = {}
        for file in file_list:
            if file[0] >= start_time and file[0] <= end_time:
                if find_first_file is False:
                    if recent_file:
                        self.get_date_from_each_file(recent_file, metric_map,
                                                     target_list,
                                                     resource_type,
                                                     last_data)
                    self.get_date_from_each_file(file, metric_map, target_list,
                                                 resource_type, last_data)
                    find_first_file = True
                else:
                    self.get_date_from_each_file(file, metric_map, target_list,
                                                 resource_type, last_data)
            recent_file = file

    @staticmethod
    def package_xml_data(file_data, file_time, resource_type):
        rb = 0
        wb = 0
        res_time = 0
        rh = 0
        wh = 0
        rht = 0
        wht = 0
        if resource_type == constants.ResourceType.PORT:
            rb = int(file_data.get('cbr')) + int(file_data.get('hbr')) + int(
                file_data.get('lnbr')) + int(
                file_data.get('rmbr')) * SSHHandler.BYTES_TO_BIT
            wb = int(file_data.get('cbt')) + int(file_data.get('hbt')) + int(
                file_data.get('lnbt')) + int(
                file_data.get('rmbt')) * SSHHandler.BYTES_TO_BIT
            ro = int(file_data.get('cer')) + int(file_data.get('her')) + int(
                file_data.get('lner')) + int(file_data.get('rmer'))
            wo = int(file_data.get('cet')) + int(file_data.get('het')) + int(
                file_data.get('lnet')) + int(file_data.get('rmet'))
            res_time = int(file_data.get('dtdt', 0)) / units.Ki
        else:
            if resource_type == constants.ResourceType.VOLUME:
                rb = int(file_data.get('rb')) * SSHHandler.BLOCK_SIZE
                wb = int(file_data.get('wb')) * SSHHandler.BLOCK_SIZE
                rh = int(file_data.get('ctrhs'))
                wh = int(file_data.get('ctwhs'))
                rht = int(file_data.get('ctrs'))
                wht = int(file_data.get('ctws'))
                res_time = int(file_data.get('xl'))
            elif resource_type == constants.ResourceType.DISK:
                rb = int(file_data.get('rb')) * SSHHandler.BLOCK_SIZE
                wb = int(file_data.get('wb')) * SSHHandler.BLOCK_SIZE
                res_time = int(file_data.get('rq')) + int(file_data.get('wq'))
            elif resource_type == constants.ResourceType.CONTROLLER:
                rb = int(file_data.get('rb')) * SSHHandler.BYTES_TO_BIT
                wb = int(file_data.get('wb')) * SSHHandler.BYTES_TO_BIT
                res_time = int(file_data.get('rq')) + int(file_data.get('wq'))
            ro = int(file_data.get('ro'))
            wo = int(file_data.get('wo'))
        now_data = {
            'rb': rb,
            'wb': wb,
            'ro': ro,
            'wo': wo,
            'tb': rb + wb,
            'to': ro + wo,
            'rh': rh,
            'wh': wh,
            'rht': rht,
            'wht': wht,
            'res_time': res_time,
            'time': int(file_time)
        }
        return now_data

    def get_stats_file_data(self, file_map, res_type, metrics, storage_id,
                            target_list, start_time, end_time):
        metric_map = {}
        for file_tye in file_map:
            file_list = file_map.get(file_tye)
            if 'Nv' in file_tye and res_type == constants.ResourceType.VOLUME:
                self.get_stats_from_file(file_list, metric_map, target_list,
                                         constants.ResourceType.VOLUME,
                                         start_time, end_time)
            elif 'Nm' in file_tye and res_type == constants.ResourceType.DISK:
                self.get_stats_from_file(file_list, metric_map, target_list,
                                         constants.ResourceType.DISK,
                                         start_time, end_time)
            elif 'Nn' in file_tye and res_type == constants.ResourceType.PORT:
                self.get_stats_from_file(file_list, metric_map, target_list,
                                         constants.ResourceType.PORT,
                                         start_time, end_time)
            elif 'Nn' in file_tye and res_type == \
                    constants.ResourceType.CONTROLLER:
                self.get_stats_from_file(file_list, metric_map, target_list,
                                         constants.ResourceType.CONTROLLER,
                                         start_time, end_time)
        self.packege_data(storage_id, res_type, metrics, metric_map)

    def collect_perf_metrics(self, storage_id, resource_metrics,
                             start_time, end_time):
        metrics = []
        file_map = {}
        try:
            self.get_stats_filelist(file_map)
            if resource_metrics.get(constants.ResourceType.VOLUME):
                self.get_stats_file_data(
                    file_map,
                    constants.ResourceType.VOLUME,
                    metrics,
                    storage_id,
                    resource_metrics.get(constants.ResourceType.VOLUME),
                    start_time, end_time)
            if resource_metrics.get(constants.ResourceType.DISK):
                self.get_stats_file_data(
                    file_map,
                    constants.ResourceType.DISK,
                    metrics,
                    storage_id,
                    resource_metrics.get(constants.ResourceType.DISK),
                    start_time, end_time)
            if resource_metrics.get(constants.ResourceType.PORT):
                self.get_stats_file_data(
                    file_map,
                    constants.ResourceType.PORT,
                    metrics,
                    storage_id,
                    resource_metrics.get(constants.ResourceType.PORT),
                    start_time, end_time)
            if resource_metrics.get(constants.ResourceType.CONTROLLER):
                self.get_stats_file_data(
                    file_map,
                    constants.ResourceType.CONTROLLER,
                    metrics,
                    storage_id,
                    resource_metrics.get(constants.ResourceType.CONTROLLER),
                    start_time, end_time)
        except Exception as err:
            err_msg = "Failed to collect metrics from svc: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return metrics

    def get_latest_perf_timestamp(self):
        latest_time = 0
        stats_file_command = 'lsdumps -prefix /dumps/iostats'
        file_list = self.exec_ssh_command(stats_file_command)
        file_line = file_list.split('\n')
        for file in islice(file_line, 1, None):
            if file:
                file_arr = ' '.join(file.split()).split(' ')
                if len(file_arr) > 1:
                    file_name = file_arr[1]
                    name_arr = file_name.split('_')
                    file_time = '20%s%s' % (name_arr[3], name_arr[4])
                    time_pattern = '%Y%m%d%H%M%S'
                    tools = Tools()
                    occur_time = tools.time_str_to_timestamp(
                        file_time, time_pattern)
                    if latest_time < occur_time:
                        latest_time = occur_time
        return latest_time

    def list_storage_hosts(self, storage_id):
        try:
            host_list = []
            hosts = self.exec_ssh_command('lshost')
            host_res = hosts.split('\n')
            for i in range(1, len(host_res)):
                if host_res[i] is None or host_res[i] == '':
                    continue
                control_str = ' '.join(host_res[i].split())
                str_info = control_str.split(' ')
                host_id = str_info[0]
                detail_command = 'lshost %s' % host_id
                deltail_info = self.exec_ssh_command(detail_command)
                host_map = {}
                self.handle_detail(deltail_info, host_map, split=' ')
                status = SSHHandler.HOST_STATUS_MAP.get(host_map.get('status'))
                host_result = {
                    "name": host_map.get('name'),
                    "storage_id": storage_id,
                    "native_storage_host_id": host_map.get('id'),
                    "os_type": SSHHandler.OS_TYPE_MAP.get(
                        host_map.get('type', '').lower()),
                    "status": status
                }
                host_list.append(host_result)
            return host_list
        except Exception as e:
            LOG.error("Failed to get host metrics from svc")
            raise e

    def list_masking_views(self, storage_id):
        try:
            view_list = []
            hosts = self.exec_ssh_command('lshostvdiskmap')
            host_res = hosts.split('\n')
            for i in range(1, len(host_res)):
                if host_res[i] is None or host_res[i] == '':
                    continue
                control_str = ' '.join(host_res[i].split())
                str_info = control_str.split(' ')
                if len(str_info) > 3:
                    host_id = str_info[0]
                    vdisk_id = str_info[3]
                    view_id = '%s_%s' % (str_info[0], str_info[3])
                    view_result = {
                        "name": view_id,
                        "native_storage_host_id": host_id,
                        "storage_id": storage_id,
                        "native_volume_id": vdisk_id,
                        "native_masking_view_id": view_id,
                    }
                    view_list.append(view_result)
            return view_list
        except Exception as e:
            LOG.error("Failed to get view metrics from svc")
            raise e

    def list_storage_host_initiators(self, storage_id):
        try:
            initiator_list = []
            hosts = self.exec_ssh_command('lshost')
            host_res = hosts.split('\n')
            for i in range(1, len(host_res)):
                if host_res[i] is None or host_res[i] == '':
                    continue
                control_str = ' '.join(host_res[i].split())
                str_info = control_str.split(' ')
                host_id = str_info[0]
                detail_command = 'lshost %s' % host_id
                deltail_info = self.exec_ssh_command(detail_command)
                init_name = None
                type = None
                host_id = None
                for host in deltail_info.split('\n'):
                    if host:
                        strinfo = host.split(' ', 1)
                        key = strinfo[0]
                        value = None
                        if len(strinfo) > 1:
                            value = strinfo[1]
                        if key == 'WWPN':
                            init_name = value
                            type = 'fc'
                        elif key == 'iscsi_name':
                            init_name = value
                            type = 'iscsi'
                        elif key == 'id':
                            host_id = value
                        elif key == 'state' and init_name:
                            status = SSHHandler.INITIATOR_STATUS_MAP.get(value)
                            init_result = {
                                "name": init_name,
                                "storage_id": storage_id,
                                "native_storage_host_initiator_id": init_name,
                                "wwn": init_name,
                                "status": status,
                                "type": type,
                                "native_storage_host_id": host_id
                            }
                            initiator_list.append(init_result)
                            init_name = None
                            type = None
            return initiator_list
        except Exception as e:
            LOG.error("Failed to get initiators metrics from svc")
            raise e
