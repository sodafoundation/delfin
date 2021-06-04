# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import re

import six
from oslo_log import log as logging

from delfin import exception
from delfin import utils
from delfin.drivers.hpe.hpe_3par import consts
from delfin.drivers.utils.ssh_client import SSHPool

LOG = logging.getLogger(__name__)


class SSHHandler(object):
    """Common class for Hpe 3parStor storage system."""

    HPE3PAR_COMMAND_SHOWWSAPI = 'showwsapi'
    HPE3PAR_COMMAND_CHECKHEALTH = 'checkhealth vv vlun task snmp ' \
                                  'port pd node network ld dar cage cabling'
    HPE3PAR_COMMAND_SHOWALERT = 'showalert -d'
    HPE3PAR_COMMAND_REMOVEALERT = 'removealert -f %s'
    ALERT_NOT_EXIST_MSG = 'Unable to read alert'
    HPE3PAR_COMMAND_SHOWNODE = 'shownode'
    HPE3PAR_COMMAND_SHOWNODE_CPU = 'shownode -cpu'
    HPE3PAR_COMMAND_SHOWEEPROM = 'showeeprom'
    HPE3PAR_COMMAND_SHOWPD = 'showpd'
    HPE3PAR_COMMAND_SHOWPD_I = 'showpd -i'
    HPE3PAR_COMMAND_SHOWPORT = 'showport'
    HPE3PAR_COMMAND_SHOWPORT_I = 'showport -i'
    HPE3PAR_COMMAND_SHOWPORT_PAR = 'showport -par'
    HPE3PAR_COMMAND_SHOWPORT_C = 'showport -c'
    HPE3PAR_COMMAND_SHOWPORT_ISCSI = 'showport -iscsi'
    HPE3PAR_COMMAND_SHOWPORT_RCIP = 'showport -rcip'
    HPE3PAR_COMMAND_SHOWPORT_FCOE = 'showport -fcoe'
    HPE3PAR_COMMAND_SHOWPORT_FS = 'showport -fs'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.ssh_pool = SSHPool(**kwargs)

    def login(self, context):
        """Test SSH connection """
        version = ''
        try:
            re = self.ssh_pool.do_exec(SSHHandler.HPE3PAR_COMMAND_SHOWWSAPI)
            wsapi_infos = re.split('\n')
            if len(wsapi_infos) > 1:
                version = self.get_version(wsapi_infos)

        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e
        return version

    def get_version(self, wsapi_infos):
        """get wsapi version """
        version = ''
        try:
            str_line = ' '.join(wsapi_infos[1].split())
            wsapi_values = str_line.split(' ')
            version = wsapi_values[6]

        except Exception as e:
            LOG.error("Get version error: %s", six.text_type(e))
        return version

    def get_health_state(self):
        """Check the hardware and software health
           status of the storage system

           return: System is healthy
        """
        return self.ssh_pool.do_exec(SSHHandler.HPE3PAR_COMMAND_CHECKHEALTH)

    def get_all_alerts(self):
        return self.ssh_pool.do_exec(SSHHandler.HPE3PAR_COMMAND_SHOWALERT)

    def remove_alerts(self, alert_id):
        """Clear alert from storage system.
            Currently not implemented   removes command : removealert
        """
        utils.check_ssh_injection([alert_id])
        command_str = SSHHandler.HPE3PAR_COMMAND_REMOVEALERT % alert_id
        res = self.ssh_pool.do_exec(command_str)
        if res:
            if self.ALERT_NOT_EXIST_MSG not in res:
                raise exception.InvalidResults(six.text_type(res))
            LOG.warning("Alert %s doesn't exist.", alert_id)

    def get_controllers(self):
        para_map = {
            'command': 'parse_node_table'
        }
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWNODE,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.NODE_PATTERN,
                                       para_map=para_map)

    def get_controllers_cpu(self):
        para_map = {
            'command': 'parse_node_cpu'
        }
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWNODE_CPU,
                                       self.parse_datas_to_map,
                                       pattern_str=consts.CPU_PATTERN,
                                       para_map=para_map, throw_excep=False)

    def get_controllers_version(self):
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWEEPROM,
                                       self.parse_node_version,
                                       throw_excep=False)

    def parse_node_version(self, resource_info, pattern_str, para_map=None):
        node_version_map = {}
        node_info_map = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if str_line.startswith('Node:'):
                        str_info = self.split_str_by_colon(str_line)
                        node_info_map['node_id'] = str_info[1]
                    if str_line.startswith('OS version:'):
                        str_info = self.split_str_by_colon(str_line)
                        node_info_map['node_os_version'] = str_info[1]
                else:
                    if node_info_map:
                        node_version_map[
                            node_info_map.get('node_id')] = node_info_map.get(
                            'node_os_version')
                        node_info_map = {}
        except Exception as e:
            err_msg = "Analyse node version info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return node_version_map

    def split_str_by_colon(self, str_line):
        str_info = []
        if str_line:
            # str_info[0] is the parsed attribute name, there are some special
            # characters such as spaces, brackets, etc.,
            # str_info[1] is the value
            str_info = str_line.split(':', 1)
            str_info[0] = str_info[0].strip()
            str_info[0] = str_info[0].replace(" ", "_") \
                .replace("(", "").replace(")", "").lower()
            if len(str_info) > 1:
                str_info[1] = str_info[1].strip()
        return str_info

    def get_disks(self):
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWPD,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.DISK_PATTERN)

    def get_disks_inventory(self):
        inventory_map = {}
        para_map = {
            'command': 'parse_disk_table'
        }
        inventorys = self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWPD_I, self.parse_datas_to_list,
            pattern_str=consts.DISK_I_PATTERN, para_map=para_map,
            throw_excep=False)
        for inventory in (inventorys or []):
            inventory_map[inventory.get('disk_id')] = inventory
        return inventory_map

    def get_ports(self):
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWPORT,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.PORT_PATTERN)

    def get_ports_inventory(self):
        para_map = {
            'key_position': 0,
            'value_position': 'last'
        }
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWPORT_I,
                                       self.parse_datas_to_map,
                                       pattern_str=consts.PORT_I_PATTERN,
                                       para_map=para_map, throw_excep=False)

    def get_ports_config(self):
        para_map = {
            'key_position': 0,
            'value_position': 4
        }
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWPORT_PAR,
                                       self.parse_datas_to_map,
                                       pattern_str=consts.PORT_PER_PATTERN,
                                       para_map=para_map, throw_excep=False)

    def get_ports_iscsi(self):
        iscsis_map = {}
        iscsis = self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWPORT_ISCSI,
            self.parse_datas_to_list, pattern_str=consts.PORT_ISCSI_PATTERN,
            throw_excep=False)
        for iscsi in (iscsis or []):
            iscsis_map[iscsi.get('n:s:p')] = iscsi
        return iscsis_map

    def get_ports_connected(self):
        para_map = {
            'key_position': 0,
            'value_position': 6
        }
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWPORT_C,
                                       self.parse_datas_to_map,
                                       pattern_str=consts.PORT_C_PATTERN,
                                       para_map=para_map, throw_excep=False)

    def get_ports_rcip(self):
        rcip_map = {}
        rcips = self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWPORT_RCIP,
            self.parse_datas_to_list, pattern_str=consts.PORT_RCIP_PATTERN,
            throw_excep=False)
        for rcip in (rcips or []):
            rcip_map[rcip.get('n:s:p')] = rcip
        return rcip_map

    def get_ports_fs(self):
        port_fs_map = {}
        port_fss = self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWPORT_FS,
            self.parse_datas_to_list, pattern_str=consts.PORT_FS_PATTERN,
            throw_excep=False)
        for port_fs in (port_fss or []):
            port_fs_map[port_fs.get('n:s:p')] = port_fs
        return port_fs_map

    def get_ports_fcoe(self):
        fcoe_map = {}
        fcoes = self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWPORT_FCOE,
            self.parse_datas_to_list, pattern_str=consts.PORT_FCOE_PATTERN,
            throw_excep=False)
        for fcoe in (fcoes or []):
            fcoe_map[fcoe.get('n:s:p')] = fcoe
        return fcoe_map

    def parse_datas_to_list(self, resource_info, pattern_str, para_map=None):
        obj_list = []
        titles_size = 9999
        try:
            pattern = re.compile(pattern_str)
            obj_infos = resource_info.split('\n')
            titles = []
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    search_obj = pattern.search(str_line)
                    if search_obj:
                        titles = str_line.split()
                        titles_size = len(titles)
                    else:
                        str_info = str_line.split()
                        cols_size = len(str_info)
                        if para_map and para_map.get('command', '') \
                                == 'parse_disk_table':
                            obj_list = self.parse_disk_table(cols_size,
                                                             titles_size,
                                                             str_info,
                                                             obj_list,
                                                             titles)
                        elif para_map and para_map.get('command', '') \
                                == 'parse_node_table':
                            obj_list = self.parse_node_table(cols_size,
                                                             titles_size,
                                                             str_info,
                                                             obj_list)
                        else:
                            if cols_size == titles_size:
                                obj_model = {}
                                for i in range(0, cols_size):
                                    key = titles[i].lower().replace('-', '')
                                    obj_model[key] = str_info[i]
                                if obj_model:
                                    obj_list.append(obj_model)
        except Exception as e:
            err_msg = "Analyse datas to list error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def parse_datas_to_map(self, resource_info, pattern_str, para_map=None):
        obj_model = {}
        titles_size = 9999
        try:
            pattern = re.compile(pattern_str)
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    search_obj = pattern.search(str_line)
                    if search_obj:
                        titles = str_line.split()
                        titles_size = len(titles)
                    else:
                        str_info = str_line.split()
                        cols_size = len(str_info)
                        if para_map and para_map.get('command',
                                                     '') == 'parse_node_cpu':
                            obj_model = self.parse_node_cpu(cols_size,
                                                            titles_size,
                                                            str_info,
                                                            obj_model)
                        else:
                            if cols_size >= titles_size:
                                key_position = para_map.get('key_position')
                                value_position = para_map.get('value_position')
                                if para_map.get('value_position') == 'last':
                                    value_position = cols_size - 1
                                obj_model[str_info[key_position]] = str_info[
                                    value_position]
        except Exception as e:
            err_msg = "Analyse datas to map error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_model

    def parse_disk_table(self, cols_size, titles_size, str_info,
                         obj_list, titles):
        if cols_size == titles_size:
            fw_rev_index = self.get_index_of_key(titles, 'FW_Rev')
            if fw_rev_index:
                inventory_map = {
                    'disk_id': str_info[0],
                    'disk_mfr': ' '.join(str_info[4:fw_rev_index - 2]),
                    'disk_model': str_info[fw_rev_index - 2],
                    'disk_serial': str_info[fw_rev_index - 1],
                    'disk_fw_rev': str_info[fw_rev_index]
                }
                obj_list.append(inventory_map)
        return obj_list

    def parse_node_table(self, cols_size, titles_size, str_info, obj_list):
        if cols_size >= titles_size:
            # Only node_ The name attribute may contain spaces,
            # so there will be several more columns
            # after splitting
            # You need to start with the last few columns
            obj_model = {
                'node_id': str_info[0],
                'node_name': ' '.join(str_info[1:cols_size - 8]),
                'node_state': str_info[cols_size - 8],
                'node_control_mem': str_info[cols_size - 3],
                'node_data_mem': str_info[cols_size - 2]
            }
            obj_list.append(obj_model)
        return obj_list

    def parse_node_cpu(self, cols_size, titles_size, str_info, obj_map):
        if cols_size >= titles_size:
            node_id = str_info[0]
            cpu_info = str_info[4]
            if obj_map.get(node_id):
                obj_map[node_id][cpu_info] = obj_map.get(node_id).get(
                    cpu_info, 0) + 1
            else:
                cpu_info_map = {}
                cpu_info_map[cpu_info] = 1
                obj_map[node_id] = cpu_info_map
        return obj_map

    def get_index_of_key(self, titles_list, key):
        if titles_list:
            for title in titles_list:
                if key in title:
                    return titles_list.index(title)
        return None

    def get_resources_info(self, command, parse_type, pattern_str=None,
                           para_map=None, throw_excep=True):
        re = self.ssh_pool.do_exec(command)
        if re and 'invalid command name' in re:
            LOG.error(re)
            raise NotImplementedError(re)
        resources_info = None
        try:
            if re:
                resources_info = parse_type(re, pattern_str,
                                            para_map=para_map)
        except Exception as e:
            LOG.error("Get %s info error: %s" % (command, six.text_type(e)))
            if throw_excep:
                raise e
        return resources_info
