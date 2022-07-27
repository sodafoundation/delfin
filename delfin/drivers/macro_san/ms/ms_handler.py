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
import hashlib
import re

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.macro_san.ms import consts
from delfin.drivers.macro_san.ms.consts import digital_constant
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools

LOG = log.getLogger(__name__)


class MsHandler(object):

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    def login(self):
        try:
            self.ssh_pool.do_exec_shell([consts.SYSTEM_QUERY])
        except Exception as e:
            LOG.error('Failed to login macro_san %s' % (six.text_type(e)))
            raise e

    def get_storage(self, storage_id):
        storage_data_map = self.get_data_query(consts.SYSTEM_QUERY)
        serial_number = storage_data_map.get('DeviceUUID')
        storage_name = storage_data_map.get('DeviceName')
        version_map = self.get_storage_version()
        firmware_version = \
            version_map.get(consts.SP_KEY).get('{}{}'.format(
                consts.SP_KEY, consts.ODSP_MSC_VERSION_KEY))
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
        storage = {
            'name': storage_name if storage_name else serial_number,
            'vendor': consts.STORAGE_VENDOR,
            'status': storage_status,
            'serial_number': serial_number,
            'firmware_version': firmware_version,
            'raw_capacity': raw_capacity,
            'total_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': total_capacity - used_capacity
        }
        return storage

    def get_storage_status(self, storage_id):
        storage_status = constants.StorageStatus.UNKNOWN
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
            total_capacity = Tools.get_capacity_size(pool.get('AllCapacity'))
            used_capacity = Tools.get_capacity_size(pool.get('UsedCapacity'))
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
        LOG.info('pools:{}'.format(pool_list))
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
                'used_capacity': total_capacity,
                'free_capacity': digital_constant.ZERO_INT
            }
            volume_list.append(volume_model)
        return volume_list

    @staticmethod
    def get_total_capacity(volume):
        total_size = volume.get('TotalSize')
        if not total_size:
            physical_size = volume.get('TotalPhysicalSize')
            number_b = physical_size.index('B')
            total_size =\
                physical_size[:number_b + consts.digital_constant.ONE_INT]
        total_capacity = Tools.get_capacity_size(total_size)
        return total_capacity

    def list_controllers(self, storage_id):
        controllers_list = []
        sp_map = self.get_storage_version()
        ha_status_map = self.get_data_query(consts.HA_STATUS)
        for sp_name in sp_map.keys():
            status_key = '{}{}'.format(sp_name, consts.HA_RUNNING_STATUS)
            status = ha_status_map.get(status_key).lower()\
                if ha_status_map.get(status_key) else None
            soft_version = sp_map.get(sp_name).get(
                '{}{}'.format(sp_name, consts.ODSP_MSC_VERSION_KEY))
            controller_model = {
                'name': sp_name,
                'storage_id': storage_id,
                'native_controller_id': sp_name,
                'status': consts.CONTROLLERS_STATUS_MAP.get(
                    status, constants.ControllerStatus.UNKNOWN),
                'location': sp_name,
                'soft_version': soft_version
            }
            controllers_list.append(controller_model)
        return controllers_list

    def list_disks(self, storage_id):
        disk_list = []
        disks = self.get_disks()
        for disk in disks:
            disk_name = consts.SYS.format(disk.get('Name'))
            disk_type = disk.get('Type').lower() if disk.get('Type') else None
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
                'speed': int(disk.get('RPMs')),
                'capacity': Tools.get_capacity_size(disk.get('Capacity')),
                'status': consts.DISK_STATUS_MAP.get(
                    status, constants.DiskStatus.NORMAL),
                'physical_type': consts.DISK_PHYSICAL_TYPE_MAP.get(
                    disk_type, constants.DiskPhysicalType.UNKNOWN),
                'logical_type': constants.DiskLogicalType.UNKNOWN
            }
            disk_list.append(disk_model)
        return disk_list

    def list_ports(self, storage_id):
        fc_ports = self.get_fc_port_encapsulation(storage_id)
        fc_ports.extend(self.get_sas_port_data(storage_id))
        return fc_ports

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
                if alert_name in consts.NORMAL_ALERT.ALL:
                    return None
                alert_model = dict()
                description = alert.get(consts.PARSE_ALERT_DESCRIPTION)
                alert_model['alert_id'] = alert.get(
                    consts.PARSE_ALERT_ALERT_ID)
                alert_model['severity'] = consts.ALERT_SEVERITY_MAP.get(
                    alert_name, constants.Severity.NOT_SPECIFIED)
                alert_model['category'] = constants.Category.FAULT
                alert_model['occur_time'] = Tools().time_str_to_timestamp(
                    alert.get(consts.PARSE_ALERT_TIME), consts.TIME_PATTERN)
                alert_model['description'] = description
                alert_model['location'] = '{}:{}'.format(alert.get(
                    consts.PARSE_ALERT_STORAGE),
                    alert.get(consts.PARSE_ALERT_LOCATION))
                alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                alert_model['alert_name'] = alert.get(
                    consts.PARSE_ALERT_NAME)
                match_key = '{}{}'.format(alert_name, description)
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
            wwn = initiator.get('InitiatorWWN')
            initiator_type = initiator.get('Type').lower() \
                if initiator.get('Type') else None
            initiator_d = {
                'native_storage_host_initiator_id': wwn,
                'native_storage_host_id': initiator.get('MappedClient'),
                'name': wwn,
                'alias': initiator.get('InitiatorAlias'),
                'type': consts.INITIATOR_TYPE_MAP.get(
                    initiator_type, constants.InitiatorType.UNKNOWN),
                'status': constants.InitiatorStatus.UNKNOWN,
                'wwn': wwn,
                'storage_id': storage_id
            }
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
                os = initiators.get('OS').lower() \
                    if initiators.get('OS') else None
                os_type = consts.HOST_OS_TYPES_MAP.get(
                    os, constants.HostOSTypes.UNKNOWN)
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
                'description': host.get('Description'),
                'ip_address': host.get('IP Address')
            }
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

    def do_exec(self, command_str, sleep_time=0.5):
        try:
            res = self.ssh_pool.do_exec_shell([command_str], sleep_time)
        except Exception as e:
            LOG.error('Command(%s) execution error: %s' % (command_str,
                                                           six.text_type(e)))
            return None
        if consts.FAILED_TAG in res or consts.UNKNOWN_COMMAND_TAG in res:
            return None
        if consts.SUCCESSFUL_TAG not in res:
            LOG.error('Command(%s) sleep(%s) return error: %s' %
                      (command_str, sleep_time, res))
            if sleep_time > consts.TIME_LIMIT:
                return None
            res = self.do_exec(command_str, sleep_time + 0.5)
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
            version_res_list = version_res.strip().\
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
                if not row_version:
                    sp_map[sp] = sp_version_map
                    sp_version_map = {}
        return sp_map

    def get_data_list(self, command, contains_fields, space=' ',
                      sleep_time=0.5):
        data_list = []
        res = self.do_exec(command, sleep_time)
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
                    object_num_one = object_num + consts.digital_constant.\
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
