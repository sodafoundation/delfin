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

    # ssh command
    HPE3PAR_COMMAND_SHOWWSAPI = 'showwsapi'
    HPE3PAR_COMMAND_CHECKHEALTH = 'checkhealth vv vlun task snmp ' \
                                  'port pd node network ld dar cage cabling'
    HPE3PAR_COMMAND_SHOWALERT = 'showalert -d'
    HPE3PAR_COMMAND_REMOVEALERT = 'removealert -f '

    def __init__(self, sshclient):
        self.sshclient = sshclient

    def login(self, context):
        """Test SSH connection """
        version = ''
        try:
            re = self.sshclient.doexec(context,
                                       SSHHandler.HPE3PAR_COMMAND_SHOWWSAPI)
            wsapiinfos = re.split('\n')
            version = self.get_version(context, wsapiinfos)
        except Exception as e:
            LOG.error('login error:{}'.format(e))
            raise e
        return version

    def get_version(self, context, wsapiinfos):
        """get wsapi version """
        version = ''
        try:
            if wsapiinfos is not None and wsapiinfos != '':
                versionseat = 7
                for wsapiinfo in wsapiinfos:
                    strline = wsapiinfo
                    if strline is not None and strline != '':
                        if '-Version-' in strline:
                            continue
                        else:
                            wsapivalues = strline.split(' ')
                            for subinfo in wsapivalues:
                                if subinfo is not None and subinfo != '':
                                    versionseat -= 1
                                    if versionseat == 0:
                                        version = subinfo
        except Exception as e:
            LOG.error('get_version error:{}'.format(e))
        return version

    def get_health_state(self, context):
        """Check the hardware and software health
           status of the storage system

           return: System is healthy
        """
        re = ''
        try:
            re = self.sshclient.doexec(context,
                                       SSHHandler.HPE3PAR_COMMAND_CHECKHEALTH)
        except Exception as e:
            LOG.error('Get health state error:{}'.format(e))
            raise e
        return re

    def get_all_alerts(self, context):
        """Get list of Hpe3parStor alerts
           return: all alerts
        """
        re = ''
        try:
            re = self.sshclient.doexec(context,
                                       SSHHandler.HPE3PAR_COMMAND_SHOWALERT)
        except Exception as e:
            LOG.error('Get all alerts error:{}'.format(e))
            raise e
        return re

    def remove_alerts(self, context, alert_id):
        """Clear alert from storage system.
            Currently not implemented   removes command : removealert
        """
        re = ''
        try:
            command_str = SSHHandler.HPE3PAR_COMMAND_REMOVEALERT + \
                alert_id
            re = self.sshclient.doexec(context, command_str)
        except Exception as e:
            LOG.error('Get all alerts error:{}'.format(e))
            raise e
        return re
