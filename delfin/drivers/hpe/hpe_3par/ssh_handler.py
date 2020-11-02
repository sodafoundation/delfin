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
import six

from oslo_log import log as logging

from delfin import exception
from delfin import utils

from delfin.drivers.utils.ssh_client import SSHClient

LOG = logging.getLogger(__name__)


class SSHHandler(object):
    """Common class for Hpe 3parStor storage system."""

    HPE3PAR_COMMAND_SHOWWSAPI = 'showwsapi'
    HPE3PAR_COMMAND_CHECKHEALTH = 'checkhealth vv vlun task snmp ' \
                                  'port pd node network ld dar cage cabling'
    HPE3PAR_COMMAND_SHOWALERT = 'showalert -d'
    HPE3PAR_COMMAND_REMOVEALERT = 'removealert -f %s'
    ALERT_NOT_EXIST_MSG = 'Unable to read alert'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def login(self, context):
        """Test SSH connection """
        version = ''
        try:
            ssh_client = SSHClient(**self.kwargs)
            re = ssh_client.do_exec(SSHHandler.HPE3PAR_COMMAND_SHOWWSAPI)
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
        re = ''
        try:
            ssh_client = SSHClient(**self.kwargs)
            re = ssh_client.do_exec(
                SSHHandler.HPE3PAR_COMMAND_CHECKHEALTH)
        except Exception as e:
            LOG.error("Get health state error: %s", six.text_type(e))
            raise e
        return re

    def get_all_alerts(self):
        """Get list of Hpe3parStor alerts
           return: all alerts
        """
        re = ''
        try:
            ssh_client = SSHClient(**self.kwargs)
            re = ssh_client.do_exec(SSHHandler.HPE3PAR_COMMAND_SHOWALERT)
        except Exception as e:
            LOG.error("Get all alerts error: %s", six.text_type(e))
            raise e
        return re

    def remove_alerts(self, alert_id):
        """Clear alert from storage system.
            Currently not implemented   removes command : removealert
        """
        ssh_client = SSHClient(**self.kwargs)
        utils.check_ssh_injection([alert_id])
        command_str = SSHHandler.HPE3PAR_COMMAND_REMOVEALERT % alert_id
        res = ssh_client.do_exec(command_str)
        if res:
            if self.ALERT_NOT_EXIST_MSG not in res:
                raise exception.InvalidResults(six.text_type(res))
            LOG.warning("Alert %s doesn't exist.", alert_id)
