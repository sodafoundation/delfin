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
import copy
import re
import time
import six
from oslo_log import log as logging
from oslo_utils import units
from delfin import cryptor
from delfin import exception
from delfin.drivers.utils.navicli_client import NaviClient
from delfin.drivers.utils.tools import Tools

LOG = logging.getLogger(__name__)


class NaviHandler(object):
    """Common class for EMC VNX storage system."""

    USER_SECURITY_API = ['naviseccli', '-AddUserSecurity', '-User',
                         '(username)', '-password', '(password)', '-h',
                         '(host)', '-scope', '0', '-t', '(timeout)']
    REMOVEUSERSECURITY_API = ['naviseccli', '-RemoveUserSecurity']
    GET_AGENT_API = ['naviseccli', '-h', '(host)', 'getagent']
    GET_DOMAIN_API = ['naviseccli', '-h', '(host)', 'domain', '-list']
    GET_STORAGEPOOL_API = ['naviseccli', '-h', '(host)', 'storagepool',
                           '-list']
    GET_RAIDGROUP_API = ['naviseccli', '-h', '(host)', 'getall', '-rg']
    GET_DISK_API = ['naviseccli', '-h', '(host)', 'getdisk']
    GET_LUN_API = ['naviseccli', '-h', '(host)', 'lun', '-list']
    GET_GETALLLUN_API = ['naviseccli', '-h', '(host)', 'getall', '-lun']
    GET_LOG_API = ['naviseccli', '-h', '(host)', 'getlog', '-date',
                   '(begin_time)', '(end_time)']

    TIME_PATTERN = '%m/%d/%Y %H:%M:%S'
    DATE_PATTERN = '%m/%d/%Y'
    ONE_DAY_SCE = 24 * 60 * 60
    SOCKET_TIMEOUT = 5

    def __init__(self, **kwargs):
        ssh_access = kwargs.get('ssh')
        if ssh_access is None:
            raise exception.InvalidInput('Input navicli_access is missing')
        self.navi_host = ssh_access.get('host')
        self.navi_port = ssh_access.get('port')
        self.navi_username = ssh_access.get('username')
        self.navi_password = cryptor.decode(ssh_access.get('password'))
        self.navi_timeout = ssh_access.get('conn_timeout')
        if self.navi_timeout is None:
            self.navi_timeout = NaviClient.SOCKET_TIMEOUT

    def login(self, host_ip=None):
        """Test connection """
        version = ''
        try:
            if host_ip is None:
                host_ip = self.navi_host
            navi_client = NaviClient()
            command_str = [item.replace('(username)', self.navi_username) for
                           item in self.USER_SECURITY_API]
            command_str = [item.replace('(password)', self.navi_password) for
                           item in command_str]
            command_str = [item.replace('(host)', host_ip) for item in
                           command_str]
            command_str = [item.replace('(timeout)', str(self.navi_timeout))
                           for item in command_str]
            if self.navi_port:
                command_str.append('-port')
                command_str.append(str(self.navi_port))
            navi_client.exec(command_str)
            command_str = [item.replace('(host)', host_ip) for item in
                           self.GET_AGENT_API]
            result = navi_client.exec(command_str)
            if result:
                agent_model = self.arrange_resource_obj(result)
                if agent_model:
                    version = agent_model.get("revision")
        except exception.NaviCliConnectTimeout as e:
            raise e
        except Exception as e:
            err_msg = "Login error: %s" % (six.text_type(e))
            raise exception.InvalidResults(err_msg)
        return version

    def logout(self, context):
        """Logout."""
        try:
            navi_client = NaviClient()
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.REMOVEUSERSECURITY_API]
            navi_client.exec(command_str)
        except exception.NaviCallerNotPrivileged as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_agent(self):
        """get agent info"""
        agent_model = {}
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_AGENT_API]
            result = self.navi_exe(command_str)
            if result:
                agent_model = self.arrange_resource_obj(result)
        except Exception as e:
            LOG.error("get agent info error: %s", six.text_type(e))
            raise e
        return agent_model

    def get_domain(self):
        """get domain info"""
        domain_model = {}
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_DOMAIN_API]
            result = self.navi_exe(command_str)
            if result:
                domain_model = self.arrange_domain_obj(result)
        except Exception as e:
            LOG.error("get domain info error: %s", six.text_type(e))
            raise e
        return domain_model

    def get_pools(self):
        """get storage pools info"""
        pool_list = []
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_STORAGEPOOL_API]
            result = self.navi_exe(command_str)
            if result:
                pool_list = self.arrange_resource_list(result)
        except Exception as e:
            LOG.error("get pool info error: %s", six.text_type(e))
            raise e
        return pool_list

    def get_disks(self):
        """get storage disks info"""
        disk_list = []
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_DISK_API]
            result = self.navi_exe(command_str)
            if result:
                disk_list = self.arrange_resource_list(result)
        except Exception as e:
            LOG.error("get disk info error: %s", six.text_type(e))
            raise e
        return disk_list

    def get_raid_group(self):
        """get storage raids info"""
        raid_list = []
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_RAIDGROUP_API]
            result = self.navi_exe(command_str)
            if result:
                raid_list = self.arrange_raid_list(result)
        except Exception as e:
            LOG.error("get raid group info error: %s", six.text_type(e))
            raise e
        return raid_list

    def get_pool_lun(self):
        """get storage luns info"""
        lun_list = []
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_LUN_API]
            result = self.navi_exe(command_str)
            if result:
                lun_list = self.arrange_resource_list(result)
        except Exception as e:
            LOG.error("get lun info error: %s", six.text_type(e))
            raise e
        return lun_list

    def get_all_lun(self):
        """get all luns info"""
        lun_list = []
        try:
            command_str = [item.replace('(host)', self.navi_host) for item in
                           self.GET_GETALLLUN_API]
            result = self.navi_exe(command_str)
            if result:
                lun_list = self.arrange_lun_list(result)
        except Exception as e:
            LOG.error("get lun info error: %s", six.text_type(e))
            raise e
        return lun_list

    def get_log(self, host_ip, query_para=None):
        """get log info"
           query_para is an optional para which contains 'begin_time' and
                'end_time' (in milliseconds) which is to be used to filter
                alerts at driver
        """
        log_list = []
        try:
            begin_time = ''
            end_time = ''
            tools = Tools()
            if query_para is not None and len(query_para) > 1:
                if query_para.get('begin_time') and query_para.get('end_time'):
                    begin_time = tools.get_time_str(
                        query_para.get('begin_time'), self.DATE_PATTERN)
                    end_time = tools.get_time_str(query_para.get('end_time'),
                                                  self.DATE_PATTERN)
            if begin_time == '':
                # Get the current time and 10 days ago
                tmp_begin = (time.time() - (9 * self.ONE_DAY_SCE)) * units.k
                tmp_end = (time.time() + self.ONE_DAY_SCE) * units.k
                begin_time = tools.get_time_str(tmp_begin, self.DATE_PATTERN)
                end_time = tools.get_time_str(tmp_end, self.DATE_PATTERN)

            if host_ip is None or host_ip == '':
                host_ip = self.navi_host
            command_str = [item.replace('(host)', host_ip) for item in
                           self.GET_LOG_API]
            command_str = [item.replace('(begin_time)', begin_time) for item in
                           command_str]
            command_str = [item.replace('(end_time)', end_time) for item in
                           command_str]
            result = self.navi_exe(command_str, host_ip)
            if result:
                log_list = self.arrange_log_list(result)
        except Exception as e:
            LOG.error("get log info error: %s", six.text_type(e))
            raise e
        return log_list

    def arrange_resource_obj(self, resource_info):
        """arrange resource info"""
        obj_model = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                strline = obj_info.strip()
                if strline and strline != '':
                    if ':' in strline:
                        strinfo = self.get_strinfo(strline)
                        key = None
                        value = None
                        if len(strinfo) > 1:
                            key = strinfo[0]
                            value = strinfo[1]
                        elif len(strinfo) == 1:
                            key = strinfo[0]
                        obj_model[key] = value

        except Exception as e:
            err_msg = "arrange resource info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_model

    def arrange_resource_list(self, resource_info):
        """arrange resource info"""
        obj_list = []
        map = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                strline = obj_info.strip()
                if strline and strline != '':
                    if 'Bus 0 Enclosure 0  Disk' in strline:
                        strline = strline.replace("Bus 0 Enclosure 0  Disk",
                                                  "disk id:")
                    if 'LOGICAL UNIT NUMBER' in strline:
                        strline = strline.replace("LOGICAL UNIT NUMBER",
                                                  "lun id:")
                    if ':' not in strline:
                        continue
                    strinfo = self.get_strinfo(strline)
                    key = None
                    value = None
                    if len(strinfo) > 1:
                        key = strinfo[0]
                        value = strinfo[1]
                    elif len(strinfo) == 1:
                        key = strinfo[0]
                    map[key] = value
                else:
                    if len(map) > 0:
                        objmap = copy.deepcopy(map)
                        obj_list.append(objmap)
                        map = {}

        except Exception as e:
            err_msg = "arrange resource info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def arrange_raid_list(self, resource_info):
        """arrange resource info"""
        obj_list = []
        map = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                strline = obj_info.strip()
                if strline and strline.startswith('RaidGroup ID:'):
                    if len(map) > 0:
                        objmap = copy.deepcopy(map)
                        obj_list.append(objmap)
                        map = {}
                if strline and strline != '':
                    if ':' not in strline:
                        continue
                    strinfo = self.get_strinfo(strline)
                    key = None
                    value = None
                    if len(strinfo) > 1:
                        key = strinfo[0]
                        value = strinfo[1]
                    elif len(strinfo) == 1:
                        key = strinfo[0]
                    map[key] = value

            if len(map) > 0:
                objmap = copy.deepcopy(map)
                obj_list.append(objmap)
                map = {}
        except Exception as e:
            err_msg = "arrange resource info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def arrange_domain_obj(self, resource_info):
        """arrange domain info"""
        obj_list = []
        map = {}
        try:
            obj_infos = resource_info.split('\n')
            node_value = ''
            for obj_info in obj_infos:
                strline = obj_info.strip()
                if strline and strline.startswith('IP Address:'):
                    if len(map) > 0:
                        objmap = copy.deepcopy(map)
                        obj_list.append(objmap)
                        map = {}
                if strline and strline != '':
                    if 'Master' in strline:
                        strline = strline.replace('(Master)', '')
                        map['master'] = 'True'
                    strinfo = self.get_strinfo(strline)
                    if strline and strline.startswith('Node:'):
                        node_value = strinfo[1]
                        continue
                    if strline and strline.startswith('IP Address:'):
                        map['node'] = node_value
                    key = None
                    value = None
                    if len(strinfo) > 1:
                        key = strinfo[0]
                        value = strinfo[1]
                    elif len(strinfo) == 1:
                        key = strinfo[0]
                    map[key] = value

            if len(map) > 0:
                objmap = copy.deepcopy(map)
                obj_list.append(objmap)
                map = {}
        except Exception as e:
            err_msg = "arrange domain info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def arrange_lun_list(self, resource_info):
        """arrange resource info"""
        obj_list = []
        map = {}
        try:
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                strline = obj_info.strip()
                if strline and strline.startswith('LOGICAL UNIT NUMBER '):
                    if len(map) > 0:
                        objmap = copy.deepcopy(map)
                        obj_list.append(objmap)
                        map = {}
                if strline and strline != '':
                    if strline.startswith('LOGICAL UNIT NUMBER '):
                        strline = strline.replace('LOGICAL UNIT NUMBER ',
                                                  'LOGICAL UNIT NUMBER:')
                    if strline.startswith('Name                        '):
                        strline = strline.replace(
                            'Name                        ', 'Name:')
                    if ':' not in strline:
                        continue
                    strinfo = self.get_strinfo(strline)
                    key = None
                    value = None
                    if len(strinfo) > 1:
                        key = strinfo[0]
                        value = strinfo[1]
                    elif len(strinfo) == 1:
                        key = strinfo[0]
                    map[key] = value

            if len(map) > 0:
                objmap = copy.deepcopy(map)
                obj_list.append(objmap)
                map = {}
        except Exception as e:
            err_msg = "arrange resource info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def arrange_log_list(self, resource_info):
        """arrange log info"""
        obj_list = []
        try:
            tools = Tools()
            pattern = re.compile(r'\(7[0-7]([a-f]|[0-9]){2}\)')
            obj_infos = resource_info.split('\n')
            for obj_info in obj_infos:
                strline = obj_info.strip()
                if strline and strline != '':
                    searchObj = pattern.search(strline)
                    if searchObj:
                        strline = strline.replace(
                            'See alerts for details.', '')
                        strinfos = strline.split(searchObj.group())
                        str_0 = strinfos[0].strip()
                        log_time = str_0[0:str_0.rindex(' ')]
                        event_code = searchObj.group() \
                            .replace('(', '').replace(')', '')
                        map = {
                            'log_time': log_time,
                            'log_time_stamp': tools.get_time_stamp(
                                log_time, self.TIME_PATTERN),
                            'event_code': event_code,
                            'message': strinfos[1].strip()
                        }
                        obj_list.append(map)
        except Exception as e:
            err_msg = "arrange resource info error: %s", six.text_type(e)
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
        return obj_list

    def get_strinfo(self, strline):
        strinfo = []
        if strline and strline != '':
            strinfo = strline.split(':', 1)
            strinfo[0] = strinfo[0].strip()
            strinfo[0] = strinfo[0].replace(" ", "_") \
                .replace("(", "").replace(")", "").lower()
            if len(strinfo) > 1:
                strinfo[1] = strinfo[1].strip()
        return strinfo

    def navi_exe(self, command_str, host_ip=None):
        try:
            if command_str:
                navi_client = NaviClient()
                result = navi_client.exec(command_str)
                return result
        except exception.NaviCallerNotPrivileged as e:
            LOG.error("execute navicli error: %s", six.text_type(e))
            self.login(host_ip)
            navi_client = NaviClient()
            result = navi_client.exec(command_str)
            return result
        except exception.NaviCliConnectTimeout as e:
            raise e
        except Exception as e:
            err_msg = six.text_type(e)
            raise exception.InvalidResults(err_msg)
