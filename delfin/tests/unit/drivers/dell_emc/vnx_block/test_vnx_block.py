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

from delfin import context
from delfin.drivers.dell_emc.vnx_block.navi_handler import NaviHandler
from delfin.drivers.dell_emc.vnx_block.vnx_block import VnxBlockStorDriver
from delfin.drivers.utils.navicli_client import NaviClient


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vnx_block",
    "ssh": {
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
        Node:                A-CETV2135000041
        Physical Node:       K10
        Signature:           3600485
        Peer Signature:      3600424
        Revision:            05.33.000.5.038
        SCSI Id:             0
        Model:               VNX5400
        Model Type:          Rackmount
        Prom Rev:            7.00.00
        SP Memory:           16384
        Serial No:           CETV2135000041
        SP Identifier:       A
        Cabinet:             DPE9

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
        Vendor Id:               HITACHI
        Product Id:              HUC10906 CLAR600
        Product Revision:        C430
        Lun:                     193 129 146 151 164 165 166 169 182 189 190
        Type:                    193: RAID5 129: RAID5 146: RAID5 151: RAID5
        State:                   Enabled
        Hot Spare:               N/A
        Prct Rebuilt:            193: 100 129: 100 146: 100 151: 100 164: 100
        Prct Bound:              193: 100 129: 100 146: 100 151: 100 164: 100
        Serial Number:           KSJEX35J
        Sectors:                 291504128 (142336)
        Capacity:                549691
        Private:                 193: 562878464 129: 577587200 146: 598562816
        Bind Signature:          N/A, 0, 0
        Hard Read Errors:        0
        Hard Write Errors:       0
        Soft Read Errors:        0
        Soft Write Errors:       0
        Read Retries:     N/A
        Write Retries:    N/A
        Remapped Sectors:        N/A
        Number of Reads:         456896
        Number of Writes:        2472556
        Number of Luns:          35
        Raid Group ID:           0
        Clariion Part Number:    DG118032933
        Request Service Time:    N/A
        Read Requests:           456896
        Write Requests:          2472556
        Kbytes Read:             9995264
        Kbytes Written:          19098690
        Stripe Boundary Crossing: 0
        Drive Type:              SAS
        Clariion TLA Part Number:005049804PWR
        User Capacity:           139
        Idle Ticks:              3760691510
        Busy Ticks:              1300634809
        Current Speed: 6Gbps
        Maximum Speed: 6Gbps

        Bus 0 Enclosure 0  Disk 1
        Vendor Id:               HITACHI
        Product Id:              HUC10906 CLAR600
        Product Revision:        C430
        Lun:                     193 129 146 151 164 165 166 169 182 189 190
        Type:                    193: RAID5 129: RAID5 146: RAID5 151: RAID5
        State:                   Enabled
        Hot Spare:               N/A
        Prct Rebuilt:            193: 100 129: 100 146: 100 151: 100 164: 100
        Prct Bound:              193: 100 129: 100 146: 100 151: 100 164: 100
        Serial Number:           KSJG24WJ
        Sectors:                 291504128 (142336)
        Capacity:                549691
        Private:                 193: 562878464 129: 577587200 146: 598562816
        Bind Signature:          N/A, 0, 1
        Hard Read Errors:        0
        Hard Write Errors:       0
        Soft Read Errors:        0
        Soft Write Errors:       0
        Read Retries:     N/A
        Write Retries:    N/A
        Remapped Sectors:        N/A
        Number of Reads:         450914
        Number of Writes:        2753596
        Number of Luns:          35
        Raid Group ID:           0
        Clariion Part Number:    DG118032933
        Request Service Time:    N/A
        Read Requests:           450914
        Write Requests:          2753596
        Kbytes Read:             10391033
        Kbytes Written:          20145718
        Stripe Boundary Crossing: 0
        Drive Type:              SAS
        Clariion TLA Part Number:005049804PWR
        User Capacity:           139
        Idle Ticks:              622691228
        Busy Ticks:              139667922
        Current Speed: 6Gbps
        Maximum Speed: 6Gbps
        """
POOL_INFOS = """
        Pool Name:  Pool 1
        Pool ID:  1
        Raid Type:  r_5
        Percent Full Threshold:  80
        Description:
        Disk Type:  Unknown
        State:  Offline
        Status:  Storage Pool requires recovery. service provider(0x712d8518)
        Current Operation:  None
        Current Operation State:  N/A
        Current Operation Status:  N/A
        Current Operation Percent Completed:  0
        Raw Capacity (Blocks):  0
        Raw Capacity (GBs):  0.000
        User Capacity (Blocks):  18001391616
        User Capacity (GBs):  8583.732
        Consumed Capacity (Blocks):  17783387136
        Consumed Capacity (GBs):  8479.780
        Available Capacity (Blocks):  218004480
        Available Capacity (GBs):  103.953
        Percent Full:  98.789
        Total Subscribed Capacity (Blocks):  17783387136
        Total Subscribed Capacity (GBs):  8479.780
        Percent Subscribed:  98.789
        Oversubscribed by (Blocks):  0
        Oversubscribed by (GBs):  0.000
        Disks:
        Bus 0 Enclosure 0 Disk 23
        Bus 0 Enclosure 0 Disk 5
        Bus 0 Enclosure 0 Disk 6
        Bus 0 Enclosure 0 Disk 4
        Bus 0 Enclosure 0 Disk 24
        Bus 0 Enclosure 0 Disk 7
        LUNs:  24, 2, 25, 23, 17

        Pool Name:  Pool 3
        Pool ID:  3
        Raid Type:  r_10
        Percent Full Threshold:  70
        Description:
        Disk Type:
        State:  Offline
        Status:  An internal error occurred lun going offline. (0x712d8514)
        Current Operation:  None
        Current Operation State:  N/A
        Current Operation Status:  N/A
        Current Operation Percent Completed:  0
        Raw Capacity (Blocks):  0
        Raw Capacity (GBs):  0.000
        User Capacity (Blocks):  1718820864
        User Capacity (GBs):  819.598
        Consumed Capacity (Blocks):  611463168
        Consumed Capacity (GBs):  291.568
        Available Capacity (Blocks):  1107357696
        Available Capacity (GBs):  528.029
        Percent Full:  35.575
        Total Subscribed Capacity (Blocks):  611463168
        Total Subscribed Capacity (GBs):  291.568
        Percent Subscribed:  35.575
        Oversubscribed by (Blocks):  0
        Oversubscribed by (GBs):  0.000
        Disks:
        LUNs:  26, 27, 30, 307, 41, 38, 40, 306, 29, 46, 32, 31, 47, 45, 61, 42

        """
RAID_INFOS = """

        Server IP Address:       8.44.162.248
        Agent Rev:           7.33.1 (0.38)


        All RAID Groups Information
        ----------------------------


        RaidGroup ID:                              0
        RaidGroup Type:                            r5
        RaidGroup State:                           Valid_luns
        List of disks:                             Bus 0 Enclosure 0  Disk 3
                                                   Bus 0 Enclosure 0  Disk 2
                                                   Bus 0 Enclosure 0  Disk 1
                                                   Bus 0 Enclosure 0  Disk 0
        List of luns:                              193 129 146 151 164 165
        Max Number of disks:                       16
        Max Number of luns:                        256
        Raw Capacity (Blocks):                     1688426496
        Logical Capacity (Blocks):                 1688420352
        Free Capacity (Blocks,non-contiguous):     522260480
        Free contiguous group of unbound segments: 482326272
        Defrag/Expand priority:                    N/A
        Percent defragmented:                      N/A
        Percent expanded:                          N/A
        Disk expanding onto:                       N/A
        Lun Expansion enabled:                     NO
        Legal RAID types:                          r5

        RaidGroup ID:                              1
        RaidGroup Type:                            r5
        RaidGroup State:                           Valid_luns
        List of disks:                             Bus 0 Enclosure 0  Disk 20
                                                   Bus 0 Enclosure 0  Disk 19
                                                   Bus 0 Enclosure 0  Disk 18
                                                   Bus 0 Enclosure 0  Disk 17
                                                   Bus 0 Enclosure 0  Disk 16
        List of luns:                              107 109 110 184 185 186
        Max Number of disks:                       16
        Max Number of luns:                        256
        Raw Capacity (Blocks):                     3076358144
        Logical Capacity (Blocks):                 3076349952
        Free Capacity (Blocks,non-contiguous):     356175872
        Free contiguous group of unbound segments: 324515584
        Defrag/Expand priority:                    N/A
        Percent defragmented:                      N/A
        Percent expanded:                          N/A
        Disk expanding onto:                       N/A
        Lun Expansion enabled:                     NO
        Legal RAID types:                          r5


        """
LUN_INFOS = """
        LOGICAL UNIT NUMBER 239
        Name:  sun_data_VNX_2
        UID:  28:F0:36:00:4D:77:DC:BE:2B:F7:EA:11
        Current Owner:  SP A
        Default Owner:  SP A
        Allocation Owner:  SP A
        User Capacity (Blocks):  18874368
        User Capacity (GBs):  9.000
        Consumed Capacity (Blocks):  3677184
        Consumed Capacity (GBs):  1.753
        Pool Name:  Migration_pool
        Raid Type:  r_5
        Offset:  0
        Auto-Assign Enabled:  DISABLED
        Auto-Trespass Enabled:  DISABLED
        Current State:  Ready
        Status:  OK(0x0)
        Is Faulted:  false
        Is Transitioning:  false
        Current Operation:  None
        Current Operation State:  N/A
        Current Operation Status:  N/A
        Current Operation Percent Completed:  0
        Is Pool LUN:  Yes
        Is Thin LUN:  Yes
        Is Private:  No
        Is Compressed:  No
        Initial Tier:  Optimize Pool
        Tier Distribution:
        Extreme Performance:  100.00%

        LOGICAL UNIT NUMBER 236
        Name:  sun_data_pool
        UID:  28:F0:36:00:DB:9F:73:CE:15:F7:EA:11
        Current Owner:  SP A
        Default Owner:  SP A
        Allocation Owner:  SP A
        User Capacity (Blocks):  10485760
        User Capacity (GBs):  5.000
        Consumed Capacity (Blocks):  3677184
        Consumed Capacity (GBs):  1.753
        Pool Name:  Migration_pool
        Raid Type:  r_5
        Offset:  0
        Auto-Assign Enabled:  DISABLED
        Auto-Trespass Enabled:  DISABLED
        Current State:  Ready
        Status:  OK(0x0)
        Is Faulted:  false
        Is Transitioning:  false
        Current Operation:  None
        Current Operation State:  N/A
        Current Operation Status:  N/A
        Current Operation Percent Completed:  0
        Is Pool LUN:  Yes
        Is Thin LUN:  Yes
        Is Private:  No
        Is Compressed:  No
        Initial Tier:  Optimize Pool
        Tier Distribution:
        Extreme Performance:  100.00%

        """
GETALLLUN_INFOS = """
        Server IP Address:       8.44.162.248
        Agent Rev:           7.33.1 (0.38)


        All logical Units Information
        -----------------------------


        LOGICAL UNIT NUMBER 186
        Prefetch size (blocks) =         N/A
        Prefetch multiplier =            N/A
        Segment size (blocks) =          N/A
        Segment multiplier =             N/A
        Maximum prefetch (blocks) =      N/A
        Prefetch Disable Size (blocks) = N/A
        Prefetch idle count =            N/A

        Prefetching:             N/A
        Prefetched data retained    N/A

        Read cache configured according to
         specified parameters.

        Total Hard Errors:          0
        Total Soft Errors:          0
        Total Queue Length:         0
        Name                        LN_10G_01
        Minimum latency reads N/A
        RAID Type:                  RAID5
        RAIDGroup ID:               1
        State:                      Bound
        Stripe Crossing:            0
        Element Size:               128
        Current owner:              SP A
        Offset:                     N/A
        Prct Bound:                 N/A
        LUN Capacity(Megabytes):    10240
        LUN Capacity(Blocks):       20971520
        UID:                        28:F0:36:00:50:23:08:59:FF:73:EA:11
        LUN Capacity(Stripes):      40960
        Shrink State:                    N/A
        Is Private:                 NO
        Snapshots List:             Not Available
        MirrorView Name if any:     Not Available
        Address Offset:             N/A
        Is Meta LUN:                NO
        Is Thin LUN:                YES
        Is Pool LUN:                YES
        Is Snapshot Mount Point:    NO
        LUN Idle Ticks:             N/A
        LUN Busy Ticks:             N/A
        LUN Offline (Cache Dirty Condition):  N/A
        LU Storage Groups:         "windows_test_1"
        Device Map:                 Valid
        Average Read Time:            0
        Average Write Time:            0
        FAST Cache :             N/A
        FAST Cache Read Hits:    N/A

        LOGICAL UNIT NUMBER 87
        Prefetch size (blocks) =         N/A
        Prefetch multiplier =            N/A
        Segment size (blocks) =          N/A
        Segment multiplier =             N/A
        Maximum prefetch (blocks) =      N/A
        Prefetch Disable Size (blocks) = N/A
        Prefetch idle count =            N/A

        Prefetching:             N/A
        Prefetched data retained    N/A

        Read cache configured according to
         specified parameters.

        Name                        LUN_Grab_2
        Minimum latency reads N/A

        RAID Type:                  N/A
        RAIDGroup ID:               N/A
        State:                      Bound
        Stripe Crossing:            0
        Element Size:               0
        Current owner:              SP A
        Offset:                     N/A
        Auto-trespass:              DISABLED
        Auto-assign:                DISABLED
        Write cache:                ENABLED
        Read cache:                 ENABLED
        Idle Threshold:             N/A
        Idle Delay Time:            N/A
        Write Aside Size:           0
        Default Owner:              SP A
        Rebuild Priority:           N/A
        Verify Priority:            N/A
        Prct Reads Forced Flushed:  N/A
        Prct Writes Forced Flushed: N/A
        Prct Rebuilt:               100
        Prct Bound:                 N/A
        LUN Capacity(Megabytes):    10
        LUN Capacity(Blocks):       20480
        UID:                        28:F0:36:00:F0:D7:DE:66:F6:A3:EA:11
        LUN Capacity(Stripes):      N/A
        Shrink State:                    N/A
        Is Private:                 NO
        Snapshots List:             Not Available
        MirrorView Name if any:     Not Available
        Address Offset:             N/A
        Is Meta LUN:                NO
        Is Thin LUN:                YES
        Is Pool LUN:                YES
        Is Snapshot Mount Point:    NO
        LUN Idle Ticks:             N/A
        LUN Busy Ticks:             N/A
        LUN Offline (Cache Dirty Condition):  N/A
        LU Storage Groups:         "windows_test_1"
        Device Map:                 Valid
        Average Read Time:            0
        Average Write Time:            0
        FAST Cache :             N/A
        FAST Cache Read Hits:    N/A

        """
LOG_INFOS = """
03/25/2020 00:13:03 N/A                  (4600)'Capture the array configurati
03/25/2020 13:30:17 N/A                  (1)   Navisphere Agent, version 7.33
09/14/2020 19:03:25 N/A                  (7606)Thinpool (Migration_pool) is (
03/25/2020 13:30:17 N/A                  (2006)Able to read events from the W
03/25/2020 13:30:17 N/A                  (2006)Able to read events from the W
03/25/2020 13:30:23 N/A                  (76)   Cabling status is unknown
03/25/2020 13:31:52 N/A                  (6004)NTP Time Synchronization Faile
03/25/2020 13:31:59 N/A                  (780d)'8.44.75.192' Calculate server
03/25/2020 13:32:17 N/A                  (7805)'51.10.192.80' Poll server age
03/25/2020 13:32:18 N/A                  (1b7c)The DNS Client service entered
03/25/2020 13:35:03 N/A                  (743a)Unisphere can no longer manage
03/25/2020 13:48:47 N/A                  (1b7c)The Application Experience ser
03/25/2020 13:58:44 N/A                  (743a)Unisphere can no longer manage
03/25/2020 13:58:44 N/A                  (7464)Thin Pool (Pool_00) is not wor
03/25/2020 13:58:44 N/A                  (7464)Thin Pool (Pool 1) is not work
03/25/2020 14:00:37 N/A                  (4600)'Log In' called by ' Navi User
03/25/2020 14:00:42 N/A                  (1)   EV_RAIDGroup::GetDiskDescripti
03/25/2020 14:00:49 N/A                  (77f1)'spcollect' called by ' Navi U
03/25/2020 14:01:19 N/A                  (7811)'spcollect' called by ' Navi U
03/25/2020 14:01:53 N/A                  (1b7c)The Application Experience ser

"""
LOG2_INFOS = """
03/25/2020 00:13:02 N/A                  (4600)'convertemlog' called by '' (1
03/25/2020 00:13:03 N/A                  (4600)'Capture the array configurati
03/25/2020 13:30:17 N/A                  (76cc)Navisphere Agent, version 7.33
09/14/2020 19:03:25 N/A                  (7711)Thinpool (Migration_pool) is (
03/25/2020 13:30:17 N/A                  (7506)Able to read events from the W
03/25/2020 13:30:17 N/A                  (2006)Able to read events from the W
03/25/2020 13:30:23 N/A                  (76)   Cabling status is unknown
03/25/2020 13:31:52 N/A                  (6004)NTP Time Synchronization Faile
03/25/2020 13:31:59 N/A                  (780d)'8.44.75.192' Calculate server
03/25/2020 13:32:17 N/A                  (7805)'51.10.192.80' Poll server age
03/25/2020 13:32:18 N/A                  (1b7c)The DNS Client service entered
03/27/2020 13:35:03 N/A                  (7464)Thin Pool (Pool 1) is not work
03/25/2020 13:48:47 N/A                  (1b7c)The Application Experience ser
03/25/2020 13:58:44 N/A                  (711a)Unisphere can no longer manage

"""

AGENT_RESULT = {
    'agent_rev': '7.33.1 (0.38)',
    'name': 'K10',
    'desc': '',
    'node': 'A-CETV2135000041',
    'physical_node': 'K10',
    'signature': '3600485',
    'peer_signature': '3600424',
    'revision': '05.33.000.5.038',
    'scsi_id': '0',
    'model': 'VNX5400',
    'model_type': 'Rackmount',
    'prom_rev': '7.00.00',
    'sp_memory': '16384',
    'serial_no': 'CETV2135000041',
    'sp_identifier': 'A',
    'cabinet': 'DPE9'
}
STORAGE_RESULT = {
    'name': 'A-CETV2135000041',
    'vendor': 'DELL EMC',
    'model': 'VNX5400',
    'status': 'normal',
    'serial_number': 'CETV2135000041',
    'firmware_version': '05.33.000.5.038',
    'total_capacity': 1142846874714,
    'raw_capacity': 1152785580032,
    'used_capacity': 14501957074,
    'free_capacity': 1128344917639
}
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
    },
    {
        'name': 'Pool 3',
        'storage_id': '12345',
        'native_storage_pool_id': '3',
        'description': '',
        'status': 'offline',
        'storage_type': 'block',
        'total_capacity': 880036651466,
        'subscribed_capacity': 313068756140,
        'used_capacity': 313068756140,
        'free_capacity': 566966821584
    }]
VOLUMES_RESULT = [
    {
        'name': 'sun_data_VNX_2',
        'storage_id': '12345',
        'description': '239 sun_data_VNX_2',
        'status': 'normal',
        'native_volume_id': '239',
        'native_storage_pool_id': '',
        'type': 'thin',
        'total_capacity': 9663676416,
        'used_capacity': 1882269417,
        'free_capacity': 7781406998,
        'compressed': False
    },
    {
        'name': 'sun_data_pool',
        'storage_id': '12345',
        'description': '236 sun_data_pool',
        'status': 'normal',
        'native_volume_id': '236',
        'native_storage_pool_id': '',
        'type': 'thin',
        'total_capacity': 5368709120,
        'used_capacity': 1882269417,
        'free_capacity': 3486439702,
        'compressed': False
    },
    {
        'name': 'LN_10G_01',
        'storage_id': '12345',
        'description': '186 LN_10G_01',
        'status': 'normal',
        'native_volume_id': '186',
        'native_storage_pool_id': 'raid_group_1',
        'type': 'thin',
        'total_capacity': 10737418240,
        'used_capacity': 10737418240,
        'free_capacity': 0
    }]
ALERTS_RESULT = [
    {
        'alert_id': '77f1',
        'alert_name': "'spcollect' called by ' Navi U",
        'severity': 'Fatal',
        'category': 'Event',
        'type': 'EquipmentAlarm',
        'occur_time': 1585116049000,
        'description': "'spcollect' called by ' Navi U",
        'resource_type': 'Storage'
    },
    {
        'alert_id': '7711',
        'alert_name': 'Thinpool (Migration_pool) is (',
        'severity': 'Fatal',
        'category': 'Event',
        'type': 'EquipmentAlarm',
        'occur_time': 1600081405000,
        'description': 'Thinpool (Migration_pool) is (',
        'resource_type': 'Storage'
    }]
ALERT_RESULT = {
    'alert_id': '761f',
    'alert_name': 'Unisphere can no longer manage',
    'severity': 'Critical',
    'category': 'Event',
    'type': 'EquipmentAlarm',
    'occur_time': 1607308236684.9626,
    'description': 'Unisphere can no longer manage',
    'resource_type': 'Storage'
}


def create_driver():
    kwargs = ACCESS_INFO

    NaviHandler.login = mock.Mock(
        return_value={"05.33.000.5.038_test"})

    return VnxBlockStorDriver(**kwargs)


class TestVnxBlocktorageDriver(TestCase):
    driver = create_driver()

    def test_init(self):
        NaviHandler.login = mock.Mock(
            return_value={"05.33.000.5.038_test"})
        kwargs = ACCESS_INFO
        VnxBlockStorDriver(**kwargs)

    def test_initssh(self):
        NaviClient.exec = mock.Mock(return_value=AGENT_INFOS)
        re_agent = self.driver.navi_handler.get_agent()
        self.assertDictEqual(re_agent, AGENT_RESULT)

    def test_get_storage(self):
        NaviClient.exec = mock.Mock(
            side_effect=[AGENT_INFOS, DISK_INFOS, POOL_INFOS, RAID_INFOS,
                         LUN_INFOS, GETALLLUN_INFOS])
        re_storage = self.driver.get_storage(context)
        self.assertDictEqual(re_storage, STORAGE_RESULT)

    def test_get_pools(self):
        NaviClient.exec = mock.Mock(side_effect=[POOL_INFOS, RAID_INFOS])
        re_pools = self.driver.list_storage_pools(context)
        self.assertDictEqual(re_pools[0], POOLS_RESULT[0])

    def test_get_volumes(self):
        NaviClient.exec = mock.Mock(
            side_effect=[LUN_INFOS, POOL_INFOS, GETALLLUN_INFOS])
        re_volumes = self.driver.list_volumes(context)
        self.assertDictEqual(re_volumes[0], VOLUMES_RESULT[0])

    def test_get_alerts(self):
        NaviClient.exec = mock.Mock(
            side_effect=[DOMAIN_INFOS, LOG_INFOS, LOG2_INFOS])
        query_para = {
            'begin_time': 1585115924000 - (1 * 24 * 60 * 60 * 1000),
            'end_time': 1585115924000
        }
        # query_para = None
        re_alerts = self.driver.list_alerts(context, query_para)
        ALERTS_RESULT[0]['occur_time'] = re_alerts[0]['occur_time']
        self.assertDictEqual(re_alerts[0], ALERTS_RESULT[0])

    def test_parse_alert(self):
        alert = {
            '1.3.6.1.4.1.1981.1.4.3': 'A-CETV2135000041',
            '1.3.6.1.4.1.1981.1.4.4': 'K10',
            '1.3.6.1.4.1.1981.1.4.5': '761f',
            '1.3.6.1.4.1.1981.1.4.6': 'Unisphere can no longer manage',
            '1.3.6.1.4.1.1981.1.4.7': 'VNX5400'
        }
        re_alert = self.driver.parse_alert(context, alert)
        ALERT_RESULT['occur_time'] = re_alert['occur_time']
        self.assertDictEqual(re_alert, ALERT_RESULT)
