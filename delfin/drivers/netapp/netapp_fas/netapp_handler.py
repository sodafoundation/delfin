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

import time
import paramiko
import six
from oslo_log import log as logging
from oslo_utils import units
from delfin.drivers.netapp.netapp_fas import netapp_constants
from delfin import exception, utils
from delfin.common import constants
from delfin.drivers.utils.ssh_client import SSHPool
import hashlib

LOG = logging.getLogger(__name__)


class NetAppHandler(object):

    OID_SERIAL_NUM = '1.3.6.1.4.1.789.1.1.9.0'
    OID_TRAP_DATA = '1.3.6.1.4.1.789.1.1.12.0'

    SECONDS_TO_MS = 1000

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    @staticmethod
    def parse_alert(alert):
        try:
            alert_info = alert.get(NetAppHandler.OID_TRAP_DATA)
            alert_arr = alert_info.split(":")
            if len(alert_arr) > 1:
                alert_name = alert_arr[0]
                description = alert_arr[1]
                if netapp_constants.SEVERITY_MAP.get(alert_name):
                    a = {
                        'alert_id': alert_name,
                        'alert_name': alert_name,
                        'severity': constants.Severity.CRITICAL,
                        'category': constants.Category.EVENT,
                        'type': constants.EventType.EQUIPMENT_ALARM,
                        'occur_time': int(time.time()),
                        'description': description,
                        'sequence_number': hashlib.md5(
                            (alert.get(NetAppHandler.OID_TRAP_DATA)
                             + str(time.time())).encode()).hexdigest(),
                        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                        'location': ''
                    }
                    return a
        except exception.DelfinException as e:
            err_msg = "Failed to parse alert from " \
                      "netapp_fas fas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to parse alert from " \
                      "netapp_fas fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def login(self):
        try:
            self.exec_ssh_command('version')
        except Exception as e:
            LOG.error("Failed to login netapp_fas %s" %
                      (six.text_type(e)))
            raise e

    @staticmethod
    def do_exec(command_str, ssh):
        result = None
        try:
            utils.check_ssh_injection(command_str)
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
                ssh_info = NetAppHandler.do_exec(command, ssh)
            return ssh_info
        except Exception as e:
            msg = "Failed to ssh netapp_fas %s: %s" % \
                  (command, six.text_type(e))
            raise exception.SSHException(msg)

    @staticmethod
    def change_capacity_to_bytes(unit):
        unit = unit.upper()
        if unit == 'TB':
            res = units.Ti
        elif unit == 'GB':
            res = units.Gi
        elif unit == 'MB':
            res = units.Mi
        elif unit == 'KB':
            res = units.Ki
        else:
            res = 1
        return int(res)

    def parse_string(self, value):
        capacity = 0
        if value and value != '' and value != '-':
            if value.isdigit():
                capacity = float(value)
            else:
                unit = value[-2:]
                capacity = float(value[:-2]) * int(
                    self.change_capacity_to_bytes(unit))
        return capacity

    @staticmethod
    def handle_detail(system_info, storage_map, split):
        detail_arr = system_info.split('\r\n')
        for detail in detail_arr:
            if detail is not None and detail != '':
                strinfo = detail.split(split + " ")
                key = strinfo[0].replace(' ', '')
                value = ''
                if len(strinfo) > 1:
                    value = strinfo[1]
                storage_map[key] = value

    def get_storage(self):
        try:
            STATUS_MAP = {
                'ok': constants.StorageStatus.NORMAL,
                'ok-with-suppressed': constants.StorageStatus.NORMAL,
                'degraded': constants.StorageStatus.ABNORMAL,
                'unreachable': constants.StorageStatus.ABNORMAL
            }
            raw_capacity = total_capacity = used_capacity = free_capacity = 0
            system_info = self.exec_ssh_command(
                netapp_constants.CLUSTER_SHOW_COMMAND)
            version = self.exec_ssh_command(
                netapp_constants.VERSION_SHOW_COMMAND)
            status_info = self.exec_ssh_command(
                netapp_constants.STORAGE_STATUS_COMMAND)
            version_arr = version.split('\r\n')
            status = STATUS_MAP.get(status_info.split("\r\n")[2])
            disk_list = self.get_disks(None)
            pool_list = self.list_storage_pools(None)
            storage_map = {}
            self.handle_detail(system_info, storage_map, split=':')
            for disk in disk_list:
                raw_capacity += disk['capacity']

            for pool in pool_list:
                total_capacity += pool['total_capacity']
                free_capacity += pool['free_capacity']
                used_capacity += pool['used_capacity']

            s = {
                "name": storage_map['ClusterName'],
                "vendor": netapp_constants.STORAGE_VENDOR,
                "model": '',
                "status": status,
                "serial_number": storage_map['ClusterSerialNumber'],
                "firmware_version": version_arr[0],
                "location": '',
                "total_capacity": total_capacity,
                "raw_capacity": raw_capacity,
                "used_capacity": used_capacity,
                "free_capacity": free_capacity
            }
            return s
        except exception.DelfinException as e:
            err_msg = "Failed to get storage from " \
                      "netapp_fas fas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage from " \
                      "netapp_fas fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_aggregate(self, storage_id):
        STATUS_MAP = {
            'online': constants.StoragePoolStatus.NORMAL,
            'creating': constants.StoragePoolStatus.NORMAL,
            'mounting': constants.StoragePoolStatus.NORMAL,
            'relocating': constants.StoragePoolStatus.NORMAL,
            'quiesced': constants.StoragePoolStatus.NORMAL,
            'quiescing': constants.StoragePoolStatus.NORMAL,
            'unmounted': constants.StoragePoolStatus.NORMAL,
            'unmounting': constants.StoragePoolStatus.NORMAL,
            'destroying': constants.StoragePoolStatus.NORMAL,
            'partial': constants.StoragePoolStatus.NORMAL,
            'frozen': constants.StoragePoolStatus.NORMAL,
            'reverted': constants.StoragePoolStatus.NORMAL,
            'restricted': constants.StoragePoolStatus.NORMAL,
            'inconsistent': constants.StoragePoolStatus.NORMAL,
            'iron_restricted': constants.StoragePoolStatus.NORMAL,
            'unknown': constants.StoragePoolStatus.ABNORMAL,
            'offline': constants.StoragePoolStatus.OFFLINE,
            'failed': constants.StoragePoolStatus.ABNORMAL,
            'remote_cluster': constants.StoragePoolStatus.NORMAL,
        }
        agg_list = []
        agg_info = self.exec_ssh_command(
            netapp_constants.AGGREGATE_SHOW_DETAIL_COMMAND)
        agg_arr = agg_info.split(
            netapp_constants.AGGREGATE_SPLIT_STR)
        agg_map = {}
        for agg in agg_arr[1:]:
            self.handle_detail(agg, agg_map, split=':')
            status = STATUS_MAP.get(agg_map['State'])
            p = {
                'name': agg_map['e'],
                'storage_id': storage_id,
                'native_storage_pool_id': agg_map['UUIDString'],
                'description': '',
                'status': status,
                'storage_type': constants.StorageType.UNIFIED,
                'total_capacity':
                    int(self.parse_string(agg_map['Size'])),
                'used_capacity':
                    int(self.parse_string(agg_map['UsedSize'])),
                'free_capacity':
                    int(self.parse_string(agg_map['AvailableSize'])),
            }
            agg_list.append(p)
        return agg_list

    def get_pool(self, storage_id):
        pool_list = []
        pool_info = self.exec_ssh_command(
            netapp_constants.POOLS_SHOW_DETAIL_COMMAND)
        pool_arr = pool_info.split(netapp_constants.POOLS_SPLIT_STR)
        pool_map = {}
        for pool_str in pool_arr[1:]:
            self.handle_detail(pool_str, pool_map, split=':')
            status = constants.StoragePoolStatus.ABNORMAL
            if pool_map['IsPoolHealthy?'] == 'true':
                status = constants.StoragePoolStatus.NORMAL
            p = {
                'name': pool_map['ame'],
                'storage_id': storage_id,
                'native_storage_pool_id': pool_map['UUIDofStoragePool'],
                'description': '',
                'status': status,
                'storage_type': constants.StorageType.UNIFIED,
                'total_capacity':
                    int(self.parse_string(pool_map['StoragePoolTotalSize'])),
                'used_capacity':
                    int(self.parse_string(pool_map['StoragePoolTotalSize'])) -
                    int(self.parse_string(pool_map['StoragePoolUsableSize'])),
                'free_capacity':
                    int(self.parse_string(pool_map['StoragePoolUsableSize']))
            }
            pool_list.append(p)
        return pool_list

    def list_storage_pools(self, storage_id):
        try:
            pool_list = self.get_pool(storage_id)
            agg_list = self.get_aggregate(storage_id)
            return agg_list + pool_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage pool from " \
                      "netapp_fas fas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage pool from " \
                      "netapp_fas fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_volumes(self, storage_id):
        try:
            STATUS_MAP = {
                'online': constants.VolumeStatus.AVAILABLE,
                'offline': constants.VolumeStatus.ERROR,
                'nvfail': constants.VolumeStatus.ERROR,
                'space-error': constants.VolumeStatus.ERROR,
                'foreign-lun-error': constants.VolumeStatus.ERROR,
            }
            volume_list = []
            volume_info = self.exec_ssh_command(
                netapp_constants.LUN_SHOW_DETAIL_COMMAND)
            volume_arr = volume_info.split(netapp_constants.LUN_SPLIT_STR)
            fs_list = self.get_filesystems(storage_id)
            volume_map = {}
            for volume_str in volume_arr[1:]:
                self.handle_detail(volume_str, volume_map, split=':')
                if volume_map is not None or volume_map != {}:
                    pool_id = ''
                    status = STATUS_MAP.get(volume_map['State'])
                    for fs in fs_list:
                        if fs['name'] == volume_map['VolumeName']:
                            pool_id = fs['native_pool_id']
                    type = constants.VolumeType.THIN \
                        if volume_map['SpaceAllocation'] == 'enabled' \
                        else constants.VolumeType.THICK
                    v = {
                        'name': volume_map['LUNName'],
                        'storage_id': storage_id,
                        'description': '',
                        'status': status,
                        'native_volume_id': volume_map['LUNUUID'],
                        'native_storage_pool_id': pool_id,
                        'wwn': '',
                        'compressed': '',
                        'deduplicated': '',
                        'type': type,
                        'total_capacity':
                            int(self.parse_string(volume_map['LUNSize'])),
                        'used_capacity':
                            int(self.parse_string(volume_map['UsedSize'])),
                        'free_capacity':
                            int(self.parse_string(volume_map['LUNSize'])) -
                            int(self.parse_string(volume_map['UsedSize']))
                    }
                    volume_list.append(v)
            return volume_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage volume from " \
                      "netapp_fas fas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage volume from " \
                      "netapp_fas fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_events(self, query_para):
        event_list = []
        event_info = self.exec_ssh_command(
            netapp_constants.EVENT_SHOW_DETAIL_COMMAND)
        event_arr = event_info.split(netapp_constants.ALTER_SPLIT_STR)
        event_map = {}
        for event_str in event_arr[1:]:
            self.handle_detail(event_str, event_map, split=':')
            occur_time = int(time.mktime(time.strptime(
                event_map['Time'],
                netapp_constants.EVENT_TIME_TYPE)))
            if query_para is None or \
                    (query_para['begin_time']
                     <= occur_time
                     <= query_para['end_time']):
                alert_model = {
                    'alert_id': event_map['Sequence#'],
                    'alert_name': event_map['MessageName'],
                    'severity': constants.Severity.CRITICAL,
                    'category': constants.Category.EVENT,
                    'type': constants.EventType.EQUIPMENT_ALARM,
                    'occur_time': occur_time,
                    'description': event_map['Event'],
                    'sequence_number': hashlib.md5(
                        (event_map['Sequence#'] +
                         str(occur_time)).encode()).hexdigest(),
                    'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                    'location': event_map['Source']
                }
                event_list.append(alert_model)
        return event_list

    def get_alerts(self, query_para):
        alert_list = []
        ALERT_SEVERITY_MAP = {
            'Unknown': constants.Severity.NOT_SPECIFIED,
            'Other': constants.Severity.NOT_SPECIFIED,
            'Information': constants.Severity.INFORMATIONAL,
            'Degraded': constants.Severity.WARNING,
            'Minor': constants.Severity.MINOR,
            'Major': constants.Severity.MAJOR,
            'Critical': constants.Severity.CRITICAL,
            'Fatal': constants.Severity.FATAL,
        }
        alert_info = self.exec_ssh_command(
            netapp_constants.ALTER_SHOW_DETAIL_COMMAND)
        alert_arr = alert_info.split(netapp_constants.ALTER_SPLIT_STR)
        alert_map = {}
        for alert_str in alert_arr[1:]:
            self.handle_detail(alert_str, alert_map, split=':')
            occur_time = int(time.mktime(time.strptime(
                alert_map['IndicationTime'],
                netapp_constants.ALTER_TIME_TYPE)))
            if query_para is None or \
                    (query_para['begin_time']
                     <= occur_time
                     <= query_para['end_time']):
                alert_model = {
                    'alert_id': alert_map['AlertID'],
                    'alert_name': alert_map['ProbableCause'],
                    'severity':
                        ALERT_SEVERITY_MAP[alert_map['PerceivedSeverity']],
                    'category': constants.Category.FAULT,
                    'type': constants.EventType.EQUIPMENT_ALARM,
                    'occur_time': occur_time,
                    'description': alert_map['Description'],
                    'sequence_number': hashlib.md5(
                        (alert_map['AlertID'] +
                         str(occur_time)).encode()).hexdigest(),
                    'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                    'location': alert_map['AlertingResourceName']
                }
                alert_list.append(alert_model)
        return alert_list

    def list_alerts(self, query_para):
        try:
            alert_list = []
            """Query the two alarms separately"""
            alert_list += self.get_events(query_para)
            alert_list += self.get_alerts(query_para)
            return alert_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage alert: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage alert: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def clear_alert(self, alert):
        try:
            ssh_command = \
                netapp_constants.CLEAR_ALERT_COMMAND + alert['alert_id']
            self.exec_ssh_command(ssh_command)
        except exception.DelfinException as e:
            err_msg = "Failed to get storage alert from " \
                      "netapp_fas fas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage alert from " \
                      "netapp_fas fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_disks(self, storage_id):
        TYPE_MAP = {
            'ATA': constants.DiskPhysicalType.SATA,
            'BSAS': constants.DiskPhysicalType,
            'FCAL': constants.DiskPhysicalType,
            'FSAS': constants.DiskPhysicalType,
            'LUN ': constants.DiskPhysicalType,
            'SAS': constants.DiskPhysicalType.SAS,
            'MSATA': constants.DiskPhysicalType,
            'SSD': constants.DiskPhysicalType.SSD,
            'VMDISK': constants.DiskPhysicalType,
            'unknown': constants.DiskPhysicalType.UNKNOWN,
        }
        LOGICAL_MAP = {
            'aggregate': constants.DiskLogicalType.MEMBER,
            'spare': constants.DiskLogicalType.HOTSPARE,
            'unknown': constants.DiskLogicalType.UNKNOWN,
            'free': constants.DiskLogicalType.FREE,
            'broken': constants.DiskLogicalType,
            'foreign': constants.DiskLogicalType,
            'labelmaint': constants.DiskLogicalType,
            'maintenance': constants.DiskLogicalType,
            'shared': constants.DiskLogicalType,
            'unassigned': constants.DiskLogicalType,
            'unsupported': constants.DiskLogicalType,
            'remote': constants.DiskLogicalType,
            'mediator': constants.DiskLogicalType,
        }
        disks_list = []
        physicals_list = []
        disks_info = self.exec_ssh_command(
            netapp_constants.DISK_SHOW_DETAIL_COMMAND)
        disks_arr = disks_info.split(
            netapp_constants.DISK_SPLIT_STR)
        physicals_info = self.exec_ssh_command(
            netapp_constants.DISK_SHOW_PHYSICAL_COMMAND)
        disks_map = {}
        physical_arr = physicals_info.split('\r\n')
        speed = physical_type = firmware = '-'
        for i in range(2, len(physical_arr), 2):
            physicals_list.append(physical_arr[i].split())
        for disk_str in disks_arr[1:]:
            self.handle_detail(disk_str, disks_map, split=':')
            logical_type = LOGICAL_MAP.get(disks_map['ContainerType'])
            """Map disk physical information"""
            for physical_info in physicals_list:
                if len(physical_info) > 6:
                    if physical_info[0] == disks_map['k']:
                        physical_type = TYPE_MAP.get(physical_info[1])
                        speed = physical_info[5]
                        firmware = physical_info[4]
            status = constants.DiskStatus.ABNORMAL
            if disks_map['Errors:'] is None or disks_map['Errors:'] == "":
                status = constants.DiskStatus.NORMAL
            d = {
                'name': disks_map['k'],
                'storage_id': storage_id,
                'native_disk_id': disks_map['k'],
                'serial_number': disks_map['SerialNumber'],
                'manufacturer': disks_map['Vendor'],
                'model': disks_map['Model'],
                'firmware': firmware,
                'speed': speed,
                'capacity':
                    int(self.parse_string(disks_map['PhysicalSize'])),
                'status': status,
                'physical_type': physical_type,
                'logical_type': logical_type,
                'health_score': '',
                'native_disk_group_id': disks_map['Aggregate'],
                'location': '',
            }
            disks_list.append(d)
        return disks_list

    def get_filesystems(self, storage_id):
        STATUS_MAP = {
            'online': constants.FilesystemStatus.NORMAL,
            'restricted': constants.FilesystemStatus.FAULTY,
            'offline': constants.FilesystemStatus.NORMAL,
            'force-online': constants.FilesystemStatus.FAULTY,
            'force-offline': constants.FilesystemStatus.FAULTY,
        }
        fs_list = []
        fs_info = self.exec_ssh_command(
            netapp_constants.FS_SHOW_DETAIL_COMMAND)
        fs_arr = fs_info.split(
            netapp_constants.FS_SPLIT_STR)
        thin_fs_info = self.exec_ssh_command(
            netapp_constants.THIN_FS_SHOW_COMMAND)
        pool_list = self.list_storage_pools(storage_id)
        thin_fs_arr = thin_fs_info.split("\r\n")
        type = constants.FSType.THICK
        fs_map = {}
        for fs_str in fs_arr[1:]:
            self.handle_detail(fs_str, fs_map, split=':')
            if fs_map is not None or fs_map != {}:
                pool_id = ""
                """get pool id"""
                for pool in pool_list:
                    if pool['name'] == fs_map['AggregateName']:
                        pool_id = pool['native_storage_pool_id']
                deduplicated = True
                if fs_map['SpaceSavedbyDeduplication'] == '0B':
                    deduplicated = False
                if len(thin_fs_arr) > 2:
                    for thin_vol in thin_fs_arr[2:]:
                        thin_arr = thin_vol.split()
                        if len(thin_arr) > 4:
                            if thin_arr[1] == fs_map['VolumeName']:
                                type = constants.VolumeType.THIN
                compressed = True
                if fs_map['VolumeContainsSharedorCompressedData'] == \
                        'false':
                    compressed = False
                status = STATUS_MAP.get(fs_map['VolumeState'])
                f = {
                    'name': fs_map['VolumeName'],
                    'storage_id': storage_id,
                    'native_filesystem_id': fs_map['VolumeName'],
                    'native_pool_id': pool_id,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                    'worm': fs_map['SnapLockType'],
                    'status': status,
                    'type': type,
                    'total_capacity':
                        int(self.parse_string(fs_map['VolumeSize'])),
                    'used_capacity':
                        int(self.parse_string(fs_map['UsedSize'])),
                    'free_capacity':
                        int(self.parse_string(fs_map['VolumeSize'])) -
                        int(self.parse_string(fs_map['UsedSize']))
                }
                fs_list.append(f)
        return fs_list
