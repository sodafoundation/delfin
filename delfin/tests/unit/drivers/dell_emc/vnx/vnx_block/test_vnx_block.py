# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import time
from unittest import TestCase, mock

from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.utils.tools import Tools

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.dell_emc.vnx.vnx_block.navi_handler import NaviHandler
from delfin.drivers.dell_emc.vnx.vnx_block.navicli_client import NaviClient
from delfin.drivers.dell_emc.vnx.vnx_block.vnx_block import VnxBlockStorDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vnx_block",
    "cli": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    }
}
AGENT_INFOS = """
    Agent Rev:           7.33.1 (0.38)
    Name:                K10
    Desc:
    Revision:            05.33.000.5.038
    Model:               VNX5400
    Serial No:           CETV00000001
"""
DOMAIN_INFOS = """
Node: APM00011111111
IP Address: 111.222.33.55
(Master)
Name: CX300I_33_55
Port: 80
Secure Port: 443
IP Address: 111.222.33.44
Name: CX300I_33_44
Port: 80
Secure Port: 443
"""
DISK_INFOS = """
        Bus 0 Enclosure 0  Disk 0
        State:                   Enabled
        Capacity:                54969
        """
POOL_INFOS = """
        Pool Name:  Pool 1
        Pool ID:  1
        Description:
        State:  Offline
        Status:  Storage Pool requires recovery. service provider(0x712d8518)
        User Capacity (GBs):  8583.732
        Consumed Capacity (GBs):  8479.780
        Available Capacity (GBs):  103.953
        Total Subscribed Capacity (GBs):  8479.780
        """
RAID_INFOS = """
        RaidGroup ID:                              0
        RaidGroup State:                           Valid_luns
        Raw Capacity (Blocks):                     1688426496
        Logical Capacity (Blocks):                 1688420352
        Free Capacity (Blocks,non-contiguous):     522260480
        """
LUN_INFOS = """
        LOGICAL UNIT NUMBER 239
        Name:  sun_data_VNX_2
        User Capacity (GBs):  9.000
        Consumed Capacity (GBs):  1.753
        Pool Name:  Migration_pool
        Current State:  Ready
        Status:  OK(0x0)
        Is Thin LUN:  Yes
        Is Compressed:  No
        """
GET_ALL_LUN_INFOS = """
        LOGICAL UNIT NUMBER 186
        Name                        LN_10G_01
        RAIDGroup ID:               1
        State:                      Bound
        LUN Capacity(Megabytes):    10240
        Is Thin LUN:                YES
        """

CER_INFOS = """
-----------------------------
Subject:CN=TrustedRoot,C=US,ST=MA,L=Hopkinton,EMAIL=rsa@emc.com,OU=CSP,O=RSA
Issuer:1.1.1.1
Serial#: 00d8280b0c863f6d4e
Valid From: 20090407135111Z
Valid To: 20190405135111Z
-----------------------------
Subject:CN=TrustedRoot,C=US,ST=MA,L=Hopkinton,EMAIL=rsa@emc.com,OU=CSP,O=RSA
Issuer:110.143.132.231
Serial#: 00d8280b0c863f6d4e
Valid From: 20090407135111Z
Valid To: 20190405135111Z
        """

AGENT_RESULT = {
    'agent_rev': '7.33.1 (0.38)',
    'name': 'K10',
    'desc': '',
    'revision': '05.33.000.5.038',
    'model': 'VNX5400',
    'serial_no': 'CETV00000001'
}
STORAGE_RESULT = {
    'name': 'APM00011111111',
    'vendor': 'DELL EMC',
    'model': 'VNX5400',
    'status': 'normal',
    'serial_number': 'CETV00000001',
    'firmware_version': '05.33.000.5.038',
    'total_capacity': 10081183274631,
    'raw_capacity': 57639174144,
    'used_capacity': 9702168298782,
    'free_capacity': 379016049590
}
DOMAIN_RESULT = [
    {
        'node': 'APM00011111111',
        'ip_address': '111.222.33.55',
        'master': 'True',
        'name': 'CX300I_33_55',
        'port': '80',
        'secure_port': '443'
    }]
POOLS_RESULT = [
    {
        'name': 'Pool 1',
        'storage_id': '12345',
        'native_storage_pool_id': '1',
        'description': '',
        'status': 'offline',
        'storage_type': 'block',
        'total_capacity': 9216712054407,
        'subscribed_capacity': 9105094444318,
        'used_capacity': 9105094444318,
        'free_capacity': 111618683830
    }]
RAID_RESULT = [
    {
        'raidgroup_id': '0',
        'raidgroup_state': 'Valid_luns',
        'raw_capacity_blocks': '1688426496',
        'logical_capacity_blocks': '1688420352',
        'free_capacity_blocks,non-contiguous': '522260480'
    }]
ALL_LUN_RESULT = [
    {
        'logical_unit_number': '186',
        'name': 'LN_10G_01',
        'raidgroup_id': '1',
        'state': 'Bound',
        'lun_capacitymegabytes': '10240',
        'is_thin_lun': 'YES'
    }]
POOLS_ANALYSE_RESULT = [{
    'pool_name': 'Pool 1',
    'pool_id': '1',
    'description': '',
    'state': 'Offline',
    'status': 'Storage Pool requires recovery. service provider(0x712d8518)',
    'user_capacity_gbs': '8583.732',
    'consumed_capacity_gbs': '8479.780',
    'available_capacity_gbs': '103.953',
    'total_subscribed_capacity_gbs': '8479.780'
}]
VOLUMES_RESULT = [
    {
        'name': 'sun_data_VNX_2',
        'storage_id': '12345',
        'status': 'normal',
        'native_volume_id': '239',
        'native_storage_pool_id': '',
        'type': 'thin',
        'total_capacity': 9663676416,
        'used_capacity': 1882269417,
        'free_capacity': 7781406998,
        'compressed': False,
        'wwn': None
    }]
ALERTS_RESULT = [
    {
        'alert_id': '0x76cc',
        'alert_name': 'Navisphere Agent, version 7.33',
        'severity': 'Critical',
        'category': 'Fault',
        'type': 'EquipmentAlarm',
        'occur_time': 1585114217000,
        'description': 'Navisphere Agent, version 7.33',
        'resource_type': 'Storage',
        'match_key': 'b969bbaa22b62ebcad4074618cc29b94'
    }]
ALERT_RESULT = {
    'alert_id': '0x761f',
    'alert_name': 'Unisphere can no longer manage',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1614310456716,
    'description': 'Unisphere can no longer manage',
    'resource_type': 'Storage',
    'match_key': '8e97fe0af779d78bad8f2de52e15c65c'
}


def create_driver():
    NaviHandler.login = mock.Mock(return_value={"05.33.000.5.038_test"})
    return VnxBlockStorDriver(**ACCESS_INFO)


class TestVnxBlocktorageDriver(TestCase):
    driver = create_driver()

    def test_init(self):
        NaviHandler.login = mock.Mock(return_value="05.33.000.5.038_test")
        vnx = VnxBlockStorDriver(**ACCESS_INFO)
        self.assertEqual(vnx.version, "05.33.000.5.038_test")

    def test_get_storage(self):
        NaviClient.exec = mock.Mock(
            side_effect=[DOMAIN_INFOS, AGENT_INFOS, DISK_INFOS, POOL_INFOS,
                         RAID_INFOS])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, STORAGE_RESULT)

    def test_get_pools(self):
        NaviClient.exec = mock.Mock(side_effect=[POOL_INFOS, RAID_INFOS])
        pools = self.driver.list_storage_pools(context)
        self.assertDictEqual(pools[0], POOLS_RESULT[0])

    def test_get_volumes(self):
        NaviClient.exec = mock.Mock(
            side_effect=[LUN_INFOS, POOL_INFOS, GET_ALL_LUN_INFOS])
        volumes = self.driver.list_volumes(context)
        self.assertDictEqual(volumes[0], VOLUMES_RESULT[0])

    def test_get_alerts(self):
        with self.assertRaises(Exception) as exc:
            self.driver.list_alerts(context, None)
        self.assertIn('Driver API list_alerts() is not Implemented',
                      str(exc.exception))

    def test_parse_alert(self):
        alert = {
            '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1981.0.6',
            '1.3.6.1.4.1.1981.1.4.3': 'A-CETV00000001',
            '1.3.6.1.4.1.1981.1.4.4': 'K10',
            '1.3.6.1.4.1.1981.1.4.5': '761f',
            '1.3.6.1.4.1.1981.1.4.6': 'Unisphere can no longer manage',
            '1.3.6.1.4.1.1981.1.4.7': 'VNX5400'
        }
        alert = self.driver.parse_alert(context, alert)
        ALERT_RESULT['occur_time'] = alert['occur_time']
        self.assertDictEqual(alert, ALERT_RESULT)

    def test_cli_res_to_dict(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        agent_re = navi_handler.cli_res_to_dict(AGENT_INFOS)
        self.assertDictEqual(agent_re, AGENT_RESULT)

    def test_cli_res_to_list(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        re_list = navi_handler.cli_res_to_list(POOL_INFOS)
        self.assertDictEqual(re_list[0], POOLS_ANALYSE_RESULT[0])

    def test_cli_domain_to_dict(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        re_list = navi_handler.cli_domain_to_dict(DOMAIN_INFOS)
        self.assertDictEqual(re_list[0], DOMAIN_RESULT[0])

    def test_cli_lun_to_list(self):
        navi_handler = NaviHandler(**ACCESS_INFO)
        re_list = navi_handler.cli_lun_to_list(GET_ALL_LUN_INFOS)
        self.assertDictEqual(re_list[0], ALL_LUN_RESULT[0])

    @mock.patch.object(NaviClient, 'exec')
    def test_init_cli(self, mock_exec):
        mock_exec.return_value = 'test'
        navi_handler = NaviHandler(**ACCESS_INFO)
        re = navi_handler.navi_exe('abc')
        self.assertEqual(re, 'test')
        self.assertEqual(mock_exec.call_count, 1)

    @mock.patch.object(NaviClient, 'exec')
    def test_remove_cer(self, mock_exec):
        navi_handler = NaviHandler(**ACCESS_INFO)
        navi_handler.remove_cer()
        self.assertEqual(mock_exec.call_count, 1)

    def test_err_cli_res_to_dict(self):
        with self.assertRaises(Exception) as exc:
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.cli_res_to_dict({})
        self.assertIn('arrange resource info error', str(exc.exception))

    def test_err_cli_res_to_list(self):
        with self.assertRaises(Exception) as exc:
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.cli_res_to_list({})
        self.assertIn('cli resource to list error', str(exc.exception))

    @mock.patch.object(time, 'mktime')
    def test_time_str_to_timestamp(self, mock_mktime):
        tools = Tools()
        log_time = '03/26/2021 14:25:36'
        tools.time_str_to_timestamp(log_time, consts.TIME_PATTERN)
        self.assertEqual(mock_mktime.call_count, 1)

    @mock.patch.object(time, 'strftime')
    def test_timestamp_to_time_str(self, mock_strftime):
        tools = Tools()
        timestamp = 1616739936000
        tools.timestamp_to_time_str(timestamp, consts.TIME_PATTERN)
        self.assertEqual(mock_strftime.call_count, 1)

    def test_cli_exec(self):
        with self.assertRaises(Exception) as exc:
            command_str = 'abc'
            NaviClient.exec(command_str)
        self.assertIn('Component naviseccli could not be found',
                      str(exc.exception))

    def test_analyse_cer(self):
        re_map = {
            '1.1.1.1': {
                'subject': 'CN=TrustedRoot,C=US,ST=MA,L=Hopkinton,'
                           'EMAIL=rsa@emc.com,OU=CSP,O=RSA',
                'issuer': '1.1.1.1',
                'serial#': '00d8280b0c863f6d4e',
                'valid_from': '20090407135111Z',
                'valid_to': '20190405135111Z'
            }
        }
        navi_handler = NaviHandler(**ACCESS_INFO)
        cer_map = navi_handler.analyse_cer(CER_INFOS, host_ip='1.1.1.1')
        print(cer_map)
        self.assertDictEqual(cer_map, re_map)
