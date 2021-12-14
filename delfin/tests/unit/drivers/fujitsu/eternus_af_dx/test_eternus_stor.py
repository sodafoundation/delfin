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
import sys
from unittest import TestCase, mock

sys.modules['delfin.cryptor'] = mock.Mock()

from delfin.drivers.fujitsu.eternus.eternus_ssh_client import \
    EternusSSHPool
import paramiko
from delfin import context
from delfin.drivers.fujitsu.eternus.eternus_stor import \
    EternusDriver


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "fujitsu",
    "model": "eternus_af650s2",
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    }
}

STORAGE_NAME_DATA = """
Name              [dx100-test]
Installation Site [test location]
Contact           []
Description       [test dx100-test]
CLI>
"""
STORAGE_MODEL_DATA = """
Enclosure View
 Storage System Name               [dx100-test]
 Model Upgrade Status              [Not Upgraded]
 Model Name                        [ET103ACU]
 Serial Number                     [4601620378]
 Device Identification Number      [280A7D]
 Status                            [Normal]
 Cache Mode                        [Write Back Mode]
 Remote Support                    [Not yet Set]
 Operation Mode                    [Normal]
 CLI Connecting Controller Module  [CM#0]
 Firmware Version                  [V10L50-9003]

 Controller Enclosure (2.5")       [Normal (Inside unused parts)]
CLI>
"""
STORAGE_STATUS_DATA = """
Summary Status  [Normal]
CLI>
"""
NODE_DATAS = """
CM#0 Information
 CPU Status/Status Code    [Normal      / 0xE001]
 Memory Size               [4.0GB]
 Parts Number              [CA07662-D111]
 Serial Number             [WK16201983]
 Hard Revision             [AA]
 CPU Clock                 [1.40GHz]
 CM Active EC              [EC#1]
 CM Next EC                [EC#1]
 BIOS Active EC            [EC#1]
 BIOS Next EC              [EC#1]
 CM EXP Active EC          [EC#1]
 CM EXP Next EC            [EC#1]
CM#0 Internal Parts Status/Status Code
 Memory#0                  [Normal      / 0xE001]
 Memory#0 Parts Number     [18KDF51272PZ-1G6K1]
 Memory#0 Serial Number    [1612121A68F5]
 Memory#0 Hard Revision    [0F4B31]
 Memory#1                  [Undefined   / 0x0000]
 Memory#1 Parts Number     []
 Memory#1 Serial Number    []
 Memory#1 Hard Revision    []
 BUD                       [Normal      / 0xE001]
 BUD Parts Number          [TOSHIBA THNSNJ12]
 BUD Serial Number         [56DS10ABTNWV    ]
 BUD Hard Revision         [JYFA0101]
 Port#0                    [Unconnected / 0xC000] (Error Code : 0x0000)
 Port#1                    [Unconnected / 0xC000] (Error Code : 0x0000)
 Port#2                    [Undefined   / 0x0000]
 Port#3                    [Undefined   / 0x0000]
 DMA Port#0                [Normal      / 0xE001]
 DMA Port#1                [Undefined   / 0x0000]
 BIOS#0                    [Normal      / 0xE001]
 BIOS#1                    [Normal      / 0xE001]
 CM EXP                    [Normal      / 0xE001]
 CM EXP InPort#0           [Normal      / 0xE001]
 CM EXP InPort#1           [Normal      / 0xE001]
 SAS Cable#0(OUT)          [Undefined   / 0x0000]
 SAS Cable#1(OUT)          [Undefined   / 0x0000]
 CM RTC                    [Normal      / 0xE001]
 CM NVRAM                  [Normal      / 0xE001]
 CM FPGA                   [Normal      / 0xE001]
 CM LAN Port#0             [Normal      / 0xE001]
 CM LAN Port#1             [Normal      / 0xE001]
 CM LAN Port#2             [Undefined   / 0x0000]
 DI#0 Port#0               [Normal      / 0xE001]
 DI#0 Port#1               [Normal      / 0xE001]
 DI#1 Port#0               [Undefined   / 0x0000]
 DI#1 Port#1               [Undefined   / 0x0000]
 SATA SSD Controller Information
  Status/Status Code       [Normal      / 0xE001]
  Active EC                [EC#1]
  Next EC                  [EC#1]
  Firmware Version         [V03L04-0000]
 SCU                       [Normal      / 0xE001]
 SCU Voltage               [11.16V]
CM#0 CA#0 Port#0 Information
 Port Type           [FC]
 Port Mode           [CA]
 Status/Status Code  [Unconnected / 0xC000] (Error Code : 0x0000)
 CA Active EC        [EC#0]
 CA Next EC          [EC#0]
 Connection          [Loop]
 Loop ID             [0x00]
 Transfer Rate       [Auto Negotiation]
 Link Status         [Unknown]
 Port WWN            [500000E0DA0A7D20]
 Node WWN            [500000E0DA0A7D40]
 Host Affinity       [Disable]
 Host Response       [0]
 SFP Type            [Unmount]
 SFP Information
                  Present    Warning(Low/High)      Alarm(Low/High)
  Temperature         [-]                [-/-]                [-/-]
  Voltage             [-]                [-/-]                [-/-]
  Current             [-]                [-/-]                [-/-]
  TX Power            [-]                [-/-]                [-/-]
  RX Power            [-]                [-/-]                [-/-]
CM#0 CA#0 Port#1 Information
 Port Type           [FC]
 Port Mode           [CA]
 Status/Status Code  [Unconnected / 0xC000] (Error Code : 0x0000)
 CA Active EC        [EC#0]
 CA Next EC          [EC#0]
 Connection          [Loop]
 Loop ID             [0x00]
 Transfer Rate       [Auto Negotiation]
 Link Status         [Unknown]
 Port WWN            [500000E0DA0A7D21]
 Node WWN            [500000E0DA0A7D40]
 Host Affinity       [Disable]
 Host Response       [0]
 SFP Type            [Unmount]
 SFP Information
                  Present    Warning(Low/High)      Alarm(Low/High)
  Temperature         [-]                [-/-]                [-/-]
  Voltage             [-]                [-/-]                [-/-]
  Current             [-]                [-/-]                [-/-]
  TX Power            [-]                [-/-]                [-/-]
  RX Power            [-]                [-/-]                [-/-]
CM#1 Information
 CPU Status/Status Code    [Normal      / 0xE001]
 Memory Size               [4.0GB]
 Parts Number              [CA07662-D111]
 Serial Number             [WK16201958]
 Hard Revision             [AA]
 CPU Clock                 [1.40GHz]
 CM Active EC              [EC#1]
 CM Next EC                [EC#1]
 BIOS Active EC            [EC#1]
 BIOS Next EC              [EC#1]
 CM EXP Active EC          [EC#1]
 CM EXP Next EC            [EC#1]
CM#1 Internal Parts Status/Status Code
 Memory#0                  [Normal      / 0xE001]
 Memory#0 Parts Number     [18KDF51272PZ-1G6K1]
 Memory#0 Serial Number    [1612121A6900]
 Memory#0 Hard Revision    [0F4B31]
 Memory#1                  [Undefined   / 0x0000]
 Memory#1 Parts Number     []
 Memory#1 Serial Number    []
 Memory#1 Hard Revision    []
 BUD                       [Normal      / 0xE001]
 BUD Parts Number          [TOSHIBA THNSNJ12]
 BUD Serial Number         [56DS1086TNWV    ]
 BUD Hard Revision         [JYFA0101]
 Port#0                    [Unconnected / 0xC000] (Error Code : 0x0000)
 Port#1                    [Unconnected / 0xC000] (Error Code : 0x0000)
 Port#2                    [Undefined   / 0x0000]
 Port#3                    [Undefined   / 0x0000]
 DMA Port#0                [Normal      / 0xE001]
 DMA Port#1                [Undefined   / 0x0000]
 BIOS#0                    [Normal      / 0xE001]
 BIOS#1                    [Normal      / 0xE001]
 CM EXP                    [Normal      / 0xE001]
 CM EXP InPort#0           [Normal      / 0xE001]
 CM EXP InPort#1           [Normal      / 0xE001]
 SAS Cable#0(OUT)          [Undefined   / 0x0000]
 SAS Cable#1(OUT)          [Undefined   / 0x0000]
 CM RTC                    [Normal      / 0xE001]
 CM NVRAM                  [Normal      / 0xE001]
 CM FPGA                   [Normal      / 0xE001]
 CM LAN Port#0             [Normal      / 0xE001]
 CM LAN Port#1             [Normal      / 0xE001]
 CM LAN Port#2             [Undefined   / 0x0000]
 DI#0 Port#0               [Normal      / 0xE001]
 DI#0 Port#1               [Normal      / 0xE001]
 DI#1 Port#0               [Undefined   / 0x0000]
 DI#1 Port#1               [Undefined   / 0x0000]
 SATA SSD Controller Information
  Status/Status Code       [Normal      / 0xE001]
  Active EC                [EC#1]
  Next EC                  [EC#1]
  Firmware Version         [V03L04-0000]
 SCU                       [Normal      / 0xE001]
 SCU Voltage               [11.16V]
CM#1 CA#0 Port#0 Information
 Port Type           [FC]
 Port Mode           [CA]
 Status/Status Code  [Unconnected / 0xC000] (Error Code : 0x0000)
 CA Active EC        [EC#0]
 CA Next EC          [EC#0]
 Connection          [Loop]
 Loop ID             [0x00]
 Transfer Rate       [Auto Negotiation]
 Link Status         [Unknown]
 Port WWN            [500000E0DA0A7D30]
 Node WWN            [500000E0DA0A7D40]
 Host Affinity       [Disable]
 Host Response       [0]
 SFP Type            [Unmount]
 SFP Information
                  Present    Warning(Low/High)      Alarm(Low/High)
  Temperature         [-]                [-/-]                [-/-]
  Voltage             [-]                [-/-]                [-/-]
  Current             [-]                [-/-]                [-/-]
  TX Power            [-]                [-/-]                [-/-]
  RX Power            [-]                [-/-]                [-/-]
CM#1 CA#0 Port#1 Information
 Port Type           [FC]
 Port Mode           [CA]
 Status/Status Code  [Unconnected / 0xC000] (Error Code : 0x0000)
 CA Active EC        [EC#0]
 CA Next EC          [EC#0]
 Connection          [Loop]
 Loop ID             [0x00]
 Transfer Rate       [Auto Negotiation]
 Link Status         [Unknown]
 Port WWN            [500000E0DA0A7D31]
 Node WWN            [500000E0DA0A7D40]
 Host Affinity       [Disable]
 Host Response       [0]
 SFP Type            [Unmount]
 SFP Information
                  Present    Warning(Low/High)      Alarm(Low/High)
  Temperature         [-]                [-/-]                [-/-]
  Voltage             [-]                [-/-]                [-/-]
  Current             [-]                [-/-]                [-/-]
  TX Power            [-]                [-/-]                [-/-]
  RX Power            [-]                [-/-]                [-/-]
CE PSU#0 Information
 Status/Status Code  [Normal      / 0xE001]
CE PSU#1 Information
 Status/Status Code  [Normal      / 0xE001]
login as: f.ce
Pre-authentication banner message from server:
| FUJITSU Storage ETERNUS login is required. [2021-11-30 06:50:01]
End of banner message from server
f.ce@192.168.1.1's password:
Access denied
f.ce@192.168.1.1's password:

Currently Network Configuration is set to factory default.
CLI>
"""
NODE_STATUS_DATAS = """
Controller Enclosure Information
 Location      Status       Error Code  Sensor 1 / Sensor 2
 Intake Temp   Normal       0x0000      24 (C)   / 23 (C)
 Exhaust Temp  Normal       0x0000      40 (C)   / 42 (C)

Controller Enclosure Status
 Controller Module Status/Status Code
  CM#0         [Normal      / 0xE001]
  CM#1         [Normal      / 0xE001]
 Power Supply Unit Status/Status Code
  PSU#0        [Normal      / 0xE001]
  PSU#1        [Normal      / 0xE001]
 Disk Status
  CE-Disk#0    [Available                    ]  CE-Disk#1    [Available ]
  CE-Disk#2    [Available                    ]  CE-Disk#3    [Available ]
  CE-Disk#4    [Present                      ]  CE-Disk#5    [Available ]
  CE-Disk#6    [Available                    ]  CE-Disk#7    [Available ]
  CE-Disk#8    [Available                    ]  CE-Disk#9    [Available ]
CLI>
"""
POOL_DATAS = """
[RAID Group No.],[RAID Group Name,R,M,Status,TotalCapacity(MB),FreeCapacity(MB)
0,pool-1,RAID1+0,CM#0,Available,1118208,1115926
1,pool-2,RAID5,CM#1,Available,1118208,1118208
CLI>
"""
POOL_OLD_DATAS = """RAID Group           RAID    Assigned Status\
                    Total        Free
No. Name             Level   CM                                 Capacity(MB)\
 Capacity(MB)
  0 JJ               RAID0   CM#0     Broken                         1676288\
        1358848
CLI> """
POOL_ERROR_DATAS = """                   ^
Error: Ambiguous command
CLI>"""
VOLUME_TPV_DATAS \
    = """Volume Status RG or TPP or FTRP TFOG Size(MB) Copy Allocation Used Me
No. Name No.  Name No. Name Protection Status (%) Level     Capacity(MB)
----- ------ ---- ---- ------- --- ------ --- ---- --- --- --- -- --- -----
1 volume-wsv Available 0 thin-1 - - 200 Disable  Thick  Normal - 80 High 200
4 voo-1 Available 0 thin-1 - - 500 Disable  Thin  Normal >500 80 High 0
CLI>
"""
VOLUME_FTV_DATAS \
    = """Error: E0331 Flexible tier mode is not valid.
             [0305-0505] -type ftv
CLI>
"""
VOLUME_DATAS = """Volume                Status                    Type\
      Expansion       RAID Group           Size(MB)   Reserved
No.  Name                                                 (Concatenation) No.\
 Name                        Deletion
   0 OVM_Repo0        Broken                    Open                    -   0\
    JJ                   51200
   1 OVM_Repo1        Broken                    Open                    -   0\
    JJ                   51200
   2 OVM_raw          Broken                    Open                    -   0\
    JJ                   10240
   3 OVM_Repo2        Broken                    Open                    -   0\
    JJ                  204800
CLI>"""

VOLUMES_ERROR = """                  ^
CLI>"""

VOLUMES = """[Volume No.],[Volume Name],[Status],[Type],[RG or TPP or\
 FTRP No.],[RG or TPP or FTRP Name],[Size(MB)],[Copy Protection]
0,volume_10,Available,Standard,0,pool-1,1024,Disable
1,volume-wsv,Available,TPV,0,thin-1,200,Disable
2,volume-4,Available,SDPV,1,pool-2,2048,Disable
3,volume_2,Available,SDV,0,pool-1,209715,Disable
4,voo-1,Available,TPV,0,thin-1,500,Disable
CLI>"""

STORAGE_RESULT = {
    'name': 'dx100-test',
    'vendor': 'FUJITSU',
    'description': 'test dx100-test',
    'model': 'ET103ACU',
    'status': 'normal',
    'serial_number': '4601620378',
    'firmware_version': 'V10L50-9003',
    'location': 'test location',
    'raw_capacity': 6657199308800.0,
    'total_capacity': 2345052143616,
    'used_capacity': 2392850432,
    'free_capacity': 2342659293184
}
CONTROLLER_RESULT = [
    {
        'name': 'CM#0',
        'storage_id': '12345',
        'native_controller_id': 'WK16201983',
        'status': 'normal',
        'location': 'CM#0',
        'soft_version': 'AA',
        'cpu_info': '1.40GHz',
        'memory_size': '4294967296'
    }]
POOL_RESULT = [
    {
        'name': 'pool-1',
        'storage_id': '12345',
        'native_storage_pool_id': '0',
        'status': 'normal',
        'storage_type': 'block',
        'total_capacity': 1172526071808,
        'used_capacity': 2392850432,
        'free_capacity': 1170133221376
    }]
POOL_old_RESULT = [
    {
        'name': 'JJ',
        'storage_id': '12345',
        'native_storage_pool_id': '0',
        'status': 'abnormal',
        'storage_type': 'block',
        'total_capacity': 1757715365888,
        'used_capacity': 332859965440,
        'free_capacity': 1424855400448
    }]
VOLUME_RESULT = [
    {
        'name': 'volume_10',
        'storage_id': '12345',
        'status': 'normal',
        'native_volume_id': '0',
        'native_storage_pool_id': '0',
        'type': 'thick',
        'total_capacity': 1073741824,
        'used_capacity': 0,
        'free_capacity': 1073741824
    }]
VOLUME_OLD_RESULT = [
    {
        'name': 'OVM_Repo0',
        'storage_id': '12345',
        'status': 'abnormal',
        'native_volume_id': '0',
        'native_storage_pool_id': '0',
        'type': 'thick',
        'total_capacity': 53687091200,
        'used_capacity': 0,
        'free_capacity': 0
    }]
LIST_ALERT_ERROR = """2021-08-19 02:33:08   Error         P 85400008   SS\
D 2.5 DE#00-Slot#8(SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA8YAA H603 15299\
A1>
2021-08-19 02:33:08   Error         P 85400007   SSD 2.5 DE#00-Slot#7(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWAHN1A H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400006   SSD 2.5 DE#00-Slot#6(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA9GSA H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400005   SSD 2.5 DE#00-Slot#5(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA91YA H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400004   SSD 2.5 DE#00-Slot#4(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA9HMA H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400003   SSD 2.5 DE#00-Slot#3(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA908A H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400002   SSD 2.5 DE#00-Slot#2(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWAHMAA H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400001   SSD 2.5 DE#00-Slot#1(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA9KJA H603 15299 A1>
2021-08-19 02:33:08   Error         P 85400000   SSD 2.5 DE#00-Slot#0(\
SAS 400GB) Fault (DE) <HUSMM1640ASS204 0QWA9GMA H603 15299 A1>
CLI>"""

LIST_ALERT_WARNING = """2021-08-19 02:33:08   Warning       P 85400008   SSD\
Fault (DE) <HUSMM1640ASS204 0QWA8YAA H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400007   SSD 2.5  Fault (DE) <\
HUSMM1640ASS204 0QWAHN1A H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400006   SSD 2.5 Fault (DE) <\
HUSMM1640ASS204 0QWA9GSA H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400005   SSD 2.5  Fault (DE) <\
HUSMM1640ASS204 0QWA91YA H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400004   SSD 2.5 Fault (DE) <\
HUSMM1640ASS204 0QWA9HMA H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400003   SSD 2.5  Fault (DE) <\
HUSMM1640ASS204 0QWA908A H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400002   SSD 2.5 DE#00-Fault (DE) <\
HUSMM1640ASS204 0QWAHMAA H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400001   SSD 2.5 DE#00-S Fault (DE) <\
HUSMM1640ASS204 0QWA9KJA H603 15299 A1>
2021-08-19 02:33:08   Warning       P 85400000   SSD 2.5 DE#00- Fault (DE) <\
HUSMM1640ASS204 0QWA9GMA H603 15299 A1>
CLI>"""

ALERTS_INFO = {
    'alert_id': '85400008',
    'severity': 'Warning',
    'category': 'Fault',
    'description': 'SSDFault (DE) <HUSMM1640ASS204 0QWA8YAA H603 15299 A1>',
    'type': 'EquipmentAlarm',
    'resource_type': 'Storage',
    'alert_name': 'SSDFault (DE) <HUSMM1640ASS204 0QWA8YAA H603 15299 A1>',
    'occur_time': 1629311588000,
    'match_key': '1809bdfa672e8b10ec9ec499a54dcd83'
}

DISK_LIST_INFO = """Controller Enclosure Disk #0 Information
 Location                   [CE-Disk#0]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [400GB]
 Type                       [2.5 SSD-M]
 Speed                      [-]
 Usage                      [Data]
 Health                     [100%]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [HGST]
 Product ID                 [HUSMM1640ASS204]
 Serial Number              [0QWA91YA]
 WWN                        [5000CCA04E4B14F3]
 Firmware Revision          [H603]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [4%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #1 Information
 Location                   [CE-Disk#1]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [400GB]
 Type                       [2.5 SSD-M]
 Speed                      [-]
 Usage                      [Data]
 Health                     [100%]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [HGST]
 Product ID                 [HUSMM1640ASS204]
 Serial Number              [0QWAHN1A]
 WWN                        [5000CCA04E4B77CF]
 Firmware Revision          [H603]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [4%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #2 Information
 Location                   [CE-Disk#2]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [400GB]
 Type                       [2.5 SSD-M]
 Speed                      [-]
 Usage                      [Data]
 Health                     [100%]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [HGST]
 Product ID                 [HUSMM1640ASS204]
 Serial Number              [0QWA9GMA]
 WWN                        [5000CCA04E4B1B17]
 Firmware Revision          [H603]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [4%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #3 Information
 Location                   [CE-Disk#3]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [400GB]
 Type                       [2.5 SSD-M]
 Speed                      [-]
 Usage                      [Data]
 Health                     [100%]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [HGST]
 Product ID                 [HUSMM1640ASS204]
 Serial Number              [0QWA9KJA]
 WWN                        [5000CCA04E4B1C7F]
 Firmware Revision          [H603]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [4%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #4 Information
 Location                   [CE-Disk#4]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [400GB]
 Type                       [2.5 SSD-M]
 Speed                      [-]
 Usage                      [Data]
 Health                     [100%]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [HGST]
 Product ID                 [HUSMM1640ASS204]
 Serial Number              [0QWAHMAA]
 WWN                        [5000CCA04E4B7777]
 Firmware Revision          [H603]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [4%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #5 Information
 Location                   [CE-Disk#5]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [S7M1LC92]
 WWN                        [5000C50098FA0A04]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #6 Information
 Location                   [CE-Disk#6]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [W7M0M8PR]
 WWN                        [5000C500A0FA7844]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #7 Information
 Location                   [CE-Disk#7]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [S7M1LC99]
 WWN                        [5000C50098FA09DC]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #8 Information
 Location                   [CE-Disk#8]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [S7M1L3XD]
 WWN                        [5000C50098EE374C]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #9 Information
 Location                   [CE-Disk#9]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [ 0 : pool-1]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [S7M1KXS5]
 WWN                        [5000C50098F06184]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #10 Information
 Location                   [CE-Disk#10]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [S7M1KCPD]
 WWN                        [5000C50098DB1E50]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]

Controller Enclosure Disk #11 Information
 Location                   [CE-Disk#11]
 Status                     [Present] (Error Code : 0x0000)
 Size                       [600GB]
 Type                       [2.5 Online]
 Speed                      [15000rpm]
 Usage                      [Data]
 Health                     [-]
 RAID Group                 [-]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST600MP0005]
 Serial Number              [W7M0MYYA]
 WWN                        [5000C500A0F7C4D0]
 Firmware Revision          [VE0C]
 <Disk Patrol Information>
   Total completed passes               [0Cycles]
   Progress with current pass           [3%]
   Completed passes since last Power On [0Cycles]
CLI>"""

PORT_LIST_INFO = """
Port                          CM#0 CA#0 Port#0       CM#0 CA#0 Port#1
Port Mode                     CA                     CA
Connection                    FC-AL                  FC-AL
Loop ID Assign                Manual(0x00)           Manual(0x00)
Transfer Rate                 8 Gbit/s               Auto Negotiation
Frame Size                    2048 bytes             2048 bytes
Host Affinity                 Disable                Disable
Host Response No.             0                      0
Host Response Name            Default                Default
Reset Scope                   I_T_L                  I_T_L
Reserve Cancel at Chip Reset  Disable                Disable
REC Line No.                  -                      -
REC Transfer Mode Sync        -                      -
REC Transfer Mode Stack       -                      -
REC Transfer Mode Consistency -                      -
REC Transfer Mode Through     -                      -
TFO Transfer Mode             -                      -
WWN Mode                      Custom                 Custom
WWPN                          500000E0DA0A7D20       500000E0DA0A7D21

Port                          CM#1 CA#0 Port#0       CM#1 CA#0 Port#1
Port Mode                     CA                     CA
Connection                    FC-AL                  FC-AL
Loop ID Assign                Manual(0x00)           Manual(0x00)
Transfer Rate                 Auto Negotiation       Auto Negotiation
Frame Size                    2048 bytes             2048 bytes
Host Affinity                 Disable                Disable
Host Response No.             0                      0
Host Response Name            Default                Default
Reset Scope                   I_T_L                  I_T_L
Reserve Cancel at Chip Reset  Disable                Disable
REC Line No.                  -                      -
REC Transfer Mode Sync        -                      -
REC Transfer Mode Stack       -                      -
REC Transfer Mode Consistency -                      -
REC Transfer Mode Through     -                      -
TFO Transfer Mode             -                      -
WWN Mode                      Custom                 Custom
WWPN                          500000E0DA0A7D30       500000E0DA0A7D31
CLI>"""

FCOE_INFO = """Port                          CM#0 CA#0 Port#0           CM#0\
 CA#0 Port#1
Port Mode                     CA                         RA
Transfer Rate                 10Gbit/s                   10Gbit/s
Frame Size                    2048bytes                  2048bytes
Host Affinity                 Enable                     Enable
Host Response No.             1                          2
Host Response Name            HP01                       HP02
Reset Scope                   I_T_L                      I_T_L
Reserve Cancel at Chip Reset  Disable                    -
FCF VLAN ID                   Disable                    Disable
FCF Fabric Name               Disable                    Disable
MAC Address                   01:02:03:04:05:06          01:02:03:04:05:07

Port                          CM#0 CA#1 Port#0           CM#0 CA#1 Port#1
Port Mode                     CA                         RA
Transfer Rate                 10Gbit/s                   10Gbit/s
Frame Size                    2048bytes                  2048bytes
Host Affinity                 Enable                     Enable
Host Response No.             1                          2
Host Response Name            HP01                       HP02
Reset Scope                   I_T_L                      I_T_L
Reserve Cancel at Chip Reset  Disable                    -
FCF VLAN ID                   Disable                    Disable
FCF Fabric Name               Disable                    Disable
MAC Address                   01:02:03:06:05:06          01:02:03:06:05:07
CLI>"""


def create_driver():
    EternusSSHPool.do_exec_shell = mock.Mock(
        side_effect=["Summary Status  [Normal]"])
    return EternusDriver(**ACCESS_INFO)


class TestEternusDriver(TestCase):
    driver = create_driver()

    def test_get_storage(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[STORAGE_NAME_DATA,
                         STORAGE_MODEL_DATA,
                         STORAGE_STATUS_DATA,
                         DISK_LIST_INFO,
                         POOL_DATAS])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, STORAGE_RESULT)

    def test_list_storage_pools(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(side_effect=[POOL_DATAS])
        pools = self.driver.list_storage_pools(context)
        self.assertDictEqual(pools[0], POOL_RESULT[0])

    def test_list_storage_pools_old(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(side_effect=[
            POOL_ERROR_DATAS, POOL_OLD_DATAS])
        pools = self.driver.list_storage_pools(context)
        self.assertDictEqual(pools[0], POOL_old_RESULT[0])

    def test_list_volumes(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VOLUMES, VOLUME_TPV_DATAS, VOLUME_FTV_DATAS])
        volumes = self.driver.list_volumes(context)
        self.assertDictEqual(volumes[0], VOLUME_RESULT[0])

    def test_list_volumes_old(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VOLUMES_ERROR, VOLUME_DATAS])
        volumes = self.driver.list_volumes(context)
        self.assertDictEqual(volumes[0], VOLUME_OLD_RESULT[0])

    def test_get_controllers(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[NODE_DATAS, NODE_STATUS_DATAS])
        controllers = self.driver.list_controllers(context)
        self.assertDictEqual(controllers[0], CONTROLLER_RESULT[0])

    def test_list_alerts(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[LIST_ALERT_WARNING,
                         LIST_ALERT_ERROR])
        list_alerts = self.driver.list_alerts(context)
        ALERTS_INFO['occur_time'] = list_alerts[0].get('occur_time')
        ALERTS_INFO['match_key'] = list_alerts[0].get('match_key')
        self.assertDictEqual(list_alerts[0], ALERTS_INFO)

    def test_list_alerts_old(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[None, None, LIST_ALERT_WARNING,
                         LIST_ALERT_ERROR])
        list_alerts = self.driver.list_alerts(context)
        ALERTS_INFO['occur_time'] = list_alerts[0].get('occur_time')
        ALERTS_INFO['match_key'] = list_alerts[0].get('match_key')
        self.assertDictEqual(list_alerts[0], ALERTS_INFO)

    def test_list_disks(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(side_effect=[DISK_LIST_INFO])
        data = self.driver.list_disks(context)
        self.assertEqual(
            data[0].get('name'), 'CE-Disk#0')

    def test_list_ports(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(side_effect=['', FCOE_INFO])
        data = self.driver.list_ports(context)
        self.assertEqual(
            data[0].get('name'), 'CM#0 CA#0 Port#0')
