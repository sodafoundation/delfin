# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase, mock
import unittest

from delfin import context
from delfin.drivers.ibm.v7000.v7000stor import IbmDriver
from delfin.drivers.ibm.v7000.ssh_handler import SSHHandler
from delfin.drivers.utils.ssh_client import SSHClient


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "hpe",
    "model": "3par",
    "rest": {
        "host": "10.0.0.1",
        "port": 8443,
        "username": "user",
        "password": "pass"
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "pass"
    }
}


def create_driver():
    kwargs = ACCESS_INFO

    SSHHandler.login = mock.Mock(
        return_value={"result": "success", "reason": "null"})

    return IbmDriver(**kwargs)


class TestIbmv7000StorageDriver(TestCase):

    def test_a_init(self):
        kwargs = ACCESS_INFO
        with self.assertRaises(Exception) as exc:
            IbmDriver(**kwargs)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))

    def test_b_initssh(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            command_str = 'help'
            ssh_client = SSHClient(**driver.ssh_hanlder.kwargs)
            ssh_client.do_exec(command_str)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))

    def test_c_get_storage(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            command_str = 'lssystem'
            ssh_client = SSHClient(**driver.ssh_hanlder.kwargs)
            ssh_client.do_exec(command_str)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))

    def test_d_list_storage_pools(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            command_str = 'lsmdiskgrp'
            ssh_client = SSHClient(**driver.ssh_hanlder.kwargs)
            ssh_client.do_exec(command_str)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))

    def test_e_list_volumes(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            command_str = 'lsvdisk'
            ssh_client = SSHClient(**driver.ssh_hanlder.kwargs)
            ssh_client.do_exec(command_str)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))

    def test_f_list_alerts(self):
        driver = create_driver()
        with self.assertRaises(Exception) as exc:
            command_str = 'lseventlog -filtervalue "status=alert"'
            ssh_client = SSHClient(**driver.ssh_hanlder.kwargs)
            ssh_client.do_exec(command_str)
        self.assertIn('Exception in SSH protocol negotiation or logic',
                      str(exc.exception))


if __name__ == '__main__':
    unittest.main()
