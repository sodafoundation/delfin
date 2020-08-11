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

import paramiko as paramiko

from io import StringIO

from oslo_log import log as logging

from delfin import exception

LOG = logging.getLogger(__name__)


class SSHClient(object):
    """Common class for Hpe 3parStor storage system."""
    SOCKET_TIMEOUT = 30

    def __init__(self, **kwargs):

        ssh_access = kwargs.get('ssh')
        if ssh_access is None:
            raise exception.InvalidInput('Input ssh_access is missing')
        self.ssh_host = ssh_access.get('host')
        self.ssh_port = ssh_access.get('port')
        self.ssh_username = ssh_access.get('username')
        self.ssh_password = ssh_access.get('password')
        self.ssh_private_key = ssh_access.get('host_key')
        self.ssh_conn_timeout = ssh_access.get('conn_timeout')
        if self.ssh_conn_timeout is None:
            self.ssh_conn_timeout = SSHClient.SOCKET_TIMEOUT

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.ssh_private_key is None:
            self.ssh.connect(hostname=self.ssh_host, port=self.ssh_port,
                             username=self.ssh_username,
                             password=self.ssh_password,
                             timeout=self.ssh_conn_timeout)
        else:

            private_key = \
                paramiko.RSAKey(file_obj=StringIO(self.ssh_private_key))

            self.ssh.connect(hostname=self.ssh_host, port=self.ssh_port,
                             username=self.ssh_username,
                             pkey=private_key,
                             timeout=self.ssh_conn_timeout)

    def execCommand(self, commandStr):
        result = None
        try:
            if commandStr is not None:
                if self.ssh is not None:
                    stdin, stdout, stderr = self.ssh.exec_command(commandStr)
                    res, err = stdout.read(), stderr.read()
                    re = res if res else err
                    result = re.decode()
                    LOG.info(
                        'execCommand over==commandStr=={}'.format(commandStr))
                    LOG.info('execCommand over==result=={}'.format(result))
        except Exception as e:
            LOG.error(e)
            result = e
        return result

    def close(self):
        try:
            if self.ssh is not None:
                # Close connection
                self.ssh.close()
                self.ssh = None
                LOG.info('self.ssh Close connection success')
        except Exception as e:
            LOG.error(e)

    def doexec(self, context, commandStr):
        # Currently not implemented   removes command : removealert
        """Clear alert from storage system."""
        re = None
        try:
            if commandStr is not None:
                LOG.info("sshClient commandStr==={}".format(commandStr))
                self.connect()
                re = self.execCommand(commandStr)
        except paramiko.AuthenticationException as ae:
            LOG.error('doexec==ae=={}'.format(ae))
            raise exception.NotAuthorized(
                reason='SSH Authentication failed')
        except Exception as e:
            LOG.error('doexec==e=={}'.format(e))
            raise exception.SSHException(
                reason=e)

        finally:
            self.close()
        return re

    def login(self, context):
        """Test SSH connection """
        try:
            commandStr = 'ls -l'
            self.doexec(context, commandStr)
        except Exception as e:
            LOG.error('login==e=={}'.format(e))
            raise e
