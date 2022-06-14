# Copyright 2022 The SODA Authors.
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
import hashlib
import six
import json

import requests
import datetime
import time
from oslo_log import log
from oslo_utils import units
from delfin import exception
from delfin import cryptor
from delfin.common import alert_util
from delfin.drivers.utils.rest_client import RestClient
from delfin.drivers.dell_emc.scaleio import consts
from delfin.drivers.dell_emc.scaleio import alert_consts
from delfin.common import constants

LOG = log.getLogger(__name__)


class RestHandler(RestClient):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_http_head()
        self.login()

    def login(self):
        try:
            res = self.get_rest_info(consts.REST_AUTH_LOGIN, 'login', 'GET')
            if res:
                self.rest_auth_token = res
            else:
                LOG.error("Login error. URL: %(url)s\n"
                          "Reason: %(reason)s.",
                          {"url": consts.REST_AUTH_LOGIN, "reason": res.text})
                if 'User authentication failed' in res.text:
                    raise exception.InvalidUsernameOrPassword()
                else:
                    raise exception.StorageBackendException(
                        six.text_type(res.text))
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def logout(self):
        try:
            if self.session:
                self.session.close()
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(e)

    def get_storage(self, storage_id):
        try:
            storage_json = self.get_rest_info(consts.REST_SCALEIO_SYSTEM)
            for system_json in (storage_json or []):
                system_id = system_json.get('id')
                system_links = json.loads(json.dumps(
                    system_json.get('links')))
                total_capacity = 0
                used_capacity = 0
                raw_capacity = 0
                if not system_links:
                    continue
                storage_disk_list = self.list_disks(storage_id)
                for storage_disk in storage_disk_list:
                    raw_capacity += storage_disk.get('capacity')
                mdm_cluster = json.loads(json.dumps(
                    system_json.get('mdmCluster')))
                version_info = json.dumps(
                    system_json.get('systemVersionName'))
                version_detail = version_info.split(' Version: ')
                version_id = version_detail[1].replace('\"', '')
                model = version_detail[0].replace('\"', '')
                cluster_state = mdm_cluster.get('clusterState')
                status = constants.StorageStatus.OFFLINE
                if 'Degraded' in cluster_state:
                    status = constants.StorageStatus.DEGRADED
                elif 'Normal' in cluster_state:
                    status = constants.StorageStatus.NORMAL
                for system_link in system_links:
                    if 'Statistics' in system_link.get('href'):
                        storage_detail = self.get_rest_info(
                            system_link.get('href'))
                        total_capacity = storage_detail. \
                            get('maxCapacityInKb')
                        used_capacity = storage_detail. \
                            get('capacityInUseInKb')
                storage_map = {
                    'name': 'ScaleIO',
                    'vendor': consts.StorageVendor,
                    'model': model,
                    'status': status,
                    'serial_number': system_id,
                    'firmware_version': version_id,
                    'raw_capacity': raw_capacity,
                    'total_capacity': int(total_capacity) * units.Ki,
                    'used_capacity': int(used_capacity) * units.Ki,
                    'free_capacity': int(total_capacity
                                         - used_capacity) * units.Ki
                }
                return storage_map
        except exception.DelfinException as err:
            err_msg = "Get Storage System error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage System error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_storage_pools(self, storage_id):
        storage_pool_list = []
        try:
            storage_pool_json = self.get_rest_info(
                consts.REST_SCALEIO_STORAGE_POOL)
            for pool_json in (storage_pool_json or []):
                pool_name = pool_json.get('name')
                native_storage_pool_id = pool_json.get('id')
                pool_links = pool_json.get('links')
                used_capacity = 0
                total_size = 0
                for pool_link in pool_links:
                    if 'Statistics' in pool_link.get('rel'):
                        storage_pool_statics = self.get_rest_info(
                            pool_link.get('href'))
                        json.dumps(storage_pool_statics)
                        used_capacity = storage_pool_statics.\
                            get('capacityInUseInKb')
                        total_size = storage_pool_statics.\
                            get('maxCapacityInKb')
                pool_map = {
                    'name': pool_name,
                    'storage_id': storage_id,
                    'native_storage_pool_id': native_storage_pool_id,
                    'status': constants.StorageStatus.NORMAL,
                    'storage_type': constants.StorageType.BLOCK,
                    'total_capacity': int(total_size) * units.Ki,
                    'used_capacity': int(used_capacity) * units.Ki,
                    'free_capacity': int(total_size -
                                         used_capacity) * units.Ki
                }
                storage_pool_list.append(pool_map)
            return storage_pool_list
        except exception.DelfinException as err:
            err_msg = "Get Storage pool error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage pool error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_volumes(self, storage_id):
        list_volumes = []
        try:
            storage_volume_json = self.get_rest_info(
                consts.REST_SCALEIO_VOLUMES)
            for json_volume in (storage_volume_json or []):
                volume_name = json_volume.get('name')
                native_storage_pool_id = json_volume.get('storagePoolId')
                native_volume_id = json_volume.get('id')
                total_size = json_volume.get('sizeInKb')
                volume_type = constants.VolumeType.THIN
                if 'Thick' in json_volume.get('volumeType'):
                    volume_type = constants.VolumeType.THICK
                volume_map = {
                    'name': volume_name,
                    'storage_id': storage_id,
                    'description': volume_name,
                    'status': 'normal',
                    'native_volume_id': native_volume_id,
                    'native_storage_pool_id': native_storage_pool_id,
                    'wwn': native_volume_id,
                    'type': volume_type,
                    'total_capacity': int(total_size) * units.Ki,
                    'free_capacit': consts.DEFAULT_VOLUME_USERD_CAPACITY,
                    'used_capacity': consts.DEFAULT_VOLUME_USERD_CAPACITY,
                    'compressed': True,
                    'deduplicated': True
                }
                list_volumes.append(volume_map)
            return list_volumes
        except exception.DelfinException as err:
            err_msg = "Get Storage volume error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage volume error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_disks(self, storage_id):
        disks_list = []
        try:
            storage_disks_json = self.get_rest_info(consts.REST_SCALEIO_DISKS)
            for json_disk in (storage_disks_json or []):
                device_status = json_disk.get('deviceState')
                capacity = json_disk.get('maxCapacityInKb')
                status = constants.DiskStatus.NORMAL
                if device_status != 'Normal':
                    status = constants.DiskStatus.OFFLINE
                disk_map = {
                    'native_disk_id': json_disk.get('id'),
                    'name': json_disk.get('name'),
                    'status': status,
                    'storage_id': storage_id,
                    'native_disk_group_id': json_disk.get('sdsId'),
                    'serial_number': json_disk.get('id'),
                    'capacity': int(capacity) * units.Ki,
                    'health_score': status
                }
                disks_list.append(disk_map)
            return disks_list
        except exception.DelfinException as err:
            err_msg = "Get Storage disk error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage disk error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_alerts(self, query_para=None):
        alert_list = []
        try:
            storage_alert = self.get_rest_info(consts.REST_SCALEIO_ALERT)
            alert_description_map = alert_consts.ALERT_MAP
            for json_alert in (storage_alert or []):
                match_key = json_alert.get('id') + json_alert.get('name')
                occur_time = json_alert.get('startTime')
                datetime_obj = datetime.datetime.strptime(
                    occur_time, consts.DATETIME_UTC_FORMAT)
                alert_time = int(time.mktime(datetime_obj.timetuple()) *
                                 consts.DEFAULT_ALERTS_TIME_CONVERSION
                                 + datetime_obj.microsecond /
                                 consts.DEFAULT_ALERTS_TIME_CONVERSION)
                alert_type_desc = json_alert.get('alertType')
                alert_type_desc = alert_type_desc.lower().replace('_', ' ')
                if not alert_util.is_alert_in_time_range(query_para,
                                                         alert_time):
                    continue
                alert_severity = json_alert.get('severity')
                if 'LOW' in alert_severity:
                    alert_severity = constants.Severity.MINOR
                elif 'MEDIUM' in alert_severity:
                    alert_severity = constants.Severity.CRITICAL
                elif 'HIGH' in alert_severity:
                    alert_severity = constants.Severity.FATAL
                alert_type = json_alert.get('alertType')
                alert_model = {
                    'alert_id': json_alert.get('id'),
                    'alert_name': alert_type + json_alert.get('name'),
                    'severity': alert_severity,
                    'category': constants.Category.FAULT,
                    'type': alert_type,
                    'sequence_number': json_alert.get('uuid'),
                    'description': alert_description_map.get(
                        json_alert.get('alertType'), alert_type_desc),
                    'occur_time': alert_time,
                    'match_key': hashlib.md5(
                        match_key.encode()).hexdigest()
                }
                alert_list.append(alert_model)
            return alert_list
        except exception.DelfinException as err:
            err_msg = "Get Storage alerts error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage alerts error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_storage_host_initiators(self, storage_id):
        initiators_list = []
        try:
            storage_initiators = self.get_rest_info(
                consts.REST_SCALIO_INITIIATORS)
            list_host = self.list_storage_hosts(storage_id)
            for initiators_json in (storage_initiators or []):
                status = initiators_json.get('sdsState')
                initiators_id = initiators_json.get('id')
                initiators_type = constants.InitiatorType.UNKNOWN
                if 'iscsi' in initiators_json.get('perfProfile'):
                    initiators_type = constants.InitiatorType.ISCSI
                if 'Normal' == status:
                    status = constants.InitiatorStatus.ONLINE
                elif 'Disconnected' == status:
                    status = constants.InitiatorStatus.OFFLINE
                ip_list = initiators_json.get('ipList')
                native_storage_host_id = None
                for ip_data in ip_list:
                    sds_ip = ip_data.get('ip')
                    for host_json in list_host:
                        ip_address = host_json.get('ip_address')
                        if sds_ip == ip_address:
                            native_storage_host_id = \
                                host_json.get('native_storage_host_id')
                initiators_dict = {
                    "name": initiators_json.get('name'),
                    "storage_id": storage_id,
                    "native_storage_host_initiator_id": initiators_id,
                    "wwn": initiators_id,
                    "type": initiators_type,
                    "status": status,
                    "native_storage_host_id": native_storage_host_id,
                }
                initiators_list.append(initiators_dict)
            return initiators_list
        except exception.DelfinException as err:
            err_msg = "Get Storage initiators error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage initiators error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_storage_hosts(self, storage_id):
        host_list = []
        try:
            storage_hosts = self.get_rest_info(consts.REST_SCALIO_HOSTS)
            for host_json in (storage_hosts or []):
                status = host_json.get('mdmConnectionState')
                if 'Connected' == status:
                    status = constants.HostStatus.NORMAL
                elif 'Disconnected' == status:
                    status = constants.HostStatus.OFFLINE
                ip_address = host_json.get('sdcIp')
                soft_version = host_json.get('softwareVersionInfo')
                host_dict = {
                    "name": host_json.get('sdcGuid'),
                    "description": ip_address + soft_version,
                    "storage_id": storage_id,
                    "native_storage_host_id":
                        host_json.get('id'),
                    "os_type": host_json.get('osType'),
                    "status": status,
                    "ip_address": ip_address
                }
                host_list.append(host_dict)
            return host_list
        except exception.DelfinException as err:
            err_msg = "Get Storage hosts error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage hosts error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    def list_masking_views(self, storage_id):
        list_masking_views_list = []
        try:
            storage_view = self.get_rest_info(consts.REST_SCALEIO_VOLUMES)
            for map_json in (storage_view or []):
                view_name = map_json.get('name')
                volume_id = map_json.get('id')
                map_sdc_list = map_json.get('mappedSdcInfo')
                if map_sdc_list:
                    for map_sdc in map_sdc_list:
                        sdc_id = map_sdc.get('sdcId')
                        view_map = {
                            "name": view_name + sdc_id + volume_id,
                            "description": view_name,
                            "storage_id": storage_id,
                            "native_masking_view_id":
                                view_name + sdc_id + volume_id,
                            'native_volume_id': volume_id,
                            'native_storage_host_id': sdc_id
                        }
                        list_masking_views_list.append(view_map)
            return list_masking_views_list
        except exception.DelfinException as err:
            err_msg = "Get Storage Views Error: %s" % err.msg
            LOG.error(err_msg)
            raise err
        except Exception as e:
            LOG.error("Get Storage Views Error: %s", six.text_type(e))
            raise exception.InvalidResults(e)

    @staticmethod
    def parse_alert(alert):
        alert_model = dict()
        try:
            alert_dict = alert.split(' ')
            for alert_json in alert_dict:
                alert_detail = alert_json.split('=')[1]
                if consts.OID_SEVERITY in alert_json:
                    severity = consts.TRAP_ALERT_MAP.get(
                        alert_detail, constants.Severity.INFORMATIONAL)
                    alert_model['severity'] = severity
                elif consts.OID_EVENT_ID in alert_json:
                    alert_model['alert_name'] = alert_detail.replace('\"', '')
                elif consts.OID_EVENT_TYPE in alert_json:
                    alert_desc = alert_detail.split('.')[2].lower().replace(
                        '_', ' ')
                    alert_model['description'] = alert_desc
                    alert_model['location'] = alert_desc
                elif consts.OID_ERR_ID in alert_json:
                    alert_model['alert_id'] = str(
                        alert_detail.replace('\"', ''))
                alert_model['category'] = constants.Category.FAULT
                alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
                now = time.time()
                alert_model['occur_time'] = \
                    int(round(now * consts.DEFAULT_ALERTS_TIME_CONVERSION))
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = "Failed to build alert model: %s." % (six.text_type(e))
            raise exception.InvalidResults(msg)

    def get_rest_info(self, url, data=None, method='GET'):
        if 'login' == data:
            self.session.auth = requests.auth.HTTPBasicAuth(
                self.rest_username, cryptor.decode(self.rest_password))
        else:
            self.login()
            self.session.auth = requests.auth.HTTPBasicAuth(
                self.rest_username, self.rest_auth_token)
        res = self.do_call(url, data, method)
        try:
            if res.status_code == 200:
                result_json = json.loads(res.text)
            elif res.status_code == 500:
                LOG.error('Connect Timeout error')
                raise exception.ConnectTimeout()
            elif res.status_code == 401:
                LOG.error('User authentication failed')
                raise exception.InvalidUsernameOrPassword
            else:
                raise exception.BadResponse()
        except Exception as err:
            LOG.exception('Get RestHandler.call failed: %(url)s.'
                          ' Error: %(err)s', {'url': url, 'err': err})
            raise exception.InvalidResults(err)
        return result_json
