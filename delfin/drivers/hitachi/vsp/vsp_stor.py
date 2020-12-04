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

    TIME_PATTERN = '%Y-%m-%dT%H:%M:%S'

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

    def list_volumes(self, context):
        try:
            volumes_info = self.rest_handler.get_all_volumes()

            volume_list = []
            volumes = volumes_info.get('data')
            for volume in volumes:
                if volume.get('emulationType') == 'NOT DEFINED':
                    continue
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
                if volume.get('label'):
                    name = volume.get('label')
                else:
                    name = 'ldev_%s' % str(volume.get('ldevId'))

                v = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'description': 'Hitachi VSP volume',
                    'status': status,
                    'native_volume_id': str(volume.get('ldevId')),
                    'native_storage_pool_id': orig_pool_id,
                    'type': vol_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                }

                volume_list.append(v)

            return volume_list
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
                'alarm_id': alert.get('alertId'),
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
                ),
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

            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = ("Failed to build alert model as some attributes missing in"
                   " alert message:%s") % (six.text_type(e))
            raise exception.InvalidResults(msg)

    def clear_alert(self, context, alert):
        pass
