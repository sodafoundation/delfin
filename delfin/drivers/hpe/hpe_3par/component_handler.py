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
import re

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

    def list_storage_host_initiators(self, storage_id):
        initiators = self.ssh_handler.list_storage_host_initiators()
        initiators_list = []
        wwn_set = set()
        for initiator in (initiators or []):
            if initiator:
                wwn = initiator.get('wwn/iscsi_name', '').replace('-', '')
                if wwn:
                    if wwn in wwn_set:
                        continue
                    wwn_set.add(wwn)
                    ip_addr = initiator.get('ip_addr')
                    type = constants.InitiatorType.FC
                    if ip_addr and ip_addr != 'n/a':
                        type = constants.InitiatorType.ISCSI
                    initiator_model = {
                        "name": wwn,
                        "storage_id": storage_id,
                        "native_storage_host_initiator_id": wwn,
                        "wwn": wwn,
                        "type": type,
                        "status": constants.InitiatorStatus.ONLINE,
                        "native_storage_host_id": initiator.get('id',
                                                                '').replace(
                            '-', ''),
                    }
                    initiators_list.append(initiator_model)
        return initiators_list

    def list_storage_hosts(self, storage_id):
        host_datas = self.rest_handler.list_storage_host()
        host_list = []
        if host_datas:
            hosts = host_datas.get('members')
            for host in (hosts or []):
                if host and host.get('name'):
                    descriptors = host.get('descriptors')
                    comment = None
                    os = ''
                    ip_addr = None
                    if descriptors:
                        comment = descriptors.get('comment')
                        os = descriptors.get('os', '')
                        ip_addr = descriptors.get('IPAddr')
                    host_model = {
                        "name": host.get('name'),
                        "description": comment,
                        "storage_id": storage_id,
                        "native_storage_host_id": host.get('id'),
                        "os_type": consts.HOST_OS_MAP.get(
                            os, constants.HostOSTypes.UNKNOWN),
                        "status": constants.HostStatus.NORMAL,
                        "ip_address": ip_addr
                    }
                    host_list.append(host_model)
        return host_list

    def list_storage_host_groups(self, storage_id):
        host_groups = self.ssh_handler.list_storage_host_groups()
        host_group_list = []
        result = {}
        if host_groups:
            hosts_map = self.ssh_handler.get_resources_ids(
                self.ssh_handler.HPE3PAR_COMMAND_SHOWHOST_D,
                consts.HOST_OR_VV_PATTERN)
            for host_group in host_groups:
                host_members = host_group.get('members')
                host_ids = []
                if hosts_map:
                    for host_name in (host_members or []):
                        host_id = hosts_map.get(host_name)
                        if host_id:
                            host_ids.append(host_id)
                host_group_model = {
                    "name": host_group.get('name'),
                    "description": host_group.get('comment'),
                    "storage_id": storage_id,
                    "native_storage_host_group_id": host_group.get('id'),
                    "storage_hosts": ','.join(host_ids)
                }
                host_group_list.append(host_group_model)
            storage_host_grp_relation_list = []
            for storage_host_group in host_group_list:
                storage_hosts = storage_host_group.pop('storage_hosts', None)
                if not storage_hosts:
                    continue
                storage_hosts = storage_hosts.split(',')

                for storage_host in storage_hosts:
                    storage_host_group_relation = {
                        'storage_id': storage_id,
                        'native_storage_host_group_id': storage_host_group.get(
                            'native_storage_host_group_id'),
                        'native_storage_host_id': storage_host
                    }
                    storage_host_grp_relation_list \
                        .append(storage_host_group_relation)

            result = {
                'storage_host_groups': host_group_list,
                'storage_host_grp_host_rels': storage_host_grp_relation_list
            }
        return result

    def list_port_groups(self, storage_id):
        views = self.ssh_handler.list_masking_views()
        port_groups_list = []
        port_list = []
        for view in (views or []):
            port = view.get('port', '').replace('-', '')
            if port:
                if port in port_list:
                    continue
                port_list.append(port)
                port_group_model = {
                    "name": "port_group_" + port,
                    "description": "port_group_" + port,
                    "storage_id": storage_id,
                    "native_port_group_id": "port_group_" + port,
                    "ports": port
                }
                port_groups_list.append(port_group_model)
        port_group_relation_list = []
        for port_group in port_groups_list:
            ports = port_group.pop('ports', None)
            if not ports:
                continue
            ports = ports.split(',')

            for port in ports:
                port_group_relation = {
                    'storage_id': storage_id,
                    'native_port_group_id':
                        port_group.get('native_port_group_id'),
                    'native_port_id': port
                }
                port_group_relation_list.append(port_group_relation)
        result = {
            'port_groups': port_groups_list,
            'port_grp_port_rels': port_group_relation_list
        }
        return result

    def list_volume_groups(self, storage_id):
        volume_groups = self.ssh_handler.list_volume_groups()
        volume_group_list = []
        result = {}
        if volume_groups:
            volumes_map = self.ssh_handler.get_resources_ids(
                self.ssh_handler.HPE3PAR_COMMAND_SHOWVV,
                consts.HOST_OR_VV_PATTERN)
            for volume_group in volume_groups:
                volume_members = volume_group.get('members')
                volume_ids = []
                if volumes_map:
                    for volume_name in (volume_members or []):
                        volume_id = volumes_map.get(volume_name)
                        if volume_id:
                            volume_ids.append(volume_id)
                volume_group_model = {
                    "name": volume_group.get('name'),
                    "description": volume_group.get('comment'),
                    "storage_id": storage_id,
                    "native_volume_group_id": volume_group.get('id'),
                    "volumes": ','.join(volume_ids)
                }
                volume_group_list.append(volume_group_model)
            volume_group_relation_list = []
            for volume_group in volume_group_list:
                volumes = volume_group.pop('volumes', None)
                if not volumes:
                    continue
                volumes = volumes.split(',')

                for volume in volumes:
                    volume_group_relation = {
                        'storage_id': storage_id,
                        'native_volume_group_id':
                            volume_group.get('native_volume_group_id'),
                        'native_volume_id': volume}
                    volume_group_relation_list.append(volume_group_relation)

            result = {
                'volume_groups': volume_group_list,
                'vol_grp_vol_rels': volume_group_relation_list
            }
        return result

    def list_masking_views(self, storage_id):
        views = self.ssh_handler.list_masking_views()
        views_list = []
        if views:
            hosts_map = self.ssh_handler.get_resources_ids(
                self.ssh_handler.HPE3PAR_COMMAND_SHOWHOST_D,
                consts.HOST_OR_VV_PATTERN)
            hosts_group_map = self.ssh_handler.get_resources_ids(
                self.ssh_handler.HPE3PAR_COMMAND_SHOWHOSTSET_D,
                consts.HOST_OR_VV_PATTERN)
            volumes_map = self.ssh_handler.get_resources_ids(
                self.ssh_handler.HPE3PAR_COMMAND_SHOWVV,
                consts.HOST_OR_VV_PATTERN)
            volumes_group_map = self.ssh_handler.get_resources_ids(
                self.ssh_handler.HPE3PAR_COMMAND_SHOWVVSET_D,
                consts.HOST_OR_VV_PATTERN)
            host_vv_set = set()
            for view in views:
                vv_name = view.get('vvname')
                host_name = view.get('hostname')
                if vv_name and host_name:
                    host_vv_key = '%s_%s' % (host_name, vv_name)
                    host_vv_key = host_vv_key.replace(' ', '')
                    if host_vv_key in host_vv_set:
                        continue
                    host_vv_set.add(host_vv_key)
                    port = view.get('port', '').replace('-', '')
                    lun_id = view.get('lun')
                    wwn = view.get('host_wwn/iscsi_name', '').replace('-', '')
                    native_port_group_id = None
                    if port:
                        lun_id = '%s_%s' % (lun_id, port)
                        native_port_group_id = 'port_group_%s' % port
                    if wwn:
                        lun_id = '%s_%s' % (lun_id, wwn)
                    lun_id = '%s_%s' % (lun_id, host_vv_key)
                    view_model = {
                        'native_masking_view_id': lun_id,
                        "name": view.get('lun'),
                        'native_port_group_id': native_port_group_id,
                        "storage_id": storage_id
                    }
                    if 'set:' in vv_name:
                        vv_set_id = volumes_group_map.get(
                            vv_name.replace('set:', ''))
                        view_model['native_volume_group_id'] = vv_set_id
                    else:
                        vv_id = volumes_map.get(vv_name)
                        view_model['native_volume_id'] = vv_id
                    if 'set:' in host_name:
                        host_set_id = hosts_group_map.get(
                            host_name.replace('set:', ''))
                        view_model[
                            'native_storage_host_group_id'] = host_set_id
                    else:
                        host_id = hosts_map.get(host_name)
                        view_model['native_storage_host_id'] = host_id
                    if (view_model.get('native_storage_host_id')
                        or view_model.get('native_storage_host_group_id')) \
                            and (view_model.get('native_volume_id')
                                 or view_model.get('native_volume_group_id')):
                        views_list.append(view_model)
        return views_list
