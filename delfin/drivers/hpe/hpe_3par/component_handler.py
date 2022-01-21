# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import copy
import datetime
import re
import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.hpe.hpe_3par import consts

LOG = log.getLogger(__name__)


class ComponentHandler():
    COMPONENT_HEALTH = 'The following components are healthy'
    SYSTEM_HEALTH = 'System is healthy'
    HPE3PAR_VERSION = 'Superclass'

    HPE3PAR_VENDOR = 'HPE'

    STATUS_MAP = {1: constants.StoragePoolStatus.NORMAL,
                  2: constants.StoragePoolStatus.ABNORMAL,
                  3: constants.StoragePoolStatus.ABNORMAL,
                  99: constants.StoragePoolStatus.OFFLINE}

    VOL_TYPE_MAP = {1: constants.VolumeType.THICK,
                    2: constants.VolumeType.THIN,
                    3: constants.VolumeType.THIN,
                    4: constants.VolumeType.THICK,
                    5: constants.VolumeType.THICK,
                    6: constants.VolumeType.THIN,
                    7: constants.VolumeType.THICK}

    def __init__(self, rest_handler=None, ssh_handler=None):
        self.rest_handler = rest_handler
        self.ssh_handler = ssh_handler

    def set_storage_id(self, storage_id):
        self.storage_id = storage_id

    def get_storage(self, context):
        storage = self.rest_handler.get_storage()
        status = constants.StorageStatus.NORMAL

        if storage:
            try:
                # Check the hardware and software health
                # status of the storage system
                re_str = self.ssh_handler.get_health_state()
                if 'degraded' in re_str or 'failed' in re_str:
                    status = constants.StorageStatus.ABNORMAL
            except Exception:
                status = constants.StorageStatus.ABNORMAL
                LOG.error('SSH check health Failed!')

            free_cap = int(storage.get('freeCapacityMiB')) * units.Mi
            used_cap = int(storage.get('allocatedCapacityMiB')) * units.Mi
            total_cap = free_cap + used_cap
            raw_cap = int(storage.get('totalCapacityMiB')) * units.Mi
            result = {
                'name': storage.get('name'),
                'vendor': ComponentHandler.HPE3PAR_VENDOR,
                'model': storage.get('model'),
                'status': status,
                'serial_number': storage.get('serialNumber'),
                'firmware_version': storage.get('systemVersion'),
                'location': storage.get('location'),
                'total_capacity': total_cap,
                'raw_capacity': raw_cap,
                'used_capacity': used_cap,
                'free_capacity': free_cap
            }
        else:
            # If no data is returned, it indicates that there
            # may be a problem with the network or the device.
            # Default return OFFLINE
            result = {
                'status': constants.StorageStatus.OFFLINE
            }
        return result

    def list_storage_pools(self, context):
        try:
            # Get list of Hpe3parStor pool details
            pools = self.rest_handler.get_all_pools()
            pool_list = []

            if pools is not None:
                members = pools.get('members')
                for pool in (members or []):
                    # Get pool status  1=normal 2,3=abnormal 99=offline
                    status = self.STATUS_MAP.get(pool.get('state'))

                    # Get pool storage_type   default block
                    pool_type = constants.StorageType.BLOCK
                    usr_used = int(pool['UsrUsage']['usedMiB']) * units.Mi
                    sa_used = int(pool['SAUsage']['usedMiB']) * units.Mi
                    sd_used = int(pool['SDUsage']['usedMiB']) * units.Mi
                    usr_total = int(pool['UsrUsage']['totalMiB']) * units.Mi
                    sa_total = int(pool['SAUsage']['totalMiB']) * units.Mi
                    sd_total = int(pool['SDUsage']['totalMiB']) * units.Mi
                    total_cap = usr_total + sa_total + sd_total
                    used_cap = usr_used + sa_used + sd_used
                    free_cap = total_cap - used_cap
                    usr_subcap = int(
                        pool['UsrUsage']['rawTotalMiB']) * units.Mi
                    sa_subcap = int(pool['SAUsage']['rawTotalMiB']) * units.Mi
                    sd_subcap = int(pool['SDUsage']['rawTotalMiB']) * units.Mi
                    subscribed_cap = usr_subcap + sa_subcap + sd_subcap

                    p = {
                        'name': pool.get('name'),
                        'storage_id': self.storage_id,
                        'native_storage_pool_id': str(pool.get('id')),
                        'description': 'Hpe 3par CPG:%s' % pool.get('name'),
                        'status': status,
                        'storage_type': pool_type,
                        'total_capacity': total_cap,
                        'subscribed_capacity': subscribed_cap,
                        'used_capacity': used_cap,
                        'free_capacity': free_cap
                    }
                    pool_list.append(p)
            return pool_list

        except exception.DelfinException as e:
            err_msg = "Failed to get pool metrics from Hpe3parStor: %s" % \
                      (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Failed to get pool metrics from Hpe3parStor: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handler_volume(self, volumes, pool_ids):
        volume_list = []
        if volumes is None:
            return
        else:
            members = volumes.get('members')
            for volume in (members or []):
                status = self.STATUS_MAP.get(volume.get('state'))
                orig_pool_name = volume.get('userCPG', '')

                compressed = True
                deduplicated = True
                if volume.get('compressionState') and volume.get(
                        'compressionState') != 1:
                    compressed = False
                if volume.get('deduplicationState') and volume.get(
                        'deduplicationState') != 1:
                    deduplicated = False
                vol_type = self.VOL_TYPE_MAP.get(
                    volume.get('provisioningType'))

                # Virtual size of volume in MiB (10242bytes).
                usr_used = int(
                    volume['userSpace']['usedMiB']) * units.Mi
                total_cap = int(volume['sizeMiB']) * units.Mi
                used_cap = usr_used
                free_cap = total_cap - used_cap

                v = {
                    'name': volume.get('name'),
                    'storage_id': self.storage_id,
                    'description': volume.get('comment'),
                    'status': status,
                    'native_volume_id': str(volume.get('id')),
                    'native_storage_pool_id': pool_ids.get(orig_pool_name,
                                                           ''),
                    'wwn': volume.get('wwn'),
                    'type': vol_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                    'compressed': compressed,
                    'deduplicated': deduplicated
                }
                volume_list.append(v)
        return volume_list

    def list_volumes(self, context):
        try:
            volumes = self.rest_handler.get_all_volumes()

            pools = self.rest_handler.get_all_pools()
            pool_ids = {}
            if pools is not None:
                members = pools.get('members')
                for pool in (members or []):
                    pool_ids[pool.get('name')] = pool.get('id')

            return self.handler_volume(volumes, pool_ids)

        except exception.DelfinException as e:
            err_msg = "Failed to get list volumes from Hpe3parStor: %s" % \
                      (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Failed to get list volumes from Hpe3parStor: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_controllers(self, storage_id):
        controllers = self.ssh_handler.get_controllers()
        controller_list = []
        if controllers:
            node_cpu_map = self.ssh_handler.get_controllers_cpu()
            node_version_map = self.ssh_handler.get_controllers_version()
            for controller in controllers:
                node_id = controller.get('node')
                memory_size = int(controller.get('controlmem(mb)',
                                                 '0')) * units.Mi + int(
                    controller.get('datamem(mb)', '0')) * units.Mi
                cpu_info = ''
                if node_cpu_map and node_cpu_map.get(node_id):
                    cpu_info_map = node_cpu_map.get(node_id)
                    cpu_info_keys = list(cpu_info_map.keys())
                    for cpu_key in cpu_info_keys:
                        if cpu_info:
                            cpu_info = '%s%s' % (cpu_info, ',')
                        cpu_info = '%s%s * %s MHz' % (
                            cpu_info, cpu_info_map.get(cpu_key), cpu_key)
                soft_version = None
                if node_version_map:
                    soft_version = node_version_map.get(node_id, '')
                controller_model = {
                    'name': controller.get('name'),
                    'storage_id': storage_id,
                    'native_controller_id': node_id,
                    'status': consts.CONTROLLER_STATUS_MAP.get(
                        controller.get('state', '').upper(),
                        constants.ControllerStatus.OFFLINE),
                    'location': None,
                    'soft_version': soft_version,
                    'cpu_info': cpu_info,
                    'memory_size': str(memory_size)
                }
                controller_list.append(controller_model)
        return controller_list

    def list_disks(self, storage_id):
        disks = self.ssh_handler.get_disks()
        disk_list = []
        if disks:
            disks_inventory_map = self.ssh_handler.get_disks_inventory()
            for disk in disks:
                disk_id = disk.get('id')
                status = consts.DISK_STATUS_MAP.get(
                    disk.get('state', '').upper(),
                    constants.DiskStatus.ABNORMAL)
                total = 0
                if disk.get('total'):
                    total = float(disk.get("total"))
                elif disk.get('size_mb'):
                    total = float(disk.get("size_mb"))
                capacity = int(total * units.Mi)
                serial_number = None
                manufacturer = None
                model = None
                firmware = None
                if disks_inventory_map:
                    inventory_map = disks_inventory_map.get(disk_id)
                    if inventory_map:
                        serial_number = inventory_map.get('disk_serial')
                        manufacturer = inventory_map.get('disk_mfr')
                        model = inventory_map.get('disk_model')
                        firmware = inventory_map.get('disk_fw_rev')
                speed = None
                if disk.get('rpm'):
                    speed = int(disk.get('rpm')) * units.k
                disk_model = {
                    'name': disk.get('cagepos'),
                    'storage_id': storage_id,
                    'native_disk_id': disk_id,
                    'serial_number': serial_number,
                    'manufacturer': manufacturer,
                    'model': model,
                    'firmware': firmware,
                    'speed': speed,
                    'capacity': capacity,
                    'status': status,
                    'physical_type': consts.DISK_PHYSICAL_TYPE_MAP.get(
                        disk.get('type').upper(),
                        constants.DiskPhysicalType.UNKNOWN),
                    'logical_type': None,
                    'health_score': None,
                    'native_disk_group_id': None,
                    'location': disk.get('cagepos')
                }
                disk_list.append(disk_model)
        return disk_list

    def list_ports(self, storage_id):
        ports = self.ssh_handler.get_ports()
        port_list = []
        if ports:
            ports_inventory_map = self.ssh_handler.get_ports_inventory()
            ports_config_map = self.ssh_handler.get_ports_config()
            ports_iscsi_map = self.ssh_handler.get_ports_iscsi()
            ports_rcip_map = self.ssh_handler.get_ports_rcip()
            ports_connected_map = self.ssh_handler.get_ports_connected()
            ports_fcoe_map = self.ssh_handler.get_ports_fcoe()
            port_fs_map = self.ssh_handler.get_ports_fs()
            for port in ports:
                port_id = port.get('n:s:p')
                port_type = ''
                if ports_inventory_map:
                    port_type = ports_inventory_map.get(port_id, '')
                max_speed = ''
                if ports_config_map:
                    max_speed = ports_config_map.get(port_id, '')
                ip_addr = None
                ip_mask = None
                ipv4 = None
                ipv4_mask = None
                ipv6 = None
                ipv6_mask = None
                rate = ''
                if ports_connected_map:
                    rate = ports_connected_map.get(port_id, '')
                if not ip_addr and ports_iscsi_map:
                    iscsi_map = ports_iscsi_map.get(port_id)
                    if iscsi_map:
                        ip_addr = iscsi_map.get('ipaddr')
                        ip_mask = iscsi_map.get('netmask/prefixlen')
                        rate = iscsi_map.get('rate')
                if not ip_addr and ports_rcip_map:
                    rcip_map = ports_rcip_map.get(port_id)
                    if rcip_map:
                        ip_addr = rcip_map.get('ipaddr')
                        ip_mask = rcip_map.get('netmask')
                        rate = rcip_map.get('rate')
                if not ip_addr and port_fs_map:
                    fs_map = port_fs_map.get(port_id)
                    if fs_map:
                        ip_addr = fs_map.get('ipaddr')
                        ip_mask = fs_map.get('netmask')
                        rate = fs_map.get('rate')
                if not rate and ports_fcoe_map:
                    fcoe_map = ports_fcoe_map.get(port_id)
                    if fcoe_map:
                        rate = fcoe_map.get('rate')
                if ip_addr and ip_addr != '-':
                    pattern = re.compile(consts.IPV4_PATTERN)
                    search_obj = pattern.search(ip_addr)
                    if search_obj:
                        ipv4 = ip_addr
                        ipv4_mask = ip_mask
                    else:
                        ipv6 = ip_addr
                        ipv6_mask = ip_mask
                wwn = None
                mac = None
                if port_type.upper() == 'ETH':
                    mac = port.get('port_wwn/hw_addr')
                else:
                    wwn = port.get('port_wwn/hw_addr')
                port_model = {
                    'name': port_id,
                    'storage_id': storage_id,
                    'native_port_id': port_id,
                    'location': port_id,
                    'connection_status':
                        consts.PORT_CONNECTION_STATUS_MAP.get(
                            port.get('state', '').upper(),
                            constants.PortConnectionStatus.UNKNOWN),
                    'health_status': constants.PortHealthStatus.NORMAL,
                    'type': consts.PORT_TYPE_MAP.get(port_type.upper(),
                                                     constants.PortType.OTHER),
                    'logical_type': None,
                    'speed': self.parse_speed(rate),
                    'max_speed': self.parse_speed(max_speed),
                    'native_parent_id': None,
                    'wwn': wwn,
                    'mac_address': mac,
                    'ipv4': ipv4,
                    'ipv4_mask': ipv4_mask,
                    'ipv6': ipv6,
                    'ipv6_mask': ipv6_mask,
                }
                port_list.append(port_model)
        return port_list

    def parse_speed(self, speed_value):
        speed = 0
        try:
            if speed_value == '' or speed_value == 'n/a':
                return None
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

    def collect_perf_metrics(self, storage_id, resource_metrics,
                             start_time, end_time):
        metrics = []
        try:
            # storage-pool metrics
            if resource_metrics.get(constants.ResourceType.STORAGE_POOL):
                pool_metrics = self.get_pool_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.STORAGE_POOL),
                    start_time, end_time)
                metrics.extend(pool_metrics)

            # volume metrics
            if resource_metrics.get(constants.ResourceType.VOLUME):
                volume_metrics = self.get_volume_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.VOLUME),
                    start_time, end_time)
                metrics.extend(volume_metrics)

            # port metrics
            if resource_metrics.get(constants.ResourceType.PORT):
                port_metrics = self.get_port_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.PORT),
                    start_time, end_time)
                metrics.extend(port_metrics)

            # disk metrics
            if resource_metrics.get(constants.ResourceType.DISK):
                disk_metrics = self.get_disk_metrics(
                    storage_id,
                    resource_metrics.get(constants.ResourceType.DISK),
                    start_time, end_time)
                metrics.extend(disk_metrics)
        except exception.DelfinException as err:
            err_msg = "Failed to collect metrics from Hpe3parStor: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err
        except Exception as err:
            err_msg = "Failed to collect metrics from Hpe3parStor: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

        return metrics

    def get_pool_metrics(self, storage_id, metric_list,
                         start_time, end_time):
        metrics = []
        obj_metrics = {}
        pool_maps = {}
        pools = self.rest_handler.get_all_pools()
        if pools:
            pool_members = pools.get('members')
            for pool in pool_members:
                pool_maps[pool.get('name')] = str(pool.get('id'))
            obj_metrics = self.rest_format_metrics_data(
                start_time, end_time, self.rest_handler.get_pool_metrics,
                constants.ResourceType.STORAGE_POOL)

        if obj_metrics:
            for obj_name in obj_metrics.keys():
                if pool_maps.get(obj_name):
                    labels = {
                        'storage_id': storage_id,
                        'resource_type': constants.ResourceType.STORAGE_POOL,
                        'resource_id': pool_maps.get(obj_name),
                        'type': 'RAW',
                        'unit': ''
                    }
                    metric_model_list = self._get_metric_model(metric_list,
                                                               labels,
                                                               obj_metrics.get(
                                                                   obj_name),
                                                               consts.POOL_CAP)
                    if metric_model_list:
                        metrics.extend(metric_model_list)
        return metrics

    def _get_metric_model(self, metric_list, labels, metric_values, obj_cap):
        metric_model_list = []
        for metric_name in (metric_list or []):
            values = {}
            obj_labels = copy.deepcopy(labels)
            obj_labels['unit'] = obj_cap.get(metric_name).get('unit')
            for metric_value in metric_values:
                if metric_value.get(metric_name) is not None:
                    collect_timestamp = self.convert_to_system_time(
                        metric_value.get('collect_timestamp'))
                    values[collect_timestamp] = metric_value.get(
                        metric_name)
            if values:
                metric_model = constants.metric_struct(name=metric_name,
                                                       labels=obj_labels,
                                                       values=values)
                metric_model_list.append(metric_model)
        return metric_model_list

    def get_port_metrics(self, storage_id, metric_list,
                         start_time, end_time):
        metrics = []
        obj_metrics = self.ssh_format_metrics_data(
            start_time, end_time, self.ssh_handler.get_port_metrics,
            constants.ResourceType.PORT)
        if obj_metrics:
            for obj_id in obj_metrics.keys():
                labels = {
                    'storage_id': storage_id,
                    'resource_type': constants.ResourceType.PORT,
                    'resource_id': obj_id,
                    'type': 'RAW',
                    'unit': ''
                }
                metric_model_list = self._get_metric_model(metric_list,
                                                           labels,
                                                           obj_metrics.get(
                                                               obj_id),
                                                           consts.PORT_CAP)
                if metric_model_list:
                    metrics.extend(metric_model_list)
        return metrics

    def get_disk_metrics(self, storage_id, metric_list,
                         start_time, end_time):
        metrics = []
        obj_metrics = self.ssh_format_metrics_data(
            start_time, end_time, self.ssh_handler.get_disk_metrics,
            constants.ResourceType.DISK)
        if obj_metrics:
            for obj_id in obj_metrics.keys():
                labels = {
                    'storage_id': storage_id,
                    'resource_type': constants.ResourceType.DISK,
                    'resource_id': obj_id,
                    'type': 'RAW',
                    'unit': ''
                }
                metric_model_list = self._get_metric_model(metric_list,
                                                           labels,
                                                           obj_metrics.get(
                                                               obj_id),
                                                           consts.DISK_CAP)
                if metric_model_list:
                    metrics.extend(metric_model_list)
        return metrics

    def get_volume_metrics(self, storage_id, metric_list,
                           start_time, end_time):
        metrics = []
        obj_metrics = {}
        try:
            obj_metrics = self.ssh_format_metrics_data(
                start_time, end_time, self.ssh_handler.get_volume_metrics,
                constants.ResourceType.VOLUME)
        except Exception as err:
            err_msg = "Failed to collect volume metrics: %s" \
                      % (six.text_type(err))
            LOG.warning(err_msg)
        if obj_metrics:
            for obj_id in obj_metrics.keys():
                labels = {
                    'storage_id': storage_id,
                    'resource_type': constants.ResourceType.VOLUME,
                    'resource_id': obj_id,
                    'type': 'RAW',
                    'unit': ''
                }
                metric_model_list = self._get_metric_model(metric_list,
                                                           labels,
                                                           obj_metrics.get(
                                                               obj_id),
                                                           consts.VOLUME_CAP)
                if metric_model_list:
                    metrics.extend(metric_model_list)
        return metrics

    def ssh_format_metrics_data(self, start_time, end_time, get_obj_metrics,
                                obj_type):
        collect_resuore_map = {}
        obj_metrics = get_obj_metrics(start_time, end_time)
        if obj_metrics:
            metric_value = obj_metrics[0]
            last_time = metric_value.get('collect_time', 0)
            first_time = last_time
            time_interval = consts.COLLECT_INTERVAL_HIRES
            while (last_time - time_interval) > start_time:
                next_obj_metrics = get_obj_metrics(
                    start_time, (last_time - time_interval))
                if next_obj_metrics:
                    metric_value = next_obj_metrics[0]
                    last_time = metric_value.get('collect_time', 0)
                    if last_time > start_time:
                        time_interval = first_time - last_time
                        first_time = last_time
                        obj_metrics.extend(next_obj_metrics)
                    else:
                        break
                else:
                    break

        for obj_metric in (obj_metrics or []):
            obj_id = ''
            if obj_type == constants.ResourceType.DISK:
                obj_id = obj_metric.get('pdid')
            elif obj_type == constants.ResourceType.PORT:
                obj_id = '%s:%s:%s' % (
                    obj_metric.get('port_n'), obj_metric.get('port_s'),
                    obj_metric.get('port_p'))
            elif obj_type == constants.ResourceType.VOLUME:
                obj_id = obj_metric.get('vvid')
            if obj_id:
                metric_list = []
                if collect_resuore_map.get(obj_id):
                    metric_list = collect_resuore_map.get(obj_id)
                else:
                    collect_resuore_map[obj_id] = metric_list
                metric_map = {}
                metric_map['iops'] = float(obj_metric.get('iotot'))
                metric_map['readIops'] = float(obj_metric.get('iord'))
                metric_map['writeIops'] = float(obj_metric.get('iowr'))
                metric_map['throughput'] = round(
                    float(obj_metric.get('kbytestot')) / units.k, 5)
                metric_map['readThroughput'] = round(
                    float(obj_metric.get('kbytesrd')) / units.k, 5)
                metric_map['writeThroughput'] = round(
                    float(obj_metric.get('kbyteswr')) / units.k, 5)
                metric_map['responseTime'] = float(
                    obj_metric.get('svcttot'))
                metric_map['ioSize'] = float(obj_metric.get('iosztot'))
                metric_map['readIoSize'] = float(obj_metric.get('ioszrd'))
                metric_map['writeIoSize'] = float(obj_metric.get('ioszwr'))
                metric_map['collect_timestamp'] = obj_metric.get(
                    'collect_time')
                metric_list.append(metric_map)
        return collect_resuore_map

    def rest_format_metrics_data(self, start_time, end_time, get_obj_metrics,
                                 obj_type):
        collect_resuore_map = {}
        obj_metrics_list = []
        obj_metrics = get_obj_metrics(start_time, end_time)
        if obj_metrics:
            last_time = obj_metrics.get('sampleTimeSec', 0) * units.k
            first_time = last_time
            time_interval = consts.COLLECT_INTERVAL_HIRES
            metric_members = obj_metrics.get('members')
            if metric_members:
                for member in metric_members:
                    member['collect_timestamp'] = last_time
                obj_metrics_list.extend(metric_members)
                while (last_time - time_interval) > start_time:
                    next_obj_metrics = get_obj_metrics(
                        start_time,
                        (last_time - time_interval))
                    metric_members = next_obj_metrics.get('members')
                    if metric_members:
                        last_time = next_obj_metrics.get(
                            'sampleTimeSec', 0) * units.k
                        if last_time > start_time:
                            time_interval = first_time - last_time
                            first_time = last_time
                            for member in metric_members:
                                member['collect_timestamp'] = last_time
                            obj_metrics_list.extend(metric_members)
                        else:
                            break
                    else:
                        break
        for obj_metric in (obj_metrics_list or []):
            obj_id = ''
            if obj_type == constants.ResourceType.STORAGE_POOL:
                obj_id = obj_metric.get('name')
            if obj_id:
                metric_list = []
                if collect_resuore_map.get(obj_id):
                    metric_list = collect_resuore_map.get(obj_id)
                else:
                    collect_resuore_map[obj_id] = metric_list
                metric_map = {}
                metric_map['iops'] = obj_metric.get('IO').get('total')
                metric_map['readIops'] = obj_metric.get('IO').get('read')
                metric_map['writeIops'] = obj_metric.get('IO').get('write')
                metric_map['throughput'] = round(
                    obj_metric.get('KBytes').get('total') / units.k, 5)
                metric_map['readThroughput'] = round(
                    obj_metric.get('KBytes').get('read') / units.k, 5)
                metric_map['writeThroughput'] = round(
                    obj_metric.get('KBytes').get('write') / units.k, 5)
                metric_map['responseTime'] = obj_metric.get(
                    'serviceTimeMS').get('total')
                metric_map['ioSize'] = obj_metric.get('IOSizeKB').get('total')
                metric_map['readIoSize'] = obj_metric.get('IOSizeKB').get(
                    'read')
                metric_map['writeIoSize'] = obj_metric.get('IOSizeKB').get(
                    'write')
                metric_map['collect_timestamp'] = obj_metric.get(
                    'collect_timestamp')
                metric_list.append(metric_map)
        return collect_resuore_map

    def get_latest_perf_timestamp(self):
        latest_time = 0
        disks_metrics_datas = self.ssh_handler.get_disk_metrics(None, None)
        for metrics_data in (disks_metrics_datas or []):
            if metrics_data and metrics_data.get('collect_time'):
                latest_time = metrics_data.get('collect_time')
                break
        return latest_time

    def convert_to_system_time(self, occur_time):
        dateArray = datetime.datetime.utcfromtimestamp(occur_time / units.k)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%SZ")
        timeArray = time.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%SZ")
        timeStamp = int(time.mktime(timeArray))
        hour_offset = (time.mktime(time.localtime()) - time.mktime(
            time.gmtime())) / consts.SECONDS_PER_HOUR
        occur_time = timeStamp * units.k + (int(hour_offset) *
                                            consts.SECONDS_PER_HOUR) * units.k
        return occur_time
