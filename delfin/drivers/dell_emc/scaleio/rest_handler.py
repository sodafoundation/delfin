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
import uuid
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
            raise e

    def logout(self):
        try:
            if self.session:
                self.session.close()
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def get_storage(self):
        try:
            storage_json = self.get_rest_info(consts.REST_SCALEIO_SYSTEM)
            if storage_json:
                for system_json in storage_json:
                    system_id = system_json.get('id')
                    system_links = json.loads(json.dumps(
                        system_json.get('links')))
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
                    total_capacity = 0
                    used_capacity = 0
                    raw_capacity = 0
                    if system_links:
                        for system_link in system_links:
                            if 'Statistics' in system_link.get('href'):
                                storage_detail = self.get_rest_info(
                                    system_link.get('href'))
                                total_capacity = storage_detail.\
                                    get('maxCapacityInKb')
                                used_capacity = storage_detail.\
                                    get('capacityInUseInKb')
                                raw_capacity = storage_detail.\
                                    get('unreachableUnusedCapacityInKb')
                        storage_map = {
                            'name': 'ScaleIO',
                            'vendor': consts.StorageVendor,
                            'model': model,
                            'status': status,
                            'serial_number': system_id,
                            'firmware_version': version_id,
                            'raw_capacity': int(raw_capacity) * units.Ki,
                            'total_capacity': int(total_capacity) * units.Ki,
                            'used_capacity': int(used_capacity) * units.Ki,
                            'free_capacity': int(total_capacity
                                                 - used_capacity) * units.Ki
                        }
                        return storage_map
        except Exception as e:
            LOG.error("Get Storage System error: %s", six.text_type(e))
            raise e

    def list_storage_pools(self, storage_id):
        storage_pool_list = []
        try:
            storage_pool_json = self.get_rest_info(
                consts.REST_SCALEIO_STORAGE_POOL)
            if storage_pool_json:
                for pool_json in storage_pool_json:
                    name = pool_json.get('name')
                    native_storage_pool_id = pool_json.get('id')
                    links = pool_json.get('links')
                    used_capacity = 0
                    total_size = 0
                    for link in links:
                        if 'Statistics' in link.get('rel'):
                            storage_pool_statics = self.get_rest_info(
                                link.get('href'))
                            json.dumps(storage_pool_statics)
                            used_capacity = storage_pool_statics.\
                                get('capacityInUseInKb')
                            total_size = storage_pool_statics.\
                                get('maxCapacityInKb')
                    pool_map = {
                        'name': name,
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
        except Exception as e:
            LOG.error("Get Storage pool error: %s", six.text_type(e))
            raise e

    def list_volumes(self, storage_id):
        list_volumes = []
        try:
            storage_volume_json = self.get_rest_info(
                consts.REST_SCALEIO_VOLUMES)
            if storage_volume_json:
                for json_volume in storage_volume_json:
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
        except Exception as e:
            LOG.error("Get Storage volume error: %s", six.text_type(e))
            raise e

    def list_disks(self, storage_id):
        disks_list = []
        try:
            disks_json = self.get_rest_info(consts.REST_SCALEIO_DISKS)
            if disks_json:
                for json_disk in disks_json:
                    device_status = json_disk.get('deviceState')
                    capacity = json_disk.get('maxCapacityInKb')
                    status = constants.DiskStatus.NORMAL
                    if device_status != 'Normal':
                        status = constants.DiskStatus.OFFLINE
                    data_map = {
                        'native_disk_id': json_disk.get('id'),
                        'name': json_disk.get('name'),
                        'status': status,
                        'storage_id': storage_id,
                        'native_disk_group_id': json_disk.get('sdsId'),
                        'serial_number': json_disk.get('id'),
                        'capacity': int(capacity) * units.Ki,
                        'health_score': status
                    }
                    disks_list.append(data_map)
                return disks_list
        except Exception as e:
            LOG.error("Get Storage disk error: %s", six.text_type(e))
            raise e

    def list_alerts(self, query_para=None):
        alert_list = []
        try:
            storage_alert = self.get_rest_info(consts.REST_SCALEIO_ALERT)
            if storage_alert:
                for json_alert in storage_alert:
                    match_key = json_alert.get('id') + json_alert.get('name')
                    occur_time = json_alert.get('startTime')
                    datetime_obj = datetime.datetime.strptime(
                        occur_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                    alert_time = int(time.mktime(datetime_obj.timetuple()) *
                                     consts.DEFAULT_ALERTS_TIME_CONVERSION
                                     + datetime_obj.microsecond /
                                     consts.DEFAULT_ALERTS_TIME_CONVERSION)
                    if not alert_util.is_alert_in_time_range(query_para,
                                                             alert_time):
                        continue
                    alert_model = {
                        'alert_id': json_alert.get('id'),
                        'alert_name': json_alert.get('name'),
                        'severity': json_alert.get('severity'),
                        'category': constants.Category.FAULT,
                        'type': json_alert.get('alertType'),
                        'sequence_number': json_alert.get('uuid'),
                        'description': json_alert.get('alertType'),
                        'occur_time': alert_time,
                        'match_key': hashlib.md5(
                            match_key.encode()).hexdigest()
                    }
                    alert_list.append(alert_model)
                return alert_list
        except Exception as e:
            LOG.error("Get Storage alerts error: %s", six.text_type(e))
            raise e

    def list_storage_host_initiators(self, storage_id):
        initiators_list = []
        try:
            storage_initiators = self.get_rest_info(
                consts.REST_SCALIO_INITIIATORS)
            if storage_initiators:
                for initiators_json in storage_initiators:
                    status = initiators_json.get('mdmConnectionState')
                    initiators_id = initiators_json['id']
                    if 'Connected' == status:
                        status = constants.HostStatus.NORMAL
                    elif 'Disconnected' == status:
                        status = constants.HostStatus.OFFLINE
                    initiators_dict = {
                        "name": initiators_json.get('name'),
                        "storage_id": storage_id,
                        "native_storage_host_initiator_id": initiators_id,
                        "wwn": initiators_id,
                        "status": status,
                        "native_storage_host_id": initiators_json.get(
                            'protectionDomainId'),
                    }
                    initiators_list.append(initiators_dict)
                return initiators_list
        except Exception as e:
            LOG.error("Get Storage initiators error: %s", six.text_type(e))
            raise e

    def list_storage_hosts(self, storage_id):
        host_list = []
        try:
            storage_hosts = self.get_rest_info(consts.REST_SCALIO_HOSTS)
            if storage_hosts:
                for host_json in storage_hosts:
                    status = host_json.get('mdmConnectionState')
                    if 'Connected' == status:
                        status = constants.HostStatus.NORMAL
                    elif 'Disconnected' == status:
                        status = constants.HostStatus.OFFLINE
                    ip_list = host_json.get('ipList')
                    ip_address = ''
                    for ip in ip_list:
                        ip_address = ip.get('ip')
                    host_dict = {
                        "name": host_json.get('name'),
                        "description": host_json.get('sdcGuid'),
                        "storage_id": storage_id,
                        "native_storage_host_id":
                            host_json.get('id'),
                        "os_type": host_json.get('osType'),
                        "status": status,
                        "ip_address": ip_address
                    }
                    host_list.append(host_dict)
                return host_list
        except Exception as e:
            LOG.error("Get Storage hosts error: %s", six.text_type(e))
            raise e

    def list_masking_views(self, storage_id):
        list_masking_views_list = []
        try:
            storage_view = self.get_rest_info(consts.REST_SCALEIO_VOLUMES)
            if storage_view:
                for map_json in storage_view:
                    view_name = map_json.get('name')
                    volume_id = map_json.get('id')
                    map_sdc_list = map_json.get('mappedSdcInfo')
                    if map_sdc_list:
                        for map_sdc in map_sdc_list:
                            sdc_id = map_sdc.get('sdcId')
                            uid = uuid.uuid4()
                            view_map = {
                                "name": view_name + sdc_id + volume_id,
                                "description": view_name,
                                "storage_id": storage_id,
                                "native_masking_view_id": str(uid) + volume_id,
                                'native_volume_id': volume_id,
                                'native_storage_host_id': sdc_id
                            }
                            list_masking_views_list.append(view_map)
                return list_masking_views_list
        except Exception as e:
            LOG.error("Get Storage views error: %s", six.text_type(e))
            raise e

    def get_rest_info(self, url, data=None, method='GET'):
        result_json = None
        if 'login' == data:
            self.session.auth = requests.auth.HTTPBasicAuth(
                self.rest_username, cryptor.decode(self.rest_password))
        else:
            self.login()
            self.session.auth = requests.auth.HTTPBasicAuth(
                self.rest_username, self.rest_auth_token)
        res = self.do_call(url, data, method)
        if res.status_code == 200:
            result_json = json.loads(res.text)
        return result_json
