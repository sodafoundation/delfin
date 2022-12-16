# Copyright 2022 The SODA Authors.
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
import sys
from unittest import TestCase, mock

import paramiko
import six
from paramiko import SSHClient

sys.modules['delfin.cryptor'] = mock.Mock()
import time
from oslo_utils import units
from delfin.common import constants
from delfin.drivers.macro_san.ms import consts
from delfin.drivers.macro_san.ms.macro_ssh_client import MacroSanSSHPool

from oslo_log import log

from delfin import context
from delfin.drivers.macro_san.ms.ms_handler import MsHandler
from delfin.drivers.macro_san.ms.ms_stor import MacroSanDriver

LOG = log.getLogger(__name__)
ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "macro_san",
    "model": "macro_san",
    "ssh": {
        "host": "110.143.133.200",
        "port": 22,
        "username": "admin",
        "password": "admin"
    }
}
POOLS_INFO = """Last login: Wed Jul 13 15:05:45 2022 from 192.168.3.235\r
(null)@(null) ODSP CLI> pool mgt getlist\r
Storage Pools Sum: 4\r
\r
Name: SYS-Pool\r
Type: Traditional\r
Is Foreign: No\r
Is Reserved: Yes\r
Cell Size: 1GB\r
All Capacity: 7144GB\r
Used Capacity: 961GB\r
Used Capacity Rate: 13.5%\r
Free Capacity(RAID): 6183GB\r
Free Capacity(HDD RAID): 0GB\r
Free Capacity(SSD RAID): 6183GB\r
\r
Name: pool-1\r
Type: Traditional\r
Is Foreign: No\r
Is Reserved: No\r
Cell Size: 1GB\r
All Capacity: 0GB\r
Used Capacity: 0GB\r
Used Capacity Rate: 0.0%\r
Free Capacity(RAID): 0GB\r
Free Capacity(HDD RAID): 0GB\r
Free Capacity(SSD RAID): 0GB\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""
RAID_SYS_POOL = """(null)@(null) ODSP CLI> raid mgt getlist -p SYS-Pool\r
RAIDs Sum: 1\r
\r
Name: SYS-RAID\r
RAID Level: RAID5\r
Health Status: Normal\r
Total Capacity: 7144GB\r
Free Capacity: 6183GB\r
Disk Type: SSD\r
Data Disks Sum: 8\r
Dedicated Spare Disks Sum: 1\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""

RAID_POOL_1 = """(null)@(null) ODSP CLI> raid mgt getlist -p pool-1\r
RAIDs Sum: 0\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """

POOLS_DATA = [{'name': 'SYS-Pool', 'storage_id': '12345',
               'native_storage_pool_id': 'SYS-Pool', 'status': 'normal',
               'storage_type': 'block', 'total_capacity': 7670811590656.0,
               'used_capacity': 1031865892864.0,
               'free_capacity': 6638945697792.0},
              {'name': 'pool-1', 'storage_id': '12345',
               'native_storage_pool_id': 'pool-1', 'status': 'unknown',
               'storage_type': 'block', 'total_capacity': 0.0,
               'used_capacity': 0.0,
               'free_capacity': 0.0}]
VOLUME_INFO = """(null)@(null) ODSP CLI> lun mgt getlist -p SYS-Pool\r
SYS-Pool: 18 LUNs (18 Normal 0 Faulty)\r
\r
Name : SYS-LUN-Config\r
LUN id   : 0\r
Total Size : 4GB\r
Current Owner(SP) : SP1\r
Health Status : Normal\r
Cache Status : Disable\r
Mapped to Client : No\r
\r
\r
Name : SYS-LUN-Log\r
LUN id   : 1\r
Total Size : 4GB\r
Current Owner(SP) : SP1\r
Health Status : Normal\r
Cache Status : Disable\r
Mapped to Client : No\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUME_QUERY_ONE = """(null)@(null) ODSP CLI> lun mgt query -n SYS-LUN-Config\r
Name : SYS-LUN-Config\r
Device ID: 600B342F1B0F9ABD7BABD272BD0000DA\r
Total Size : 4GB\r
Current Owner(SP) : SP1\r
Owner(Pool) : SYS-Pool\r
Health Status : Normal\r
Is Reserved : Yes\r
Is Foreign : No\r
Created Time: 2021/12/23 11:26:40\r
Cache Set Status: Disable\r
Cache Status: Disable\r
LUN Distr Mode : concatenated\r
Mapped to Client : No\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUME_QUERY_TWO = """(null)@(null) ODSP CLI> lun mgt query -n SYS-LUN-Log\r
Name : SYS-LUN-Log\r
Device ID: 600B342EF209582D8D07D1EE4D0000DA\r
Total Size : 4GB\r
Current Owner(SP) : SP1\r
Owner(Pool) : SYS-Pool\r
Health Status : Normal\r
Is Reserved : Yes\r
Is Foreign : No\r
Created Time: 2021/12/23 11:26:44\r
Cache Set Status: Disable\r
Cache Status: Disable\r
LUN Distr Mode : concatenated\r
Mapped to Client : No\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""
VOLUME_ONE_NEW = """(null)@(null) ODSP CLI> lun mgt query -n SYS-LUN-Config\r
Name: SYS-LUN-Config\r
WWN: 600B342F1B0F9ABD7BABD272BD0000DA\r
Type: Standard-LUN\r
Is RDV LUN: No\r
Total Logical Size: 4GB (209715200sector)\r
Total Physical Size: 4GB (209715200sector)\r
Thin-Provisioning: Disable\r
Default Owner(SP): SP1\r
Current Owner(SP): SP1\r
Owner(Group): N/A\r
Owner(Pool): SYS-Pool\r
Health Status: Normal\r
Ua_type: ALUA\r
Is Reserved: No\r
Is Foreign: No\r
Write Zero Status: Disable\r
Created Time: 2020/03/02 17:49:15\r
Read Cache: Enable\r
Read Cache Status: Enable\r
Write Cache: Enable\r
Write Cache Status: Enable\r
Mapped to Client: No\r
LUN UUID: 0x50b34200-154800ee-a8746477-234b74a7\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUME_TWO_NEW = """(null)@(null) ODSP CLI> lun mgt query -n SYS-LUN-Log\r
Name: SYS-LUN-Log\r
WWN: 600B3423899AC1EDB125DCAE6D4E00D0\r
NGUID: 040F09004EE6CA2500B342B11EAC9938\r
Type: Standard-LUN\r
Is RDV LUN: No\r
Total Logical Size: 1GB (2097152sector)\r
Total Physical Size: 1GB (2097152sector)\r
Thin-Provisioning: Enable\r
Thin-LUN Extent Size: 16KB\r
Thin-LUN Private-area Allocate Mode: SSD RAID First\r
Thin-LUN Data-area Allocate Mode: HDD RAID First\r
Thin-LUN Expand Threshold: 30GB\r
Thin-LUN Expand Step Size: 50GB\r
Thin-LUN Allocated Physical Capacity: 1GB\r
Thin-LUN Allocated Physical Capacity Percentage: 100.0%\r
Thin-LUN Used Capacity: 3956KB\r
Thin-LUN Used Capacity Percentage: 0.0%\r
Thin-LUN Unused Capacity: 1,048,576KB\r
Thin-LUN Unused Capacity Percentage: 100.0%\r
Thin-LUN Distribute Mode: Single\r
Thin-LUN Dedup Switch: Disable\r
Thin-LUN Compress Switch: Disable\r
Default Owner(SP): SP1\r
Current Owner(SP): SP1\r
Owner(Group): N/A\r
Owner(Pool): Pool-1\r
Health Status: Normal\r
Ua_type: ALUA\r
Is Reserved: No\r
Is Foreign: No\r
Created Time: 2022/08/29 17:36:37\r
Read Cache: Enable\r
Read Cache Status: Enable\r
Write Cache: Enable\r
Write Cache Status: Enable\r
Mapped to Client: No\r
LUN UUID: 0x00b34204-0f09004e-e6ca25b1-1eac9938\r
Thin-LUN private UUID: 0x00b34204-0f09006f-6c27276c-a6d3f14b\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUME_TWO_INFO = """(null)@(null) ODSP CLI> lun mgt getlist -p pool-1\r
pool-1: 0 LUNs (0 Normal 0 Faulty)\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUMES_DATA = [
    {'name': 'SYS-LUN-Config', 'storage_id': '12345', 'status': 'normal',
     'native_volume_id': 'SYS-LUN-Config',
     'native_storage_pool_id': 'SYS-Pool', 'type': 'thick',
     'wwn': '600B342F1B0F9ABD7BABD272BD0000DA', 'total_capacity': 4294967296.0,
     'used_capacity': 4294967296.0, 'free_capacity': 0.0},
    {'name': 'SYS-LUN-Log', 'storage_id': '12345', 'status': 'normal',
     'native_volume_id': 'SYS-LUN-Log', 'native_storage_pool_id': 'Pool-1',
     'type': 'thin', 'wwn': '600B3423899AC1EDB125DCAE6D4E00D0',
     'total_capacity': 1073741824.0, 'used_capacity': 4050944.0,
     'free_capacity': 1069690880.0}]
THICK_VOLUMES_DATA = [
    {'name': 'SYS-LUN-Config', 'storage_id': '12345', 'status': 'normal',
     'native_volume_id': 'SYS-LUN-Config',
     'native_storage_pool_id': 'SYS-Pool', 'type': 'thick',
     'wwn': '600B342F1B0F9ABD7BABD272BD0000DA', 'total_capacity': 4294967296.0,
     'used_capacity': 4294967296.0, 'free_capacity': 0.0},
    {'name': 'SYS-LUN-Log', 'storage_id': '12345', 'status': 'normal',
     'native_volume_id': 'SYS-LUN-Log', 'native_storage_pool_id': 'SYS-Pool',
     'type': 'thick', 'wwn': '600B342EF209582D8D07D1EE4D0000DA',
     'total_capacity': 4294967296.0, 'used_capacity': 4294967296.0,
     'free_capacity': 0.0}]
VERSION_INFO = """(null)@(null) ODSP CLI> system mgt getversion\r
[SP1 Version]\r
SP1 ODSP_MSC Version: V2.0.14T04\r
SP1 ODSP_Driver Version: V607\r
\r
[SP2 Version]\r
SP2 ODSP_MSC Version: V2.0.14T04\r
SP2 ODSP_Driver Version: V607\r
\r
[SP3 Version]\r
SP3 ODSP_MSC Version: N/A\r
SP3 ODSP_Driver Version: N/A\r
\r
[SP4 Version]\r
SP4 ODSP_MSC Version: N/A\r
SP4 ODSP_Driver Version: N/A\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
CPU_INFO = """(null)@(null) ODSP CLI> system mgt getcpuinfo\r
[SP1 CPU Information]\r
SP1 Processor0 ID: 0\r
SP1 Processor0 Vendor_id: GenuineIntel\r
SP1 Processor0 CPU Frequency: 2200.000 MHz\r
SP1 Processor1 ID: 1\r
SP1 Processor1 Vendor_id: GenuineIntel\r
SP1 Processor1 CPU Frequency: 2200.000 MHz\r
SP1 Processor2 ID: 2\r
SP1 Processor2 Vendor_id: GenuineIntel\r
SP1 Processor2 CPU Frequency: 2200.000 MHz\r
SP1 Processor3 ID: 3\r
SP1 Processor3 Vendor_id: GenuineIntel\r
SP1 Processor3 CPU Frequency: 2200.000 MHz\r
\r
[SP2 CPU Information]\r
SP2 Processor0 ID: 0\r
SP2 Processor0 Vendor_id: GenuineIntel\r
SP2 Processor0 CPU Frequency: 2200.000 MHz\r
SP2 Processor1 ID: 1\r
SP2 Processor1 Vendor_id: GenuineIntel\r
SP2 Processor1 CPU Frequency: 2200.000 MHz\r
SP2 Processor2 ID: 2\r
SP2 Processor2 Vendor_id: GenuineIntel\r
SP2 Processor2 CPU Frequency: 2200.000 MHz\r
SP2 Processor3 ID: 3\r
SP2 Processor3 Vendor_id: GenuineIntel\r
SP2 Processor3 CPU Frequency: 2200.000 MHz\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""
HA_STATUS = """(null)@(null) ODSP CLI> ha mgt getstatus\r
SP1 HA Running Status  : dual--single\r
SP2 HA Running Status  : dual--single\r
SP3 HA Running Status  : absent--poweroff\r
SP4 HA Running Status  : absent--poweroff\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""
HA_STATUS_NEW = """(null)@(null) ODSP CLI> ha mgt getstatus\r
System HA Status       : normal\r
SP1 HA Running Status  : single\r
SP2 HA Running Status  : single\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""
CONTROLLERS_DATA = [
    {'name': 'SP1', 'storage_id': '12345', 'native_controller_id': 'SP1',
     'status': 'normal', 'location': 'SP1', 'soft_version': 'V2.0.14T04',
     'cpu_info': 'GenuineIntel@2200.000MHz', 'cpu_count': 1},
    {'name': 'SP2', 'storage_id': '12345', 'native_controller_id': 'SP2',
     'status': 'normal', 'location': 'SP2', 'soft_version': 'V2.0.14T04',
     'cpu_info': 'GenuineIntel@2200.000MHz', 'cpu_count': 1},
    {'name': 'SP3', 'storage_id': '12345', 'native_controller_id': 'SP3',
     'status': 'offline', 'location': 'SP3', 'soft_version': 'N/A',
     'cpu_info': ''},
    {'name': 'SP4', 'storage_id': '12345', 'native_controller_id': 'SP4',
     'status': 'offline', 'location': 'SP4', 'soft_version': 'N/A',
     'cpu_info': ''}]
DSU_INFO = """(null)@(null) ODSP CLI> dsu mgt getlist\r
DSUs Sum:1\r
\r
Name: DSU-7:1:1\r
Disks: 2\r
DSU EP1 SAS address: 500b342000dd26ff\r
DSU EP2 SAS address: 500b342000dd273f\r
\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
DISKS_INFO = """(null)@(null) ODSP CLI> disk mgt getlist -d 7:1:1\r
Disks Sum: 2\r
\r
Name: Disk-7:1:1:1\r
Type: SSD\r
Capacity: 893GB\r
Vendor: ATA\r
RPMs: 0\r
Health Status: Normal\r
Disk Role: Data disk\r
Owner(Pool): SYS-Pool\r
Owner(RAID): SYS-RAID\r
\r
Name: Disk-7:1:1:2\r
Type: SSD\r
Capacity: 893GB\r
Vendor: ATA\r
RPMs: 0\r
Health Status: Normal\r
Disk Role: Data disk\r
Owner(Pool): SYS-Pool\r
Owner(RAID): SYS-RAID\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
DISK_ONE = """(null)@(null) ODSP CLI> disk mgt query -d 7:1:1:1\r
Name: Disk-7:1:1:1\r
Type: HDD\r
Capacity: 893GB\r
Vendor: ATA\r
Model: Micron_5200_MTFDDAK960TDD\r
FW Version: U004\r
Serial Number: 18311E8D2787\r
Size: 2.5inch\r
RPMs: 0\r
Read Cache Setting: Enable\r
Write Cache Setting: Enable\r
Health Status: Normal\r
Role: Data disk\r
Owner(Pool): SYS-Pool\r
Owner(RAID): SYS-RAID\r
Locating Status: NO\r
SP1 Disk Online Status: Online\r
SP2 Disk Online Status: Online\r
SP3 Disk Online Status: Online\r
SP4 Disk Online Status: Online\r
SSD Estimated Life Remaining: N/A\r
SSD Estimated Time Remaining: N/A\r
SSD Applicable Scene: N/A\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
DISKS_TWO = """(null)@(null) ODSP CLI> disk mgt query -d 7:1:1:2\r
Name: Disk-7:1:1:2\r
Type: SSD\r
Capacity: 893GB\r
Vendor: ATA\r
Model: Micron_5200_MTFDDAK960TDD\r
FW Version: U004\r
Serial Number: 18311E8D2C03\r
Size: 2.5inch\r
RPMs: 0\r
Read Cache Setting: Enable\r
Write Cache Setting: Enable\r
Health Status: Normal\r
Role: Data disk\r
Owner(Pool): SYS-Pool\r
Owner(RAID): SYS-RAID\r
Locating Status: NO\r
SP1 Disk Online Status: Online\r
SP2 Disk Online Status: Online\r
SP3 Disk Online Status: Online\r
SP4 Disk Online Status: Online\r
SSD Estimated Life Remaining: N/A\r
SSD Estimated Time Remaining: N/A\r
SSD Applicable Scene: N/A\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
DISKS_DATA = [{'name': 'Disk-7:1:1:1', 'storage_id': '12345',
               'native_disk_id': 'Disk-7:1:1:1',
               'serial_number': '18311E8D2787', 'manufacturer': 'ATA',
               'model': 'Micron_5200_MTFDDAK960TDD', 'firmware': 'U004',
               'location': 'Disk-7:1:1:1', 'speed': 0,
               'capacity': 958851448832.0, 'status': 'normal',
               'physical_type': 'hdd', 'logical_type': 'data'},
              {'name': 'Disk-7:1:1:2', 'storage_id': '12345',
               'native_disk_id': 'Disk-7:1:1:2',
               'serial_number': '18311E8D2C03', 'manufacturer': 'ATA',
               'model': 'Micron_5200_MTFDDAK960TDD', 'firmware': 'U004',
               'location': 'Disk-7:1:1:2', 'speed': 0,
               'capacity': 958851448832.0, 'status': 'normal',
               'physical_type': 'ssd', 'logical_type': 'data'}]
FC_INFO = """(null)@(null) ODSP CLI> client target queryportlist\r
fc port-1:4:1\r
wwn                 : 50:0b:34:20:02:fe:b5:0d\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-1:4:2\r
wwn                 : 50:0b:34:20:02:fe:b5:0e\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-1:4:3\r
wwn                 : 50:0b:34:20:02:fe:b5:0f\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-1:4:4\r
wwn                 : 50:0b:34:20:02:fe:b5:10\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-2:4:1\r
wwn                 : 50:0b:34:20:02:fe:b3:0d\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-2:4:2\r
wwn                 : 50:0b:34:20:02:fe:b3:0e\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-2:4:3\r
wwn                 : 50:0b:34:20:02:fe:b3:0f\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
fc port-2:4:4\r
wwn                 : 50:0b:34:20:02:fe:b3:10\r
online state        : 2\r
actual speed        : 0\r
port topology       : 0\r
initiator num       : 0\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
SAS_INFO = """(null)@(null) ODSP CLI>system sas getportlist -c 1:1\r
SAS Controller 1:1 Ports Sum:2\r
\r
SAS-1:1:1 Link Status: Full-Linkup\r
SAS-1:1:1 PHY Max Speed: 12Gbps\r
SAS-1:1:1 PHY1 Speed: 12Gbps\r
SAS-1:1:1 PHY2 Speed: 12Gbps\r
SAS-1:1:1 PHY3 Speed: 12Gbps\r
SAS-1:1:1 PHY4 Speed: 12Gbps\r
\r
SAS-1:1:2 Link Status: Full-Linkup\r
SAS-1:1:2 PHY Max Speed: 12Gbps\r
SAS-1:1:2 PHY1 Speed: 6Gbps\r
SAS-1:1:2 PHY2 Speed: 6Gbps\r
SAS-1:1:2 PHY3 Speed: 6Gbps\r
SAS-1:1:2 PHY4 Speed: 6Gbps\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
PORT_DATA = [{'native_port_id': 'FC-1:4:1', 'name': 'FC-1:4:1', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-1:4:1',
              'storage_id': '12345', 'native_parent_id': 'SP1', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b5:0d'},
             {'native_port_id': 'FC-1:4:2', 'name': 'FC-1:4:2', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-1:4:2',
              'storage_id': '12345', 'native_parent_id': 'SP1', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b5:0e'},
             {'native_port_id': 'FC-1:4:3', 'name': 'FC-1:4:3', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-1:4:3',
              'storage_id': '12345', 'native_parent_id': 'SP1', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b5:0f'},
             {'native_port_id': 'FC-1:4:4', 'name': 'FC-1:4:4', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-1:4:4',
              'storage_id': '12345', 'native_parent_id': 'SP1', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b5:10'},
             {'native_port_id': 'FC-2:4:1', 'name': 'FC-2:4:1', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-2:4:1',
              'storage_id': '12345', 'native_parent_id': 'SP2', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b3:0d'},
             {'native_port_id': 'FC-2:4:2', 'name': 'FC-2:4:2', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-2:4:2',
              'storage_id': '12345', 'native_parent_id': 'SP2', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b3:0e'},
             {'native_port_id': 'FC-2:4:3', 'name': 'FC-2:4:3', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-2:4:3',
              'storage_id': '12345', 'native_parent_id': 'SP2', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b3:0f'},
             {'native_port_id': 'FC-2:4:4', 'name': 'FC-2:4:4', 'type': 'fc',
              'logical_type': 'physical', 'connection_status': 'disconnected',
              'health_status': 'unknown', 'location': 'FC-2:4:4',
              'storage_id': '12345', 'native_parent_id': 'SP2', 'speed': 0.0,
              'wwn': '50:0b:34:20:02:fe:b3:10'},
             {'native_port_id': 'SAS-1:1:1', 'name': 'SAS-1:1:1',
              'type': 'sas', 'logical_type': 'physical',
              'connection_status': 'connected', 'health_status': 'unknown',
              'location': 'SAS-1:1:1', 'storage_id': '12345',
              'native_parent_id': 'SP1', 'max_speed': 12000000000,
              'speed': 12000000000},
             {'native_port_id': 'SAS-1:1:2', 'name': 'SAS-1:1:2',
              'type': 'sas', 'logical_type': 'physical',
              'connection_status': 'connected', 'health_status': 'unknown',
              'location': 'SAS-1:1:2', 'storage_id': '12345',
              'native_parent_id': 'SP1', 'max_speed': 12000000000,
              'speed': 6000000000}]
PARSE_ALERT_INFO = {
    '1.3.6.1.2.1.1.3.0': '2995472',
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.35904.1.3.3',
    '1.3.6.1.2.1.25.1.2': '2022-07-12 17:43:40',
    '1.3.6.1.4.1.35904.1.2.1.1': 'Storage-1',
    '1.3.6.1.4.1.35904.1.2.1.4.1': 'Battery_expired',
    '1.3.6.1.4.1.35904.1.2.1.4.2': 'SP1',
    '1.3.6.1.4.1.35904.1.2.1.4.3': "SSU-7:1:1's battery '2' becomes expired,"
                                   " please prepare a new module and replace"
                                   " it as soon as possible.",
    '1.3.6.1.4.1.35904.1.2.1.4.4': '2',
    'transport_address': '192.168.3.235',
    'storage_id': '05e007e4-62ef-4e24-a14e-57a8ee8e5bf3'}
PARSE_ALERT_DATA = {
    'alert_id': '2995472', 'severity': 'Major',
    'category': 'Fault', 'occur_time': 1657619020000,
    'description': "SSU-7:1:1's battery '2' becomes expired, please prepare"
                   " a new module and replace it as soon as possible.",
    'location': 'Storage-1:SP1', 'type': 'EquipmentAlarm',
    'resource_type': 'Storage',
    'alert_name': '电池模块超期',
    'match_key': 'ec62c3cdd862da9b0f8da6d03d97d76e'}
INITIATOR_INFO = """(null)@(null) ODSP CLI> client initiator getlist -t all\r
Initiators Sum: 3\r

Initiator Alias: VMWare\r
Initiator WWN: 20:18:f8:2e:3f:f9:85:54\r
Type: FC\r
OS: AIX\r
IP Address Used in Last iSCSI Login Session: N/A\r
Mapped Client: Client-1\r
Mapped Targets Sum: 2\r
Mapped LUNs Sum: 6\r
\r
Initiator Alias: ds\r
Initiator WWN: 20:ab:30:48:56:01:fc:31\r
Type: FC\r
OS: Other\r
IP Address Used in Last iSCSI Login Session: N/A\r
Mapped Client: Client-2\r
Mapped Targets Sum: 1\r
Mapped LUNs Sum: 1\r
\r
Initiator Alias: dc\r
Initiator WWN: 42:25:dc:35:ab:69:12:cb\r
Type: FC\r
OS: HP_UNIX\r
IP Address Used in Last iSCSI Login Session: N/A\r
Mapped Client: Client-2\r
Mapped Targets Sum: 1\r
Mapped LUNs Sum: 2\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
INITIATOR_DATA = [
    {'native_storage_host_initiator_id': '20:18:f8:2e:3f:f9:85:54',
     'native_storage_host_id': 'Client-1', 'name': '20:18:f8:2e:3f:f9:85:54',
     'alias': 'VMWare', 'type': 'fc', 'status': 'unknown',
     'wwn': '20:18:f8:2e:3f:f9:85:54', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '20:ab:30:48:56:01:fc:31',
     'native_storage_host_id': 'Client-2', 'name': '20:ab:30:48:56:01:fc:31',
     'alias': 'ds', 'type': 'fc', 'status': 'unknown',
     'wwn': '20:ab:30:48:56:01:fc:31', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '42:25:dc:35:ab:69:12:cb',
     'native_storage_host_id': 'Client-2', 'name': '42:25:dc:35:ab:69:12:cb',
     'alias': 'dc', 'type': 'fc', 'status': 'unknown',
     'wwn': '42:25:dc:35:ab:69:12:cb', 'storage_id': '12345'}]
UNKNOWN_COMMAND = """(null)@(null) ODSP CLI> client host gethostlist
% Unknown command.
(null)@(null) ODSP CLI> """
HOSTS_INFO = """(null)@(null) ODSP CLI> client mgt getclientlist\r
Clients Sum: 7\r
\r
Name: Client-1\r
Description: ds  mss\r
Mapped Initiators Num: 1\r
\r
Name: Client-2\r
Description: \r
Mapped Initiators Num: 2\r
\r
Name: Client-3\r
Description: sss\r
Mapped Initiators Num: 0\r
\r
Name: Client-4\r
Description: dsd\r
Mapped Initiators Num: 0\r
\r
Name: Client-5\r
Description: ds\r
Mapped Initiators Num: 0\r
\r
Name: Client-6\r
Description: \r
Mapped Initiators Num: 0\r
\r
Name: 5\r
Description: \r
Mapped Initiators Num: 0\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
HOST_INFO_NEW = """(null)@(null) ODSP CLI> client host gethostlist\r
Host Sum: 1\r
\r
Host Name: Host-1\r
OS: Windows2008\r
IP Address: 192.168.1.20\r
Description: Server 1\r
Location: Room-201\r
Initiators Sum: 4\r
iSCSI Initiators Sum: 2\r
FC Initiators Sum: 2\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
HOST_DATA = [{'name': 'Client-1', 'storage_id': '12345',
              'native_storage_host_id': 'Client-1', 'os_type': 'AIX',
              'status': 'normal', 'description': 'ds  mss'},
             {'name': 'Client-2', 'storage_id': '12345',
              'native_storage_host_id': 'Client-2', 'os_type': 'HP-UX',
              'status': 'normal', 'description': ''},
             {'name': 'Client-3', 'storage_id': '12345',
              'native_storage_host_id': 'Client-3', 'os_type': 'Unknown',
              'status': 'normal', 'description': 'sss'},
             {'name': 'Client-4', 'storage_id': '12345',
              'native_storage_host_id': 'Client-4', 'os_type': 'Unknown',
              'status': 'normal', 'description': 'dsd'},
             {'name': 'Client-5', 'storage_id': '12345',
              'native_storage_host_id': 'Client-5', 'os_type': 'Unknown',
              'status': 'normal', 'description': 'ds'},
             {'name': 'Client-6', 'storage_id': '12345',
              'native_storage_host_id': 'Client-6', 'os_type': 'Unknown',
              'status': 'normal', 'description': ''},
             {'name': '5', 'storage_id': '12345',
              'native_storage_host_id': '5', 'os_type': 'Unknown',
              'status': 'normal', 'description': ''}]
HOST_DATA_NEW = [{'name': 'Host-1', 'storage_id': '12345',
                  'native_storage_host_id': 'Host-1', 'os_type': 'Windows',
                  'status': 'normal', 'description': 'Server 1',
                  'ip_address': '192.168.1.20'}]
HOST_GROUPS_INFO = """(null)@(null) ODSP CLI> client hostgroup gethglist\r
Host Groups Sum: 1\r
\r
Host Group Name: Host-Group-1\r
Description: Host Group\r
Hosts Sum: 1\r
Initiators Sum: 4\r
iSCSI Initiators Sum: 2\r
FC Initiators Sum: 2\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
HOST_GROUPS_H_INFO = """(null)@(null) ODSP CLI> client hostgroup gethostlist\
 -n Host-Group-1\r
Hosts Sum: 1\r
\r
HostName: Host-1\r
OS: Windows2008\r
IP Address: 192.168.1.20\r
Description: Server1\r
Location: Room-201\r
Initiators Sum: 4\r
iSCSI Initiators Sum: 2\r
FC Initiators Sum: 2\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
HOST_GROUPS_DATA = {
    'storage_host_groups': [
        {'name': 'Host-Group-1', 'storage_id': '12345',
         'native_storage_host_group_id': 'Host-Group-1',
         'description': 'Host Group'}
    ],
    'storage_host_grp_host_rels': [
        {'storage_id': '12345', 'native_storage_host_group_id': 'Host-Group-1',
         'native_storage_host_id': 'Host-1'}
    ]
}
VOLUME_GROUPS_INFO = """(null)@(null) ODSP CLI> client lungroup getlglist\r
LUN Group Sum: 1\r
\r
LUN Group Name: LUN-Group-1\r
Description: LUN Group description\r
LUNs Sum: 4\r
Local LUNs Sum: 4\r
Remote LUNs Sum: 0\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUME_GROUPS_N_INFO = """(null)@(null) ODSP CLI> client lungroup getlunlist\
 -n LUN-Group-1\r
LUNs Sum: 1\r
\r
LUN Name: LUN-0001/N/A\r
Location: Local/Remote\r
LUN Capacity: 10GB (20971520sector)/N/A\r
LUN WWN: 600B34249837CEBDC611DCB12DD500D6/N/A\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VOLUME_GROUP_DATA = {'volume_groups': [
    {'name': 'LUN-Group-1', 'storage_id': '12345',
     'native_volume_group_id': 'LUN-Group-1',
     'description': 'LUN Group description'}], 'vol_grp_vol_rels': [
    {'storage_id': '12345', 'native_volume_group_id': 'LUN-Group-1',
     'native_volume_id': 'LUN-0001/N/A'}]}
VIEWS_ONE = """(null)@(null) ODSP CLI> client mgt getsharelunlist -n Client-1\r
LUNs Sum: 6\r
\r
LUN Name: Test_Lun-1\r
LUN Capacity: 10GB\r
LUN WWN: 600B3427C77BBDFD2FF0DBA82D0000DB\r
LUN ID: 0\r
Access Mode: Read-Write\r
Thin-Provisioning: Disable\r
\r
LUN Name: Test_Lun-2\r
LUN Capacity: 10GB\r
LUN WWN: 600B342A316B328D7035DD724D0000DB\r
LUN ID: 1\r
Access Mode: Read-Write\r
Thin-Provisioning: Disable\r
\r
LUN Name: Test_Lun-3\r
LUN Capacity: 10GB\r
LUN WWN: 600B342AB2FE2ACDBC63D8B0DD0000DB\r
LUN ID: 2\r
Access Mode: Read-Write\r
Thin-Provisioning: Disable\r
\r
LUN Name: Test_Lun-4\r
LUN Capacity: 10GB\r
LUN WWN: 600B342B328A722D55F7DEF5DD0000DB\r
LUN ID: 3\r
Access Mode: Read-Write\r
Thin-Provisioning: Disable\r
\r
LUN Name: Test_Lun-5\r
LUN Capacity: 10GB\r
LUN WWN: 600B34221067D72D65DFD18C8D0000DB\r
LUN ID: 4\r
Access Mode: Read-Write\r
Thin-Provisioning: Disable\r
\r
LUN Name: LUN-1\r
LUN Capacity: 2GB\r
LUN WWN: 600B342A816A4F2D9098DB015D0000DB\r
LUN ID: 5\r
Access Mode: Read-Write\r
Thin-Provisioning: Disable\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VIEW_TWO = """(null)@(null) ODSP CLI> client mgt getsharelunlist -n Client-2\r
LUNs Sum: 0\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VIEWS_DATA = [{'native_masking_view_id': 'Client-10', 'name': 'Client-10',
               'native_storage_host_id': 'Client-1', 'native_volume_id': '0',
               'storage_id': '12345'},
              {'native_masking_view_id': 'Client-11', 'name': 'Client-11',
               'native_storage_host_id': 'Client-1', 'native_volume_id': '1',
               'storage_id': '12345'},
              {'native_masking_view_id': 'Client-12', 'name': 'Client-12',
               'native_storage_host_id': 'Client-1', 'native_volume_id': '2',
               'storage_id': '12345'},
              {'native_masking_view_id': 'Client-13', 'name': 'Client-13',
               'native_storage_host_id': 'Client-1', 'native_volume_id': '3',
               'storage_id': '12345'},
              {'native_masking_view_id': 'Client-14', 'name': 'Client-14',
               'native_storage_host_id': 'Client-1', 'native_volume_id': '4',
               'storage_id': '12345'},
              {'native_masking_view_id': 'Client-15', 'name': 'Client-15',
               'native_storage_host_id': 'Client-1', 'native_volume_id': '5',
               'storage_id': '12345'}]
VIEW_NEW_INFO = """client mapview getlist\r
Mapviews Sum: 1\r
\r
Mapview Name: Mapview-1\r
Description: Map view\r
Host Group Name: Host-Group-1\r
Target Group Name: Target-Group-1\r
LUN Group Name: LUN-Group-1\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
VIEWS_NEW_DATA = [{'native_masking_view_id': 'Mapview-1', 'name': 'Mapview-1',
                   'native_storage_host_group_id': 'Host-Group-1',
                   'native_volume_group_id': 'LUN-Group-1',
                   'description': 'Map view', 'storage_id': '12345'}]
SYSTEM_QUERY = """(null)@(null) ODSP CLI> system mgt query\r
system mgt query\r
Device UUID:0x00b34202-fea90000-fa41e0d6-ded905a8\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
SYSTEM_QUERY_TWO = """(null)@(null) ODSP CLI> system mgt query\r
Device UUID:0x50b34200-0b750056-42ab74ff-6265d80e\r
Device Name:Storage-1\r
Command completed successfully.\r
(null)@(null) ODSP CLI> """
STORAGE_DATA = {
    'name': '0x00b34202-fea90000-fa41e0d6-ded905a8',
    'vendor': 'MacroSAN', 'status': 'normal',
    'serial_number': '110.143.133.200:0x00b34202-fea90000-fa41e0d6-ded905a8',
    'firmware_version': 'V2.0.14T04',
    'raw_capacity': 1917702897664.0,
    'total_capacity': 7670811590656.0,
    'used_capacity': 1031865892864.0,
    'free_capacity': 6638945697792.0,
    'model': ''
}
STORAGE_TWO_DATA = {
    'name': 'Storage-1', 'vendor': 'MacroSAN',
    'status': 'normal',
    'serial_number': '110.143.133.200:0x50b34200-0b750056-42ab74ff-6265d80e',
    'firmware_version': 'V2.0.14T04',
    'raw_capacity': 1917702897664.0,
    'total_capacity': 7670811590656.0,
    'used_capacity': 1031865892864.0,
    'free_capacity': 6638945697792.0,
    'model': ''
}
TIMESTAMP = """[root@00-b3-42-04-0f-09 ~]# date +%s\r
1662345266\r
[root@00-b3-42-04-0f-09 ~]#"""
VERSION_SHOW = """[root@00-b3-42-04-0f-09 ~]# versionshow\r
\r
SP2 Version:\r
        ODSP_MSC: V1.5.12T03\r
        ODSP_DRIVER: V230T03\r
        BIOS    : V166\r
        BMC     : V272P001\r
        MCPLD   : V104\r
        MPCB    : VER.B\r
        BCB1    : V214\r
        BCB2    : V214\r
        BAT1HW  : BAT1111A\r
        BAT2HW  : FAN2021A\r
        IOC1PCB :\r
        IOC2PCB :\r
DSU : 1:1:1\r
        ODSP_JMC : V221\r
        ODSP_JMCB: N/A\r
        EPCB     : N/A\r
        ECPLD    : V101\r
        BAT0_BCB : N/A\r
        BAT1_BCB : N/A\r
\r
[root@00-b3-42-04-0f-09 ~]#"""
GET_FILE_LIST = """(null)@(null) ODSP CLI> system performance getfilelist\r
Performance Statistics Files Sum:2\r

SP Name: SP2\r
Object Type: DEVICE\r
Object Name: Device\r
Object Identification: N/A\r
File Name: perf_device_SP2_20220920181959.csv\r
File Create Time: 2022-09-20 18:19:59\r
File Size: 58 KB\r
\r
SP Name: SP2\r
Object Type: SAS PORT\r
Object Name: SAS-2:1:1\r
Object Identification: N/A\r
File Name: perf_sasport_SAS-2_1_1_SP2_20220920181959.csv\r
File Create Time: 2022-09-20 18:19:59\r
File Size: 56 KB\r
\r
Command completed successfully.\r
(null)@(null) ODSP CLI>"""
resource_metrics = {
    constants.ResourceType.STORAGE: consts.STORAGE_CAP,
    constants.ResourceType.VOLUME: consts.VOLUME_CAP,
    constants.ResourceType.PORT: consts.PORT_CAP
}


def create_driver():
    MsHandler.login = mock.Mock(
        return_value={None})
    return MacroSanDriver(**ACCESS_INFO)


class test_macro_san_driver(TestCase):
    driver = create_driver()

    def test_init(self):
        MsHandler.login = mock.Mock(
            return_value={""})
        MacroSanDriver(**ACCESS_INFO)

    def test_get_storage(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[SYSTEM_QUERY, VERSION_INFO,
                         POOLS_INFO, RAID_SYS_POOL, RAID_POOL_1,
                         DSU_INFO, DISKS_INFO, DISK_ONE, DISKS_TWO,
                         HA_STATUS, VERSION_INFO, CPU_INFO, HA_STATUS,
                         VERSION_SHOW])
        MacroSanSSHPool.create = mock.Mock(__class__)
        SSHClient.open_sftp = mock.Mock(__class__)
        storage_object = self.driver.get_storage(context)
        self.assertDictEqual(storage_object, STORAGE_DATA)

    def test_get_storage_new(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[SYSTEM_QUERY_TWO, VERSION_INFO,
                         POOLS_INFO, RAID_SYS_POOL, RAID_POOL_1,
                         DSU_INFO, DISKS_INFO, DISK_ONE, DISKS_TWO,
                         HA_STATUS_NEW, VERSION_INFO, CPU_INFO, HA_STATUS_NEW,
                         VERSION_SHOW])
        MacroSanSSHPool.create = mock.Mock(__class__)
        SSHClient.open_sftp = mock.Mock(__class__)
        storage_object = self.driver.get_storage(context)
        self.assertDictEqual(storage_object, STORAGE_TWO_DATA)

    def test_list_storage_pools(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[POOLS_INFO, RAID_SYS_POOL, RAID_POOL_1])
        pools = self.driver.list_storage_pools(context)
        self.assertListEqual(pools, POOLS_DATA)

    def test_list_volumes(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[POOLS_INFO, RAID_SYS_POOL, RAID_POOL_1,
                         VOLUME_INFO, VOLUME_QUERY_ONE, VOLUME_QUERY_TWO,
                         VOLUME_TWO_INFO])
        volumes = self.driver.list_volumes(context)
        self.assertListEqual(volumes, THICK_VOLUMES_DATA)

    def test_list_volumes_new(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[POOLS_INFO, RAID_SYS_POOL, RAID_POOL_1,
                         VOLUME_INFO, VOLUME_ONE_NEW, VOLUME_TWO_NEW,
                         VOLUME_TWO_INFO])
        volumes = self.driver.list_volumes(context)
        self.assertListEqual(volumes, VOLUMES_DATA)

    def test_list_controllers(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VERSION_INFO, CPU_INFO, HA_STATUS])
        controllers = self.driver.list_controllers(context)
        self.assertListEqual(controllers, CONTROLLERS_DATA)

    def test_list_disks(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[DSU_INFO, DISKS_INFO, DISK_ONE, DISKS_TWO])
        disks = self.driver.list_disks(context)
        self.assertListEqual(disks, DISKS_DATA)

    def test_list_ports(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[FC_INFO, HA_STATUS, DSU_INFO, SAS_INFO, None, None,
                         None])
        ports = self.driver.list_ports(context)
        self.assertListEqual(ports, PORT_DATA)

    def test_parse_alert(self):
        parse_alert = self.driver.parse_alert(context, PARSE_ALERT_INFO)
        PARSE_ALERT_DATA['occur_time'] = parse_alert.get('occur_time')
        self.assertDictEqual(parse_alert, PARSE_ALERT_DATA)

    def test_list_storage_host_initiators(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[INITIATOR_INFO])
        initiators = self.driver.list_storage_host_initiators(context)
        self.assertListEqual(initiators, INITIATOR_DATA)

    def test_list_storage_hosts_old(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[consts.UNKNOWN_COMMAND_TAG,
                         INITIATOR_INFO, HOSTS_INFO])
        hosts = self.driver.list_storage_hosts(context)
        self.assertListEqual(hosts, HOST_DATA)

    def test_list_storage_hosts_new(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[HOST_INFO_NEW])
        hosts = self.driver.list_storage_hosts(context)
        self.assertListEqual(hosts, HOST_DATA_NEW)

    def test_list_storage_hosts_group(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[HOST_GROUPS_INFO, HOST_GROUPS_H_INFO])
        host_groups = self.driver.list_storage_host_groups(context)
        self.assertDictEqual(host_groups, HOST_GROUPS_DATA)

    def test_list_volume_groups(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VOLUME_GROUPS_INFO, VOLUME_GROUPS_N_INFO])
        volume_groups = self.driver.list_volume_groups(context)
        self.assertDictEqual(volume_groups, VOLUME_GROUP_DATA)

    def test_list_masking_views_old(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[consts.UNKNOWN_COMMAND_TAG,
                         HOSTS_INFO, VIEWS_ONE, VIEW_TWO, VIEW_TWO, VIEW_TWO,
                         VIEW_TWO, VIEW_TWO, VIEW_TWO])
        views = self.driver.list_masking_views(context)
        self.assertListEqual(views, VIEWS_DATA)

    def test_list_masking_views_new(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VIEW_NEW_INFO])
        views = self.driver.list_masking_views(context)
        self.assertListEqual(views, VIEWS_NEW_DATA)

    def test_list_alert(self):
        block = False
        try:
            self.driver.list_alerts(context)
        except Exception as e:
            LOG.error(six.text_type(e))
            block = True
        self.assertEqual(block, True)

    def test_get_latest_perf_timestamp(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[TIMESTAMP])
        timestamp = self.driver.get_latest_perf_timestamp(context)
        times = 1662345240000
        self.assertEqual(timestamp, times)

    def test_get_capabilities(self):
        capabilities = self.driver.get_capabilities(context)
        metrics = {
            'is_historic': True,
            'resource_metrics': {
                constants.ResourceType.STORAGE: consts.STORAGE_CAP,
                constants.ResourceType.VOLUME: consts.VOLUME_CAP,
                constants.ResourceType.PORT: consts.PORT_CAP,
                constants.ResourceType.DISK: consts.DISK_CAP,
            }
        }
        self.assertDictEqual(capabilities, metrics)

    def test_collect_perf_metrics(self):
        MacroSanSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        MacroSanSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VERSION_SHOW, GET_FILE_LIST])
        MsHandler.down_perf_file = mock.Mock(return_value='')
        MacroSanSSHPool.create = mock.Mock(__class__)
        SSHClient.open_sftp = mock.Mock(__class__)
        localtime = time.mktime(time.localtime()) * units.k
        storage_id = 12345
        start_time = localtime - 1000 * 60 * 5
        end_time = localtime
        metrics = self.driver.collect_perf_metrics(
            context, storage_id, resource_metrics, start_time, end_time)
        self.assertListEqual(metrics, [])
