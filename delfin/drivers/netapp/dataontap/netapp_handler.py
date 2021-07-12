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
import re
import time
import six
import hashlib
import eventlet

from oslo_log import log as logging
from oslo_utils import units

from delfin.drivers.netapp.dataontap import constants as constant
from delfin import exception, utils
from delfin.common import constants
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools

LOG = logging.getLogger(__name__)


class NetAppHandler(object):
    OID_SERIAL_NUM = '1.3.6.1.4.1.789.1.1.9.0'
    OID_TRAP_DATA = '1.3.6.1.4.1.789.1.1.12.0'
    SECONDS_TO_MS = 1000

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    @staticmethod
    def get_table_data(values):
        pattern = re.compile('^[-]{3,}')
        header_index = 0
        table = values.split("\r\n")
        for i in range(0, len(table)):
            if pattern.search(table[i]) is not None:
                header_index = i
        return table[(header_index + 1):]

    @staticmethod
    def get_fs_id(vserver, volume):
        return vserver + '_' + volume

    @staticmethod
    def get_qt_id(vserver, volume, qtree):
        qt_id = vserver + '/' + volume
        if qtree != '':
            qt_id += '/' + qtree
        return qt_id

    def ssh_do_exec(self, command):
        res = ''
        with eventlet.Timeout(10, False):
            res = self.ssh_pool.do_exec(command)
        return res

    @staticmethod
    def get_size(limit, is_calculate=False):
        if limit == '0B':
            return 0
        if limit == '-':
            return 0 if is_calculate else '-'
        return int(Tools.get_capacity_size(limit))

    @staticmethod
    def parse_alert(alert):
        try:
            alert_info = alert.get(NetAppHandler.OID_TRAP_DATA)
            alert_array = alert_info.split(":")
            alert_model = {}
            if len(alert_array) > 1:
                alert_name = alert_array[0]
                description = alert_array[1]
                if constant.SEVERITY_MAP.get(alert_name):
                    alert_model = {
                        'alert_id': alert_name,
                        'alert_name': alert_name,
                        'severity': constants.Severity.CRITICAL,
                        'category': constants.Category.FAULT,
                        'type': constants.EventType.EQUIPMENT_ALARM,
                        'occur_time': utils.utcnow_ms(),
                        'description': description,
                        'match_key': hashlib.md5(
                            (alert.get(NetAppHandler.OID_TRAP_DATA)
                             + str(utils.utcnow_ms())).encode()).hexdigest(),
                        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                        'location': None
                    }
            return alert_model
        except Exception as err:
            err_msg = "Failed to parse alert from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def login(self):
        try:
            result = self.ssh_do_exec('version')
            if 'is not a recognized command' in result:
                raise exception.InvalidIpOrPort()
        except Exception as e:
            LOG.error("Failed to login netapp %s" %
                      (six.text_type(e)))
            raise e

    def get_storage(self):
        try:
            raw_capacity = total_capacity = used_capacity = free_capacity = 0
            controller_map_list = []
            system_info = self.ssh_do_exec(
                constant.CLUSTER_SHOW_COMMAND)
            version_info = self.ssh_do_exec(
                constant.VERSION_SHOW_COMMAND)
            status_info = self.ssh_do_exec(
                constant.STORAGE_STATUS_COMMAND)
            controller_info = self.ssh_do_exec(
                constant.CONTROLLER_SHOW_DETAIL_COMMAND)
            Tools.split_value_map_list(
                controller_info, controller_map_list, ":")
            version_array = version_info.split("\r\n")
            version = version_array[len(version_array) - 1].split(":")
            status = self.get_table_data(status_info)
            status = constant.STORAGE_STATUS.get(status[0].split()[0])
            disk_list = self.get_disks(None)
            pool_list = self.list_storage_pools(None)
            storage_map_list = []
            Tools.split_value_map_list(
                system_info, storage_map_list, split=':')
            if len(storage_map_list) > 0:
                storage_map = storage_map_list[len(storage_map_list) - 1]
                controller_map = \
                    controller_map_list[len(controller_map_list) - 1]
                for disk in disk_list:
                    raw_capacity += disk['capacity']
                for pool in pool_list:
                    total_capacity += pool['total_capacity']
                    free_capacity += pool['free_capacity']
                    used_capacity += pool['used_capacity']
                storage_model = {
                    "name": storage_map['ClusterName'],
                    "vendor": constant.STORAGE_VENDOR,
                    "model": controller_map['Model'],
                    "status": status,
                    "serial_number": storage_map['ClusterSerialNumber'],
                    "firmware_version": version[0],
                    "location": controller_map['Location'],
                    "total_capacity": total_capacity,
                    "raw_capacity": raw_capacity,
                    "used_capacity": used_capacity,
                    "free_capacity": free_capacity
                }
                return storage_model
        except exception.DelfinException as e:
            err_msg = "Failed to get storage from " \
                      "netapp cmode: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_aggregate(self, storage_id):
        agg_list = []
        agg_info = self.ssh_do_exec(
            constant.AGGREGATE_SHOW_DETAIL_COMMAND)
        agg_map_list = []
        Tools.split_value_map_list(agg_info, agg_map_list, split=':')
        for agg_map in agg_map_list:
            if 'Aggregate' in agg_map.keys():
                status = constant.AGGREGATE_STATUS.get(agg_map['State'])
                pool_model = {
                    'name': agg_map['Aggregate'],
                    'storage_id': storage_id,
                    'native_storage_pool_id': agg_map['UUIDString'],
                    'description': None,
                    'status': status,
                    'storage_type': constants.StorageType.UNIFIED,
                    'total_capacity': self.get_size(agg_map['Size'], True),
                    'used_capacity': self.get_size(agg_map['UsedSize'], True),
                    'free_capacity':
                        self.get_size(agg_map['AvailableSize'], True),
                }
                agg_list.append(pool_model)
        return agg_list

    def get_pool(self, storage_id):
        pool_list = []
        pool_info = self.ssh_do_exec(
            constant.POOLS_SHOW_DETAIL_COMMAND)
        pool_map_list = []
        Tools.split_value_map_list(pool_info, pool_map_list, split=':')
        for pool_map in pool_map_list:
            if 'StoragePoolName' in pool_map.keys():
                status = constants.StoragePoolStatus.ABNORMAL
                if pool_map['IsPoolHealthy?'] == 'true':
                    status = constants.StoragePoolStatus.NORMAL
                pool_model = {
                    'name': pool_map['StoragePoolName'],
                    'storage_id': storage_id,
                    'native_storage_pool_id': pool_map['UUIDofStoragePool'],
                    'description': None,
                    'status': status,
                    'storage_type': constants.StorageType.UNIFIED,
                    'total_capacity':
                        self.get_size(pool_map['StoragePoolTotalSize'], True),
                    'used_capacity':
                        self.get_size(pool_map['StoragePoolTotalSize'], True) -
                        self.get_size(pool_map['StoragePoolUsableSize'], True),
                    'free_capacity':
                        self.get_size(pool_map['StoragePoolUsableSize'], True)
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
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage pool from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_volumes(self, storage_id):
        try:
            volume_list = []
            volume_info = self.ssh_do_exec(
                constant.LUN_SHOW_DETAIL_COMMAND)
            fs_list = self.get_filesystems(storage_id)
            volume_map_list = []
            Tools.split_value_map_list(volume_info, volume_map_list, split=':')
            for volume_map in volume_map_list:
                if volume_map is not None and volume_map != {} \
                        and 'LUNName' in volume_map.keys():
                    pool_id = None
                    status = 'normal' if volume_map['State'] == 'online' \
                        else 'offline'
                    for fs in fs_list:
                        if fs['name'] == volume_map['VolumeName']:
                            pool_id = fs['native_pool_id']
                    type = constants.VolumeType.THIN \
                        if volume_map['SpaceAllocation'] == 'enabled' \
                        else constants.VolumeType.THICK
                    volume_model = {
                        'name': volume_map['LUNName'],
                        'storage_id': storage_id,
                        'description': None,
                        'status': status,
                        'native_volume_id': volume_map['SerialNumber'],
                        'native_storage_pool_id': pool_id,
                        'wwn': None,
                        'compressed': None,
                        'deduplicated': None,
                        'type': type,
                        'total_capacity':
                            self.get_size(volume_map['LUNSize'], True),
                        'used_capacity':
                            self.get_size(volume_map['UsedSize'], True),
                        'free_capacity':
                            self.get_size(volume_map['LUNSize'], True) -
                            self.get_size(volume_map['UsedSize'], True)
                    }
                    volume_list.append(volume_model)
            return volume_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage volume from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage volume from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_alerts(self, query_para):
        alert_list = []
        alert_info = self.ssh_do_exec(
            constant.ALTER_SHOW_DETAIL_COMMAND)
        alert_map_list = []
        Tools.split_value_map_list(
            alert_info, alert_map_list, True, split=':')
        for alert_map in alert_map_list:
            if 'AlertID' in alert_map.keys():
                occur_time = int(time.mktime(time.strptime(
                    alert_map['IndicationTime'],
                    constant.ALTER_TIME_TYPE)))
                if query_para is None or query_para == {} or\
                        (int(query_para['begin_time'])
                         <= occur_time
                         <= int(query_para['end_time'])):
                    alert_model = {
                        'alert_id': alert_map['AlertID'],
                        'alert_name': alert_map['AlertID'],
                        'severity': constant.ALERT_SEVERITY
                        [alert_map['PerceivedSeverity']],
                        'category': constants.Category.FAULT,
                        'type': constants.EventType.EQUIPMENT_ALARM,
                        'occur_time': occur_time * 1000,
                        'description': alert_map['Description'],
                        'sequence_number': alert_map['AlertID'],
                        'match_key': hashlib.md5(
                            (alert_map['AlertID'] +
                             str(occur_time)).encode()).hexdigest(),
                        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                        'location':
                            alert_map['ProbableCause'] +
                            ':' + alert_map['PossibleEffect']
                    }
                    alert_list.append(alert_model)
        return alert_list

    def list_alerts(self, query_para):
        try:
            """Query the two alarms separately"""
            alert_list = self.get_alerts(query_para)
            return alert_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage alert from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage alert from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def clear_alert(self, alert):
        try:
            ssh_command = \
                constant.CLEAR_ALERT_COMMAND + alert['alert_id']
            self.ssh_do_exec(ssh_command)
        except exception.DelfinException as e:
            err_msg = "Failed to get storage alert from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage alert from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_disks(self, storage_id):
        disks_list = []
        physicals_list = []
        disks_info = self.ssh_do_exec(
            constant.DISK_SHOW_DETAIL_COMMAND)
        physicals_info = self.ssh_do_exec(
            constant.DISK_SHOW_PHYSICAL_COMMAND)
        error_disk = self.ssh_do_exec(
            constant.DISK_ERROR_COMMAND
        )
        error_disk_list = []
        error_disk_array = self.get_table_data(error_disk)
        for error_disk in error_disk_array:
            error_array = error_disk.split()
            if len(error_array) > 2:
                error_disk_list.append(error_array[0])
        disks_map_list = []
        physical_array = self.get_table_data(physicals_info)
        for physical in physical_array:
            physicals_list.append(physical.split())
        Tools.split_value_map_list(disks_info, disks_map_list, split=':')
        for disks_map in disks_map_list:
            if 'Disk' in disks_map.keys():
                speed = physical_type = firmware = None
                logical_type = constant.DISK_LOGICAL. \
                    get(disks_map['ContainerType'])
                """Map disk physical information"""
                for physical_info in physicals_list:
                    if len(physical_info) > 6 and \
                            physical_info[0] == disks_map['Disk']:
                        physical_type = \
                            constant.DISK_TYPE.get(physical_info[1])
                        speed = physical_info[5] \
                            if physical_info[5] != '-' else 0
                        firmware = physical_info[4]
                status = constants.DiskStatus.NORMAL
                if disks_map['Disk'] in error_disk_list:
                    status = constants.DiskStatus.ABNORMAL
                disk_model = {
                    'name': disks_map['Disk'],
                    'storage_id': storage_id,
                    'native_disk_id': disks_map['Disk'],
                    'serial_number': disks_map['SerialNumber'],
                    'manufacturer': disks_map['Vendor'],
                    'model': disks_map['Model'],
                    'firmware': firmware,
                    'speed': speed,
                    'capacity': self.get_size(disks_map['PhysicalSize'], True),
                    'status': status,
                    'physical_type': physical_type,
                    'logical_type': logical_type,
                    'native_disk_group_id': disks_map['Aggregate'],
                    'location': None,
                }
                disks_list.append(disk_model)
        return disks_list

    def get_filesystems(self, storage_id):
        fs_list = []
        fs_info = self.ssh_do_exec(
            constant.FS_SHOW_DETAIL_COMMAND)
        thin_fs_info = self.ssh_do_exec(
            constant.THIN_FS_SHOW_COMMAND)
        pool_list = self.list_storage_pools(storage_id)
        thin_fs_array = self.get_table_data(thin_fs_info)
        fs_map_list = []
        Tools.split_value_map_list(fs_info, fs_map_list, split=':')
        for fs_map in fs_map_list:
            type = constants.FSType.THICK
            if fs_map is not None and fs_map != {} \
                    and 'VolumeName' in fs_map.keys():
                pool_id = ""
                """get pool id"""
                for pool in pool_list:
                    if pool['name'] == fs_map['AggregateName']:
                        pool_id = pool['native_storage_pool_id']
                deduplicated = True
                if fs_map['SpaceSavedbyDeduplication'] == '0B':
                    deduplicated = False
                if len(thin_fs_array) > 2:
                    for thin_vol in thin_fs_array:
                        thin_array = thin_vol.split()
                        if len(thin_array) > 4:
                            if thin_array[1] == fs_map['VolumeName']:
                                type = constants.VolumeType.THIN
                compressed = True
                if fs_map['VolumeContainsSharedorCompressedData'] == \
                        'false':
                    compressed = False
                status = constant.FS_STATUS.get(fs_map['VolumeState'])
                fs_id = self.get_fs_id(
                    fs_map['VserverName'], fs_map['VolumeName'])
                fs_model = {
                    'name': fs_map['VolumeName'],
                    'storage_id': storage_id,
                    'native_filesystem_id': fs_id,
                    'native_pool_id': pool_id,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                    'worm': constant.WORM_TYPE.get(fs_map['SnapLockType']),
                    'status': status,
                    'security_mode':
                        constant.SECURITY_STYLE.get(
                            fs_map['SecurityStyle'], fs_map['SecurityStyle']),
                    'type': type,
                    'total_capacity': self.get_size(fs_map['VolumeSize']),
                    'used_capacity':
                        self.get_size(fs_map['VolumeSize'], True) -
                        self.get_size(fs_map['AvailableSize'], True),
                    'free_capacity': self.get_size(fs_map['AvailableSize'])
                }
                if fs_model['total_capacity'] != '-' \
                        and fs_model['total_capacity'] > 0:
                    fs_list.append(fs_model)
        return fs_list

    def list_controllers(self, storage_id):
        try:
            controller_list = []
            controller_info = self.ssh_do_exec(
                constant.CONTROLLER_SHOW_DETAIL_COMMAND)
            controller_map_list = []
            Tools.split_value_map_list(
                controller_info, controller_map_list, split=':')
            for controller_map in controller_map_list:
                if controller_map is not None and controller_map != {} \
                        and 'Node' in controller_map.keys():
                    status = constants.ControllerStatus.NORMAL \
                        if controller_map['Health'] == 'true' \
                        else constants.ControllerStatus.OFFLINE
                    controller_model = {
                        'name': controller_map['Node'],
                        'storage_id': storage_id,
                        'native_controller_id': controller_map['SystemID'],
                        'status': status,
                        'location': controller_map['Location'],
                        'soft_version': None,
                        'cpu_info': None,
                        'memory_size': None,
                    }
                    controller_list.append(controller_model)
            return controller_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage controllers from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

        except Exception as err:
            err_msg = "Failed to get storage controllers from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_eth_port(self, storage_id):
        try:
            eth_list = []
            eth_info = self.ssh_do_exec(
                constant.PORT_SHOW_DETAIL_COMMAND)

            eth_map_list = []
            Tools.split_value_map_list(eth_info, eth_map_list, split=':')
            for eth_map in eth_map_list:
                if 'Port' in eth_map.keys():
                    logical_type = constant.ETH_LOGICAL_TYPE.get(
                        eth_map['PortType'])
                    port_id = \
                        eth_map['Node'] + '_' + eth_map['Port']
                    eth_model = {
                        'name': eth_map['Port'],
                        'storage_id': storage_id,
                        'native_port_id': port_id,
                        'location':
                            eth_map['Node'] +
                            ':' + eth_map['Port'],
                        'connection_status':
                            constants.PortConnectionStatus.CONNECTED
                            if eth_map['Link'] == 'up'
                            else constants.PortConnectionStatus.DISCONNECTED,
                        'health_status':
                            constants.PortHealthStatus.NORMAL
                            if eth_map['PortHealthStatus'] == 'healthy'
                            else constants.PortHealthStatus.ABNORMAL,
                        'type': constants.PortType.ETH,
                        'logical_type': logical_type,
                        'speed': int(eth_map['SpeedOperational']) * units.Mi
                        if eth_map['SpeedOperational'] != '-' else 0,
                        'max_speed':
                            int(eth_map['SpeedOperational']) * units.Mi
                        if eth_map['SpeedOperational'] != '-' else 0,
                        'native_parent_id': None,
                        'wwn': None,
                        'mac_address': eth_map['MACAddress'],
                        'ipv4': None,
                        'ipv4_mask': None,
                        'ipv6': None,
                        'ipv6_mask': None,
                    }
                    eth_list.append(eth_model)
            return eth_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage ports from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage ports from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_fc_port(self, storage_id):
        try:
            fc_list = []
            fc_info = self.ssh_do_exec(
                constant.FC_PORT_SHOW_DETAIL_COMMAND)
            fc_map_list = []
            Tools.split_value_map_list(fc_info, fc_map_list, split=':')
            for fc_map in fc_map_list:
                if 'Node' in fc_map.keys():
                    type = constant.FC_TYPE.get(fc_map['PhysicalProtocol'])
                    port_id = \
                        fc_map['Node'] + '_' + fc_map['Adapter']
                    fc_model = {
                        'name':
                            fc_map['Node'] +
                            ':' + fc_map['Adapter'],
                        'storage_id': storage_id,
                        'native_port_id': port_id,
                        'location':
                            fc_map['Node'] +
                            ':' + fc_map['Adapter'],
                        'connection_status':
                            constants.PortConnectionStatus.CONNECTED
                            if fc_map['AdministrativeStatus'] == 'up'
                            else constants.PortConnectionStatus.DISCONNECTED,
                        'health_status':
                            constants.PortHealthStatus.NORMAL
                            if fc_map['OperationalStatus'] == 'online'
                            else constants.PortHealthStatus.ABNORMAL,
                        'type': type,
                        'logical_type': None,
                        'speed': int(fc_map['DataLinkRate(Gbit)']) * units.Gi
                        if fc_map['DataLinkRate(Gbit)'] != '-' else 0,
                        'max_speed': int(fc_map['MaximumSpeed']) * units.Gi
                        if fc_map['MaximumSpeed'] != '-' else 0,
                        'native_parent_id': None,
                        'wwn': fc_map['AdapterWWNN'],
                        'mac_address': None,
                        'ipv4': None,
                        'ipv4_mask': None,
                        'ipv6': None,
                        'ipv6_mask': None,
                    }
                    fc_list.append(fc_model)
            return fc_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage ports from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

        except Exception as err:
            err_msg = "Failed to get storage ports from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_ports(self, storage_id):
        ports_list = \
            self.get_fc_port(storage_id) + \
            self.get_eth_port(storage_id)
        return ports_list

    def list_disks(self, storage_id):
        try:
            return self.get_disks(storage_id)
        except exception.DelfinException as e:
            err_msg = "Failed to get storage disks from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

        except Exception as err:
            err_msg = "Failed to get storage disks from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_qtrees(self, storage_id):
        try:
            qt_list = []
            qt_info = self.ssh_do_exec(
                constant.QTREE_SHOW_DETAIL_COMMAND)
            fs_info = self.ssh_do_exec(
                constant.FS_SHOW_DETAIL_COMMAND)
            fs_map_list = []
            qt_map_list = []
            Tools.split_value_map_list(fs_info, fs_map_list, split=':')
            Tools.split_value_map_list(qt_info, qt_map_list, split=':')
            for qt_map in qt_map_list:
                if 'QtreeName' in qt_map.keys():
                    fs_id = self.get_fs_id(qt_map['VserverName'],
                                           qt_map['VolumeName'])
                    qtree_path = None
                    for fs_map in fs_map_list:
                        if 'VserverName' in fs_map.keys() \
                                and fs_id == self.get_fs_id(
                                fs_map['VserverName'],
                                fs_map['VolumeName']) \
                                and fs_map['JunctionPath'] != '-':
                            qtree_path = fs_map['JunctionPath']
                            break
                    qt_id = self.get_qt_id(
                        qt_map['VserverName'],
                        qt_map['VolumeName'],
                        qt_map['QtreeName'])
                    qtree_name = qt_map['QtreeName']
                    if qt_map['QtreeName'] != '' and qtree_path is not None:
                        qtree_path += '/' + qt_map['QtreeName']
                    else:
                        qtree_name = qt_id
                    qt_model = {
                        'name': qtree_name,
                        'storage_id': storage_id,
                        'native_qtree_id': qt_id,
                        'path': qtree_path,
                        'native_filesystem_id': fs_id,
                        'security_mode': qt_map['SecurityStyle'],
                    }
                    qt_list.append(qt_model)
            return qt_list
        except exception.DelfinException as err:
            err_msg = "Failed to get storage qtrees from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get storage qtrees from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_nfs_shares(self, storage_id, qtree_list, protocol_map):
        try:
            nfs_info = self.ssh_do_exec(
                constant.NFS_SHARE_SHOW_COMMAND)
            nfs_list = []
            fs_map_list = []
            Tools.split_value_map_list(nfs_info, fs_map_list, split=':')
            for fs_map in fs_map_list:
                if 'VserverName' in fs_map.keys():
                    protocol = protocol_map.get(fs_map['VserverName'])
                    if constants.ShareProtocol.NFS in protocol:
                        fs_id = self.get_fs_id(fs_map['VserverName'],
                                               fs_map['VolumeName'])
                        share_name = \
                            fs_map['VserverName'] + '/' + fs_map['VolumeName']
                        qt_id = self.get_qt_id(fs_map['VserverName'],
                                               fs_map['VolumeName'], '')
                        qtree_id = None
                        for qtree in qtree_list:
                            if qtree['native_qtree_id'] == qt_id:
                                qtree_id = qt_id
                            if fs_id == qtree['native_filesystem_id']\
                                    and qtree['name'] != ""\
                                    and qtree['name'] != \
                                    qtree['native_qtree_id']:
                                qt_share_name = \
                                    share_name + '/' + qtree['name']
                                share = {
                                    'name': qt_share_name,
                                    'storage_id': storage_id,
                                    'native_share_id':
                                        qt_share_name + '_' +
                                        constants.ShareProtocol.NFS,
                                    'native_qtree_id':
                                        qtree['native_qtree_id'],
                                    'native_filesystem_id':
                                        qtree['native_filesystem_id'],
                                    'path': qtree['path'],
                                    'protocol': constants.ShareProtocol.NFS
                                }
                                nfs_list.append(share)
                        share = {
                            'name': share_name,
                            'storage_id': storage_id,
                            'native_share_id':
                                share_name + '_' + constants.ShareProtocol.NFS,
                            'native_qtree_id': qtree_id,
                            'native_filesystem_id': fs_id,
                            'path': fs_map['JunctionPath'],
                            'protocol': constants.ShareProtocol.NFS
                        }
                        nfs_list.append(share)
            return nfs_list
        except exception.DelfinException as err:
            err_msg = "Failed to get storage nfs share from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise err
        except Exception as err:
            err_msg = "Failed to get storage nfs share from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_cifs_shares(self, storage_id, vserver_name,
                        qtree_list, protocol_map):
        shares_list = []
        share_info = self.ssh_do_exec(
            (constant.CIFS_SHARE_SHOW_DETAIL_COMMAND %
             {'vserver_name': vserver_name}))
        share_map_list = []
        Tools.split_value_map_list(share_info, share_map_list, split=':')
        for share_map in share_map_list:
            if 'VolumeName' in share_map.keys() and \
                    share_map['VolumeName'] != '-':
                protocol_str = protocol_map.get(
                    share_map['Vserver'])
                fs_id = self.get_fs_id(share_map['Vserver'],
                                       share_map['VolumeName'])
                share_id = fs_id + '_' + share_map['Share'] + '_'
                qtree_id = None
                for qtree in qtree_list:
                    name_array = share_map['Path'].split('/')
                    if len(name_array) > 0:
                        qtree_name = name_array[len(name_array) - 1]
                        if qtree_name == share_map['VolumeName']:
                            qtree_name = ''
                        qt_id = self.get_qt_id(
                            share_map['Vserver'],
                            share_map['VolumeName'], qtree_name)
                    else:
                        break
                    if qtree['native_qtree_id'] == qt_id:
                        qtree_id = qt_id
                        break
                if constants.ShareProtocol.CIFS in protocol_str:
                    share = {
                        'name': share_map['Share'],
                        'storage_id': storage_id,
                        'native_share_id':
                            share_id + constants.ShareProtocol.CIFS,
                        'native_qtree_id': qtree_id,
                        'native_filesystem_id': fs_id,
                        'path': share_map['Path'],
                        'protocol': constants.ShareProtocol.CIFS
                    }
                    shares_list.append(share)
        return shares_list

    def list_shares(self, storage_id):
        try:
            shares_list = []
            qtree_list = self.list_qtrees(None)
            protocol_info = self.ssh_do_exec(
                constant.SHARE_AGREEMENT_SHOW_COMMAND)
            protocol_map = {}
            protocol_arr = self.get_table_data(protocol_info)
            for protocol in protocol_arr:
                agr_arr = protocol.split()
                if len(agr_arr) > 1:
                    protocol_map[agr_arr[0]] = agr_arr[1]
            vserver_info = self.ssh_do_exec(
                constant.VSERVER_SHOW_COMMAND)
            vserver_array = self.get_table_data(vserver_info)
            for vserver in vserver_array:
                vserver_name = vserver.split()
                if len(vserver_name) > 1:
                    shares_list += self.get_cifs_shares(
                        storage_id, vserver_name[0], qtree_list, protocol_map)
            shares_list += self.get_nfs_shares(
                storage_id, qtree_list, protocol_map)
            return shares_list
        except exception.DelfinException as err:
            err_msg = "Failed to get storage shares from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get storage shares from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_filesystems(self, storage_id):
        try:
            fs_list = self.get_filesystems(storage_id)
            return fs_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage volume from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage volume from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_quotas(self, storage_id):
        try:
            quota_list = []
            quotas_info = self.ssh_do_exec(
                constant.QUOTA_SHOW_DETAIL_COMMAND)
            quota_map_list = []
            Tools.split_value_map_list(quotas_info, quota_map_list, ":")
            for quota_map in quota_map_list:
                user_group_name = None
                if 'VolumeName' in quota_map.keys():
                    quota_id = \
                        quota_map['Vserver'] + '_' + \
                        quota_map['VolumeName'] + '_' + \
                        quota_map['Type'] + '_' + \
                        quota_map['QtreeName'] + '_' + \
                        quota_map['Target']
                    type = constant.QUOTA_TYPE.get(quota_map['Type'])
                    qt_id = self.get_qt_id(
                        quota_map['Vserver'],
                        quota_map['VolumeName'], '')
                    if type == 'tree' and quota_map['Target'] != '':
                        qt_id += '/' + quota_map['Target']
                    else:
                        if type == 'user' or 'group':
                            user_group_name = quota_map['Target']
                        if quota_map['QtreeName'] != '':
                            qt_id += '/' + quota_map['QtreeName']
                    fs_id = self.get_fs_id(quota_map['Vserver'],
                                           quota_map['VolumeName'])
                    quota = {
                        'native_quota_id': quota_id,
                        'type': type,
                        'storage_id': storage_id,
                        'native_filesystem_id': fs_id,
                        'native_qtree_id': qt_id,
                        'capacity_hard_limit':
                            self.get_size(quota_map['DiskLimit']),
                        'capacity_soft_limit':
                            self.get_size(quota_map['SoftDiskLimit']),
                        'file_hard_limit':
                            int(quota_map['FilesLimit'])
                            if quota_map['FilesLimit'] != '-' else '-',
                        'file_soft_limit':
                            int(quota_map['SoftFilesLimit'])
                            if quota_map['SoftFilesLimit'] != '-' else '-',
                        'file_count': None,
                        'used_capacity': None,
                        'user_group_name': user_group_name
                    }
                    quota_list.append(quota)
            return quota_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage volume from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage volume from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_alert_sources(self):
        try:
            ip_list = []
            mgt_ip = self.ssh_pool.do_exec(constant.MGT_IP_COMMAND)
            node_ip = self.ssh_pool.do_exec(constant.NODE_IP_COMMAND)
            mgt_ip_array = self.get_table_data(mgt_ip)
            node_ip_array = self.get_table_data(node_ip)
            for node in node_ip_array:
                ip_array = node.split()
                if len(ip_array) == 3:
                    ip_list.append({'host': ip_array[2]})
            ip_list.append({'host': mgt_ip_array[0].split()[2]})
            return ip_list
        except exception.DelfinException as e:
            err_msg = "Failed to get storage ip from " \
                      "netapp cmode: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage ip from " \
                      "netapp cmode: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
