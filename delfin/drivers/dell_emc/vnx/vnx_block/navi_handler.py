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
import os
import re
import threading
import time

import six
from oslo_log import log as logging

from delfin import cryptor
from oslo_utils import units

from delfin import exception
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.dell_emc.vnx.vnx_block.navicli_client import NaviClient
from delfin.drivers.utils.tools import Tools

LOG = logging.getLogger(__name__)


class NaviHandler(object):
    session_lock = None

    def __init__(self, **kwargs):
        cli_access = kwargs.get('cli')
        if cli_access is None:
            raise exception.InvalidInput('Input navicli_access is missing')
        self.navi_host = cli_access.get('host')
        self.navi_port = cli_access.get('port')
        self.navi_username = cli_access.get('username')
        self.navi_password = cli_access.get('password')
        self.navi_timeout = cli_access.get('conn_timeout',
                                           consts.SOCKET_TIMEOUT)
        self.verify = kwargs.get('verify', False)
        self.session_lock = threading.Lock()

    def get_cli_command_str(self, host_ip=None, sub_command=None,
                            timeout=None):
        if host_ip is None:
            host_ip = self.navi_host
        if timeout is None:
            timeout = self.navi_timeout
        command_str = consts.NAVISECCLI_API % {
            'username': self.navi_username,
            'password': cryptor.decode(self.navi_password),
            'host': host_ip, 'timeout': timeout}
        if self.navi_port:
            command_str = '%s -port %d' % (command_str, self.navi_port)
        command_str = '%s %s' % (command_str, sub_command)
        return command_str

    def login(self, host_ip=None):
        """Successful login returns the version number
           Failure to log in will throw an exception
        """
        version = ''
        if host_ip is None:
            host_ip = self.navi_host
        accept_cer = consts.CER_STORE
        if self.verify:
            accept_cer = consts.CER_REJECT
            self.remove_cer(host_ip=host_ip)
            cer_add_command = '%s %s' % (consts.CER_ADD_API, self.verify)
            NaviClient.exec(cer_add_command.split())
        command_str = \
            self.get_cli_command_str(host_ip=host_ip,
                                     sub_command=consts.GET_AGENT_API,
                                     timeout=consts.LOGIN_SOCKET_TIMEOUT)
        result = NaviClient.exec(command_str.split(), stdin_value=accept_cer)
        if result:
            agent_model = self.cli_res_to_dict(result)
            if agent_model:
                version = agent_model.get("revision")
        return version

    def remove_cer(self, host_ip=None):
        if host_ip is None:
            host_ip = self.navi_host
        cer_list_str = NaviClient.exec(consts.CER_LIST_API.split())
        cer_map = self.analyse_cer(cer_list_str, host_ip)
        if cer_map.get(host_ip):
            cer_remove_command = '%s -issuer %s -serialNumber %s' % (
                consts.CER_REMOVE_API,
                cer_map.get(host_ip).get('issuer'),
                cer_map.get(host_ip).get('serial#'))
            NaviClient.exec(cer_remove_command.split())

    def get_agent(self):
        return self.get_resources_info(consts.GET_AGENT_API,
                                       self.cli_res_to_dict)

    def get_domain(self):
        return self.get_resources_info(consts.GET_DOMAIN_API,
                                       self.cli_domain_to_dict)

    def get_pools(self):
        return self.get_resources_info(consts.GET_STORAGEPOOL_API,
                                       self.cli_res_to_list)

    def get_disks(self):
        return self.get_resources_info(consts.GET_DISK_API,
                                       self.cli_disk_to_list)

    def get_raid_group(self):
        return self.get_resources_info(consts.GET_RAIDGROUP_API,
                                       self.cli_raid_to_list)

    def get_pool_lun(self):
        return self.get_resources_info(consts.GET_LUN_API,
                                       self.cli_res_to_list)

    def get_all_lun(self):
        return self.get_resources_info(consts.GET_GETALLLUN_API,
                                       self.cli_lun_to_list)

    def get_controllers(self):
        return self.get_resources_info(consts.GET_SP_API,
                                       self.cli_sp_to_list)

    def get_cpus(self):
        return self.get_resources_info(consts.GET_RESUME_API,
                                       self.cli_cpu_to_dict)

    def get_ports(self):
        return self.get_resources_info(consts.GET_PORT_API,
                                       self.cli_port_to_list)

    def get_bus_ports(self):
        return self.get_resources_info(consts.GET_BUS_PORT_API,
                                       self.cli_bus_port_to_list)

    def get_bus_port_state(self):
        return self.get_resources_info(consts.GET_BUS_PORT_STATE_API,
                                       self.cli_bus_port_state_to_dict)

    def get_iscsi_ports(self):
        return self.get_resources_info(consts.GET_ISCSI_PORT_API,
                                       self.cli_iscsi_port_to_list)

    def get_io_configs(self):
        return self.get_resources_info(consts.GET_IO_PORT_CONFIG_API,
                                       self.cli_io_config_to_dict)

    def get_resources_info(self, sub_command, analyse_type):
        # Execute commands to query data and analyze
        try:
            command_str = self.get_cli_command_str(sub_command=sub_command)
            resource_info = self.navi_exe(command_str.split())
            return_value = None
            if resource_info:
                return_value = analyse_type(resource_info)
        except Exception as e:
            err_msg = "Failed to get resources info from %s: %s" \
                      % (sub_command, six.text_type(e))
            LOG.error(err_msg)
            raise e
        return return_value

    def cli_res_to_dict(self, resource_info):
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if ':' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)
        except Exception as e:
            err_msg = "arrange resource info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_model

    def cli_res_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if consts.DISK_ID_KEY in str_line:
                        str_line = str_line.replace(consts.DISK_ID_KEY,
                                                    "disk id:")
                    if consts.LUN_ID_KEY in str_line:
                        str_line = str_line.replace(consts.LUN_ID_KEY,
                                                    "lun id:")
                    if ':' not in str_line:
                        continue
                    str_info = self.split_str_by_colon(str_line)
                    obj_model = self.str_info_to_model(str_info, obj_model)
                else:
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
            # If the last object is not added to the LIST,
            # perform the join operation
            obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "cli resource to list error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_raid_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                # Use 'RaidGroup ID' to determine whether it is
                # a new object
                if str_line and str_line.startswith('RaidGroup ID:'):
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
                if str_line:
                    if ':' not in str_line:
                        continue
                    str_info = self.split_str_by_colon(str_line)
                    obj_model = self.str_info_to_model(str_info, obj_model)
            # If the last object is not added to the LIST,
            # perform the join operation
            obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "arrange raid info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_sp_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if ':' not in str_line:
                        obj_model['sp_name'] = str_line
                    else:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)

                        if str_line and str_line.startswith(
                                'SP SCSI ID if Available:'):
                            obj_list = self.add_model_to_list(obj_model,
                                                              obj_list)
                            obj_model = {}
        except Exception as e:
            err_msg = "arrange sp info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_port_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        max_speed_str = ''
        previous_line = ''
        try:
            spport_infos = resource_info.split(consts.SPPORT_KEY)[1]
            obj_infos = spport_infos.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if ':' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)
                        previous_line = str_line
                    else:
                        if 'Available Speeds:' in previous_line:
                            if 'Auto' not in str_line \
                                    and str_line > max_speed_str:
                                max_speed_str = str_line
                else:
                    if max_speed_str:
                        obj_model['max_speed'] = max_speed_str
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
                    max_speed_str = ''
                    previous_line = ''
            if obj_model:
                if max_speed_str:
                    obj_model['max_speed'] = max_speed_str
                obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "arrange port info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_bus_port_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        sp_list = []
        max_speed_str = ''
        previous_line = ''
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if 'Bus ' in str_line and ':' not in str_line:
                        if max_speed_str:
                            obj_model['max_speed'] = max_speed_str
                        obj_list = self.add_model_to_list(obj_model, obj_list)
                        obj_model = {}
                        sp_list = []
                        max_speed_str = ''
                        previous_line = ''
                        obj_model['bus_name'] = str_line
                    elif ':' in str_line:
                        previous_line = str_line
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)
                        if ' Connector State' in str_line:
                            sp_list.append(
                                str_info[0].replace('_connector_state', ''))
                            obj_model['sps'] = sp_list
                    else:
                        if 'Available Speeds:' in previous_line:
                            if 'Auto' not in str_line \
                                    and str_line > max_speed_str:
                                max_speed_str = str_line
            if max_speed_str:
                obj_model['max_speed'] = max_speed_str
            obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "arrange port info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_bus_port_state_to_dict(self, resource_info):
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            sp = ''
            port_id = ''
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if 'SP ID:' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        sp = str_info[1]
                    if 'Physical Port ID:' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        port_id = str_info[1]
                    if 'Port State:' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model[sp + '_' + port_id] = str_info[1]
        except Exception as e:
            err_msg = "arrange bus port state info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_model

    def cli_iscsi_port_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if ':' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)
                else:
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
        except Exception as e:
            err_msg = "arrange iscsi port info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_io_config_to_dict(self, resource_info):
        obj_model = {}
        try:
            obj_list = []
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if ':' in str_line:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)
                else:
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
            for config in obj_list:
                if config.get('i/o_module_slot'):
                    key = '%s_%s' % (
                        config.get('sp_id'), config.get('i/o_module_slot'))
                    obj_model[key] = config.get('i/o_module_type').replace(
                        ' Channel', '')
        except Exception as e:
            err_msg = "arrange io port config info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_model

    def cli_cpu_to_dict(self, resource_info):
        obj_model = {}
        try:
            obj_list = []
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if 'CPU Module' in str_line:
                        str_line = '%s:True' % str_line
                    str_info = self.split_str_by_colon(str_line)
                    obj_model = self.str_info_to_model(str_info, obj_model)
                else:
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
            for cpu_module in obj_list:
                if cpu_module.get('cpu_module'):
                    obj_model[
                        cpu_module.get('emc_serial_number')] = cpu_module.get(
                        'assembly_name')
        except Exception as e:
            err_msg = "arrange cpu info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_model

    def cli_disk_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if str_line.startswith('Bus '):
                        disk_name = 'disk_name:%s' % str_line
                        str_info = self.split_str_by_colon(disk_name)
                        obj_model = self.str_info_to_model(str_info, obj_model)
                        str_line = "disk id:%s" % (str_line.replace(' ', ''))
                    if ':' not in str_line:
                        continue
                    str_info = self.split_str_by_colon(str_line)
                    obj_model = self.str_info_to_model(str_info, obj_model)
                else:
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
            # If the last object is not added to the LIST,
            # perform the join operation
            obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "cli resource to list error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_domain_to_dict(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            node_value = ''
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                # Use "IP Address" to determine whether it is a new object
                if str_line and str_line.startswith('IP Address:'):
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
                if str_line:
                    if 'Master' in str_line:
                        obj_model['master'] = 'True'
                        str_line = str_line.replace('(Master)', '')
                    str_info = self.split_str_by_colon(str_line)
                    if str_line and str_line.startswith('Node:'):
                        node_value = str_info[1]
                        continue
                    if str_line and str_line.startswith('IP Address:'):
                        obj_model['node'] = node_value
                    obj_model = self.str_info_to_model(str_info, obj_model)
            # If the last object is not added to the LIST,
            # perform the join operation
            obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "arrange domain info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def cli_lun_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line and str_line.startswith(consts.LUN_ID_KEY):
                    obj_list = self.add_model_to_list(obj_model, obj_list)
                    obj_model = {}
                if str_line:
                    if str_line.startswith(consts.LUN_ID_KEY):
                        str_line = str_line.replace(consts.LUN_ID_KEY,
                                                    'LOGICAL UNIT NUMBER:')
                    if str_line.startswith(consts.LUN_NAME_KEY):
                        str_line = str_line.replace(consts.LUN_NAME_KEY,
                                                    'Name:')
                    if ':' not in str_line:
                        continue
                    str_info = self.split_str_by_colon(str_line)
                    obj_model = self.str_info_to_model(str_info, obj_model)
            obj_list = self.add_model_to_list(obj_model, obj_list)
        except Exception as e:
            err_msg = "arrange lun info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def analyse_cer(self, resource_info, host_ip=None):
        cer_map = {}
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line and consts.CER_SEPARATE_KEY not in str_line:
                    str_info = self.split_str_by_colon(str_line)
                    if str_info[0] == 'issuer' and host_ip not in str_info[1]:
                        continue
                    obj_model[str_info[0]] = str_info[1]
                else:
                    if obj_model and obj_model.get('issuer'):
                        cer_map[host_ip] = obj_model
                        break
        except Exception as e:
            err_msg = "arrange cer info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return cer_map

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

    def str_info_to_model(self, str_info, obj_model):
        # Some information is'attribute: value'
        # Some attributes: no value for example:
        # Pool ID:  1
        # Description:
        # State:  Offline
        if str_info:
            key = None
            value = None
            if len(str_info) > 1:
                key = str_info[0]
                value = str_info[1]
            elif len(str_info) == 1:
                key = str_info[0]
            obj_model[key] = value
        return obj_model

    def add_model_to_list(self, obj_model, obj_list):
        if len(obj_model) > 0:
            obj_list.append(obj_model)
        return obj_list

    def navi_exe(self, command_str, host_ip=None):
        self.session_lock.acquire()
        try:
            if command_str:
                accept_cer = consts.CER_STORE
                if self.verify:
                    accept_cer = consts.CER_REJECT
                result = NaviClient.exec(command_str, stdin_value=accept_cer)
                return result
        except exception.SSLCertificateFailed as e:
            LOG.error("ssl error: %s", six.text_type(e))
            self.login(host_ip)
            result = NaviClient.exec(command_str)
            return result
        except exception.InvalidUsernameOrPassword as e:
            LOG.error("auth error: %s", six.text_type(e))
            self.login(host_ip)
            result = NaviClient.exec(command_str)
            return result
        except Exception as e:
            err_msg = "naviseccli exec error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        finally:
            self.session_lock.release()

    def list_masking_views(self):
        return self.get_resources_info(consts.GET_SG_LIST_HOST_API,
                                       self.cli_sg_to_list)

    def cli_sg_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            pattern = re.compile(consts.ALU_PAIRS_PATTERN)
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if ':' not in str_line:
                        search_obj = pattern.search(str_line)
                        if search_obj:
                            str_info = str_line.split()
                            lun_ids = obj_model.get('lun_ids')
                            if lun_ids:
                                lun_ids.add(str_info[1])
                            else:
                                lun_ids = set()
                                lun_ids.add(str_info[1])
                                obj_model['lun_ids'] = lun_ids
                    else:
                        str_info = self.split_str_by_colon(str_line)
                        if 'Host name:' in str_line:
                            host_names = obj_model.get('host_names')
                            if host_names:
                                host_names.add(str_info[1])
                            else:
                                host_names = set()
                                host_names.add(str_info[1])
                                obj_model['host_names'] = host_names
                            continue

                        obj_model = self.str_info_to_model(str_info, obj_model)

                        if str_line.startswith('Shareable:'):
                            obj_list = self.add_model_to_list(obj_model,
                                                              obj_list)
                            obj_model = {}
        except Exception as e:
            err_msg = "arrange sg info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def list_hbas(self):
        return self.get_resources_info(consts.GET_PORT_LIST_HBA_API,
                                       self.cli_hba_to_list)

    def cli_hba_to_list(self, resource_info):
        obj_list = []
        obj_model = {}
        sp_name = ''
        port_ids = set()
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    if 'Information about each HBA:' in obj_info:
                        if obj_model:
                            obj_model['port_ids'] = port_ids
                        obj_list = self.add_model_to_list(obj_model,
                                                          obj_list)
                        obj_model = {}
                        port_ids = set()
                        sp_name = ''
                    if ':' in obj_info:
                        str_info = self.split_str_by_colon(str_line)
                        obj_model = self.str_info_to_model(str_info, obj_model)
                        if 'SP Name:' in obj_info:
                            sp_name = obj_info.replace('SP Name:', '').replace(
                                'SP', '').replace('\r', '').replace(' ', '')
                        if 'SP Port ID:' in obj_info:
                            port_id = obj_info.replace('SP Port ID:',
                                                       '').replace('\r',
                                                                   '').replace(
                                ' ', '')
                            port_id = '%s-%s' % (sp_name, port_id)
                            port_ids.add(port_id)

            if obj_model:
                obj_model['port_ids'] = port_ids
                obj_list.append(obj_model)
        except Exception as e:
            err_msg = "arrange host info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def get_archives(self):
        return self.get_resources_info(consts.GET_ARCHIVE_API,
                                       self.cli_archives_to_list)

    def cli_archives_to_list(self, resource_info):
        obj_list = []
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    archive_infos = str_line.split()
                    if archive_infos and len(archive_infos) == 5:
                        obj_model = {}
                        obj_model['collection_time'] = \
                            "%s %s" % (archive_infos[2], archive_infos[3])
                        obj_model['archive_name'] = archive_infos[4]
                        obj_list.append(obj_model)
        except Exception as e:
            err_msg = "arrange archives info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def download_archives(self, archive_name):
        download_archive_api = consts.DOWNLOAD_ARCHIVE_API % (
            archive_name, self.get_local_file_path())
        self.get_resources_info(download_archive_api, self.cli_res_to_list)
        archive_name_infos = archive_name.split('.')
        archivedump_api = consts.ARCHIVEDUMP_API % (
            self.get_local_file_path(), archive_name,
            self.get_local_file_path(), archive_name_infos[0])
        self.get_resources_info(archivedump_api, self.cli_res_to_list)

    def get_local_file_path(self):
        driver_path = os.path.abspath(os.path.join(os.getcwd()))
        driver_path = driver_path.replace("\\", "/")
        driver_path = driver_path.replace(consts.REPLACE_PATH, "")
        local_path = '%s%s' % (driver_path, consts.ARCHIVE_FILE_DIR)
        return local_path

    def get_sp_time(self):
        return self.get_resources_info(consts.GET_SP_TIME,
                                       self.analysis_sp_time)

    def analysis_sp_time(self, resource_info):
        system_time = 0
        try:
            tools = Tools()
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if "Time on SP A:" in str_line:
                    time_str = str_line.replace("Time on SP A:", "").strip()
                    system_time = tools.time_str_to_timestamp(
                        time_str, consts.GET_SP_TIME_PATTERN)
        except Exception as e:
            err_msg = "analysis sp time error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return system_time

    def get_nar_interval(self):
        return self.get_resources_info(consts.GET_NAR_INTERVAL_API,
                                       self.analysis_nar_interval)

    def analysis_nar_interval(self, resource_info):
        nar_interval = 60
        try:
            if resource_info and ":" in resource_info:
                nar_interval_str = resource_info.split(":")[1].strip()
                nar_interval = int(nar_interval_str)
        except Exception as e:
            err_msg = "analysis sp time error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return nar_interval

    def get_archive_file_name(self, storage_id):
        tools = Tools()
        create_time = tools.timestamp_to_time_str(
            time.time() * units.k, consts.ARCHIVE_FILE_NAME_TIME_PATTERN)
        archive_file_name = consts.ARCHIVE_FILE_NAME % (storage_id,
                                                        create_time)
        return archive_file_name

    def create_archives(self, storage_id):
        archive_name = self.get_archive_file_name(storage_id)
        create_archive_api = consts.CREATE_ARCHIVE_API % (
            archive_name, self.get_local_file_path())
        self.get_resources_info(create_archive_api, self.cli_res_to_list)

        archive_name_infos = archive_name.split('.')
        archivedump_api = consts.ARCHIVEDUMP_API % (
            self.get_local_file_path(), archive_name,
            self.get_local_file_path(), archive_name_infos[0])
        self.get_resources_info(archivedump_api, self.cli_res_to_list)
        return archive_name
