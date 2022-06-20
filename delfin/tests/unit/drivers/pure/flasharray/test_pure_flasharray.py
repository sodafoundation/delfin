# Copyright 2022 The SODA Authors.
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

import six
from oslo_log import log
from oslo_utils import units

from delfin.common import constants
from delfin.drivers.pure.flasharray import consts

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.pure.flasharray.rest_handler import RestHandler
from delfin.drivers.pure.flasharray.pure_flasharray import PureFlashArrayDriver

LOG = log.getLogger(__name__)

ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "10.0.0.1",
        "port": 8443,
        "username": "user",
        "password": "pass"
    }
}

volumes_info = [
    {
        "total": 116272464547,
        "name": "oracl_ail",
        "system": "",
        "snapshots": 0,
        "volumes": 116272464547,
        "data_reduction": 1.82656654775252,
        "size": 2156324555567,
        "shared_space": "",
        "thin_provisioning": 0.9225557589632,
        "total_reduction": 18.92245232244555
    },
    {
        "total": 0,
        "name": "wxt1",
        "system": "",
        "snapshots": 0,
        "volumes": 0,
        "data_reduction": 1,
        "size": 1073741824,
        "shared_space": "",
        "thin_provisioning": 1,
        "total_reduction": 1
    }
]

pool_info = [
    {
        "name": "lktest",
        "volumes": [
            "oracl_ail",
            "wxt1",
            "lktest/lk301",
            "lktest/lk401",
            "lktest/lk501",
        ]
    },
    {
        "name": "ethanTestVG",
        "volumes": [

        ]
    }
]
volume_info = {
    "created": "2016-05-02T20:36:20Z",
    "name": "oracl_ail",
    "serial": "Fedd3455666y",
    "size": 1073740124,
    "source": ""
}
volume_info_two = {
    "created": "2016-05-02T20:36:20Z",
    "name": "wxt1",
    "serial": "Fedd3475666y",
    "size": 1073740124,
    "source": ""
}
storage_info = [
    {
        "parity": "0.996586544522471235",
        "provisioned": "20869257625600",
        "hostname": "FA-m20",
        "system": 0,
        "snapshots": 0,
        "volumes": 227546215656,
        "data_reduction": 1,
        "capacity": 122276719419392,
        "total": 324829845504,
        "shared_space": 97544451659,
        "thin_provisioning": 0.9526445631455244,
        "total_reduction": 64.152236458789225
    }
]
storage_id_info = {
    "array_name": "pure01",
    "id": "dlmkk15xcfdf4v5",
    "revision": "2016-20-29mfmkkk",
    "version": "4.6.7"
}
alerts_info = [
    {
        "category": "array",
        "code": 42,
        "actual": "",
        "opened": "2018-05-12T10:55:21Z",
        "component_type": "hardware",
        "event": "failure",
        "current_severity": "warning",
        "details": "",
        "expected": "",
        "id": 135,
        "component_name": "ct1.eth0"
    },
    {
        "category": "array",
        "code": 13,
        "actual": "",
        "opened": "2018-05-12T10:55:21Z",
        "component_type": "process",
        "event": "server unreachable",
        "current_severity": "warning",
        "details": "",
        "expected": "",
        "id": 10088786,
        "component_name": "ct1.ntpd"
    }
]
parse_alert_info = {
    '1.3.6.1.2.1.1.3.0': '30007589',
    '1.3.6.1.4.1.40482.3.7': '2',
    '1.3.6.1.4.1.40482.3.6': 'server error',
    '1.3.6.1.4.1.40482.3.3': 'cto',
    '1.3.6.1.4.1.40482.3.5': 'cto.server error'
}
controllers_info = [
    {
        "status": "ready",
        "name": "CT0",
        "version": "5.3.0",
        "mode": "primary",
        "model": "FA-m20r2",
        "type": "array_controller"
    },
    {
        "status": "ready",
        "name": "CT1",
        "version": "5.3.0",
        "mode": "secondary",
        "model": "FA-m20r2",
        "type": "array_controller"
    }
]
hardware_info = [
    {
        "details": "",
        "identify": "off",
        "index": 0,
        "name": "CTO.FC1",
        "slot": "",
        "speed": 0,
        "status": "ok",
        "temperature": ""
    },
    {
        "details": "",
        "identify": "",
        "index": 0,
        "name": "CTO.ETH15",
        "slot": 0,
        "speed": 1000000,
        "status": "ok",
        "temperature": ""
    }
]
drive_info = [
    {
        "status": "healthy",
        "protocol": "SAS",
        "name": "CH0.BAY1",
        "last_evac_completed": "1970-01-01T00:00:00Z",
        "details": "",
        "capacity": 1027895542547,
        "type": "SSD",
        "last_failure": "1970-01-01T00:00:00Z"
    },
    {
        "status": "healthy",
        "protocol": "SAS",
        "name": "CH0.BAY2",
        "last_evac_completed": "1970-01-01T00:00:00Z",
        "details": "",
        "capacity": 1027895542547,
        "type": "SSD",
        "last_failure": "1970-01-01T00:00:00Z"
    },
    {
        "status": "healthy",
        "protocol": "SAS",
        "name": "CH0.BAY3",
        "last_evac_completed": "1970-01-01T00:00:00Z",
        "details": "",
        "capacity": 1027895542547,
        "type": "SSD",
        "last_failure": "1970-01-01T00:00:00Z"
    }
]
port_info = [
    {
        "name": "CTO.FC1",
        "failover": "",
        "iqn": "iqn.2016-11-01.com.pure",
        "portal": "100.12.253.23:4563",
        "wwn": "43ddff45ggg4rty",
        "nqn": ""
    },
    {
        "name": "CTO.ETH15",
        "failover": "",
        "iqn": "iqn.2016-11-01.com.pure",
        "portal": "100.12.253.23:4563",
        "wwn": None,
        "nqn": None
    }
]
port_network_info = [
    {
        "name": "CTO.FC1",
        "address": "45233662jksndj",
        "speed": 12000,
        "netmask": "100.12.253.23:4563",
        "wwn": "43ddff45ggg4rty",
        "nqn": None,
        "services": [
            "management"
        ]
    },
    {
        "name": "CTO.ETH15",
        "address": "45233662jksndj",
        "speed": 13000,
        "netmask": "100.12.253.23:4563",
        "wwn": None,
        "nqn": None,
        "services": [
            "management"
        ]
    }
]
pools_info = [
    {
        "total": "",
        "name": "lktest",
        "snapshots": "",
        "volumes": 0,
        "data_reduction": 1,
        "size": 5632155322,
        "thin_provisioning": 1,
        "total_reduction": 1
    },
    {
        "total": "",
        "name": "ethanTestVG",
        "snapshots": "",
        "volumes": 0,
        "data_reduction": 1,
        "size": 5632155322,
        "thin_provisioning": 1,
        "total_reduction": 1
    }
]
reset_connection_info = {
    "username": "username",
    "status": 200
}
hosts_info = [
    {
        "iqn": [
            "iqn.1996-04.de.suse:01:ca9f3bcaf47"
        ],
        "wwn": [],
        "nqn": [],
        "name": "host",
        "hgroup": "HGTest"
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "wxth",
        "hgroup": None
    },
    {
        "iqn": [
            "iqn.1991-05.com.microsoft:win3"
        ],
        "wwn": [],
        "nqn": [],
        "name": "huhuitest",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "testGroup",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [
            "21000024FF2C9524",
            "21000024FF2C9525"
        ],
        "nqn": [],
        "name": "windows223",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [
            "10000000C9D5BC06",
            "10000000C9D5BC07"
        ],
        "nqn": [],
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [
            "21000024FF76D0CC",
            "21000024FF76D0CD"
        ],
        "nqn": [],
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "hgroup": None
    },
    {
        "iqn": [
            "iqn.1996-04.de.suse:01:66bf70288332"
        ],
        "wwn": [],
        "nqn": [],
        "name": "test-1s",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "rhev125",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [
            "210034800D6E7ADE",
            "210034800D6E7ADF"
        ],
        "nqn": [],
        "name": "QIB",
        "hgroup": "QIB"
    },
    {
        "iqn": [],
        "wwn": [
            "20090002D2937E9F",
            "20190002D2937E9F"
        ],
        "nqn": [],
        "name": "v6-8-44-128-21",
        "hgroup": None
    },
    {
        "iqn": [
            "iqn.1994-05.com.redhat:1a9eaa70b558"
        ],
        "wwn": [],
        "nqn": [],
        "name": "host135",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [
            "2200CC05777C3EDF",
            "2210CC05777C3EDF"
        ],
        "nqn": [],
        "name": "zty-doradoV6",
        "hgroup": None
    },
    {
        "iqn": [
            "iqn.1994-05.com.redhat:71cfb5b97df"
        ],
        "wwn": [
            "21000024FF76D0CF"
        ],
        "nqn": [],
        "name": "CL-Test1",
        "hgroup": None
    },
    {
        "iqn": [
            "iqn.1994-05.com.redhat:80c412848b94"
        ],
        "wwn": [],
        "nqn": [],
        "name": "host137",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "hsesxi",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [
            "21000024FF40272A",
            "21000024FF40272B"
        ],
        "nqn": [],
        "name": "zty-windows",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "hosttest",
        "hgroup": "HGTest"
    },
    {
        "iqn": [],
        "wwn": [
            "21000024FF5351F0",
            "21000024FF5351F1"
        ],
        "nqn": [],
        "name": "hswin41",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "ztj201",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "test123",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [],
        "name": "zsytest",
        "hgroup": None
    },
    {
        "iqn": [],
        "wwn": [],
        "nqn": [
            "nqn.2021-12.org.nvmexpress.mytest"
        ],
        "name": "zhilong-host0000002130",
        "hgroup": None
    }
]
HOSTS_PERSONALITY_INFO = [
    {
        "name": "host",
        "personality": None
    },
    {
        "name": "wxth",
        "personality": None
    },
    {
        "name": "huhuitest",
        "personality": None
    },
    {
        "name": "testGroup",
        "personality": None
    },
    {
        "name": "windows223",
        "personality": None
    },
    {
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "personality": None
    },
    {
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "personality": None
    },
    {
        "name": "test-1s",
        "personality": None
    },
    {
        "name": "rhev125",
        "personality": None
    },
    {
        "name": "QIB",
        "personality": None
    },
    {
        "name": "v6-8-44-128-21",
        "personality": None
    },
    {
        "name": "host135",
        "personality": None
    },
    {
        "name": "zty-doradoV6",
        "personality": None
    },
    {
        "name": "CL-Test1",
        "personality": None
    },
    {
        "name": "host137",
        "personality": None
    },
    {
        "name": "hsesxi",
        "personality": None
    },
    {
        "name": "zty-windows",
        "personality": None
    },
    {
        "name": "hosttest",
        "personality": None
    },
    {
        "name": "hswin41",
        "personality": None
    },
    {
        "name": "ztj201",
        "personality": None
    },
    {
        "name": "test123",
        "personality": None
    },
    {
        "name": "zsytest",
        "personality": None
    },
    {
        "name": "zhilong-host0000002130",
        "personality": "aix"
    }
]
HGROUP_INFO = [
    {
        "hosts": [],
        "name": "podgroup"
    },
    {
        "hosts": [],
        "name": "NewTest"
    },
    {
        "hosts": [
            "QIB"
        ],
        "name": "QIB"
    },
    {
        "hosts": [
            "host",
            "hosttest"
        ],
        "name": "HGTest"
    }
]

VOLUME_GROUP_INFO = [
    {
        "name": "vvol-pure-VM1-072e131e-vg",
        "volumes": []
    },
    {
        "name": "vvol-pure-vm2-e48a0ef8-vg",
        "volumes": []
    },
    {
        "name": "vvol-pure-vm3-65d42a4e-vg",
        "volumes": []
    },
    {
        "name": "vvol-pure-vm4-17c41971-vg",
        "volumes": []
    },
    {
        "name": "Volume-Group",
        "volumes": [
            "Volume-Group/voltest001",
            "Volume-Group/voltest002",
            "Volume-Group/voltest003",
            "Volume-Group/voltest004",
            "Volume-Group/voltest005"
        ]
    },
    {
        "name": "test1",
        "volumes": []
    },
    {
        "name": "tangxuan",
        "volumes": []
    }
]
HOSTS_CONNECT_INFO = [
    {
        "vol": "huhuitest",
        "name": "huhuitest",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "test",
        "name": "wxth",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "test",
        "name": "testGroup",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "win2016_223",
        "name": "windows223",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "pure-protocol-endpoint",
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "CL_VOLUME_1_remote",
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "lun-test1s",
        "name": "test-1s",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "QIB1",
        "name": "QIB",
        "lun": 254,
        "hgroup": "QIB"
    },
    {
        "vol": "QIB1",
        "name": "zty-windows",
        "lun": 254,
        "hgroup": "QIB"
    },
    {
        "vol": "QIB2",
        "name": "zty-windows",
        "lun": 253,
        "hgroup": "QIB"
    },
    {
        "vol": "QIB2",
        "name": "QIB",
        "lun": 253,
        "hgroup": "QIB"
    },
    {
        "vol": "yzw_iotest",
        "name": "host135",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000003",
        "name": "host137",
        "lun": 3,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000009",
        "name": "host135",
        "lun": 3,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000012",
        "name": "host135",
        "lun": 6,
        "hgroup": None
    },
    {
        "vol": "v6-8-44-128-21",
        "name": "v6-8-44-128-21",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "V6-8-44-128-21-002",
        "name": "v6-8-44-128-21",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000007",
        "name": "host137",
        "lun": 7,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000010",
        "name": "host135",
        "lun": 4,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000013",
        "name": "host137",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000000",
        "name": "host135",
        "lun": 5,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000001",
        "name": "host137",
        "lun": 4,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000016",
        "name": "host137",
        "lun": 5,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000018",
        "name": "host135",
        "lun": 7,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000015",
        "name": "host135",
        "lun": 8,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000020",
        "name": "host137",
        "lun": 6,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000021",
        "name": "host135",
        "lun": 9,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000022",
        "name": "host137",
        "lun": 8,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000019",
        "name": "host135",
        "lun": 10,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000026",
        "name": "host137",
        "lun": 9,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000028",
        "name": "host135",
        "lun": 11,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000024",
        "name": "host137",
        "lun": 10,
        "hgroup": None
    },
    {
        "vol": "hsboot",
        "name": "hsesxi",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "hszdata",
        "name": "hsesxi",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "zty_lun16",
        "name": "zty-doradoV6",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "zty_lun15",
        "name": "zty-doradoV6",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "zty_lun13",
        "name": "zty-doradoV6",
        "lun": 3,
        "hgroup": None
    },
    {
        "vol": "zty_lun11",
        "name": "zty-doradoV6",
        "lun": 4,
        "hgroup": None
    },
    {
        "vol": "zty_lun14",
        "name": "zty-doradoV6",
        "lun": 5,
        "hgroup": None
    },
    {
        "vol": "zty_lun2",
        "name": "zty-doradoV6",
        "lun": 6,
        "hgroup": None
    },
    {
        "vol": "zty_lun5",
        "name": "zty-doradoV6",
        "lun": 7,
        "hgroup": None
    },
    {
        "vol": "zty_lun4",
        "name": "zty-doradoV6",
        "lun": 8,
        "hgroup": None
    },
    {
        "vol": "zty_lun1",
        "name": "zty-doradoV6",
        "lun": 9,
        "hgroup": None
    },
    {
        "vol": "zty_lun3",
        "name": "zty-doradoV6",
        "lun": 10,
        "hgroup": None
    },
    {
        "vol": "zty_lun6",
        "name": "zty-doradoV6",
        "lun": 11,
        "hgroup": None
    },
    {
        "vol": "zty_lun12",
        "name": "zty-doradoV6",
        "lun": 12,
        "hgroup": None
    },
    {
        "vol": "zty_lun10",
        "name": "zty-doradoV6",
        "lun": 13,
        "hgroup": None
    },
    {
        "vol": "zty_lun8",
        "name": "zty-doradoV6",
        "lun": 14,
        "hgroup": None
    },
    {
        "vol": "zty_lun7",
        "name": "zty-doradoV6",
        "lun": 15,
        "hgroup": None
    },
    {
        "vol": "zty_lun9",
        "name": "zty-doradoV6",
        "lun": 16,
        "hgroup": None
    },
    {
        "vol": "Volume-Group/voltest005",
        "name": "hosttest",
        "lun": 254,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest005",
        "name": "host",
        "lun": 254,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest001",
        "name": "host",
        "lun": 253,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest001",
        "name": "hosttest",
        "lun": 253,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest002",
        "name": "host",
        "lun": 252,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest002",
        "name": "hosttest",
        "lun": 252,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest003",
        "name": "host",
        "lun": 251,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest003",
        "name": "hosttest",
        "lun": 251,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest004",
        "name": "hosttest",
        "lun": 250,
        "hgroup": "HGTest"
    },
    {
        "vol": "Volume-Group/voltest004",
        "name": "host",
        "lun": 250,
        "hgroup": "HGTest"
    },
    {
        "vol": "homelab-pso-db_0000000001-u",
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "lun": 4,
        "hgroup": None
    },
    {
        "vol": "Volume-Group/voltest001",
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "hswin4102",
        "name": "zhilong-host0000002130",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "tangxuan/tt001",
        "name": "host135",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "hswin",
        "name": "CL-Test1",
        "lun": 1,
        "hgroup": None
    },
    {
        "vol": "homelab-pso-db_0000000000-u",
        "name": "zhilong-host0000002130",
        "lun": 2,
        "hgroup": None
    },
    {
        "vol": "nc::136_connect",
        "name": "hosttest",
        "lun": 1,
        "hgroup": None
    }
]
HGROUP_CONNECT_INFO = [
    {
        "vol": "QIB1",
        "name": "QIB",
        "lun": 254
    },
    {
        "vol": "QIB2",
        "name": "QIB",
        "lun": 253
    },
    {
        "vol": "Volume-Group/voltest005",
        "name": "HGTest",
        "lun": 254
    },
    {
        "vol": "Volume-Group/voltest001",
        "name": "HGTest",
        "lun": 253
    },
    {
        "vol": "Volume-Group/voltest002",
        "name": "HGTest",
        "lun": 252
    },
    {
        "vol": "Volume-Group/voltest003",
        "name": "HGTest",
        "lun": 251
    },
    {
        "vol": "Volume-Group/voltest004",
        "name": "HGTest",
        "lun": 250
    },
    {
        "vol": "homelab-pso-db_0000000002",
        "name": "NewTest",
        "lun": 254
    },
    {
        "vol": "yzw_test0",
        "name": "zhilong-hg",
        "lun": 254
    }
]
volume_data = [
    {'native_volume_id': 'oracl_ail', 'name': 'oracl_ail',
     'total_capacity': 2156324555567, 'used_capacity': 116272464547,
     'free_capacity': 2040052091020, 'storage_id': '12345', 'status': 'normal',
     'type': 'thin'},
    {'native_volume_id': 'wxt1', 'name': 'wxt1', 'total_capacity': 1073741824,
     'used_capacity': 0, 'free_capacity': 1073741824, 'storage_id': '12345',
     'status': 'normal', 'type': 'thin'}]
storage_data = {
    'model': 'FA-m20r2', 'total_capacity': 122276719419392,
    'raw_capacity': 3083686627641, 'used_capacity': 324829845504,
    'free_capacity': 121951889573888, 'vendor': 'PURE', 'name': 'pure01',
    'serial_number': 'dlmkk15xcfdf4v5', 'firmware_version': '4.6.7',
    'status': 'normal'}
list_alert_data = [
    {'occur_time': 1526122521000, 'alert_id': 135, 'severity': 'Warning',
     'category': 'Fault', 'location': 'ct1.eth0', 'type': 'EquipmentAlarm',
     'resource_type': 'Storage', 'alert_name': 'failure',
     'match_key': '7f1de29e6da19d22b51c68001e7e0e54',
     'description': '(hardware:ct1.eth0): failure'},
    {'occur_time': 1526122521000, 'alert_id': 10088786, 'severity': 'Warning',
     'category': 'Fault', 'location': 'ct1.ntpd', 'type': 'EquipmentAlarm',
     'resource_type': 'Storage', 'alert_name': 'server unreachable',
     'match_key': 'b35a0c63d4cd82256b95f51522c6ba32',
     'description': '(process:ct1.ntpd): server unreachable'}]
parse_alert_data = {
    'alert_id': '30007589', 'severity': 'Informational', 'category': 'Fault',
    'occur_time': 1644833673861, 'description': '(None:cto): server error',
    'location': 'cto', 'type': 'EquipmentAlarm', 'resource_type': 'Storage',
    'alert_name': 'cto.server error', 'sequence_number': '30007589',
    'match_key': '11214c87bb6efcf8dc2aed1095271774'}
controllers_data = [
    {'name': 'CT0', 'status': 'unknown', 'soft_version': '5.3.0',
     'storage_id': '12345', 'native_controller_id': 'CT0', 'location': 'CT0'},
    {'name': 'CT1', 'status': 'unknown', 'soft_version': '5.3.0',
     'storage_id': '12345', 'native_controller_id': 'CT1', 'location': 'CT1'}]
disk_data = [
    {'name': 'CH0.BAY1', 'physical_type': 'ssd', 'status': 'normal',
     'storage_id': '12345', 'capacity': 1027895542547, 'speed': None,
     'model': None, 'serial_number': None, 'native_disk_id': 'CH0.BAY1',
     'location': 'CH0.BAY1', 'manufacturer': 'PURE', 'firmware': ''},
    {'name': 'CH0.BAY2', 'physical_type': 'ssd', 'status': 'normal',
     'storage_id': '12345', 'capacity': 1027895542547, 'speed': None,
     'model': None, 'serial_number': None, 'native_disk_id': 'CH0.BAY2',
     'location': 'CH0.BAY2', 'manufacturer': 'PURE', 'firmware': ''},
    {'name': 'CH0.BAY3', 'physical_type': 'ssd', 'status': 'normal',
     'storage_id': '12345', 'capacity': 1027895542547, 'speed': None,
     'model': None, 'serial_number': None, 'native_disk_id': 'CH0.BAY3',
     'location': 'CH0.BAY3', 'manufacturer': 'PURE', 'firmware': ''}]
port_data = [
    {'type': 'fc', 'name': 'CTO.FC1', 'native_port_id': 'CTO.FC1',
     'storage_id': '12345', 'location': 'CTO.FC1',
     'connection_status': 'disconnected', 'speed': 0,
     'health_status': 'normal', 'wwn': '43:dd:ff:45:gg:g4:rt:y',
     'mac_address': None, 'logical_type': 'management',
     'ipv4_mask': '100.12.253.23:4563', 'ipv4': '45233662jksndj'},
    {'type': 'eth', 'name': 'CTO.ETH15', 'native_port_id': 'CTO.ETH15',
     'storage_id': '12345', 'location': 'CTO.ETH15',
     'connection_status': 'connected', 'speed': 1000000,
     'health_status': 'normal', 'wwn': 'iqn.2016-11-01.com.pure',
     'mac_address': None, 'logical_type': 'management',
     'ipv4_mask': '100.12.253.23:4563', 'ipv4': '45233662jksndj'}]
initiator_data = [
    {'native_storage_host_initiator_id': 'iqn.1996-04.de.suse:01:ca9f3bcaf47',
     'native_storage_host_id': 'host',
     'name': 'iqn.1996-04.de.suse:01:ca9f3bcaf47', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.1996-04.de.suse:01:ca9f3bcaf47',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'iqn.1991-05.com.microsoft:win3',
     'native_storage_host_id': 'huhuitest',
     'name': 'iqn.1991-05.com.microsoft:win3', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.1991-05.com.microsoft:win3',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:2C:95:24',
     'native_storage_host_id': 'windows223', 'name': '21:00:00:24:FF:2C:95:24',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:00:24:FF:2C:95:24',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:2C:95:25',
     'native_storage_host_id': 'windows223', 'name': '21:00:00:24:FF:2C:95:25',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:00:24:FF:2C:95:25',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '10:00:00:00:C9:D5:BC:06',
     'native_storage_host_id': 'CL-B06-RH2288HV3-8-44-157-33',
     'name': '10:00:00:00:C9:D5:BC:06', 'type': 'fc', 'status': 'unknown',
     'wwn': '10:00:00:00:C9:D5:BC:06', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '10:00:00:00:C9:D5:BC:07',
     'native_storage_host_id': 'CL-B06-RH2288HV3-8-44-157-33',
     'name': '10:00:00:00:C9:D5:BC:07', 'type': 'fc', 'status': 'unknown',
     'wwn': '10:00:00:00:C9:D5:BC:07', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:76:D0:CC',
     'native_storage_host_id': 'CL-C21-RH5885HV3-8-44-165-22',
     'name': '21:00:00:24:FF:76:D0:CC', 'type': 'fc', 'status': 'unknown',
     'wwn': '21:00:00:24:FF:76:D0:CC', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:76:D0:CD',
     'native_storage_host_id': 'CL-C21-RH5885HV3-8-44-165-22',
     'name': '21:00:00:24:FF:76:D0:CD', 'type': 'fc', 'status': 'unknown',
     'wwn': '21:00:00:24:FF:76:D0:CD', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'iqn.1996-04.de.suse:01:66bf70288332',
     'native_storage_host_id': 'test-1s',
     'name': 'iqn.1996-04.de.suse:01:66bf70288332', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.1996-04.de.suse:01:66bf70288332',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:34:80:0D:6E:7A:DE',
     'native_storage_host_id': 'QIB', 'name': '21:00:34:80:0D:6E:7A:DE',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:34:80:0D:6E:7A:DE',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:34:80:0D:6E:7A:DF',
     'native_storage_host_id': 'QIB', 'name': '21:00:34:80:0D:6E:7A:DF',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:34:80:0D:6E:7A:DF',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '20:09:00:02:D2:93:7E:9F',
     'native_storage_host_id': 'v6-8-44-128-21',
     'name': '20:09:00:02:D2:93:7E:9F', 'type': 'fc', 'status': 'unknown',
     'wwn': '20:09:00:02:D2:93:7E:9F', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '20:19:00:02:D2:93:7E:9F',
     'native_storage_host_id': 'v6-8-44-128-21',
     'name': '20:19:00:02:D2:93:7E:9F', 'type': 'fc', 'status': 'unknown',
     'wwn': '20:19:00:02:D2:93:7E:9F', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'iqn.1994-05.com.redhat:1a9eaa70b558',
     'native_storage_host_id': 'host135',
     'name': 'iqn.1994-05.com.redhat:1a9eaa70b558', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.1994-05.com.redhat:1a9eaa70b558',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '22:00:CC:05:77:7C:3E:DF',
     'native_storage_host_id': 'zty-doradoV6',
     'name': '22:00:CC:05:77:7C:3E:DF', 'type': 'fc', 'status': 'unknown',
     'wwn': '22:00:CC:05:77:7C:3E:DF', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '22:10:CC:05:77:7C:3E:DF',
     'native_storage_host_id': 'zty-doradoV6',
     'name': '22:10:CC:05:77:7C:3E:DF', 'type': 'fc', 'status': 'unknown',
     'wwn': '22:10:CC:05:77:7C:3E:DF', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'iqn.1994-05.com.redhat:71cfb5b97df',
     'native_storage_host_id': 'CL-Test1',
     'name': 'iqn.1994-05.com.redhat:71cfb5b97df', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.1994-05.com.redhat:71cfb5b97df',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:76:D0:CF',
     'native_storage_host_id': 'CL-Test1', 'name': '21:00:00:24:FF:76:D0:CF',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:00:24:FF:76:D0:CF',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'iqn.1994-05.com.redhat:80c412848b94',
     'native_storage_host_id': 'host137',
     'name': 'iqn.1994-05.com.redhat:80c412848b94', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.1994-05.com.redhat:80c412848b94',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:40:27:2A',
     'native_storage_host_id': 'zty-windows',
     'name': '21:00:00:24:FF:40:27:2A', 'type': 'fc', 'status': 'unknown',
     'wwn': '21:00:00:24:FF:40:27:2A', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:40:27:2B',
     'native_storage_host_id': 'zty-windows',
     'name': '21:00:00:24:FF:40:27:2B', 'type': 'fc', 'status': 'unknown',
     'wwn': '21:00:00:24:FF:40:27:2B', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:53:51:F0',
     'native_storage_host_id': 'hswin41', 'name': '21:00:00:24:FF:53:51:F0',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:00:24:FF:53:51:F0',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': '21:00:00:24:FF:53:51:F1',
     'native_storage_host_id': 'hswin41', 'name': '21:00:00:24:FF:53:51:F1',
     'type': 'fc', 'status': 'unknown', 'wwn': '21:00:00:24:FF:53:51:F1',
     'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'nqn.2021-12.org.nvmexpress.mytest',
     'native_storage_host_id': 'zhilong-host0000002130',
     'name': 'nqn.2021-12.org.nvmexpress.mytest', 'type': 'nvme-of',
     'status': 'unknown', 'wwn': 'nqn.2021-12.org.nvmexpress.mytest',
     'storage_id': '12345'}]
host_data = [
    {'name': 'host', 'storage_id': '12345', 'native_storage_host_id': 'host',
     'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'wxth', 'storage_id': '12345', 'native_storage_host_id': 'wxth',
     'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'huhuitest', 'storage_id': '12345',
     'native_storage_host_id': 'huhuitest', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'testGroup', 'storage_id': '12345',
                           'native_storage_host_id': 'testGroup',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'windows223', 'storage_id': '12345',
     'native_storage_host_id': 'windows223', 'os_type': 'Unknown',
     'status': 'normal'},
    {'name': 'CL-B06-RH2288HV3-8-44-157-33', 'storage_id': '12345',
     'native_storage_host_id': 'CL-B06-RH2288HV3-8-44-157-33',
     'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'CL-C21-RH5885HV3-8-44-165-22', 'storage_id': '12345',
     'native_storage_host_id': 'CL-C21-RH5885HV3-8-44-165-22',
     'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'test-1s', 'storage_id': '12345',
     'native_storage_host_id': 'test-1s', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'rhev125', 'storage_id': '12345',
                           'native_storage_host_id': 'rhev125',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'QIB', 'storage_id': '12345', 'native_storage_host_id': 'QIB',
     'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'v6-8-44-128-21', 'storage_id': '12345',
     'native_storage_host_id': 'v6-8-44-128-21', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'host135', 'storage_id': '12345',
                           'native_storage_host_id': 'host135',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'zty-doradoV6', 'storage_id': '12345',
     'native_storage_host_id': 'zty-doradoV6', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'CL-Test1', 'storage_id': '12345',
                           'native_storage_host_id': 'CL-Test1',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'host137', 'storage_id': '12345',
     'native_storage_host_id': 'host137', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'hsesxi', 'storage_id': '12345',
                           'native_storage_host_id': 'hsesxi',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'zty-windows', 'storage_id': '12345',
     'native_storage_host_id': 'zty-windows', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'hosttest', 'storage_id': '12345',
                           'native_storage_host_id': 'hosttest',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'hswin41', 'storage_id': '12345',
     'native_storage_host_id': 'hswin41', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'ztj201', 'storage_id': '12345',
                           'native_storage_host_id': 'ztj201',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'test123', 'storage_id': '12345',
     'native_storage_host_id': 'test123', 'os_type': 'Unknown',
     'status': 'normal'}, {'name': 'zsytest', 'storage_id': '12345',
                           'native_storage_host_id': 'zsytest',
                           'os_type': 'Unknown', 'status': 'normal'},
    {'name': 'zhilong-host0000002130', 'storage_id': '12345',
     'native_storage_host_id': 'zhilong-host0000002130', 'os_type': 'AIX',
     'status': 'normal'}]
host_group_data = {
    'storage_host_groups':
        [
            {'native_storage_host_group_id': 'podgroup', 'name': 'podgroup',
             'storage_id': '12345'},
            {'native_storage_host_group_id': 'NewTest', 'name': 'NewTest',
             'storage_id': '12345'},
            {'native_storage_host_group_id': 'QIB', 'name': 'QIB',
             'storage_id': '12345'},
            {'native_storage_host_group_id': 'HGTest', 'name': 'HGTest',
             'storage_id': '12345'}],
    'storage_host_grp_host_rels': [
        {'native_storage_host_group_id': 'QIB', 'storage_id': '12345',
         'native_storage_host_id': 'QIB'},
        {'native_storage_host_group_id': 'HGTest', 'storage_id': '12345',
         'native_storage_host_id': 'host'},
        {'native_storage_host_group_id': 'HGTest', 'storage_id': '12345',
         'native_storage_host_id': 'hosttest'}]
}
volume_group_data = {
    'volume_groups':
        [
            {'name': 'vvol-pure-VM1-072e131e-vg', 'storage_id': '12345',
             'native_volume_group_id': 'vvol-pure-VM1-072e131e-vg'},
            {'name': 'vvol-pure-vm2-e48a0ef8-vg', 'storage_id': '12345',
             'native_volume_group_id': 'vvol-pure-vm2-e48a0ef8-vg'},
            {'name': 'vvol-pure-vm3-65d42a4e-vg', 'storage_id': '12345',
             'native_volume_group_id': 'vvol-pure-vm3-65d42a4e-vg'},
            {'name': 'vvol-pure-vm4-17c41971-vg', 'storage_id': '12345',
             'native_volume_group_id': 'vvol-pure-vm4-17c41971-vg'},
            {'name': 'Volume-Group', 'storage_id': '12345',
             'native_volume_group_id': 'Volume-Group'},
            {'name': 'test1', 'storage_id': '12345',
             'native_volume_group_id': 'test1'},
            {'name': 'tangxuan', 'storage_id': '12345',
             'native_volume_group_id': 'tangxuan'}
        ],
    'vol_grp_vol_rels': [
        {'storage_id': '12345', 'native_volume_group_id': 'Volume-Group',
         'native_volume_id': 'Volume-Group/voltest001'},
        {'storage_id': '12345', 'native_volume_group_id': 'Volume-Group',
         'native_volume_id': 'Volume-Group/voltest002'},
        {'storage_id': '12345', 'native_volume_group_id': 'Volume-Group',
         'native_volume_id': 'Volume-Group/voltest003'},
        {'storage_id': '12345', 'native_volume_group_id': 'Volume-Group',
         'native_volume_id': 'Volume-Group/voltest004'},
        {'storage_id': '12345', 'native_volume_group_id': 'Volume-Group',
         'native_volume_id': 'Volume-Group/voltest005'}]
}
views_data = [
    {'native_masking_view_id': 'QIBQIB1', 'name': 'QIBQIB1',
     'native_storage_host_group_id': 'QIB', 'native_volume_id': 'QIB1',
     'storage_id': '12345'},
    {'native_masking_view_id': 'QIBQIB2', 'name': 'QIBQIB2',
     'native_storage_host_group_id': 'QIB', 'native_volume_id': 'QIB2',
     'storage_id': '12345'},
    {'native_masking_view_id': 'HGTestVolume-Group/voltest005',
     'name': 'HGTestVolume-Group/voltest005',
     'native_storage_host_group_id': 'HGTest',
     'native_volume_id': 'Volume-Group/voltest005', 'storage_id': '12345'},
    {'native_masking_view_id': 'HGTestVolume-Group/voltest001',
     'name': 'HGTestVolume-Group/voltest001',
     'native_storage_host_group_id': 'HGTest',
     'native_volume_id': 'Volume-Group/voltest001', 'storage_id': '12345'},
    {'native_masking_view_id': 'HGTestVolume-Group/voltest002',
     'name': 'HGTestVolume-Group/voltest002',
     'native_storage_host_group_id': 'HGTest',
     'native_volume_id': 'Volume-Group/voltest002', 'storage_id': '12345'},
    {'native_masking_view_id': 'HGTestVolume-Group/voltest003',
     'name': 'HGTestVolume-Group/voltest003',
     'native_storage_host_group_id': 'HGTest',
     'native_volume_id': 'Volume-Group/voltest003', 'storage_id': '12345'},
    {'native_masking_view_id': 'HGTestVolume-Group/voltest004',
     'name': 'HGTestVolume-Group/voltest004',
     'native_storage_host_group_id': 'HGTest',
     'native_volume_id': 'Volume-Group/voltest004', 'storage_id': '12345'},
    {'native_masking_view_id': 'NewTesthomelab-pso-db_0000000002',
     'name': 'NewTesthomelab-pso-db_0000000002',
     'native_storage_host_group_id': 'NewTest',
     'native_volume_id': 'homelab-pso-db_0000000002', 'storage_id': '12345'},
    {'native_masking_view_id': 'zhilong-hgyzw_test0',
     'name': 'zhilong-hgyzw_test0',
     'native_storage_host_group_id': 'zhilong-hg',
     'native_volume_id': 'yzw_test0', 'storage_id': '12345'},
    {'native_masking_view_id': 'huhuitestNonehuhuitest',
     'name': 'huhuitestNonehuhuitest', 'native_storage_host_id': 'huhuitest',
     'native_volume_id': 'huhuitest', 'storage_id': '12345'},
    {'native_masking_view_id': 'wxthNonetest', 'name': 'wxthNonetest',
     'native_storage_host_id': 'wxth', 'native_volume_id': 'test',
     'storage_id': '12345'}, {'native_masking_view_id': 'testGroupNonetest',
                              'name': 'testGroupNonetest',
                              'native_storage_host_id': 'testGroup',
                              'native_volume_id': 'test',
                              'storage_id': '12345'},
    {'native_masking_view_id': 'windows223Nonewin2016_223',
     'name': 'windows223Nonewin2016_223',
     'native_storage_host_id': 'windows223', 'native_volume_id': 'win2016_223',
     'storage_id': '12345'}, {
        'native_masking_view_id':
            'CL-C21-RH5885HV3-8-44-165-22Nonepure-protocol-endpoint',
        'name': 'CL-C21-RH5885HV3-8-44-165-22Nonepure-protocol-endpoint',
        'native_storage_host_id': 'CL-C21-RH5885HV3-8-44-165-22',
        'native_volume_id': 'pure-protocol-endpoint', 'storage_id': '12345'}, {
        'native_masking_view_id':
            'CL-C21-RH5885HV3-8-44-165-22NoneCL_VOLUME_1_remote',
        'name': 'CL-C21-RH5885HV3-8-44-165-22NoneCL_VOLUME_1_remote',
        'native_storage_host_id': 'CL-C21-RH5885HV3-8-44-165-22',
        'native_volume_id': 'CL_VOLUME_1_remote', 'storage_id': '12345'},
    {'native_masking_view_id': 'test-1sNonelun-test1s',
     'name': 'test-1sNonelun-test1s', 'native_storage_host_id': 'test-1s',
     'native_volume_id': 'lun-test1s', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Noneyzw_iotest',
     'name': 'host135Noneyzw_iotest', 'native_storage_host_id': 'host135',
     'native_volume_id': 'yzw_iotest', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000003',
     'name': 'host137Nonehomelab-pso-db_0000000003',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000003', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000009',
     'name': 'host135Nonehomelab-pso-db_0000000009',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000009', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000012',
     'name': 'host135Nonehomelab-pso-db_0000000012',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000012', 'storage_id': '12345'},
    {'native_masking_view_id': 'v6-8-44-128-21Nonev6-8-44-128-21',
     'name': 'v6-8-44-128-21Nonev6-8-44-128-21',
     'native_storage_host_id': 'v6-8-44-128-21',
     'native_volume_id': 'v6-8-44-128-21', 'storage_id': '12345'},
    {'native_masking_view_id': 'v6-8-44-128-21NoneV6-8-44-128-21-002',
     'name': 'v6-8-44-128-21NoneV6-8-44-128-21-002',
     'native_storage_host_id': 'v6-8-44-128-21',
     'native_volume_id': 'V6-8-44-128-21-002', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000007',
     'name': 'host137Nonehomelab-pso-db_0000000007',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000007', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000010',
     'name': 'host135Nonehomelab-pso-db_0000000010',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000010', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000013',
     'name': 'host137Nonehomelab-pso-db_0000000013',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000013', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000000',
     'name': 'host135Nonehomelab-pso-db_0000000000',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000000', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000001',
     'name': 'host137Nonehomelab-pso-db_0000000001',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000001', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000016',
     'name': 'host137Nonehomelab-pso-db_0000000016',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000016', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000018',
     'name': 'host135Nonehomelab-pso-db_0000000018',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000018', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000015',
     'name': 'host135Nonehomelab-pso-db_0000000015',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000015', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000020',
     'name': 'host137Nonehomelab-pso-db_0000000020',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000020', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000021',
     'name': 'host135Nonehomelab-pso-db_0000000021',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000021', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000022',
     'name': 'host137Nonehomelab-pso-db_0000000022',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000022', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000019',
     'name': 'host135Nonehomelab-pso-db_0000000019',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000019', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000026',
     'name': 'host137Nonehomelab-pso-db_0000000026',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000026', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonehomelab-pso-db_0000000028',
     'name': 'host135Nonehomelab-pso-db_0000000028',
     'native_storage_host_id': 'host135',
     'native_volume_id': 'homelab-pso-db_0000000028', 'storage_id': '12345'},
    {'native_masking_view_id': 'host137Nonehomelab-pso-db_0000000024',
     'name': 'host137Nonehomelab-pso-db_0000000024',
     'native_storage_host_id': 'host137',
     'native_volume_id': 'homelab-pso-db_0000000024', 'storage_id': '12345'},
    {'native_masking_view_id': 'hsesxiNonehsboot', 'name': 'hsesxiNonehsboot',
     'native_storage_host_id': 'hsesxi', 'native_volume_id': 'hsboot',
     'storage_id': '12345'}, {'native_masking_view_id': 'hsesxiNonehszdata',
                              'name': 'hsesxiNonehszdata',
                              'native_storage_host_id': 'hsesxi',
                              'native_volume_id': 'hszdata',
                              'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun16',
     'name': 'zty-doradoV6Nonezty_lun16',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun16',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun15',
     'name': 'zty-doradoV6Nonezty_lun15',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun15',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun13',
     'name': 'zty-doradoV6Nonezty_lun13',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun13',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun11',
     'name': 'zty-doradoV6Nonezty_lun11',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun11',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun14',
     'name': 'zty-doradoV6Nonezty_lun14',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun14',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun2',
     'name': 'zty-doradoV6Nonezty_lun2',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun2',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun5',
     'name': 'zty-doradoV6Nonezty_lun5',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun5',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun4',
     'name': 'zty-doradoV6Nonezty_lun4',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun4',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun1',
     'name': 'zty-doradoV6Nonezty_lun1',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun1',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun3',
     'name': 'zty-doradoV6Nonezty_lun3',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun3',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun6',
     'name': 'zty-doradoV6Nonezty_lun6',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun6',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun12',
     'name': 'zty-doradoV6Nonezty_lun12',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun12',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun10',
     'name': 'zty-doradoV6Nonezty_lun10',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun10',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun8',
     'name': 'zty-doradoV6Nonezty_lun8',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun8',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun7',
     'name': 'zty-doradoV6Nonezty_lun7',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun7',
     'storage_id': '12345'},
    {'native_masking_view_id': 'zty-doradoV6Nonezty_lun9',
     'name': 'zty-doradoV6Nonezty_lun9',
     'native_storage_host_id': 'zty-doradoV6', 'native_volume_id': 'zty_lun9',
     'storage_id': '12345'}, {
        'native_masking_view_id':
            'CL-B06-RH2288HV3-8-44-157-33Nonehomelab-pso-db_0000000001-u',
        'name': 'CL-B06-RH2288HV3-8-44-157-33Nonehomelab-pso-db_0000000001-u',
        'native_storage_host_id': 'CL-B06-RH2288HV3-8-44-157-33',
        'native_volume_id': 'homelab-pso-db_0000000001-u',
        'storage_id': '12345'}, {
        'native_masking_view_id':
            'CL-B06-RH2288HV3-8-44-157-33NoneVolume-Group/voltest001',
        'name': 'CL-B06-RH2288HV3-8-44-157-33NoneVolume-Group/voltest001',
        'native_storage_host_id': 'CL-B06-RH2288HV3-8-44-157-33',
        'native_volume_id': 'Volume-Group/voltest001', 'storage_id': '12345'},
    {'native_masking_view_id': 'zhilong-host0000002130Nonehswin4102',
     'name': 'zhilong-host0000002130Nonehswin4102',
     'native_storage_host_id': 'zhilong-host0000002130',
     'native_volume_id': 'hswin4102', 'storage_id': '12345'},
    {'native_masking_view_id': 'host135Nonetangxuan/tt001',
     'name': 'host135Nonetangxuan/tt001', 'native_storage_host_id': 'host135',
     'native_volume_id': 'tangxuan/tt001', 'storage_id': '12345'},
    {'native_masking_view_id': 'CL-Test1Nonehswin',
     'name': 'CL-Test1Nonehswin', 'native_storage_host_id': 'CL-Test1',
     'native_volume_id': 'hswin', 'storage_id': '12345'}, {
        'native_masking_view_id':
            'zhilong-host0000002130Nonehomelab-pso-db_0000000000-u',
        'name': 'zhilong-host0000002130Nonehomelab-pso-db_0000000000-u',
        'native_storage_host_id': 'zhilong-host0000002130',
        'native_volume_id': 'homelab-pso-db_0000000000-u',
        'storage_id': '12345'},
    {'native_masking_view_id': 'hosttestNonenc::136_connect',
     'name': 'hosttestNonenc::136_connect',
     'native_storage_host_id': 'hosttest',
     'native_volume_id': 'nc::136_connect', 'storage_id': '12345'}]
storage_resource_metrics = {
    constants.ResourceType.STORAGE: consts.STORAGE_CAP,
}
volume_resource_metrics = {
    constants.ResourceType.VOLUME: consts.VOLUME_CAP
}
drive_metrics = [
    {
        "writes_per_sec": 0,
        "output_per_sec": 0,
        "usec_per_write_op": 0,
        "local_queue_usec_per_op": 0,
        "time": "2022-04-25T02:24:46Z",
        "reads_per_sec": 0,
        "input_per_sec": 0,
        "usec_per_read_op": 0,
        "queue_depth": 0
    }, {
        "writes_per_sec": 1856,
        "output_per_sec": 0,
        "usec_per_write_op": 653021.569741,
        "local_queue_usec_per_op": 43158,
        "time": "2022-04-25T02:25:46Z",
        "reads_per_sec": 0,
        "input_per_sec": 0,
        "usec_per_read_op": 5360,
        "queue_depth": 0
    }]
volume_metrics_info = [{
    "writes_per_sec": 1864,
    "name": "136_connect",
    "usec_per_write_op": 46200000,
    "output_per_sec": 0,
    "reads_per_sec": 0,
    "input_per_sec": 5620302,
    "time": "2022-04-12T02:12:16Z",
    "usec_per_read_op": 0
}, {
    "writes_per_sec": 1864,
    "name": "136_connect",
    "usec_per_write_op": 46200000,
    "output_per_sec": 0,
    "reads_per_sec": 0,
    "input_per_sec": 5620302,
    "time": "2022-04-12T02:13:16Z",
    "usec_per_read_op": 0
}]


def create_driver():
    RestHandler.login = mock.Mock(
        return_value={None})
    return PureFlashArrayDriver(**ACCESS_INFO)


class test_PureFlashArrayDriver(TestCase):
    driver = create_driver()

    def test_init(self):
        RestHandler.login = mock.Mock(
            return_value={""})
        PureFlashArrayDriver(**ACCESS_INFO)

    def test_list_volumes(self):
        RestHandler.get_volumes = mock.Mock(
            side_effect=[volumes_info])
        volume = self.driver.list_volumes(context)
        self.assertEqual(volume, volume_data)

    def test_get_storage(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[storage_info, hardware_info, drive_info,
                         storage_id_info, controllers_info])
        storage_object = self.driver.get_storage(context)
        self.assertEqual(storage_object, storage_data)

    def test_list_alerts(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[alerts_info])
        list_alerts = self.driver.list_alerts(context)
        self.assertEqual(list_alerts, list_alert_data)

    def test_parse_alert(self):
        parse_alert = self.driver.parse_alert(context, parse_alert_info)
        parse_alert_data['occur_time'] = parse_alert.get('occur_time')
        self.assertDictEqual(parse_alert, parse_alert_data)

    def test_list_controllers(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[controllers_info, hardware_info])
        list_controllers = self.driver.list_controllers(context)
        self.assertListEqual(list_controllers, controllers_data)

    def test_list_disks(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[hardware_info, drive_info])
        list_disks = self.driver.list_disks(context)
        self.assertListEqual(list_disks, disk_data)

    def test_list_ports(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[port_network_info, port_info, hardware_info])
        list_ports = self.driver.list_ports(context)
        self.assertListEqual(list_ports, port_data)

    def test_list_storage_pools(self):
        list_storage_pools = self.driver.list_storage_pools(context)
        self.assertEqual(list_storage_pools, [])

    def test_reset_connection(self):
        RestHandler.logout = mock.Mock(side_effect=None)
        RestHandler.login = mock.Mock(side_effect=None)
        username = None
        try:
            self.driver.reset_connection(context)
        except Exception as e:
            LOG.error("test_reset_connection error: %s", six.text_type(e))
            username = reset_connection_info.get('username')
        self.assertEqual(username, None)

    def test_list_storage_host_initiators(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[hosts_info])
        hosts = self.driver.list_storage_host_initiators(context)
        self.assertEqual(hosts, initiator_data)

    def test_list_storage_hosts(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[HOSTS_PERSONALITY_INFO])
        hosts = self.driver.list_storage_hosts(context)
        self.assertListEqual(hosts, host_data)

    def test_list_storage_host_groups(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[HGROUP_INFO])
        hgroup = self.driver.list_storage_host_groups(context)
        self.assertDictEqual(hgroup, host_group_data)

    def test_list_volume_groups(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[VOLUME_GROUP_INFO])
        v_group = self.driver.list_volume_groups(context)
        self.assertDictEqual(v_group, volume_group_data)

    def test_list_masking_views(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[HGROUP_CONNECT_INFO, HOSTS_CONNECT_INFO])
        views = self.driver.list_masking_views(context)
        self.assertListEqual(views, views_data)

    def test_collect_perf_metrics(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[storage_id_info, drive_metrics])
        localtime = time.mktime(time.localtime()) * units.k
        storage_id = 12345
        start_time = localtime - 1000 * 60 * 60 * 24 * 364
        end_time = localtime
        metrics = self.driver.collect_perf_metrics(
            context, storage_id, storage_resource_metrics, start_time,
            end_time)
        storage_metrics = [
            constants.metric_struct(
                name='iops',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'IOPS'},
                values={1650853440000: 0, 1650853500000: 1856}
            ),
            constants.metric_struct(
                name='readIops',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'IOPS'},
                values={1650853440000: 0, 1650853500000: 0}
            ),
            constants.metric_struct(
                name='writeIops',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'IOPS'},
                values={1650853440000: 0, 1650853500000: 1856}
            ),
            constants.metric_struct(
                name='throughput',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'MB/s'},
                values={1650853440000: 0.0, 1650853500000: 0.0}
            ),
            constants.metric_struct(
                name='readThroughput',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'MB/s'},
                values={1650853440000: 0.0, 1650853500000: 0.0}
            ),
            constants.metric_struct(
                name='writeThroughput',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'MB/s'},
                values={1650853440000: 0.0, 1650853500000: 0.0}
            ),
            constants.metric_struct(
                name='readResponseTime',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'ms'},
                values={1650853440000: 0.0, 1650853500000: 5.36}
            ),
            constants.metric_struct(
                name='writeResponseTime',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'storage',
                    'resource_id': 'dlmkk15xcfdf4v5',
                    'resource_name': 'pure01',
                    'type': 'RAW',
                    'unit': 'ms'},
                values={1650853440000: 0.0, 1650853500000: 653.022}
            )
        ]
        self.assertListEqual(metrics, storage_metrics)
        volume_metrics = [
            constants.metric_struct(
                name='iops',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'IOPS'},
                values={1649729520000: 1864, 1649729580000: 1864}
            ),
            constants.metric_struct(
                name='readIops',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'IOPS'},
                values={1649729520000: 0, 1649729580000: 0}
            ),
            constants.metric_struct(
                name='writeIops',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'IOPS'},
                values={1649729520000: 1864, 1649729580000: 1864}
            ),
            constants.metric_struct(
                name='throughput',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'MB/s'},
                values={1649729520000: 5.36, 1649729580000: 5.36}
            ),
            constants.metric_struct(
                name='readThroughput',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'MB/s'},
                values={1649729520000: 0.0, 1649729580000: 0.0}
            ),
            constants.metric_struct(
                name='writeThroughput',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'MB/s'},
                values={1649729520000: 5.36, 1649729580000: 5.36}
            ),
            constants.metric_struct(
                name='readResponseTime',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'ms'},
                values={1649729520000: 0.0, 1649729580000: 0.0}
            ),
            constants.metric_struct(
                name='writeResponseTime',
                labels={
                    'storage_id': 12345,
                    'resource_type': 'volume',
                    'resource_id': '136_connect',
                    'resource_name': '136_connect',
                    'type': 'RAW',
                    'unit': 'ms'},
                values={1649729520000: 46200.0, 1649729580000: 46200.0}
            )
        ]
        RestHandler.rest_call = mock.Mock(
            side_effect=[volume_metrics_info])
        metrics = self.driver.collect_perf_metrics(
            context, storage_id, volume_resource_metrics, start_time,
            end_time)
        self.assertListEqual(metrics, volume_metrics)

    def test_get_capabilities(self):
        err = None
        try:
            self.driver.get_capabilities(context)
        except Exception as e:
            err = six.text_type(e)
            LOG.error("test_get_capabilities error: %s", err)
        self.assertEqual(err, None)

    def test_get_latest_perf_timestamp(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[drive_metrics])
        timestamp = self.driver.get_latest_perf_timestamp(context)
        times = 1650853500000
        self.assertEqual(timestamp, times)
