# Copyright 2021 The SODA Authors.
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

from unittest import TestCase, mock

import paramiko

from delfin.tests.unit.drivers.hitachi.hnas import test_constans
from delfin import context
from delfin.drivers.hitachi.hnas.hds_nas import HitachiHNasDriver
from delfin.drivers.utils.ssh_client import SSHPool


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


class TestHitachiHNasDriver(TestCase):
    SSHPool.get = mock.Mock(
        return_value={paramiko.SSHClient()})

    SSHPool.do_exec_command = mock.Mock(
        side_effect=[test_constans.NODE_INFO])
    hnas_client = HitachiHNasDriver(**test_constans.ACCESS_INFO)

    def test_reset_connection(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.NODE_INFO,
                         test_constans.NODE_INFO])
        kwargs = test_constans.ACCESS_INFO

        hnas_client = HitachiHNasDriver(**kwargs)
        hnas_client.reset_connection(context, **kwargs)
        self.assertEqual(hnas_client.nas_handler.ssh_pool.ssh_host,
                         "192.168.3.211")
        self.assertEqual(hnas_client.nas_handler.ssh_pool.ssh_port, 22)

    def test_get_storage(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.STORAGE_INFO,
                         test_constans.VERSION_INFO,
                         test_constans.LOCATION_INFO,
                         test_constans.DISK_INFO,
                         test_constans.POOL_INFO,
                         test_constans.POOL_DETAIL_INFO])
        data = self.hnas_client.get_storage(context)
        self.assertEqual(data['vendor'], 'HITACHI')

    def test_list_storage_pools(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.POOL_INFO,
                         test_constans.POOL_DETAIL_INFO])
        data = self.hnas_client.list_storage_pools(context)
        self.assertEqual(data[0]['name'], 'span1')

    def test_list_alerts(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.ALERT_INFO])
        data = self.hnas_client.list_alerts(context)
        self.assertEqual(data[0]['alert_name'],
                         '8462')

    def test_parse_alert(self):
        data = self.hnas_client.parse_alert(context, test_constans.TRAP_INFO)
        self.assertEqual(data['alert_name'], '8462')

    def test_list_controllers(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.NODE_INFO])
        data = self.hnas_client.list_controllers(context)
        self.assertEqual(data[0]['name'], 'pba-hnas-1-1')

    def test_list_ports(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.FC_PORT_INFO,
                         test_constans.FC_PORT_STATUS,
                         test_constans.ETH_PORT_INFO])
        data = self.hnas_client.list_ports(context)
        self.assertEqual(data[0]['name'], 'FC1')

    def test_list_disks(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.DISK_INFO])
        data = self.hnas_client.list_disks(context)
        self.assertEqual(data[0]['name'], '1000')

    def test_list_qtrees(self):
        SSHPool.do_exec_command = mock.Mock(side_effect=[
            test_constans.FS_INFO, test_constans.QTREE_INFO])
        data = self.hnas_client.list_qtrees(context)
        self.assertEqual(data[0]['name'], 'tree1')

    def test_list_shares(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.FS_INFO,
                         test_constans.CIFS_SHARE_INFO,
                         test_constans.NFS_SHARE_INFO,
                         test_constans.QTREE_INFO])
        data = self.hnas_client.list_shares(context)
        self.assertEqual(data[0]['name'], 'tree1')

    def test_list_filesystems(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.FS_DETAIL_INFO,
                         test_constans.FS_INFO])
        data = self.hnas_client.list_filesystems(context)
        self.assertEqual(data[0]['name'], 'fs1')

    def test_list_quotas(self):
        SSHPool.do_exec_command = mock.Mock(
            side_effect=[test_constans.FS_INFO,
                         test_constans.QUOTA_INFO])
        data = self.hnas_client.list_quotas(context)
        self.assertEqual(data[0]['file_soft_limit'], '213')
