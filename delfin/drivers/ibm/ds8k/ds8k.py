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
import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.ibm.ds8k import rest_handler, alert_handler, consts
from delfin.drivers.ibm.ds8k.alert_handler import AlertHandler

LOG = log.getLogger(__name__)


class DS8KDriver(driver.StorageDriver):

    PORT_TYPE_MAP = {'FC-AL': constants.PortType.FC,
                     'SCSI-FCP': constants.PortType.FC,
                     'FICON': constants.PortType.FICON
                     }
    PORT_STATUS_MAP = {
        'online': constants.PortHealthStatus.NORMAL,
        'offline': constants.PortHealthStatus.ABNORMAL,
        'fenced': constants.PortHealthStatus.UNKNOWN,
        'quiescing': constants.PortHealthStatus.UNKNOWN
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

    def get_storage(self, context):
        try:
            result = None
            system_info = self.rest_handler.get_rest_info('/api/v1/systems')
            if system_info:
                system_data = system_info.get('data', {}).get('systems', [])
                if system_data:
                    for system in system_data:
                        name = system.get('name')
                        model = system.get('MTM')
                        serial_number = system.get('sn')
                        version = system.get('release')
                        status = constants.StorageStatus.NORMAL
                        if system.get('state') != 'online':
                            status = constants.StorageStatus.ABNORMAL
                        total = 0
                        free = 0
                        used = 0
                        raw = 0
                        if system.get('cap') != '' and \
                                system.get('cap') is not None:
                            total = int(system.get('cap'))
                        if system.get('capraw') != '' and \
                                system.get('capraw') is not None:
                            raw = int(system.get('capraw'))
                        if system.get('capalloc') != '' and \
                                system.get('capalloc') is not None:
                            used = int(system.get('capalloc'))
                        if system.get('capavail') != '' and \
                                system.get('capavail') is not None:
                            free = int(system.get('capavail'))
                        result = {
                            'name': name,
                            'vendor': 'IBM',
                            'model': model,
                            'status': status,
                            'serial_number': serial_number,
                            'firmware_version': version,
                            'location': '',
                            'total_capacity': total,
                            'raw_capacity': raw,
                            'used_capacity': used,
                            'free_capacity': free
                        }
                        break
                else:
                    raise exception.StorageBackendException(
                        "ds8k storage system info is None")
            else:
                raise exception.StorageBackendException(
                    "ds8k storage system info is None")
            return result
        except Exception as err:
            err_msg = "Failed to get storage attributes from ds8k: %s" % \
                      (six.text_type(err))
            raise exception.InvalidResults(err_msg)

    def list_storage_pools(self, context):
        pool_info = self.rest_handler.get_rest_info('/api/v1/pools')
        pool_list = []
        status = constants.StoragePoolStatus.NORMAL
        if pool_info is not None:
            pool_data = pool_info.get('data', {}).get('pools', [])
            for pool in pool_data:
                if pool.get('stgtype') == 'fb':
                    pool_type = constants.StorageType.BLOCK
                else:
                    pool_type = constants.StorageType.FILE
                if (int(pool.get('capalloc')) / int(pool.get('cap'))) * 100 > \
                        int(pool.get('threshold')):
                    status = constants.StoragePoolStatus.ABNORMAL
                pool_name = '%s_%s' % (pool.get('name'), pool.get('node'))
                pool_result = {
                    'name': pool_name,
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': str(pool.get('id')),
                    'status': status,
                    'storage_type': pool_type,
                    'total_capacity': int(pool.get('cap')),
                    'used_capacity': int(pool.get('capalloc')),
                    'free_capacity': int(pool.get('capavail'))
                }
                pool_list.append(pool_result)
        return pool_list

    def list_volumes(self, context):
        volume_list = []
        pool_list = self.rest_handler.get_rest_info('/api/v1/pools')
        if pool_list is not None:
            pool_data = pool_list.get('data', {}).get('pools', [])
            for pool in pool_data:
                url = '/api/v1/pools/%s/volumes' % pool.get('id')
                volumes = self.rest_handler.get_rest_info(url)
                if volumes is not None:
                    vol_entries = volumes.get('data', {}).get('volumes', [])
                    for volume in vol_entries:
                        total = volume.get('cap')
                        used = volume.get('capalloc')
                        vol_type = constants.VolumeType.THICK if \
                            volume.get('stgtype') == 'fb' else \
                            constants.VolumeType.THIN
                        status = constants.StorageStatus.NORMAL if \
                            volume.get('state') == 'normal' else\
                            constants.StorageStatus.ABNORMAL
                        vol_name = '%s_%s' % (volume.get('name'),
                                              volume.get('id'))
                        vol = {
                            'name': vol_name,
                            'storage_id': self.storage_id,
                            'description': '',
                            'status': status,
                            'native_volume_id': str(volume.get('id')),
                            'native_storage_pool_id':
                                volume.get('pool').get('id'),
                            'wwn': '',
                            'type': vol_type,
                            'total_capacity': int(total),
                            'used_capacity': int(used),
                            'free_capacity': int(total) - int(used)
                        }
                        volume_list.append(vol)
        return volume_list

    def list_alerts(self, context, query_para=None):
        alert_model_list = []
        alert_list = self.rest_handler.get_rest_info(
            '/api/v1/events?severity=warning,error')
        alert_handler.AlertHandler() \
            .parse_queried_alerts(alert_model_list, alert_list, query_para)
        return alert_model_list

    @staticmethod
    def division_port_wwn(original_wwn):
        result_wwn = None
        if not original_wwn:
            return result_wwn
        is_first = True
        for i in range(0, len(original_wwn), 2):
            if is_first is True:
                result_wwn = '%s' % (original_wwn[i:i + 2])
                is_first = False
            else:
                result_wwn = '%s:%s' % (result_wwn, original_wwn[i:i + 2])
        return result_wwn

    def list_ports(self, context):
        port_list = []
        port_info = self.rest_handler.get_rest_info('/api/v1/ioports')
        if port_info:
            port_data = port_info.get('data', {}).get('ioports', [])
            for port in port_data:
                status = DS8KDriver.PORT_STATUS_MAP.get(
                    port.get('state'), constants.PortHealthStatus.UNKNOWN)
                speed = None
                connection_status = constants.PortConnectionStatus.CONNECTED\
                    if status == constants.PortHealthStatus.NORMAL \
                    else constants.PortConnectionStatus.DISCONNECTED
                if port.get('speed'):
                    speed = int(port.get('speed').split(' ')[0]) * units.G
                port_result = {
                    'name': port.get('loc'),
                    'storage_id': self.storage_id,
                    'native_port_id': port.get('id'),
                    'location': port.get('loc'),
                    'connection_status': connection_status,
                    'health_status': status,
                    'type': DS8KDriver.PORT_TYPE_MAP.get(
                        port.get('protocol'), constants.PortType.OTHER),
                    'logical_type': '',
                    'speed': speed,
                    'max_speed': speed,
                    'wwn': DS8KDriver.division_port_wwn(port.get('wwpn'))
                }
                port_list.append(port_result)
        return port_list

    def list_controllers(self, context):
        controller_list = []
        controller_info = self.rest_handler.get_rest_info('/api/v1/nodes')
        if controller_info:
            contrl_data = controller_info.get('data', {}).get('nodes', [])
            for contrl in contrl_data:
                status = constants.ControllerStatus.NORMAL if \
                    contrl.get('state') == 'online' else \
                    constants.ControllerStatus.UNKNOWN
                controller_result = {
                    'name': contrl.get('id'),
                    'storage_id': self.storage_id,
                    'native_controller_id': contrl.get('id'),
                    'status': status
                }
                controller_list.append(controller_result)
        return controller_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        pass

    def clear_alert(self, context, alert):
        pass

    @staticmethod
    def get_access_url():
        return 'https://{ip}:{port}'

    def get_serial_number(self):
        serial_number = None
        system_info = \
            self.rest_handler.get_rest_info('/api/v1/systems')
        if system_info:
            system_data = system_info.get('data', {}).get(
                'systems', [])
            for system in system_data:
                serial_number = system.get('sn')
                break
        return serial_number

    def handle_performance_data(self, metrics, serial_number,
                                start_time, end_time, storage_id):
        perf_url = '/api/v1/systems/%s/performance' % serial_number
        perf_info = self.rest_handler.get_rest_info(perf_url)
        if perf_info:
            time_pattern = "%Y-%m-%dT%H:%M:%S%z"
            perf_data = \
                perf_info.get('data', {}).get('performance', [])
            for perf in perf_data:
                occur_time = int(time.mktime(time.strptime(
                    perf.get('performancesampletime'),
                    time_pattern))
                ) * AlertHandler.SECONDS_TO_MS
                if occur_time < start_time:
                    break
                if start_time <= occur_time <= end_time:
                    DS8KDriver.search_record_from_metrics(
                        metrics, 'iops', storage_id, occur_time,
                        float(perf.get('IOPS', {}).get('total', 0)))
                    DS8KDriver.search_record_from_metrics(
                        metrics, 'readIops', storage_id, occur_time,
                        float(perf.get('IOPS', {}).get('read', 0)))
                    DS8KDriver.search_record_from_metrics(
                        metrics, 'writeIops', storage_id, occur_time,
                        float(perf.get('IOPS', {}).get('write', 0)))
                    DS8KDriver.search_record_from_metrics(
                        metrics, 'responseTime', storage_id, occur_time,
                        float(perf.get('responseTime', {}).get('average', 0)))

    @staticmethod
    def search_record_from_metrics(metrics, metric_type, storage_id,
                                   occur_time, value):
        bfind = False
        for metric in metrics:
            if metric.get('resource_id') == storage_id and \
                    metric.get('type') == metric_type:
                bfind = True
                metric['values'][occur_time] = value
                break
        if not bfind:
            metric_value = {
                'type': metric_type,
                'resource_id': storage_id,
                'values': {occur_time: value}
            }
            metrics.append(metric_value)

    @staticmethod
    def package_metrics(storage_id, resource_type, metrics, metrics_list):
        for metric in metrics_list:
            unit = consts.STORAGE_CAP[metric.get('type')]['unit']
            labels = {
                'storage_id': storage_id,
                'resource_type': resource_type,
                'resource_id': metric.get('resource_id'),
                'type': 'RAW',
                'unit': unit
            }
            value = constants.metric_struct(name=metric.get('type'),
                                            labels=labels,
                                            values=metric.get('values'))
            metrics.append(value)

    def collect_perf_metrics(self, context, storage_id,
                             resource_metrics, start_time,
                             end_time):
        metrics = []
        try:
            if resource_metrics.get(constants.ResourceType.STORAGE):
                storage_metrics = []
                serial_number = self.get_serial_number()
                if not serial_number:
                    return metrics
                self.handle_performance_data(storage_metrics, serial_number,
                                             start_time, end_time, storage_id)
                DS8KDriver.package_metrics(
                    storage_id, constants.ResourceType.STORAGE,
                    metrics, storage_metrics)
        except Exception as err:
            err_msg = "Failed to collect metrics from ds8k: %s" % \
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
                constants.ResourceType.STORAGE: consts.STORAGE_CAP
            }
        }

    def get_latest_perf_timestamp(self, context):
        latest_time = 0
        serial_number = self.get_serial_number()
        if not serial_number:
            return latest_time
        perf_url = '/api/v1/systems/%s/performance' % serial_number
        perf_info = self.rest_handler.get_rest_info(perf_url)
        if perf_info:
            time_pattern = "%Y-%m-%dT%H:%M:%S%z"
            perf_data = \
                perf_info.get('data', {}).get('performance', [])
            for perf in perf_data:
                occur_time = int(time.mktime(time.strptime(
                    perf.get('performancesampletime'),
                    time_pattern))
                ) * AlertHandler.SECONDS_TO_MS
                latest_time = occur_time
                break
        return latest_time
