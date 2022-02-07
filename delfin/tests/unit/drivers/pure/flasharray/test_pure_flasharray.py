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
from unittest import TestCase, mock

import six
from oslo_log import log

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.pure.flasharray.rest_handler import RestHandler
from delfin.drivers.pure.flasharray.pure_flasharray import PureFlashArrayDriver
LOG = log.getLogger(__name__)

ACCESS_INFO = {
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
HOSTS_ALL_INFO = [
    {
        "host_wwn": None,
        "name": "host",
        "host_iqn": "iqn.1996-04.de.suse:01:ca9f3bcaf47",
        "host_nqn": None,
        "hgroup": None,
        "vol": "oracle-oltp-1",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": None,
        "name": "huhuitest",
        "host_iqn": "iqn.1991-05.com.microsoft:win3",
        "host_nqn": None,
        "hgroup": None,
        "vol": "huhuitest",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "21000024FF2C9524",
        "name": "windows223",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "win2016_223",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "21000024FF2C9525",
        "name": "windows223",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "win2016_223",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "21000024FF76D0CC",
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "pure-protocol-endpoint",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "21000024FF76D0CD",
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "pure-protocol-endpoint",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "21000024FF76D0CC",
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "CL_VOLUME_1_remote",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": "21000024FF76D0CD",
        "name": "CL-C21-RH5885HV3-8-44-165-22",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "CL_VOLUME_1_remote",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": None,
        "name": "test-1s",
        "host_iqn": "iqn.1996-04.de.suse:01:66bf70288332",
        "host_nqn": None,
        "hgroup": None,
        "vol": "lun-test1s",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "210034800D6E7ADE",
        "name": "QIB",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": "QIB",
        "vol": "QIB1",
        "target_port": [],
        "lun": 254
    },
    {
        "host_wwn": "210034800D6E7ADF",
        "name": "QIB",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": "QIB",
        "vol": "QIB1",
        "target_port": [],
        "lun": 254
    },
    {
        "host_wwn": "210034800D6E7ADE",
        "name": "QIB",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": "QIB",
        "vol": "QIB2",
        "target_port": [],
        "lun": 253
    },
    {
        "host_wwn": "210034800D6E7ADF",
        "name": "QIB",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": "QIB",
        "vol": "QIB2",
        "target_port": [],
        "lun": 253
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "yzw_iotest",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000003",
        "target_port": [],
        "lun": 3
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000009",
        "target_port": [],
        "lun": 3
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000012",
        "target_port": [],
        "lun": 6
    },
    {
        "host_wwn": "20090002D2937E9F",
        "name": "v6-8-44-128-21",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "v6-8-44-128-21",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "20190002D2937E9F",
        "name": "v6-8-44-128-21",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "v6-8-44-128-21",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "20090002D2937E9F",
        "name": "v6-8-44-128-21",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "V6-8-44-128-21-002",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": "20190002D2937E9F",
        "name": "v6-8-44-128-21",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "V6-8-44-128-21-002",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000007",
        "target_port": [],
        "lun": 7
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000010",
        "target_port": [],
        "lun": 4
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000013",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000000",
        "target_port": [],
        "lun": 5
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000001",
        "target_port": [],
        "lun": 4
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000016",
        "target_port": [],
        "lun": 5
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000018",
        "target_port": [],
        "lun": 7
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000015",
        "target_port": [],
        "lun": 8
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000020",
        "target_port": [],
        "lun": 6
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000021",
        "target_port": [],
        "lun": 9
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000022",
        "target_port": [],
        "lun": 8
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000019",
        "target_port": [],
        "lun": 10
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000026",
        "target_port": [],
        "lun": 9
    },
    {
        "host_wwn": None,
        "name": "host135",
        "host_iqn": "iqn.1994-05.com.redhat:1a9eaa70b558",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000028",
        "target_port": [],
        "lun": 11
    },
    {
        "host_wwn": None,
        "name": "host137",
        "host_iqn": "iqn.1994-05.com.redhat:80c412848b94",
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000024",
        "target_port": [],
        "lun": 10
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun16",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun16",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun15",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun15",
        "target_port": [],
        "lun": 2
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun13",
        "target_port": [],
        "lun": 3
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun13",
        "target_port": [],
        "lun": 3
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun11",
        "target_port": [],
        "lun": 4
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun11",
        "target_port": [],
        "lun": 4
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun14",
        "target_port": [],
        "lun": 5
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun14",
        "target_port": [],
        "lun": 5
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun2",
        "target_port": [],
        "lun": 6
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun2",
        "target_port": [],
        "lun": 6
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun5",
        "target_port": [],
        "lun": 7
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun5",
        "target_port": [],
        "lun": 7
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun4",
        "target_port": [],
        "lun": 8
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun4",
        "target_port": [],
        "lun": 8
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun1",
        "target_port": [],
        "lun": 9
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun1",
        "target_port": [],
        "lun": 9
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun3",
        "target_port": [],
        "lun": 10
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun3",
        "target_port": [],
        "lun": 10
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun6",
        "target_port": [],
        "lun": 11
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun6",
        "target_port": [],
        "lun": 11
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun12",
        "target_port": [],
        "lun": 12
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun12",
        "target_port": [],
        "lun": 12
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun10",
        "target_port": [],
        "lun": 13
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun10",
        "target_port": [],
        "lun": 13
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun8",
        "target_port": [],
        "lun": 14
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun8",
        "target_port": [],
        "lun": 14
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun7",
        "target_port": [],
        "lun": 15
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun7",
        "target_port": [],
        "lun": 15
    },
    {
        "host_wwn": "2200CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun9",
        "target_port": [],
        "lun": 16
    },
    {
        "host_wwn": "2210CC05777C3EDF",
        "name": "zty-doradoV6",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "zty_lun9",
        "target_port": [],
        "lun": 16
    },
    {
        "host_wwn": None,
        "name": "host",
        "host_iqn": "iqn.1996-04.de.suse:01:ca9f3bcaf47",
        "host_nqn": None,
        "hgroup": "HGTest",
        "vol": "Volume-Group/voltest005",
        "target_port": [],
        "lun": 254
    },
    {
        "host_wwn": None,
        "name": "host",
        "host_iqn": "iqn.1996-04.de.suse:01:ca9f3bcaf47",
        "host_nqn": None,
        "hgroup": "HGTest",
        "vol": "Volume-Group/voltest001",
        "target_port": [],
        "lun": 253
    },
    {
        "host_wwn": None,
        "name": "host",
        "host_iqn": "iqn.1996-04.de.suse:01:ca9f3bcaf47",
        "host_nqn": None,
        "hgroup": "HGTest",
        "vol": "Volume-Group/voltest002",
        "target_port": [],
        "lun": 252
    },
    {
        "host_wwn": None,
        "name": "host",
        "host_iqn": "iqn.1996-04.de.suse:01:ca9f3bcaf47",
        "host_nqn": None,
        "hgroup": "HGTest",
        "vol": "Volume-Group/voltest003",
        "target_port": [],
        "lun": 251
    },
    {
        "host_wwn": None,
        "name": "host",
        "host_iqn": "iqn.1996-04.de.suse:01:ca9f3bcaf47",
        "host_nqn": None,
        "hgroup": "HGTest",
        "vol": "Volume-Group/voltest004",
        "target_port": [],
        "lun": 250
    },
    {
        "host_wwn": "10000000C9D5BC06",
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000001-u",
        "target_port": [],
        "lun": 4
    },
    {
        "host_wwn": "10000000C9D5BC07",
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "homelab-pso-db_0000000001-u",
        "target_port": [],
        "lun": 4
    },
    {
        "host_wwn": "10000000C9D5BC06",
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "Volume-Group/voltest001",
        "target_port": [],
        "lun": 1
    },
    {
        "host_wwn": "10000000C9D5BC07",
        "name": "CL-B06-RH2288HV3-8-44-157-33",
        "host_iqn": None,
        "host_nqn": None,
        "hgroup": None,
        "vol": "Volume-Group/voltest001",
        "target_port": [],
        "lun": 1
    }
]


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
        self.assertEqual(volume[0]['native_volume_id'],
                         pool_info[0].get('volumes')[0])

    def test_get_storage(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[storage_info, hardware_info, drive_info,
                         storage_id_info, controllers_info])
        storage_object = self.driver.get_storage(context)
        self.assertEqual(storage_object.get('name'),
                         storage_id_info.get('array_name'))

    def test_list_alerts(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[alerts_info])
        list_alerts = self.driver.list_alerts(context)
        self.assertEqual(list_alerts[0].get('alert_id'),
                         alerts_info[0].get('id'))

    def test_parse_alert(self):
        parse_alert = self.driver.parse_alert(context, parse_alert_info)
        self.assertEqual(parse_alert.get('alert_id'),
                         parse_alert_info.get('1.3.6.1.2.1.1.3.0'))

    def test_list_controllers(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[controllers_info, hardware_info])
        list_controllers = self.driver.list_controllers(context)
        self.assertEqual(list_controllers[0].get('name'),
                         controllers_info[0].get('name'))

    def test_list_disks(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[hardware_info, drive_info])
        list_disks = self.driver.list_disks(context)
        self.assertEqual(list_disks[0].get('name'),
                         drive_info[0].get('name'))

    def test_list_ports(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[port_network_info, port_info, hardware_info])
        list_ports = self.driver.list_ports(context)
        self.assertEqual(list_ports[0].get('name'),
                         hardware_info[0].get('name'))

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
        self.assertEqual(hosts[0].get('name'),
                         hosts_info[0].get('iqn')[0])

    def test_list_storage_hosts(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[HOSTS_PERSONALITY_INFO])
        hosts = self.driver.list_storage_hosts(context)
        self.assertEqual(hosts[0].get('name'),
                         HOSTS_PERSONALITY_INFO[0].get('name'))

    def test_list_storage_host_groups(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[HGROUP_INFO])
        hgroup = self.driver.list_storage_host_groups(context)
        self.assertEqual(hgroup.get('storage_host_groups')[0].get('name'),
                         HGROUP_INFO[0].get('name'))

    def test_list_volume_groups(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[VOLUME_GROUP_INFO])
        v_group = self.driver.list_volume_groups(context)
        self.assertEqual(v_group.get('volume_groups')[0].get('name'),
                         VOLUME_GROUP_INFO[0].get('name'))

    def test_list_masking_views(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[HOSTS_ALL_INFO])
        views = self.driver.list_masking_views(context)
        self.assertEqual(views[0].get('native_volume_id'),
                         HOSTS_ALL_INFO[0].get('vol'))
