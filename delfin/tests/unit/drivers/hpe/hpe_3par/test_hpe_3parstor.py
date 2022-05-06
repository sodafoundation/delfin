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

import paramiko

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import exception
from delfin import context
from delfin.drivers.hpe.hpe_3par.hpe_3parstor import Hpe3parStorDriver
from delfin.drivers.hpe.hpe_3par.alert_handler import AlertHandler
from delfin.drivers.hpe.hpe_3par.rest_handler import RestHandler
from delfin.drivers.hpe.hpe_3par.ssh_handler import SSHHandler
from delfin.drivers.utils.rest_client import RestClient
from delfin.drivers.utils.ssh_client import SSHPool

from requests import Session


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
        "password": "cGFzc3dvcmQ="
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    }
}

NODE_DATAS = """
                                  Control    Data        Cache
Node --Name--- -State-- Master IC SLED LED Mem(MB) Mem(MB) Available(%)
   0 1307327-0 Degraded Yes Yes unknown AmberBlnk    4096    6144            0
   1 1307327-1 Degraded No  Yes unknown AmberBlnk    4096    6144            0
"""
NODE_CPU_DATAS = """
----------------------------CPUs----------------------------
Node CPU -Manufacturer- -Serial- CPUSpeed(MHz) BusSpeed(MHz)
   0   0 GenuineIntel   --                2327       1334.57
   0   1 GenuineIntel   --                2327       1334.57
   0   2 GenuineIntel   --                2327       1334.57
   0   3 GenuineIntel   --                2327       1334.57
   1   0 GenuineIntel   --                2327       1332.19
   1   1 GenuineIntel   --                2327       1332.19
   1   2 GenuineIntel   --                2327       1332.19
   1   3 GenuineIntel   --                2327       1332.19
"""
NODE_VERSION = """
Node: 0
--------
System serial: 1000183
BIOS version: 4.8.34
OS version: 3.2.2.204
Reset reason: Unknown

Node: 1
--------
BIOS version: 4.8.34
OS version: 3.2.2.204
Reset reason: Unknown
"""
DISK_DATAS = """
                           ---Size(MB)--- ----Ports----
Id CagePos Type RPM State      Total   Free A      B      Cap(GB)
 0 0:14:0  FC    15 degraded  571904  83968 0:2:2* -----      600
 1 0:1:0   FC    15 degraded  571904  62720 0:2:2* -----      600
-----------------------------------------------------------------
16 total                     9150464 912896

"""
DISK_I_DATAS = """
Id CagePos State Node_WWN MFR Model Serial FW_Rev Protocol MediaType AdminTime
0 0:14:0  degraded WWN11  MFR111 Model11  Serial111 FW_Rev111 Pl  MT1 600
1 0:1:0   degraded WWN22  MFR2222  Model22  Serial222 FW_Rev222 P2   MT2 600

"""
PORT_DATAS = """
N:S:P Mode State -Node_WWN- -Port_WWN/HW_Addr- Type Protocol Label Ptner FState
0:0:1 target ready 2FF70002AC001C9F 20010002AC001C9F host FC - 1:0:1 none
0:0:2 target loss_sync 2FF70002AC001C9F 20020002AC001C9F  free FC - - -
0:2:2 target loss_sync 2FF70002AC001C9F 20020002AC001C9F  free FC - - -
0:6:1 target loss_sync 2FF70002AC001C9F 20020002AC001C9F  free FC - - -
--------------------------------------------------------------------------
   18
"""
PORT_I_DATAS = """
N:S:P Brand Model Rev Firmware Serial HWType
0:0:1 LSI 9205-8e 01 17.11.00.00 SP12430085 SAS
0:0:2 LSI 9205-8e 01 17.11.00.00 SP12430085 FC
0:1:1 QLOGIC QLE2672 02 8.1.1 RFE1228G50820 FC
0:1:2 QLOGIC QLE2672 02 8.1.1 RFE1228G50820 FC
0:2:1 QLOGIC QLE8242 58 4.15.2 PCGLTX0RC1G3PX CNA
"""
PORT_PER_DATAS = """
N:S:P Connmode ConnType CfgRate MaxRate Class2 UniqNodeWwn VCN Il TMWO SSAN
0:0:1 disk point 6Gbps 6Gbps n/a n/a n/a enabled n/a n/a
0:0:2 disk point 6Gbps 6Gbps n/a n/a n/a enabled n/a n/a
0:1:1 host point auto 16Gbps disabled disabled disabled enabled disabled n/a
0:1:2 host point auto 16Gbps disabled disabled disabled enabled disabled n/a
"""
PORT_ISCSI_DATAS = """
N:S:P State IPAddr Netmask/PrefixLen Gateway TPGT MTU Rate iAddr iPort ST VLAN
0:2:1 ready 1df9:7b7b:790::21 64 :: 21 1500 10Gbps :: 3205 21 Y
0:2:2 ready 10.99.1.3 255.255.255.0 0.0.0.0 22 1500 10Gbps 0.0.0.0 3205 22 Y
"""
PORT_RCIP_DATAS = """
N:S:P State ---HwAddr--- IPAddr Netmask Gateway  MTU Rate Duplex AutoNeg
0:6:1 loss_sync 0002AC684AAD 10.11.35.10 255.255.0.0 10.11.0.1 900 n/a n/a n/a
1:6:1   offline 0002AC6A3A0F              -           - - -  n/a n/a n/a
-----------------------------------------------------------------------------
    2
"""
PORT_C_DATAS = """
N:S:P      Mode Device Pos Config Topology   Rate Cls Mode_change
0:0:1    target RedHat_196   0  valid fabric  8Gbps   3     allowed
                 RedHat_196   0  valid fabric  8Gbps   3     allowe
0:0:2    target Dorado5000V3_F1   0  valid fabric  8Gbps   3     allowed
                Dorado5000V3_F1   0  valid fabric  8Gbps   3     allowed
--------------------------------------------------------------------------
  108
"""

HOST_GROUP_DATAS = """
 Id Name                    Members                 Comment
194 HostSet_VMware          Host_ESXi6.5_125        --
229 HostSet_Suse11_Oracle   Host_Suse11_8.44.75.122 --
257 HostGroup_ESX6.0        ESX6.0_8.44.75.145      --
                            ESX6.0_8.44.75.146
264 HostSet_Win2016_WSFC    RH2288V5_Win2016_node2  --
                            RH2288V5_Win2016_node1
266 HostSet_Win2012_WSFC    RH2285_Win2012_wsfc1    --
                            Rh2285_Win2012_wsfc2
268 HostSet_AIX             Host_AIX_51.10.192.20   --
270 HostSet_Suse11          Host_Suse11_8.44.75.123 --
274 Suse11sp4_150           litng138.150            --
-----------------------------------------------------------
 32 total                   28
"""
HOST_ID_DATAS = """
  Id Name                      Persona        -WWN/iSCSI_Name- Port  IP_addr
 175 Host_ESXi6.5_125               Generic        2408244427906812 ---   n/a
 54 Doradov3_lm               Generic        2418244427906812 ---   n/a
 57 AIX_wenbin                AIX-legacy     10000000C9E74BCC ---   n/a
 65 SKY-ESXI60                Generic        2100001B321BE0FF ---   n/a
 65 SKY-ESXI60                Generic        2101001B323BE0FF ---   n/a
 67 zouming                   Generic        2012E4A8B6B0A1CC ---   n/a
 67 zouming                   Generic        2002E4A8B6B0A1CC ---   n/a
 68 powerpath                 Generic        21000024FF36D406 ---   n/a
 68 powerpath                 Generic        21000024FF36D407 ---   n/a
 69 power_v3                  Generic        20809CE37435D845 ---   n/a
 69 power_v3                  Generic        20909CE37435D845 ---   n/a
 89 vplex_meta_important      Generic        5000144280292012 0:1:2 n/a
 89 vplex_meta_important      Generic        5000144280292010 0:1:2 n/a
 89 vplex_meta_important      Generic        5000144290292012 1:1:2 n/a
 89 vplex_meta_important      Generic        500014429029E910 1:1:2 n/a
 89 vplex_meta_important      Generic        500014429029E912 1:1:2 n/a
 89 vplex_meta_important      Generic        500014428029E912 1:1:2 n/a
 89 vplex_meta_important      Generic        500014428029E910 1:1:2 n/a
 89 vplex_meta_important      Generic        5000144290292010 1:1:2 n/a
 89 vplex_meta_important      Generic        5000144290292012 0:1:2 n/a
 89 vplex_meta_important      Generic        5000144290292010 0:1:2 n/a
 89 vplex_meta_important      Generic        500014429029E912 0:1:2 n/a
 89 vplex_meta_important      Generic        500014429029E910 0:1:2 n/a
 89 vplex_meta_important      Generic        5000144280292012 1:1:2 n/a
 89 vplex_meta_important      Generic        5000144280292010 1:1:2 n/a
 89 vplex_meta_important      Generic        500014428029E912 0:1:2 n/a
 89 vplex_meta_important      Generic        500014428029E910 0:1:2 n/a
 91 Dorado5000_51.45          Generic        200080D4A58EA53A ---   n/a
 91 Dorado5000_51.45          Generic        201080D4A58EA53A ---   n/a
 98 AIX6.1_LN                 AIX-legacy     10000000C9781C57 ---   n/a
 98 AIX6.1_LN                 AIX-legacy     10000000C9781853 ---   n/a
115 huhuihost                 Generic        2100000E1E1A9B30 ---   n/a
121 Dorado5000V3_F3           Generic        201880D4A58EA53A ---   n/a
160 host002                     Generic        21000024FF41DCF8 ---   n/a
 -- --                        --             21000024FF41DCF7 1:0:2 n/a
 -- --                        --             21000024FF41DCF6 1:0:2 n/a
 -- --                        --             21000024FF0CC6CA 0:1:2 n/a
 -- --                        --             21000024FF0CC6CA 1:1:2 n/a
 -- --                        --             21000024FF0CBF47 0:1:2 n/a
 -- --                        --             21000024FF0CBF47 1:1:2 n/a
"""
VOLUME_GROUP_DATAS = """
Id Name              Members              Comment
 91 wcj_2             wcj_2.0              --
                      wcj_2.1
                      wcj_2.2
                      wcj_2.3
110 HP-Esxi-LUNSet    --                   --
124 zhangjun          --                   --
126 wcj_1             wcj_1.1              --
127 wcj_3             wcj_3.0              --
                      wcj_3.1
128 IBM_SVC           --                   --
129 zyz_3parF200_     zyz_3parF200.0       --
                      zyz_3parF200.1
                      zyz_3parF200.2
                      zyz_3parF200.3
130 zyz               zyz_2                --
131 tx                --                   --
132 tx9               --                   --
133 wcj_hp_1          --                   --
136 AIX_YG_WYK_LUN    AIX_YG_WYK_LUN.0     --
                      AIX_YG_WYK_LUN.1
                      AIX_YG_WYK_LUN.2
                      AIX_YG_WYK_LUN.3
140 st11              --                   --
146 Solaris_lun_group Solaris_LUN1_13G     --
                      solaris_LUN_2_33G
147 wcj_vplex         wcj_vplex.0          --
-----------------------------------------------------------
 32 total                   28
"""
VOLUME_ID_DATAS = """
  Id Name        Prov Type CopyOf BsId Rd -Detailed_State-  Adm Snp Usr VSize
4836 wcj_2.0    tpvv base ---    4836 RW normal        256 512 512  5120
4798 zyz_2         tpvv base ---    4836 RW normal        256 512 512  5120
4797 wcj_3.1         tpvv base ---    4836 RW normal        256 512 512  5120
666 yytest_vv_001     tpvv base ---    4836 RW normal        256 512 512  5120
------------------------------------------------------------------------
 409 total                             51072 158720 3279488 18186240
"""
HOST_DATAS = [
    {
        "total": 38,
        "members": [
            {
                "id": 54,
                "name": "Doradov3_lm",
                "descriptors": {
                    "location": "U9-3-B17R_B7",
                    "IPAddr": "100.157.61.100",
                    "os": "ESXI6.0",
                    "model": "RH2288H V3"
                },
                "FCPaths": [
                    {
                        "wwn": "2408244427906812",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2418244427906812",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 57,
                "name": "AIX_wenbin",
                "FCPaths": [
                    {
                        "wwn": "10000000C9E74BCC",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 5,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 65,
                "name": "SKY-ESXI60",
                "descriptors": {
                    "location": "U9-3-B17R_B7",
                    "IPAddr": "100.157.61.100",
                    "os": "ESXI6.0",
                    "model": "RH2288H V3"
                },
                "FCPaths": [
                    {
                        "wwn": "2100001B321BE0FF",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2101001B323BE0FF",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 67,
                "name": "zouming",
                "FCPaths": [
                    {
                        "wwn": "2012E4A8B6B0A1CC",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2002E4A8B6B0A1CC",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 68,
                "name": "powerpath",
                "FCPaths": [
                    {
                        "wwn": "21000024FF36D406",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF36D407",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 69,
                "name": "power_v3",
                "FCPaths": [
                    {
                        "wwn": "20809CE37435D845",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "20909CE37435D845",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 89,
                "name": "vplex_meta_important",
                "FCPaths": [
                    {
                        "wwn": "5000144280292012",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144280292010",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144290292012",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014429029E910",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014429029E912",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014428029E912",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014428029E910",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144290292010",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144290292012",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144290292010",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014429029E912",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014429029E910",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144280292012",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "5000144280292010",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014428029E912",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500014428029E910",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 91,
                "name": "Dorado5000_51.45",
                "FCPaths": [
                    {
                        "wwn": "200080D4A58EA53A",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "201080D4A58EA53A",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 98,
                "name": "AIX6.1_LN",
                "descriptors": {
                    "os": "AIX"
                },
                "FCPaths": [
                    {
                        "wwn": "10000000C9781C57",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "10000000C9781853",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 5,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 115,
                "name": "huhuihost",
                "descriptors": {
                    "os": "SuSE"
                },
                "FCPaths": [
                    {
                        "wwn": "2100000E1E1A9B30",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 121,
                "name": "Dorado5000V3_F3",
                "descriptors": {
                    "os": "Red Hat Enterprise Linux"
                },
                "FCPaths": [
                    {
                        "wwn": "201880D4A58EA53A",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "200380D4A58EA53A",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 122,
                "name": "DYP_RHEL",
                "descriptors": {
                    "IPAddr": "100.157.18.22",
                    "os": "Red Hat Enterprise Linux"
                },
                "FCPaths": [
                    {
                        "wwn": "10000090FA76D446",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "10000090FA76D447",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 123,
                "name": "DYP_Dorado6000",
                "FCPaths": [
                    {
                        "wwn": "2618346AC212FB94",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 124,
                "name": "tool_rhel6.8",
                "FCPaths": [
                    {
                        "wwn": "21000024FF543687",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF543686",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 125,
                "name": "OceanStor6800",
                "FCPaths": [
                    {
                        "wwn": "2430E0979656725A",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2208E0979656725A",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2218E0979656725A",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2428E0979656725A",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 126,
                "name": "fyc_test",
                "FCPaths": [
                    {
                        "wwn": "21000024FF41DE7E",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 127,
                "name": "huhui",
                "descriptors": {
                    "os": "SuSE"
                },
                "FCPaths": [
                    {
                        "wwn": "500601610864241E",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 132,
                "name": "ESX8.44.161.152",
                "descriptors": {
                    "os": "ESX 4.x/5.x"
                },
                "FCPaths": [
                    {
                        "wwn": "21000024FF2F3266",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF2F3267",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 8,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 133,
                "name": "ESX89PT_suse_8.44.190.111",
                "descriptors": {
                    "os": "SuSE"
                },
                "FCPaths": [
                    {
                        "wwn": "21000024FF36F1ED",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 134,
                "name": "SVC",
                "descriptors": {
                    "os": "Exanet"
                },
                "FCPaths": [
                    {
                        "wwn": "500507680110EF7C",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500507680120EF7C",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500507680120EF3E",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "500507680110EF3E",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 3,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 135,
                "name": "NSS_8.44.162.50",
                "descriptors": {
                    "os": "Red Hat Enterprise Linux"
                },
                "FCPaths": [
                    {
                        "wwn": "21000024FF0DC381",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 137,
                "name": "D185_8.44.143.201",
                "descriptors": {
                    "os": "Red Hat Enterprise Linux"
                },
                "FCPaths": [
                    {
                        "wwn": "29A11603042D0306",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "28D01603042D0306",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2903010203040509",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2802010203040509",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 139,
                "name": "Dorado3000V6",
                "FCPaths": [
                    {
                        "wwn": "2019CC64A68314D3",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2009CC64A68314D3",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 141,
                "name": "8.44.143.27T2",
                "FCPaths": [
                    {
                        "wwn": "10000090FA50C4DF",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "10000090FA50C4DE",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 142,
                "name": "8.44.143.27T1",
                "FCPaths": [],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 144,
                "name": "C61_51.10.58.190",
                "descriptors": {
                    "os": "Red Hat Enterprise Linux"
                },
                "FCPaths": [
                    {
                        "wwn": "2210112224901223",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2200112224901223",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2230112224901223",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2220112224901223",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 145,
                "name": "8.44.43.19",
                "FCPaths": [
                    {
                        "wwn": "21000024FF754606",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF1A99E1",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 146,
                "name": "ZTY_win2012",
                "descriptors": {
                    "os": "Windows 2012"
                },
                "FCPaths": [
                    {
                        "wwn": "21000024FF40272B",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF40272A",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 2,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 147,
                "name": "DoradoV6_183",
                "FCPaths": [
                    {
                        "wwn": "240B121314151617",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2409121314151617",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 148,
                "name": "rhev_125",
                "descriptors": {
                    "os": "Windows 2012"
                },
                "FCPaths": [
                    {
                        "wwn": "21000024FF4BC1B7",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF4BC1B6",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 2,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 150,
                "name": "windows2012_68",
                "descriptors": {
                    "os": "Windows 2012"
                },
                "FCPaths": [
                    {
                        "wwn": "2101001B32B0667A",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2100001B3290667A",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 2,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 151,
                "name": "Dorado5000V6_80",
                "FCPaths": [
                    {
                        "wwn": "2001183D5E0F5131",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "2011183D5E0F5131",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 152,
                "name": "windows2012_60",
                "descriptors": {
                    "os": "Windows 2012"
                },
                "FCPaths": [
                    {
                        "wwn": "21000024FF53B4BC",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF53B4BD",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 2,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 153,
                "name": "aix_8.44.134.204",
                "descriptors": {
                    "os": "AIX"
                },
                "FCPaths": [
                    {
                        "wwn": "10000000C975804C",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "10000000C9765E79",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 5,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 154,
                "name": "Dorado5500_V6_109",
                "descriptors": {
                    "IPAddr": "8.44.133.82",
                    "os": "Windows 2012"
                },
                "FCPaths": [
                    {
                        "wwn": "221818022D189653",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "220818022D189653",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 2,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 155,
                "name": "aix134.205",
                "descriptors": {
                    "IPAddr": "8.44.134.205",
                    "os": "AIX"
                },
                "FCPaths": [
                    {
                        "wwn": "20000000C9781C81",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "10000000C9781C0C",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 5,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "id": 158,
                "name": "hsv6",
                "FCPaths": [
                    {
                        "wwn": "28130A2B304438A8",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "28120A2B304438A8",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "28F20A2B304438A8",
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "28F30A2B304438A8",
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "persona": 1,
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            },
            {
                "FCPaths": [
                    {
                        "wwn": "21000024FF41DCF7",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF41DCF6",
                        "portPos": {
                            "node": 1,
                            "slot": 0,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF0CC6CA",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF0CC6CA",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF0CBF47",
                        "portPos": {
                            "node": 0,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    },
                    {
                        "wwn": "21000024FF0CBF47",
                        "portPos": {
                            "node": 1,
                            "slot": 1,
                            "cardPort": 2
                        },
                        "hostSpeed": 0
                    }
                ],
                "iSCSIPaths": [],
                "initiatorChapEnabled": False,
                "targetChapEnabled": False
            }
        ]
    }
]
VIEW_DATAS = """
  Lun VVName        HostName       -Host_WWN/iSCSI_Name- Port     Type
  2 yytest_vv_001 host002        ----------------       0:2:1     host
  0 set:vvset001  set:hostset111 ----------------       1:2:1 host set
--------------------------------------------------------------------
  2 total
"""

CONTROLLER_RESULT = [
    {
        'name': '1307327-0',
        'storage_id': '12345',
        'native_controller_id': '0',
        'status': 'degraded',
        'location': None,
        'soft_version': '3.2.2.204',
        'cpu_info': '4 * 2327 MHz',
        'memory_size': '10737418240'
    }]
DISK_RESULT = [
    {
        'name': '0:14:0',
        'storage_id': '12345',
        'native_disk_id': '0',
        'serial_number': 'Serial111',
        'manufacturer': 'MFR111',
        'model': 'Model11',
        'firmware': 'FW_Rev111',
        'speed': 15000,
        'capacity': 599684808704,
        'status': 'degraded',
        'physical_type': 'fc',
        'logical_type': None,
        'health_score': None,
        'native_disk_group_id': None,
        'location': '0:14:0'
    }]
PORT_RESULT = [
    {
        'name': '0:0:1',
        'storage_id': '12345',
        'native_port_id': '0:0:1',
        'location': '0:0:1',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'sas',
        'logical_type': None,
        'speed': 8000000000,
        'max_speed': 6000000000,
        'native_parent_id': None,
        'wwn': '20010002AC001C9F',
        'mac_address': None,
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }]
HOST_GROUP_RESULT = [
    {
        'name': 'HostSet_VMware',
        'description': '',
        'storage_id': '12345',
        'native_storage_host_group_id': '194'
    }]
VOLUME_GROUP_RESULT = [
    {
        'name': 'wcj_2',
        'description': '',
        'storage_id': '12345',
        'native_volume_group_id': '91'
    }]
PORT_GROUP_RESULT = [
    {
        'name': 'port_group_0:2:1',
        'description': 'port_group_0:2:1',
        'storage_id': '12345',
        'native_port_group_id': 'port_group_0:2:1'
    }]
HOST_RESULT = [
    {
        'name': 'Doradov3_lm',
        'description': None,
        'storage_id': '12345',
        'native_storage_host_id': 54,
        'os_type': 'VMware ESX',
        'status': 'normal',
        'ip_address': '100.157.61.100'
    }]
INITIATOR_RESULT = [
    {
        'name': '2408244427906812',
        'storage_id': '12345',
        'native_storage_host_initiator_id': '2408244427906812',
        'wwn': '2408244427906812',
        'type': 'fc',
        'status': 'online',
        'native_storage_host_id': '175'
    }]
VIEW_RESULT = [
    {
        'native_masking_view_id': '2_0:2:1_host002_yytest_vv_001',
        'name': '2',
        'storage_id': '12345',
        'native_port_group_id': 'port_group_0:2:1',
        'native_volume_id': '666',
        'native_storage_host_id': '160'
    }]


def create_driver():
    kwargs = ACCESS_INFO

    SSHHandler.login = mock.Mock(
        return_value={"result": "success", "reason": "null"})

    m = mock.MagicMock(status_code=201)
    with mock.patch.object(Session, 'post', return_value=m):
        m.raise_for_status.return_value = 201
        m.json.return_value = {
            'key': 'deviceid123ABC456'
        }
        return Hpe3parStorDriver(**kwargs)


class TestHpe3parStorageDriver(TestCase):

    def test_a_init(self):
        kwargs = ACCESS_INFO
        SSHHandler.login = mock.Mock(
            return_value={""})
        RestHandler.login = mock.Mock(
            return_value={""})
        Hpe3parStorDriver(**kwargs)

    def test_b_initrest(self):
        m = mock.MagicMock()
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 201
            m.json.return_value = {
                'key': '1&2F28CA9FC1EA0B8EAB80E9D8FD'
            }
            kwargs = ACCESS_INFO
            rc = RestClient(**kwargs)
            RestHandler(rc)

    def test_d_get_storage(self):
        driver = create_driver()
        expected = {
            'name': 'hp3parf200',
            'vendor': 'HPE',
            'model': 'InServ F200',
            'status': 'abnormal',
            'serial_number': '1307327',
            'firmware_version': '3.1.2.484',
            'location': None,
            'total_capacity': 7793486594048,
            'raw_capacity': 9594956939264,
            'used_capacity': 6087847706624,
            'free_capacity': 1705638887424
        }

        ret = {
            "id": 7327,
            "name": "hp3parf200",
            "systemVersion": "3.1.2.484",
            "IPv4Addr": "100.157.92.213",
            "model": "InServ F200",
            "serialNumber": "1307327",
            "totalNodes": 2,
            "masterNode": 0,
            "onlineNodes": [
                0,
                1
            ],
            "clusterNodes": [
                0,
                1
            ],
            "chunkletSizeMiB": 256,
            "totalCapacityMiB": 9150464,
            "allocatedCapacityMiB": 5805824,
            "freeCapacityMiB": 1626624,
            "failedCapacityMiB": 1718016,
            "timeZone": "Asia/Shanghai"
        }

        RestHandler.get_capacity = mock.Mock(
            return_value={
                "allCapacity": {
                    "totalMiB": 9150464,
                    "allocated": {
                        "system": {
                            "totalSystemMiB": 1232384,
                            "internalMiB": 303104,
                            "spareMiB": 929280,
                            "spareUsedMiB": 307456,
                            "spareUnusedMiB": 621824
                        }
                    }
                }
            }
        )
        health_state = 'PDs that are degraded'
        SSHHandler.get_health_state = mock.Mock(return_value=health_state)
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(RestHandler, 'call', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = ret

            storage = driver.get_storage(context)
            self.assertDictEqual(storage, expected)

    def test_e_list_storage_pools(self):
        driver = create_driver()
        expected = [
            {
                'name': 'test',
                'storage_id': '12345',
                'native_storage_pool_id': '0',
                'description': 'Hpe 3par CPG:test',
                'status': 'normal',
                'storage_type': 'block',
                'total_capacity': 2003870679040,
                'subscribed_capacity': 2917892358144,
                'used_capacity': 1448343502848,
                'free_capacity': 555527176192
            }, {
                'name': 'cxd',
                'storage_id': '12345',
                'native_storage_pool_id': '1',
                'description': 'Hpe 3par CPG:cxd',
                'status': 'normal',
                'storage_type': 'block',
                'total_capacity': 1744025157632,
                'subscribed_capacity': 2200095948800,
                'used_capacity': 1696512081920,
                'free_capacity': 47513075712
            }
        ]

        ret = [
            {
                "total": 2,
                "members": [
                    {
                        "id": 0,
                        "uuid": "aa43f218-d3dd-4626-948f-8a160b0eac1d",
                        "name": "test",
                        "numFPVVs": 21,
                        "numTPVVs": 25,
                        "UsrUsage": {
                            "totalMiB": 1381504,
                            "rawTotalMiB": 1842004,
                            "usedMiB": 1376128,
                            "rawUsedMiB": 712703
                        },
                        "SAUsage": {
                            "totalMiB": 140800,
                            "rawTotalMiB": 422400,
                            "usedMiB": 5120,
                            "rawUsedMiB": 15360
                        },
                        "SDUsage": {
                            "totalMiB": 388736,
                            "rawTotalMiB": 518315,
                            "usedMiB": 0,
                            "rawUsedMiB": 0
                        },
                        "SAGrowth": {
                            "incrementMiB": 8192,
                            "LDLayout": {
                                "HA": 3,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "SDGrowth": {
                            "incrementMiB": 32768,
                            "LDLayout": {
                                "RAIDType": 3,
                                "HA": 3,
                                "setSize": 4,
                                "chunkletPosPref": 1,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": []
                    },
                    {
                        "id": 1,
                        "uuid": "c392910e-7648-4972-b594-47dd3d28f3ec",
                        "name": "cxd",
                        "numFPVVs": 14,
                        "numTPVVs": 319,
                        "UsrUsage": {
                            "totalMiB": 1418752,
                            "rawTotalMiB": 1702500,
                            "usedMiB": 1417984,
                            "rawUsedMiB": 568934
                        },
                        "SAUsage": {
                            "totalMiB": 56832,
                            "rawTotalMiB": 170496,
                            "usedMiB": 42752,
                            "rawUsedMiB": 128256
                        },
                        "SDUsage": {
                            "totalMiB": 187648,
                            "rawTotalMiB": 225179,
                            "usedMiB": 157184,
                            "rawUsedMiB": 188620
                        },
                        "SAGrowth": {
                            "incrementMiB": 8192,
                            "LDLayout": {
                                "HA": 3,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "SDGrowth": {
                            "incrementMiB": 32768,
                            "LDLayout": {
                                "RAIDType": 3,
                                "HA": 3,
                                "setSize": 6,
                                "chunkletPosPref": 1,
                                "diskPatterns": [
                                    {
                                        "diskType": 1
                                    }
                                ]
                            }
                        },
                        "state": 1,
                        "failedStates": [],
                        "degradedStates": [],
                        "additionalStates": []
                    }
                ]
            }
        ]

        with mock.patch.object(RestHandler, 'get_resinfo_call',
                               side_effect=ret):
            pools = driver.list_storage_pools(context)
            self.assertDictEqual(pools[0], expected[0])
            self.assertDictEqual(pools[1], expected[1])

        with mock.patch.object(RestHandler, 'get_all_pools',
                               side_effect=exception.DelfinException):
            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)
            self.assertIn('An unknown exception occurred',
                          str(exc.exception))

    def test_f_list_volumes(self):
        driver = create_driver()
        expected = [{
            'name': 'admin',
            'storage_id': '12345',
            'description': None,
            'status': 'normal',
            'native_volume_id': '0',
            'native_storage_pool_id': '',
            'wwn': '50002AC000001C9F',
            'type': 'thick',
            'total_capacity': 10737418240,
            'used_capacity': 10737418240,
            'free_capacity': 0,
            'compressed': True,
            'deduplicated': True
        }]
        ret = [{
            "members": [{
                "id": 0,
                "name": "admin",
                "provisioningType": 1,
                "copyType": 1,
                "baseId": 0,
                "readOnly": False,
                "state": 1,
                "userSpace": {
                    "reservedMiB": 10240,
                    "rawReservedMiB": 20480,
                    "usedMiB": 10240,
                    "freeMiB": 0
                },
                "sizeMiB": 10240,
                "wwn": "50002AC000001C9F"
            }]
        }]
        pool_ret = {
            "members": [{
                "id": 0,
                "uuid": "aa43f218-d3dd-4626-948f-8a160b0eac1d",
                "name": "test"
            }]
        }
        RestHandler.get_all_pools = mock.Mock(return_value=pool_ret)
        with mock.patch.object(RestHandler, 'get_resinfo_call',
                               side_effect=ret):
            volumes = driver.list_volumes(context)
            self.assertDictEqual(volumes[0], expected[0])

    def test_h_parse_alert(self):
        """ Success flow with all necessary parameters"""
        driver = create_driver()
        alert = {
            'sysUpTime': '1399844806',
            'snmpTrapOID': 'alertNotify',
            '1.3.6.1.4.1.12925.1.7.1.5.1': 'test_trap',
            '1.3.6.1.4.1.12925.1.7.1.6.1': 'This is a test trap',
            'nodeID': '0',
            '1.3.6.1.4.1.12925.1.7.1.2.1': '6',
            '1.3.6.1.4.1.12925.1.7.1.3.1': 'test time',
            '1.3.6.1.4.1.12925.1.7.1.7.1': '89',
            '1.3.6.1.4.1.12925.1.7.1.8.1': '2555934',
            '1.3.6.1.4.1.12925.1.7.1.9.1': '5',
            'serialNumber': '1307327',
            'transport_address': '100.118.18.100',
            'storage_id': '1c094309-70f2-4da3-ac47-e87cc1492ad5'
        }

        expected_alert_model = {
            'alert_id': '0x027001e',
            'alert_name': 'CPG growth non admin limit',
            'severity': 'NotSpecified',
            'category': 'Recovery',
            'type': 'EquipmentAlarm',
            'sequence_number': '89',
            'description': 'This is a test trap',
            'resource_type': 'Storage',
            'location': 'test_trap',
            'occur_time': '',
            'clear_category': 'Automatic'
        }
        context = {}
        alert_model = driver.parse_alert(context, alert)

        # Verify that all other fields are matching
        self.assertDictEqual(expected_alert_model, alert_model)

    def test_list_alert(self):
        """ Success flow with all necessary parameters"""
        driver = create_driver()
        alert = """
        Id : 1
        State : New
        MessageCode : 0x2200de
        Time : 2015-07-17 20:14:29 PDT
        Severity : Degraded
        Type : Component state change
        Message : Node 0, Power Supply 1, Battery 0 Degraded
        Component: 100.118.18.100

        """

        expected_alert = [{
            'alert_id': '0x2200de',
            'alert_name': 'Component state change',
            'severity': 'Warning',
            'category': 'Fault',
            'type': 'EquipmentAlarm',
            'sequence_number': '1',
            'occur_time': 1437135269000,
            'description': 'Node 0, Power Supply 1, Battery 0 Degraded',
            'resource_type': 'Storage',
            'location': '100.118.18.100'
        }]
        SSHHandler.get_all_alerts = mock.Mock(return_value=alert)
        alert_list = driver.list_alerts(context, None)
        expected_alert[0]['occur_time'] = alert_list[0]['occur_time']
        self.assertDictEqual(alert_list[0], expected_alert[0])

    @mock.patch.object(AlertHandler, 'clear_alert')
    def test_clear_alert(self, mock_clear_alert):
        driver = create_driver()
        alert_id = '230584300921369'
        driver.clear_alert(context, alert_id)
        self.assertEqual(mock_clear_alert.call_count, 1)

    def test_get_controllers(self):
        driver = create_driver()
        SSHPool.get = mock.Mock(return_value={paramiko.SSHClient()})
        SSHPool.do_exec = mock.Mock(
            side_effect=[NODE_DATAS, NODE_CPU_DATAS, NODE_VERSION])
        controllers = driver.list_controllers(context)
        self.assertDictEqual(controllers[0], CONTROLLER_RESULT[0])

    def test_get_disks(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(side_effect=[DISK_DATAS, DISK_I_DATAS])
        disks = driver.list_disks(context)
        self.assertDictEqual(disks[0], DISK_RESULT[0])

    def test_get_ports(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(
            side_effect=[PORT_DATAS, PORT_I_DATAS, PORT_PER_DATAS,
                         PORT_ISCSI_DATAS, PORT_RCIP_DATAS, PORT_C_DATAS,
                         PORT_RCIP_DATAS, PORT_RCIP_DATAS])
        ports = driver.list_ports(context)
        self.assertDictEqual(ports[0], PORT_RESULT[0])

    def test_get_storage_host_groups(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(side_effect=[HOST_GROUP_DATAS,
                                                 HOST_ID_DATAS])
        host_groups = driver.list_storage_host_groups(context)
        self.assertDictEqual(host_groups.get('storage_host_groups')[0],
                             HOST_GROUP_RESULT[0])

    def test_get_volume_groups(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(side_effect=[VOLUME_GROUP_DATAS,
                                                 VOLUME_ID_DATAS])
        volume_groups = driver.list_volume_groups(context)
        self.assertDictEqual(volume_groups.get('volume_groups')[0],
                             VOLUME_GROUP_RESULT[0])

    def test_storage_hosts(self):
        driver = create_driver()
        with mock.patch.object(RestHandler, 'get_resinfo_call',
                               side_effect=HOST_DATAS):
            storage_hosts = driver.list_storage_hosts(context)
            self.assertDictEqual(storage_hosts[0], HOST_RESULT[0])

    def test_get_storage_host_initiators(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(side_effect=[HOST_ID_DATAS])
        initiators = driver.list_storage_host_initiators(context)
        self.assertDictEqual(initiators[0], INITIATOR_RESULT[0])

    def test_get_masking_views(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(
            side_effect=[VIEW_DATAS, HOST_ID_DATAS, HOST_GROUP_DATAS,
                         VOLUME_ID_DATAS, VOLUME_GROUP_DATAS])
        views = driver.list_masking_views(context)
        self.assertDictEqual(views[0], VIEW_RESULT[0])

    def test_get_port_groups(self):
        driver = create_driver()
        SSHPool.do_exec = mock.Mock(side_effect=[VIEW_DATAS])
        port_groups = driver.list_port_groups(context)
        self.assertDictEqual(port_groups.get('port_groups')[0],
                             PORT_GROUP_RESULT[0])
