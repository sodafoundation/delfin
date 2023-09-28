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
import time

import six
from oslo_log import log as logging
from oslo_utils import units

from delfin import exception
from delfin import utils
from delfin.drivers.hpe.hpe_3par import consts
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools

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
    HPE3PAR_COMMAND_SHOWHOSTSET_D = 'showhostset -d'
    HPE3PAR_COMMAND_SHOWVVSET_D = 'showvvset -d'
    HPE3PAR_COMMAND_SHOWHOST_D = 'showhost -d'
    HPE3PAR_COMMAND_SHOWVV = 'showvv'
    HPE3PAR_COMMAND_SHOWVLUN_T = 'showvlun -t'

    HPE3PAR_COMMAND_SRSTATPORT = 'srstatport -attime -groupby ' \
                                 'PORT_N,PORT_S,PORT_P -btsecs %d -etsecs %d'
    HPE3PAR_COMMAND_SRSTATPD = 'srstatpd -attime -btsecs %d -etsecs %d'
    HPE3PAR_COMMAND_SRSTATVV = 'srstatvv -attime -groupby VVID,VV_NAME' \
                               ' -btsecs %d -etsecs %d'
    HPE3PAR_COMMAND_SRSTATPD_ATTIME = 'srstatpd -attime'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.ssh_pool = SSHPool(**kwargs)

    def login(self, context):
        """Test SSH connection """
        version = ''
        try:
            re = self.exec_command(SSHHandler.HPE3PAR_COMMAND_SHOWWSAPI)
            if re:
                version = self.get_version(re)
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e
        return version

    def get_version(self, wsapi_infos):
        """get wsapi version """
        version = ''
        try:
            version_list = self.parse_datas_to_list(wsapi_infos,
                                                    consts.VERSION_PATTERN)
            if version_list and version_list[0]:
                version = version_list[0].get('version')
        except Exception as e:
            LOG.error("Get version error: %s, wsapi info: %s" % (
                six.text_type(e), wsapi_infos))
        return version

    def get_health_state(self):
        """Check the hardware and software health
           status of the storage system

           return: System is healthy
        """
        return self.exec_command(SSHHandler.HPE3PAR_COMMAND_CHECKHEALTH)

    def get_all_alerts(self):
        return self.exec_command(SSHHandler.HPE3PAR_COMMAND_SHOWALERT)

    def remove_alerts(self, alert_id):
        """Clear alert from storage system.
            Currently not implemented   removes command : removealert
        """
        utils.check_ssh_injection([alert_id])
        command_str = SSHHandler.HPE3PAR_COMMAND_REMOVEALERT % alert_id
        res = self.exec_command(command_str)
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
                                                             obj_list,
                                                             titles)
                        elif para_map and para_map.get('command', '') \
                                == 'parse_metric_table':
                            if '---------------------------------' in str_line:
                                break
                            if 'Time:' in str_line:
                                collect_time = Tools.get_numbers_in_brackets(
                                    str_line, consts.SSH_COLLECT_TIME_PATTERN)
                                if collect_time:
                                    collect_time = int(collect_time) * units.k
                                else:
                                    collect_time = int(time.time() * units.k)
                                para_map['collect_time'] = collect_time
                            obj_list = self.parse_metric_table(cols_size,
                                                               titles_size,
                                                               str_info,
                                                               obj_list,
                                                               titles,
                                                               para_map)
                        elif para_map and para_map.get('command', '') \
                                == 'parse_set_groups_table':
                            if '---------------------------------' in str_line:
                                break
                            obj_list = self.parse_set_groups_table(cols_size,
                                                                   titles_size,
                                                                   str_info,
                                                                   obj_list)
                        elif para_map and para_map.get('command', '') \
                                == 'parse_view_table':
                            if '---------------------------------' in str_line:
                                break
                            obj_list = self.parse_view_table(cols_size,
                                                             titles_size,
                                                             str_info,
                                                             obj_list,
                                                             titles)
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
        titles = []
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
                                                            obj_model,
                                                            titles)
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
        if cols_size >= titles_size:
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

    def parse_node_table(self, cols_size, titles_size, str_info, obj_list,
                         titles):
        if cols_size >= titles_size:
            obj_model = {}
            num_prefix = 1
            for i in range(cols_size):
                key_prefix = ''
                key = titles[i].lower().replace('-', '')
                if key == 'mem(mb)':
                    key_prefix = consts.SSH_NODE_MEM_TYPE.get(num_prefix)
                    num_prefix += 1
                key = '%s%s' % (key_prefix, key)
                obj_model[key] = str_info[i]
            if obj_model:
                obj_list.append(obj_model)
        return obj_list

    def parse_node_cpu(self, cols_size, titles_size, str_info, obj_map,
                       titles):
        if cols_size >= titles_size:
            if 'Cores' in titles:
                node_id = str_info[0]
                cpu_info = ' '.join(str_info[5:])
                cpu_map = obj_map.setdefault(node_id, {})
                cpu_map[cpu_info] = int(str_info[2])
            else:
                node_id = str_info[0]
                cpu_info = str_info[4]
                cpu_map = obj_map.setdefault(node_id, {})
                cpu_map[cpu_info] = cpu_map.get(cpu_info, 0) + 1
        return obj_map

    def parse_metric_table(self, cols_size, titles_size, str_info,
                           obj_list, titles, para_map):
        if cols_size == titles_size:
            obj_model = {}
            metric_type_num = 1
            key_prefix = ''
            for i in range(0, cols_size):
                key = titles[i].lower().replace('-', '')
                if key == 'rd':
                    key_prefix = consts.SSH_METRIC_TYPE.get(metric_type_num)
                    metric_type_num += 1
                key = '%s%s' % (key_prefix, key)
                obj_model[key] = str_info[i]
            if obj_model:
                if para_map and para_map.get('collect_time'):
                    obj_model['collect_time'] = para_map.get('collect_time')
                obj_list.append(obj_model)
        return obj_list

    def get_index_of_key(self, titles_list, key):
        if titles_list:
            for title in titles_list:
                if key in title:
                    return titles_list.index(title)
        return None

    def get_resources_info(self, command, parse_type, pattern_str=None,
                           para_map=None, throw_excep=True):
        re = self.exec_command(command)
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

    def exec_command(self, command):
        re = self.ssh_pool.do_exec(command)
        if re:
            if 'invalid command name' in re or 'Invalid option' in re:
                LOG.warning(re)
                raise NotImplementedError(re)
            elif 'Too many local CLI connections' in re:
                LOG.error("command %s failed: %s" % (command, re))
                raise exception.StorageMaxUserCountException(re)
        return re

    def get_volumes(self):
        return self.get_resources_info(SSHHandler.HPE3PAR_COMMAND_SHOWVV,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.VOLUME_PATTERN)

    def get_port_metrics(self, start_time, end_time):
        command = SSHHandler.HPE3PAR_COMMAND_SRSTATPORT % (
            int(start_time / units.k), int(end_time / units.k))
        return self.get_resources_info(command,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.SRSTATPORT_PATTERN,
                                       para_map={
                                           'command': 'parse_metric_table'})

    def get_disk_metrics(self, start_time, end_time):
        command = SSHHandler.HPE3PAR_COMMAND_SRSTATPD_ATTIME
        if start_time and end_time:
            command = SSHHandler.HPE3PAR_COMMAND_SRSTATPD % (
                int(start_time / units.k), int(end_time / units.k))
        return self.get_resources_info(command,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.SRSTATPD_PATTERN,
                                       para_map={
                                           'command': 'parse_metric_table'})

    def get_volume_metrics(self, start_time, end_time):
        command = SSHHandler.HPE3PAR_COMMAND_SRSTATVV % (
            int(start_time / units.k), int(end_time / units.k))
        return self.get_resources_info(command,
                                       self.parse_datas_to_list,
                                       pattern_str=consts.SRSTATVV_PATTERN,
                                       para_map={
                                           'command': 'parse_metric_table'})

    def list_storage_host_groups(self):
        para_map = {
            'command': 'parse_set_groups_table'
        }
        return self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWHOSTSET_D,
            self.parse_datas_to_list,
            pattern_str=consts.HOST_OR_VV_SET_PATTERN,
            para_map=para_map)

    def list_volume_groups(self):
        para_map = {
            'command': 'parse_set_groups_table'
        }
        return self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWVVSET_D,
            self.parse_datas_to_list,
            pattern_str=consts.HOST_OR_VV_SET_PATTERN,
            para_map=para_map)

    def parse_set_groups_table(self, cols_size, titles_size, str_info,
                               obj_list):
        if cols_size >= titles_size:
            members = []
            value = str_info[2].replace('-', '')
            if value:
                members = [str_info[2]]
            obj_model = {
                'id': str_info[0],
                'name': str_info[1],
                'members': members,
                'comment': (" ".join(str_info[3:])).replace('-', ''),
            }
            obj_list.append(obj_model)
        elif obj_list and cols_size == 1:
            value = str_info[0].replace('-', '')
            if value:
                obj_model = obj_list[-1]
                if obj_model and obj_model.get('members'):
                    obj_model.get('members').append(str_info[0])
                else:
                    members = [str_info[0]]
                    obj_model['members'] = members

        return obj_list

    def parse_view_table(self, cols_size, titles_size, str_info, obj_list,
                         titles):
        if cols_size >= titles_size:
            obj_model = {}
            for i in range(titles_size):
                key = titles[i].lower().replace('-', '')
                obj_model[key] = str_info[i]
            if obj_model:
                obj_list.append(obj_model)
        return obj_list

    def get_resources_ids(self, command, pattern_str, para_map=None):
        if not para_map:
            para_map = {
                'key_position': 1,
                'value_position': 0
            }
        return self.get_resources_info(command,
                                       self.parse_datas_to_map,
                                       pattern_str=pattern_str,
                                       para_map=para_map, throw_excep=False)

    def list_storage_host_initiators(self):
        return self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWHOST_D,
            self.parse_datas_to_list,
            pattern_str=consts.HOST_OR_VV_PATTERN)

    def list_masking_views(self):
        para_map = {
            'command': 'parse_view_table'
        }
        return self.get_resources_info(
            SSHHandler.HPE3PAR_COMMAND_SHOWVLUN_T,
            self.parse_datas_to_list,
            pattern_str=consts.VLUN_PATTERN,
            para_map=para_map)
