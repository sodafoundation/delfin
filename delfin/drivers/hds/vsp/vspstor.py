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

from oslo_log import log
from delfin.common import constants
from delfin.drivers import driver
from delfin import exception
from delfin.drivers.hds.vsp import rest_handler, alert_handler
from delfin.drivers.utils.rest_client import RestClient
from delfin.drivers.hds.vsp import consts

LOG = log.getLogger(__name__)


class HdsVspDriver(driver.StorageDriver):
    ALERT_LEVEL_MAP = {"Acute": constants.Severity.CRITICAL,
                       "Serious": constants.Severity.MAJOR,
                       "Moderate": constants.Severity.WARNING,
                       "Service": constants.Severity.INFORMATIONAL
                       }
    POOL_STATUS_MAP = {"POLN": consts.StoragePoolStatus.NORMAL,
                       "POLF": constants.StoragePoolStatus.ABNORMAL,
                       "POLS": constants.StoragePoolStatus.ABNORMAL,
                       "POLE": constants.StoragePoolStatus.OFFLINE
                       }

    TIME_PATTERN = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.restclient = RestClient(**kwargs)
        self.resthanlder = rest_handler.RestHandler(self.restclient)
        self.resthanlder.get_device_id()
        self.resthanlder.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_client.verify = kwargs.get('verify', False)
        self.resthanlder.get_device_id()
        self.rest_handler.login()

    def close_connection(self):
        self.rest_handler.logout()

    def get_storage(self, context):
        self.resthanlder.get_device_id()
        if self.resthanlder.device_model in consts.VSP_MODEL_NOT_USE_SVPIP:
            system_name = self.resthanlder.get_system_by_snmp()
        else:
            system_name = self.resthanlder.get_summaries_system()
        capacityjson = self.resthanlder.get_capacity()
        status = constants.StorageStatus.OFFLINE
        if system_name is not None:
            status = consts.StorageStatus.NORMAL

        s = {
            'name': system_name,
            'vendor': 'Hitachi',
            'description': 'Hitachi VSP Storage',
            'model': self.resthanlder.device_model,
            'status': status,
            'serial_number': self.resthanlder.serialNumber,
            'firmware_version': '',
            'location': '',
            'raw_capacity': capacityjson["internal"]["totalCapacity"]
                        * consts.KB_TO_Bytes,
            'subscribed_capacity': capacityjson["internal"]["totalCapacity"]
                        * consts.KB_TO_Bytes -
            capacityjson["internal"]["freeSpace"] * consts.KB_TO_Bytes,
            'total_capacity': capacityjson["total"]["totalCapacity"]
                        * consts.KB_TO_Bytes,
            'used_capacity': capacityjson["total"]["totalCapacity"]
                        * consts.KB_TO_Bytes -
            capacityjson["total"]["freeSpace"] * consts.KB_TO_Bytes,
            'free_capacity': capacityjson["total"]["freeSpace"]
                        * consts.KB_TO_Bytes
        }
        return s

    def list_storage_pools(self, context):
        try:
            poolsinfo = self.resthanlder.get_all_pools()
            pool_list = []
            if poolsinfo is not None:
                pools = poolsinfo.get('data')
            else:
                return pool_list

            for pool in pools:
                status = self.POOL_STATUS_MAP.get(
                    pool.get('poolStatus'),
                    constants.StoragePoolStatus.OFFLINE
                )
                storage_type = consts.StorageType.FILE
                total_cap = \
                    int(pool.get('totalPoolCapacity')) * consts.MiB_TO_Bytes
                free_cap = int(
                    pool.get('availableVolumeCapacity')) * consts.MiB_TO_Bytes
                used_cap = total_cap - free_cap
                subscribed_capacity = int(pool['totalReservedCapacity']) \
                    * consts.MiB_TO_Bytes

                p = {
                    'name': pool.get('poolName'),
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': pool.get('poolId'),
                    'description': 'Hitachi VSP Pool',
                    'status': status,
                    'storage_type': storage_type,
                    'subscribed_capacity': subscribed_capacity,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from hdsvspttor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from hdsvspttor')

    def list_volumes(self, context):
        try:
            wwn = ''
            volumesinfo = self.resthanlder.get_all_volumes()

            volume_list = []
            if volumesinfo is not None:
                volumes = volumesinfo.get('data')
            else:
                return volume_list

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
                status = 'offline'
                if volume.get('status') == 'NML':
                    status = 'normal'
                else:
                    status = 'abnormal'

                # for port in volume.get('ports'):
                #     if 'wwn' in port:
                #         if wwn is None:
                #             wwn = '''%s''' % (port.get('wwn'))
                #         else:
                #             wwn = '''%s,%s''' % (wwn, port.get('wwn'))

                vol_type = consts.VolumeType.THICK
                for voltype in volume.get('attributes'):
                    if voltype == 'HTI':
                        vol_type = consts.VolumeType.THIN

                total_cap = \
                    int(volume.get('blockCapacity')) * consts.Block_Size
                used_cap = \
                    int(volume.get('numOfUsedBlock')) * consts.Block_Size
                free_cap = total_cap - used_cap

                v = {
                    'name': volume.get('label'),
                    'storage_id': self.storage_id,
                    'description': 'Hitachi VSP volume',
                    'status': status,
                    'native_volume_id': volume.get('ldevId'),
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

        except Exception as err:
            LOG.error(
                "Failed to get list volumes from OceanStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get list volumes from hitachi')

    def handle_alert(self, alerts, alert_list):
        if alerts is not None:
            alerts = alerts.get('data')
        else:
            return alert_list

        for alert in alerts:
            occur_time = int(time.mktime(time.strptime(
                alert.get('occurenceTime'),
                self.TIME_PATTERN)))
            a = {
                'location': alert.get('location'),
                'alarm_id': alert.get('alertId'),
                'sequence_number': alert.get('alertIndex'),
                'description': alert.get('errorDetail'),
                'alert_name': alert.get('errorSection'),
                'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                'occur_time': int(occur_time * 1000),
                'category': 'Fault',
                'type': constants.EventType.EQUIPMENT_ALARM,
                'severity': self.ALERT_LEVEL_MAP.get(
                    alert.get('errorLevel'),
                    constants.Severity.NOT_SPECIFIED
                ),
            }
            alert_list.append(a)

    def list_alerts(self, context):
        alerts_info_ctl1 = self.resthanlder.get_alerts('type=CTL1')
        alerts_info_ctl2 = self.resthanlder.get_alerts('type=CTL2')
        alerts_info_dkc = self.resthanlder.get_alerts('type=DKC')
        alert_list = []
        self.handle_alert(alerts_info_ctl1, alert_list)
        self.handle_alert(alerts_info_ctl2, alert_list)
        self.handle_alert(alerts_info_dkc, alert_list)

        return alert_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(self, context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, alert):
        pass
