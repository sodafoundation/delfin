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
import codecs
import csv
import datetime
import hashlib
import os
import re
import shutil
import tarfile
import time

import six
import xlrd
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.macro_san.ms import consts
from delfin.drivers.macro_san.ms.consts import digital_constant
from delfin.drivers.macro_san.ms.macro_ssh_client import MacroSanSSHPool
from delfin.drivers.utils.tools import Tools

LOG = log.getLogger(__name__)


class MsHandler(object):

    def __init__(self, **kwargs):
        self.ssh_pool = MacroSanSSHPool(**kwargs)
        ssh_access = kwargs.get('ssh')
        self.ssh_host = ssh_access.get('host')
        self.down_lock = True

    def login(self):
        res = ''
        try:
            res = self.ssh_pool.do_exec_shell([consts.ODSP_SH])
        except Exception as e:
            LOG.error('Failed to ssh login macro_san %s' % (
                six.text_type(e)))
        if consts.UNKNOWN_COMMAND_TAG in res:
            try:
                self.ssh_pool.do_exec_shell([consts.SYSTEM_QUERY])
                self.down_lock = False
            except Exception as e:
                LOG.error('Failed to cli login macro_san %s' % (
                    six.text_type(e)))
                raise e

    def get_storage(self, storage_id):
        storage_data_map = self.get_data_query(consts.SYSTEM_QUERY)
        if not storage_data_map:
            raise exception.SSHException('The command returns empty data')
        device_uuid = storage_data_map.get('DeviceUUID')
        storage_serial_number = storage_data_map.get('DeviceSerialNumber')
        serial_number = f'{self.ssh_host}:{storage_serial_number}'\
            if storage_serial_number else f'{self.ssh_host}:{device_uuid}'
        storage_name = storage_data_map.get('DeviceName')
        storage_model = storage_data_map.get('DeviceModel')
        storage_vendor = storage_data_map.get('DeviceVender')
        firmware_version = self.get_firmware_version()
        pools = self.list_storage_pools(storage_id)
        total_capacity = digital_constant.ZERO_INT
        used_capacity = digital_constant.ZERO_INT
        for pool in pools:
            total_capacity += pool.get('total_capacity')
            used_capacity += pool.get('used_capacity')
        disks = self.list_disks(storage_id)
        raw_capacity = digital_constant.ZERO_INT
        for disk in disks:
            raw_capacity += disk.get('capacity')
        storage_status = self.get_storage_status(storage_id)
        model = storage_model if storage_model else\
            self.get_storage_model(storage_id)
        storage = {
            'name': storage_name if storage_name else device_uuid,
            'vendor': storage_vendor if storage_vendor else
            consts.STORAGE_VENDOR,
            'status': storage_status,
            'model': model,
            'serial_number': serial_number,
            'firmware_version': firmware_version,
            'raw_capacity': raw_capacity,
            'total_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': total_capacity - used_capacity
        }
        return storage

    def get_storage_model(self, storage_id):
        storage_model = ''
        if not self.down_lock:
            return storage_model
        local_path = self.download_model_file(storage_id)
        if local_path:
            try:
                storage_model = self.analysis_model_file(local_path,
                                                         storage_model)
            finally:
                shutil.rmtree(local_path)
        return storage_model

    @staticmethod
    def analysis_model_file(local_path, storage_model):
        list_dir = os.listdir(local_path)
        for dir_name in list_dir:
            excel = xlrd.open_workbook('{}/{}'.format(local_path, dir_name))
            sheet = excel[consts.digital_constant.ZERO_INT]
            rows_data_list = sheet.row_values(consts.digital_constant.ONE_INT)
            for rows_data in rows_data_list:
                title_pattern = re.compile(consts.STORAGE_INFO_MODEL_REGULAR)
                title_search_obj = title_pattern.search(rows_data)
                if title_search_obj:
                    storage_model = rows_data
                    break
        return storage_model

    def download_model_file(self, storage_id):
        sftp = None
        local_path = ''
        try:
            ssh = self.ssh_pool.create()
            sftp = ssh.open_sftp()
            file_name_list = sftp.listdir(consts.FTP_PATH_TMP)
            for file_name in file_name_list:
                title_pattern = re.compile(consts.STORAGE_INFO_REGULAR)
                title_search_obj = title_pattern.search(file_name)
                if title_search_obj:
                    os_path = os.getcwd()
                    localtime = int(time.mktime(time.localtime())) * units.k
                    local_path = consts.MODEL_PATH.format(
                        os_path, storage_id, localtime)
                    os.mkdir(local_path)
                    local_path_file = '{}/{}'.format(local_path, file_name)
                    sftp.get(consts.FTP_PATH_FILE.format(file_name),
                             local_path_file)
                    break
        except Exception as e:
            LOG.error('Failed to down storage model file macro_san %s' %
                      (six.text_type(e)))
        if sftp:
            sftp.close()
        return local_path

    def get_firmware_version(self):
        firmware_version = None
        version_map = self.get_storage_version()
        for sp_num in range(
                consts.digital_constant.ONE_INT,
                len(version_map) + consts.digital_constant.ONE_INT):
            sp_key = '{}{}'.format(consts.SP, sp_num)
            firmware_version = \
                version_map.get(sp_key, {}).get('{}{}'.format(
                    sp_key, consts.ODSP_MSC_VERSION_KEY))
            if consts.FIELDS_INITIATOR_HOST != firmware_version:
                break
        return firmware_version

    def get_storage_status(self, storage_id):
        storage_status = constants.StorageStatus.NORMAL
        ha_status_map = self.get_data_query(consts.HA_STATUS)
        ha_status = ha_status_map.get('SystemHAStatus')
        if ha_status:
            storage_status = consts.STORAGE_STATUS_MAP.get(
                ha_status.lower(), constants.StorageStatus.UNKNOWN)
        else:
            controllers_list = self.list_controllers(storage_id)
            for controllers in controllers_list:
                controllers_status = controllers.get('status')
                if controllers_status in constants.ControllerStatus.FAULT:
                    storage_status = constants.StorageStatus.ABNORMAL
        return storage_status

    def list_storage_pools(self, storage_id):
        pool_list = []
        pools = self.get_data_list(consts.POOL_LIST, consts.FIELDS_NAME)
        for pool in pools:
            pool_name = pool.get('Name')
            health_status = self.get_pool_status(pool_name)
            all_capacity_str = pool.get('AllCapacity').replace(',', '')\
                if pool.get('AllCapacity') else ''
            total_capacity_str = pool.get('TotalCapacity').replace(',', '')\
                if pool.get('TotalCapacity') else ''
            total_capacity = Tools.get_capacity_size(all_capacity_str)\
                if all_capacity_str else\
                Tools.get_capacity_size(total_capacity_str)
            used_capacity = Tools.get_capacity_size(
                pool.get('UsedCapacity').replace(',', ''))
            pool_model = {
                'name': pool_name,
                'storage_id': storage_id,
                'native_storage_pool_id': pool_name,
                'status': health_status,
                'storage_type': constants.StorageType.BLOCK,
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'free_capacity': total_capacity - used_capacity
            }
            pool_list.append(pool_model)
        return pool_list

    def get_pool_status(self, pool_name):
        raids = self.get_data_list(consts.RAID_LIST.format(pool_name),
                                   consts.FIELDS_NAME)
        pool_status = constants.StoragePoolStatus.UNKNOWN
        if raids:
            pool_status = constants.StoragePoolStatus.NORMAL
        for raid in raids:
            health_status = raid.get('HealthStatus').lower() \
                if raid.get('HealthStatus') else None
            if health_status in consts.POOL_STATUS_ABNORMAL.ALL:
                pool_status = constants.StoragePoolStatus.ABNORMAL
                break
            if health_status == constants.StoragePoolStatus.DEGRADED:
                pool_status = constants.StoragePoolStatus.DEGRADED
                break
            if health_status not in consts.POOL_STATUS_NORMAL.ALL:
                pool_status = constants.StoragePoolStatus.UNKNOWN
        return pool_status

    def list_volumes(self, storage_id):
        volume_list = []
        pool_volumes = self.get_volumes(storage_id)
        for volume in pool_volumes:
            status = volume.get('HealthStatus').lower() \
                if volume.get('HealthStatus') else None
            total_capacity = self.get_total_capacity(volume)
            thin_provisioning = volume.get('Thin-Provisioning').lower() \
                if volume.get('Thin-Provisioning') else None
            used_capacity = self.get_used_capacity(thin_provisioning,
                                                   total_capacity, volume)
            volume_model = {
                'name': volume.get('Name'),
                'storage_id': storage_id,
                'status': consts.LIST_VOLUMES_STATUS_MAP.get(
                    status, constants.StorageStatus.UNKNOWN),
                'native_volume_id': volume.get('Name'),
                'native_storage_pool_id': volume.get('Owner(Pool)'),
                'type': consts.VOLUME_TYPE_MAP.get(
                    thin_provisioning, constants.VolumeType.THICK),
                'wwn': volume.get('DeviceID') if
                volume.get('DeviceID') else volume.get('WWN'),
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'free_capacity': total_capacity - used_capacity
            }
            volume_list.append(volume_model)
        return volume_list

    @staticmethod
    def get_used_capacity(thin_provisioning, total_capacity, volume):
        if consts.FIELDS_ENABLE == thin_provisioning:
            used_capacity_str = volume.get('Thin-LUNUsedCapacity')
            number_b = used_capacity_str.index('B')
            used_capacity =\
                used_capacity_str[:number_b + consts.digital_constant.ONE_INT]
            used_capacity = Tools.get_capacity_size(
                used_capacity.replace(',', ''))
        else:
            used_capacity = total_capacity
        return used_capacity

    @staticmethod
    def get_total_capacity(volume):
        total_size = volume.get('TotalSize')
        if not total_size:
            physical_size = volume.get('TotalPhysicalSize')
            number_b = physical_size.index('B')
            total_size = \
                physical_size[:number_b + consts.digital_constant.ONE_INT]
        total_capacity = Tools.get_capacity_size(total_size.replace(',', ''))
        return total_capacity

    def list_controllers(self, storage_id):
        controllers_list = []
        sp_map = self.get_storage_version()
        cpu_map = self.get_cup_information()
        ha_status_map = self.get_data_query(consts.HA_STATUS)
        for sp_name in sp_map.keys():
            status_key = '{}{}'.format(sp_name, consts.HA_RUNNING_STATUS)
            status = ha_status_map.get(status_key).lower() \
                if ha_status_map.get(status_key) else None
            soft_version = sp_map.get(sp_name, {}).get(
                '{}{}'.format(sp_name, consts.ODSP_MSC_VERSION_KEY))
            cpu_vendor_id = cpu_map.get(sp_name, {}).get(
                '{}{}'.format(sp_name, consts.PROCESSOR_VENDOR_KEY))
            cpu_frequency = cpu_map.get(sp_name, {}).get(
                '{}{}'.format(sp_name, consts.PROCESSOR_FREQUENCY_KEY))
            cpu_info = ''
            if cpu_vendor_id and cpu_frequency:
                cpu_info = '{}@{}'.format(cpu_vendor_id, cpu_frequency)
            controller_model = {
                'name': sp_name,
                'storage_id': storage_id,
                'native_controller_id': sp_name,
                'status': consts.CONTROLLERS_STATUS_MAP.get(
                    status, constants.ControllerStatus.UNKNOWN),
                'location': sp_name,
                'soft_version': soft_version,
                'cpu_info': cpu_info
            }
            if cpu_info:
                controller_model['cpu_count'] = consts.digital_constant.ONE_INT
            controllers_list.append(controller_model)
        return controllers_list

    def get_cup_information(self):
        cpu_res = self.do_exec(consts.SYSTEM_CPU)
        sp_map = {}
        if cpu_res:
            cpu_res_list = cpu_res.strip(). \
                replace('\r', '').split('\n')
            sp_cpu_map = {}
            sp = None
            bag = True
            for row_cpu in (cpu_res_list or []):
                row_pattern = re.compile(consts.SYSTEM_CPU_SP_REGULAR)
                row_search = row_pattern.search(row_cpu)
                if row_search:
                    bag = False
                    sp = row_cpu.replace(
                        consts.LEFT_HALF_BRACKET, '').replace(
                        consts.CPU_INFORMATION_BRACKET, '').replace(' ', '')
                if bag:
                    continue
                if consts.COLON in row_cpu:
                    row_version_list = row_cpu.replace(' ', '').split(
                        consts.COLON, digital_constant.ONE_INT)
                    key = row_version_list[digital_constant.ZERO_INT]
                    sp_cpu_map[key] = row_version_list[
                        digital_constant.ONE_INT]
                if not row_cpu:
                    sp_map[sp] = sp_cpu_map
                    sp_cpu_map = {}
                    sp = None
        return sp_map

    def list_disks(self, storage_id):
        disk_list = []
        disks = self.get_disks()
        for disk in disks:
            disk_name = disk.get('Name')
            physical = disk.get('Type').lower() if disk.get('Type') else None
            logical = disk.get('Role').lower() if disk.get('Role') else None
            status = disk.get('HealthStatus').lower() if \
                disk.get('HealthStatus') else None
            disk_model = {
                'name': disk_name,
                'storage_id': storage_id,
                'native_disk_id': disk_name,
                'serial_number': disk.get('SerialNumber'),
                'manufacturer': disk.get('Vendor'),
                'model': disk.get('Model'),
                'firmware': disk.get('FWVersion'),
                'location': disk_name,
                'speed': int(disk.get('RPMs')) if disk.get('RPMs') else '',
                'capacity': Tools.get_capacity_size(disk.get('Capacity')),
                'status': consts.DISK_STATUS_MAP.get(
                    status, constants.DiskStatus.NORMAL),
                'physical_type': consts.DISK_PHYSICAL_TYPE_MAP.get(
                    physical, constants.DiskPhysicalType.UNKNOWN),
                'logical_type': consts.DISK_LOGICAL_TYPE_MAP.get(
                    logical, constants.DiskLogicalType.UNKNOWN)
            }
            disk_list.append(disk_model)
        return disk_list

    def list_ports(self, storage_id):
        ports = self.get_fc_port_encapsulation(storage_id)
        ports.extend(self.get_sas_port_data(storage_id))
        return ports

    def get_fc_port_encapsulation(self, storage_id):
        ports = []
        fc_port_map = self.get_fc_port()
        for fc_port_id in fc_port_map.keys():
            fc_port_id_upper = fc_port_id.upper()
            port_type = self.get_port_type(fc_port_id.lower())
            fc_ports = fc_port_map.get(fc_port_id)
            status_int = fc_ports.get('onlinestate')
            native_parent_id = '{}{}'.format(
                consts.SP, self.numbers_character(fc_port_id))
            fc_port_m = {
                'native_port_id': fc_port_id_upper,
                'name': fc_port_id_upper,
                'type': port_type,
                'logical_type': constants.PortLogicalType.PHYSICAL,
                'connection_status': consts.PORT_CONNECTION_STATUS_MAP.get(
                    status_int, constants.PortConnectionStatus.UNKNOWN),
                'health_status': constants.PortHealthStatus.UNKNOWN,
                'location': fc_port_id_upper,
                'storage_id': storage_id,
                'native_parent_id': native_parent_id,
                'speed': Tools.get_capacity_size(fc_ports.get('actualspeed')),
                'wwn': fc_ports.get('wwn')
            }
            ports.append(fc_port_m)
        return ports

    @staticmethod
    def parse_alert(alert):
        try:
            if consts.PARSE_ALERT_DESCRIPTION in alert.keys():
                alert_name = alert.get(consts.PARSE_ALERT_NAME)
                alert_name_e = alert_name.lower()
                alert_name_c = consts.ALERT_NAME_CONFIG.get(
                    alert_name_e, alert_name)
                alert_model = dict()
                description = alert.get(consts.PARSE_ALERT_DESCRIPTION)\
                    .encode('iso-8859-1').decode('gbk')
                alert_model['alert_id'] = alert.get(
                    consts.PARSE_ALERT_ALERT_ID)
                alert_model['severity'] = consts.PARSE_ALERT_SEVERITY_MAP.get(
                    alert.get(consts.PARSE_ALERT_SEVERITY),
                    constants.Severity.NOT_SPECIFIED)
                alert_model['category'] = constants.Category.FAULT
                alert_model['occur_time'] = Tools().time_str_to_timestamp(
                    alert.get(consts.PARSE_ALERT_TIME), consts.TIME_PATTERN)
                alert_model['description'] = description
                alert_model['location'] = '{}:{}'.format(alert.get(
                    consts.PARSE_ALERT_STORAGE),
                    alert.get(consts.PARSE_ALERT_LOCATION))
                alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                alert_model['alert_name'] = alert_name_c
                match_key = '{}{}'.format(alert_name_c, description)
                alert_model['match_key'] = hashlib.md5(
                    match_key.encode()).hexdigest()
                return alert_model
        except Exception as e:
            err_msg = "Failed to parse alert from " \
                      "macro_san ms: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_storage_host_initiators(self, storage_id):
        initiators_list = []
        initiators = self.get_data_list(
            consts.CLIENT_INITIATOR_GETLIST, consts.FIELDS_INITIATOR_ALIAS)
        for initiator in initiators:
            host_name = initiator.get('MappedClient') \
                if initiator.get('MappedClient') else initiator.get(
                'MappedHost')
            wwn = initiator.get('InitiatorWWN')
            online_status = initiator.get('OnlineStatus').lower() \
                if initiator.get('OnlineStatus') else None
            initiator_type = initiator.get('Type').lower() \
                if initiator.get('Type') else None
            initiator_d = {
                'native_storage_host_initiator_id': wwn,
                'name': wwn,
                'alias': initiator.get('InitiatorAlias'),
                'type': consts.INITIATOR_TYPE_MAP.get(
                    initiator_type, constants.InitiatorType.UNKNOWN),
                'status': consts.INITIATOR_STATUS_MAP.get(
                    online_status, constants.InitiatorStatus.UNKNOWN),
                'wwn': wwn,
                'storage_id': storage_id
            }
            if consts.FIELDS_INITIATOR_HOST != host_name:
                initiator_d['native_storage_host_id'] = host_name
            initiators_list.append(initiator_d)
        return initiators_list

    def list_storage_hosts_old(self, storage_id):
        host_list = []
        initiators_host_relation = self.get_initiators_host_relation()
        hosts = self.get_data_list(consts.CLIENT_LIST, consts.FIELDS_NAME, '')
        for host in hosts:
            host_name = host.get('Name')
            initiators = initiators_host_relation.get(host_name)
            os_type = constants.HostOSTypes.UNKNOWN
            if initiators:
                os_str = initiators.get('OS').lower() \
                    if initiators.get('OS') else None
                os_type = consts.HOST_OS_TYPES_MAP.get(
                    os_str, constants.HostOSTypes.UNKNOWN)
            host_d = {
                'name': host_name,
                'storage_id': storage_id,
                'native_storage_host_id': host_name,
                'os_type': os_type,
                'status': constants.HostStatus.NORMAL,
                'description': host.get('Description')
            }
            host_list.append(host_d)
        return host_list

    def list_storage_hosts_new(self, storage_id):
        hosts_new = self.get_data_list(consts.CLIENT_HOST,
                                       consts.FIELDS_HOST_NAME, '')
        host_list = []
        for host in hosts_new:
            host_name = host.get('Host Name')
            os = host.get('OS').lower() if host.get('OS') else None
            host_d = {
                'name': host_name,
                'storage_id': storage_id,
                'native_storage_host_id': host_name,
                'os_type': consts.HOST_OS_TYPES_MAP.get(
                    os, constants.HostOSTypes.UNKNOWN),
                'status': constants.HostStatus.NORMAL,
                'description': host.get('Description')
            }
            if consts.FIELDS_INITIATOR_HOST != host.get('IP Address'):
                host_d['ip_address'] = host.get('IP Address')
            host_list.append(host_d)
        return host_list

    def list_storage_host_groups(self, storage_id):
        host_groups = self.get_data_list(consts.HOST_GROUP,
                                         consts.FIELDS_HOST_GROUP_NAME, '')
        storage_host_groups = []
        host_grp_relation_list = []
        for host_group in host_groups:
            host_group_name = host_group.get('Host Group Name')
            host_g = {
                'name': host_group_name,
                'storage_id': storage_id,
                'native_storage_host_group_id': host_group_name,
                'description': host_group.get('Description')
            }
            storage_host_groups.append(host_g)
            hosts = self.get_data_list(
                consts.HOST_GROUP_N.format(host_group_name),
                consts.FIELDS_HOST_NAME_TWO)
            for host in hosts:
                host_name = host.get('HostName')
                host_group_relation = {
                    'storage_id': storage_id,
                    'native_storage_host_group_id': host_group_name,
                    'native_storage_host_id': host_name
                }
                host_grp_relation_list.append(host_group_relation)
        result = {
            'storage_host_groups': storage_host_groups,
            'storage_host_grp_host_rels': host_grp_relation_list
        }
        return result

    def list_volume_groups(self, storage_id):
        volume_groups = self.get_data_list(consts.VOLUME_GROUP,
                                           consts.FIELDS_VOLUME_GROUP_NAME, '')
        volume_group_list = []
        volume_grp_relation_list = []
        for volume_group in volume_groups:
            volume_group_name = volume_group.get('LUN Group Name')
            volume_g = {
                'name': volume_group_name,
                'storage_id': storage_id,
                'native_volume_group_id': volume_group_name,
                'description': volume_group.get('Description')
            }
            volume_group_list.append(volume_g)
            volumes = self.get_data_list(
                consts.VOLUME_GROUP_N.format(volume_group_name),
                consts.FIELDS_LUN_NAME)
            for volume in volumes:
                volume_name = volume.get('LUNName')
                volume_group_relation = {
                    'storage_id': storage_id,
                    'native_volume_group_id': volume_group_name,
                    'native_volume_id': volume_name
                }
                volume_grp_relation_list.append(volume_group_relation)
        result = {
            'volume_groups': volume_group_list,
            'vol_grp_vol_rels': volume_grp_relation_list
        }
        return result

    def list_masking_views_old(self, storage_id):
        views = []
        hosts = self.get_data_list(consts.CLIENT_LIST, consts.FIELDS_NAME)
        for host in hosts:
            host_name = host.get('Name')
            masking_list = self.get_data_list(
                consts.SHARE_LUN_LIST.format(host_name),
                consts.FIELDS_LUN_NAME)
            for masking_object in masking_list:
                volume_id = masking_object.get('LUNID')
                native_masking_view_id = '{}{}'.format(host_name, volume_id)
                view = {
                    'native_masking_view_id': native_masking_view_id,
                    'name': native_masking_view_id,
                    'native_storage_host_id': host_name,
                    'native_volume_id': volume_id,
                    'storage_id': storage_id
                }
                views.append(view)
        return views

    def list_masking_views_new(self, storage_id):
        views = self.get_data_list(consts.MAPVIEW, consts.FIELDS_MAPVIEW_NAME,
                                   '')
        views_list = []
        for view in views:
            mapview_name = view.get('Mapview Name')
            view_d = {
                'native_masking_view_id': mapview_name,
                'name': mapview_name,
                'native_storage_host_group_id': view.get('Host Group Name'),
                'native_volume_group_id': view.get('LUN Group Name'),
                'description': view.get('Description'),
                'storage_id': storage_id
            }
            views_list.append(view_d)
        return views_list

    def do_exec(self, command_str, sleep_time=1, mix_time=consts.TIME_LIMIT):
        if self.down_lock:
            try:
                res = self.ssh_pool.do_exec_shell(
                    [consts.ODSP_SH, command_str], sleep_time)
            except Exception as e:
                LOG.error('ssh Command(%s) execution info: %s' % (
                    command_str, six.text_type(e)))
                raise e
        else:
            try:
                res = self.ssh_pool.do_exec_shell([command_str], sleep_time)
            except Exception as e:
                LOG.error('cli Command(%s) execution info: %s' % (
                    command_str, six.text_type(e)))
                raise e
        if consts.FAILED_TAG in res or consts.UNKNOWN_COMMAND_TAG in res:
            return None
        if consts.SUCCESSFUL_TAG not in res:
            LOG.info('Command(%s) sleep(%s) return info: %s' %
                     (command_str, sleep_time, res))
            if sleep_time > mix_time:
                return None
            res = self.do_exec(command_str, sleep_time + 2, mix_time)
        return res

    def get_data_query(self, command):
        data_map = {}
        res = self.do_exec(command)
        if res is not None:
            row_res_list = res.strip().replace('\r', '').split('\n')
            for row_res in (row_res_list or []):
                if consts.COLON not in row_res:
                    continue
                row_data_list = row_res.replace(' ', '').split(
                    consts.COLON, digital_constant.ONE_INT)
                key = row_data_list[digital_constant.ZERO_INT]
                data_map[key] = row_data_list[digital_constant.ONE_INT]
        return data_map

    def get_storage_version(self):
        version_res = self.do_exec(consts.SYSTEM_VERSION)
        sp_map = {}
        if version_res:
            version_res_list = version_res.strip(). \
                replace('\r', '').split('\n')
            sp_version_map = {}
            sp = None
            bag = True
            for row_version in (version_res_list or []):
                row_pattern = re.compile(consts.SYSTEM_VERSION_SP_REGULAR)
                row_search = row_pattern.search(row_version)
                if row_search:
                    bag = False
                    sp = row_version.replace(
                        consts.LEFT_HALF_BRACKET, '').replace(
                        consts.AFTER_HALF_BRACKET, '').replace(' ', '')
                if bag:
                    continue
                if consts.COLON in row_version:
                    row_version_list = row_version.replace(' ', '').split(
                        consts.COLON, digital_constant.ONE_INT)
                    key = row_version_list[digital_constant.ZERO_INT]
                    sp_version_map[key] = row_version_list[
                        digital_constant.ONE_INT]
                    if consts.ODSP_DRIVER_VERSION_KEY in key:
                        sp_map[sp] = sp_version_map
                        sp_version_map = {}
        return sp_map

    def get_data_list(self, command, contains_fields, space=' ',
                      sleep_time=1, mix_time=consts.TIME_LIMIT):
        data_list = []
        res = self.do_exec(command, sleep_time, mix_time)
        if res:
            res_list = res.strip().replace('\r', '').split('\n\n')
            for object_str in (res_list or []):
                object_str = object_str.replace(space, '')
                if contains_fields not in object_str:
                    continue
                object_list = object_str.split('\n')
                data_map = {}
                for row_str in (object_list or []):
                    if consts.COLON not in row_str:
                        continue
                    row_list = row_str.split(
                        consts.COLON, digital_constant.ONE_INT)
                    key = row_list[digital_constant.ZERO_INT].strip()
                    data_map[key] = row_list[digital_constant.ONE_INT].strip()
                data_list.append(data_map)
        return data_list

    def get_volumes(self, storage_id):
        pools = self.list_storage_pools(storage_id)
        volumes = []
        for pool in pools:
            pool_name = pool.get('name')
            lun_list = self.get_data_list(
                consts.LUN_LIST.format(pool_name), consts.FIELDS_NAME)
            for lun in lun_list:
                lun_name = lun.get('Name')
                lun_query = self.get_data_query(
                    consts.LUN_QUERY.format(lun_name))
                if lun_query:
                    volumes.append(lun_query)
        return volumes

    def get_disks(self):
        disk_list = []
        dsu_list = self.get_data_list(consts.DSU_LIST, consts.FIELDS_NAME)
        for dsu in dsu_list:
            dsu_name = dsu.get('Name')
            if not dsu_name:
                continue
            dsu_id = dsu_name.replace(consts.DSU, '')
            disks = self.get_data_list(
                consts.DISK_LIST.format(dsu_id), consts.FIELDS_NAME)
            for disk in disks:
                disk_name = disk.get('Name')
                if not disk_name:
                    continue
                disk_id = disk_name.replace(consts.DISK, '')
                disk_map = self.get_data_query(
                    consts.DISK_QUERY.format(disk_id))
                if disk_map:
                    disk_list.append(disk_map)
        return disk_list

    def get_fc_port(self):
        target_port_res = self.do_exec(consts.TARGET_QUERY_PORT_LIST)
        fc_port = {}
        if target_port_res:
            bag = True
            port_id = None
            port_map = {}
            target_port_list = target_port_res.replace('\r', '').split('\n')
            for port_row_str in target_port_list:
                port_row_str = port_row_str.replace(' ', '')
                row_pattern = re.compile(consts.TARGET_PORT_REGULAR)
                row_search = row_pattern.search(port_row_str)
                if row_search:
                    if port_map:
                        fc_port[port_id] = port_map
                        port_map = {}
                    port_id = port_row_str.replace(consts.PORT, '')
                    bag = False
                    continue
                if bag:
                    continue
                if consts.COLON in port_row_str:
                    port_row_list = port_row_str.split(
                        consts.COLON, digital_constant.ONE_INT)
                    port_key = port_row_list[digital_constant.ZERO_INT]
                    port_map[port_key] = port_row_list[
                        digital_constant.ONE_INT]
                if consts.PORT_SUCCESSFUL_TAG in port_row_str:
                    fc_port[port_id] = port_map
        return fc_port

    def get_sas_port_data(self, storage_id):
        sas_list = []
        try:
            ha_status_map = self.get_data_query(consts.HA_STATUS)
            for ha_status_key in ha_status_map.keys():
                if consts.SP not in ha_status_key:
                    continue
                sp_num = ha_status_key.replace(
                    consts.HA_RUNNING_STATUS, '').replace(consts.SP, '')
                dsu_list = self.get_data_list(consts.DSU_LIST,
                                              consts.FIELDS_NAME)
                for dsu in dsu_list:
                    dsu_num = self.numbers_character(dsu.get('Name'))
                    sas_data_map = self.get_sas_data_list(
                        consts.SAS_PORT_LIST.format(sp_num, dsu_num),
                        consts.FIELDS_LINK_STATUS)
                    self.get_sas_encapsulation_data(sas_data_map, sas_list,
                                                    storage_id)
        finally:
            return sas_list

    def get_sas_encapsulation_data(self, sas_data_map, sas_list, storage_id):
        for sas_port_id in sas_data_map.keys():
            sas_object_map = sas_data_map.get(sas_port_id)
            status = sas_object_map.get(
                '{} Link Status'.format(sas_port_id))
            max_speed = sas_object_map.get(
                '{} PHY Max Speed'.format(sas_port_id))
            speed = sas_object_map.get(
                '{} PHY1 Speed'.format(sas_port_id))
            native_parent_id = '{}{}'.format(
                consts.SP, self.numbers_character(sas_port_id))
            sas_port_m = {
                'native_port_id': sas_port_id,
                'name': sas_port_id,
                'type': constants.PortType.SAS,
                'logical_type': constants.PortLogicalType.PHYSICAL,
                'connection_status': consts.PORT_CONNECTION_STATUS_MAP.get(
                    status, constants.PortConnectionStatus.UNKNOWN),
                'health_status': constants.PortHealthStatus.UNKNOWN,
                'location': sas_port_id,
                'storage_id': storage_id,
                'native_parent_id': native_parent_id,
                'max_speed': self.capacity_conversion(max_speed),
                'speed': self.capacity_conversion(speed)
            }
            sas_list.append(sas_port_m)

    @staticmethod
    def capacity_conversion(capacity_str):
        capacity_int = consts.digital_constant.ZERO_INT
        if consts.GBPS in capacity_str:
            capacity_int = int(capacity_str.replace(consts.GBPS, '')) * units.G
        elif consts.MBPS in capacity_str:
            capacity_int = int(capacity_str.replace(consts.GBPS, '')) * units.M
        elif consts.KBPS in capacity_str:
            capacity_int = int(capacity_str.replace(consts.GBPS, '')) * units.k
        return capacity_int

    def get_sas_data_list(self, command, contains_fields):
        sas_data = {}
        res = self.do_exec(command)
        if res:
            res_list = res.strip().replace('\r', '').split('\n\n')
            for object_str in (res_list or []):
                if contains_fields not in object_str:
                    continue
                object_list = object_str.split('\n')
                sas_object = {}
                sas_data_key = None
                for row_str in (object_list or []):
                    if consts.COLON not in row_str:
                        continue
                    object_num = row_str.rindex(consts.COLON)
                    object_key = row_str[:object_num].strip()
                    object_num_one = object_num + consts.digital_constant. \
                        ONE_INT
                    sas_object[object_key] = row_str[object_num_one:].strip()
                    if consts.FIELDS_LINK_STATUS in row_str:
                        sas_data_num = row_str.index(' ')
                        sas_data_key = row_str[:sas_data_num]
                sas_data[sas_data_key] = sas_object
        return sas_data

    @staticmethod
    def get_port_type(fc_port_id_lower):
        if constants.PortType.FC in fc_port_id_lower:
            port_type = constants.PortType.FC
        elif constants.PortType.ISCSI in fc_port_id_lower:
            port_type = constants.PortType.ISCSI
        elif constants.PortType.SAS in fc_port_id_lower:
            port_type = constants.PortType.SAS
        elif constants.PortType.ETH in fc_port_id_lower:
            port_type = constants.PortType.ETH
        else:
            port_type = constants.PortType.OTHER
        return port_type

    @staticmethod
    def numbers_character(character_string):
        for character in list(character_string):
            if character.isdigit():
                return character

    def get_initiators_host_relation(self):
        initiators_host = {}
        initiators = self.get_data_list(
            consts.CLIENT_INITIATOR_GETLIST, consts.FIELDS_INITIATOR_ALIAS)
        for initiator in initiators:
            host_id = initiator.get('MappedClient')
            initiators_host[host_id] = initiator
        return initiators_host

    def collect_perf_metrics(self, storage_id, resource_metrics, start_time,
                             end_time):
        metrics = []
        if not self.down_lock:
            return metrics
        LOG.info('The system(storage_id: %s) starts to collect macro_san'
                 ' performance, start_time: %s, end_time: %s',
                 storage_id, start_time, end_time)
        resource_storage = resource_metrics.get(constants.ResourceType.STORAGE)
        if resource_storage:
            storage_metrics = self.get_storage_metrics(
                end_time, resource_storage, start_time, storage_id)
            metrics.extend(storage_metrics)
            LOG.info('The system(storage_id: %s) stop to collect storage'
                     ' performance, The length is: %s',
                     storage_id, len(storage_metrics))
        file_name_map = self.get_identification()
        resource_volume = resource_metrics.get(constants.ResourceType.VOLUME)
        if resource_volume and file_name_map:
            volume_metrics = self.get_volume_metrics(
                end_time, resource_volume, start_time, storage_id,
                file_name_map)
            metrics.extend(volume_metrics)
            LOG.info('The system(storage_id: %s) stop to collect volume'
                     ' performance, The length is: %s',
                     storage_id, len(volume_metrics))
        resource_port = resource_metrics.get(constants.ResourceType.PORT)
        if resource_port:
            sas_port_metrics = self.get_port_metrics(
                end_time, resource_port, start_time, storage_id,
                consts.SAS_PORT, consts.SASPORT_REGULAR)
            metrics.extend(sas_port_metrics)
            LOG.info('The system(storage_id: %s) stop to collect sas port'
                     ' performance, The length is: %s',
                     storage_id, len(sas_port_metrics))
            if file_name_map:
                fc_port_metrics = self.get_fc_port_metrics(
                    end_time, resource_port, start_time, storage_id,
                    file_name_map)
                metrics.extend(fc_port_metrics)
                LOG.info('The system(storage_id: %s) stop to collect fc port'
                         ' performance, The length is: %s', storage_id,
                         len(fc_port_metrics))
        resource_disk = resource_metrics.get(constants.ResourceType.DISK)
        if resource_disk and file_name_map:
            disk_metrics = self.get_disk_metrics(
                end_time, resource_disk, start_time, storage_id, file_name_map)
            metrics.extend(disk_metrics)
            LOG.info('The system(storage_id: %s) stop to collect disk'
                     ' performance, The length is: %s',
                     storage_id, len(disk_metrics))
        return metrics

    def get_fc_port_metrics(self, end_time, resource_disk, start_time,
                            storage_id, file_name_map):
        local_path = self.down_perf_file(
            consts.FC_PORT, storage_id, consts.FCPORT_REGULAR, start_time)
        disk_metrics = []
        if local_path:
            metrics_data = None
            try:
                metrics_data = self.analysis_per_file(
                    local_path, start_time, end_time,
                    consts.FC_PORT, file_name_map)
            except Exception as e:
                LOG.error('Failed to fc port analysis per file %s' % (
                    six.text_type(e)))
            finally:
                shutil.rmtree(local_path)
            if metrics_data:
                disk_metrics = self.packaging_metrics(
                    storage_id, metrics_data, resource_disk,
                    constants.ResourceType.PORT)
        return disk_metrics

    def get_disk_metrics(self, end_time, resource_disk, start_time,
                         storage_id, file_name_map):
        local_path = self.down_perf_file(
            constants.ResourceType.DISK, storage_id, consts.DISK_REGULAR,
            start_time)
        disk_metrics = []
        if local_path:
            metrics_data = None
            try:
                metrics_data = self.analysis_per_file(
                    local_path, start_time, end_time,
                    constants.ResourceType.DISK, file_name_map)
            except Exception as e:
                LOG.error('Failed to disk analysis per file %s' % (
                    six.text_type(e)))
            finally:
                shutil.rmtree(local_path)
            if metrics_data:
                disk_metrics = self.packaging_metrics(
                    storage_id, metrics_data, resource_disk,
                    constants.ResourceType.DISK)
        return disk_metrics

    def get_port_metrics(self, end_time, resource_port, start_time,
                         storage_id, folder, pattern):
        local_path = self.down_perf_file(
            folder, storage_id, pattern, start_time)
        sas_port_metrics = []
        if local_path:
            metrics_data = None
            try:
                metrics_data = self.analysis_per_file(
                    local_path, start_time, end_time, folder)
            except Exception as e:
                LOG.error('Failed to sas port analysis per file %s' % (
                    six.text_type(e)))
            finally:
                shutil.rmtree(local_path)
            if metrics_data:
                sas_port_metrics = self.packaging_metrics(
                    storage_id, metrics_data, resource_port,
                    constants.ResourceType.PORT)
        return sas_port_metrics

    def get_volume_metrics(self, end_time, resource_volume, start_time,
                           storage_id, file_name_map):
        local_path = self.down_perf_file(
            constants.ResourceType.VOLUME, storage_id, consts.LUN_REGULAR,
            start_time)
        volume_metrics = []
        if local_path:
            metrics_data = None
            try:
                # uuid_map = self.get_volume_uuid()
                metrics_data = self.analysis_per_file(
                    local_path, start_time, end_time,
                    constants.ResourceType.VOLUME, file_name_map)
            except Exception as e:
                LOG.error('Failed to volume analysis per file %s' % (
                    six.text_type(e)))
            finally:
                shutil.rmtree(local_path)
            if metrics_data:
                volume_metrics = self.packaging_metrics(
                    storage_id, metrics_data, resource_volume,
                    constants.ResourceType.VOLUME)
        return volume_metrics

    def get_storage_metrics(self, end_time, resource_storage, start_time,
                            storage_id):
        local_path = self.down_perf_file(
            constants.ResourceType.STORAGE, storage_id, consts.STRAGE_REGULAR,
            start_time)
        storage_metrics = []
        if local_path:
            metrics_data = None
            try:
                metrics_data = self.analysis_per_file(
                    local_path, start_time, end_time,
                    constants.ResourceType.STORAGE)
            except Exception as e:
                LOG.error('Failed to storage analysis per file %s' % (
                    six.text_type(e)))
            finally:
                shutil.rmtree(local_path)
            if metrics_data:
                resource_id, resource_name = self.get_storages()
                storage_metrics = self.storage_packaging_data(
                    storage_id, metrics_data, resource_storage,
                    resource_id, resource_name)
        return storage_metrics

    def get_storages(self):
        storage_data_map = self.get_data_query(consts.SYSTEM_QUERY)
        device_uuid = storage_data_map.get('DeviceUUID')
        storage_name = storage_data_map.get('DeviceName')
        resource_name = storage_name if storage_name else device_uuid
        storage_serial_number = storage_data_map.get('DeviceSerialNumber')
        resource_id = f'{self.ssh_host}:{storage_serial_number}' \
            if storage_serial_number else f'{self.ssh_host}:{device_uuid}'
        return resource_id, resource_name

    def down_perf_file(self, folder, storage_id, pattern, start_time):
        sftp = None
        tar = None
        ssh = None
        local_path = ''
        try:
            ssh = self.ssh_pool.create()
            sftp = ssh.open_sftp()
            file_name_list = sftp.listdir(consts.FTP_PERF_PATH)
            ms_path = os.getcwd()
            localtime = int(round(time.time() * 1000))
            local_path = consts.ADD_FOLDER.format(
                ms_path, folder, storage_id, localtime)
            os.mkdir(local_path)
            file_time_dict = self.get_file_max_time(
                file_name_list, pattern, start_time)
            for file_name in file_name_list:
                title_pattern = re.compile(pattern)
                title_search_obj = title_pattern.search(file_name)
                if not title_search_obj:
                    continue
                time_int, time_ms = self.time_cycle(file_name)
                max_time = file_time_dict.get(file_name.replace(
                    time_int, '').replace(consts.CSV, '').replace('.tgz', ''))
                if time_ms < max_time:
                    continue
                local_path_file = '{}/{}'.format(local_path, file_name)
                ftp_path = '{}/{}'.format(consts.FTP_PERF_PATH, file_name)
                sftp.get(ftp_path, local_path_file)
                if consts.CSV in file_name:
                    continue
                tar = tarfile.open(local_path_file)
                tar.extractall(local_path)
        except Exception as e:
            LOG.error('Failed to down perf file %s macro_san %s' %
                      (folder, six.text_type(e)))
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()
        if tar:
            tar.close()
        return local_path

    @staticmethod
    def get_file_max_time(file_name_list, pattern, start_time):
        name_time_dict = {}
        for file_name_time in file_name_list:
            title_pattern = re.compile(pattern)
            title_search_obj = title_pattern.search(file_name_time)
            if not title_search_obj:
                continue
            time_int, time_ms = MsHandler.time_cycle(file_name_time)
            if time_ms > start_time:
                continue
            file_name = file_name_time.replace(
                time_int, '').replace(consts.CSV, '').replace('.tgz', '')
            exist_time_ms = name_time_dict.get(file_name)
            if exist_time_ms:
                if exist_time_ms > time_ms:
                    name_time_dict[file_name] = exist_time_ms
            else:
                name_time_dict[file_name] = time_ms
        return name_time_dict

    @staticmethod
    def time_cycle(file_name_time):
        time_int = file_name_time.split('_')[
            consts.digital_constant.MINUS_ONE_INT].replace(
            consts.CSV, '').replace('.tgz', '')
        time_ms = Tools().time_str_to_timestamp(
            time_int, consts.PERF_FILE_TIME)
        return time_int, time_ms

    def get_identification(self):
        identification = {}
        controller = self.get_controller()
        if not controller:
            return identification
        files = self.get_data_list(
            consts.SYSTEM_PERFORMANCE_FILE, consts.FIELDS_NAME,
            sleep_time=consts.INITIAL_WAITING_TIME,
            mix_time=consts.MAX_WAITING_TIME)
        for file in files:
            sp = file.get('SPName')
            file_name = file.get('FileName')
            if controller != sp or not file_name:
                continue
            identification[file_name] = file.get('ObjectName')
        return identification

    def get_controller(self):
        res = self.ssh_pool.do_exec_shell([consts.VERSION_SHOW],
                                          consts.digital_constant.ONE_INT)
        if res:
            res_list = res.strip().replace('\r', '').split('\n')
            for res in res_list:
                if consts.SPECIAL_VERSION in res:
                    controller = res.replace(' ', '').replace(
                        consts.SPECIAL_VERSION, '')
                    return controller

    def get_volume_uuid(self):
        uuid_map = {}
        pools = self.get_data_list(consts.POOL_LIST, consts.FIELDS_NAME)
        for pool in pools:
            pool_name = pool.get('Name')
            lun_list = self.get_data_list(
                consts.LUN_LIST.format(pool_name), consts.FIELDS_NAME)
            for lun in lun_list:
                lun_name = lun.get('Name')
                lun_query = self.get_data_query(
                    consts.LUN_QUERY.format(lun_name))
                uuid = lun_query.get('LUNUUID')
                uuid_map[uuid] = lun_name
        return uuid_map

    def analysis_per_file(self, local_path, start_time, end_time,
                          resource_type, uuid_map=None):
        resource_key_data = {}
        resource_key = None
        if constants.ResourceType.STORAGE == resource_type:
            resource_key = resource_type
        list_dir = os.listdir(local_path)
        for dir_name in list_dir:
            data = {}
            dir_name = dir_name.replace(' ', '')
            if consts.CSV not in dir_name:
                continue
            resource_key = self.get_resource_key(dir_name, resource_key,
                                                 resource_type, uuid_map)
            resource_data = resource_key_data.get(resource_key)
            if resource_data:
                data = resource_data
            with codecs.open('{}/{}'.format(local_path, dir_name),
                             encoding='utf-8-sig') as f:
                for row in csv.DictReader(
                        line.replace('\0', '') for line in f):
                    time_str = row.get('')
                    timestamp_s = self.get_timestamp_s(time_str)
                    timestamp_ms = timestamp_s * units.k
                    if timestamp_ms < start_time or timestamp_ms >= end_time:
                        continue
                    row_data, timestamp = self.get_perf_data(row, timestamp_s)
                    data[timestamp] = row_data
            resource_key_data[resource_key] = data
        return resource_key_data

    @staticmethod
    def get_resource_key(dir_name, resource_key, resource_type, uuid_map):
        if consts.SAS_PORT == resource_type:
            uuid_list = dir_name.replace(consts.PERF_SAS_PORT, '').split(
                consts.PERF_SP)
            resource_key = uuid_list[consts.digital_constant.ZERO_INT] \
                .replace('_', ':')
        if constants.ResourceType.DISK == resource_type or \
                consts.FC_PORT == resource_type or \
                constants.ResourceType.VOLUME == resource_type:
            resource_key = uuid_map.get(dir_name) if \
                uuid_map.get(dir_name) else \
                uuid_map.get(dir_name.replace('.csv', '.tgz'))
        return resource_key

    @staticmethod
    def get_perf_data(row, timestamp_s):
        timestamp = int(timestamp_s / consts.SIXTY) * consts.SIXTY * units.k
        throughput = round(
            int(row.get('r&w/throughput(B)')) / units.Mi, 3)
        r_throughput = round(
            int(row.get('r/throughput(B)')) / units.Mi, 3)
        w_throughput = round(
            int(row.get('w/throughput(B)')) / units.Mi, 3)
        response = round(
            int(row.get('r&w/avg_rsp_time(us)')) / units.k, 3)
        r_response = round(
            int(row.get('r/avg_rsp_time(us)')) / units.k, 3)
        w_response = round(
            int(row.get('w/avg_rsp_time(us)')) / units.k, 3)
        cache_hit_ratio = round(
            int(row.get('r&w/cacherate(%*100)')) / 100, 3)
        r_cache_hit_ratio = round(
            int(row.get('r/cacherate(%*100)')) / 100, 3)
        w_cache_hit_ratio = round(
            int(row.get('w/cacherate(%*100)')) / 100, 3)
        row_data = {
            constants.StorageMetric.IOPS.name: int(row.get('r&w/iops')),
            constants.StorageMetric.READ_IOPS.name: int(row.get('r/iops')),
            constants.StorageMetric.WRITE_IOPS.name: int(row.get('w/iops')),
            constants.StorageMetric.THROUGHPUT.name: throughput,
            constants.StorageMetric.READ_THROUGHPUT.name: r_throughput,
            constants.StorageMetric.WRITE_THROUGHPUT.name: w_throughput,
            constants.StorageMetric.RESPONSE_TIME.name: response,
            constants.StorageMetric.READ_RESPONSE_TIME.name: r_response,
            constants.StorageMetric.WRITE_RESPONSE_TIME.name: w_response,
            constants.StorageMetric.CACHE_HIT_RATIO.name: cache_hit_ratio,
            constants.StorageMetric.READ_CACHE_HIT_RATIO.name:
                r_cache_hit_ratio,
            constants.StorageMetric.WRITE_CACHE_HIT_RATIO.name:
                w_cache_hit_ratio
        }
        return row_data, timestamp

    @staticmethod
    def storage_packaging_data(storage_id, metrics_data, resource_metrics,
                               resource_id, resource_name):
        metrics = []
        for resource_key in resource_metrics.keys():
            labels = {
                'storage_id': storage_id,
                'resource_type': constants.ResourceType.STORAGE,
                'resource_id': resource_id,
                'resource_name': resource_name,
                'type': 'RAW',
                'unit': resource_metrics[resource_key]['unit']
            }
            resource_value = {}
            time_key_data = metrics_data.get(constants.ResourceType.STORAGE)
            for time_key in time_key_data.keys():
                resource_key_data = time_key_data.get(time_key)
                resource_data = resource_key_data.get(resource_key)
                resource_value[time_key] = resource_data
            metrics_res = constants.metric_struct(
                name=resource_key, labels=labels, values=resource_value)
            metrics.append(metrics_res)
        return metrics

    @staticmethod
    def packaging_metrics(storage_id, metrics_data, resource_metrics,
                          resource_type):
        metrics = []
        for resource_id in metrics_data.keys():
            for resource_key in resource_metrics.keys():
                labels = {
                    'storage_id': storage_id,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'resource_name': resource_id,
                    'type': 'RAW',
                    'unit': resource_metrics[resource_key]['unit']
                }
                resource_value = {}
                resource_data = metrics_data.get(resource_id)
                for time_key in resource_data.keys():
                    resource_value[time_key] = \
                        resource_data.get(time_key, {}).get(resource_key)
                if resource_value:
                    metrics_res = constants.metric_struct(
                        name=resource_key, labels=labels,
                        values=resource_value)
                    metrics.append(metrics_res)
        return metrics

    @staticmethod
    def get_timestamp_s(time_str):
        timestamp_s = \
            int(datetime.datetime.strptime(
                time_str, consts.MACRO_SAN_TIME_FORMAT).timestamp())
        return timestamp_s

    def get_latest_perf_timestamp(self):
        timestamp = None
        if not self.down_lock:
            return timestamp
        res = self.ssh_pool.do_exec_shell([consts.GET_DATE])
        if res:
            res_list = res.strip().replace('\r', '').split('\n')
            for row in res_list:
                if row.isdigit():
                    timestamp = int(
                        int(row) / consts.SIXTY) * consts.SIXTY * units.k
        return timestamp
