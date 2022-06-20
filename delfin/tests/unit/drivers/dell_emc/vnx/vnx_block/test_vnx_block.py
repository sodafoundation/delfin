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

from delfin.common import constants
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.drivers.dell_emc.vnx.vnx_block.alert_handler import AlertHandler
from delfin.drivers.dell_emc.vnx.vnx_block.component_handler import \
    ComponentHandler
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

DISK_DATAS = """
        Bus 0 Enclosure 0  Disk 0
        Vendor Id:               HITACHI
        Product Id:              HUC10906 CLAR600
        Product Revision:        C430
        Type:                    193: RAID5 129: RAID5 146: RAID5 151: RAID5
        State:                   Enabled
        Hot Spare:               N/A
        Serial Number:           KSJEX35J
        Capacity:                549691
        Raid Group ID:           0
        Drive Type:              SAS
        Current Speed: 6Gbps
        """
SP_DATAS = """

SP A

Cabinet:             DPE9
Signature For The SP:          3600485
Signature For The Peer SP:     3600424
Revision Number For The SP:    05.33.000.5.038
Serial Number For The SP:      CF2Z7134700101
Memory Size For The SP:        16384
SP SCSI ID if Available:       0

SP B

Cabinet:             DPE9
Signature For The SP:          3600424
Signature For The Peer SP:     3600485
Revision Number For The SP:    05.33.000.5.038
Serial Number For The SP:      CF2Z7134700040
Memory Size For The SP:        16384
SP SCSI ID if Available:       0


"""
RESUME_DATAS = """
Storage Processor A
  CPU Module
    EMC Serial Number:               CF2Z7134700101
    Assembly Name:                   JFSP 1.8GHZ 4C CPU GEN3

Storage Processor B
  CPU Module
    EMC Serial Number:               CF2Z7134700040
    Assembly Name:                   JFSP 1.8GHZ 4C CPU GEN3
"""
PORT_DATAS = """
Information about each SPPORT:

SP Name:             SP A
SP Port ID:          6
SP UID:              50:06:01:60:88:60:24:1E:50:06:01:66:08:60:24:1E
Link Status:         Up
Port Status:         Online
Switch Present:      YES
Switch UID:          10:00:C4:F5:7C:20:05:80:20:0E:C4:F5:7C:20:05:80
SP Source ID:        1773056
ALPA Value:         0
Speed Value :         8Gbps
Auto Negotiable :     YES
Available Speeds:
2Gbps
4Gbps
8Gbps
Auto
Requested Value:      Auto
MAC Address:         Not Applicable
SFP State:           Online
Reads:               510068560
Writes:              331050079
Blocks Read:         1504646456
Blocks Written:      236376118
Queue Full/Busy:     12246
I/O Module Slot:     3
Physical Port ID:    0
"""
BUS_PORT_DATAS = """

Bus 0

Current Speed: 6Gbps.
Available Speeds:
              3Gbps.
              6Gbps.

SPA SFP State: N/A
SPB SFP State: N/A

I/O Module Slot: Base Module
Physical Port ID: 0
Port Combination In Use: No



SPA Connector State: None
SPB Connector State: None

"""
BUS_PORT_STATE_DATAS = """
Information about each I/O module(s) on SPA:

SP ID: A
I/O Module Slot: Base Module
I/O Module Type: SAS
I/O Module State: Present
I/O Module Substate: Good
I/O Module Power state: On
I/O Carrier: No

Information about each port on this I/O module:
Physical Port ID: 0
Port State: Enabled
Physical Port ID: 1
Port State: Missing
Information about each I/O module(s) on SPB:

SP ID: B
I/O Module Slot: Base Module
I/O Module Type: SAS
I/O Module State: Present
I/O Module Substate: Good
I/O Module Power state: On
I/O Carrier: No

Information about each port on this I/O module:
Physical Port ID: 0
Port State: Enabled
Physical Port ID: 1
Port State: Missing
"""
ISCSI_PORT_DATAS = """
SP: A
Port ID: 4
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a4
iSCSI Alias: 0877.a4
IP Address: 172.20.1.140
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.1.1
Initiator Authentication: Not Available

SP: A
Port ID: 5
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a5
iSCSI Alias: 0877.a5

SP: A
Port ID: 6
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a6
iSCSI Alias: 0877.a6
IP Address: 172.20.2.140
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.2.1
Initiator Authentication: Not Available

SP: A
Port ID: 7
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.a7
iSCSI Alias: 0877.a7

SP: B
Port ID: 4
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b4
iSCSI Alias: 0877.b4
IP Address: 172.20.1.141
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.1.1
Initiator Authentication: Not Available

SP: B
Port ID: 5
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b5
iSCSI Alias: 0877.b5

SP: B
Port ID: 6
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b6
iSCSI Alias: 0877.b6
IP Address: 172.20.2.141
Subnet Mask: 255.255.255.0
Gateway Address: 172.20.2.1
Initiator Authentication: Not Available

SP: B
Port ID: 7
Port WWN: iqn.1992-04.com.emc:cx.apm00093300877.b7
iSCSI Alias: 0877.b7

SP: B
Port ID: 9
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:69:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A

SP: A
Port ID: 8
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:60:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A

SP: A
Port ID: 9
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:61:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A

SP: B
Port ID: 8
Port WWN: 50:06:01:60:BB:20:13:0D:50:06:01:68:3B:24:13:0D
iSCSI Alias: N/A
IP Address: N/A
Subnet Mask: N/A
Gateway Address: N/A
Initiator Authentication: N/A
"""
IO_PORT_CONFIG_DATAS = """
SP ID :  A
I/O Module Slot :  3
I/O Module Type :  Fibre Channel
I/O Module State :  Present

SP ID :  A
I/O Module Slot :  Base Module
I/O Module Type :  SAS

SP ID :  B
I/O Module Slot :  Base Module
I/O Module Type :  SAS
"""

VIEW_DATAS = """
Storage Group Name:    AIX_PowerHA_node2
Storage Group UID:     0B:33:4A:6E:81:38:EC:11:90:2B:00:60:16:63
HBA/SP Pairs:

  HBA UID                                          SP Name     SPPort
 -------                                          -------     ------
  20:00:00:00:C9:76:5E:79:10:00:00:00:C9:76:5E:79   SP A         6
Host name:             AIX_21
  20:00:00:00:C9:75:80:4C:10:00:00:00:C9:75:80:4C   SP B         3
Host name:             AIX_21

HLU/ALU Pairs:

  HLU Number     ALU Number
  ----------     ----------
    1               335
Shareable:             YES
"""
HBA_DATAS = """
Information about each HBA:

HBA UID:                 20:00:00:00:C9:9B:57:79:10:00:00:00:C9:9B:57:79
Server Name:             aix_ma
Server IP Address:       8.44.129.26
HBA Model Description:
HBA Vendor Description:
HBA Device Driver Name:   N/A
Information about each port of this HBA:

    SP Name:               SP A
    SP Port ID:            6
    HBA Devicename:        N/A
    Trusted:               NO
    Logged In:             NO
    Defined:               YES
    Initiator Type:          3
    StorageGroup Name:     None
"""

ARCHIVE_DATAS = """
Index Size in KB     Last Modified            Filename
2 46 07/08/2021 01:20:29  CETV2135000041_SPA_2021-07-07_17-20-26-GMT_P08-00.nar
3 40 07/08/2021 03:56:28  CETV2135000041_SPA_2021-07-07_19-56-25-GMT_P08-00.nar
4 31 07/08/2021 06:32:29  CETV2135000041_SPA_2021-07-07_22-32-26-GMT_P08-00.nar
5 02 07/08/2021 09:08:29  CETV2135000041_SPA_2021-07-08_01-08-26-GMT_P08-00.nar
6 76 07/08/2021 11:44:29  CETV2135000041_SPA_2021-07-08_03-44-26-GMT_P08-00.nar
7 48 07/08/2021 14:20:28  CETV2135000041_SPA_2021-07-08_06-20-26-GMT_P08-00.nar
8 34 07/08/2021 16:31:13  CETV2135000041_SPA_2021-07-08_08-31-11-GMT_P08-00.nar
"""
PERFORMANCE_LINES_MAP = {
    'SP A': [['SP A', '07/08/2021 12:15:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0', '', '', '0', '', '', '0', '', '', '0', '',
              '', '0', '', '', '0', '', '', '0', '', '', '0'],
             ['SP A', '07/08/2021 12:16:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0', '', '', '0', '', '', '0', '', '', '0', '', '',
              '0', '', '', '0', '', '', '0', '', '', '0'],
             ['SP A', '07/08/2021 12:17:55', '', '', '', '', '', '', '',
              '', '0', '', '', '0', '', '', '0', '', '', '0', '', '', '0',
              '', '', '0', '', '', '0', '', '', '0', '', '', '0'],
             ['SP A', '07/08/2021 12:18:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0.28', '', '', '0.73', '', '', '0', '', '',
              '0', '', '', '0', '', '', '0.28', '', '', '', '', '', '0.73'],
             ['SP A', '07/08/2021 12:19:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0', '', '', '0', '', '', '0', '', '', '0', '',
              '', '0', '', '', '0', '', '', '0', '', '', '0']],
    'SP B': [['SP B', '07/08/2021 12:15:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0.9', '', '', '2.6', '', '', '0.9', '', '',
              '2.4', '', '', '1', '', '', '0.7', '', '', '', '', '', '0.2'],
             ['SP B', '07/08/2021 12:16:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0.1', '', '', '5.6', '', '', '0.2', '', '', '6.7',
              '', '', '2', '', '', '1.6', '', '', '', '', '', '1.4'],
             ['SP B', '07/08/2021 12:17:55', '', '', '', '', '', '', '',
              '', '0', '', '', '0.2', '', '', '4.6', '', '', '0.3', '', '',
              '1.7', '', '', '3', '', '', '2.6', '', '', '', '', '', '2.4'],
             ['SP B', '07/08/2021 12:18:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0.3', '', '', '6.6', '', '', '0.4', '', '',
              '2.7', '', '', '4', '', '', '3.6', '', '', '', '', '', '3.4'],
             ['SP B', '07/08/2021 12:19:56', '', '', '', '', '', '', '', '',
              '0', '', '', '0.4', '', '', '7.6', '', '', '0.5', '', '',
              '3.7', '', '', '5', '', '', '4.6', '', '', '', '', '', '4.4']]
}
NAR_INTERVAL_DATAS = """
Archive Poll Interval (sec):  60
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
DISK_RESULT = [
    {
        'name': 'Bus 0 Enclosure 0 Disk 0',
        'storage_id': '12345',
        'native_disk_id': 'Bus0Enclosure0Disk0',
        'serial_number': 'KSJEX35J',
        'manufacturer': 'HITACHI',
        'model': 'HUC10906 CLAR600',
        'firmware': 'C430',
        'speed': None,
        'capacity': 576392790016,
        'status': 'normal',
        'physical_type': 'sas',
        'logical_type': 'unknown',
        'health_score': None,
        'native_disk_group_id': None,
        'location': 'Bus 0 Enclosure 0 Disk 0'
    }]
SP_RESULT = [
    {
        'name': 'SP A',
        'storage_id': '12345',
        'native_controller_id': '3600485',
        'status': 'normal',
        'location': None,
        'soft_version': '05.33.000.5.038',
        'cpu_info': 'JFSP 1.8GHZ 4C CPU GEN3',
        'memory_size': '17179869184'
    },
    {
        'name': 'SP B',
        'storage_id': '12345',
        'native_controller_id': '3600424',
        'status': None,
        'location': None,
        'soft_version': '05.33.000.5.038',
        'cpu_info': 'JFSP 1.8GHZ 4C CPU GEN3',
        'memory_size': '16777216'
    }]
PORT_RESULT = [
    {
        'name': 'Slot A3,Port 0',
        'storage_id': '12345',
        'native_port_id': 'A-6',
        'location': 'Slot A3,Port 0',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'fc',
        'logical_type': None,
        'speed': 8000000000,
        'max_speed': 8000000000,
        'native_parent_id': None,
        'wwn': '50:06:01:60:88:60:24:1E:50:06:01:66:08:60:24:1E',
        'mac_address': None,
        'ipv4': '172.20.2.140',
        'ipv4_mask': '255.255.255.0',
        'ipv6': None,
        'ipv6_mask': None
    }]
VIEW_RESULT = [
    {
        'native_masking_view_id': '0B:33:4A:6E:81:38:EC:11:90:2B:00:'
                                  '60:16:63_AIX_21_335',
        'name': 'AIX_PowerHA_node2',
        'storage_id': '12345',
        'native_storage_host_id': 'AIX_21',
        'native_volume_id': '335'
    }]
INITIATOR_RESULT = [
    {
        'name': '20:00:00:00:C9:9B:57:79:10:00:00:00:C9:9B:57:79',
        'storage_id': '12345',
        'native_storage_host_initiator_id': '20:00:00:00:C9:9B:57:79:10:'
                                            '00:00:00:C9:9B:57:79',
        'wwn': '20:00:00:00:C9:9B:57:79:10:00:00:00:C9:9B:57:79',
        'type': 'unknown',
        'status': 'online',
        'native_storage_host_id': 'aix_ma'
    }]
HOST_RESULT = [
    {
        'name': 'aix_ma',
        'storage_id': '12345',
        'native_storage_host_id': 'aix_ma',
        'os_type': 'Unknown',
        'status': 'normal',
        'ip_address': '8.44.129.26'
    }]
METRICS_RESULT = [
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'controller',
        'resource_id': '3600485',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={
        1625717816000: 0.0,
        1625717875000: 0.0,
        1625717936000: 0.73,
        1625717996000: 0.0
    }),
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'port',
        'resource_id': 'A-6',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={
        1625717816000: 3.0,
        1625717875000: 4.0,
        1625717936000: 5.0,
        1625717996000: 6.0
    }),
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'disk',
        'resource_id': 'Bus0Enclosur0Disk0',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={
        1625717816000: 4.0,
        1625717875000: 5.0,
        1625717936000: 6.0,
        1625717996000: 6.0
    }),
    constants.metric_struct(name='iops', labels={
        'storage_id': '12345',
        'resource_type': 'volume',
        'resource_id': '230',
        'type': 'RAW',
        'unit': 'IOPS'
    }, values={
        1625717816000: 0.0,
        1625717875000: 0.0,
        1625717936000: 0.0,
        1625717996000: 0.0
    })
]


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
        time_str = '03/26/2021 14:25:36'
        mock_mktime.return_value = 1616739936
        re = tools.time_str_to_timestamp(time_str, consts.TIME_PATTERN)
        self.assertEqual(1616739936000, re)

    @mock.patch.object(time, 'strftime')
    def test_timestamp_to_time_str(self, mock_strftime):
        tools = Tools()
        mock_strftime.return_value = '03/26/2021 14:25:36'
        timestamp = 1616739936000
        re = tools.timestamp_to_time_str(timestamp, consts.TIME_PATTERN)
        self.assertEqual('03/26/2021 14:25:36', re)

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
        self.assertDictEqual(cer_map, re_map)

    def test_analyse_cer_exception(self):
        with self.assertRaises(Exception) as exc:
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.analyse_cer(CER_INFOS)
        self.assertIn('arrange cer info error', str(exc.exception))

    def test_get_resources_info_exception(self):
        with self.assertRaises(Exception) as exc:
            NaviClient.exec = mock.Mock(side_effect=[LUN_INFOS])
            navi_handler = NaviHandler(**ACCESS_INFO)
            navi_handler.get_resources_info('abc', None)
        self.assertIn('object is not callable', str(exc.exception))

    def test_parse_alert_exception(self):
        with self.assertRaises(Exception) as exc:
            AlertHandler.parse_alert(None)
        self.assertIn('The results are invalid', str(exc.exception))

    def test_clear_alert(self):
        self.driver.clear_alert(None, None)

    def test_remove_trap_config(self):
        self.driver.remove_trap_config(None, None)

    def test_get_disks(self):
        NaviClient.exec = mock.Mock(return_value=DISK_DATAS)
        disks = self.driver.list_disks(context)
        self.assertDictEqual(disks[0], DISK_RESULT[0])

    def test_get_controllers(self):
        NaviClient.exec = mock.Mock(side_effect=[SP_DATAS, RESUME_DATAS])
        controllers = self.driver.list_controllers(context)
        self.assertDictEqual(controllers[0], SP_RESULT[0])

    def test_get_ports(self):
        NaviClient.exec = mock.Mock(
            side_effect=[IO_PORT_CONFIG_DATAS, ISCSI_PORT_DATAS, PORT_DATAS,
                         BUS_PORT_DATAS, BUS_PORT_STATE_DATAS])
        ports = self.driver.list_ports(context)
        self.assertDictEqual(ports[0], PORT_RESULT[0])

    def test_get_masking_views(self):
        NaviClient.exec = mock.Mock(side_effect=[VIEW_DATAS])
        views = self.driver.list_masking_views(context)
        self.assertDictEqual(views[0], VIEW_RESULT[0])

    def test_get_initiators(self):
        NaviClient.exec = mock.Mock(side_effect=[HBA_DATAS,
                                                 IO_PORT_CONFIG_DATAS,
                                                 ISCSI_PORT_DATAS, PORT_DATAS,
                                                 BUS_PORT_DATAS,
                                                 BUS_PORT_STATE_DATAS])
        initiators = self.driver.list_storage_host_initiators(context)
        self.assertDictEqual(initiators[0], INITIATOR_RESULT[0])

    def test_get_hosts(self):
        NaviClient.exec = mock.Mock(side_effect=[HBA_DATAS])
        hosts = self.driver.list_storage_hosts(context)
        self.assertDictEqual(hosts[0], HOST_RESULT[0])

    def test_get_perf_metrics(self):
        driver = create_driver()
        resource_metrics = {
            'controller': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime'
            ],
            'port': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime'
            ],
            'disk': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime'
            ],
            'volume': [
                'iops', 'readIops', 'writeIops',
                'throughput', 'readThroughput', 'writeThroughput',
                'responseTime',
                'cacheHitRatio', 'readCacheHitRatio', 'writeCacheHitRatio',
                'ioSize', 'readIoSize', 'writeIoSize',
            ]
        }
        start_time = 1625717756000
        end_time = 1625717996000
        ComponentHandler._filter_performance_data = mock.Mock(
            side_effect=[PERFORMANCE_LINES_MAP])
        NaviClient.exec = mock.Mock(
            side_effect=[ARCHIVE_DATAS, SP_DATAS, PORT_DATAS, DISK_DATAS,
                         GET_ALL_LUN_INFOS, NAR_INTERVAL_DATAS])
        ComponentHandler._remove_archive_file = mock.Mock(return_value="")
        metrics = driver.collect_perf_metrics(context, '12345',
                                              resource_metrics, start_time,
                                              end_time)
        self.assertEqual(metrics[0][1]["resource_id"], '3600485')

    def test_get_capabilities(self):
        cap = VnxBlockStorDriver.get_capabilities(context)
        self.assertIsNotNone(cap.get('resource_metrics'))
        self.assertIsNotNone(cap.get('resource_metrics').get('controller'))
        self.assertIsNotNone(cap.get('resource_metrics').get('volume'))
        self.assertIsNotNone(cap.get('resource_metrics').get('port'))
        self.assertIsNotNone(cap.get('resource_metrics').get('disk'))
