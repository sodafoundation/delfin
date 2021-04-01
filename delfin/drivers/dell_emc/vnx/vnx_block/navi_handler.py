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
import threading
import time

import six
from oslo_log import log as logging
from oslo_utils import units

from delfin import cryptor
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

    def get_cli_command_str(self, host_ip=None, sub_command=None):
        if host_ip is None:
            host_ip = self.navi_host
        command_str = consts.NAVISECCLI_API % {
            'username': self.navi_username,
            'password': cryptor.decode(self.navi_password),
            'host': host_ip, 'timeout': self.navi_timeout}
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
                                     sub_command=consts.GET_AGENT_API)
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
                                       self.cli_res_to_list)

    def get_raid_group(self):
        return self.get_resources_info(consts.GET_RAIDGROUP_API,
                                       self.cli_raid_to_list)

    def get_pool_lun(self):
        return self.get_resources_info(consts.GET_LUN_API,
                                       self.cli_res_to_list)

    def get_all_lun(self):
        return self.get_resources_info(consts.GET_GETALLLUN_API,
                                       self.cli_lun_to_list)

    def get_log(self, host_ip, query_para=None):
        log_list = []
        try:
            query_time_list = self.get_log_query_time_list(query_para)
            for i in range(len(query_time_list) - 1, -1, -1):
                query_time = query_time_list[i]
                command_str = consts.GET_LOG_API % {
                    'begin_time': query_time.get('begin_time'),
                    'end_time': query_time.get('end_time')}
                command_str = self.get_cli_command_str(host_ip=host_ip,
                                                       sub_command=command_str)
                result = self.navi_exe(command_str.split(), host_ip)
                if result:
                    log_list.extend(self.cli_log_to_list(result))
                else:
                    break
        except Exception as e:
            # The log query error of a single control node does not affect
            # the overall return, so only the log is recorded here,
            # and no exception is thrown
            err_msg = "Failed to get log from %s: %s" \
                      % (host_ip, six.text_type(e))
            LOG.error(err_msg)
        return log_list

    def get_log_query_time_list(self, query_para=None):
        log_query_time_list = []
        try:
            if query_para is None:
                tmp_begin = (time.time() -
                             consts.SECS_OF_DEFAULT_QUERY_LOG_DAYS) * units.k
                tmp_end = (time.time() + consts.ONE_DAY_SCE) * units.k
                query_para = {
                    'begin_time': str(tmp_begin),
                    'end_time': str(tmp_end)
                }
            begin_time_int = int(float(query_para.get('begin_time')))
            end_time_int = int(float(query_para.get('end_time')))
            next_start_time = (begin_time_int +
                               consts.SECS_OF_QUERY_TIME_RANGE_DAYS)
            if next_start_time < end_time_int:
                while (begin_time_int < end_time_int):
                    begin_time_tmp = begin_time_int
                    end_time_tmp = (begin_time_int +
                                    consts.SECS_OF_QUERY_TIME_RANGE_DAYS)
                    if end_time_tmp > end_time_int:
                        end_time_tmp = end_time_int
                    query_time = self.log_query_time_to_list(begin_time_tmp,
                                                             end_time_tmp)
                    log_query_time_list.append(query_time)
                    begin_time_int = end_time_tmp
            else:
                query_time = self.log_query_time_to_list(begin_time_int,
                                                         end_time_int)
                log_query_time_list.append(query_time)
        except Exception as e:
            err_msg = "Error splitting query time: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return log_query_time_list

    def log_query_time_to_list(self, begin_timestamp, end_timestamp):
        tools = Tools()
        begin_time = tools.timestamp_to_time_str(begin_timestamp,
                                                 consts.DATE_PATTERN)
        end_time = tools.timestamp_to_time_str(end_timestamp,
                                               consts.DATE_PATTERN)
        query_time_map = {
            'begin_time': begin_time,
            'end_time': end_time
        }
        return query_time_map

    def get_resources_info(self, sub_command, analyse_type):
        """Execute commands to query data and analyze"""
        command_str = self.get_cli_command_str(sub_command=sub_command)
        resource_info = self.navi_exe(command_str.split())
        return_value = None
        if resource_info:
            return_value = analyse_type(resource_info)
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

    def cli_log_to_list(self, resource_info):
        obj_list = []
        try:
            tools = Tools()
            # Filter log information for log codes 70-77
            pattern = re.compile(consts.LOG_FILTER_PATTERN)
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                str_line = obj_info.strip()
                if str_line:
                    search_obj = pattern.search(str_line)
                    if search_obj:
                        str_line = str_line.replace(
                            'See alerts for details.', '')
                        str_infos = str_line.split(search_obj.group())
                        str_0 = str_infos[0].strip()
                        log_time = str_0[0:str_0.rindex(' ')]
                        event_code = search_obj.group() \
                            .replace('(', '').replace(')', '')
                        obj_model = {
                            'log_time': log_time,
                            'log_time_stamp': tools.time_str_to_timestamp(
                                log_time, consts.TIME_PATTERN),
                            'event_code': event_code,
                            'message': str_infos[1].strip()
                        }
                        obj_list.append(obj_model)
        except Exception as e:
            err_msg = "arrange log info error: %s", six.text_type(e)
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
        finally:
            self.session_lock.release()
