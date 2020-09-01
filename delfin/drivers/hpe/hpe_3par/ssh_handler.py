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

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class SSHHandler(object):
    """Common class for Hpe 3parStor storage system."""

    HPE3PAR_COMMAND_SHOWWSAPI = 'showwsapi'
    HPE3PAR_COMMAND_CHECKHEALTH = 'checkhealth vv vlun task snmp ' \
                                  'port pd node network ld dar cage cabling'
    HPE3PAR_COMMAND_SHOWALERT = 'showalert -d'
    HPE3PAR_COMMAND_REMOVEALERT = 'removealert -f '

    def __init__(self, ssh_client):
        self.ssh_client = ssh_client

    def login(self):
        """SSH connection """
        version = ''
        try:
            re = self.ssh_client.do_exec(SSHHandler.HPE3PAR_COMMAND_SHOWWSAPI)
            wsapi_infos = re.split('\n')
            version = self.get_version(wsapi_infos)
        except Exception as e:
            LOG.error('Login error:{}'.format(e))
            raise e
        return version

    def get_version(self, wsapi_infos):
        """get wsapi version """
        version = ''
        try:
            if wsapi_infos is not None and wsapi_infos != '':
                version_seat = 7
                for wsapi_info in wsapi_infos:
                    str_line = wsapi_info
                    if str_line is not None and str_line != '':
                        if '-Version-' in str_line:
                            continue
                        else:
                            wsapi_values = str_line.split(' ')
                            for sub_info in wsapi_values:
                                if sub_info is not None and sub_info != '':
                                    version_seat -= 1
                                    if version_seat == 0:
                                        version = sub_info
        except Exception as e:
            LOG.error('Get version error:{}'.format(e))
        return version

    def get_health_state(self):
        """Check the hardware and software health
           status of the storage system

           return: System is healthy
        """
        re = ''
        try:
            re = self.ssh_client.do_exec(
                SSHHandler.HPE3PAR_COMMAND_CHECKHEALTH)
        except Exception as e:
            LOG.error('Get health state error:{}'.format(e))
            raise e
        return re

    def get_all_alerts(self):
        """Get list of Hpe3parStor alerts
           return: all alerts
        """
        re = ''
        try:
            re = self.ssh_client.do_exec(SSHHandler.HPE3PAR_COMMAND_SHOWALERT)
        except Exception as e:
            LOG.error('Get all alerts error:{}'.format(e))
            raise e
        return re

    def remove_alerts(self, alert_id):
        """Clear alert from storage system.
        """
        re = ''
        try:
            command_str = SSHHandler.HPE3PAR_COMMAND_REMOVEALERT + alert_id
            re = self.ssh_client.do_exec(command_str)
        except Exception as e:
            LOG.error('Clear alert error:{}'.format(e))
            raise e
        return re
