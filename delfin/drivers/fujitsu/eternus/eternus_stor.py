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
import re

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception, utils
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.fujitsu.eternus import cli_handler, consts
from delfin.drivers.fujitsu.eternus.consts import DIGITAL_CONSTANT
from delfin.drivers.utils.tools import Tools
from delfin.i18n import _

LOG = log.getLogger(__name__)


class EternusDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cli_handler = cli_handler.CliHandler(**kwargs)
        self.login = self.cli_handler.login()

    def list_volumes(self, context):
        list_volumes = self.get_volumes_model()
        if not list_volumes:
            list_volumes = self.get_volumes_old()
        return list_volumes

    def get_volumes_model(self):
        list_volumes = []
        volumes_str = self.cli_handler.exec_command(
            consts.GET_LIST_VOLUMES_MODE_UID)
        volume_id_dict = self.cli_handler.get_volumes_type(
            command=consts.GET_LIST_VOLUMES_TYPE_TPV)
        volume_id_dict = self.cli_handler.get_volumes_type(
            volume_id_dict, consts.GET_LIST_VOLUMES_TYPE_TPV)
        block = True
        if volumes_str:
            volumes_arr = volumes_str.replace('\r', '').split('\n')
            for volumes_row_str in volumes_arr:
                if not volumes_row_str or \
                        consts.CLI_STR in volumes_row_str:
                    continue
                if consts.SPECIAL_CHARACTERS_TWO in volumes_row_str:
                    block = False
                    continue
                if block:
                    continue
                volumes_row_arr = volumes_row_str.split()
                volume_id = volumes_row_arr[
                    consts.GET_VOLUMES_MODEL_VOLUME_ID_COUNT]
                type_capacity = volume_id_dict.get(volume_id, {})
                volume_type = type_capacity.get('type',
                                                constants.VolumeType.THICK)
                used_capacity = type_capacity.get('used_capacity',
                                                  DIGITAL_CONSTANT.ZERO_INT)
                volume_name = volumes_row_arr[
                    consts.GET_VOLUMES_MODEL_VOLUME_NAME_COUNT]
                volume_status = volumes_row_arr[
                    consts.GET_VOLUMES_MODEL_VOLUME_STATUS_COUNT]
                pool_id = volumes_row_arr[
                    consts.GET_VOLUMES_MODEL_POOL_ID_COUNT]
                total_capacity = \
                    int(volumes_row_arr[consts.
                        GET_VOLUMES_MODEL_TOTAL_CAPACITY_COUNT]) * units.Mi
                wwn = volumes_row_arr[consts.GET_VOLUMES_MODEL_WWN_COUNT]
                volume = {
                    'name': volume_name,
                    'storage_id': self.storage_id,
                    'status': consts.LIST_VOLUMES_STATUS_MAP.get(
                        volume_status),
                    'native_volume_id': volume_id,
                    'native_storage_pool_id': pool_id,
                    'type': volume_type,
                    'wwn': wwn,
                    'total_capacity': total_capacity,
                    'used_capacity': used_capacity,
                    'free_capacity': total_capacity - used_capacity
                }
                list_volumes.append(volume)
        return list_volumes

    def get_volumes_old(self):
        list_volumes = []
        volumes_str = self.cli_handler.exec_command(consts.GET_LIST_VOLUMES)
        volumes_arr = volumes_str.split('\n')
        if len(volumes_arr) < consts.VOLUMES_LENGTH:
            return list_volumes
        for volumes_num in range(consts.VOLUMES_CYCLE, len(volumes_arr)):
            volumes_row_str = volumes_arr[volumes_num]
            if not volumes_row_str or \
                    consts.CLI_STR in volumes_row_str.strip():
                continue
            volumes_row_arr = volumes_row_str.split()
            volume_id = volumes_row_arr[consts.VOLUME_ID_COUNT]
            volume_name = volumes_row_arr[consts.VOLUME_NAME_COUNT]
            volume_status = volumes_row_arr[consts.VOLUME_STATUS_COUNT]
            volume_type = volumes_row_arr[consts.VOLUME_TYPE_COUNT]
            pool_id = volumes_row_arr[consts.NATIVE_STORAGE_POOL_ID_COUNT]
            total_capacity = volumes_row_arr[consts.TOTAL_CAPACITY_COUNT]
            volume_results = {
                'name': volume_name,
                'storage_id': self.storage_id,
                'status': consts.LIST_VOLUMES_STATUS_MAP.get(
                    volume_status),
                'native_volume_id': volume_id,
                'native_storage_pool_id': pool_id,
                'type': constants.VolumeType.THIN if
                volume_type and consts.VOLUME_TYPE_OPEN in volume_type else
                constants.VolumeType.THICK,
                'total_capacity': int(total_capacity) * units.Mi,
                'used_capacity': consts.DEFAULT_USED_CAPACITY,
                'free_capacity': consts.DEFAULT_FREE_CAPACITY
            }
            list_volumes.append(volume_results)
        return list_volumes

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        pass

    def get_storage(self, context):
        storage_name_dict = self.cli_handler.common_data_encapsulation(
            consts.GET_STORAGE_NAME)
        storage_name = storage_name_dict.get('Name')
        storage_description = storage_name_dict.get('Description')
        storage_location = storage_name_dict.get('Installation Site')

        enclosure_status = self.cli_handler.common_data_encapsulation(
            consts.GET_ENCLOSURE_STATUS)
        storage_model = enclosure_status.get('Model Name')
        storage_serial_number = enclosure_status.get('Serial Number')
        storage_firmware_version = enclosure_status.get('Firmware Version')

        storage_status_dict = self.cli_handler.common_data_encapsulation(
            consts.GET_STORAGE_STATUS)
        storage_status = consts.STORAGE_STATUS_MAP.get(
            storage_status_dict.get('Summary Status'))

        raw_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        list_disks = self.list_disks(context)
        if list_disks:
            for disks in list_disks:
                raw_capacity += disks.get('capacity',
                                          consts.DIGITAL_CONSTANT.ZERO_INT)
        total_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        used_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        free_capacity = consts.DIGITAL_CONSTANT.ZERO_INT
        list_storage_pools = self.list_storage_pools(context)
        if list_storage_pools:
            for pools in list_storage_pools:
                total_capacity += pools.get('total_capacity')
                used_capacity += pools.get('used_capacity')
                free_capacity += pools.get('free_capacity')
        storage = {
            'name': storage_name,
            'vendor': consts.GET_STORAGE_VENDOR,
            'description': storage_description,
            'model': storage_model,
            'status': storage_status,
            'serial_number': storage_serial_number,
            'firmware_version': storage_firmware_version,
            'location': storage_location,
            'raw_capacity': raw_capacity,
            'total_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': free_capacity
        }
        return storage

    def list_controllers(self, context):
        controllers = self.cli_handler.get_controllers()
        controllers_status = self.cli_handler.common_data_encapsulation(
            consts.GET_STORAGE_CONTROLLER_STATUS)
        controller_list = []
        for controller in (controllers or []):
            name = controller.get('name')
            status = constants.ControllerStatus.FAULT
            if controllers_status and controllers_status.get(name):
                status_value = controllers_status.get(name)
                if status_value and \
                        consts.CONTROLLER_STATUS_NORMAL_KEY in status_value:
                    status = constants.ControllerStatus.NORMAL
            controller_model = {
                'name': controller.get('name'),
                'storage_id': self.storage_id,
                'native_controller_id': controller.get('Serial Number'),
                'status': status,
                'location': controller.get('name'),
                'soft_version': controller.get('Hard Revision'),
                'cpu_info': controller.get('CPU Clock'),
                'memory_size': str(int(
                    Tools.get_capacity_size(controller.get('Memory Size'))))
            }
            controller_list.append(controller_model)
        return controller_list

    def list_disks(self, context):
        try:
            disk_list = \
                self.cli_handler.format_data(
                    consts.GET_DISK_COMMAND,
                    self.storage_id,
                    self.cli_handler.format_disks,
                    False)
            return disk_list
        except Exception as e:
            error = six.text_type(e)
            LOG.error("Failed to get disk from fujitsu eternus %s" % error)
            raise exception.InvalidResults(error)

    def list_ports(self, context):
        port_list = self.cli_handler.format_data(
            consts.GET_PORT_FC_PARAMETERS, self.storage_id,
            self.cli_handler.format_fc_ports, True)
        ports_status = self.cli_handler.get_ports_status()
        for port in port_list:
            name = port.get('name')
            status_dict = ports_status.get(name, {})
            if status_dict:
                link_status = status_dict.get('Link Status')
                connection_status = constants.PortConnectionStatus.UNKNOWN
                if 'Gbit/s' in link_status:
                    reality = link_status.split()[0].replace('Gbit/s', '')
                    speed = int(reality) * units.G
                    port['speed'] = speed
                if 'Link Up' in link_status:
                    connection_status = \
                        constants.PortConnectionStatus.CONNECTED
                if 'Link Down' in link_status:
                    connection_status = \
                        constants.PortConnectionStatus.DISCONNECTED

                status_keys = status_dict.keys()
                status_dicts = {}
                for status_key in status_keys:
                    if status_key and 'Status/Status Code' in status_key:
                        status_dicts['Status/Status Code'] = status_dict.get(
                            status_key)
                    if status_key and status_key in 'Port WWN':
                        status_dicts['WWN'] = status_dict.get(status_key)
                status = status_dicts.get('Status/Status Code')
                health_status = constants.PortHealthStatus.UNKNOWN
                if 'Normal' in status or 'normal' in status:
                    health_status = constants.PortHealthStatus.NORMAL
                elif 'Unconnected' in status or 'unconnected' in status:
                    health_status = constants.PortHealthStatus.UNKNOWN
                elif 'Error' in status or 'error' in status:
                    health_status = constants.PortHealthStatus.ABNORMAL
                port['connection_status'] = connection_status
                port['wwn'] = status_dicts.get('WWN')
                port['health_status'] = health_status
        return port_list

    def list_storage_pools(self, context):
        pool_list = self.get_list_pools()
        if not pool_list:
            pool_list = self.get_list_pools_old(pool_list)
        return pool_list

    def get_list_pools_old(self, pool_list):
        pools_str = self.cli_handler.exec_command(consts.GET_STORAGE_POOL)
        if not pools_str:
            return pool_list
        pools_row_str = pools_str.split('\n')
        if len(pools_row_str) < consts.POOL_LENGTH:
            return pool_list
        for pools_row_num in range(consts.POOL_CYCLE, len(pools_row_str)):
            pools_row_arr = pools_row_str[pools_row_num].strip()
            if pools_row_arr in consts.CLI_STR or \
                    pools_row_arr in consts.SPECIAL_CHARACTERS_ONE:
                continue
            pools_arr = pools_row_arr.split()
            pool_id = pools_arr[consts.POOL_ID_COUNT]
            pool_name = pools_arr[consts.POOL_NAME_COUNT]
            pool_status = consts.STORAGE_POOL_STATUS_MAP.get(
                pools_arr[consts.POOL_STATUS_COUNT],
                constants.StoragePoolStatus.UNKNOWN)
            try:
                total_capacity = int(
                    pools_arr[consts.POOL_TOTAL_CAPACITY_COUNT]) * units.Mi
                free_capacity = int(
                    pools_arr[consts.POOL_FREE_CAPACITY_COUNT]) * units.Mi
            except Exception as e:
                LOG.info('Conversion digital exception:%s' % six.text_type(e))
                return pool_list
            pool_model = {
                'name': pool_name,
                'storage_id': self.storage_id,
                'native_storage_pool_id': str(pool_id),
                'status': pool_status,
                'storage_type': constants.StorageType.BLOCK,
                'total_capacity': total_capacity,
                'used_capacity': total_capacity - free_capacity,
                'free_capacity': free_capacity
            }
            pool_list.append(pool_model)
        return pool_list

    def get_list_pools(self):
        pool_list = []
        pools = self.cli_handler.get_volumes_or_pool(
            consts.GET_STORAGE_POOL_CSV, consts.POOL_TITLE_PATTERN)
        for pool in (pools or []):
            free_cap = float(
                pool.get("freecapacity(mb)")) * units.Mi
            total_cap = float(
                pool.get("totalcapacity(mb)")) * units.Mi
            used_cap = total_cap - free_cap
            status = consts.STORAGE_POOL_STATUS_MAP.get(
                pool.get('status'),
                constants.StoragePoolStatus.UNKNOWN)
            pool_model = {
                'name': pool.get('raidgroupname'),
                'storage_id': self.storage_id,
                'native_storage_pool_id': str(pool.get('raidgroupno.')),
                'status': status,
                'storage_type': constants.StorageType.BLOCK,
                'total_capacity': int(total_cap),
                'used_capacity': int(used_cap),
                'free_capacity': int(free_cap)
            }
            pool_list.append(pool_model)
        return pool_list

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        pass

    def list_alerts(self, context, query_para=None):
        list_alert = self.cli_handler.get_alerts(
            consts.SHOW_EVENTS_SEVERITY_WARNING, query_para)
        list_alert = self.cli_handler.get_alerts(
            consts.SHOW_EVENTS_SEVERITY_ERROR, query_para, list_alert)
        if not list_alert:
            list_alert = self.cli_handler.get_alerts(
                consts.SHOW_EVENTS_LEVEL_WARNING, query_para)
            list_alert = self.cli_handler.get_alerts(
                consts.SHOW_EVENTS_LEVEL_ERROR, query_para, list_alert)
        return list_alert

    @staticmethod
    def parse_alert(context, alert):
        try:
            if consts.PARSE_ALERT_DESCRIPTION in alert.keys():
                alert_model = dict()
                alert_model['alert_id'] = alert.get(
                    consts.PARSE_ALERT_ALERT_ID)
                alert_model['severity'] = consts.PARSE_ALERT_SEVERITY_MAP.get(
                    alert.get(consts.PARSE_ALERT_SEVERITY),
                    constants.Severity.NOT_SPECIFIED)
                alert_model['category'] = constants.Category.FAULT
                alert_model['occur_time'] = utils.utcnow_ms()
                alert_model['description'] = alert.get(
                    consts.PARSE_ALERT_DESCRIPTION)
                alert_model['location'] = '{}{}'.format(alert.get(
                    consts.PARSE_ALERT_LOCATION),
                    alert.get(consts.PARSE_ALERT_COMPONENT))
                alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                alert_model['alert_name'] = alert.get(
                    consts.PARSE_ALERT_DESCRIPTION)
                alert_model['match_key'] = hashlib.md5(str(alert.get(
                    consts.PARSE_ALERT_ALERT_ID)).encode()).hexdigest()
                return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing"))
            raise exception.InvalidResults(msg)

    @staticmethod
    def get_access_url():
        return 'https://{ip}'

    def list_storage_host_initiators(self, ctx):
        initiator_list = []
        host_status = self.get_host_status()
        host_fc_list = self.get_data(consts.GET_HOST_WWN_NAMES,
                                     consts.HOST_TOTAL)
        for host_fc in (host_fc_list or []):
            if len(host_fc) < consts.HOST_TOTAL:
                continue
            fc_name = host_fc[consts.HOST_NAME_COUNT]
            fc_wwn = host_fc[consts.HOST_WWN_COUNT]
            state = host_status.get(fc_name)
            initiator_item = {
                'name': fc_wwn,
                'storage_id': self.storage_id,
                'native_storage_host_initiator_id': fc_wwn,
                'wwn': fc_wwn,
                'status': constants.HostStatus.NORMAL if
                state is not None and state in
                consts.HOST_PATH_STATUS_SPECIFIC_TWO else
                constants.HostStatus.OFFLINE,
                'native_storage_host_id': fc_name,
                'type': constants.InitiatorType.FC
            }
            initiator_list.append(initiator_item)
        host_iscsi_list = self.get_iscsi_host()
        for host_iscsi in (host_iscsi_list or []):
            iscsi_name = host_iscsi.get('name')
            state = host_status.get(iscsi_name)
            initiator_item = {
                "name": host_iscsi.get('iqn'),
                "storage_id": self.storage_id,
                "native_storage_host_initiator_id": host_iscsi.get('iqn'),
                "wwn": host_iscsi.get('iqn'),
                "status": constants.HostStatus.NORMAL if
                state is not None and state in
                consts.HOST_PATH_STATUS_SPECIFIC_TWO else
                constants.HostStatus.OFFLINE,
                "native_storage_host_id": iscsi_name,
                'type': constants.InitiatorType.ISCSI,
                'alias': host_iscsi.get('alias')
            }
            initiator_list.append(initiator_item)
        host_sas_list = self.get_data(consts.GET_HOST_SAS_ADDRESSES,
                                      consts.HOST_SAS_FIVE)
        for host_sas in (host_sas_list or []):
            if len(host_sas) < consts.HOST_SAS_FIVE:
                continue
            sas_name = host_sas[consts.HOST_SAS_ONE]
            sas_address = host_sas[consts.HOST_SAS_TWO]
            state = host_status.get(sas_name)
            initiator_item = {
                "name": sas_address,
                "storage_id": self.storage_id,
                "native_storage_host_initiator_id": sas_address,
                "wwn": sas_address,
                "status": constants.HostStatus.NORMAL if
                state is not None and state in
                consts.HOST_PATH_STATUS_SPECIFIC_TWO else
                constants.HostStatus.OFFLINE,
                "native_storage_host_id": sas_name,
                'type': constants.InitiatorType.SAS
            }
            initiator_list.append(initiator_item)
        return initiator_list

    def list_storage_hosts(self, ctx):
        host_list = []
        host_status = self.get_host_status()
        host_fc_list = self.get_data(consts.GET_HOST_WWN_NAMES,
                                     consts.HOST_TOTAL)
        for host_fc in (host_fc_list or []):
            if len(host_fc) < consts.HOST_TOTAL:
                continue
            fc_name = host_fc[consts.HOST_NAME_COUNT]
            os = host_fc[consts.HOST_TYPE_COUNT].lower()
            state = host_status.get(fc_name)
            host_d = {
                "name": fc_name,
                "storage_id": self.storage_id,
                "native_storage_host_id": fc_name,
                "os_type": consts.HOST_OS_TYPES_MAP.get(
                    os, constants.HostOSTypes.UNKNOWN),
                "status": constants.HostStatus.NORMAL if
                state is not None and state in
                consts.HOST_PATH_STATUS_SPECIFIC_TWO else
                constants.HostStatus.OFFLINE
            }
            host_list.append(host_d)

        host_iscsi_list = self.get_iscsi_host()
        for host_iscsi in (host_iscsi_list or []):
            iscsi_name = host_iscsi.get('name')
            state = host_status.get(iscsi_name)
            os = host_iscsi.get('os')
            os = os.lower() if os else None
            host_d = {
                "name": iscsi_name,
                "storage_id": self.storage_id,
                "native_storage_host_id": iscsi_name,
                "os_type": consts.HOST_OS_TYPES_MAP.get(
                    os, constants.HostOSTypes.UNKNOWN),
                "status": constants.HostStatus.NORMAL if
                state is not None and state in
                consts.HOST_PATH_STATUS_SPECIFIC_TWO else
                constants.HostStatus.OFFLINE,
                'ip_address': host_iscsi.get('address')
            }
            host_list.append(host_d)

        host_sas_list = self.get_data(consts.GET_HOST_SAS_ADDRESSES,
                                      consts.HOST_SAS_FIVE)
        for host_sas in (host_sas_list or []):
            if len(host_sas) < consts.HOST_SAS_FIVE:
                continue
            sas_name = host_sas[consts.HOST_SAS_ONE]
            sas_os = host_sas[consts.HOST_SAS_FOUR].lower()
            state = host_status.get(sas_name)
            host_d = {
                "name": sas_name,
                "storage_id": self.storage_id,
                "native_storage_host_id": sas_name,
                "os_type": consts.HOST_OS_TYPES_MAP.get(
                    sas_os, constants.HostOSTypes.UNKNOWN),
                "status": constants.HostStatus.NORMAL if
                state is not None and state in
                consts.HOST_PATH_STATUS_SPECIFIC_TWO else
                constants.HostStatus.OFFLINE
            }
            host_list.append(host_d)
        return host_list

    def get_data(self, command, length_count):
        host_list = []
        host_str = self.cli_handler.exec_command(command)
        block = True
        length_list = []
        if host_str:
            host_arr = host_str.strip().replace('\r', '').split('\n')
            for host_row_str in (host_arr or []):
                if not host_row_str or \
                        consts.CLI_STR in host_row_str:
                    continue
                if consts.SPECIAL_CHARACTERS_TWO in host_row_str:
                    identify_list = host_row_str.split()
                    for identify in identify_list:
                        length_list.append(len(identify))
                    block = False
                    continue
                if block:
                    continue
                if len(host_row_str.split()) < length_count:
                    continue
                volume_list = []
                key_length = DIGITAL_CONSTANT.ZERO_INT
                for length_key in length_list:
                    volume = host_row_str[key_length:
                                          key_length + length_key].strip()
                    volume_list.append(volume)
                    key_length = key_length + length_key + DIGITAL_CONSTANT \
                        .ONE_INT
                host_list.append(volume_list)
        return host_list

    def get_iscsi_host(self):
        iscsi_list = []
        iscsi_ids_str = self.cli_handler.exec_command(
            consts.GET_HOST_ISCSI_NAMES)
        block = True
        if iscsi_ids_str:
            iscsi_ids_arr = iscsi_ids_str.strip().replace('\r', '').split('\n')
            for iscsi_ids_row_str in (iscsi_ids_arr or []):
                if not iscsi_ids_row_str or \
                        consts.CLI_STR in iscsi_ids_row_str:
                    continue
                if consts.HOST_PATH_STATUS_SPECIFIC_ONE in iscsi_ids_row_str:
                    block = False
                    continue
                if block:
                    continue
                iscsi_ids_row_arr = iscsi_ids_row_str.strip().split()
                if len(iscsi_ids_row_arr) < consts.HOST_ISCSI_NAMES_SEVEN:
                    continue
                details = self.get_iscsi_details(
                    iscsi_ids_row_arr[consts.HOST_ISCSI_NAMES_ZERO])
                iscsi_d = {
                    'iscsi_id': details.get('Host No.'),
                    'name': details.get('Host Name'),
                    'iqn': details.get('iSCSI Name'),
                    'alias': details.get('Alias Name'),
                    'address': None if
                    consts.HOST_ISCSI_SPECIFIC_ONE in
                    details.get('IP Address') else details.get('IP Address'),
                    'os': details.get('Host Response Name')
                }
                iscsi_list.append(iscsi_d)
        return iscsi_list

    def get_iscsi_details(self, number):
        details = {}
        iscsi_details_str = self.cli_handler.exec_command(
            consts.GET_HOST_ISCSI_NAMES_NUMBER.format(number))
        if iscsi_details_str:
            iscsi_ids_arr = iscsi_details_str.strip().replace('\r', '') \
                .split('\n')
            for row_str in (iscsi_ids_arr or []):
                if not row_str or consts.CLI_STR in row_str:
                    continue
                iscsi_details_row_arr = row_str.strip().split('   ')
                if len(iscsi_details_row_arr) < consts.HOST_ISCSI_NAMES_TWO:
                    continue
                key = row_str[:consts.HOST_ISCSI_DETAIL_EIGHTEEN].strip()
                value = row_str[consts.HOST_ISCSI_DETAIL_EIGHTEEN:].strip()
                details[key] = value
        return details

    def get_host_status(self):
        status_d = {}
        status_list = self.get_data(consts.GET_HOST_PATH_STATUS,
                                    consts.HOST_PATH_STATUS_TOTAL)
        for status_row in status_list:
            if len(status_row) < consts.HOST_PATH_STATUS_TOTAL:
                continue
            host_name = status_row[consts.HOST_PATH_STATUS_NAME]
            path_state = status_row[consts.HOST_PATH_STATUS]
            status_d[host_name] = path_state
        return status_d

    def list_storage_host_groups(self, ctx):
        host_group_list = []
        storage_id = self.storage_id
        host_group_all = self.cli_handler.exec_command(
            consts.GET_HOST_GROUPS_ALL)
        if host_group_all:
            host_group_all_arr = host_group_all.replace('\r', '').split('\n\n')
            for host_group_str in (host_group_all_arr or []):
                host_group_arr = host_group_str.split(
                    consts.HOST_GROUPS_SPECIFIC_ONE)
                host_group_row_arr = host_group_arr[
                    consts.HOST_GROUP_ZERO].strip().split('\n')
                host_group_id = None
                host_group_name = None
                block = True
                for host_group_row_str in (host_group_row_arr or []):
                    if not host_group_row_str or \
                            consts.CLI_STR in host_group_row_str:
                        continue
                    if consts.HOST_GROUPS_SPECIFIC_TWO in host_group_row_str:
                        block = False
                        continue
                    if block:
                        continue
                    host_group = host_group_row_str.split()
                    host_group_id = host_group[consts.HOST_GROUP_ZERO]
                    host_group_name = host_group[consts.HOST_GROUP_ONE]
                storage_hosts = self.get_storage_hosts(host_group_arr)
                host_g = {
                    'name': host_group_name,
                    'storage_id': storage_id,
                    'native_storage_host_group_id': host_group_id,
                    'storage_hosts': storage_hosts,
                }
                host_group_list.append(host_g)
        storage_host_grp_relation_list = []
        for storage_host_group in host_group_list:
            storage_hosts = storage_host_group.pop('storage_hosts', None)
            if not storage_hosts:
                continue
            storage_hosts = storage_hosts.split(',')

            for storage_host in storage_hosts:
                storage_host_group_relation = {
                    'storage_id': storage_id,
                    'native_storage_host_group_id': storage_host_group.get(
                        'native_storage_host_group_id'),
                    'native_storage_host_id': storage_host
                }
                storage_host_grp_relation_list \
                    .append(storage_host_group_relation)
        result = {
            'storage_host_groups': host_group_list,
            'storage_host_grp_host_rels': storage_host_grp_relation_list
        }
        return result

    @staticmethod
    def get_storage_hosts(host_group_arr):
        storage_hosts = None
        if len(host_group_arr) == consts.HOST_GROUP_TOTAL:
            host_row_arr = host_group_arr[consts.HOST_GROUP_ONE].split('\n')
            block = True
            for host_row_str in (host_row_arr or []):
                if not host_row_str or consts.CLI_STR in host_row_str:
                    continue
                if consts.HOST_GROUPS_SPECIFIC_TWO in host_row_str:
                    block = False
                    continue
                if block:
                    continue
                host_arr = host_row_str.split()
                host_id = host_arr[consts.HOST_GROUP_ONE]
                if storage_hosts:
                    storage_hosts = "{0},{1}".format(storage_hosts,
                                                     host_id)
                else:
                    storage_hosts = "{0}".format(host_id)
        return storage_hosts

    def list_volume_groups(self, ctx):
        vol_group_list = []
        storage_id = self.storage_id
        lun_groups_list = self.get_data(
            consts.GET_LUN_GROUPS, consts.LUN_VOLUME_LENGTH)
        for lun in (lun_groups_list or []):
            lun_groups_id = lun[consts.LUN_GROUPS_ID_COUNT]
            lun_groups_name = lun[consts.LUN_GROUPS_NAME_COUNT]
            volumes_str = self.get_lun_group_details(lun_groups_id)
            vol_g = {
                'name': lun_groups_name,
                'storage_id': storage_id,
                'native_volume_group_id': lun_groups_id,
                'volumes': volumes_str
            }
            vol_group_list.append(vol_g)
        vol_grp_vol_relation_list = []
        for vol_group in vol_group_list:
            volumes = vol_group.pop('volumes', None)
            if not volumes:
                continue
            for volume_id in volumes.split(','):
                storage_volume_group_relation = {
                    'storage_id': storage_id,
                    'native_volume_group_id': vol_group.get(
                        'native_volume_group_id'),
                    'native_volume_id': volume_id
                }
                vol_grp_vol_relation_list \
                    .append(storage_volume_group_relation)
        result = {
            'volume_groups': vol_group_list,
            'vol_grp_vol_rels': vol_grp_vol_relation_list
        }
        return result

    def get_lun_group_details(self, lun_groups_id):
        lun_group_details_str = self.cli_handler.exec_command(
            consts.GET_LUN_GROUPS_LG_NUMBER.format(lun_groups_id))
        volumes_str = None
        if lun_group_details_str:
            lun_group_details_arr = lun_group_details_str.strip(
            ).replace('\r', '').split('\n')
            block = True
            for lun_details_row_str in (lun_group_details_arr or []):
                if not lun_details_row_str or \
                        consts.CLI_STR in lun_details_row_str:
                    continue
                if consts.LUN_GROUPS_SPECIFIC_TWO in lun_details_row_str:
                    block = False
                    continue
                if block:
                    continue
                lun_details_arr = lun_details_row_str.strip().split()
                volume_id = lun_details_arr[consts.LUN_VOLUME_ID]
                if volumes_str:
                    volumes_str = "{0},{1}".format(volumes_str, volume_id)
                else:
                    volumes_str = "{0}".format(volume_id)
        return volumes_str

    def list_port_groups(self, ctx):
        port_group_list = []
        storage_id = self.storage_id
        port_groups_str = self.cli_handler.exec_command(consts.GET_PORT_GROUPS)
        if port_groups_str:
            port_groups_arr = port_groups_str.strip().replace('\r', '').split(
                '\n\n')
            for port_group_str in port_groups_arr:
                port_group_arr = port_group_str.split(
                    consts.LIST_MASKING_VIEWS_SPECIFIC_TWO)
                port_g_row_arr = port_group_arr[
                    consts.PORT_GROUP_ROW_ARR_NUM].split('\n')
                port_group_id = None
                port_group_name = None
                block = True
                for port_g_row_str in port_g_row_arr:
                    if not port_g_row_str or \
                            consts.CLI_STR in port_g_row_str:
                        continue
                    if consts.LIST_MASKING_VIEWS_SPECIFIC_ONE \
                            in port_g_row_str:
                        block = False
                        continue
                    if block:
                        continue
                    port_group = port_g_row_str.strip().split()
                    port_group_id = port_group[consts.PORT_GROUP_ID_NUM]
                    port_group_name = port_group[consts.PORT_GROUP_NAME_NUM]
                    break
                ports_str = None
                if len(port_group_arr) == consts.PORT_GROUP_ARR_LENGTH:
                    port_list_row_arr = port_group_arr[
                        consts.PORT_LIST_ROW_ARR_NUM].strip().split('\n')
                    for port in (port_list_row_arr or []):
                        port_id = port.strip()
                        if port_id in consts.CLI_STR:
                            continue
                        if ports_str:
                            ports_str = "{0},{1}".format(ports_str, port_id)
                        else:
                            ports_str = "{0}".format(port_id)
                port_g = {
                    'name': port_group_name,
                    'storage_id': storage_id,
                    'native_port_group_id': port_group_id,
                    'ports': ports_str
                }
                port_group_list.append(port_g)
        port_grp_port_relation_list = []
        for port_group in port_group_list:
            ports = port_group.pop('ports', None)
            if not ports:
                continue
            ports = ports.split(',')
            for ports_id in ports:
                port_groups_relation = {
                    'storage_id': storage_id,
                    'native_port_group_id': port_group.get(
                        'native_port_group_id'),
                    'native_port_id': ports_id
                }
                port_grp_port_relation_list \
                    .append(port_groups_relation)
        result = {
            'port_groups': port_group_list,
            'port_grp_port_rels': port_grp_port_relation_list
        }
        return result

    def list_masking_views(self, ctx):
        list_masking_views = []
        hosts = self.list_storage_hosts(ctx)
        view_id_dict = {}
        for host in (hosts or []):
            host_name = host.get('name')
            views_str = self.cli_handler.exec_command(
                consts.GET_HOST_AFFINITY_NAME.format(host_name))
            if views_str:
                views_arr = views_str.strip().replace('\r', '').split('\n\n')
                for views_group_str in (views_arr or []):
                    if consts.LIST_MASKING_VIEWS_SPECIFIC_FOUR \
                            in views_group_str:
                        self.get_host_group_views(
                            view_id_dict, list_masking_views, views_group_str)
                    else:
                        self.get_host_views(host_name, list_masking_views,
                                            views_group_str, view_id_dict)
        return list_masking_views

    def get_host_views(self, host_name, list_masking_views,
                       views_group_str, view_id_dict):
        views_row_arr = views_group_str.strip().split('\n')
        block = True
        key = []
        port_id = None
        for views_row_str in (views_row_arr or []):
            if not views_row_str or \
                    consts.CLI_STR in views_row_str:
                continue
            if consts.LIST_MASKING_VIEWS_SPECIFIC_FIVE in views_row_str:
                port_id = views_row_str.split(
                    consts.LIST_MASKING_VIEWS_SPECIFIC_SIX)[
                    consts.LIST_MASKING_VIEWS_CONSTANT_ZERO]
            self.get_group_key(views_row_str,
                               consts.VIEWS_REGULAR_SPECIFIC_TWO, key)
            if consts.LIST_MASKING_VIEWS_SPECIFIC_ONE in views_row_str:
                block = False
                continue
            if block:
                continue
            if len(key) != consts.VIEWS_HOST_ROW_KEY_LENGTH:
                continue
            views_arr = views_row_str.strip().split()
            volume_group_id = views_arr[consts.LIST_MASKING_VIEWS_CONSTANT_TWO]
            view_id = '{}{}{}{}'.format(None, volume_group_id, host_name, None)
            if view_id_dict.get(view_id):
                continue
            view_id_dict[view_id] = view_id
            view = {
                'native_masking_view_id': view_id,
                'name': view_id,
                'native_storage_host_id': host_name,
                'native_volume_group_id': volume_group_id,
                'native_port_id': port_id,
                'storage_id': self.storage_id,
            }
            list_masking_views.append(view)

    def get_host_group_views(self, view_id_dict, list_masking_views,
                             views_group_str):
        views_group_arr = views_group_str.strip().split(
            consts.LIST_MASKING_VIEWS_SPECIFIC_FOUR)
        views_group_row_arr = views_group_arr[
            consts.VIEWS_GROUP_NUM_ZERO].strip().split('\n')
        block = True
        group_key = []
        for views_group_row in (views_group_row_arr or []):
            if not views_group_row or \
                    consts.CLI_STR in views_group_row:
                continue
            self.get_group_key(views_group_row,
                               consts.VIEWS_REGULAR_SPECIFIC_ONE, group_key)
            if consts.LIST_MASKING_VIEWS_SPECIFIC_ONE in views_group_row:
                block = False
                continue
            if block:
                continue
            views_row_arr = views_group_row.strip().split()
            if len(views_row_arr) != consts.VIEWS_GROUP_ROW_VALUE_LENGTH \
                    or len(group_key) != consts.VIEWS_GROUP_ROW_KEY_LENGTH:
                continue
            host_group_name = views_row_arr[consts.HOST_GROUP_NAME_NUM]
            volume_group_id = views_row_arr[consts.LUN_GROUP_ID_NUM]
            view_id = '{}{}{}{}'.format(host_group_name, volume_group_id,
                                        None, None)
            if view_id_dict.get(view_id):
                continue
            view_id_dict[view_id] = view_id
            view = {
                'native_masking_view_id': view_id,
                'name': view_id,
                'native_storage_host_group_id': host_group_name,
                'native_port_group_id': views_row_arr[
                    consts.PORT_GROUP_NAME_NUM],
                'native_volume_group_id': volume_group_id,
                'storage_id': self.storage_id,
            }
            list_masking_views.append(view)

    @staticmethod
    def get_group_key(views_group_row, regular_str, key):
        title_pattern = re.compile(regular_str)
        title_search_obj = title_pattern.search(views_group_row)
        if title_search_obj:
            views_row_arr = views_group_row.strip().split('  ')
            for views in (views_row_arr or []):
                if views:
                    key.append(views.strip())
        return key
