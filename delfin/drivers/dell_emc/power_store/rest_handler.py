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
import datetime
import hashlib
import threading
import time
from decimal import Decimal

import requests
import six
from oslo_log import log as logging
from oslo_utils import units

from delfin import exception, utils, cryptor
from delfin.common import constants
from delfin.drivers.dell_emc.power_store import consts
from delfin.drivers.utils.rest_client import RestClient
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_LOGIN_SESSION_URL = '/api/rest/login_session'
    REST_LOGOUT_URL = '/api/rest/logout'
    REST_CLUSTER_URL = \
        '/api/rest/cluster?select=name,compatibility_level,global_id,state,' \
        'primary_appliance_id,id,system_time&limit=2000&offset={}'
    REST_APPLIANCE_URL = '/api/rest/appliance?select=id,name,model,mode' \
                         '&limit=2000&offset={}'
    REST_SOFTWARE_INSTALLED_URL = \
        '/api/rest/software_installed?select=id,release_version,' \
        'build_version,appliance&limit=2000&offset={}'
    REST_VOLUME_URL = '/api/rest/volume?select=id,name,description,state,' \
                      'type,wwn,size,appliance_id&limit=2000&offset={}'
    REST_GENERATE_URL = '/api/rest/metrics/generate'
    REST_FC_PORT_URL = \
        '/api/rest/fc_port?select=appliance_id,current_speed,id,is_link_up,' \
        'name,partner_id,supported_speeds,wwn,node_id,sfp_id' \
        '&limit=2000&offset={}'
    REST_ETH_PORT_URL = \
        '/api/rest/eth_port?select=appliance_id,current_speed,id,is_link_up,' \
        'name,partner_id,supported_speeds,mac_address,node_id,sfp_id' \
        '&limit=2000&offset={}'
    REST_SAS_PORT_URL = \
        '/api/rest/sas_port?select=appliance_id,current_speed,id,' \
        'is_link_up,name,node_id,speed,sfp_id&limit=2000&offset={}'
    REST_HARDWARE_URL = \
        '/api/rest/hardware?select=name,extra_details,id,lifecycle_state,' \
        'serial_number,slot,type,appliance_id,status_led_state' \
        '&limit=2000&offset={}'
    REST_NODE_URL = \
        '/api/rest/node?select=appliance_id,id,slot&limit=2000&offset={}'
    REST_ALERT_URL = \
        '/api/rest/alert?select=id,description_l10n,severity,resource_name,' \
        'resource_type,raised_timestamp,state,event_code,resource_id' \
        '&limit=2000&offset={}'
    REST_SNMP_ALERT_URL = \
        '/api/rest/alert?select=id,description_l10n,severity,resource_name,' \
        'resource_type,raised_timestamp,state&limit=2000&offset=0' \
        '&description_l10n=in.({})&snmp_sent_timestamp=not.is.null' \
        '&order=snmp_sent_timestamp'
    REST_INITIATOR_URL = '/api/rest/initiator?select=id,port_name,port_type,' \
                         'host_id&limit=2000&offset={}'
    REST_HOST_URL = '/api/rest/host?select=id,name,host_initiators,os_type,' \
                    'description&limit=2000&offset={}'
    REST_HOST_GROUP_URL = '/api/rest/host_group?select=id,name,hosts,' \
                          'description&limit=2000&offset={}'
    REST_VOLUME_GROUP_URL = '/api/rest/volume_group?select=description,name,' \
                            'id,volumes&limit=2000&offset={}'
    REST_HOST_VOLUME_MAPPING_URL = \
        '/api/rest/host_volume_mapping?select=host_group_id,host_id,id,' \
        'volume_id&limit=2000&offset={}'
    REST_IP_POOL_ADDRESS_URL = \
        '/api/rest/ip_pool_address?select=id,name,address,appliance_id,' \
        'node_id,purposes&limit=2000&offset={}'
    REST_METRICS_ARCHIVE_URL = '/api/rest/metrics_archive'
    REST_FILE_SYSTEM_URL = \
        '/api/rest/file_system?select=id,name,access_policy,filesystem_type,' \
        'size_total,size_used,nas_server_id&limit=2000&offset={}'
    REST_FILE_TREE_QUOTA_URL = \
        '/api/rest/file_tree_quota?select=id,file_system_id,path,' \
        'description,is_user_quotas_enforced,state,hard_limit,soft_limit,' \
        'size_used&limit=2000&offset={}'
    REST_SMB_SHARE_URL = \
        '/api/rest/smb_share?select=id,name,file_system_id,path' \
        '&limit=2000&offset={}'
    REST_NFS_EXPORT_URL = \
        '/api/rest/nfs_export?select=id,name,description,file_system,path' \
        '&limit=2000&offset={}'
    REST_NAS_SERVER_URL = \
        '/api/rest/nas_server?select=id,name&limit=2000&offset={}'
    REST_FILE_USER_QUOTA_URL = \
        '/api/rest/file_user_quota?select=id,uid,hard_limit,size_used,' \
        'soft_limit,state,tree_quota_id,unix_name,windows_name,windows_sid,' \
        'file_system_id&limit=2000&offset={}'
    AUTH_KEY = 'DELL-EMC-TOKEN'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)
        rest_access = kwargs.get('rest')
        self.username = rest_access.get('username')
        self.session_lock = threading.Lock()

    def login(self):
        try:
            with self.session_lock:
                if self.session is None:
                    self.init_http_head()
                self.session.auth = requests.auth.HTTPBasicAuth(
                    self.rest_username, cryptor.decode(self.rest_password))
                res = self.call_with_token(RestHandler.REST_LOGIN_SESSION_URL)
                if res.status_code == 200 or res.status_code == 206:
                    self.session.headers[RestHandler.AUTH_KEY] = \
                        cryptor.encode(res.headers[RestHandler.AUTH_KEY])
                else:
                    LOG.error("Login error.URL: %s,Reason: %s.",
                              RestHandler.REST_LOGIN_SESSION_URL, res.text)
                    if 'Unauthorized' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    elif 'Forbidden' in res.text:
                        raise exception.InvalidIpOrPort()
                    else:
                        raise exception.StorageBackendException(
                            six.text_type(res.text))
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def call_with_token(self, url, data=None, method='GET',
                        calltimeout=consts.DEFAULT_TIMEOUT):
        auth_key = None
        if self.session:
            auth_key = self.session.headers.get(RestHandler.AUTH_KEY, None)
            if auth_key:
                self.session.headers[RestHandler.AUTH_KEY] \
                    = cryptor.decode(auth_key)
        res = self.do_call(url, data, method, calltimeout)
        if auth_key:
            self.session.headers[RestHandler.AUTH_KEY] = auth_key
        return res

    def logout(self):
        res = self.call_with_token(RestHandler.REST_LOGOUT_URL, None, 'POST')
        if res.status_code != consts.StatusCode.SUCCESS_NO_CONTENT and \
                res.status_code != consts.StatusCode.SUCCESS_CREATE_RESPONSE:
            LOG.error("logout error.URL: %s,Reason: %s.",
                      RestHandler.REST_LOGOUT_URL, res.text)
            raise exception.StorageBackendException(six.text_type(res.text))

    def rest_call(self, url, data=None, method='GET', offset=0, result=None,
                  count=0):
        if result is None:
            result = []
        if '{}' in url:
            res = self.call_with_token(url.format(offset), data, method)
        else:
            res = self.call_with_token(url, data, method)
        if res.status_code == consts.StatusCode.SUCCESS:
            result.extend(res.json())
        elif res.status_code == consts.StatusCode.PARTIAL_CONTENT:
            result.extend(res.json())
            if len(res.json()) == consts.LIMIT_COUNT:
                offset += consts.LIMIT_COUNT
                self.rest_call(url, data, method, offset, result, count)
        elif res.status_code == consts.StatusCode.UNAUTHORIZED or \
                res.status_code == consts.StatusCode.FORBIDDEN:
            if count < consts.DigitalConstant.THREE:
                self.login()
                count = count + consts.DigitalConstant.ONE
                self.rest_call(url, data, method, offset, result, count)
        return result

    def get_storage(self, storage_id):
        clusters = self.rest_call(self.REST_CLUSTER_URL)
        if not clusters:
            LOG.error('The cluster data is empty')
            raise exception.StorageBackendException(
                'The cluster data is empty')
        cluster = clusters[consts.DigitalConstant.ZERO]
        appliance_id = cluster.get('primary_appliance_id')
        appliances = self.rest_call(self.REST_APPLIANCE_URL)
        model = ''
        for appliance in appliances:
            if appliance_id == appliance.get('id'):
                model = appliance.get('model')
        pools = self.get_storage_pools(storage_id)
        total_capacity = consts.DigitalConstant.ZERO
        used_capacity = consts.DigitalConstant.ZERO
        for pool in pools:
            total_capacity += pool.get('total_capacity')
            used_capacity += pool.get('used_capacity')
        disks = self.get_disks(storage_id)
        storage_result = {
            'model': model,
            'total_capacity': total_capacity,
            'raw_capacity': sum(disk.get('capacity') for disk in disks),
            'used_capacity': used_capacity,
            'free_capacity': total_capacity - used_capacity,
            'vendor': 'DELL EMC',
            'name': cluster.get('name'),
            'serial_number': cluster.get('global_id'),
            'firmware_version': self.get_firmware_version(appliance_id),
            'status': consts.STORAGE_STATUS_MAP.get(
                cluster.get('state'), constants.StorageStatus.UNKNOWN)
        }
        return storage_result

    def get_firmware_version(self, appliance_id):
        software_s = self.rest_call(RestHandler.REST_SOFTWARE_INSTALLED_URL)
        for software in software_s:
            appliance_d = software.get('appliance')
            if not appliance_d:
                continue
            software_appliance_id = appliance_d.get('id')
            if appliance_id == software_appliance_id:
                return software.get('release_version')

    def get_storage_pools(self, storage_id):
        list_pool = []
        appliances = self.rest_call(RestHandler.REST_APPLIANCE_URL)
        for appliance in appliances:
            appliance_id = appliance.get('id')
            data = {'entity': consts.SPACE_METRICS_BY_APPLIANCE,
                    'entity_id': appliance_id}
            appliance_spaces = self.rest_call(self.REST_GENERATE_URL,
                                              data, 'POST')
            if not appliance_spaces:
                LOG.error('The pools space data is empty')
                raise exception.StorageBackendException(
                    'The pools space data is empty')
            appliance_space = \
                appliance_spaces[consts.DigitalConstant.MINUS_ONE]
            total_capacity = appliance_space.get('physical_total')
            used_capacity = appliance_space.get('physical_used')
            pool_result = {
                'name': appliance.get('name'),
                'storage_id': storage_id,
                'native_storage_pool_id': appliance_id,
                'status': constants.StoragePoolStatus.NORMAL,
                'storage_type': consts.POOL_MODE_MAP.get(
                    appliance.get('mode'), constants.StorageType.BLOCK),
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'free_capacity': total_capacity - used_capacity
            }
            list_pool.append(pool_result)
        return list_pool

    def get_volumes(self, storage_id):
        list_volume = []
        volumes = self.rest_call(self.REST_VOLUME_URL)
        for volume in volumes:
            snapshot_type = volume.get('type')
            if consts.CHARACTER_SNAPSHOT == snapshot_type:
                continue
            volume_type = consts.VOLUME_TYPE_MAP.get(
                snapshot_type, constants.VolumeType.THIN)
            status = consts.VOLUME_STATUS_MAP.get(
                volume.get('state'), constants.StorageStatus.UNKNOWN)
            volume_id = volume.get('id')
            total_capacity = volume.get('size')
            used_capacity = self.get_volume_used_capacity(
                volume_id, volume_type, total_capacity)
            volume_result = {
                'name': volume.get('name'),
                'storage_id': storage_id,
                'description': volume.get('description'),
                'status': status,
                'native_volume_id': volume_id,
                'native_storage_pool_id': volume.get('appliance_id'),
                'wwn': volume.get('wwn') if volume.get('wwn') else '',
                'type': volume_type,
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'free_capacity': total_capacity - used_capacity
            }
            list_volume.append(volume_result)
        return list_volume

    def get_volume_used_capacity(self, volume_id, volume_type, used_capacity):
        if volume_type == constants.VolumeType.THICK:
            return used_capacity
        data = {'entity': consts.SPACE_METRICS_BY_VOLUME,
                'entity_id': volume_id}
        volumes_spaces = self.rest_call(self.REST_GENERATE_URL, data, 'POST')
        if volumes_spaces:
            volumes_space = \
                volumes_spaces[consts.DigitalConstant.MINUS_ONE]
            used_capacity = volumes_space.get('logical_used')
        return used_capacity

    def get_disks(self, storage_id):
        disk_list = []
        hardware_list = self.rest_call(self.REST_HARDWARE_URL)
        for hardware in hardware_list:
            lifecycle_state = hardware.get('lifecycle_state')
            if consts.CHARACTER_DRIVE != hardware.get('type') or \
                    lifecycle_state == consts.CHARACTER_EMPTY:
                continue
            extra_details = hardware.get('extra_details')
            capacity = None
            firmware = ''
            physical_type = constants.DiskPhysicalType.UNKNOWN
            if extra_details:
                firmware = extra_details.get('firmware_version')
                drive_type = extra_details.get('drive_type')
                if drive_type in consts.DiskType.ALL:
                    continue
                physical_type = consts.DISK_PHYSICAL_TYPE.get(
                    drive_type, constants.DiskPhysicalType.UNKNOWN)
                capacity = extra_details.get('size')
            hardware_name = hardware.get('name')
            if not capacity:
                LOG.warning("disk capacity is null: %s", hardware_name)
                continue
            disk_result = {
                'name': hardware_name,
                'storage_id': storage_id,
                'native_disk_id': hardware.get('id'),
                'serial_number': hardware.get('serial_number'),
                'manufacturer': 'DELL EMC',
                'firmware': firmware,
                'capacity': capacity,
                'status': consts.DISK_STATUS_MAP.get(
                    lifecycle_state, constants.DiskStatus.NORMAL),
                'physical_type': physical_type,
                'logical_type': constants.DiskLogicalType.UNKNOWN,
                'location': str(hardware.get('slot'))
            }
            disk_list.append(disk_result)
        return disk_list

    def get_controllers(self, storage_id):
        list_controllers = []
        nodes = self.get_node()
        ips = self.get_ip()
        hardware_list = self.rest_call(self.REST_HARDWARE_URL)
        for hardware in hardware_list:
            lifecycle_state = hardware.get('lifecycle_state')
            if consts.CHARACTER_NODE != hardware.get('type') or \
                    lifecycle_state == consts.CHARACTER_EMPTY:
                continue
            slot = hardware.get('slot')
            appliance_id = hardware.get('appliance_id')
            node_id = nodes.get(f'{appliance_id}{slot}')
            address = ips.get(f'{appliance_id}{node_id}')
            if not address:
                LOG.warning('mgmt_ip is empty,'
                            ' Exceptions may occur in snmptrap')
            extra_details = hardware.get('extra_details')
            memory_size = ''
            cpu_info = ''
            if extra_details:
                memory_size = extra_details.get(
                    'physical_memory_size_gb', 0) * units.Gi
                cpu_info = extra_details.get('cpu_model')
            full_name = hardware.get('name')
            if full_name:
                name = full_name.split('-')[
                    consts.DigitalConstant.MINUS_ONE]
            else:
                LOG.warning('The name of hardware is empty')
                continue
            controller_result = {
                'name': name,
                'storage_id': storage_id,
                'native_controller_id': hardware.get('id'),
                'status': consts.CONTROLLER_STATUS_MAP.get(
                    lifecycle_state, constants.ControllerStatus.UNKNOWN),
                'location': f'{name}:Slot-{slot}',
                'cpu_info': cpu_info,
                'cpu_count': consts.DigitalConstant.ONE,
                'memory_size': memory_size,
                'mgmt_ip': address
            }
            list_controllers.append(controller_result)
        return list_controllers

    def get_node(self):
        node_dict = {}
        nodes = self.rest_call(self.REST_NODE_URL)
        for node in nodes:
            appliance_id = node.get('appliance_id')
            slot = node.get('slot')
            node_id = node.get('id')
            node_dict[f'{appliance_id}{slot}'] = node_id
        return node_dict

    def get_ip(self):
        ip_dict = {}
        ip_pool_address = self.rest_call(self.REST_IP_POOL_ADDRESS_URL)
        for ip_address in ip_pool_address:
            purposes_list = ip_address.get('purposes')
            if consts.MGMT_NODE_COREOS not in purposes_list:
                continue
            address = ip_address.get('address')
            appliance_id = ip_address.get('appliance_id')
            node_id = ip_address.get('node_id')
            ip_dict[f'{appliance_id}{node_id}'] = address
        return ip_dict

    def get_appliance_name(self):
        appliance_name = {}
        appliances = self.rest_call(self.REST_APPLIANCE_URL)
        for appliance in appliances:
            appliance_name[appliance.get('id')] = appliance.get('name')
        return appliance_name

    def get_port_hardware(self):
        hardware_dict = {}
        hardware_list = self.rest_call(self.REST_HARDWARE_URL)
        for hardware in hardware_list:
            hardware_dict[hardware.get('id')] = hardware
        return hardware_dict

    def get_fc_ports(self, storage_id, hardware_dict, appliance_name_dict):
        list_fc_ports = []
        fc_res = self.rest_call(self.REST_FC_PORT_URL)
        for fc in fc_res:
            appliance_id = fc.get('appliance_id')
            name = fc.get('name')
            is_link_up = fc.get('is_link_up')
            connection_status = consts.PORT_CONNECTION_STATUS_MAP.get(
                is_link_up, constants.PortConnectionStatus.UNKNOWN)
            lifecycle_state = hardware_dict.get(
                fc.get('sfp_id'), {}).get('lifecycle_state')
            health_status = consts.PORT_HEALTH_STATUS_MAP.get(
                lifecycle_state, constants.PortHealthStatus.UNKNOWN)
            fc_port_result = {
                'name': name,
                'storage_id': storage_id,
                'native_port_id': fc.get('id'),
                'location': f'{appliance_name_dict.get(appliance_id)}:{name}',
                'connection_status': connection_status,
                'health_status': health_status,
                'type': constants.PortType.FC,
                'speed': self.convert_speed(fc.get('current_speed')),
                'max_speed': self.convert_speed(fc.get('supported_speeds')),
                'native_parent_id': fc.get('node_id'),
                'wwn': fc.get('wwn')
            }
            list_fc_ports.append(fc_port_result)
        return list_fc_ports

    @staticmethod
    def convert_speed(supported_speeds):
        if not supported_speeds:
            return
        supported_speed = \
            supported_speeds[consts.DigitalConstant.MINUS_ONE]\
            if isinstance(supported_speeds, list) else supported_speeds
        if '_Gbps' in supported_speed:
            supported_speed = supported_speed.replace('_Gbps', '')
            return int(supported_speed) * units.G
        if '_Mbps' in supported_speed:
            supported_speed = supported_speed.replace('_Mbps', '')
            return int(supported_speed) * units.M
        if '_Kbps' in supported_speed:
            supported_speed = supported_speed.replace('_Kbps', '')
            return int(supported_speed) * units.k

    def get_eth_ports(self, storage_id, hardware_dict, appliance_name_dict):
        list_eth_ports = []
        eth_ports = self.rest_call(self.REST_ETH_PORT_URL)
        for eth in eth_ports:
            name = eth.get('name')
            appliance_id = eth.get('appliance_id')
            is_link_up = eth.get('is_link_up')
            connection_status = consts.PORT_CONNECTION_STATUS_MAP.get(
                is_link_up, constants.PortConnectionStatus.UNKNOWN)
            lifecycle_state = hardware_dict.get(
                eth.get('sfp_id'), {}).get('lifecycle_state')
            health_status = consts.PORT_HEALTH_STATUS_MAP.get(
                lifecycle_state, constants.PortHealthStatus.UNKNOWN)
            eth_port_result = {
                'name': name,
                'storage_id': storage_id,
                'native_port_id': eth.get('id'),
                'location': f'{appliance_name_dict.get(appliance_id)}:{name}',
                'connection_status': connection_status,
                'health_status': health_status,
                'type': constants.PortType.ETH,
                'speed': self.convert_speed(eth.get('current_speed')),
                'max_speed': self.convert_speed(eth.get('supported_speeds')),
                'native_parent_id': eth.get('node_id'),
                'mac_address': eth.get('mac_address')
            }
            list_eth_ports.append(eth_port_result)
        return list_eth_ports

    def get_sas_ports(self, storage_id, hardware_dict, appliance_name_dict):
        list_sas_ports = []
        sas_ports = self.rest_call(self.REST_SAS_PORT_URL)
        for sas in sas_ports:
            name = sas.get('name')
            appliance_id = sas.get('appliance_id')
            is_link_up = sas.get('is_link_up')
            connection_status = consts.PORT_CONNECTION_STATUS_MAP.get(
                is_link_up, constants.PortConnectionStatus.UNKNOWN)
            lifecycle_state = hardware_dict.get(
                sas.get('sfp_id'), {}).get('lifecycle_state')
            health_status = consts.PORT_HEALTH_STATUS_MAP.get(
                lifecycle_state, constants.PortHealthStatus.UNKNOWN)
            sas_port_result = {
                'name': name,
                'storage_id': storage_id,
                'native_port_id': sas.get('id'),
                'location': f'{appliance_name_dict.get(appliance_id)}:{name}',
                'connection_status': connection_status,
                'health_status': health_status,
                'type': constants.PortType.SAS,
                'speed': self.convert_speed(sas.get('speed')),
                'native_parent_id': sas.get('node_id')
            }
            list_sas_ports.append(sas_port_result)
        return list_sas_ports

    def list_alerts(self, query_para=None):
        alerts = self.rest_call(self.REST_ALERT_URL)
        alerts_list = []
        for alert in alerts:
            if 'CLEARED' == alert.get('state'):
                continue
            raised_timestamp = alert.get('raised_timestamp')
            time_difference = self.get_time_difference()
            timestamp_s = datetime.datetime.strptime(
                raised_timestamp, consts.UTC_FORMAT).timestamp()
            timestamp = int((timestamp_s + time_difference) * units.k) if\
                raised_timestamp else None
            if query_para:
                try:
                    if timestamp is None or timestamp \
                            < int(query_para.get('begin_time')) or \
                            timestamp > int(query_para.get('end_time')):
                        continue
                except Exception as e:
                    LOG.error(e)
            alerts_model = self.set_alert_model(alert, timestamp)
            alerts_list.append(alerts_model)
        return alerts_list

    @staticmethod
    def get_time_difference():
        time_difference = time.mktime(
            time.localtime()) - time.mktime(time.gmtime())
        return time_difference

    @staticmethod
    def get_parse_alerts(snmp_alert):
        try:
            if consts.PARSE_ALERT_DESCRIPTION in snmp_alert.keys():
                description = snmp_alert.get(consts.PARSE_ALERT_DESCRIPTION)
                raised_time = snmp_alert.get(consts.PARSE_ALERT_TIME_UTC)
                timestamp = None
                if raised_time:
                    time_difference = RestHandler.get_time_difference()
                    timestamp_s = datetime.datetime.strptime(
                        raised_time, consts.SYSTEM_TIME_FORMAT).timestamp()
                    timestamp = int((timestamp_s + time_difference) * units.k)
                resource_type = snmp_alert.get(
                    consts.PARSE_ALERT_RESOURCE_TYPE)
                resource_name = snmp_alert.get(
                    consts.PARSE_ALERT_RESOURCE_NAME)
                location = f'{resource_type}:{resource_name}'
                event_code = snmp_alert.get(consts.PARSE_ALERT_CODE)
                resource_id = snmp_alert.get(consts.PARSE_ALERT_RESOURCE_ID)
                match_key_str = f'{description}{timestamp}{resource_type}' \
                                f'{resource_name}{event_code}{resource_id}'
                match_key = hashlib.md5(match_key_str.encode()).hexdigest()
                alerts_model = {
                    'alert_id': match_key,
                    'occur_time': timestamp if
                    timestamp else utils.utcnow_ms(),
                    'severity': consts.SNMP_SEVERITY_MAP.get(
                        snmp_alert.get(consts.PARSE_ALERT_SEVERITY),
                        constants.Severity.NOT_SPECIFIED),
                    'category': constants.Category.FAULT,
                    'location': location if
                    resource_type and resource_name else '',
                    'type': constants.EventType.EQUIPMENT_ALARM,
                    'resource_type': resource_type if resource_type else
                    constants.DEFAULT_RESOURCE_TYPE,
                    'alert_name': description,
                    'match_key': match_key,
                    'description': description
                }
                return alerts_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing"))
            raise exception.InvalidResults(msg)

    def get_alert_sources(self, storage_id):
        sources_list = []
        controllers = self.get_controllers(storage_id)
        for controller in controllers:
            mgmt_ip = controller.get('mgmt_ip')
            mgmt_ip_t = {'host': mgmt_ip}
            sources_list.append(mgmt_ip_t)
        return sources_list

    @staticmethod
    def set_alert_model(alert, timestamp):
        description = alert.get('description_l10n')
        resource_type = alert.get('resource_type')
        resource_name = alert.get('resource_name')
        resource_id = alert.get('resource_id')
        event_code = alert.get('event_code')
        match_key_str = f'{description}{timestamp}{resource_type}' \
                        f'{resource_name}{event_code}{resource_id}'
        alerts_model = {
            'alert_id': alert.get('id'),
            'occur_time': timestamp,
            'severity': consts.ALERT_SEVERITY_MAP.get(
                alert.get('severity'), constants.Severity.NOT_SPECIFIED),
            'category': constants.Category.FAULT,
            'location': f'{resource_type}:{resource_name}',
            'type': constants.EventType.EQUIPMENT_ALARM,
            'resource_type': resource_type,
            'alert_name': description,
            'match_key': hashlib.md5(match_key_str.encode()).hexdigest(),
            'description': description
        }
        return alerts_model

    def list_storage_host_initiators(self, storage_id):
        list_initiators = self.get_initiators(storage_id)
        if list_initiators:
            return list_initiators
        hosts = self.rest_call(self.REST_HOST_URL)
        for host in hosts:
            initiators = host.get('host_initiators')
            for initiator in (initiators or []):
                port_name = initiator.get('port_name')
                initiator_dict = {
                    'native_storage_host_initiator_id': port_name,
                    'native_storage_host_id': host.get('id'),
                    'name': port_name,
                    'type': consts.INITIATOR_TYPE_MAP.get(
                        initiator.get('port_type'),
                        constants.InitiatorType.UNKNOWN),
                    'status': constants.InitiatorStatus.UNKNOWN,
                    'wwn': port_name,
                    'storage_id': storage_id
                }
                list_initiators.append(initiator_dict)
        return list_initiators

    def get_initiators(self, storage_id):
        list_initiators = []
        try:
            initiators = self.rest_call(self.REST_INITIATOR_URL)
            for initiator in initiators:
                port_name = initiator.get('port_name')
                initiator_dict = {
                    'native_storage_host_initiator_id': initiator.get('id'),
                    'native_storage_host_id': initiator.get('host_id'),
                    'name': port_name,
                    'type': consts.INITIATOR_TYPE_MAP.get(
                        initiator.get('port_type'),
                        constants.InitiatorType.UNKNOWN),
                    'status': constants.InitiatorStatus.UNKNOWN,
                    'wwn': port_name,
                    'storage_id': storage_id
                }
                list_initiators.append(initiator_dict)
        except Exception as e:
            LOG.error("get initiators error: %s", six.text_type(e))
        return list_initiators

    def list_storage_hosts(self, storage_id):
        host_list = []
        hosts = self.rest_call(self.REST_HOST_URL)
        for host in hosts:
            h = {
                "name": host.get('name'),
                "storage_id": storage_id,
                "native_storage_host_id": host.get('id'),
                'description': host.get('description')
                if host.get('description') else '',
                "os_type": consts.HOST_OS_TYPES_MAP.get(
                    host.get('os_type'), constants.HostOSTypes.UNKNOWN),
                "status": constants.HostStatus.NORMAL
            }
            host_list.append(h)
        return host_list

    def list_storage_host_groups(self, storage_id):
        host_groups = self.rest_call(self.REST_HOST_GROUP_URL)
        host_group_list = []
        storage_host_grp_relation_list = []
        for hgroup in (host_groups or []):
            hgroup_id = hgroup.get('id')
            hg = {
                'native_storage_host_group_id': hgroup_id,
                'name': hgroup.get('name'),
                'description': hgroup.get('description') if
                hgroup.get('description') else '',
                'storage_id': storage_id
            }
            host_group_list.append(hg)
            for host in (hgroup.get('hosts') or []):
                host_relation = {
                    'native_storage_host_group_id': hgroup_id,
                    'storage_id': storage_id,
                    'native_storage_host_id': host.get('id')
                }
                storage_host_grp_relation_list.append(host_relation)
        result = {
            'storage_host_groups': host_group_list,
            'storage_host_grp_host_rels': storage_host_grp_relation_list
        }
        return result

    def list_volume_groups(self, storage_id):
        volume_groups = self.rest_call(self.REST_VOLUME_GROUP_URL)
        vol_group_list = []
        vol_grp_vol_relation_list = []
        for volume_group in volume_groups:
            volume_group_id = volume_group.get('id')
            vol_g = {
                'name': volume_group.get('name'),
                'storage_id': storage_id,
                'native_volume_group_id': volume_group_id,
                'description': volume_group.get('description')
                if volume_group.get('description') else ''
            }
            vol_group_list.append(vol_g)
            for volumes in (volume_group.get('volumes') or []):
                volume_group_relation = {
                    'storage_id': storage_id,
                    'native_volume_group_id': volume_group_id,
                    'native_volume_id': volumes.get('id')
                }
                vol_grp_vol_relation_list.append(volume_group_relation)
        result = {
            'volume_groups': vol_group_list,
            'vol_grp_vol_rels': vol_grp_vol_relation_list
        }
        return result

    def list_masking_views(self, storage_id):
        list_masking_views = []
        volume_mapping = self.rest_call(self.REST_HOST_VOLUME_MAPPING_URL)
        for mapping in volume_mapping:
            native_masking_view_id = mapping.get('id')
            host_group_id = mapping.get('host_group_id')
            host_id = mapping.get('host_id')
            view = {
                'native_masking_view_id': native_masking_view_id,
                'name': native_masking_view_id,
                'native_volume_id': mapping.get('volume_id'),
                'storage_id': storage_id
            }
            if host_group_id:
                view['native_storage_host_group_id'] = host_group_id
            if host_id:
                view['native_storage_host_id'] = host_id
            list_masking_views.append(view)
        return list_masking_views

    def get_storage_metrics(self, storage_id, resource_metrics, start_time,
                            end_time):
        storage_metrics = []
        clusters = self.rest_call(self.REST_CLUSTER_URL)
        if not clusters:
            return storage_metrics
        cluster = clusters[consts.DigitalConstant.ZERO]
        cluster_id = cluster.get('id')
        cluster_name = cluster.get('name')
        if not cluster_id or not cluster_name:
            return storage_metrics
        data = {'entity': consts.PERFORMANCE_METRICS_BY_CLUSTER,
                'entity_id': cluster_id,
                'interval': consts.PERFORMANCE_METRICS_INTERVAL}
        packaging_data = self.package_data(data, end_time, start_time)
        storage_metrics = self.set_metrics_data(
            cluster.get('global_id'), cluster_name, packaging_data,
            resource_metrics, constants.ResourceType.STORAGE, storage_id)
        return storage_metrics

    def get_pool_metrics(self, storage_id, resource_metrics, start_time,
                         end_time):
        pool_metrics_list = []
        appliances = self.rest_call(self.REST_APPLIANCE_URL)
        for appliance in appliances:
            pool_id = appliance.get('id')
            pool_name = appliance.get('name')
            if not pool_id or not pool_name:
                continue
            data = {'entity': consts.PERFORMANCE_METRICS_BY_APPLIANCE,
                    'entity_id': pool_id,
                    'interval': consts.PERFORMANCE_METRICS_INTERVAL}
            packaging_data = self.package_data(data, end_time, start_time)
            pool_metrics = self.set_metrics_data(
                pool_id, pool_name, packaging_data, resource_metrics,
                constants.ResourceType.STORAGE_POOL, storage_id)
            pool_metrics_list.extend(pool_metrics)
        return pool_metrics_list

    def get_volume_metrics(self, storage_id, resource_metrics, start_time,
                           end_time):
        volume_metrics_list = []
        volumes = self.rest_call(self.REST_VOLUME_URL)
        for volume in volumes:
            volume_id = volume.get('id')
            volume_name = volume.get('name')
            if not volume_id or not volume_name:
                continue
            data = {'entity': consts.PERFORMANCE_METRICS_BY_VOLUME,
                    'entity_id': volume_id,
                    'interval': consts.PERFORMANCE_METRICS_INTERVAL}
            packaging_data = self.package_data(data, end_time, start_time)
            volume_metrics = self.set_metrics_data(
                volume_id, volume_name, packaging_data, resource_metrics,
                constants.ResourceType.VOLUME, storage_id)
            volume_metrics_list.extend(volume_metrics)
        return volume_metrics_list

    def get_controllers_metrics(self, storage_id, resource_metrics, start_time,
                                end_time):
        controllers_metrics_list = []
        controller_dict = self.get_node_hardware()
        controllers = self.rest_call(self.REST_NODE_URL)
        for controller in controllers:
            controller_id = controller.get('id')
            if not controller_id:
                continue
            hardware_id, hardware_name = self.get_resource(controller,
                                                           controller_dict)
            if not hardware_id:
                LOG.info('controllers performance: Unexpected data')
                continue
            data = {'entity': consts.PERFORMANCE_METRICS_BY_NODE,
                    'entity_id': controller_id,
                    'interval': consts.PERFORMANCE_METRICS_INTERVAL}
            packaging_data = self.package_data(data, end_time, start_time)
            controllers_metrics = self.set_metrics_data(
                hardware_id, hardware_name, packaging_data, resource_metrics,
                constants.ResourceType.CONTROLLER, storage_id)
            controllers_metrics_list.extend(controllers_metrics)
        return controllers_metrics_list

    @staticmethod
    def get_resource(controller, controller_dict):
        appliance_id = controller.get('appliance_id')
        slot = controller.get('slot')
        hardware = controller_dict.get(f'{appliance_id}{slot}', {})
        hardware_id = hardware.get('id')
        full_name = hardware.get('name')
        if full_name:
            hardware_name = full_name.split('-')[
                consts.DigitalConstant.MINUS_ONE]
        else:
            hardware_name = hardware_id
        return hardware_id, hardware_name

    def get_node_hardware(self):
        hardware_dict = {}
        hardware_list = self.rest_call(self.REST_HARDWARE_URL)
        for hardware in hardware_list:
            lifecycle_state = hardware.get('lifecycle_state')
            if consts.CHARACTER_NODE != hardware.get('type') or \
                    lifecycle_state == consts.CHARACTER_EMPTY:
                continue
            slot = hardware.get('slot')
            appliance_id = hardware.get('appliance_id')
            key = f'{appliance_id}{slot}'
            hardware_dict[key] = hardware
        return hardware_dict

    def get_fc_port_metrics(self, storage_id, resource_metrics, start_time,
                            end_time):
        fc_port_metrics_list = []
        fc_ports = self.rest_call(self.REST_FC_PORT_URL)
        for fc_port in fc_ports:
            fc_port_id = fc_port.get('id')
            fc_port_name = fc_port.get('name')
            if not fc_port_id or not fc_port_name:
                continue
            data = {'entity': consts.PERFORMANCE_METRICS_BY_FE_FC_PORT,
                    'entity_id': fc_port_id,
                    'interval': consts.PERFORMANCE_METRICS_INTERVAL}
            packaging_data = self.package_data(data, end_time, start_time)
            fc_port_metrics = self.set_metrics_data(
                fc_port_id, fc_port_name, packaging_data, resource_metrics,
                constants.ResourceType.PORT, storage_id)
            fc_port_metrics_list.extend(fc_port_metrics)
        return fc_port_metrics_list

    def get_file_system_metrics(self, storage_id, resource_metrics, start_time,
                                end_time):
        file_system_metrics_list = []
        file_systems = self.rest_call(self.REST_FILE_SYSTEM_URL)
        for file_system in file_systems:
            file_system_id = file_system.get('id')
            file_system_name = file_system.get('name')
            if not file_system_id or not file_system_name:
                continue
            data = {'entity': consts.PERFORMANCE_METRICS_BY_FILE_SYSTEM,
                    'entity_id': file_system_id,
                    'interval': consts.PERFORMANCE_METRICS_INTERVAL}
            packaging_data = self.package_data(data, end_time, start_time)
            file_system_metrics = self.set_metrics_data(
                file_system_id, file_system_name, packaging_data,
                resource_metrics, constants.ResourceType.FILESYSTEM,
                storage_id)
            file_system_metrics_list.extend(file_system_metrics)
        return file_system_metrics_list

    @staticmethod
    def set_metrics_data(resource_id, resource_name, packaging_data,
                         resource_metrics, resource_type, storage_id):
        metrics_list = []
        for resource_key in resource_metrics.keys():
            labels = {
                'storage_id': storage_id,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'resource_name': resource_name,
                'type': 'RAW',
                'unit': resource_metrics[resource_key]['unit']
            }
            resource_value = {}
            for about_timestamp in packaging_data.keys():
                metrics_data = packaging_data.get(about_timestamp)
                resource_value[about_timestamp] = \
                    metrics_data.get(resource_key)
            if resource_value:
                metrics_res = constants.metric_struct(
                    name=resource_key, labels=labels, values=resource_value)
                metrics_list.append(metrics_res)
        return metrics_list

    def package_data(self, data, end_time, start_time):
        perf_data = self.rest_call(self.REST_GENERATE_URL, data, 'POST')
        packaging_data = {}
        duplicate = set()
        for perf in perf_data:
            timestamp = perf.get('timestamp')
            time_difference = self.get_time_difference()
            timestamp_s = int(
                datetime.datetime.strptime(timestamp, consts.PERF_TIME_FORMAT)
                .timestamp() + time_difference)
            repeat_count = perf.get('repeat_count')
            if repeat_count > consts.DigitalConstant.ONE:
                repeat_timestamp_s =\
                    (repeat_count - consts.DigitalConstant.ONE)\
                    * consts.PERF_INTERVAL
                count_timestamp_s = timestamp_s + repeat_timestamp_s
                count_timestamp_ms = count_timestamp_s * units.k
                if start_time > count_timestamp_ms:
                    continue
            for count in range(consts.DigitalConstant.ZERO, repeat_count):
                count_timestamp_s = timestamp_s + count * consts.PERF_INTERVAL
                count_timestamp_ms = count_timestamp_s * units.k
                about_timestamp = \
                    int(count_timestamp_s / consts.DigitalConstant.SIXTY) \
                    * consts.DigitalConstant.SIXTY * units.k
                if count_timestamp_ms < start_time or \
                        count_timestamp_ms >= end_time \
                        or about_timestamp in duplicate:
                    continue
                duplicate.add(about_timestamp)
                cpu_utilization = perf.get('io_workload_cpu_utilization')
                avg_io_size = perf.get('avg_io_size')
                metrics_d = {
                    'iops': Decimal(str(perf.get('total_iops'))).quantize(
                        Decimal('0'), rounding="ROUND_HALF_UP"),
                    "readIops": Decimal(str(perf.get('read_iops'))).quantize(
                        Decimal('0'), rounding="ROUND_HALF_UP"),
                    "writeIops": Decimal(str(perf.get('write_iops'))).quantize(
                        Decimal('0'), rounding="ROUND_HALF_UP"),
                    "throughput": round(
                        perf.get('total_bandwidth') / units.Mi, 3),
                    "readThroughput": round(
                        perf.get('read_bandwidth') / units.Mi, 3),
                    "writeThroughput": round(
                        perf.get('write_bandwidth') / units.Mi, 3),
                    "responseTime": round(
                        perf.get('avg_latency') / units.k, 3),
                    "readResponseTime": round(
                        perf.get('avg_read_latency') / units.k, 3),
                    "writeResponseTime": round(
                        perf.get('avg_write_latency') / units.k, 3),
                    "ioSize": round(perf.get('avg_size') / units.Ki, 3) if
                    avg_io_size is None else round(avg_io_size / units.Ki, 3),
                    "readIoSize": round(
                        perf.get('avg_read_size') / units.Ki, 3),
                    "writeIoSize": round(
                        perf.get('avg_write_size') / units.Ki, 3),
                    "cpuUsage": Decimal(str(cpu_utilization)).quantize(
                        Decimal('0.000'), rounding="ROUND_HALF_UP")
                    if cpu_utilization else '',
                    'time': about_timestamp
                }
                packaging_data[about_timestamp] = metrics_d
        return packaging_data

    def get_system_time(self):
        clusters = self.rest_call(self.REST_CLUSTER_URL)
        if clusters:
            cluster = clusters[consts.DigitalConstant.ZERO]
            system_time = cluster.get('system_time')
            time_difference = self.get_time_difference()
            timestamp_s = datetime.datetime.strptime(
                system_time, consts.SYSTEM_TIME_FORMAT).timestamp()
            timestamp = int((timestamp_s + time_difference) * units.k)\
                if system_time else None
            return timestamp

    def list_filesystems(self, storage_id):
        list_filesystems = []
        file_system_list = self.rest_call(self.REST_FILE_SYSTEM_URL)
        for file_system in file_system_list:
            fs_type = file_system.get('filesystem_type')
            total_capacity = int(file_system.get('size_total'))
            used_capacity = int(file_system.get('size_used'))
            file_dict = {
                'native_filesystem_id': file_system.get('id'),
                'name': file_system.get('name'),
                'type': consts.FS_TYPE_MAP.get(fs_type, constants.FSType.THIN),
                'status': constants.FilesystemStatus.NORMAL,
                'storage_id': storage_id,
                'total_capacity': total_capacity,
                'used_capacity': used_capacity,
                'free_capacity': total_capacity - used_capacity,
                'security_mode': consts.FS_SECURITY_MODE_MAP.get(
                    file_system.get('access_policy'),
                    constants.NASSecurityMode.MIXED)
            }
            list_filesystems.append(file_dict)
        return list_filesystems

    def list_qtrees(self, storage_id):
        list_qtrees = []
        nas_dict = {}
        nas_server_list = self.rest_call(self.REST_NAS_SERVER_URL)
        for nas_server in nas_server_list:
            nas_server_id = nas_server.get('id')
            nas_server_name = nas_server.get('name')
            nas_dict[nas_server_id] = nas_server_name
        file_system_list = self.rest_call(self.REST_FILE_SYSTEM_URL)
        for file_system in file_system_list:
            file_system_id = file_system.get('id')
            file_system_name = file_system.get('name')
            nas_server_id = file_system.get('nas_server_id')
            nas_server_name = nas_dict.get(nas_server_id)
            native_qtree_id = f'{nas_server_id}{file_system_id}'
            name = f'NAS Servers Name:{nas_server_name}' \
                   f'@File Systems Name:{file_system_name}'
            qtrees_dict = {
                'native_qtree_id': hashlib.md5(
                    native_qtree_id.encode()).hexdigest(),
                'name': name,
                'storage_id': storage_id,
                'native_filesystem_id': file_system_id,
                'path': name,
                'security_mode': consts.FS_SECURITY_MODE_MAP.get(
                    file_system.get('access_policy'),
                    constants.NASSecurityMode.MIXED)
            }
            list_qtrees.append(qtrees_dict)
        return list_qtrees

    def list_quotas(self, storage_id):
        list_quotas = []
        qtree_dict = self.get_qtree_id(storage_id)
        tree_quota_list = self.rest_call(self.REST_FILE_TREE_QUOTA_URL)
        for tree_quota in tree_quota_list:
            file_system_id = tree_quota.get('file_system_id')
            tree_quotas_dict = {
                'native_quota_id': tree_quota.get('id'),
                'type': constants.QuotaType.TREE,
                'storage_id': storage_id,
                'native_filesystem_id': file_system_id,
                'native_qtree_id': qtree_dict.get(file_system_id),
                'capacity_hard_limit': tree_quota.get('hard_limit'),
                'capacity_soft_limit': tree_quota.get('soft_limit'),
                'used_capacity': tree_quota.get('size_used')
            }
            list_quotas.append(tree_quotas_dict)
        user_quota_list = self.rest_call(self.REST_FILE_USER_QUOTA_URL)
        for user_quota in user_quota_list:
            user_group_name = user_quota.get('unix_name')
            windows_name = user_quota.get('windows_name')
            windows_sid = user_quota.get('windows_sid')
            uid = user_quota.get('uid')
            if windows_name:
                user_group_name = windows_name
            if windows_sid:
                user_group_name = windows_sid
            if uid:
                user_group_name = uid
            file_system_id = user_quota.get('file_system_id')
            user_quotas_dict = {
                'native_quota_id': user_quota.get('id'),
                'type': constants.QuotaType.USER,
                'storage_id': storage_id,
                'native_filesystem_id': user_quota.get('file_system_id'),
                'native_qtree_id': qtree_dict.get(file_system_id),
                'capacity_hard_limit': user_quota.get('hard_limit'),
                'capacity_soft_limit': user_quota.get('soft_limit'),
                'used_capacity': user_quota.get('size_used'),
                'user_group_name': user_group_name
            }
            list_quotas.append(user_quotas_dict)
        return list_quotas

    def get_qtree_id(self, storage_id):
        qtree_dict = {}
        list_qtrees = self.list_qtrees(storage_id)
        for qtrees in list_qtrees:
            native_qtree_id = qtrees.get('native_qtree_id')
            native_filesystem_id = qtrees.get('native_filesystem_id')
            qtree_dict[native_filesystem_id] = native_qtree_id
        return qtree_dict

    def list_shares(self, storage_id):
        list_shares = []
        qtree_dict = self.get_qtree_id(storage_id)
        nfs_list = self.rest_call(self.REST_NFS_EXPORT_URL)
        for nfs in nfs_list:
            file_system_id = nfs.get('file_system', {}).get('id')
            nfs_dict = {
                'native_share_id': nfs.get('id'),
                'name': nfs.get('name'),
                'storage_id': storage_id,
                'native_filesystem_id': file_system_id,
                'native_qtree_id': qtree_dict.get(file_system_id),
                'protocol': constants.ShareProtocol.NFS,
                'path': nfs.get('path')
            }
            list_shares.append(nfs_dict)
        shares_list = self.rest_call(self.REST_SMB_SHARE_URL)
        for shares in shares_list:
            shares_path = shares.get('path')
            file_system_id = shares.get('file_system_id')
            shares_dict = {
                'native_share_id': shares.get('id'),
                'name': shares.get('name'),
                'storage_id': storage_id,
                'native_filesystem_id': file_system_id,
                'native_qtree_id': qtree_dict.get(file_system_id),
                'protocol': constants.ShareProtocol.CIFS,
                'path': shares_path
            }
            list_shares.append(shares_dict)
        return list_shares
