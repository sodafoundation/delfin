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
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.hds.vsp import consts
from delfin.drivers.hds.vsp import rest_handler
from delfin.drivers.utils.rest_client import RestClient

LOG = log.getLogger(__name__)


class HdsVspDriver(driver.StorageDriver):
    POOL_STATUS_MAP = {"POLN": constants.StoragePoolStatus.NORMAL,
                       "POLF": constants.StoragePoolStatus.ABNORMAL,
                       "POLS": constants.StoragePoolStatus.ABNORMAL,
                       "POLE": constants.StoragePoolStatus.OFFLINE
                       }

    TIME_PATTERN = '%Y-%m-%dT%H:%M:%S'

    REFCODE_OID = '1.3.6.1.4.1.116.5.11.4.2.3'
    DESC_OID = '1.3.6.1.4.1.116.5.11.4.2.7'
    TRAP_TIME_OID = '1.3.6.1.4.1.116.5.11.4.2.6'
    TRAP_DATE_OID = '1.3.6.1.4.1.116.5.11.4.2.5'
    TRAP_NICKNAME_OID = '1.3.6.1.4.1.116.5.11.4.2.2'
    LOCATION_OID = '1.3.6.1.4.1.116.5.11.4.2.4'
    SECONDS_TO_MS = 1000

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(RestClient(**kwargs))
        self.rest_handler.get_device_id()
        self.rest_handler.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.rest_client.verify = kwargs.get('verify', False)
        self.rest_handler.get_device_id()
        self.rest_handler.login()

    def close_connection(self):
        self.rest_handler.logout()

    def get_storage(self, context):
        free_total = 0
        total_total = 0
        used_total = 0
        self.rest_handler.get_device_id()
        if self.rest_handler.device_model in consts.VSP_MODEL_NOT_USE_SVPIP:
            capacity_json = self.rest_handler.get_capacity()
            free_total = capacity_json.get("total").get("freeSpace") * units.Ki
            total_total = capacity_json.get("total").get("totalCapacity") * \
                units.Ki
            used_total = total_total - free_total
        else:
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
                    free_total = free_total + free_cap
                    total_total = total_total + total_cap
                used_total = total_total - free_total
        firmware_version = self.rest_handler.get_specific_storage()
        status = constants.StorageStatus.OFFLINE
        if firmware_version is not None:
            status = constants.StorageStatus.NORMAL
        system_name = '%s_%s' % (self.rest_handler.device_model,
                                 self.rest_handler.rest_client.rest_host)

        s = {
            'name': system_name,
            'vendor': 'Hitachi',
            'description': 'Hitachi VSP Storage',
            'model': str(self.rest_handler.device_model),
            'status': status,
            'serial_number': str(self.rest_handler.serial_number),
            'firmware_version': str(firmware_version),
            'location': '',
            'raw_capacity': int(total_total),
            'total_capacity': int(total_total),
            'used_capacity': int(used_total),
            'free_capacity': int(free_total)
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
                    'subscribed_capacity': int(total_cap),
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
            wwn = ''
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
                    int(volume.get('blockCapacity')) * consts.Block_Size
                used_cap = \
                    int(volume.get('blockCapacity')) * consts.Block_Size
                free_cap = total_cap - used_cap
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
                    'wwn': wwn,
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

    def list_alerts(self, context, query_para=None):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = alert.get(HdsVspDriver.REFCODE_OID)
            alert_model['alert_name'] = alert.get(HdsVspDriver.DESC_OID)
            alert_model['severity'] = constants.Severity.INFORMATIONAL
            alert_model['category'] = constants.Category.NOT_SPECIFIED
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            aler_time = '%s %s' % (alert.get(HdsVspDriver.TRAP_DATE_OID),
                                   alert.get(HdsVspDriver.TRAP_TIME_OID))
            pattern = '%Y-%m-%d %H:%M:%S'
            occur_time = time.strptime(aler_time, pattern)
            alert_model['occur_time'] = int(time.mktime(occur_time) *
                                            HdsVspDriver.SECONDS_TO_MS)
            alert_model['description'] = alert.get(HdsVspDriver.DESC_OID)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['location'] = alert.get(HdsVspDriver.LOCATION_OID)

            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = ("Failed to build alert model as some attributes missing in"
                   " alert message:%s") % (six.text_type(e))
            raise exception.InvalidResults(msg)

    def clear_alert(self, context, alert):
        pass
