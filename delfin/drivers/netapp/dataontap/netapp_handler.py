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
    def get_size(limit):
        if limit == '-':
            return '-'
        elif limit == '0B':
            return 0
        else:
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
            controller_map = {}
            system_info = self.ssh_do_exec(
                constant.CLUSTER_SHOW_COMMAND)
            version_info = self.ssh_do_exec(
                constant.VERSION_SHOW_COMMAND)
            status_info = self.ssh_do_exec(
                constant.STORAGE_STATUS_COMMAND)
            controller_info = self.ssh_do_exec(
                constant.CONTROLLER_SHOW_DETAIL_COMMAND)
            controller_array = controller_info.split(
                constant.CONTROLLER_SPLIT_STR)
            Tools.split_value_map(controller_array[1], controller_map, ":")
            version_array = version_info.split('\r\n')
            version = version_array[0].split(":")
            status = constant.STORAGE_STATUS.get(
                status_info.split("\r\n")[2])
            disk_list = self.get_disks(None)
            pool_list = self.list_storage_pools(None)
            storage_map = {}
            Tools.split_value_map(system_info, storage_map, split=':')
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
        agg_array = agg_info.split(
            constant.AGGREGATE_SPLIT_STR)
        agg_map = {}
        for agg in agg_array[1:]:
            Tools.split_value_map(agg, agg_map, split=':')
            status = constant.AGGREGATE_STATUS.get(agg_map['State'])
            pool_model = {
                'name': agg_map[constant.AGGREGATE_NAME],
                'storage_id': storage_id,
                'native_storage_pool_id': agg_map['UUIDString'],
                'description': None,
                'status': status,
                'storage_type': constants.StorageType.UNIFIED,
                'total_capacity':
                    int(Tools.get_capacity_size(agg_map['Size'])),
                'used_capacity':
                    int(Tools.get_capacity_size(agg_map['UsedSize'])),
                'free_capacity':
                    int(Tools.get_capacity_size(agg_map['AvailableSize'])),
            }
            agg_list.append(pool_model)
        return agg_list

    def get_pool(self, storage_id):
        pool_list = []
        pool_info = self.ssh_do_exec(
            constant.POOLS_SHOW_DETAIL_COMMAND)
        pool_array = pool_info.split(constant.POOLS_SPLIT_STR)
        pool_map = {}
        for pool_str in pool_array[1:]:
            Tools.split_value_map(pool_str, pool_map, split=':')
            status = constants.StoragePoolStatus.ABNORMAL
            if pool_map['IsPoolHealthy?'] == 'true':
                status = constants.StoragePoolStatus.NORMAL
            pool_model = {
                'name': pool_map[constant.POOL_NAME],
                'storage_id': storage_id,
                'native_storage_pool_id': pool_map['UUIDofStoragePool'],
                'description': None,
                'status': status,
                'storage_type': constants.StorageType.UNIFIED,
                'total_capacity':
                    int(Tools.get_capacity_size(
                        pool_map['StoragePoolTotalSize'])),
                'used_capacity':
                    int(Tools.get_capacity_size(
                        pool_map['StoragePoolTotalSize'])) -
                    int(Tools.get_capacity_size(
                        pool_map['StoragePoolUsableSize'])),
                'free_capacity':
                    int(Tools.get_capacity_size(
                        pool_map['StoragePoolUsableSize']))
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
            volume_array = volume_info.split(constant.LUN_SPLIT_STR)
            fs_list = self.get_filesystems(storage_id)
            volume_map = {}
            for volume_str in volume_array[1:]:
                Tools.split_value_map(volume_str, volume_map, split=':')
                if volume_map is not None or volume_map != {}:
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
                            int(Tools.get_capacity_size(
                                volume_map['LUNSize'])),
                        'used_capacity':
                            int(Tools.get_capacity_size(
                                volume_map['UsedSize'])),
                        'free_capacity':
                            int(Tools.get_capacity_size(
                                volume_map['LUNSize'])) -
                            int(Tools.get_capacity_size(
                                volume_map['UsedSize']))
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

    def get_events(self, query_para):
        event_list = []
        event_info = self.ssh_do_exec(
            constant.EVENT_SHOW_DETAIL_COMMAND)
        event_array = event_info.split(constant.ALTER_SPLIT_STR)
        event_map = {}
        for event_str in event_array[1:]:
            Tools.split_value_map(event_str, event_map, split=':')
            occur_time = int(time.mktime(time.strptime(
                event_map['Time'],
                constant.EVENT_TIME_TYPE)))
            if query_para is None or \
                    (int(query_para['begin_time'])
                     <= occur_time
                     <= int(query_para['end_time'])):
                alert_model = {
                    'alert_id': event_map['Sequence#'],
                    'alert_name': event_map['MessageName'],
                    'severity': constants.Severity.CRITICAL,
                    'category': constants.Category.FAULT,
                    'type': constants.EventType.EQUIPMENT_ALARM,
                    'occur_time': occur_time * 1000,
                    'description': event_map['Event'],
                    'match_key': hashlib.md5(
                        (event_map['Sequence#'] +
                         str(occur_time)).encode()).hexdigest(),
                    'sequence_number': event_map['Sequence#'],
                    'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                    'location': event_map['Source']
                }
                event_list.append(alert_model)
        return event_list

    def get_alerts(self, query_para):
        alert_list = []
        alert_info = self.ssh_do_exec(
            constant.ALTER_SHOW_DETAIL_COMMAND)
        alert_array = alert_info.split(constant.ALTER_SPLIT_STR)
        alert_map = {}
        for alert_str in alert_array[1:]:
            Tools.split_value_map(alert_str, alert_map, split=':')
            occur_time = int(time.mktime(time.strptime(
                alert_map['IndicationTime'],
                constant.ALTER_TIME_TYPE)))
            if query_para is None or \
                    (int(query_para['begin_time'])
                     <= occur_time
                     <= int(query_para['end_time'])):
                alert_model = {
                    'alert_id': alert_map['AlertID'],
                    'alert_name': alert_map['ProbableCause'],
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
        disks_array = disks_info.split(
            constant.DISK_SPLIT_STR)
        physicals_info = self.ssh_do_exec(
            constant.DISK_SHOW_PHYSICAL_COMMAND)
        error_disk = self.ssh_do_exec(
            constant.DISK_ERROR_COMMAND
        )
        error_disk_list = []
        error_disk_array = error_disk.split('\r\n')
        for error_disk in error_disk_array[1:]:
            error_array = error_disk.split()
            if len(error_array) > 2:
                error_disk_list.append(error_array[0])
        disks_map = {}
        physical_array = physicals_info.split('\r\n')
        for i in range(2, len(physical_array), 2):
            physicals_list.append(physical_array[i].split())
        for disk_str in disks_array[1:]:
            speed = physical_type = firmware = None
            Tools.split_value_map(disk_str, disks_map, split=':')
            logical_type = constant.DISK_LOGICAL. \
                get(disks_map['ContainerType'])
            """Map disk physical information"""
            for physical_info in physicals_list:
                if len(physical_info) > 6 and \
                        physical_info[0] == disks_map['k']:
                    physical_type = \
                        constant.DISK_TYPE.get(physical_info[1])
                    speed = physical_info[5]
                    firmware = physical_info[4]
            status = constants.DiskStatus.NORMAL
            if disks_map[constant.DISK_NAME] in error_disk_list:
                status = constants.DiskStatus.ABNORMAL
            disk_model = {
                'name': disks_map[constant.DISK_NAME],
                'storage_id': storage_id,
                'native_disk_id': disks_map[constant.DISK_NAME],
                'serial_number': disks_map['SerialNumber'],
                'manufacturer': disks_map['Vendor'],
                'model': disks_map['Model'],
                'firmware': firmware,
                'speed': speed,
                'capacity':
                    int(Tools.get_capacity_size(disks_map['PhysicalSize'])),
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
        fs_array = fs_info.split(
            constant.FS_SPLIT_STR)
        thin_fs_info = self.ssh_do_exec(
            constant.THIN_FS_SHOW_COMMAND)
        pool_list = self.list_storage_pools(storage_id)
        thin_fs_array = thin_fs_info.split("\r\n")
        fs_map = {}
        for fs_str in fs_array[1:]:
            type = constants.FSType.THICK
            Tools.split_value_map(fs_str, fs_map, split=':')
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
                status = constant.FS_STATUS.get(fs_map['VolumeState'])
                fs_id = self.get_fs_id(fs_map['Name'], fs_map['VolumeName'])
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
                    'total_capacity':
                        int(Tools.get_capacity_size(fs_map['VolumeSize'])),
                    'used_capacity':
                        int(Tools.get_capacity_size(fs_map['VolumeSize'])) -
                        int(Tools.get_capacity_size(fs_map['AvailableSize'])),
                    'free_capacity':
                        int(Tools.get_capacity_size(fs_map['AvailableSize']))
                }
                if fs_model['total_capacity'] > 0:
                    fs_list.append(fs_model)
        return fs_list

    def list_controllers(self, storage_id):
        try:
            controller_list = []
            controller_info = self.ssh_do_exec(
                constant.CONTROLLER_SHOW_DETAIL_COMMAND)
            controller_array = controller_info.split(
                constant.CONTROLLER_SPLIT_STR)
            controller_map = {}
            for controller_str in controller_array[1:]:
                Tools.split_value_map(
                    controller_str, controller_map, split=':')
                if controller_map is not None or controller_map != {}:
                    status = constants.ControllerStatus.NORMAL \
                        if controller_map['Health'] == 'true' \
                        else constants.ControllerStatus.OFFLINE
                    controller_model = {
                        'name': controller_map[constant.CONTROLLER_NAME],
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
            eth_array = eth_info.split(
                constant.PORT_SPLIT_STR)
            for eth in eth_array[1:]:
                eth_map = {}
                Tools.split_value_map(eth, eth_map, split=':')
                logical_type = constant.ETH_LOGICAL_TYPE.get(
                    eth_map['PortType'])
                port_id = \
                    eth_map[constant.CONTROLLER_NAME] + '_' + eth_map['Port']
                eth_model = {
                    'name': eth_map['Port'],
                    'storage_id': storage_id,
                    'native_port_id': port_id,
                    'location':
                        eth_map[constant.CONTROLLER_NAME] +
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
                    'speed': int(eth_map['SpeedOperational']) * units.Mi,
                    'max_speed': int(eth_map['SpeedOperational']) * units.Mi,
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
            fc_array = fc_info.split(
                constant.PORT_SPLIT_STR)
            for fc in fc_array[1:]:
                fc_map = {}
                Tools.split_value_map(fc, fc_map, split=':')
                type = constant.FC_TYPE.get(fc_map['PhysicalProtocol'])
                port_id = \
                    fc_map[constant.CONTROLLER_NAME] + '_' + fc_map['Adapter']
                fc_model = {
                    'name':
                        fc_map[constant.CONTROLLER_NAME] +
                        ':' + fc_map['Adapter'],
                    'storage_id': storage_id,
                    'native_port_id': port_id,
                    'location':
                        fc_map[constant.CONTROLLER_NAME] +
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
                    'speed': int(fc_map['DataLinkRate(Gbit)']) * units.Gi,
                    'max_speed': int(fc_map['MaximumSpeed']) * units.Gi,
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
            fs_array = fs_info.split(constant.FS_SPLIT_STR)
            qt_array = qt_info.split(constant.QTREE_SPLIT_STR)
            for qt in qt_array[1:]:
                qt_map = {}
                Tools.split_value_map(qt, qt_map, split=':')
                if 'QtreeName' in qt_map.keys():
                    fs_id = self.get_fs_id(qt_map['Name'],
                                           qt_map['VolumeName'])
                    qtree_path = None
                    for fs in fs_array[1:]:
                        fs_map = {}
                        Tools.split_value_map(fs, fs_map, split=':')
                        if fs_id == self.get_fs_id(
                                fs_map['Name'],
                                fs_map['VolumeName']) \
                                and fs_map['JunctionPath'] != '-':
                            qtree_path = fs_map['JunctionPath']
                            break
                    qt_id = self.get_qt_id(
                        qt_map['Name'],
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
            nfs_array = nfs_info.split(constant.FS_SPLIT_STR)
            fs_map = {}
            for nfs_share in nfs_array[1:]:
                Tools.split_value_map(nfs_share, fs_map, split=':')
                protocol = protocol_map.get(fs_map['Name'])
                if constants.ShareProtocol.NFS in protocol:
                    fs_id = self.get_fs_id(fs_map['Name'],
                                           fs_map['VolumeName'])
                    share_name = \
                        fs_map['Name'] + '/' + fs_map['VolumeName']
                    qt_id = self.get_qt_id(fs_map['Name'],
                                           fs_map['VolumeName'], '')
                    qtree_id = None
                    for qtree in qtree_list:
                        if qtree['native_qtree_id'] == qt_id:
                            qtree_id = qt_id
                        if fs_id == qtree['native_filesystem_id'] \
                                and qtree['name'] != "" \
                                and qtree['name'] != qtree['native_qtree_id']:
                            qt_share_name = share_name + '/' + qtree['name']
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
        cifs_share_array = share_info.split(
            constant.CIFS_SHARE_SPLIT_STR)
        for cifs_share in cifs_share_array[1:]:
            share_map = {}
            Tools.split_value_map(cifs_share, share_map, split=':')
            if 'VolumeName' in share_map.keys() and \
                    share_map['VolumeName'] != '-':
                protocol_str = protocol_map.get(
                    share_map[constant.VSERVER_NAME])
                fs_id = self.get_fs_id(share_map[constant.VSERVER_NAME],
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
                            share_map[constant.VSERVER_NAME],
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
            protocol_arr = protocol_info.split('\r\n')
            for protocol in protocol_arr[1:]:
                agr_arr = protocol.split()
                if len(agr_arr) > 1:
                    protocol_map[agr_arr[0]] = agr_arr[1]
            vserver_info = self.ssh_do_exec(
                constant.VSERVER_SHOW_COMMAND)
            vserver_array = vserver_info.split("\r\n")
            for vserver in vserver_array[3:]:
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
            quotas_array = quotas_info.split(constant.QUOTA_SPLIT_STR)
            for quota_info in quotas_array[1:]:
                quota_map = {}
                user_group_name = None
                Tools.split_value_map(quota_info, quota_map, ":")
                if 'VolumeName' in quota_map.keys():
                    quota_id = \
                        quota_map[constant.VSERVER_NAME] + '_' + \
                        quota_map['VolumeName'] + '_' + \
                        quota_map['Type'] + '_' + \
                        quota_map['QtreeName'] + '_' + \
                        quota_map['Target']
                    type = constant.QUOTA_TYPE.get(quota_map['Type'])
                    qt_id = self.get_qt_id(
                        quota_map[constant.VSERVER_NAME],
                        quota_map['VolumeName'], '')
                    if type == 'tree' and quota_map['Target'] != '':
                        qt_id += '/' + quota_map['Target']
                    else:
                        if type == 'user' or 'group':
                            user_group_name = quota_map['Target']
                        if quota_map['QtreeName'] != '':
                            qt_id += '/' + quota_map['QtreeName']
                    fs_id = self.get_fs_id(quota_map[constant.VSERVER_NAME],
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
            mgt_ip_array = mgt_ip.split("\r\n")
            node_ip_array = node_ip.split("\r\n")
            for node in node_ip_array[2:]:
                ip_array = node.split()
                if len(ip_array) == 3:
                    ip_list.append({'host': ip_array[2]})
            ip_list.append({'host': mgt_ip_array[2].split()[2]})
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
