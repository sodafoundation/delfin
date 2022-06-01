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
import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.dell_emc.unity import rest_handler, alert_handler, consts
from delfin.drivers.dell_emc.unity.alert_handler import AlertHandler

LOG = log.getLogger(__name__)


class UnityStorDriver(driver.StorageDriver):
    """UnityStorDriver implement the DELL EMC Storage driver"""
    HEALTH_OK = (5, 7)
    STORAGE_STATUS_MAP = {5: constants.StorageStatus.NORMAL,
                          7: constants.StorageStatus.NORMAL,
                          15: constants.StorageStatus.NORMAL,
                          20: constants.StorageStatus.NORMAL,
                          10: constants.StorageStatus.DEGRADED
                          }
    FILESYSTEM_FLR_MAP = {0: constants.WORMType.NON_WORM,
                          1: constants.WORMType.ENTERPRISE,
                          2: constants.WORMType.COMPLIANCE
                          }
    FILESYSTEM_SECURITY_MAP = {0: constants.NASSecurityMode.NATIVE,
                               1: constants.NASSecurityMode.UNIX,
                               2: constants.NASSecurityMode.NTFS
                               }
    CONTROLLER_STATUS_MAP = {5: constants.ControllerStatus.NORMAL,
                             7: constants.ControllerStatus.NORMAL,
                             10: constants.ControllerStatus.DEGRADED
                             }
    DISK_TYPE_MAP = {1: constants.DiskPhysicalType.SAS,
                     2: constants.DiskPhysicalType.NL_SAS,
                     6: constants.DiskPhysicalType.FLASH,
                     7: constants.DiskPhysicalType.FLASH,
                     8: constants.DiskPhysicalType.FLASH,
                     9: constants.DiskPhysicalType.FLASH,
                     99: constants.DiskPhysicalType.VMDISK
                     }
    VOLUME_PERF_METRICS = {
        'readIops': 'sp.*.storage.lun.*.readsRate',
        'writeIops': 'sp.*.storage.lun.*.writesRate',
        'readThroughput': 'sp.*.storage.lun.*.readBytesRate',
        'writeThroughput': 'sp.*.storage.lun.*.writeBytesRate',
        'responseTime': 'sp.*.storage.lun.*.responseTime',
        'readIoSize': 'sp.*.storage.lun.*.avgReadSize',
        'writeIoSize': 'sp.*.storage.lun.*.avgWriteSize'
    }
    DISK_PERF_METRICS = {
        'readIops': 'sp.*.physical.disk.*.readsRate',
        'writeIops': 'sp.*.physical.disk.*.writesRate',
        'readThroughput': 'sp.*.physical.disk.*.readBytesRate',
        'writeThroughput': 'sp.*.physical.disk.*.writeBytesRate',
        'responseTime': 'sp.*.physical.disk.*.responseTime'
    }
    ETHERNET_PORT_METRICS = {
        'readThroughput': 'sp.*.net.device.*.bytesInRate',
        'writeThroughput': 'sp.*.net.device.*.bytesOutRate',
        'readIops': 'sp.*.net.device.*.pktsInRate',
        'writeIops': 'sp.*.net.device.*.pktsOutRate',
    }
    FC_PORT_METRICS = {
        'readIops': 'sp.*.fibreChannel.fePort.*.readsRate',
        'writeIops': 'sp.*.fibreChannel.fePort.*.writesRate',
        'readThroughput': 'sp.*.fibreChannel.fePort.*.readBytesRate',
        'writeThroughput': 'sp.*.fibreChannel.fePort.*.writeBytesRate'
    }
    ISCSI_PORT_METRICS = {
        'readIops': 'sp.*.iscsi.fePort.*.readsRate',
        'writeIops': 'sp.*.iscsi.fePort.*.writesRate',
        'readThroughput': 'sp.*.iscsi.fePort.*.readBytesRate',
        'writeThroughput': 'sp.*.iscsi.fePort.*.writeBytesRate'
    }
    FILESYSTEM_PERF_METRICS = {
        'readIops': 'sp.*.storage.filesystem.*.readsRate',
        'writeIops': 'sp.*.storage.filesystem.*.writesRate',
        'readThroughput': 'sp.*.storage.filesystem.*.readBytesRate',
        'writeThroughput': 'sp.*.storage.filesystem.*.writeBytesRate',
        'readIoSize': 'sp.*.storage.filesystem.*.readSizeAvg',
        'writeIoSize': 'sp.*.storage.filesystem.*.writeSizeAvg'
    }
    PERF_TYPE_MAP = {
        'readIops': {'write': 'writeIops',
                     'total': 'iops'},
        'readThroughput': {'write': 'writeThroughput',
                           'total': 'throughput'},
        'readIoSize': {'write': 'writeIoSize',
                       'total': 'ioSize'},
    }
    MS_PER_HOUR = 60 * 60 * 1000

    OS_TYPE_MAP = {'AIX': constants.HostOSTypes.AIX,
                   'Citrix XenServer': constants.HostOSTypes.XEN_SERVER,
                   'HP-UX': constants.HostOSTypes.HP_UX,
                   'IBM VIOS': constants.HostOSTypes.UNKNOWN,
                   'Linux': constants.HostOSTypes.LINUX,
                   'Mac OS': constants.HostOSTypes.MAC_OS,
                   'Solaris': constants.HostOSTypes.SOLARIS,
                   'VMware ESXi': constants.HostOSTypes.VMWARE_ESX,
                   'Windows Client': constants.HostOSTypes.WINDOWS,
                   'Windows Server': constants.HostOSTypes.WINDOWS
                   }
    INITIATOR_STATUS_MAP = {5: constants.InitiatorStatus.ONLINE,
                            7: constants.InitiatorStatus.ONLINE,
                            15: constants.InitiatorStatus.ONLINE,
                            20: constants.InitiatorStatus.ONLINE,
                            10: constants.InitiatorStatus.OFFLINE
                            }
    HOST_STATUS_MAP = {5: constants.HostStatus.NORMAL,
                       7: constants.HostStatus.NORMAL,
                       15: constants.HostStatus.NORMAL,
                       20: constants.HostStatus.NORMAL,
                       10: constants.HostStatus.DEGRADED
                       }
    INITIATOR_TYPE_MAP = {0: constants.InitiatorType.UNKNOWN,
                          1: constants.InitiatorType.FC,
                          2: constants.InitiatorType.ISCSI
                          }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.verify = kwargs.get('verify', False)
        self.rest_handler.login()

    def close_connection(self):
        self.rest_handler.logout()

    def get_disk_capacity(self, context):
        raw_capacity = 0
        try:
            disk_info = self.list_disks(context)
            if disk_info:
                for disk in disk_info:
                    raw_capacity += disk.get('capacity')
        except Exception:
            LOG.info("get disk info fail in get_disk_capacity")
        return raw_capacity

    def get_storage(self, context):
        system_info = self.rest_handler.get_storage()
        capacity = self.rest_handler.get_capacity()
        version_info = self.rest_handler.get_soft_version()
        if not system_info or not capacity:
            err_msg = "unity get system or capacity info failed"
            LOG.error(err_msg)
            raise exception.StorageBackendException(err_msg)
        system_entries = system_info.get('entries')
        for system in system_entries:
            content = system.get('content', {})
            name = content.get('name')
            model = content.get('model')
            serial_number = content.get('serialNumber')
            health_value = content.get('health', {}).get('value')
            status = UnityStorDriver.STORAGE_STATUS_MAP.get(
                health_value, constants.StorageStatus.ABNORMAL)
            break
        capacity_info = capacity.get('entries')
        for per_capacity in capacity_info:
            content = per_capacity.get('content', {})
            free = content.get('sizeFree')
            total = content.get('sizeTotal')
            used = content.get('sizeUsed')
            subs = content.get('sizeSubscribed')
            break
        if version_info:
            soft_version = version_info.get('entries')
            for soft_info in soft_version:
                content = soft_info.get('content', {})
                if content:
                    version = content.get('id')
                    break
        raw_capacity = self.get_disk_capacity(context)
        raw_capacity = raw_capacity if raw_capacity else int(total)
        system_result = {
            'name': name,
            'vendor': 'DELL EMC',
            'model': model,
            'status': status,
            'serial_number': serial_number,
            'firmware_version': version,
            'location': '',
            'subscribed_capacity': int(subs),
            'total_capacity': int(total),
            'raw_capacity': raw_capacity,
            'used_capacity': int(used),
            'free_capacity': int(free)
        }
        return system_result

    def list_storage_pools(self, context):
        pool_info = self.rest_handler.get_all_pools()
        pool_list = []
        pool_type = constants.StorageType.UNIFIED
        if pool_info is not None:
            pool_entries = pool_info.get('entries')
            for pool in pool_entries:
                content = pool.get('content', {})
                health_value = content.get('health').get('value')
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                pool_result = {
                    'name': content.get('name'),
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': str(content.get('id')),
                    'description': content.get('description'),
                    'status': status,
                    'storage_type': pool_type,
                    'total_capacity': int(content.get('sizeTotal')),
                    'subscribed_capacity': int(content.get('sizeSubscribed')),
                    'used_capacity': int(content.get('sizeUsed')),
                    'free_capacity': int(content.get('sizeFree'))
                }
                pool_list.append(pool_result)
        return pool_list

    def volume_handler(self, volumes, volume_list):
        if volumes is not None:
            vol_entries = volumes.get('entries')
            for volume in vol_entries:
                content = volume.get('content', {})
                total = content.get('sizeTotal')
                used = content.get('sizeAllocated')
                vol_type = constants.VolumeType.THICK
                if content.get('isThinEnabled') is True:
                    vol_type = constants.VolumeType.THIN
                health_value = content.get('health').get('value')
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
                volume_result = {
                    'name': content.get('name'),
                    'storage_id': self.storage_id,
                    'description': content.get('description'),
                    'status': status,
                    'native_volume_id': str(content.get('id')),
                    'native_storage_pool_id': content.get('pool').get('id'),
                    'wwn': content.get('wwn'),
                    'type': vol_type,
                    'total_capacity': int(total),
                    'used_capacity': int(used),
                    'free_capacity': int(total - used)
                }
                volume_list.append(volume_result)

    def list_volumes(self, context):
        page_number = 1
        volume_list = []
        while True:
            luns = self.rest_handler.get_all_luns(page_number)
            if luns is None:
                break
            if 'entries' not in luns:
                break
            if len(luns['entries']) < 1:
                break
            self.volume_handler(luns, volume_list)
            page_number = page_number + 1

        return volume_list

    def list_alerts(self, context, query_para=None):
        page_number = 1
        alert_model_list = []
        while True:
            alert_list = self.rest_handler.get_all_alerts(page_number)
            if not alert_list:
                alert_list = self.rest_handler.get_all_alerts_without_state(
                    page_number)
            if alert_list is None:
                break
            if 'entries' not in alert_list:
                break
            if len(alert_list['entries']) < 1:
                break
            alert_handler.AlertHandler() \
                .parse_queried_alerts(alert_model_list, alert_list, query_para)
            page_number = page_number + 1

        return alert_model_list

    def list_controllers(self, context):
        try:
            controller_list = []
            controller_info = self.rest_handler.get_all_controllers()
            if controller_info is not None:
                pool_entries = controller_info.get('entries')
                for pool in pool_entries:
                    content = pool.get('content')
                    if not content:
                        continue
                    health_value = content.get('health', {}).get('value')
                    status = UnityStorDriver.CONTROLLER_STATUS_MAP.get(
                        health_value,
                        constants.ControllerStatus.FAULT
                    )
                    controller_result = {
                        'name': content.get('name'),
                        'storage_id': self.storage_id,
                        'native_controller_id': content.get('id'),
                        'status': status,
                        'location': content.get('slotNumber'),
                        'memory_size':
                            int(content.get('memorySize')) * units.Mi
                    }
                    controller_list.append(controller_result)
            return controller_list
        except Exception as err:
            err_msg = "Failed to get controller attributes from Unity: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def handle_port_ip(ip, result):
        if ip is None:
            ip = result
        else:
            ip = '%s;%s' % (ip, result)
        return ip

    def get_eth_ports(self):
        port_list = []
        ports = self.rest_handler.get_all_ethports()
        ip_interfaces = self.rest_handler.get_port_interface()
        if ports:
            port_entries = ports.get('entries')
            for port in port_entries:
                content = port.get('content')
                if not content:
                    continue
                health_value = content.get('health', {}).get('value')
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.PortHealthStatus.NORMAL
                else:
                    status = constants.PortHealthStatus.ABNORMAL
                conn_status = constants.PortConnectionStatus.CONNECTED if \
                    content.get('isLinkUp') is True \
                    else constants.PortConnectionStatus.DISCONNECTED
                ipv4 = None
                ipv4_mask = None
                ipv6 = None
                ipv6_mask = None
                if ip_interfaces:
                    for ip_info in ip_interfaces.get('entries'):
                        ip_content = ip_info.get('content')
                        if not ip_content:
                            continue
                        if content.get('id') == ip_content.get(
                                'ipPort').get('id'):
                            if ip_content.get('ipProtocolVersion') == 4:
                                ipv4 = UnityStorDriver.handle_port_ip(
                                    ipv4, ip_content.get('ipAddress'))
                                ipv4_mask = UnityStorDriver.handle_port_ip(
                                    ipv4_mask, ip_content.get('netmask'))
                            else:
                                ipv6 = UnityStorDriver.handle_port_ip(
                                    ipv6, ip_content.get('ipAddress'))
                                ipv6_mask = UnityStorDriver.handle_port_ip(
                                    ipv6_mask, ip_content.get('netmask'))
                port_result = {
                    'name': content.get('name'),
                    'storage_id': self.storage_id,
                    'native_port_id': content.get('id'),
                    'location': content.get('name'),
                    'connection_status': conn_status,
                    'health_status': status,
                    'type': constants.PortType.ETH,
                    'logical_type': '',
                    'speed': int(content.get('speed')) * units.M
                    if content.get('speed') is not None else None,
                    'max_speed': int(content.get('speed')) * units.M
                    if content.get('speed') is not None else None,
                    'native_parent_id':
                        content.get('storageProcessor', {}).get('id'),
                    'wwn': '',
                    'mac_address': content.get('macAddress'),
                    'ipv4': ipv4,
                    'ipv4_mask': ipv4_mask,
                    'ipv6': ipv6,
                    'ipv6_mask': ipv6_mask
                }
                port_list.append(port_result)
        return port_list

    def get_fc_ports(self):
        port_list = []
        ports = self.rest_handler.get_all_fcports()
        if ports:
            port_entries = ports.get('entries')
            for port in port_entries:
                content = port.get('content')
                if not content:
                    continue
                health_value = content.get('health', {}).get('value')
                connect_value = \
                    content.get('health', {}).get('descriptionIds', [])
                if 'ALRT_PORT_LINK_DOWN_NOT_IN_USE' in connect_value:
                    conn_status = constants.PortConnectionStatus.DISCONNECTED
                elif 'ALRT_PORT_LINK_UP' in connect_value:
                    conn_status = constants.PortConnectionStatus.CONNECTED
                else:
                    conn_status = constants.PortConnectionStatus.UNKNOWN
                if health_value in UnityStorDriver.HEALTH_OK:
                    status = constants.PortHealthStatus.NORMAL
                else:
                    status = constants.PortHealthStatus.ABNORMAL
                port_result = {
                    'name': content.get('name'),
                    'storage_id': self.storage_id,
                    'native_port_id': content.get('id'),
                    'location': content.get('name'),
                    'connection_status': conn_status,
                    'health_status': status,
                    'type': constants.PortType.FC,
                    'logical_type': '',
                    'speed': int(content.get('currentSpeed')) * units.G
                    if content.get('currentSpeed') is not None else None,
                    'max_speed': int(content.get('currentSpeed')) * units.G
                    if content.get('currentSpeed') is not None else None,
                    'native_parent_id':
                        content.get('storageProcessor', {}).get('id'),
                    'wwn': content.get('wwn')
                }
                port_list.append(port_result)
        return port_list

    def list_ports(self, context):
        try:
            port_list = []
            port_list.extend(self.get_eth_ports())
            port_list.extend(self.get_fc_ports())
            return port_list
        except Exception as err:
            err_msg = "Failed to get ports attributes from Unity: %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def list_disks(self, context):
        try:
            disks = self.rest_handler.get_all_disks()
            disk_list = []
            if disks and disks.get('entries'):
                disk_entries = disks.get('entries')
                for disk in disk_entries:
                    content = disk.get('content')
                    if not content:
                        continue
                    health_value = content.get('health', {}).get('value')
                    slot_info = \
                        content.get('health', {}).get('descriptionIds', [])
                    if 'ALRT_DISK_SLOT_EMPTY' in slot_info:
                        continue
                    if health_value in UnityStorDriver.HEALTH_OK:
                        status = constants.DiskStatus.NORMAL
                    else:
                        status = constants.DiskStatus.ABNORMAL
                    physical_type = UnityStorDriver.DISK_TYPE_MAP.get(
                        content.get('diskTechnology'),
                        constants.DiskPhysicalType.UNKNOWN)
                    disk_result = {
                        'name': content.get('name'),
                        'storage_id': self.storage_id,
                        'native_disk_id': content.get('id'),
                        'serial_number': content.get('emcSerialNumber'),
                        'manufacturer': content.get('manufacturer'),
                        'model': content.get('model'),
                        'firmware': content.get('version'),
                        'speed': int(content.get('rpm')),
                        'capacity': int(content.get('size')),
                        'status': status,
                        'physical_type': physical_type,
                        'logical_type': '',
                        'native_disk_group_id':
                            content.get('diskGroup', {}).get('id'),
                        'location': content.get('name')
                    }
                    disk_list.append(disk_result)
            else:
                disk_list = self.get_virtual_disk()
            return disk_list

        except Exception as err:
            err_msg = "Failed to get disk attributes from Unity: %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def list_filesystems(self, context):
        try:
            files = self.rest_handler.get_all_filesystems()
            if not files:
                files = self.rest_handler.get_all_filesystems_without_flr()
            fs_list = []
            if files is not None:
                fs_entries = files.get('entries')
                for file in fs_entries:
                    content = file.get('content')
                    if not content:
                        continue
                    health_value = content.get('health', {}).get('value')
                    if health_value in UnityStorDriver.HEALTH_OK:
                        status = constants.FilesystemStatus.NORMAL
                    else:
                        status = constants.FilesystemStatus.FAULTY
                    fs_type = constants.VolumeType.THICK
                    if content.get('isThinEnabled') is True:
                        fs_type = constants.VolumeType.THIN
                    worm = UnityStorDriver.FILESYSTEM_FLR_MAP.get(
                        content.get('flrVersion'),
                        constants.WORMType.NON_WORM)
                    security_model = \
                        UnityStorDriver.FILESYSTEM_SECURITY_MAP.get(
                            content.get('accessPolicy'),
                            constants.NASSecurityMode.NATIVE
                        )
                    fs = {
                        'name': content.get('name'),
                        'storage_id': self.storage_id,
                        'native_filesystem_id': content.get('id'),
                        'native_pool_id': content.get('pool', {}).get('id'),
                        'status': status,
                        'type': fs_type,
                        'total_capacity': int(content.get('sizeTotal')),
                        'used_capacity': int(content.get('sizeUsed')),
                        'free_capacity': int(content.get('sizeTotal')) - int(
                            content.get('sizeUsed')),
                        'worm': worm,
                        'security_mode': security_model
                    }
                    fs_list.append(fs)
            return fs_list
        except Exception as err:
            err_msg = "Failed to get filesystem attributes from Unity: %s"\
                      % (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def list_qtrees(self, context):
        try:
            qts = self.rest_handler.get_all_qtrees()
            qt_list = []
            if qts is not None:
                qts_entries = qts.get('entries')
                for qtree in qts_entries:
                    content = qtree.get('content')
                    if not content:
                        continue
                    qt = {
                        'name': content.get('path'),
                        'storage_id': self.storage_id,
                        'native_qtree_id': content.get('id'),
                        'native_filesystem_id':
                            content.get('filesystem', {}).get('id'),
                        'path': content.get('path')
                    }
                    qt_list.append(qt)
            return qt_list
        except Exception as err:
            err_msg = "Failed to get qtree attributes from Unity: %s"\
                      % (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def get_share_qtree(self, path, qtree_list):
        qtree_id = None
        if not qtree_list:
            return qtree_id
        qts_entries = qtree_list.get('entries')
        for qtree in qts_entries:
            content = qtree.get('content')
            if not content:
                continue
            if content.get('path') == path:
                qtree_id = content.get('id')
                break
        return qtree_id

    def get_share(self, protocol, qtree_list, filesystems):
        try:
            share_list = []
            if protocol == 'cifs':
                shares = self.rest_handler.get_all_cifsshares()
                protocol = constants.ShareProtocol.CIFS
            else:
                shares = self.rest_handler.get_all_nfsshares()
                protocol = constants.ShareProtocol.NFS
            if shares is not None:
                share_entries = shares.get('entries')
                for share in share_entries:
                    content = share.get('content')
                    if not content:
                        continue
                    file_name = ''
                    if filesystems:
                        file_entries = filesystems.get('entries')
                        for file in file_entries:
                            file_content = file.get('content')
                            if not file_content:
                                continue
                            if file_content.get('id') == content.get(
                                    'filesystem', {}).get('id'):
                                file_name = file_content.get('name')
                                break
                    path = '/%s%s' % (file_name, content.get('path')) if \
                        file_name != '' else content.get('path')
                    fs = {
                        'name': content.get('name'),
                        'storage_id': self.storage_id,
                        'native_share_id': content.get('id'),
                        'native_qtree_id': self.get_share_qtree(
                            content.get('path'), qtree_list),
                        'native_filesystem_id':
                            content.get('filesystem', {}).get('id'),
                        'path': path,
                        'protocol': protocol
                    }
                    share_list.append(fs)
            return share_list
        except Exception as err:
            err_msg = "Failed to get share attributes from Unity: %s"\
                      % (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def list_shares(self, context):
        try:
            share_list = []
            qtrees = self.rest_handler.get_all_qtrees()
            filesystems = self.rest_handler.get_all_filesystems()
            if not filesystems:
                filesystems = \
                    self.rest_handler.get_all_filesystems_without_flr()
            share_list.extend(self.get_share('cifs', qtrees, filesystems))
            share_list.extend(self.get_share('nfs', qtrees, filesystems))
            return share_list
        except Exception as err:
            err_msg = "Failed to get shares attributes from Unity: %s"\
                      % (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def get_tree_quotas(self):
        quotas_list = []
        qts = self.rest_handler.get_all_qtrees()
        if qts is None:
            return quotas_list
        qt_entries = qts.get('entries')
        for quota in qt_entries:
            content = quota.get('content')
            if not content:
                continue
            qt = {
                "native_quota_id": content.get('id'),
                "type": constants.QuotaType.TREE,
                "storage_id": self.storage_id,
                "native_filesystem_id":
                    content.get('filesystem', {}).get('id'),
                "native_qtree_id": content.get('id'),
                "capacity_hard_limit": content.get('hardLimit'),
                "capacity_soft_limit": content.get('softLimit'),
                "used_capacity": int(content.get('sizeUsed'))
            }
            quotas_list.append(qt)
        return quotas_list

    def get_user_quotas(self):
        quotas_list = []
        user_qts = self.rest_handler.get_all_userquotas()
        if user_qts is None:
            return quotas_list
        user_entries = user_qts.get('entries')
        for user_quota in user_entries:
            content = user_quota.get('content')
            if not content:
                continue
            qt = {
                "native_quota_id": content.get('id'),
                "type": constants.QuotaType.USER,
                "storage_id": self.storage_id,
                "native_filesystem_id":
                    content.get('filesystem', {}).get('id'),
                "native_qtree_id": content.get('treeQuota', {}).get('id'),
                "capacity_hard_limit": content.get('hardLimit'),
                "capacity_soft_limit": content.get('softLimit'),
                "used_capacity": int(content.get('sizeUsed')),
                "user_group_name": str(content.get('uid'))
            }
            quotas_list.append(qt)
        return quotas_list

    def list_quotas(self, context):
        try:
            quotas_list = []
            quotas_list.extend(self.get_tree_quotas())
            quotas_list.extend(self.get_user_quotas())
            return quotas_list
        except Exception as err:
            err_msg = "Failed to get quotas attributes from Unity: %s"\
                      % (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return AlertHandler.parse_alert(context, alert)

    def clear_alert(self, context, alert):
        return self.rest_handler.remove_alert(alert)

    @staticmethod
    def get_access_url():
        return 'https://{ip}'

    def list_storage_host_initiators(self, context):
        try:
            initiator_list = []
            page = 1
            while True:
                initiators = self.rest_handler.get_host_initiators(page)
                if not initiators:
                    return initiator_list
                if 'entries' not in initiators or \
                        len(initiators['entries']) < 1:
                    break
                init_entries = initiators.get('entries')
                for initiator in init_entries:
                    content = initiator.get('content')
                    if not content:
                        continue
                    health_value = content.get('health', {}).get('value')
                    status = UnityStorDriver.INITIATOR_STATUS_MAP.get(
                        health_value,
                        constants.InitiatorStatus.UNKNOWN
                    )
                    init_result = {
                        "name": content.get('initiatorId'),
                        "storage_id": self.storage_id,
                        "native_storage_host_initiator_id": content.get('id'),
                        "wwn": content.get('initiatorId'),
                        "status": status,
                        "type": UnityStorDriver.INITIATOR_TYPE_MAP.get(
                            content.get('type')),
                        "native_storage_host_id": content.get(
                            'parentHost', {}).get('id')
                    }
                    initiator_list.append(init_result)
                page += 1
            return initiator_list
        except Exception as e:
            LOG.error("Failed to get initiators from unity")
            raise e

    def list_storage_hosts(self, context):
        try:
            host_list = []
            page = 1
            while True:
                hosts = self.rest_handler.get_all_hosts(page)
                if not hosts:
                    return host_list
                if 'entries' not in hosts or len(hosts['entries']) < 1:
                    break
                ips = self.rest_handler.get_host_ip()
                host_entries = hosts.get('entries')
                for host in host_entries:
                    host_ip = None
                    content = host.get('content')
                    if not content:
                        continue
                    health_value = content.get('health', {}).get('value')
                    status = UnityStorDriver.HOST_STATUS_MAP.get(
                        health_value,
                        constants.HostStatus.OFFLINE
                    )
                    if ips:
                        ip_entries = ips.get('entries')
                        for ip in ip_entries:
                            ip_content = ip.get('content')
                            if not ip_content:
                                continue
                            if ip_content.get('host', {}).get('id') \
                                    == content.get('id'):
                                host_ip = ip_content.get('address')
                                break
                    if content.get('osType'):
                        if 'VMware ESXi' in content.get('osType'):
                            os_type = constants.HostOSTypes.VMWARE_ESX
                        else:
                            os_type = UnityStorDriver.OS_TYPE_MAP.get(
                                content.get('osType'),
                                constants.HostOSTypes.UNKNOWN)
                    else:
                        os_type = None
                    host_result = {
                        "name": content.get('name'),
                        "description": content.get('description'),
                        "storage_id": self.storage_id,
                        "native_storage_host_id": content.get('id'),
                        "os_type": os_type,
                        "status": status,
                        "ip_address": host_ip
                    }
                    host_list.append(host_result)
                page += 1
            return host_list
        except Exception as e:
            LOG.error("Failed to get host metrics from unity")
            raise e

    def list_masking_views(self, context):
        try:
            view_list = []
            page = 1
            while True:
                views = self.rest_handler.get_host_lun(page)
                if not views:
                    return view_list
                if 'entries' not in views or len(views['entries']) < 1:
                    break
                view_entries = views.get('entries')
                for view in view_entries:
                    content = view.get('content')
                    view_result = {
                        "name": content.get('id'),
                        "native_storage_host_id":
                            content.get('host', {}).get('id'),
                        "storage_id": self.storage_id,
                        "native_volume_id": content.get('lun', {}).get('id'),
                        "native_masking_view_id": content.get('id'),
                    }
                    view_list.append(view_result)
                page += 1
            return view_list

        except Exception as e:
            LOG.error("Failed to get view metrics from unity")
            raise e

    def get_metrics_loop(self, target, start_time,
                         end_time, metrics, path):
        page = 1
        bend = False
        time_map = {'latest_time': 0}
        if not path:
            return
        while True:
            if bend is True:
                break
            results = self.rest_handler.get_history_metrics(path, page)
            if not results:
                break
            if 'entries' not in results:
                break
            if len(results['entries']) < 1:
                break
            bend = UnityStorDriver.get_metric_value(
                target, start_time, end_time, metrics, results, time_map)
            page += 1

    def get_history_metrics(self, resource_type, targets,
                            start_time, end_time):
        metrics = []
        for target in targets:
            path = None
            if resource_type == constants.ResourceType.VOLUME:
                path = self.VOLUME_PERF_METRICS.get(target)
            elif resource_type == constants.ResourceType.DISK:
                path = self.DISK_PERF_METRICS.get(target)
            elif resource_type == constants.ResourceType.FILESYSTEM:
                path = self.FILESYSTEM_PERF_METRICS.get(target)
            elif resource_type == constants.ResourceType.PORT:
                self.get_metrics_loop(target, start_time, end_time, metrics,
                                      self.ETHERNET_PORT_METRICS.get(target))
                self.get_metrics_loop(target, start_time, end_time, metrics,
                                      self.FC_PORT_METRICS.get(target))
                continue
            if path:
                self.get_metrics_loop(target, start_time, end_time,
                                      metrics, path)
        return metrics

    @staticmethod
    def get_metric_value(target, start_time, end_time, metrics,
                         results, time_map):
        try:
            if results is None:
                return True
            entries = results.get('entries')
            for entry in entries:
                content = entry.get('content')
                if not content or not content.get('values'):
                    continue
                occur_time = int(time.mktime(time.strptime(
                    content.get('timestamp'),
                    AlertHandler.TIME_PATTERN))
                ) * AlertHandler.SECONDS_TO_MS
                hour_offset = (time.mktime(time.localtime()) - time.mktime(
                    time.gmtime())) / AlertHandler.SECONDS_PER_HOUR
                occur_time = occur_time + (int(hour_offset) *
                                           UnityStorDriver.MS_PER_HOUR)
                if occur_time < start_time:
                    return True
                if time_map.get('latest_time') <= occur_time \
                        and time_map.get('latest_time') != 0:
                    continue
                time_map['latest_time'] = occur_time
                if start_time <= occur_time <= end_time:
                    for sp_value in content.get('values'):
                        perf_value = content.get('values').get(sp_value)
                        for key, value in perf_value.items():
                            bfind = False
                            value = float(value)
                            for metric in metrics:
                                if metric.get('resource_id') == key and \
                                        metric.get('type') == target:
                                    if metric.get('values').get(
                                            occur_time):
                                        if target == 'responseTime':
                                            metric.get(
                                                'values')[occur_time] = \
                                                max(value, metric.get(
                                                    'values').get(
                                                    occur_time))
                                        else:
                                            metric.get('values')[
                                                occur_time] += value
                                    else:
                                        metric.get('values')[occur_time] \
                                            = value
                                    bfind = True
                                    break
                            if bfind is False:
                                metric_value = {
                                    'type': target,
                                    'resource_id': key,
                                    'values': {occur_time: value}
                                }
                                metrics.append(metric_value)
        except Exception as err:
            err_msg = "Failed to collect history metrics from Unity: %s, " \
                      "target:%s" % (six.text_type(err), target)
            LOG.error(err_msg)
        return False

    @staticmethod
    def count_total_perf(metrics):
        if metrics is None:
            return
        for metric in metrics:
            write_tye = None
            total_type = None
            if UnityStorDriver.PERF_TYPE_MAP.get(metric.get('type')):
                write_tye = UnityStorDriver.PERF_TYPE_MAP.get(
                    metric.get('type')).get('write')
                total_type = UnityStorDriver.PERF_TYPE_MAP.get(
                    metric.get('type')).get('total')
            else:
                continue
            for metric_write in metrics:
                if metric_write.get('resource_id') == \
                        metric.get('resource_id') \
                        and metric_write.get('type') == write_tye:
                    total = {
                        'type': total_type,
                        'resource_id': metric.get('resource_id')
                    }
                    bfind_total = False
                    for tr, read in metric.get('values').items():
                        for tw, write in metric_write.get(
                                'values').items():
                            if tr == tw:
                                value = read + write
                                if total.get('values'):
                                    total['values'][tr] = value
                                else:
                                    total['values'] = {tr: value}
                                bfind_total = True
                                break
                    if bfind_total:
                        metrics.append(total)
                    break

    @staticmethod
    def package_metrics(storage_id, resource_type, metrics, metrics_list):
        for metric in metrics_list:
            unit = None
            if resource_type == constants.ResourceType.PORT:
                unit = consts.PORT_CAP[metric.get('type')]['unit']
            elif resource_type == constants.ResourceType.VOLUME:
                unit = consts.VOLUME_CAP[metric.get('type')]['unit']
            elif resource_type == constants.ResourceType.DISK:
                unit = consts.DISK_CAP[metric.get('type')]['unit']
            elif resource_type == constants.ResourceType.FILESYSTEM:
                unit = consts.FILESYSTEM_CAP[metric.get('type')]['unit']
            labels = {
                'storage_id': storage_id,
                'resource_type': resource_type,
                'resource_id': metric.get('resource_id'),
                'type': 'RAW',
                'unit': unit
            }
            if 'THROUGHPUT' in metric.get('type').upper() or \
                    'RESPONSETIME' in metric.get('type').upper():
                for tm in metric.get('values'):
                    metric['values'][tm] = metric['values'][tm] / units.k
            value = constants.metric_struct(name=metric.get('type'),
                                            labels=labels,
                                            values=metric.get('values'))
            metrics.append(value)

    def collect_perf_metrics(self, context, storage_id,
                             resource_metrics, start_time,
                             end_time):
        metrics = []
        try:
            if resource_metrics.get(constants.ResourceType.VOLUME):
                volume_metrics = self.get_history_metrics(
                    constants.ResourceType.VOLUME,
                    resource_metrics.get(constants.ResourceType.VOLUME),
                    start_time,
                    end_time)
                UnityStorDriver.count_total_perf(volume_metrics)
                UnityStorDriver.package_metrics(storage_id,
                                                constants.ResourceType.VOLUME,
                                                metrics, volume_metrics)
            if resource_metrics.get(constants.ResourceType.DISK):
                disk_metrics = self.get_history_metrics(
                    constants.ResourceType.DISK,
                    resource_metrics.get(constants.ResourceType.DISK),
                    start_time,
                    end_time)
                UnityStorDriver.count_total_perf(disk_metrics)
                UnityStorDriver.package_metrics(storage_id,
                                                constants.ResourceType.DISK,
                                                metrics, disk_metrics)
            if resource_metrics.get(constants.ResourceType.PORT):
                port_metrics = self.get_history_metrics(
                    constants.ResourceType.PORT,
                    resource_metrics.get(constants.ResourceType.PORT),
                    start_time,
                    end_time)
                UnityStorDriver.count_total_perf(port_metrics)
                UnityStorDriver.package_metrics(storage_id,
                                                constants.ResourceType.PORT,
                                                metrics, port_metrics)
            if resource_metrics.get(constants.ResourceType.FILESYSTEM):
                file_metrics = self.get_history_metrics(
                    constants.ResourceType.FILESYSTEM,
                    resource_metrics.get(constants.ResourceType.FILESYSTEM),
                    start_time,
                    end_time)
                UnityStorDriver.count_total_perf(file_metrics)
                UnityStorDriver.package_metrics(
                    storage_id, constants.ResourceType.FILESYSTEM,
                    metrics, file_metrics)
        except Exception as err:
            err_msg = "Failed to collect metrics from Unity: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return metrics

    @staticmethod
    def get_capabilities(context, filters=None):
        """Get capability of supported driver"""
        return {
            'is_historic': True,
            'resource_metrics': {
                constants.ResourceType.VOLUME: consts.VOLUME_CAP,
                constants.ResourceType.PORT: consts.PORT_CAP,
                constants.ResourceType.DISK: consts.DISK_CAP,
                constants.ResourceType.FILESYSTEM: consts.FILESYSTEM_CAP
            }
        }

    def get_latest_perf_timestamp(self, context):
        latest_time = 0
        page = 1
        results = self.rest_handler.get_history_metrics(
            UnityStorDriver.VOLUME_PERF_METRICS.get('readIops'), page)
        if not results:
            results = self.rest_handler.get_history_metrics(
                UnityStorDriver.ETHERNET_PORT_METRICS.get('readIops'), page)
        if results:
            if 'entries' in results:
                entries = results.get('entries')
                for entry in entries:
                    content = entry.get('content')
                    if not content:
                        continue
                    occur_time = int(time.mktime(time.strptime(
                        content.get('timestamp'),
                        AlertHandler.TIME_PATTERN))
                    ) * AlertHandler.SECONDS_TO_MS
                    hour_offset = \
                        (time.mktime(time.localtime()) -
                         time.mktime(time.gmtime()))\
                        / AlertHandler.SECONDS_PER_HOUR
                    occur_time = occur_time + (int(hour_offset) *
                                               UnityStorDriver.MS_PER_HOUR)
                    latest_time = occur_time
                    break
        return latest_time

    def get_virtual_disk(self):
        try:
            disks = self.rest_handler.get_virtual_disks()
            disk_list = []
            if disks is not None:
                disk_entries = disks.get('entries')
                for disk in disk_entries:
                    content = disk.get('content')
                    if not content:
                        continue
                    health_value = content.get('health', {}).get('value')
                    slot_info = \
                        content.get('health', {}).get('descriptionIds', [])
                    if 'ALRT_DISK_SLOT_EMPTY' in slot_info:
                        continue
                    if health_value in UnityStorDriver.HEALTH_OK:
                        status = constants.DiskStatus.NORMAL
                    else:
                        status = constants.DiskStatus.ABNORMAL
                    disk_result = {
                        'name': content.get('name'),
                        'storage_id': self.storage_id,
                        'native_disk_id': content.get('id'),
                        'capacity': int(content.get('sizeTotal')),
                        'status': status,
                        'manufacturer': content.get('manufacturer'),
                        'model': content.get('model'),
                        'physical_type': constants.DiskPhysicalType.VMDISK
                    }
                    disk_list.append(disk_result)
            return disk_list
        except Exception as err:
            err_msg = "Failed to get virtual disk from Unity: %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)
