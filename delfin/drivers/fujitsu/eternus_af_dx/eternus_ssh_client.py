# Copyright 2020 The SODA Authors.
# Copyright 2011 OpenStack LLC
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
import time

import paramiko
import six
from oslo_log import log as logging
from cryptography.hazmat.primitives.asymmetric import dsa

from delfin import cryptor
from delfin import exception, utils
from delfin.drivers.utils.ssh_client import SSHPool

LOG = logging.getLogger(__name__)


def override_check_dsa_parameters(parameters):
    if parameters.p.bit_length() not in [512, 1024, 2048, 3072, 4096]:
        raise ValueError(
            "p must be exactly 1024, 2048, 3072, or 4096 bits long"
        )
    if parameters.q.bit_length() not in [160, 224, 256]:
        raise ValueError("q must be exactly 160, 224, or 256 bits long")

    if not (1 < parameters.g < parameters.p):
        raise ValueError("g, p don't satisfy 1 < g < p.")


dsa._check_dsa_parameters = override_check_dsa_parameters


class EternusSSHPool(SSHPool):
    def create(self):
        ssh = paramiko.SSHClient()
        try:
            if self.ssh_pub_key is None:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                host_key = '%s %s %s' % \
                           (self.ssh_host, self.ssh_pub_key_type,
                            self.ssh_pub_key)
                self.set_host_key(host_key, ssh)
            try:
                ssh.connect(hostname=self.ssh_host, port=self.ssh_port,
                            username=self.ssh_username,
                            password=cryptor.decode(self.ssh_password),
                            timeout=self.ssh_conn_timeout)
            except Exception as e:
                if 'Authentication failed' in six.text_type(e):
                    ssh.connect(hostname=self.ssh_host, port=self.ssh_port,
                                username=self.ssh_username,
                                password=cryptor.decode(self.ssh_password),
                                timeout=self.ssh_conn_timeout,
                                look_for_keys=False)
                else:
                    raise
            if self.conn_timeout:
                transport = ssh.get_transport()
                transport.set_keepalive(self.SOCKET_TIMEOUT)
            return ssh
        except Exception as e:
            err = six.text_type(e)
            LOG.error(err)
            if 'timed out' in err:
                raise exception.InvalidIpOrPort()
            elif 'No authentication methods available' in err \
                    or 'Authentication failed' in err:
                raise exception.InvalidUsernameOrPassword()
            elif 'not a valid RSA private key file' in err:
                raise exception.InvalidPrivateKey()
            elif 'not found in known_hosts' in err:
                raise exception.SSHNotFoundKnownHosts(self.ssh_host)
            else:
                raise exception.SSHException(err)

    def do_exec_shell(self, command_list):
        result = ''
        try:
            with self.item() as ssh:
                if command_list and ssh:
                    channel = ssh.invoke_shell()
                    for command in command_list:
                        utils.check_ssh_injection(command)
                        channel.send(command + '\r\n')
                        time.sleep(0.5)
                    channel.send("exit" + "\r\n")
                    channel.close()
                    while True:
                        resp = channel.recv(9999).decode('utf8')
                        if not resp:
                            time.sleep(0.5)
                            break
                        result += resp
            if 'is not a recognized command' in result \
                    or 'Unknown command' in result \
                    or 'Bad command' in result:
                raise exception.StorageBackendException(result)
        except paramiko.AuthenticationException as ae:
            LOG.error('doexec Authentication error:{}'.format(ae))
            raise exception.InvalidUsernameOrPassword()
        except Exception as e:
            err = six.text_type(e)
            LOG.error(err)
            if 'timed out' in err \
                    or 'SSH connect timeout' in err:
                raise exception.SSHConnectTimeout()
            elif 'No authentication methods available' in err \
                    or 'Authentication failed' in err \
                    or 'Invalid username or password' in err:
                raise exception.InvalidUsernameOrPassword()
            elif 'not a valid RSA private key file' in err \
                    or 'not a valid RSA private key' in err:
                raise exception.InvalidPrivateKey()
            elif 'Unable to connect to port' in err \
                    or 'Invalid ip or port' in err:
                raise exception.InvalidIpOrPort()
            else:
                raise exception.SSHException(err)
        return result
