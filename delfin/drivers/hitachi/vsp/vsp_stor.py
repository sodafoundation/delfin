# Copyright 2021 The SODA Authors.
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
import hashlib
import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import alert_util
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.hitachi.vsp import consts
from delfin.drivers.hitachi.vsp import rest_handler

LOG = log.getLogger(__name__)


class HitachiVspDriver(driver.StorageDriver):
    POOL_STATUS_MAP = {"POLN": constants.StoragePoolStatus.NORMAL,
                       "POLF": constants.StoragePoolStatus.NORMAL,
                       "POLS": constants.StoragePoolStatus.ABNORMAL,
                       "POLE": constants.StoragePoolStatus.OFFLINE
                       }
    ALERT_LEVEL_MAP = {"Acute": constants.Severity.CRITICAL,
                       "Serious": constants.Severity.MAJOR,
                       "Moderate": constants.Severity.WARNING,
                       "Service": constants.Severity.INFORMATIONAL
                       }
    TRAP_ALERT_LEVEL_MAP = {
        "1.3.6.1.4.1.116.3.11.4.1.1.0.1": constants.Severity.CRITICAL,
        "1.3.6.1.4.1.116.3.11.4.1.1.0.2": constants.Severity.MAJOR,
        "1.3.6.1.4.1.116.3.11.4.1.1.0.3": constants.Severity.WARNING,
        "1.3.6.1.4.1.116.3.11.4.1.1.0.4": constants.Severity.INFORMATIONAL
    }
    DISK_LOGIC_TYPE_MAP = {"DATA": constants.DiskLogicalType.MEMBER,
                           "SPARE": constants.DiskLogicalType.SPARE,
                           "FREE": constants.DiskLogicalType.FREE
                           }
    DISK_PHYSICAL_TYPE_MAP = {"SAS": constants.DiskPhysicalType.SAS,
                              "SATA": constants.DiskPhysicalType.SATA,
                              "SSD": constants.DiskPhysicalType.SSD,
                              "FC": constants.DiskPhysicalType.FC
                              }
    PORT_TYPE_MAP = {"FIBRE": constants.PortType.FC,
                     "SCSI": constants.PortType.OTHER,
                     "ISCSI": constants.PortType.ETH,
                     "ENAS": constants.PortType.OTHER,
                     "ESCON": constants.PortType.OTHER,
                     "FICON": constants.PortType.FICON,
                     "FCoE": constants.PortType.FCOE,
                     "HNASS": constants.PortType.OTHER,
                     "HNASU": constants.PortType.OTHER
                     }

    TIME_PATTERN = '%Y-%m-%dT%H:%M:%S'
    AUTO_PORT_SPEED = 8 * units.Gi

    REFCODE_OID = '1.3.6.1.4.1.116.5.11.4.2.3'
    DESC_OID = '1.3.6.1.4.1.116.5.11.4.2.7'
    TRAP_TIME_OID = '1.3.6.1.4.1.116.5.11.4.2.6'
    TRAP_DATE_OID = '1.3.6.1.4.1.116.5.11.4.2.5'
    TRAP_NICKNAME_OID = '1.3.6.1.4.1.116.5.11.4.2.2'
    OID_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'
    SECONDS_TO_MS = 1000

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

    def get_storage(self, context):
        self.rest_handler.get_device_id()
        if self.rest_handler.device_model in consts.SUPPORTED_VSP_SERIES:
            capacity_json = self.rest_handler.get_capacity()
            free_capacity = capacity_json.get("total").get("freeSpace") * \
                units.Ki
            total_capacity = \
                capacity_json.get("total").get("totalCapacity") * units.Ki
        else:
            free_capacity = 0
            total_capacity = 0
            pools_info = self.rest_handler.get_all_pools()
            if pools_info is not None:
                pools = pools_info.get('data')
                for pool in pools:
                    total_cap = \
                        int(pool.get(
                            'totalPoolCapacity')) * units.Mi
                    free_cap = int(
                        pool.get(
                            'availableVolumeCapacity')) * units.Mi
                    free_capacity = free_capacity + free_cap
                    total_capacity = total_capacity + total_cap
        firmware_version = self.rest_handler.get_firmware_version()
        status = constants.StorageStatus.OFFLINE
        if firmware_version is not None:
            status = constants.StorageStatus.NORMAL
        system_name = '%s_%s' % (self.rest_handler.device_model,
                                 self.rest_handler.rest_host)

        s = {
            'name': system_name,
            'vendor': 'Hitachi',
            'description': 'Hitachi VSP Storage',
            'model': str(self.rest_handler.device_model),
            'status': status,
            'serial_number': str(self.rest_handler.serial_number),
            'firmware_version': str(firmware_version),
            'location': '',
            'raw_capacity': int(total_capacity),
            'total_capacity': int(total_capacity),
            'used_capacity': int(total_capacity - free_capacity),
            'free_capacity': int(free_capacity)
        }
        return s

    def list_storage_pools(self, context):
        try:
            pools_info = self.rest_handler.get_all_pools()
            pool_list = []
            pools = pools_info.get('data')
            for pool in pools:
                status = self.POOL_STATUS_MAP.get(
                    pool.get('poolStatus'),
                    constants.StoragePoolStatus.ABNORMAL
                )
                storage_type = constants.StorageType.BLOCK
                total_cap = \
                    int(pool.get('totalPoolCapacity')) * units.Mi
                free_cap = int(
                    pool.get('availableVolumeCapacity')) * units.Mi
                used_cap = total_cap - free_cap
                p = {
                    'name': pool.get('poolName'),
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': str(pool.get('poolId')),
                    'description': 'Hitachi VSP Pool',
                    'status': status,
                    'storage_type': storage_type,
                    'total_capacity': int(total_cap),
                    'used_capacity': int(used_cap),
                    'free_capacity': int(free_cap),
                }
                pool_list.append(p)

            return pool_list
        except exception.DelfinException as err:
            err_msg = "Failed to get pool metrics from hitachi vsp: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err
        except Exception as e:
            err_msg = "Failed to get pool metrics from hitachi vsp: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def to_vsp_lun_id_format(lun_id):
        hex_str = hex(lun_id)
        result = ''
        hex_lun_id = hex_str[2::].rjust(6, '0')
        is_first = True
        for i in range(0, len(hex_lun_id), 2):
            if is_first is True:
                result = '%s' % (hex_lun_id[i:i + 2])
                is_first = False
            else:
                result = '%s:%s' % (result, hex_lun_id[i:i + 2])
        return result

    def list_volumes(self, context):
        head_id = 0
        is_end = False
        volume_list = []
        while is_end is False:
            is_end = self.get_volumes_paginated(volume_list, head_id)
            head_id += consts.LDEV_NUMBER_OF_PER_REQUEST
        return volume_list

    def get_volumes_paginated(self, volume_list, head_id):
        try:
            volumes_info = self.rest_handler.get_volumes(head_id)
            volumes = volumes_info.get('data')
            for volume in volumes:
                if volume.get('emulationType') == 'NOT DEFINED':
                    return True
                orig_pool_id = volume.get('poolId')
                compressed = False
                deduplicated = False
                if volume.get('dataReductionMode') == \
                        'compression_deduplication':
                    deduplicated = True
                    compressed = True
                if volume.get('dataReductionMode') == 'compression':
                    compressed = True
                if volume.get('status') == 'NML':
                    status = 'normal'
                else:
                    status = 'abnormal'

                vol_type = constants.VolumeType.THICK
                for voltype in volume.get('attributes'):
                    if voltype == 'HTI':
                        vol_type = constants.VolumeType.THIN

                total_cap = \
                    int(volume.get('blockCapacity')) * consts.BLOCK_SIZE
                used_cap = \
                    int(volume.get('blockCapacity')) * consts.BLOCK_SIZE
                # Because there is only subscribed capacity in device,so free
                # capacity always 0
                free_cap = 0
                native_volume_id = HitachiVspDriver.to_vsp_lun_id_format(
                    volume.get('ldevId'))
                if volume.get('label'):
                    name = volume.get('label')
                else:
                    name = native_volume_id

                v = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'description': 'Hitachi VSP volume',
                    'status': status,
                    'native_volume_id': str(native_volume_id),
                    'native_storage_pool_id': orig_pool_id,
                    'type': vol_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                }

                volume_list.append(v)
            return False
        except exception.DelfinException as err:
            err_msg = "Failed to get volumes metrics from hitachi vsp: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err
        except Exception as e:
            err_msg = "Failed to get volumes metrics from hitachi vsp: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_controllers(self, context):
        try:
            controller_list = []
            controller_info = self.rest_handler.get_controllers()
            if controller_info is not None:
                con_entries = controller_info.get('ctls')
                for control in con_entries:
                    status = constants.ControllerStatus.OFFLINE
                    if control.get('status') == 'Normal':
                        status = constants.ControllerStatus.NORMAL
                    controller_result = {
                        'name': control.get('location'),
                        'storage_id': self.storage_id,
                        'native_controller_id': control.get('location'),
                        'status': status,
                        'location': control.get('location')
                    }
                    controller_list.append(controller_result)
            return controller_list
        except Exception as err:
            err_msg = "Failed to get controller attributes from vsp: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_ports(self, context):
        try:
            port_list = []
            ports = self.rest_handler.get_all_ports()
            if ports is None:
                return port_list
            port_entries = ports.get('data')
            for port in port_entries:
                ipv4 = None
                ipv4_mask = None
                ipv6 = None
                wwn = None
                status = constants.PortHealthStatus.NORMAL
                conn_status = constants.PortConnectionStatus.CONNECTED
                if port.get('portType') == 'ISCSI':
                    iscsi_port = self.rest_handler.get_detail_ports(
                        port.get('portId'))
                    LOG.error(iscsi_port)
                    ipv4 = iscsi_port.get('ipv4Address')
                    ipv4_mask = iscsi_port.get('ipv4Subnetmask')
                    if iscsi_port.get('ipv6LinkLocalAddress', {}).get(
                        "status") == 'VAL':
                        ipv6 = iscsi_port.get('ipv6LinkLocalAddress', {}).get(
                            "address")
                speed = HitachiVspDriver.AUTO_PORT_SPEED if \
                    port.get('portSpeed') == 'AUT' else \
                    int(port.get('portSpeed')[:-1]) * units.Gi
                if port.get('portType') == 'FIBRE':
                    wwn = port.get('wwn')
                    if wwn:
                        wwn = wwn.upper()
                port_type = HitachiVspDriver.PORT_TYPE_MAP.get(
                    port.get('portType'),
                    constants.PortType.OTHER)
                port_result = {
                    'name': port.get('portId'),
                    'storage_id': self.storage_id,
                    'native_port_id': port.get('portId'),
                    'location': port.get('portId'),
                    'connection_status': conn_status,
                    'health_status': status,
                    'type': port_type,
                    'logical_type': '',
                    'max_speed': speed,
                    'mac_address': port.get('macAddress'),
                    'wwn': wwn,
                    'ipv4': ipv4,
                    'ipv4_mask': ipv4_mask,
                    'ipv6': ipv6
                }
                port_list.append(port_result)
            LOG.error(port_list)
            return port_list
        except Exception as err:
            err_msg = "Failed to get ports attributes from vsp: %s" % \
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_disks(self, context):
        try:
            disks = self.rest_handler.get_disks()
            disk_list = []
            if disks is not None:
                disk_entries = disks.get('data')
                for disk in disk_entries:
                    status = constants.DiskStatus.ABNORMAL
                    if disk.get('status' == 'NML'):
                        status = constants.DiskStatus.NORMAL
                    physical_type = \
                        HitachiVspDriver.DISK_PHYSICAL_TYPE_MAP.get(
                            disk.get('driveTypeName'),
                            constants.DiskPhysicalType.UNKNOWN)
                    logical_type = HitachiVspDriver.DISK_LOGIC_TYPE_MAP.get(
                        disk.get('usageType'),
                        constants.DiskLogicalType.UNKNOWN)
                    disk_result = {
                        'name': disk.get('driveLocationId'),
                        'storage_id': self.storage_id,
                        'native_disk_id': disk.get('driveLocationId'),
                        'serial_number': disk.get('serialNumber'),
                        'speed': int(disk.get('driveSpeed')),
                        'capacity': int(disk.get('totalCapacity') * units.Gi),
                        'status': status,
                        'physical_type': physical_type,
                        'logical_type': logical_type,
                        'native_disk_group_id': disk.get('parityGroupId'),
                        'location': disk.get('driveLocationId')
                    }
                    disk_list.append(disk_result)
            return disk_list

        except Exception as err:
            err_msg = "Failed to get disk attributes from : %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def parse_queried_alerts(alerts, alert_list, query_para=None):
        for alert in alerts:
            occur_time = int(time.mktime(time.strptime(
                alert.get('occurenceTime'),
                HitachiVspDriver.TIME_PATTERN))) * \
                HitachiVspDriver.SECONDS_TO_MS
            if not alert_util.is_alert_in_time_range(query_para,
                                                     occur_time):
                continue
            a = {
                'location': alert.get('location'),
                'alert_id': alert.get('alertId'),
                'sequence_number': alert.get('alertIndex'),
                'description': alert.get('errorDetail'),
                'alert_name': alert.get('errorSection'),
                'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                'occur_time': occur_time,
                'category': constants.Category.FAULT,
                'type': constants.EventType.EQUIPMENT_ALARM,
                'severity': HitachiVspDriver.ALERT_LEVEL_MAP.get(
                    alert.get('errorLevel'),
                    constants.Severity.INFORMATIONAL
                )
            }
            alert_list.append(a)

    def list_alerts(self, context, query_para=None):
        alert_list = []
        if self.rest_handler.device_model in consts.SUPPORTED_VSP_SERIES:
            alerts_info_ctl1 = self.resthanlder.get_alerts('type=CTL1')
            alerts_info_ctl2 = self.resthanlder.get_alerts('type=CTL2')
            alerts_info_dkc = self.resthanlder.get_alerts('type=DKC')
            HitachiVspDriver.parse_queried_alerts(alerts_info_ctl1,
                                                  alert_list, query_para)
            HitachiVspDriver.parse_queried_alerts(alerts_info_ctl2,
                                                  alert_list, query_para)
            HitachiVspDriver.parse_queried_alerts(alerts_info_dkc,
                                                  alert_list, query_para)
        else:
            err_msg = "list_alerts is not supported in model %s" % \
                      self.rest_handler.device_model
            LOG.error(err_msg)
            raise NotImplementedError(err_msg)

        return alert_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = alert.get(HitachiVspDriver.REFCODE_OID)
            alert_model['alert_name'] = alert.get(HitachiVspDriver.DESC_OID)
            severity = HitachiVspDriver.TRAP_ALERT_LEVEL_MAP.get(
                alert.get(HitachiVspDriver.OID_SEVERITY),
                constants.Severity.INFORMATIONAL
            )
            alert_model['severity'] = severity
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            aler_time = '%s%s' % (alert.get(HitachiVspDriver.TRAP_DATE_OID),
                                  alert.get(HitachiVspDriver.TRAP_TIME_OID))
            pattern = '%Y/%m/%d%H:%M:%S'
            occur_time = time.strptime(aler_time, pattern)
            alert_model['occur_time'] = int(time.mktime(occur_time) *
                                            HitachiVspDriver.SECONDS_TO_MS)
            alert_model['description'] = alert.get(HitachiVspDriver.DESC_OID)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['location'] = alert.get(HitachiVspDriver.
                                                TRAP_NICKNAME_OID)
            alert_model['match_key'] = hashlib.md5(
                alert.get(HitachiVspDriver.DESC_OID).encode()).hexdigest()

            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = ("Failed to build alert model as some attributes missing in"
                   " alert message:%s") % (six.text_type(e))
            raise exception.InvalidResults(msg)

    def clear_alert(self, context, alert):
        pass
