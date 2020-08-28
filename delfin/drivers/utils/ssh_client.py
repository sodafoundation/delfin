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
from oslo_log import log as logging
from paramiko.hostkeys import HostKeyEntry

from delfin import exception

LOG = logging.getLogger(__name__)


class SSHClient(object):
    SOCKET_TIMEOUT = 10

    def __init__(self, **kwargs):

        ssh_access = kwargs.get('ssh')
        if ssh_access is None:
            raise exception.InvalidInput('Input ssh_access is missing')
        self.ssh_host = ssh_access.get('host')
        self.ssh_port = ssh_access.get('port')
        self.ssh_username = ssh_access.get('username')
        self.ssh_password = ssh_access.get('password')
        self.ssh_pub_key_type = ssh_access.get('pub_key_type')
        self.ssh_pub_key = ssh_access.get('pub_key')
        self.ssh_conn_timeout = ssh_access.get('conn_timeout')
        if self.ssh_conn_timeout is None:
            self.ssh_conn_timeout = SSHClient.SOCKET_TIMEOUT

    def connect(self):
        self.ssh = paramiko.SSHClient()

        if self.ssh_pub_key is None:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        else:
            host_key = (self.ssh_host + ' ' + self.ssh_pub_key_type
                        + ' ' + self.ssh_pub_key)
            self.sethostkey(host_key)

        self.ssh.connect(hostname=self.ssh_host, port=self.ssh_port,
                         username=self.ssh_username,
                         password=self.ssh_password,
                         timeout=self.ssh_conn_timeout)

    def sethostkey(self, host_key):
        """
        Set public key,because input kwargs parameter host_key is string,
        not a file path,we can not use load file to get public key,so we set
        it as a string.
        :param str host_key: the public key which as a string
        """
        if (len(host_key) == 0) or (host_key[0] == "#"):
            return
        try:
            e = HostKeyEntry.from_line(host_key)
        except exception.SSHException:
            return
        if e is not None:
            _hostnames = e.hostnames
            for h in _hostnames:
                if self.ssh._host_keys.check(h, e.key):
                    e.hostnames.remove(h)
            if len(e.hostnames):
                self.ssh._host_keys._entries.append(e)

    def execCommand(self, command_str):
        result = None
        try:
            if command_str is not None:
                if self.ssh is not None:
                    stdin, stdout, stderr = self.ssh.exec_command(command_str)
                    res, err = stdout.read(), stderr.read()
                    re = res if res else err
                    result = re.decode()
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
        except Exception as e:
            LOG.error(e)

    def doexec(self, context, command_str):
        """Execute command"""
        re = None
        try:
            if command_str is not None:
                self.connect()
                re = self.execCommand(command_str)
        except paramiko.AuthenticationException as ae:
            LOG.error('doexec Authentication error:{}'.format(ae))
            raise exception.InvalidUsernameOrPassword()
        except Exception as e:
            LOG.error('doexec InvalidUsernameOrPassword error:{}'.format(e))
            if 'WSAETIMEDOUT' in str(e):
                raise exception.SSHConnectTimeout()
            elif 'No authentication methods available' in str(e) \
                    or 'Authentication failed' in str(e):
                raise exception.SSHInvalidUsernameOrPassword()
            elif 'not a valid RSA private key file' in str(e):
                raise exception.InvalidPrivateKey()
            elif 'not found in known_hosts' in str(e):
                raise exception.SSHNotFoundKnownHosts(self.ssh_host)
            else:
                raise exception.SSHException()

        finally:
            self.close()
        return re
