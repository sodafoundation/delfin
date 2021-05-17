# Copyright 2021 The SODA Authors.
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
import re

import six
from delfin import exception
from oslo_log import log
from oslo_utils import units

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.dell_emc.vplex import alert_handler
from delfin.drivers.dell_emc.vplex import rest_handler
from delfin.drivers.dell_emc.vplex import consts

LOG = log.getLogger(__name__)


class VplexStorageDriver(driver.StorageDriver):
    """DELL EMC VPLEX storage driver implement the DELL EMC Storage driver"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.verify = kwargs.get('verify', False)
        self.rest_handler.login()

    def get_storage(self, context):
        health_check = self.rest_handler.get_health_check_resp()
        all_cluster = self.rest_handler.get_cluster_resp()
        cluster_name_list = VplexStorageDriver.get_resource_names(all_cluster)
        if cluster_name_list:
            health_map = {}
            custom_data = health_check.get("custom-data")
            VplexStorageDriver.handle_detail(custom_data,
                                             health_map, split=':')
            for cluster_name in cluster_name_list:
                response = self.rest_handler.get_cluster_by_name_resp(
                    cluster_name)
                attr_map = VplexStorageDriver.get_attribute_map(response)
                operate_status = attr_map.get('operational-status')
                health_status = attr_map.get('health-state')
                status = VplexStorageDriver.analyse_status(operate_status,
                                                           health_status)
                try:
                    raw_capacity = self.get_cluster_raw_capacity(cluster_name)
                    total_capacity = self.get_cluster_total_capacity(
                        cluster_name)
                    used_capacity = self.get_cluster_used_capacity(
                        cluster_name)
                except Exception:
                    error_msg = "Failed to get capacity from VPLEX!"
                    raise exception.StorageBackendException(error_msg)
                free_capacity = total_capacity - used_capacity
                if free_capacity < 0:
                    free_capacity = 0
                cluster = {
                    'name': cluster_name,
                    'vendor': 'DELL EMC',
                    'description': 'EMC VPlex Storage',
                    'status': status,
                    'serial_number': attr_map.get('top-level-assembly'),
                    'firmware_version': health_map.get("Product Version"),
                    'model': 'EMC VPLEX ' + health_map.get("Product Type"),
                    'location': '',
                    'raw_capacity': int(raw_capacity),
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': int(free_capacity)
                }
                break
        return cluster

    def list_storage_pools(self, context):
        device_list = []
        all_cluster = self.rest_handler.get_cluster_resp()
        cluster_name_list = VplexStorageDriver.get_resource_names(all_cluster)
        for cluster_name in cluster_name_list:
            response_device = self.rest_handler.get_devcie_resp(cluster_name)
            map_device_childer = VplexStorageDriver.get_children_map(
                response_device)
            for name, resource_type in map_device_childer.items():
                response_dn = self.rest_handler.get_device_by_name_resp(
                    cluster_name, name)
                map_dn_attribute = VplexStorageDriver.get_attribute_map(
                    response_dn)
                virtual_volume = map_dn_attribute.get("virtual-volume")
                total_capacity_str = map_dn_attribute.get("capacity")
                total_capacity = VplexStorageDriver.analyse_capacity(
                    total_capacity_str)
                operate_status = map_dn_attribute.get('operational-status')
                health_status = map_dn_attribute.get('health-state')
                used_capacity = 0
                free_capacity = 0
                if virtual_volume:
                    used_capacity = total_capacity
                else:
                    free_capacity = total_capacity

                device = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': map_dn_attribute.get(
                        "system-id"),
                    'description': 'EMC VPlex Pool',
                    'status': self.analyse_status(operate_status,
                                                  health_status),
                    'storage_type': constants.StorageType.BLOCK,
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': int(free_capacity)
                }
                device_list.append(device)
        return device_list

    def list_volumes(self, context):
        vv_list = []
        all_cluster = self.rest_handler.get_cluster_resp()
        cluster_name_list = VplexStorageDriver.get_resource_names(all_cluster)
        for cluster_name in cluster_name_list:
            resposne_vv = self.rest_handler.get_virtual_volume_resp(
                cluster_name)
            map_vv_children = VplexStorageDriver.get_children_map(resposne_vv)
            for name, resource_type in map_vv_children.items():
                response_vvn = self.rest_handler. \
                    get_virtual_volume_by_name_resp(cluster_name, name)
                map_vvn_attribute = VplexStorageDriver.get_attribute_map(
                    response_vvn)
                thin_enabled = map_vvn_attribute.get("thin-enabled")
                operate_status = map_vvn_attribute.get('operational-status')
                health_status = map_vvn_attribute.get('health-state')
                vv_type = self.analyse_vv_type(thin_enabled)
                total_capacity = VplexStorageDriver.analyse_capacity(
                    map_vvn_attribute.get("capacity"))
                vpd_id = map_vvn_attribute.get("vpd-id")
                cells = vpd_id.split(":")
                wwn = ''
                if len(cells) > 1:
                    wwn = cells[1]
                used_capacity = 0
                if vv_type == constants.VolumeType.THICK:
                    used_capacity = total_capacity
                vv = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'description': 'EMC VPlex volume',
                    'status': self.analyse_status(operate_status,
                                                  health_status),
                    'native_volume_id': vpd_id,
                    'native_storage_pool_id': map_vvn_attribute.get(
                        'supporting-device'),
                    'type': vv_type,
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': 0,
                    'wwn': wwn
                }
                vv_list.append(vv)
        return vv_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def list_alerts(self, context, query_para=None):
        info_msg = "list_alerts is not supported in model VPLEX"
        LOG.info(info_msg)
        raise NotImplementedError(info_msg)

    def clear_alert(self, context, alert):
        pass

    @staticmethod
    def get_access_url():
        return 'https://{ip}'

    @staticmethod
    def get_attribute_map(response):
        attr_map = {}
        if response:
            contexts = response.get("context")
            for context in contexts:
                attributes = context.get("attributes")
                for attribute in attributes:
                    key = attribute.get("name")
                    value = attribute.get("value")
                    attr_map[key] = value
        return attr_map

    @staticmethod
    def analyse_capacity(capacity_str):
        capacity = 0
        if capacity_str.strip():
            capacity = re.findall("\\d+", capacity_str)[0]
        return capacity

    @staticmethod
    def analyse_status(operational_status, health_status):
        status = constants.StorageStatus.ABNORMAL
        status_normal = ["ok"]
        status_offline = ["unknown", "isolated", "not-running",
                          "non-recoverable-error"]
        if operational_status and health_status in status_normal:
            status = constants.StorageStatus.NORMAL
        elif operational_status and health_status in status_offline:
            status = constants.StorageStatus.OFFLINE
        return status

    @staticmethod
    def analyse_vv_type(thin_enabled):
        rs_type = constants.VolumeType.THICK
        if thin_enabled == "enabled":
            rs_type = constants.VolumeType.THIN
        return rs_type

    @staticmethod
    def get_children_map(response):
        child_map = {}
        if response:
            contexts = response.get("context")
            for context in contexts:
                childrens = context.get("children")
                for children in childrens:
                    name = children.get("name")
                    type = children.get("type")
                    child_map[name] = type
        return child_map

    @staticmethod
    def get_resource_names(response):
        resource_name_list = []
        if response:
            contexts = response.get('context')
            for context in contexts:
                childer_clusters = context.get("children")
                for childer_cluster in childer_clusters:
                    cluster_name = childer_cluster.get("name")
                    resource_name_list.append(cluster_name)
        return resource_name_list

    @staticmethod
    def handle_detail(detail_info, detail_map, split):
        detail_arr = detail_info.split('\n')
        for detail in detail_arr:
            if detail is not None and detail != '':
                strinfo = detail.split(split, 1)
                key = strinfo[0]
                value = ''
                if len(strinfo) > 1:
                    value = strinfo[1]
                detail_map[key] = value

    def get_cluster_raw_capacity(self, cluster_name):
        resposne_summary = self.rest_handler. \
            get_storage_volume_summary_resp(cluster_name)
        try:
            custom_data = resposne_summary.get("custom-data")
            find_capacity = re.findall(
                r"Capacity\s+total\s+(([0-9]*(\.[0-9]{1,3}))|([0-9]+))",
                custom_data)
            find_capacity_str = find_capacity[-1][0]
            find_capacity_float = float(find_capacity_str)
            capacity = int(find_capacity_float * units.Ti)
        except Exception as e:
            LOG.error("Storage raw capacity, cluster %s analyse error %s" %
                      cluster_name, six.text_type(e))
            raise e
        return capacity

    def get_cluster_total_capacity(self, cluster_name):
        resposne_summary = self.rest_handler.get_device_summary_resp(
            cluster_name)
        try:
            custom_data = resposne_summary.get("custom-data")
            find_capacity = re.findall(
                r'total.*?(([0-9]*(\.[0-9]{1,3}))|([0-9]+))',
                custom_data)
            find_capacity_str = find_capacity[-1][0]
            find_capacity_float = float(find_capacity_str)
            capacity = int(find_capacity_float * units.Ti)
        except Exception as e:
            LOG.error("Storage total capacity, cluster %s analyse error %s" %
                      cluster_name, six.text_type(e))
            raise e
        return capacity

    def get_cluster_used_capacity(self, cluster_name):
        resposne_summary = self.rest_handler. \
            get_virtual_volume_summary_resp(cluster_name)
        try:
            custom_data = resposne_summary.get("custom-data")
            find_capacity = re.findall(
                r"capacity\s+is\s+(([0-9]*(\.[0-9]{1,3}))|([0-9]+))",
                custom_data)
            find_capacity_str = find_capacity[-1][0]
            find_capacity_float = float(find_capacity_str)
            capacity = int(find_capacity_float * units.Ti)
        except Exception as e:
            LOG.error("Storage used capacity, cluster %s analyse error %s" %
                      cluster_name, six.text_type(e))
            raise e
        return capacity

    def list_controllers(self, context):
        """List all storage controllers from storage system."""
        ct_list = []
        director_version_map = {}
        version_resp = self.rest_handler.get_version_verbose()
        all_director = self.rest_handler.get_engine_director_resp()
        ct_context_list = VplexStorageDriver.get_context_list(all_director)
        VplexStorageDriver.analyse_director_version(version_resp,
                                                    director_version_map)
        for ct_context in ct_context_list:
            ct_attr_map = ct_context.get("attributes")
            communication_status = ct_attr_map.get('communication-status')
            name = ct_attr_map.get('name')
            ct = {
                'native_controller_id ': ct_attr_map.get('director-id'),
                'name': name,
                'status': VplexStorageDriver.analyse_director_status(
                    communication_status),
                'location ': '',
                'storage_id ': self.storage_id,
                'soft_version ': self.get_value_from_nest_map(
                    director_version_map, name, "Director Software"),
                'cpu_info': '',
                'memory_size': ''
            }
            ct_list.append(ct)
        return ct_list

    def list_ports(self, context):
        """List all ports from storage system."""
        port_list = []
        hardware_port_map = {}
        hardware_port_resp = self.rest_handler. \
            get_engine_director_hardware_port_resp()
        export_port_resp = self.rest_handler.get_cluster_export_port_resp()
        VplexStorageDriver.analyse_hardware_port(hardware_port_resp,
                                                 hardware_port_map)
        port_context_list = VplexStorageDriver. \
            get_context_list(export_port_resp)
        for port_context in port_context_list:
            port_attr = port_context.get('attributes')
            port_name = port_attr.get('name')
            speed, max_speed, protocols, role, port_status, \
                operational_status = self.get_hardware_port_info(
                    hardware_port_map, port_name, 'attributes')
            connection_status = VplexStorageDriver.analyse_port_connect_status(
                port_status)
            port = {
                'native_port_id': port_attr.get('name'),
                'name': port_attr.get('name'),
                'type': VplexStorageDriver.analyse_port_type(protocols),
                'logical_type': VplexStorageDriver.analyse_port_logical_type(
                    role),
                'connection_status': connection_status,
                'health_status': VplexStorageDriver.analyse_port_health_status(
                    operational_status),
                'location': '',
                'storage_id': self.storage_id,
                'native_parent_id': port_attr.get('director-id'),
                'speed': VplexStorageDriver.analyse_speed(speed),
                'max_speed': VplexStorageDriver.analyse_speed(max_speed),
                'wwn': port_attr.get('port-wwn'),
                'mac_address': '',
                'ipv4': '',
                'ipv4_mask': '',
                'ipv6': '',
                'ipv6_mask': ''
            }
            port_list.append(port)
        return port_list

    def list_disks(self, context):
        """List all disks from storage system."""
        pass

    @staticmethod
    def get_context_list(response):
        context_list = []
        if response:
            contexts = response.get("context")
            for context in contexts:
                type = context.get("type")
                parent = context.get("parent")
                attributes = context.get("attributes")
                context_map = {}
                attr_map = {}
                for attribute in attributes:
                    key = attribute.get("name")
                    value = attribute.get("value")
                    attr_map[key] = value
                context_map["type"] = type
                context_map["parent"] = parent
                context_map["attributes"] = attr_map
                context_list.append(context_map)
        return context_list

    @staticmethod
    def analyse_director_version(version_resp, director_version_map):
        custom_data = version_resp.get('custom-data')
        detail_arr = custom_data.split('\n')
        director_name = ''
        version_name = ''
        for detail in detail_arr:
            if detail is not None and detail != '':
                if "For director" in detail:
                    match_obj = re.search(
                        r'For director.+?directors/(.*?):', detail)
                    if match_obj:
                        director_name = match_obj.group(1)
                    continue
                if director_name:
                    if "What:" in detail:
                        match_obj = re.search(r'What:\s+(.+?)$', detail)
                        if match_obj:
                            version_name = match_obj.group(1)
                        continue
                    if version_name:
                        match_obj = re.search(r'Version:\s+(.+?)$', detail)
                        if match_obj:
                            version_value = match_obj.group(1)
                            if director_version_map.get(director_name):
                                director_version_map.get(director_name)[
                                    version_name] = version_value
                            else:
                                version_map = {}
                                version_map[version_name] = version_value
                                director_version_map[
                                    director_name] = version_map

    @staticmethod
    def analyse_director_status(status):
        controller_status = constants.ControllerStatus.UNKNOWN
        if status:
            status_value = consts.CONTROLLER_STATUS_MAP.get(status)
            if status_value:
                controller_status = status_value
        return controller_status

    def get_director_specified_version(self, version_map, director_name,
                                       specified_name):
        version_value = ''
        if version_map:
            director_map = version_map.get(director_name)
            if director_map:
                version_value = director_map.get(specified_name)
        return version_value

    def get_value_from_nest_map(self, nest_map, first_key, second_key):
        final_value = ''
        if nest_map:
            second_map = nest_map.get(first_key)
            if second_map:
                final_value = second_map.get(second_key)
        return final_value

    def get_hardware_port_info(self, nest_map, first_key, second_key):
        speed = ''
        max_speed = ''
        protocols = []
        role = ''
        port_status = ''
        operational_status = ''

        if nest_map:
            second_map = nest_map.get(first_key)
            if second_map:
                third_map = second_map.get(second_key)
                if third_map:
                    speed = third_map.get('current-speed')
                    max_speed = third_map.get('max-speed')
                    protocols = third_map.get('protocols')
                    role = third_map.get('role')
                    port_status = third_map.get('port-status')
                    operational_status = third_map.get('operational-status')
        return (speed, max_speed, protocols, role, port_status,
                operational_status)

    @staticmethod
    def analyse_hardware_port(resp, hardware_port_map):
        port_list = VplexStorageDriver.get_context_list(resp)
        if port_list:
            for port in port_list:
                port_name = port.get("attributes").get("target-port")
                hardware_port_map[port_name] = port

    @staticmethod
    def analyse_port_type(protocols):
        port_type = constants.PortType.OTHER
        if protocols:
            for protocol in protocols:
                port_type_value = consts.PORT_TYPE_MAP.get(protocol)
                if port_type_value:
                    port_type = port_type_value
                    break
        return port_type

    @staticmethod
    def analyse_port_logical_type(role):
        port_logic_type = constants.PortLogicalType.OTHER
        if role:
            port_type_value = consts.PORT_LOGICAL_TYPE_MAP.get(role)
            if port_type_value:
                port_logic_type = port_type_value
        return port_logic_type

    @staticmethod
    def analyse_port_connect_status(status):
        port_connect_status = constants.PortConnectionStatus.UNKNOWN
        if status:
            port_status_value = consts.PORT_CONNECT_STATUS_MAP.get(status)
            if port_status_value:
                port_connect_status = port_status_value
        return port_connect_status

    @staticmethod
    def analyse_port_health_status(status):
        port_health_status = constants.PortHealthStatus.UNKNOWN
        if status:
            port_status_value = consts.PORT_HEALTH_STATUS_MAP.get(status)
            if port_status_value:
                port_health_status = port_status_value
        return port_health_status

    @staticmethod
    def analyse_speed(speed):
        speed_value = 0
        if speed:
            match_obj = re.search(r'([1-9]\d*\.?\d*)|(0\.\d*[1-9])', speed)
            if match_obj:
                speed_value = int(match_obj.group(0)) * units.G
        return speed_value


@staticmethod
def handle_detail_list(detail_info, detail_map, split):
    detail_arr = detail_info.split('\n')
    for detail in detail_arr:
        if detail is not None and detail != '':
            strinfo = detail.split(split, 1)
            key = strinfo[0]
            value = ''
            if len(strinfo) > 1:
                value = strinfo[1]
            detail_map[key] = value
