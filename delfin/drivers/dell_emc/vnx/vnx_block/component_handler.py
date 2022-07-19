# Copyright 2021 The SODA Authors.
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
import copy
import csv
import os
import re
import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.utils.tools import Tools

LOG = log.getLogger(__name__)


class ComponentHandler(object):

    def __init__(self, navi_handler):
        self.navi_handler = navi_handler

    def get_storage(self):
        domain = self.navi_handler.get_domain()
        agent = self.navi_handler.get_agent()
        status = constants.StorageStatus.NORMAL
        raw_cap = self.handle_disk_capacity()
        pool_capacity = self.handle_pool_capacity()
        if domain and agent:
            result = {
                'name': domain[0].get('node'),
                'vendor': consts.EMCVNX_VENDOR,
                'model': agent.get('model'),
                'status': status,
                'serial_number': agent.get('serial_no'),
                'firmware_version': agent.get('revision'),
                'total_capacity': pool_capacity.get('total_capacity'),
                'raw_capacity': int(raw_cap),
                'used_capacity': pool_capacity.get('used_capacity'),
                'free_capacity': pool_capacity.get('free_capacity')
            }
        else:
            err_msg = "domain or agent error: %s, %s" %\
                      (six.text_type(domain), six.text_type(agent))
            LOG.error(err_msg)
            raise exception.StorageBackendException(err_msg)
        return result

    def list_storage_pools(self, storage_id):
        pools = self.navi_handler.get_pools()
        pool_list = []
        if pools:
            for pool in pools:
                if pool.get('pool_name') is not None:
                    status = consts.STATUS_MAP.get(
                        pool.get('state'),
                        constants.StoragePoolStatus.OFFLINE)
                    used_cap = float(
                        pool.get("consumed_capacity_gbs")) * units.Gi
                    free_cap = float(
                        pool.get("available_capacity_gbs")) * units.Gi
                    total_cap = float(
                        pool.get("user_capacity_gbs")) * units.Gi
                    subscribed_cap = float(pool.get(
                        "total_subscribed_capacity_gbs")) * units.Gi
                    p = {
                        'name': pool.get('pool_name'),
                        'storage_id': storage_id,
                        'native_storage_pool_id': str(pool.get('pool_id')),
                        'description': pool.get('description'),
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_cap),
                        'subscribed_capacity': int(subscribed_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap)
                    }
                    pool_list.append(p)
        raid_groups = self.handle_raid_groups(storage_id)
        if raid_groups:
            pool_list.extend(raid_groups)
        return pool_list

    def handle_raid_groups(self, storage_id):
        raid_groups = self.navi_handler.get_raid_group()
        raid_list = []
        if raid_groups:
            for raid in raid_groups:
                if raid.get('raidgroup_id') is not None:
                    status = consts.STATUS_MAP.get(
                        raid.get('raidgroup_state'),
                        constants.StoragePoolStatus.OFFLINE)
                    free_cap = float(raid.get(
                        "free_capacity_blocks,non-contiguous"))
                    total_cap = float(
                        raid.get("logical_capacity_blocks"))
                    used_cap = total_cap - free_cap
                    p = {
                        'name': 'RAID Group %s' % raid.get('raidgroup_id'),
                        'storage_id': storage_id,
                        'native_storage_pool_id': '%s%s' % (
                            consts.RAID_GROUP_ID_PREFIX,
                            raid.get('raidgroup_id')),
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_cap * (units.Ki / 2)),
                        'used_capacity': int(used_cap * (units.Ki / 2)),
                        'free_capacity': int(free_cap * (units.Ki / 2))
                    }
                    raid_list.append(p)
        return raid_list

    def handle_volume_from_pool(self, volumes, pool_ids, storage_id):
        volume_list = []
        if volumes:
            for volume in volumes:
                if volume.get('name') is not None:
                    status = consts.STATUS_MAP.get(
                        volume.get('current_state'),
                        constants.StoragePoolStatus.OFFLINE)
                    orig_pool_name = volume.get('pool_name')
                    vol_type = consts.VOL_TYPE_MAP.get(
                        volume.get('is_thin_lun').lower())
                    volume_used_cap_str = volume.get('consumed_capacity_gbs')
                    used_cap = 0
                    if volume_used_cap_str and volume_used_cap_str != 'N/A':
                        used_cap = float(volume_used_cap_str) * units.Gi
                    total_cap = float(
                        volume.get('user_capacity_gbs')) * units.Gi
                    free_cap = total_cap - used_cap
                    if free_cap < 0:
                        free_cap = 0
                    v = {
                        'name': volume.get('name'),
                        'storage_id': storage_id,
                        'status': status,
                        'native_volume_id': str(volume.get('lun_id')),
                        'native_storage_pool_id': pool_ids.get(orig_pool_name,
                                                               ''),
                        'type': vol_type,
                        'total_capacity': int(total_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap),
                        'compressed': consts.VOL_COMPRESSED_MAP.get(
                            volume.get('is_compressed').lower()),
                        'wwn': volume.get('uid')
                    }
                    volume_list.append(v)
        return volume_list

    def handle_volume_from_raid_group(self, storage_id):
        volume_list = []
        volumes = self.navi_handler.get_all_lun()
        if volumes:
            for volume in volumes:
                if volume.get('raidgroup_id') and (
                        volume.get('raidgroup_id') != 'N/A' or volume.get(
                        'is_meta_lun') == 'YES'):
                    pool_id = None
                    if volume.get('raidgroup_id') != 'N/A':
                        pool_id = '%s%s' % (consts.RAID_GROUP_ID_PREFIX,
                                            volume.get('raidgroup_id'))
                    status = consts.STATUS_MAP.get(
                        volume.get('state'),
                        constants.StoragePoolStatus.OFFLINE)
                    vol_type = consts.VOL_TYPE_MAP.get(
                        volume.get('is_thin_lun').lower())
                    total_cap = float(
                        volume.get('lun_capacitymegabytes')) * units.Mi
                    used_cap = total_cap
                    free_cap = 0
                    v = {
                        'name': volume.get('name'),
                        'storage_id': storage_id,
                        'status': status,
                        'native_volume_id': str(
                            volume.get('logical_unit_number')),
                        'native_storage_pool_id': pool_id,
                        'type': vol_type,
                        'total_capacity': int(total_cap),
                        'used_capacity': int(used_cap),
                        'free_capacity': int(free_cap),
                        'wwn': volume.get('uid')
                    }
                    volume_list.append(v)
        return volume_list

    def list_volumes(self, storage_id):
        volumes = self.navi_handler.get_pool_lun()
        pools = self.navi_handler.get_pools()
        pool_ids = {}
        if pools:
            for pool in pools:
                if pool.get('pool_name') is not None:
                    pool_ids[pool.get('pool_name')] = pool.get('pool_id')
        volume_list = self.handle_volume_from_pool(volumes, pool_ids,
                                                   storage_id)
        raid_volumes = self.handle_volume_from_raid_group(storage_id)
        if raid_volumes:
            volume_list.extend(raid_volumes)
        return volume_list

    def handle_disk_capacity(self):
        disks = self.navi_handler.get_disks()
        raw_capacity = 0
        if disks:
            for disk in disks:
                if disk.get('disk_id') is not None:
                    capacity = float(disk.get("capacity", 0))
                    raw_capacity += capacity
        return raw_capacity * units.Mi

    def handle_pool_capacity(self):
        pools = self.list_storage_pools(None)
        total_capacity = 0
        free_capacity = 0
        used_capacity = 0
        obj_model = None
        if pools:
            for pool in pools:
                total_capacity += pool.get("total_capacity")
                free_capacity += pool.get("free_capacity")
                used_capacity += pool.get("used_capacity")
            obj_model = {
                'total_capacity': total_capacity,
                'free_capacity': free_capacity,
                'used_capacity': used_capacity
            }
        return obj_model

    def list_disks(self, storage_id):
        disks = self.navi_handler.get_disks()
        disk_list = []
        for disk in (disks or []):
            if disk.get('disk_id'):
                status = consts.DISK_STATUS_MAP.get(
                    disk.get('state', '').upper(),
                    constants.DiskStatus.ABNORMAL)
                capacity = int(float(disk.get("capacity", 0)) * units.Mi)
                logical_type = constants.DiskLogicalType.UNKNOWN
                hot_spare = disk.get('hot_spare', '')
                if hot_spare and hot_spare != 'N/A':
                    logical_type = constants.DiskLogicalType.HOTSPARE
                disk_name = disk.get('disk_name')
                disk_name = ' '.join(disk_name.strip().split())
                disk_model = {
                    'name': disk_name,
                    'storage_id': storage_id,
                    'native_disk_id': disk.get('disk_id'),
                    'serial_number': disk.get('serial_number'),
                    'manufacturer': disk.get('vendor_id'),
                    'model': disk.get('product_id'),
                    'firmware': disk.get('product_revision'),
                    'speed': None,
                    'capacity': capacity,
                    'status': status,
                    'physical_type': consts.DISK_PHYSICAL_TYPE_MAP.get(
                        disk.get('drive_type', '').upper(),
                        constants.DiskPhysicalType.UNKNOWN),
                    'logical_type': logical_type,
                    'health_score': None,
                    'native_disk_group_id': None,
                    'location': disk_name
                }
                disk_list.append(disk_model)
        return disk_list

    def analyse_speed(self, speed_value):
        speed = 0
        try:
            speeds = re.findall("\\d+", speed_value)
            if speeds:
                speed = int(speeds[0])
            if 'Gbps' in speed_value:
                speed = speed * units.G
            elif 'Mbps' in speed_value:
                speed = speed * units.M
            elif 'Kbps' in speed_value:
                speed = speed * units.k
        except Exception as err:
            err_msg = "analyse speed error: %s" % (six.text_type(err))
            LOG.error(err_msg)
        return speed

    def list_controllers(self, storage_id):
        controllers = self.navi_handler.get_controllers()
        cpus = self.navi_handler.get_cpus()
        controller_list = []
        for controller in (controllers or []):
            memory_size = int(controller.get('memory_size_for_the_sp',
                                             '0')) * units.Mi
            cpu_info = ''
            if cpus:
                cpu_info = cpus.get(
                    controller.get('serial_number_for_the_sp', ''), '')
            controller_model = {
                'name': controller.get('sp_name'),
                'storage_id': storage_id,
                'native_controller_id': controller.get('signature_for_the_sp'),
                'status': constants.ControllerStatus.NORMAL,
                'location': None,
                'soft_version': controller.get(
                    'revision_number_for_the_sp'),
                'cpu_info': cpu_info,
                'memory_size': str(memory_size)
            }
            controller_list.append(controller_model)
        return controller_list

    def list_ports(self, storage_id):
        port_list = []
        io_configs = self.navi_handler.get_io_configs()
        iscsi_port_map = self.get_iscsi_ports()
        ports = self.get_ports(storage_id, io_configs, iscsi_port_map)
        port_list.extend(ports)
        bus_ports = self.get_bus_ports(storage_id, io_configs)
        port_list.extend(bus_ports)
        return port_list

    def get_ports(self, storage_id, io_configs, iscsi_port_map):
        ports = self.navi_handler.get_ports()
        port_list = []
        for port in (ports or []):
            port_id = port.get('sp_port_id')
            sp_name = port.get('sp_name').replace('SP ', '')
            name = '%s-%s' % (sp_name, port_id)
            location = 'Slot %s%s,Port %s' % (
                sp_name, port.get('i/o_module_slot'),
                port.get('physical_port_id'))
            mac_address = port.get('mac_address')
            if mac_address == 'Not Applicable':
                mac_address = None
            module_key = '%s_%s' % (
                sp_name, port.get('i/o_module_slot'))
            type = ''
            if io_configs:
                type = io_configs.get(module_key, '')

            ipv4 = None
            ipv4_mask = None
            if iscsi_port_map:
                iscsi_port = iscsi_port_map.get(name)
                if iscsi_port:
                    ipv4 = iscsi_port.get('ip_address')
                    ipv4_mask = iscsi_port.get('subnet_mask')
            port_model = {
                'name': location,
                'storage_id': storage_id,
                'native_port_id': name,
                'location': location,
                'connection_status':
                    consts.PORT_CONNECTION_STATUS_MAP.get(
                        port.get('link_status', '').upper(),
                        constants.PortConnectionStatus.UNKNOWN),
                'health_status': consts.PORT_HEALTH_STATUS_MAP.get(
                    port.get('port_status', '').upper(),
                    constants.PortHealthStatus.UNKNOWN),
                'type': consts.PORT_TYPE_MAP.get(
                    type.upper(), constants.PortType.OTHER),
                'logical_type': None,
                'speed': self.analyse_speed(
                    port.get('speed_value', '')),
                'max_speed': self.analyse_speed(
                    port.get('max_speed', '')),
                'native_parent_id': None,
                'wwn': port.get('sp_uid'),
                'mac_address': mac_address,
                'ipv4': ipv4,
                'ipv4_mask': ipv4_mask,
                'ipv6': None,
                'ipv6_mask': None,
            }
            port_list.append(port_model)
        return port_list

    def get_bus_ports(self, storage_id, io_configs):
        bus_ports = self.navi_handler.get_bus_ports()
        port_list = []
        if bus_ports:
            bus_port_state_map = self.navi_handler.get_bus_port_state()
            for bus_port in bus_ports:
                sps = bus_port.get('sps')
                for sp in (sps or []):
                    sp_name = sp.replace('sp', '').upper()
                    location = '%s %s,Port %s' % (
                        bus_port.get('i/o_module_slot'), sp_name,
                        bus_port.get('physical_port_id'))
                    native_port_id = location.replace(' ', '')
                    native_port_id = native_port_id.replace(',', '')
                    module_key = '%s_%s' % (
                        sp_name, bus_port.get('i/o_module_slot'))
                    type = ''
                    if io_configs:
                        type = io_configs.get(module_key, '')
                    state = ''
                    if bus_port_state_map:
                        port_state_key = '%s_%s' % (
                            sp_name, bus_port.get('physical_port_id'))
                        state = bus_port_state_map.get(port_state_key,
                                                       '')
                    port_model = {
                        'name': location,
                        'storage_id': storage_id,
                        'native_port_id': native_port_id,
                        'location': location,
                        'connection_status':
                            constants.PortConnectionStatus.UNKNOWN,
                        'health_status':
                            consts.PORT_HEALTH_STATUS_MAP.get(
                                state.upper(),
                                constants.PortHealthStatus.UNKNOWN),
                        'type': consts.PORT_TYPE_MAP.get(
                            type.upper(), constants.PortType.OTHER),
                        'logical_type': None,
                        'speed': self.analyse_speed(
                            bus_port.get('current_speed', '')),
                        'max_speed': self.analyse_speed(
                            bus_port.get('max_speed', '')),
                        'native_parent_id': None,
                        'wwn': None,
                        'mac_address': None,
                        'ipv4': None,
                        'ipv4_mask': None,
                        'ipv6': None,
                        'ipv6_mask': None,
                    }
                    port_list.append(port_model)
        return port_list

    def get_iscsi_ports(self):
        iscsi_port_map = {}
        iscsi_ports = self.navi_handler.get_iscsi_ports()
        for iscsi_port in (iscsi_ports or []):
            name = '%s-%s' % (iscsi_port.get('sp'), iscsi_port.get('port_id'))
            iscsi_port_map[name] = iscsi_port
        return iscsi_port_map

    def list_masking_views(self, storage_id):
        views = self.navi_handler.list_masking_views()
        views_list = []
        host_vv_set = set()
        if views:
            for view in views:
                name = view.get('storage_group_name')
                host_names = view.get('host_names')
                lun_ids = view.get('lun_ids')
                if name:
                    if name == '~physical' or name == '~management':
                        continue
                    view_model_template = {
                        'native_masking_view_id': view.get(
                            'storage_group_uid'),
                        "name": view.get('storage_group_name'),
                        "storage_id": storage_id
                    }
                    if host_names and lun_ids:
                        host_names = list(set(host_names))
                        for host_name in host_names:
                            host_id = host_name.replace(' ', '')
                            for lun_id in lun_ids:
                                host_vv_key = '%s_%s' % (host_id, lun_id)
                                if host_vv_key in host_vv_set:
                                    continue
                                host_vv_set.add(host_vv_key)
                                view_model = copy.deepcopy(view_model_template)
                                view_model[
                                    'native_storage_host_id'] = host_id
                                view_model['native_volume_id'] = lun_id
                                view_model[
                                    'native_masking_view_id'] = '%s_%s_%s' % (
                                    view_model.get('native_masking_view_id'),
                                    host_id, lun_id)
                                views_list.append(view_model)
        return views_list

    def list_storage_host_initiators(self, storage_id):
        initiators = self.navi_handler.list_hbas()
        initiators_list = []
        initiator_set = set()
        port_types = {}
        if initiators:
            ports = self.list_ports(storage_id)
            for port in (ports or []):
                if port and port.get('type'):
                    port_types[port.get('name')] = port.get('type')
            for initiator in (initiators or []):
                if initiator and initiator.get('hba_uid'):
                    hba_uid = initiator.get('hba_uid')
                    type = ''
                    if port_types:
                        ports = initiator.get('port_ids')
                        if ports:
                            port_id = list(ports)[0]
                            type = port_types.get(port_id, '')
                    host_id = initiator.get('server_name', '').replace(' ', '')
                    if host_id == hba_uid:
                        host_id = None
                    if not host_id:
                        continue
                    if hba_uid in initiator_set:
                        continue
                    initiator_set.add(hba_uid)

                    initiator_model = {
                        "name": hba_uid,
                        "storage_id": storage_id,
                        "native_storage_host_initiator_id": hba_uid,
                        "wwn": hba_uid,
                        "type": consts.INITIATOR_TYPE_MAP.get(
                            type.upper(), constants.InitiatorType.UNKNOWN),
                        "status": constants.InitiatorStatus.ONLINE,
                        "native_storage_host_id": host_id
                    }
                    initiators_list.append(initiator_model)
        return initiators_list

    def list_storage_hosts(self, storage_id):
        hosts = self.navi_handler.list_hbas()
        host_list = []
        host_ids = set()
        host_ips = {}
        for host in (hosts or []):
            if host and host.get('server_name'):
                os_type = constants.HostOSTypes.UNKNOWN
                os_name = host.get('hba_vendor_description')
                ip_addr = host.get('server_ip_address')
                if ip_addr == 'UNKNOWN':
                    continue
                if os_name and 'VMware ESXi' in os_name:
                    os_type = constants.HostOSTypes.VMWARE_ESX
                id = host.get('server_name').replace(' ', '')
                if id in host_ids:
                    continue
                host_ids.add(id)

                if ip_addr in host_ips.keys():
                    first_port_ids = host_ips.get(ip_addr)
                    cur_port_ids = host.get('port_ids')
                    add_host = False
                    intersections = list(
                        set(first_port_ids).intersection(set(cur_port_ids)))
                    if not intersections:
                        add_host = True
                    if not add_host:
                        continue
                host_ips[ip_addr] = host.get('port_ids')

                host_model = {
                    "name": host.get('server_name'),
                    "storage_id": storage_id,
                    "native_storage_host_id": id,
                    "os_type": os_type,
                    "status": constants.HostStatus.NORMAL,
                    "ip_address": ip_addr
                }
                host_list.append(host_model)
        return host_list

    def collect_perf_metrics(self, storage_id, resource_metrics,
                             start_time, end_time):
        metrics = []
        archive_file_list = []
        try:
            LOG.info("Start collection, storage:%s, start time:%s, end time:%s"
                     % (storage_id, start_time, end_time))
            archive_file_list = self._get__archive_file(start_time, end_time)
            LOG.info("Get archive files: {}".format(archive_file_list))
            if not archive_file_list:
                LOG.warning("The required performance file was not found!")
                return metrics
            resources_map, resources_type_map = self._get_resources_map(
                resource_metrics)
            if not resources_map or not resources_type_map:
                LOG.warning("Resource object not found!")
                return metrics
            performance_lines_map = self._filter_performance_data(
                archive_file_list, resources_map, start_time, end_time)
            if not performance_lines_map:
                LOG.warning("The required performance data was not found!")
                return metrics
            metrics = self.create_metrics(storage_id, resource_metrics,
                                          resources_map, resources_type_map,
                                          performance_lines_map)
            LOG.info("Collection complete, storage:%s, start time:%s, "
                     "end time:%s, length of metrics:%s "
                     % (storage_id, start_time, end_time, len(metrics)))
        except exception.DelfinException as err:
            err_msg = "Failed to collect metrics from VnxBlockStor: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err
        except Exception as err:
            err_msg = "Failed to collect metrics from VnxBlockStor: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        finally:
            self._remove_archive_file(archive_file_list)
        return metrics

    def create_metrics(self, storage_id, resource_metrics, resources_map,
                       resources_type_map, performance_lines_map):
        metrics = []
        for resource_obj, resource_type in resources_type_map.items():
            if not resources_map.get(resource_obj) \
                    or not resource_type:
                continue
            if not performance_lines_map.get(resource_obj):
                continue
            labels = {
                'storage_id': storage_id,
                'resource_type': resource_type,
                'resource_id': resources_map.get(resource_obj),
                'type': 'RAW',
                'unit': ''
            }
            metric_model_list = self._get_metric_model(
                resource_metrics.get(resource_type), labels,
                performance_lines_map.get(resource_obj),
                consts.RESOURCES_TYPE_TO_METRIC_CAP.get(resource_type),
                resource_type)
            if metric_model_list:
                metrics.extend(metric_model_list)
        return metrics

    def _get__archive_file(self, start_time, end_time):
        archive_file_list = []
        archives = self.navi_handler.get_archives()
        tools = Tools()
        for archive_info in (archives or []):
            collection_timestamp = tools.time_str_to_timestamp(
                archive_info.get('collection_time'), consts.TIME_PATTERN)
            if collection_timestamp > start_time:
                archive_file_list.append(archive_info.get('archive_name'))
            if collection_timestamp > end_time:
                break
        return archive_file_list

    def _get_metric_model(self, metric_list, labels, metric_values, obj_cap,
                          resources_type):
        metric_model_list = []
        tools = Tools()
        for metric_name in (metric_list or []):
            values = {}
            obj_labels = copy.copy(labels)
            obj_labels['unit'] = obj_cap.get(metric_name).get('unit')
            for metric_value in metric_values:
                metric_value_infos = metric_value
                if not consts.METRIC_MAP.get(resources_type, {}).get(
                        metric_name):
                    continue
                value = metric_value_infos[
                    consts.METRIC_MAP.get(resources_type).get(metric_name)]
                if not value:
                    value = '0'
                collection_timestamp = tools.time_str_to_timestamp(
                    metric_value_infos[1], consts.TIME_PATTERN)
                collection_time_str = tools.timestamp_to_time_str(
                    collection_timestamp, consts.COLLECTION_TIME_PATTERN)
                collection_timestamp = tools.time_str_to_timestamp(
                    collection_time_str, consts.COLLECTION_TIME_PATTERN)
                if "iops" == obj_cap.get(metric_name).get('unit').lower():
                    value = int(float(value))
                else:
                    value = float('%.6f' % (float(value)))
                values[collection_timestamp] = value
            if values:
                metric_model = constants.metric_struct(name=metric_name,
                                                       labels=obj_labels,
                                                       values=values)
                metric_model_list.append(metric_model)
        return metric_model_list

    def _get_resources_map(self, resource_metrics):
        resources_map = {}
        resources_type_map = {}
        for resource_type_key in resource_metrics.keys():
            sub_resources_map = {}
            sub_resources_type_map = {}
            if resource_type_key == constants.ResourceType.CONTROLLER:
                sub_resources_map, sub_resources_type_map = \
                    self._get_controllers_map()
            elif resource_type_key == constants.ResourceType.PORT:
                sub_resources_map, sub_resources_type_map = \
                    self._get_ports_map()
            elif resource_type_key == constants.ResourceType.DISK:
                sub_resources_map, sub_resources_type_map = \
                    self._get_disks_map()
            elif resource_type_key == constants.ResourceType.VOLUME:
                sub_resources_map, sub_resources_type_map = \
                    self._get_volumes_map()
            if sub_resources_map and sub_resources_type_map:
                resources_map.update(sub_resources_map)
                resources_type_map.update(sub_resources_type_map)
        return resources_map, resources_type_map

    def _get_controllers_map(self):
        resources_map = {}
        resources_type_map = {}
        controllers = self.navi_handler.get_controllers()
        for controller in (controllers or []):
            resources_map[controller.get('sp_name')] = controller.get(
                'signature_for_the_sp')
            resources_type_map[controller.get('sp_name')] = \
                constants.ResourceType.CONTROLLER
        return resources_map, resources_type_map

    def _get_ports_map(self):
        resources_map = {}
        resources_type_map = {}
        ports = self.navi_handler.get_ports()
        for port in (ports or []):
            port_id = port.get('sp_port_id')
            sp_name = port.get('sp_name').replace('SP ', '')
            name = '%s-%s' % (sp_name, port_id)
            port_id = 'Port %s [ %s ]' % (port_id, port.get('sp_uid'))
            resources_map[port_id] = name
            resources_type_map[port_id] = constants.ResourceType.PORT
        return resources_map, resources_type_map

    def _get_disks_map(self):
        resources_map = {}
        resources_type_map = {}
        disks = self.navi_handler.get_disks()
        for disk in (disks or []):
            disk_name = disk.get('disk_name')
            disk_name = ' '.join(disk_name.strip().split())
            resources_map[disk_name] = disk.get('disk_id')
            resources_type_map[disk_name] = constants.ResourceType.DISK
        return resources_map, resources_type_map

    def _get_volumes_map(self):
        resources_map = {}
        resources_type_map = {}
        volumes = self.navi_handler.get_all_lun()
        for volume in (volumes or []):
            if not volume.get('name'):
                continue
            volume_name = '%s [%s]' % (
                volume.get('name'), volume.get('logical_unit_number'))
            resources_map[volume_name] = str(volume.get('logical_unit_number'))
            resources_type_map[volume_name] = constants.ResourceType.VOLUME
        return resources_map, resources_type_map

    def _filter_performance_data(self, archive_file_list, resources_map,
                                 start_time, end_time):
        performance_lines_map = {}
        try:
            tools = Tools()
            for archive_file in archive_file_list:
                self.navi_handler.download_archives(archive_file)
                archive_name_infos = archive_file.split('.')
                file_path = '%s%s.csv' % (
                    self.navi_handler.get_local_file_path(),
                    archive_name_infos[0])
                with open(file_path) as file:
                    f_csv = csv.reader(file)
                    next(f_csv)
                    for row in f_csv:
                        self._package_performance_data(row, resources_map,
                                                       start_time, end_time,
                                                       tools,
                                                       performance_lines_map)
        except Exception as err:
            err_msg = "Failed to filter performance data: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.StorageBackendException(err_msg)
        return performance_lines_map

    def _package_performance_data(self, row, resources_map, start_time,
                                  end_time, tools, performance_lines_map):
        resource_obj_name = row[0]
        resource_obj_name = self._package_resource_obj_name(resource_obj_name)
        if resource_obj_name in resources_map:
            obj_collection_timestamp = tools.time_str_to_timestamp(
                row[1], consts.TIME_PATTERN)
            if (start_time + consts.TIME_INTERVAL_FLUCTUATION) \
                    <= obj_collection_timestamp \
                    and obj_collection_timestamp \
                    <= (end_time + consts.TIME_INTERVAL_FLUCTUATION):
                performance_lines_map.setdefault(resource_obj_name, []).append(
                    row)

    def _package_resource_obj_name(self, source_name):
        target_name = source_name
        if 'Port ' in target_name:
            return re.sub(r'(\[.*;)', '[', target_name)
        elif '; ' in target_name:
            return re.sub(r'(; .*])', ']', target_name)
        return target_name

    def _remove_archive_file(self, archive_file_list):
        try:
            for archive_file in archive_file_list:
                nar_file_path = '%s%s' % (
                    self.navi_handler.get_local_file_path(), archive_file)
                archive_name_infos = archive_file.split('.')
                csv_file_path = '%s%s.csv' % (
                    self.navi_handler.get_local_file_path(),
                    archive_name_infos[0])
                for file_path in [nar_file_path, csv_file_path]:
                    LOG.info("Delete file :{}".format(file_path))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    else:
                        err_msg = 'no such file:%s' % file_path
                        LOG.error(err_msg)
                        raise exception.StorageBackendException(err_msg)
        except Exception as err:
            err_msg = "Failed to remove archive file: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.StorageBackendException(err_msg)

    def get_latest_perf_timestamp(self, storage_id):
        latest_time = 0
        num = 0
        tools = Tools()
        while latest_time <= 0:
            num += 1
            latest_time, file_latest_time = self.check_latest_timestamp(
                storage_id)
            if num > consts.EXEC_MAX_NUM:
                latest_time = file_latest_time
                LOG.warning("Storage:{}, Exit after {} executions.".format(
                    storage_id, consts.EXEC_MAX_NUM))
                break
            if latest_time <= 0:
                wait_time = tools.timestamp_to_time_str(
                    time.time() * units.k,
                    consts.ARCHIVE_FILE_NAME_TIME_PATTERN)
                LOG.warning("Storage:{} No new file found, "
                            "wait for next execution:{}".format(storage_id,
                                                                wait_time))
                time.sleep(consts.SLEEP_TIME_SECONDS)
        return latest_time

    def get_data_latest_timestamp(self, storage_id):
        archive_file_list = []
        try:
            tools = Tools()
            archive_name = self.navi_handler.create_archives(storage_id)
            LOG.info("Create archive_name: {}".format(archive_name))
            archive_file_list.append(archive_name)
            archive_name_infos = archive_name.split('.')
            file_path = '%s%s.csv' % (
                self.navi_handler.get_local_file_path(), archive_name_infos[0])
            resource_obj_name = ''
            collection_time = ''
            with open(file_path) as file:
                f_csv = csv.reader(file)
                next(f_csv)
                for row in f_csv:
                    if not resource_obj_name or resource_obj_name == row[0]:
                        resource_obj_name = row[0]
                        collection_time = row[1]
                    else:
                        break
                latest_time = tools.time_str_to_timestamp(collection_time,
                                                          consts.TIME_PATTERN)
        except Exception as err:
            err_msg = "Failed to get latest perf timestamp " \
                      "from VnxBlockStor: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        finally:
            self._remove_archive_file(archive_file_list)
        return latest_time

    def check_latest_timestamp(self, storage_id):
        latest_time = 0
        file_latest_time = self.get_data_latest_timestamp(storage_id)
        sys_time = self.navi_handler.get_sp_time()
        LOG.info("Get sys_time=={},file_latest_time=={}".format(
            sys_time, file_latest_time))
        if sys_time > 0 and file_latest_time > 0:
            LOG.info("(sys_time - file_latest_time)={}".format(
                (sys_time - file_latest_time)))
            if (sys_time - file_latest_time) < \
                    consts.CREATE_FILE_TIME_INTERVAL:
                latest_time = file_latest_time
                time.sleep(consts.CHECK_WAITE_TIME_SECONDS)
        return latest_time, file_latest_time
