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
from delfin.tests.unit.drivers.netapp.netapp_fas import test_constans
from delfin import context
from delfin.drivers.netapp.netapp_fas.netapp_handler import NetAppHandler
from delfin.drivers.netapp.netapp_fas.netapp_fas import NetAppFasDriver
from delfin.drivers.utils.ssh_client import SSHPool


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


class TestNetAppStorageDriver(TestCase):
    SSHPool.get = mock.Mock(
        return_value={paramiko.SSHClient()})
    NetAppHandler.login = mock.Mock()
    netapp_client = NetAppFasDriver(**test_constans.ACCESS_INFO)

    def test_reset_connection(self):
        kwargs = test_constans.ACCESS_INFO
        NetAppHandler.login = mock.Mock()
        netapp_client = NetAppFasDriver(**kwargs)
        netapp_client.reset_connection(context, **kwargs)
        self.assertEqual(netapp_client.netapp_handler.ssh_pool.ssh_host,
                         "192.168.159.130")
        self.assertEqual(netapp_client.netapp_handler.ssh_pool.ssh_port, 22)

    def test_get_storage(self):
        NetAppHandler.do_exec = mock.Mock(
            side_effect=[test_constans.SYSTEM_INFO,
                         test_constans.VERSION,
                         test_constans.SYSTEM_STATUS,
                         test_constans.DISKS_INFO,
                         test_constans.PHYSICAL_INFO,
                         test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.get_storage(context)
        self.assertEqual(data['vendor'], 'NetApp')

    def test_list_storage_pools(self):
        NetAppHandler.do_exec = mock.Mock(
            side_effect=[test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.list_storage_pools(context)
        self.assertEqual(data[0]['name'], 'aggr0')

    def test_list_volumes(self):
        NetAppHandler.do_exec = mock.Mock(
            side_effect=[test_constans.LUN_INFO,
                         test_constans.FS_INFO,
                         test_constans.THIN_FS_INFO,
                         test_constans.POOLS_INFO,
                         test_constans.AGGREGATE_DETAIL_INFO])
        data = self.netapp_client.list_volumes(context)
        self.assertEqual(data[0]['name'], 'lun_0')

    def test_list_alerts(self):
        NetAppHandler.do_exec = mock.Mock(
            side_effect=[test_constans.EVENT_INFO,
                         test_constans.ALERT_INFO])
        data = self.netapp_client.list_alerts(context)
        self.assertEqual(data[0]['alert_name'],
                         'mgmtgwd.configbr.noSNCBackup')

    def test_clear_alters(self):
        alert = {'alert_id': '123'}
        NetAppHandler.do_exec = mock.Mock()
        self.netapp_client.clear_alert(context, alert)

    def test_parse_alert(self):
        data = self.netapp_client.parse_alert(context, test_constans.TRAP_MAP)
        self.assertEqual(data['alert_name'], 'LUN.inconsistent.filesystem')
