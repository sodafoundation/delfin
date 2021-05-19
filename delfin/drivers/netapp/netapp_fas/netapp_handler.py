# Copyright 2021 The SODA Authors.
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
#    WarrayANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import time
import six
from oslo_log import log as logging
from oslo_utils import units
from delfin.drivers.netapp.netapp_fas import netapp_constants
from delfin import exception
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
            alert_array = alert_info.split(":")
            if len(alert_array) > 1:
                alert_name = alert_array[0]
                description = alert_array[1]
                if netapp_constants.SEVERITY_MAP.get(alert_name):
                    alert_model = {
                        'alert_id': alert_name,
                        'alert_name': alert_name,
                        'severity': constants.Severity.CRITICAL,
                        'category': constants.Category.EVENT,
                        'type': constants.EventType.EQUIPMENT_ALARM,
                        'occur_time': int(time.time()),
                        'description': description,
                        'match_key': hashlib.md5(
                            (alert.get(NetAppHandler.OID_TRAP_DATA)
                             + str(time.time())).encode()).hexdigest(),
                        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                        'location': ''
                    }
                    return alert_model
                else:
                    err_msg = "netapp fas TRAP only supports " \
                              "emergency level alerts"
                    LOG.error(err_msg)
                    raise NotImplementedError(err_msg)
        except exception.DelfinException as e:
            err_msg = "Failed to parse alert from " \
                      "netapp fas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to parse alert from " \
                      "netapp fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def login(self):
        try:
            self.ssh_pool.do_exec('version')
        except Exception as e:
            LOG.error("Failed to login netapp %s" %
                      (six.text_type(e)))
            raise e

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
        detail_arrayay = system_info.split('\r\n')
        for detail in detail_arrayay:
            if detail is not None and detail != '':
                strinfo = detail.split(split + " ")
                key = strinfo[0].replace(' ', '')
                value = ''
                if len(strinfo) > 1:
                    value = strinfo[1]
                storage_map[key] = value

    def get_storage(self):
        try:
            raw_capacity = total_capacity = used_capacity = free_capacity = 0
            system_info = self.ssh_pool.do_exec(
                netapp_constants.CLUSTER_SHOW_COMMAND)
            version = self.ssh_pool.do_exec(
                netapp_constants.VERSION_SHOW_COMMAND)
            status_info = self.ssh_pool.do_exec(
                netapp_constants.STORAGE_STATUS_COMMAND)
            version_arrayay = version.split('\r\n')
            status = netapp_constants.STORAGE_STATUS.get(
                status_info.split("\r\n")[2])
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

            storage_model = {
                "name": storage_map['ClusterName'],
                "vendor": netapp_constants.STORAGE_VENDOR,
                "model": '',
                "status": status,
                "serial_number": storage_map['ClusterSerialNumber'],
                "firmware_version": version_arrayay[0],
                "location": '',
                "total_capacity": total_capacity,
                "raw_capacity": raw_capacity,
                "used_capacity": used_capacity,
                "free_capacity": free_capacity
            }
            return storage_model
        except exception.DelfinException as e:
            err_msg = "Failed to get storage from " \
                      "netapp fas: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage from " \
                      "netapp fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_aggregate(self, storage_id):
        agg_list = []
        agg_info = self.ssh_pool.do_exec(
            netapp_constants.AGGREGATE_SHOW_DETAIL_COMMAND)
        agg_arrayay = agg_info.split(
            netapp_constants.AGGREGATE_SPLIT_STR)
        agg_map = {}
        for agg in agg_arrayay[1:]:
            self.handle_detail(agg, agg_map, split=':')
            status = netapp_constants.AGGREGATE_STATUS.get(agg_map['State'])
            pool_model = {
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
            agg_list.append(pool_model)
        return agg_list

    def get_pool(self, storage_id):
        pool_list = []
        pool_info = self.ssh_pool.do_exec(
            netapp_constants.POOLS_SHOW_DETAIL_COMMAND)
        pool_arrayay = pool_info.split(netapp_constants.POOLS_SPLIT_STR)
        pool_map = {}
        for pool_str in pool_arrayay[1:]:
            self.handle_detail(pool_str, pool_map, split=':')
            status = constants.StoragePoolStatus.ABNORMAL
            if pool_map['IsPoolHealthy?'] == 'true':
                status = constants.StoragePoolStatus.NORMAL
            pool_model = {
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
            pool_list.append(pool_model)
        return pool_list

    def list_storage_pools(self, storage_id):
        try:
            pool_list = self.get_pool(storage_id)
            agg_list = self.get_aggregate(storage_id)
            return agg_list + pool_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage pool from " \
                      "netapp fas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage pool from " \
                      "netapp fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_volumes(self, storage_id):
        try:
            volume_list = []
            volume_info = self.ssh_pool.do_exec(
                netapp_constants.LUN_SHOW_DETAIL_COMMAND)
            volume_arrayay = volume_info.split(netapp_constants.LUN_SPLIT_STR)
            fs_list = self.get_filesystems(storage_id)
            volume_map = {}
            for volume_str in volume_arrayay[1:]:
                self.handle_detail(volume_str, volume_map, split=':')
                if volume_map is not None or volume_map != {}:
                    pool_id = ''
                    status = netapp_constants.VOLUME_STATUS.get(
                        volume_map['State'])
                    for fs in fs_list:
                        if fs['name'] == volume_map['VolumeName']:
                            pool_id = fs['native_pool_id']
                    type = constants.VolumeType.THIN \
                        if volume_map['SpaceAllocation'] == 'enabled' \
                        else constants.VolumeType.THICK
                    volume_model = {
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
                    volume_list.append(volume_model)
            return volume_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage volume from " \
                      "netapp fas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage volume from " \
                      "netapp fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_events(self, query_para):
        event_list = []
        event_info = self.ssh_pool.do_exec(
            netapp_constants.EVENT_SHOW_DETAIL_COMMAND)
        event_arrayay = event_info.split(netapp_constants.ALTER_SPLIT_STR)
        event_map = {}
        for event_str in event_arrayay[1:]:
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
                    'match_key': hashlib.md5(
                        (event_map['Sequence#'] +
                         str(occur_time)).encode()).hexdigest(),
                    'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                    'location': event_map['Source']
                }
                event_list.append(alert_model)
        return event_list

    def get_alerts(self, query_para):
        alert_list = []
        alert_info = self.ssh_pool.do_exec(
            netapp_constants.ALTER_SHOW_DETAIL_COMMAND)
        alert_arrayay = alert_info.split(netapp_constants.ALTER_SPLIT_STR)
        alert_map = {}
        for alert_str in alert_arrayay[1:]:
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
                    'severity': netapp_constants.ALERT_SEVERITY
                    [alert_map['PerceivedSeverity']],
                    'category': constants.Category.FAULT,
                    'type': constants.EventType.EQUIPMENT_ALARM,
                    'occur_time': occur_time,
                    'description': alert_map['Description'],
                    'match_key': hashlib.md5(
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
            self.ssh_pool.do_exec(ssh_command)
        except exception.DelfinException as e:
            err_msg = "Failed to get storage alert from " \
                      "netapp fas: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage alert from " \
                      "netapp fas: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_disks(self, storage_id):
        disks_list = []
        physicals_list = []
        disks_info = self.ssh_pool.do_exec(
            netapp_constants.DISK_SHOW_DETAIL_COMMAND)
        disks_array = disks_info.split(
            netapp_constants.DISK_SPLIT_STR)
        physicals_info = self.ssh_pool.do_exec(
            netapp_constants.DISK_SHOW_PHYSICAL_COMMAND)
        disks_map = {}
        physical_array = physicals_info.split('\r\n')
        speed = physical_type = firmware = '-'
        for i in range(2, len(physical_array), 2):
            physicals_list.append(physical_array[i].split())
        for disk_str in disks_array[1:]:
            self.handle_detail(disk_str, disks_map, split=':')
            logical_type = netapp_constants.DISK_LOGICAL. \
                get(disks_map['ContainerType'])
            """Map disk physical information"""
            for physical_info in physicals_list:
                if len(physical_info) > 6:
                    if physical_info[0] == disks_map['k']:
                        physical_type = \
                            netapp_constants.DISK_TYPE.get(physical_info[1])
                        speed = physical_info[5]
                        firmware = physical_info[4]
            status = constants.DiskStatus.ABNORMAL
            if disks_map['Errors:'] is None or disks_map['Errors:'] == "":
                status = constants.DiskStatus.NORMAL
            disk_model = {
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
            disks_list.append(disk_model)
        return disks_list

    def get_filesystems(self, storage_id):
        fs_list = []
        fs_info = self.ssh_pool.do_exec(
            netapp_constants.FS_SHOW_DETAIL_COMMAND)
        fs_array = fs_info.split(
            netapp_constants.FS_SPLIT_STR)
        thin_fs_info = self.ssh_pool.do_exec(
            netapp_constants.THIN_FS_SHOW_COMMAND)
        pool_list = self.list_storage_pools(storage_id)
        thin_fs_array = thin_fs_info.split("\r\n")
        type = constants.FSType.THICK
        fs_map = {}
        for fs_str in fs_array[1:]:
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
                if len(thin_fs_array) > 2:
                    for thin_vol in thin_fs_array[2:]:
                        thin_array = thin_vol.split()
                        if len(thin_array) > 4:
                            if thin_array[1] == fs_map['VolumeName']:
                                type = constants.VolumeType.THIN
                compressed = True
                if fs_map['VolumeContainsSharedorCompressedData'] == \
                        'false':
                    compressed = False
                status = netapp_constants.FS_STATUS.get(fs_map['VolumeState'])
                fs_model = {
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
                fs_list.append(fs_model)
        return fs_list
