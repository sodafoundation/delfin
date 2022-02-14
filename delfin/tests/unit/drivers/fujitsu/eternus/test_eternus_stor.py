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
NODE_DATAS_OLD = """your ip address
you username is huawei
CLI> show fru-ce
CM#0 Information
 Status/Status Code  [Normal      / 0xE001]
 Memory Size         [1.0GB]
 Type                [FC Model]
 Parts Number        [CA07415-C621]
 Serial Number       [WK13510516]
 Hardware Revision   [AA   ]
 CPU Clock           [1.20GHz]
 Active EC           [EC#1]
 Next EC             [EC#1]
CM#0 Internal Parts Status/Status Code
 Memory              [Normal      / 0xE001]
 BE Expander         [Normal      / 0xE001]
 BE EXP Port#0       [Normal      / 0xE001]
 BE EXP Port#1       [Undefined   / 0x0000]
 BE EXP Port#2       [Normal      / 0xE001]
 DI Port#0           [Normal      / 0xE001]
 DI Port#1           [Normal      / 0xE001]
 FC Port#0           [Normal      / 0xE001]
 FC Port#1           [Normal      / 0xE001]
 SAS Cable#1(OUT)    [-           / -     ]
 NAND Controller     [Normal      / 0xE001]
 Flash ROM           [Normal      / 0xE001]
CM#0 SCU Information
 Status/Status Code  [Normal      / 0xE001]
 Voltage             [9.50V]
 Expires             [0-00]
CM#0 Port#0 Information
 Port Mode           [CA]
 Status/Status Code  [Normal      / 0xE001]
 Connection          [Fabric]
 Loop ID             [-]
 Transfer Rate       [Auto Negotiation]
 Link Status         [4Gbit/s Link Up]
 WWN                 [500000E0D0376706]
 Host Affinity       [Enable]
 Host Response       [-]
CM#0 Port#1 Information
 Port Mode           [CA]
 Status/Status Code  [Normal      / 0xE001]
 Connection          [Loop]
 Loop ID             [-]
 Transfer Rate       [Auto Negotiation]
 Link Status         [Link Down]
 WWN                 [500000E0D0376707]
 Host Affinity       [Enable]
 Host Response       [-]
CM#1 Information
 Status/Status Code  [Normal      / 0xE001]
 Memory Size         [1.0GB]
 Type                [FC Model]
 Parts Number        [CA07415-C621]
 Serial Number       [WK13510538]
 Hardware Revision   [AA   ]
 CPU Clock           [1.20GHz]
 Active EC           [EC#1]
 Next EC             [EC#1]
CM#1 Internal Parts Status/Status Code
 Memory              [Normal      / 0xE001]
 BE Expander         [Normal      / 0xE001]
 BE EXP Port#0       [Normal      / 0xE001]
 BE EXP Port#1       [Undefined   / 0x0000]
 BE EXP Port#2       [Normal      / 0xE001]
 DI Port#0           [Normal      / 0xE001]
 DI Port#1           [Normal      / 0xE001]
 FC Port#0           [Normal      / 0xE001]
 FC Port#1           [Normal      / 0xE001]
 SAS Cable#1(OUT)    [-           / -     ]
 NAND Controller     [Normal      / 0xE001]
 Flash ROM           [Normal      / 0xE001]
CM#1 SCU Information
 Status/Status Code  [Normal      / 0xE001]
 Voltage             [9.50V]
 Expires             [0-00]
CM#1 Port#0 Information
 Port Mode           [CA]
 Status/Status Code  [Normal      / 0xE001]
 Connection          [Loop]
 Loop ID             [-]
 Transfer Rate       [Auto Negotiation]
 Link Status         [Link Down]
 WWN                 [500000E0D0376786]
 Host Affinity       [Enable]
 Host Response       [-]
CM#1 Port#1 Information
 Port Mode           [CA]
 Status/Status Code  [Normal      / 0xE001]
 Connection          [Fabric]
 Loop ID             [-]
 Transfer Rate       [Auto Negotiation]
 Link Status         [4Gbit/s Link Up]
 WWN                 [500000E0D0376787]
 Host Affinity       [Enable]
 Host Response       [-]
CE PSU#0 Information
 Status/Status Code  [Normal      / 0xE001]
CE PSU#1 Information
 Status/Status Code  [Normal      / 0xE001]
CLI>"""
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
POOL_OLD_DATAS = """your ip address
you username is huawei
CLI> show raid-groups
RAID Group           RAID    Assigned Status\
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
VOLUME_DATAS = """your ip address
you username is huawei
CLI> show raid-groups
Volume                Status                    Type\
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

VOLUMES = """CLI> show volumes -mode uid
Volume                                 Status                    Type\
              RG or TPP or FTRP     TFOG                 Size(MB)  UID
No.   Name                                                             \
            No.  Name             No. Name                       ID\
                                           Mode
----- -------------------------------- ------------------------- ----------\
------- ---- ---------------- --- ---------------- --------- ---------------\
----------------- -------
    0 LUN00                            Available                 TPV          \
            0 Pool0              - -                    20480\
             600000E00D29000000291B6B00000000 Default
    1 LUN01                            Available                 TPV          \
            0 Pool0              - -                    20480\
            600000E00D29000000291B6B00010000 Default
    2 LUN02                            Available                 TPV\
                      0 Pool0              - -                    20480\
                       600000E00D29000000291B6B00020000 Default
    3 LUN03                            Available                 TPV\
                      0 Pool0              - -                    20480\
                       600000E00D29000000291B6B00030000 Default
    4 LUN04                            Available                 TPV\
                      0 Pool0              - -                    20480\
                       600000E00D29000000291B6B00040000 Default
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
        'name': 'LUN00',
        'storage_id': '12345',
        'status': 'normal',
        'native_volume_id': '0',
        'native_storage_pool_id': '0',
        'type': 'thick',
        'wwn': '600000E00D29000000291B6B00000000',
        'total_capacity': 21474836480,
        'used_capacity': 0,
        'free_capacity': 21474836480
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
LIST_ALERT_ERROR = """your ip address
you username is huawei
CLI> show raid-groups
2021-08-19 02:33:08   Error         P 85400008   SS\
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

LIST_ALERT_WARNING = """your ip address
you username is huawei
CLI> show raid-groups
2021-08-19 02:33:08   Warning       P 85400008   SSD\
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
DISK_OLD = """your ip address
you username is huawei
CLI> show disks -disks all
Controller Enclosure Disk #0 Information
 Location                   [CE-Disk#0]
 Status                     [Failed Usable] (Error Code : 0x0001)
 Size                       [450GB]
 Type                       [3.5" SAS]
 Speed                      [15000rpm]
 Usage                      [System]
 RAID Group                 [ 0 : JJ]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST3450857SS]
 Serial Number              [6SK2CEG91327]
 WWN                        [5000C5006BC80184]
 Firmware Revision          [GF0D]
\r
Controller Enclosure Disk #1 Information
 Location                   [CE-Disk#1]
 Status                     [Failed Usable] (Error Code : 0x0009)
 Size                       [450GB]
 Type                       [3.5" SAS]
 Speed                      [15000rpm]
 Usage                      [System]
 RAID Group                 [ 0 : JJ]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST3450857SS]
 Serial Number              [6SK262SZ1312]
 WWN                        [5000C5006806E318]
 Firmware Revision          [GF0D]
\r
Controller Enclosure Disk #2 Information
 Location                   [CE-Disk#2]
 Status                     [Available]
 Size                       [450GB]
 Type                       [3.5" SAS]
 Speed                      [15000rpm]
 Usage                      [Data]
 RAID Group                 [ 0 : JJ]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST3450857SS]
 Serial Number              [6SK26QCA1312]
 WWN                        [5000C5006810B6AC]
 Firmware Revision          [GF0D]
\r
Controller Enclosure Disk #3 Information
 Location                   [CE-Disk#3]
 Status                     [Available]
 Size                       [450GB]
 Type                       [3.5" SAS]
 Speed                      [15000rpm]
 Usage                      [Data]
 RAID Group                 [ 0 : JJ]
 Motor Status               [Active]
 Rebuild/Copyback Progress  [-]
 Vendor ID                  [SEAGATE]
 Product ID                 [ST3450857SS]
 Serial Number              [6SK2DE941330]
 WWN                        [5000C5006C3E26FC]
 Firmware Revision          [GF0D]
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
FC_INFO_OLD = """your ip address
you username is huawei
CLI> show fc-parameters
Port                          CM#0 Port#0      CM#0 Port#1\
      CM#1 Port#0      CM#1 Port#1
Port Mode                     CA               CA               CA\
               CA
Connection                    Fabric           FC-AL            FC-AL\
            Fabric
Loop ID Assign                -                Auto(Ascending)\
  Auto(Ascending)  -
Transfer Rate                 Auto Negotiation Auto Negotiation\
 Auto Negotiation Auto Negotiation
Frame Size                    2048 bytes       2048 bytes\
       2048 bytes       2048 bytes
Host Affinity                 Enable           Enable           Enable\
           Enable
Host Response No.             -                -                -\
                -
Host Response Name            -                -                -\
                -
Reset Scope                   I_T_L            I_T_L            I_T_L\
            I_T_L
Reserve Cancel at Chip Reset  Enable           Enable           Enable\
           Enable\
CLI>"""
HOST_STATUS_INFO = """CLI> show host-path-state
 Port                  Host                  Path State
                       No.  Name
 --------------------- ---- ---------------- ----------
 CM#0 CA#0 Port#0         0 dbs01_0          Online
 CM#0 CA#0 Port#0         1 dbs01_1          Online
 CM#0 CA#0 Port#1         1 dbs01_1          Online
 CM#0 CA#0 Port#1         2 dbs02_0          Online
 CM#1 CA#0 Port#0         0 dbs01_0          Online
 CM#1 CA#0 Port#0         1 dbs01_1          Online
 CM#1 CA#0 Port#0         3 dbs02_1          Online
 CM#1 CA#0 Port#1         7 h_g_1_0          Online
CLI>"""
FC_HOSTS_INFO = """CLI> show host-wwn-names
Host                  WWN              Host Response
No.  Name                              No. Name
---- ---------------- ---------------- --- ----------------
   0 dbs01_0          10000090faec8449   0 Default
   1 dbs01_1          10000090faec84a7   0 Default
   2 dbs02_0          10000090faec852a   0 Default
   3 dbs02_1          10000090faec842d   0 Default
   4 dbs03_0          10000090faec7f2f   0 Default
   5 dbs03_1          10000090faec7f06   0 Default
   7 h_g_1_0          12ac13ab15af21ae 252 AIX
CLI>"""
ISCSI_HOST_INFO = """CLI> show host-iscsi-names
Host                  Host Response        IP Address\
                              iSCSI Name                       CmdSN Count
No.  Name             No. Name
---- ---------------- --- ---------------- ---------------------------------\
------ -------------------------------- -----------
   0 iscsi_host_0     252 AIX              126.0.0.2\
                                  iqn.2006-08.com.huawei:21004447d Unlimited
                                                                cca426::0
   1 iscsi_host-1_0   252 AIX              126.0.0.3\
                                  iqn.2006-08.com.huawei:21004447d Unlimited
                                                                cca426::1
   2 iscsi_1_0          0 Default          *(IPv6)\
                                    iqn.2007-08.com.huawei:21004447d Unlimited
                                                                cca426::7\
CLI>"""
ISCSI_HOST_DETAIL_ZERO = """CLI> show host-iscsi-names -host-number 0
Host No.             0
Host Name            iscsi_host_0
iSCSI Name           iqn.2006-08.com.huawei:21004447dcca426::0
Alias Name           iscsi 230   25
IP Address           126.0.0.2
Chap User Name
Host Response No.    252
Host Response Name   AIX
CmdSN Count          Unlimited

CLI>"""
ISCSI_HOST_DETAIL_ONE = """CLI> show host-iscsi-names -host-number 1
Host No.             1
Host Name            iscsi_host-1_0
iSCSI Name           iqn.2006-08.com.huawei:21004447dcca426::1
Alias Name           iscsi1
IP Address           126.0.0.3
Chap User Name
Host Response No.    252
Host Response Name   AIX
CmdSN Count          Unlimited

CLI>"""
ISCSI_HOST_DETAIL_TWO = """CLI> show host-iscsi-names -host-number 2
Host No.             2
Host Name            iscsi_1_0
iSCSI Name           iqn.2007-08.com.huawei:21004447dcca426::7
Alias Name
IP Address           *(IPv6)
Chap User Name
Host Response No.    0
Host Response Name   Default
CmdSN Count          Unlimited

CLI>"""
SAS_HOST_INFO = """CLI> show host-sas-addresses
Host                  SAS Address      Host Response
No.  Name                              No. Name
---- ---------------- ---------------- --- ----------------
   6 sas_g_0_0        12ab13ac14ad15af 253 AIX VxVM
   8 sas2_0           14ab13ac46ae20af   0 Default
CLI>"""
INITIATORS_DATA = [
    {'name': '10000090faec8449', 'storage_id': '12345',
     'native_storage_host_initiator_id': '10000090faec8449',
     'wwn': '10000090faec8449', 'status': 'online',
     'native_storage_host_id': 'dbs01_0', 'type': 'fc'},
    {'name': '10000090faec84a7', 'storage_id': '12345',
     'native_storage_host_initiator_id': '10000090faec84a7',
     'wwn': '10000090faec84a7', 'status': 'online',
     'native_storage_host_id': 'dbs01_1', 'type': 'fc'},
    {'name': '10000090faec852a', 'storage_id': '12345',
     'native_storage_host_initiator_id': '10000090faec852a',
     'wwn': '10000090faec852a', 'status': 'online',
     'native_storage_host_id': 'dbs02_0', 'type': 'fc'},
    {'name': '10000090faec842d', 'storage_id': '12345',
     'native_storage_host_initiator_id': '10000090faec842d',
     'wwn': '10000090faec842d', 'status': 'online',
     'native_storage_host_id': 'dbs02_1', 'type': 'fc'},
    {'name': '10000090faec7f2f', 'storage_id': '12345',
     'native_storage_host_initiator_id': '10000090faec7f2f',
     'wwn': '10000090faec7f2f', 'status': 'offline',
     'native_storage_host_id': 'dbs03_0', 'type': 'fc'},
    {'name': '10000090faec7f06', 'storage_id': '12345',
     'native_storage_host_initiator_id': '10000090faec7f06',
     'wwn': '10000090faec7f06', 'status': 'offline',
     'native_storage_host_id': 'dbs03_1', 'type': 'fc'},
    {'name': '12ac13ab15af21ae', 'storage_id': '12345',
     'native_storage_host_initiator_id': '12ac13ab15af21ae',
     'wwn': '12ac13ab15af21ae', 'status': 'online',
     'native_storage_host_id': 'h_g_1_0', 'type': 'fc'},
    {'name': 'iqn.2006-08.com.huawei:21004447dcca426::0',
     'storage_id': '12345',
     'native_storage_host_initiator_id':
         'iqn.2006-08.com.huawei:21004447dcca426::0',
     'wwn': 'iqn.2006-08.com.huawei:21004447dcca426::0', 'status': 'offline',
     'native_storage_host_id': 'iscsi_host_0', 'type': 'iscsi',
     'alias': 'iscsi 230   25'},
    {'name': 'iqn.2006-08.com.huawei:21004447dcca426::1',
     'storage_id': '12345',
     'native_storage_host_initiator_id':
         'iqn.2006-08.com.huawei:21004447dcca426::1',
     'wwn': 'iqn.2006-08.com.huawei:21004447dcca426::1', 'status': 'offline',
     'native_storage_host_id': 'iscsi_host-1_0', 'type': 'iscsi',
     'alias': 'iscsi1'},
    {'name': 'iqn.2007-08.com.huawei:21004447dcca426::7',
     'storage_id': '12345',
     'native_storage_host_initiator_id':
         'iqn.2007-08.com.huawei:21004447dcca426::7',
     'wwn': 'iqn.2007-08.com.huawei:21004447dcca426::7',
     'status': 'offline',
     'native_storage_host_id': 'iscsi_1_0',
     'type': 'iscsi', 'alias': None},
    {'name': '12ab13ac14ad15af', 'storage_id': '12345',
     'native_storage_host_initiator_id': '12ab13ac14ad15af',
     'wwn': '12ab13ac14ad15af', 'status': 'offline',
     'native_storage_host_id': 'sas_g_0_0', 'type': 'sas'},
    {'name': '14ab13ac46ae20af', 'storage_id': '12345',
     'native_storage_host_initiator_id': '14ab13ac46ae20af',
     'wwn': '14ab13ac46ae20af', 'status': 'offline',
     'native_storage_host_id': 'sas2_0', 'type': 'sas'}]
HOSTS_DATA = [
    {'name': 'dbs01_0', 'storage_id': '12345',
     'native_storage_host_id': 'dbs01_0', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'dbs01_1', 'storage_id': '12345',
                           'native_storage_host_id': 'dbs01_1',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'dbs02_0', 'storage_id': '12345',
     'native_storage_host_id': 'dbs02_0', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'dbs02_1', 'storage_id': '12345',
                           'native_storage_host_id': 'dbs02_1',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'dbs03_0', 'storage_id': '12345',
     'native_storage_host_id': 'dbs03_0', 'os_type': 'Unknown',
     'status': 'offline'}, {'name': 'dbs03_1', 'storage_id': '12345',
                            'native_storage_host_id': 'dbs03_1',
                            'os_type': 'Unknown', 'status': 'offline'},
    {'name': 'h_g_1_0', 'storage_id': '12345',
     'native_storage_host_id': 'h_g_1_0', 'os_type': 'AIX',
     'status': 'normal'}, {'name': 'iscsi_host_0', 'storage_id': '12345',
                           'native_storage_host_id': 'iscsi_host_0',
                           'os_type': 'AIX', 'status': 'offline',
                           'ip_address': '126.0.0.2'},
    {'name': 'iscsi_host-1_0', 'storage_id': '12345',
     'native_storage_host_id': 'iscsi_host-1_0', 'os_type': 'AIX',
     'status': 'offline', 'ip_address': '126.0.0.3'},
    {'name': 'iscsi_1_0', 'storage_id': '12345',
     'native_storage_host_id': 'iscsi_1_0', 'os_type': 'Unknown',
     'status': 'offline', 'ip_address': None},
    {'name': 'sas_g_0_0', 'storage_id': '12345',
     'native_storage_host_id': 'sas_g_0_0', 'os_type': 'Unknown',
     'status': 'offline'}, {'name': 'sas2_0', 'storage_id': '12345',
                            'native_storage_host_id': 'sas2_0',
                            'os_type': 'Unknown', 'status': 'offline'}]
HOST_GROUPS_INFO = """CLI> show host-groups -all
Host Group            Host Response        Host Type
No.  Name             No. Name
---- ---------------- --- ---------------- ----------
   0 dbs01              0 Default          FC/FCoE
<Host List>
  Host                  WWN
  No.  Name
  ---- ---------------- ----------------------------------------
     0 dbs01_0          10000090faec8449
     1 dbs01_1          10000090faec84a7

Host Group            Host Response        Host Type
No.  Name             No. Name
---- ---------------- --- ---------------- ----------
   1 dbs02              0 Default          FC/FCoE
<Host List>
  Host                  WWN
  No.  Name
  ---- ---------------- ----------------------------------------
     2 dbs02_0          10000090faec852a
     3 dbs02_1          10000090faec842d

Host Group            Host Response        Host Type
No.  Name             No. Name
---- ---------------- --- ---------------- ----------
   2 dbs03              0 Default          FC/FCoE
<Host List>
  Host                  WWN
  No.  Name
  ---- ---------------- ----------------------------------------
     4 dbs03_0          10000090faec7f2f
     5 dbs03_1          10000090faec7f06
CLI>"""
HOST_GROUPS_DATA = {
    'storage_host_groups': [{'name': 'dbs01', 'storage_id': '12345',
                             'native_storage_host_group_id': '0'},
                            {'name': 'dbs02', 'storage_id': '12345',
                             'native_storage_host_group_id': '1'},
                            {'name': 'dbs03', 'storage_id': '12345',
                             'native_storage_host_group_id': '2'}],
    'storage_host_grp_host_rels': [
        {'storage_id': '12345', 'native_storage_host_group_id': '0',
         'native_storage_host_id': 'dbs01_0'},
        {'storage_id': '12345', 'native_storage_host_group_id': '0',
         'native_storage_host_id': 'dbs01_1'},
        {'storage_id': '12345', 'native_storage_host_group_id': '1',
         'native_storage_host_id': 'dbs02_0'},
        {'storage_id': '12345', 'native_storage_host_group_id': '1',
         'native_storage_host_id': 'dbs02_1'},
        {'storage_id': '12345', 'native_storage_host_group_id': '2',
         'native_storage_host_id': 'dbs03_0'},
        {'storage_id': '12345', 'native_storage_host_group_id': '2',
         'native_storage_host_id': 'dbs03_1'}]}
VOLUME_GROUPS_INFO = """CLI> show lun-groups
LUN Group             LUN Overlap
No.  Name             Volumes
---- ---------------- -----------
   0 dbs01         20 No
CLI>
"""
VOLUME_DETAILS_INFO = """CLI> show lun-groups -lg-number 0
LUN Group No.0
LUN Group Name   dbs01
LUN  Volume                                 Status                    Size(MB)\
  LUN Overlap UID
     No.   Name\
                                                                      Volume
---- ----- -------------------------------- -------------------------\
 --------- ----------- --------------------------------
   0     0 LUN00                            Available\
                        20480 No          600000E00D29000000291B6B00000000
   1     1 LUN01                            Available\
                        20480 No          600000E00D29000000291B6B00010000
   2     2 LUN02                            Available\
                        20480 No          600000E00D29000000291B6B00020000
CLI>
"""
VOLUME_GROUPS_DATA = {
    'volume_groups': [{'name': 'dbs01         20', 'storage_id': '12345',
                       'native_volume_group_id': '0'}],
    'vol_grp_vol_rels': [
        {'storage_id': '12345', 'native_volume_group_id': '0',
         'native_volume_id': '0'},
        {'storage_id': '12345', 'native_volume_group_id': '0',
         'native_volume_id': '1'},
        {'storage_id': '12345', 'native_volume_group_id': '0',
         'native_volume_id': '2'}]}
PORT_G_VIEW_INFO = """CLI> show port-groups -all
Port Group           CA Type
No. Name
--- ---------------- -------
  0 PortGroup01      FC
<Port List>
  CM#0 CA#0 Port#0
  CM#1 CA#0 Port#0

Port Group           CA Type
No. Name
--- ---------------- -------
  1 PortGroup02      FC
<Port List>
  CM#0 CA#0 Port#1
  CM#1 CA#0 Port#1

Port Group           CA Type
No. Name
--- ---------------- -------
  2 PortGroup03      FC
<Port List>
  CM#0 CA#1 Port#0
  CM#1 CA#1 Port#0
CLI>"""
PORT_G_DATA = {
    'port_groups': [{'name': 'PortGroup01', 'storage_id': '12345',
                     'native_port_group_id': '0'},
                    {'name': 'PortGroup02', 'storage_id': '12345',
                     'native_port_group_id': '1'},
                    {'name': 'PortGroup03', 'storage_id': '12345',
                     'native_port_group_id': '2'}],
    'port_grp_port_rels': [
        {'storage_id': '12345', 'native_port_group_id': '0',
         'native_port_id': 'CM#0 CA#0 Port#0'},
        {'storage_id': '12345', 'native_port_group_id': '0',
         'native_port_id': 'CM#1 CA#0 Port#0'},
        {'storage_id': '12345', 'native_port_group_id': '1',
         'native_port_id': 'CM#0 CA#0 Port#1'},
        {'storage_id': '12345', 'native_port_group_id': '1',
         'native_port_id': 'CM#1 CA#0 Port#1'},
        {'storage_id': '12345', 'native_port_group_id': '2',
         'native_port_id': 'CM#0 CA#1 Port#0'},
        {'storage_id': '12345', 'native_port_group_id': '2',
         'native_port_id': 'CM#1 CA#1 Port#0'}]}
MASKING_VIEWS_INFO = """CLI> show host-affinity
Port Group           Host Group           LUN Group             LUN Overlap
No. Name             No. Name             No.  Name             Volumes
--- ---------------- --- ---------------- ---- ---------------- -----------
  0 huawie             3 Dorado5000V6        7 test             No
<Connection List>
  Port             Host
                   No.  Name
  ---------------- ---- ----------------
  CM#0 CA#0 Port#1    6 Dorado5000V6_0
  CM#0 CA#0 Port#1    7 Dorado5000V6_1
  CM#1 CA#0 Port#0    6 Dorado5000V6_0
  CM#1 CA#0 Port#0    7 Dorado5000V6_1

Port Group           Host Group           LUN Group             LUN Overlap
No. Name             No. Name             No.  Name             Volumes
--- ---------------- --- ---------------- ---- ---------------- -----------
  0 huawie            10 Dorado5500_V6       9 lun_fujitsu      No
<Connection List>
  Port             Host
                   No.  Name
  ---------------- ---- ----------------
  CM#0 CA#0 Port#1    4 Dorado5500v6_0
  CM#0 CA#0 Port#1    5 Dorado5500v6_1
  CM#1 CA#0 Port#0    4 Dorado5500v6_0
  CM#1 CA#0 Port#0    5 Dorado5500v6_1

Port Group           Host Group           LUN Group             LUN Overlap
No. Name             No. Name             No.  Name             Volumes
--- ---------------- --- ---------------- ---- ---------------- -----------
  0 huawie            12 AIX206              8 new1             No
<Connection List>
  Port             Host
                   No.  Name
  ---------------- ---- ----------------
  CM#0 CA#0 Port#1   20 AIX206_0
  CM#0 CA#0 Port#1   21 AIX206_1
  CM#1 CA#0 Port#0   20 AIX206_0
  CM#1 CA#0 Port#0   21 AIX206_1

CM#0 CA#0 Port#0 (Host Affinity Mode Enable)
Host                  LUN Group             LUN Overlap LUN Mask
No.  Name             No.  Name             Volumes     Group No.
---- ---------------- ---- ---------------- ----------- ---------
   1 RH_196_02           1 RH2288_test      No                  -
  20 AIX206_0            9 lun_fujitsu      No                  -

CM#0 CA#0 Port#1 (Host Affinity Mode Enable)

CM#1 CA#0 Port#0 (Host Affinity Mode Enable)
Host                  LUN Group             LUN Overlap LUN Mask
No.  Name             No.  Name             Volumes     Group No.
---- ---------------- ---- ---------------- ----------- ---------
   2 RH197_0             5 RH196            Yes                 -

CM#1 CA#0 Port#1 (Host Affinity Mode Disable)
CLI>"""
GET_MAPPING = """CLI> show mapping
CM#0 CA#0 Port#0 (Host Affinity Mode Enable)

CM#0 CA#0 Port#1 (Host Affinity Mode Enable)

CM#0 CA#1 Port#0 (Host Affinity Mode Enable)

CM#0 CA#1 Port#1 (Host Affinity Mode Disable)
LUN  Volume                                 Status                    Size(MB)
     No.   Name
---- ----- -------------------------------- ------------------------- ---------
   0     3 LUN03                            Available                     20480
   1     6 lun051                           Available                      2048

CM#1 CA#0 Port#0 (Host Affinity Mode Enable)

CM#1 CA#0 Port#1 (Host Affinity Mode Enable)

CM#1 CA#1 Port#0 (Host Affinity Mode Enable)

CM#1 CA#1 Port#1 (Host Affinity Mode Disable)
LUN  Volume                                 Status                    Size(MB)
     No.   Name
---- ----- -------------------------------- ------------------------- ---------
   1     5 lun050                           Available                      2048
CLI>"""
MASKING_VIEWS_DATA = [
    {'native_masking_view_id': '37host_idvolume_id',
     'name': '37host_idvolume_id', 'native_storage_host_group_id': '3',
     'native_port_group_id': '0', 'native_volume_group_id': '7',
     'storage_id': '12345'}, {'native_masking_view_id': '109host_idvolume_id',
                              'name': '109host_idvolume_id',
                              'native_storage_host_group_id': '10',
                              'native_port_group_id': '0',
                              'native_volume_group_id': '9',
                              'storage_id': '12345'},
    {'native_masking_view_id': '128host_idvolume_id',
     'name': '128host_idvolume_id', 'native_storage_host_group_id': '12',
     'native_port_group_id': '0', 'native_volume_group_id': '8',
     'storage_id': '12345'},
    {'native_masking_view_id': 'host_group_id1RH_196_02volume_id',
     'name': 'host_group_id1RH_196_02volume_id',
     'native_storage_host_id': 'RH_196_02', 'native_volume_group_id': '1',
     'native_port_id': 'CM#0 CA#0 Port#0', 'storage_id': '12345'},
    {'native_masking_view_id': 'host_group_id9AIX206_0volume_id',
     'name': 'host_group_id9AIX206_0volume_id',
     'native_storage_host_id': 'AIX206_0', 'native_volume_group_id': '9',
     'native_port_id': 'CM#0 CA#0 Port#0', 'storage_id': '12345'},
    {'native_masking_view_id': 'host_group_id5RH197_0volume_id',
     'name': 'host_group_id5RH197_0volume_id',
     'native_storage_host_id': 'RH197_0', 'native_volume_group_id': '5',
     'native_port_id': 'CM#1 CA#0 Port#0', 'storage_id': '12345'}]
PARSE_ALERT_DATA = {
    'alert_id': '123456', 'severity': 'Fatal',
    'category': 'Fault', 'occur_time': 1644827799328,
    'description': 'cm0 error', 'location': 'cm0#eterus-213546',
    'type': 'EquipmentAlarm', 'resource_type': 'Storage',
    'alert_name': 'cm0 error', 'match_key': 'e10adc3949ba59abbe56e057f20f883e'}
PORTS_OLD_DATA = [
    {'name': 'CM#0 Port#0', 'storage_id': '12345',
     'native_port_id': 'CM#0 Port#0', 'location': 'CM#0 Port#0', 'type': 'fc',
     'speed': 4000000000, 'connection_status': 'connected',
     'wwn': '500000E0D0376706', 'health_status': 'normal'},
    {'name': 'CM#0 Port#1', 'storage_id': '12345',
     'native_port_id': 'CM#0 Port#1', 'location': 'CM#0 Port#1', 'type': 'fc',
     'speed': None, 'connection_status': 'disconnected',
     'wwn': '500000E0D0376707', 'health_status': 'normal'},
    {'name': 'CM#1 Port#0', 'storage_id': '12345',
     'native_port_id': 'CM#1 Port#0', 'location': 'CM#1 Port#0', 'type': 'fc',
     'speed': None, 'connection_status': 'disconnected',
     'wwn': '500000E0D0376786', 'health_status': 'normal'},
    {'name': 'CM#1 Port#1', 'storage_id': '12345',
     'native_port_id': 'CM#1 Port#1', 'location': 'CM#1 Port#1', 'type': 'fc',
     'speed': 4000000000, 'connection_status': 'connected',
     'wwn': '500000E0D0376787', 'health_status': 'normal'}]
PORTS_DATA = [{'name': 'CM#0 CA#0 Port#0', 'storage_id': '12345',
               'native_port_id': 'CM#0 CA#0 Port#0',
               'location': 'CM#0 CA#0 Port#0', 'type': 'fc',
               'speed': 10000000000, 'connection_status': 'unknown',
               'wwn': '500000E0DA0A7D20', 'health_status': 'unknown'},
              {'name': 'CM#0 CA#0 Port#1', 'storage_id': '12345',
               'native_port_id': 'CM#0 CA#0 Port#1',
               'location': 'CM#0 CA#0 Port#1', 'type': 'fc',
               'speed': 10000000000, 'connection_status': 'unknown',
               'wwn': '500000E0DA0A7D21', 'health_status': 'unknown'},
              {'name': 'CM#0 CA#1 Port#0', 'storage_id': '12345',
               'native_port_id': 'CM#0 CA#1 Port#0',
               'location': 'CM#0 CA#1 Port#0', 'type': 'fc',
               'speed': 10000000000},
              {'name': 'CM#0 CA#1 Port#1', 'storage_id': '12345',
               'native_port_id': 'CM#0 CA#1 Port#1',
               'location': 'CM#0 CA#1 Port#1', 'type': 'fc',
               'speed': 10000000000}]
DISKS_OLD = [
    {'name': 'CE-Disk#0', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#0',
     'serial_number': '6SK2CEG91327', 'manufacturer': 'SEAGATE',
     'model': '3.5" SAS', 'firmware': 'GF0D', 'location': 'CE-Disk#0',
     'speed': 15000, 'capacity': 483183820800.0, 'status': 'abnormal',
     'physical_type': 'sas', 'logical_type': 'unknown'},
    {'name': 'CE-Disk#1', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#1',
     'serial_number': '6SK262SZ1312', 'manufacturer': 'SEAGATE',
     'model': '3.5" SAS', 'firmware': 'GF0D', 'location': 'CE-Disk#1',
     'speed': 15000, 'capacity': 483183820800.0, 'status': 'abnormal',
     'physical_type': 'sas', 'logical_type': 'unknown'},
    {'name': 'CE-Disk#2', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#2',
     'serial_number': '6SK26QCA1312', 'manufacturer': 'SEAGATE',
     'model': '3.5" SAS', 'firmware': 'GF0D', 'location': 'CE-Disk#2',
     'speed': 15000, 'capacity': 483183820800.0, 'status': 'normal',
     'physical_type': 'sas', 'logical_type': 'member'},
    {'name': 'CE-Disk#3', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#3',
     'serial_number': '6SK2DE941330', 'manufacturer': 'SEAGATE',
     'model': '3.5" SAS', 'firmware': 'GF0D', 'location': 'CE-Disk#3',
     'speed': 15000, 'capacity': 483183820800.0, 'status': 'normal',
     'physical_type': 'sas', 'logical_type': 'member'}]
DISKS_DATA = [
    {'name': 'CE-Disk#0', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#0',
     'serial_number': '0QWA91YA', 'manufacturer': 'HGST', 'model': '2.5 SSD-M',
     'firmware': 'H603', 'location': 'CE-Disk#0', 'speed': None,
     'capacity': 429496729600.0, 'status': 'normal', 'physical_type': 'ssd',
     'logical_type': 'member'},
    {'name': 'CE-Disk#1', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#1',
     'serial_number': '0QWAHN1A', 'manufacturer': 'HGST', 'model': '2.5 SSD-M',
     'firmware': 'H603', 'location': 'CE-Disk#1', 'speed': None,
     'capacity': 429496729600.0, 'status': 'normal', 'physical_type': 'ssd',
     'logical_type': 'member'},
    {'name': 'CE-Disk#2', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#2',
     'serial_number': '0QWA9GMA', 'manufacturer': 'HGST', 'model': '2.5 SSD-M',
     'firmware': 'H603', 'location': 'CE-Disk#2', 'speed': None,
     'capacity': 429496729600.0, 'status': 'normal', 'physical_type': 'ssd',
     'logical_type': 'member'},
    {'name': 'CE-Disk#3', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#3',
     'serial_number': '0QWA9KJA', 'manufacturer': 'HGST', 'model': '2.5 SSD-M',
     'firmware': 'H603', 'location': 'CE-Disk#3', 'speed': None,
     'capacity': 429496729600.0, 'status': 'normal', 'physical_type': 'ssd',
     'logical_type': 'member'},
    {'name': 'CE-Disk#4', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#4',
     'serial_number': '0QWAHMAA', 'manufacturer': 'HGST', 'model': '2.5 SSD-M',
     'firmware': 'H603', 'location': 'CE-Disk#4', 'speed': None,
     'capacity': 429496729600.0, 'status': 'normal', 'physical_type': 'ssd',
     'logical_type': 'member'},
    {'name': 'CE-Disk#5', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#5',
     'serial_number': 'S7M1LC92', 'manufacturer': 'SEAGATE',
     'model': '2.5 Online', 'firmware': 'VE0C', 'location': 'CE-Disk#5',
     'speed': 15000, 'capacity': 644245094400.0, 'status': 'normal',
     'physical_type': 'unknown', 'logical_type': 'member'},
    {'name': 'CE-Disk#6', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#6',
     'serial_number': 'W7M0M8PR', 'manufacturer': 'SEAGATE',
     'model': '2.5 Online', 'firmware': 'VE0C', 'location': 'CE-Disk#6',
     'speed': 15000, 'capacity': 644245094400.0, 'status': 'normal',
     'physical_type': 'unknown', 'logical_type': 'member'},
    {'name': 'CE-Disk#7', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#7',
     'serial_number': 'S7M1LC99', 'manufacturer': 'SEAGATE',
     'model': '2.5 Online', 'firmware': 'VE0C', 'location': 'CE-Disk#7',
     'speed': 15000, 'capacity': 644245094400.0, 'status': 'normal',
     'physical_type': 'unknown', 'logical_type': 'member'},
    {'name': 'CE-Disk#8', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#8',
     'serial_number': 'S7M1L3XD', 'manufacturer': 'SEAGATE',
     'model': '2.5 Online', 'firmware': 'VE0C', 'location': 'CE-Disk#8',
     'speed': 15000, 'capacity': 644245094400.0, 'status': 'normal',
     'physical_type': 'unknown', 'logical_type': 'member'},
    {'name': 'CE-Disk#9', 'storage_id': '12345', 'native_disk_id': 'CE-Disk#9',
     'serial_number': 'S7M1KXS5', 'manufacturer': 'SEAGATE',
     'model': '2.5 Online', 'firmware': 'VE0C', 'location': 'CE-Disk#9',
     'speed': 15000, 'capacity': 644245094400.0, 'status': 'normal',
     'physical_type': 'unknown', 'logical_type': 'member'},
    {'name': 'CE-Disk#10', 'storage_id': '12345',
     'native_disk_id': 'CE-Disk#10', 'serial_number': 'S7M1KCPD',
     'manufacturer': 'SEAGATE', 'model': '2.5 Online', 'firmware': 'VE0C',
     'location': 'CE-Disk#10', 'speed': 15000, 'capacity': 644245094400.0,
     'status': 'normal', 'physical_type': 'unknown', 'logical_type': 'member'},
    {'name': 'CE-Disk#11', 'storage_id': '12345',
     'native_disk_id': 'CE-Disk#11', 'serial_number': 'W7M0MYYA',
     'manufacturer': 'SEAGATE', 'model': '2.5 Online', 'firmware': 'VE0C',
     'location': 'CE-Disk#11', 'speed': 15000, 'capacity': 644245094400.0,
     'status': 'normal', 'physical_type': 'unknown', 'logical_type': 'member'}]
PARSE_ALERT_INFO = {
    '1.3.6.1.2.1.1.3.0': '123456',
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.211.4.1.1.126.1.150.0.2',
    '1.3.6.1.4.1.211.1.21.1.150.7.0': '-213546',
    '1.3.6.1.4.1.211.1.21.1.150.1.1.0': 'cm0#eterus',
    '1.3.6.1.4.1.211.1.21.1.150.11.0': 'cm0 error'
}


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
            side_effect=[VOLUMES_ERROR, VOLUMES_ERROR, VOLUMES_ERROR,
                         VOLUME_DATAS])
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
        self.assertEqual(data, DISKS_DATA)

    def test_list_disks_OLD(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(side_effect=[DISK_OLD])
        data = self.driver.list_disks(context)
        self.assertListEqual(data, DISKS_OLD)

    def test_list_ports(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[FCOE_INFO, NODE_DATAS])
        data = self.driver.list_ports(context)
        self.assertListEqual(data, PORTS_DATA)

    def test_list_ports_old(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[FC_INFO_OLD, NODE_DATAS_OLD])
        data = self.driver.list_ports(context)
        self.assertListEqual(data, PORTS_OLD_DATA)

    def test_parse_alert(self):
        parse_alert = self.driver.parse_alert(context, PARSE_ALERT_INFO)
        PARSE_ALERT_DATA['occur_time'] = parse_alert.get('occur_time')
        self.assertDictEqual(parse_alert, PARSE_ALERT_DATA)

    def test_list_storage_host_initiators(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[HOST_STATUS_INFO, FC_HOSTS_INFO, ISCSI_HOST_INFO,
                         ISCSI_HOST_DETAIL_ZERO, ISCSI_HOST_DETAIL_ONE,
                         ISCSI_HOST_DETAIL_TWO, SAS_HOST_INFO])
        initiators = self.driver.list_storage_host_initiators(context)
        self.assertListEqual(initiators, INITIATORS_DATA)

    def test_list_storage_hosts(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[HOST_STATUS_INFO, FC_HOSTS_INFO, ISCSI_HOST_INFO,
                         ISCSI_HOST_DETAIL_ZERO, ISCSI_HOST_DETAIL_ONE,
                         ISCSI_HOST_DETAIL_TWO, SAS_HOST_INFO])
        hosts = self.driver.list_storage_hosts(context)
        self.assertListEqual(hosts, HOSTS_DATA)

    def test_list_storage_host_groups(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[HOST_GROUPS_INFO])
        host_groups = self.driver.list_storage_host_groups(context)
        self.assertDictEqual(host_groups, HOST_GROUPS_DATA)

    def test_list_port_groups(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[PORT_G_VIEW_INFO])
        host_groups = self.driver.list_port_groups(context)
        self.assertDictEqual(host_groups, PORT_G_DATA)

    def test_list_volume_groups(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[VOLUME_GROUPS_INFO, VOLUME_DETAILS_INFO])
        volume_groups = self.driver.list_volume_groups(context)
        self.assertDictEqual(volume_groups, VOLUME_GROUPS_DATA)

    def test_list_masking_views(self):
        EternusSSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        EternusSSHPool.do_exec_shell = mock.Mock(
            side_effect=[MASKING_VIEWS_INFO])
        masking_views = self.driver.list_masking_views(context)
        self.assertListEqual(masking_views, MASKING_VIEWS_DATA)
