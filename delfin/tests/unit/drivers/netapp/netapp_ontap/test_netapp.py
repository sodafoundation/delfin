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

import paramiko
from delfin.tests.unit.drivers.netapp.netapp_ontap import test_constans
from delfin import context
from delfin.drivers.netapp.dataontap.netapp_handler import NetAppHandler
from delfin.drivers.netapp.dataontap.cluster_mode import NetAppCmodeDriver
from delfin.drivers.utils.ssh_client import SSHPool


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


class TestNetAppCmodeDriver(TestCase):
    SSHPool.get = mock.Mock(
        return_value={paramiko.SSHClient()})

    NetAppHandler.login = mock.Mock()
    netapp_client = NetAppCmodeDriver(**test_constans.ACCESS_INFO)

    def test_reset_connection(self):
        kwargs = test_constans.ACCESS_INFO
        NetAppHandler.login = mock.Mock()
        netapp_client = NetAppCmodeDriver(**kwargs)
        netapp_client.reset_connection(context, **kwargs)
        self.assertEqual(netapp_client.netapp_handler.ssh_pool.ssh_host,
                         "192.168.159.130")
        self.assertEqual(netapp_client.netapp_handler.ssh_pool.ssh_port, 22)

    def test_get_storage(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.SYSTEM_INFO,
                         test_constans.VERSION,
                         test_constans.SYSTEM_STATUS,
                         test_constans.CONTROLLER_INFO,
                         test_constans.DISKS_INFO,
                         test_constans.PHYSICAL_INFO,
                         test_constans.ERROR_DISK_INFO,
                         test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.get_storage(context)
        self.assertEqual(data['vendor'], 'netapp')

    def test_list_storage_pools(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.list_storage_pools(context)
        self.assertEqual(data[0]['name'], 'aggr0')

    def test_list_volumes(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.LUN_INFO,
                         test_constans.FS_INFO,
                         test_constans.THIN_FS_INFO,
                         test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.list_volumes(context)
        self.assertEqual(data[0]['name'], 'lun_0')

    def test_list_alerts(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.EVENT_INFO,
                         test_constans.ALERT_INFO])
        data = self.netapp_client.list_alerts(context)
        self.assertEqual(data[0]['alert_name'],
                         'mgmtgwd.configbr.noSNCBackup')

    def test_clear_alters(self):
        alert = {'alert_id': '123'}
        SSHPool.do_exec = mock.Mock()
        self.netapp_client.clear_alert(context, alert)

    def test_parse_alert(self):
        data = self.netapp_client.parse_alert(context, test_constans.TRAP_MAP)
        self.assertEqual(data['alert_name'], 'LUN.inconsistent.filesystem')

    def test_list_controllers(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.CONTROLLER_INFO])
        data = self.netapp_client.list_controllers(context)
        self.assertEqual(data[0]['name'], 'cl-01')

    def test_list_ports(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.FC_PORT_INFO,
                         test_constans.PORTS_INFO])
        data = self.netapp_client.list_ports(context)
        self.assertEqual(data[0]['name'], 'cl-01:0a')

    def test_list_disks(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.DISKS_INFO,
                         test_constans.PHYSICAL_INFO,
                         test_constans.ERROR_DISK_INFO])
        data = self.netapp_client.list_disks(context)
        self.assertEqual(data[0]['name'], 'NET-1.1')

    def test_list_qtrees(self):
        SSHPool.do_exec = mock.Mock(side_effect=[
            test_constans.QTREES_INFO, test_constans.FS_INFO])
        data = self.netapp_client.list_qtrees(context)
        self.assertEqual(data[0]['security_mode'], 'ntfs')

    def test_list_shares(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.QTREES_INFO,
                         test_constans.FS_INFO,
                         test_constans.SHARES_AGREEMENT_INFO,
                         test_constans.SHARE_VSERVER_INFO,
                         test_constans.SHARES_INFO,
                         test_constans.NFS_SHARE_INFO])
        data = self.netapp_client.list_shares(context)
        self.assertEqual(data[0]['name'], 'admin$')

    def test_list_filesystems(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.FS_INFO,
                         test_constans.THIN_FS_INFO,
                         test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.list_filesystems(context)
        self.assertEqual(data[0]['name'], 'vol0')

    def test_list_quotas(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.QUOTAS_INFO])
        data = self.netapp_client.list_quotas(context)
        self.assertEqual(data[0]['file_soft_limit'], 1000)

    def test_ge_alert_sources(self):
        SSHPool.do_exec = mock.Mock(
            side_effect=[test_constans.NODE_IPS_INFO,
                         test_constans.CLUSTER_IPS_INFO])
        data = self.netapp_client.get_alert_sources(context)
        self.assertEqual(data[0]['host'], '192.168.159.131')
