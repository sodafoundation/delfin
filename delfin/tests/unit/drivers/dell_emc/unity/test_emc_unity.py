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
from unittest import TestCase, mock

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.dell_emc.unity.rest_handler import RestHandler
from delfin.drivers.dell_emc.unity.unity import UnityStorDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "110.143.132.231",
        "port": "8443",
        "username": "username",
        "password": "cGFzc3dvcmQ="
    }
}
GET_STORAGE_NORMAL = {
    "entries": [
        {
            "content": {
                "id": "0",
                "health": {
                    "value": 5,
                },
                "name": "CETV3182000026",
                "model": "Unity 350F",
                "serialNumber": "CETV3182000026"
            }
        }
    ]
}
GET_STORAGE_ABNORMAL = {
    "entries": [
        {
            "content": {
                "id": "0",
                "health": {
                    "value": 20,
                },
                "name": "CETV3182000026",
                "model": "Unity 350F",
                "serialNumber": "CETV3182000026"
            }
        }
    ]
}
GET_CAPACITY = {
    "entries": [
        {
            "content": {
                "id": "0",
                "sizeFree": 2311766147072,
                "sizeTotal": 8838774259712,
                "sizeUsed": 6527008112640,
                "sizeSubscribed": 307567976775680,
                "totalLogicalSize": 307542206971904
            }
        }
    ]
}
GET_SOFT_VERSION = {
    "entries": [
        {
            "content": {
                "id": "4.7.1"
            }
        }
    ]
}
storage_normal_result = {
    'free_capacity': 2311766147072,
    'serial_number': 'CETV3182000026',
    'subscribed_capacity': 307567976775680,
    'used_capacity': 6527008112640,
    'vendor': 'DELL EMC',
    'location': '',
    'total_capacity': 8838774259712,
    'status': 'normal',
    'name': 'CETV3182000026',
    'model': 'Unity 350F',
    'raw_capacity': 12121212,
    'firmware_version': '4.7.1'
}
storage_abnormal_result = {
    'name': 'CETV3182000026',
    'vendor': 'DELL EMC',
    'model': 'Unity 350F',
    'status': 'normal',
    'serial_number': 'CETV3182000026',
    'firmware_version': '4.7.1',
    'location': '',
    'subscribed_capacity': 307567976775680,
    'total_capacity': 8838774259712,
    'raw_capacity': 12121212,
    'used_capacity': 6527008112640,
    'free_capacity': 2311766147072
}
GET_ALL_POOLS = {
    "entries": [
        {
            "content": {
                "id": "pool_1",
                "health": {
                    "value": 7
                },
                "name": "pool1",
                "sizeFree": 2311766147072,
                "sizeTotal": 8838774259712,
                "sizeUsed": 6527008112640,
                "sizeSubscribed": 310896039559168
            }
        }
    ]
}
GET_ALL_ABNORMAL_POOLS = {
    "entries": [
        {
            "content": {
                "id": "pool_1",
                "health": {
                    "value": 20
                },
                "name": "pool1",
                "sizeFree": 2311766147072,
                "sizeTotal": 8838774259712,
                "sizeUsed": 6527008112640,
                "sizeSubscribed": 310896039559168
            }
        }
    ]
}
pool_result = [
    {
        'native_storage_pool_id': 'pool_1',
        'status': 'normal',
        'free_capacity': 2311766147072,
        'name': 'pool1',
        'storage_type': 'unified',
        'total_capacity': 8838774259712,
        'description': None,
        'subscribed_capacity': 310896039559168,
        'used_capacity': 6527008112640,
        'storage_id': '12345'
    }
]
pool_abnormal_result = [
    {
        'native_storage_pool_id': 'pool_1',
        'status': 'abnormal',
        'free_capacity': 2311766147072,
        'name': 'pool1',
        'storage_type': 'unified',
        'total_capacity': 8838774259712,
        'description': None,
        'subscribed_capacity': 310896039559168,
        'used_capacity': 6527008112640,
        'storage_id': '12345'
    }
]
GET_ALL_LUNS = {
    "entries": [
        {
            "content": {
                "id": "sv_1",
                "type": 2,
                "health": {
                    "value": 5
                },
                "name": "LUN-00",
                "sizeTotal": 107374182400,
                "sizeAllocated": 0,
                "wwn": "60:06:01:60:0B:00:49:00:BE:CE:6C:5C:56:C1:9D:D2",
                "pool": {
                    "id": "pool_1"
                }
            }
        }
    ]
}
GET_ALL_LUNS_NULL = {
    "entries": []
}
volume_result = [
    {
        'used_capacity': 0,
        'free_capacity': 107374182400,
        'native_storage_pool_id': 'pool_1',
        'description': None,
        'native_volume_id': 'sv_1',
        'total_capacity': 107374182400,
        'storage_id': '12345',
        'wwn': '60:06:01:60:0B:00:49:00:BE:CE:6C:5C:56:C1:9D:D2',
        'type': 'thick',
        'name': 'LUN-00',
        'status': 'normal'
    }
]
TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.103.1.18.2.0',
    '1.3.6.1.4.1.1139.103.1.18.1.1': 'eeeeeeeee',
    '1.3.6.1.4.1.1139.103.1.18.1.3': '14:60bba',
    '1.3.6.1.4.1.1139.103.1.18.1.4': 'this is test',
    '1.3.6.1.4.1.1139.103.1.18.1.5': '2020/11/20 14:10:10',
    '1.3.6.1.4.1.1139.103.1.18.1.2': 'test'
}
TRAP_NOT_IN_MAPPPING_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.103.1.18.2.0',
    '1.3.6.1.4.1.1139.103.1.18.1.1': 'eeeeeeeee',
    '1.3.6.1.4.1.1139.103.1.18.1.3': '14:60bba1',
    '1.3.6.1.4.1.1139.103.1.18.1.4': 'this is test',
    '1.3.6.1.4.1.1139.103.1.18.1.5': '2020/11/20 14:10:10',
    '1.3.6.1.4.1.1139.103.1.18.1.2': 'test'
}
trap_result = {
    'alert_id': '14:60bba',
    'alert_name': 'this is test',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'Storage resource allocation from one of the pools has '
                   'exceed the 85% threshold. Allocate more storage space '
                   'from the pool to the storage resource.',
    'resource_type': 'Storage',
    'location': 'eeeeeeeee',
    'match_key': '8c6d115258631625b625486f81b09532'
}
trap_not_in_mapping_result = {
    'alert_id': '14:60bba1',
    'alert_name': 'this is test',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'this is test',
    'resource_type': 'Storage',
    'location': 'eeeeeeeee',
    'match_key': '8c6d115258631625b625486f81b09532'
}
GET_ALL_ALERTS = {
    "entries": [
        {
            "content": {
                "id": "alert_31523",
                "severity": 4,
                "timestamp": "2020-10-12T09:09:52.609Z",
                "component": {
                    "id": "Host_87",
                    "resource": "host"
                },
                "messageId": "14:608fe",
                "message": "Host hpux11iv2 does not have any initiators",
                "description": "The host does not have any initiators."
            }
        }
    ]
}
GET_ALL_ALERTS_NULL = {
    "entries": []
}
alert_result = [
    {
        'severity': 'Warning',
        'location': 'Host_87',
        'occur_time': 1602464992000,
        'type': 'EquipmentAlarm',
        'alert_name': 'Host hpux11iv2 does not have any initiators',
        'resource_type': 'Storage',
        'alert_id': '14:608fe',
        'description': 'The host does not have any initiators.',
        'category': 'Fault',
        'sequence_number': 'alert_31523',
        'match_key': 'de23e7c25b5a46f029cb2f84f15a4a3a'
    }
]
GET_ALL_CONTROLLERS = {
    "entries": [
        {
            "content": {
                "id": "spa",
                "parent": {
                    "id": "dpe",
                    "resource": "dpe"
                },
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "needsReplacement": "false",
                "isRescueMode": "false",
                "model": "",
                "slotNumber": 0,
                "name": "SP A",
                "emcPartNumber": "",
                "emcSerialNumber": "VIRT2102W6CHH8",
                "manufacturer": "",
                "vendorPartNumber": "",
                "vendorSerialNumber": "",
                "sasExpanderVersion": "",
                "memorySize": 12288,
                "parentDpe": {
                    "id": "dpe"
                }
            }
        }
    ]
}
controller_result = [
    {
        'name': 'SP A',
        'storage_id': '12345',
        'native_controller_id': 'spa',
        'status': 'normal',
        'location': 0,
        'memory_size': 12884901888
    }
]
GET_ALL_DISKS = {
    "entries": [
        {
            "content": {
                "id": "disk1",
                "parent": {
                    "id": "dpe",
                    "resource": "dpe"
                },
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "model": "ddd",
                "slotNumber": 12,
                "name": "disk1",
                "version": "dddd",
                "emcSerialNumber": "VIRT2102W6CHH8",
                "manufacturer": "ibm",
                "vendorPartNumber": "",
                "vendorSerialNumber": "",
                "sasExpanderVersion": "",
                "rpm": 12288,
                "size": 12121212,
                "diskTechnology": 1,
                "diskGroup": {
                    "id": "dp1"
                }
            }
        }
    ]
}
disk_result = [
    {
        'name': 'disk1',
        'storage_id': '12345',
        'native_disk_id': 'disk1',
        'serial_number': 'VIRT2102W6CHH8',
        'manufacturer': 'ibm',
        'model': 'ddd',
        'firmware': 'dddd',
        'speed': 12288,
        'capacity': 12121212,
        'status': 'normal',
        'physical_type': 'sas',
        'logical_type': '',
        'native_disk_group_id': 'dp1',
        'location': 'disk1'
    }
]
GET_ALL_ETHPORTS = {
    "entries": [
        {
            "content": {
                "id": "spa_eth0",
                "speed": 10000,
                "connectorType": 1,
                "requestedSpeed": 0,
                "supportedSpeeds": [
                    0
                ],
                "sfpSupportedSpeeds": [],
                "sfpSupportedProtocols": [],
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_PORT_LINK_UP"
                    ],
                    "descriptions": [
                        "The port is operating normally."
                    ]
                },
                "name": "SP A Ethernet Port 0",
                "portNumber": 0,
                "mtu": 1500,
                "minMtu": 46,
                "maxMtu": 9000,
                "bond": False,
                "isLinkUp": True,
                "macAddress": "00:50:56:81:E1:50",
                "isRSSCapable": False,
                "isRDMACapable": False,
                "requestedMtu": 1500,
                "parent": {
                    "id": "spa",
                    "resource": "storageProcessor"
                },
                "storageProcessor": {
                    "id": "spa"
                },
                "parentStorageProcessor": {
                    "id": "spa"
                }
            }
        },
        {
            "content": {
                "id": "spa_eth1",
                "speed": 10000,
                "connectorType": 1,
                "requestedSpeed": 0,
                "supportedSpeeds": [
                    0
                ],
                "sfpSupportedSpeeds": [],
                "sfpSupportedProtocols": [],
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_PORT_LINK_UP"
                    ],
                    "descriptions": [
                        "The port is operating normally."
                    ]
                },
                "name": "SP A Ethernet Port 1",
                "portNumber": 1,
                "mtu": 1500,
                "minMtu": 46,
                "maxMtu": 9000,
                "bond": False,
                "isLinkUp": True,
                "macAddress": "00:50:56:81:E8:4B",
                "isRSSCapable": False,
                "isRDMACapable": False,
                "requestedMtu": 1500,
                "parent": {
                    "id": "spa",
                    "resource": "storageProcessor"
                },
                "storageProcessor": {
                    "id": "spa"
                },
                "parentStorageProcessor": {
                    "id": "spa"
                }
            }
        },
        {
            "content": {
                "id": "spa_eth2",
                "speed": 10000,
                "connectorType": 1,
                "requestedSpeed": 0,
                "supportedSpeeds": [
                    0
                ],
                "sfpSupportedSpeeds": [],
                "sfpSupportedProtocols": [],
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_PORT_LINK_UP"
                    ],
                    "descriptions": [
                        "The port is operating normally."
                    ]
                },
                "name": "SP A Ethernet Port 2",
                "portNumber": 2,
                "mtu": 1500,
                "minMtu": 46,
                "maxMtu": 9000,
                "bond": False,
                "isLinkUp": True,
                "macAddress": "00:50:56:81:11:EF",
                "isRSSCapable": False,
                "isRDMACapable": False,
                "requestedMtu": 1500,
                "parent": {
                    "id": "spa",
                    "resource": "storageProcessor"
                },
                "storageProcessor": {
                    "id": "spa"
                },
                "parentStorageProcessor": {
                    "id": "spa"
                }
            }
        },
        {
            "content": {
                "id": "spa_eth3",
                "speed": 10000,
                "connectorType": 1,
                "requestedSpeed": 0,
                "supportedSpeeds": [
                    0
                ],
                "sfpSupportedSpeeds": [],
                "sfpSupportedProtocols": [],
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_PORT_LINK_UP"
                    ],
                    "descriptions": [
                        "The port is operating normally."
                    ]
                },
                "name": "SP A Ethernet Port 3",
                "portNumber": 3,
                "mtu": 1500,
                "minMtu": 46,
                "maxMtu": 9000,
                "isLinkUp": True,
                "macAddress": "00:50:56:81:DB:5D",
                "requestedMtu": 1500,
                "parent": {
                    "id": "spa",
                    "resource": "storageProcessor"
                },
                "storageProcessor": {
                    "id": "spa"
                },
                "parentStorageProcessor": {
                    "id": "spa"
                }
            }
        },
        {
            "content": {
                "id": "spa_mgmt",
                "speed": 10000,
                "connectorType": 1,
                "requestedSpeed": 0,
                "supportedSpeeds": [
                    0
                ],
                "sfpSupportedSpeeds": [],
                "sfpSupportedProtocols": [],
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_PORT_LINK_UP"
                    ],
                    "descriptions": [
                        "The port is operating normally."
                    ]
                },
                "name": "SP A Management Port",
                "portNumber": 0,
                "mtu": 1500,
                "minMtu": 0,
                "maxMtu": 0,
                "bond": False,
                "isLinkUp": True,
                "macAddress": "00:50:56:81:E5:05",
                "isRSSCapable": False,
                "isRDMACapable": False,
                "requestedMtu": 0,
                "parent": {
                    "id": "spa",
                    "resource": "storageProcessor"
                },
                "storageProcessor": {
                    "id": "spa"
                },
                "parentStorageProcessor": {
                    "id": "spa"
                }
            }
        }
    ]
}
GET_ALL_IP = {
    "entries": [
        {
            "content": {
                "id": "1",
                "netmask": "255.255.255.0",
                "ipAddress": "192.168.3.111",
                "ipProtocolVersion": 4,
                "ipPort": {
                    "id": "spa_eth1"
                }
            }
        }
    ]
}
GET_ALL_FCPORTS = {
    "entries": [
        {
            "content": {
                "id": "spa_fc0",
                "currentSpeed": 10,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_PORT_LINK_UP"
                    ],
                    "descriptions": [
                        "The port is operating normally."
                    ]
                },
                "name": "SP A FC Port 0",
                "portNumber": 0,
                "isLinkUp": True,
                "macAddress": "00:50:56:81:E1:50",
                "wwn": "fffffffffff",
                "isRDMACapable": False,
                "requestedMtu": 1500,
                "parent": {
                    "id": "spa",
                    "resource": "storageProcessor"
                },
                "storageProcessor": {
                    "id": "spa"
                },
                "parentStorageProcessor": {
                    "id": "spa"
                }
            }
        }
    ]
}
port_result = [
    {
        'name': 'SP A Ethernet Port 0',
        'storage_id': '12345',
        'native_port_id': 'spa_eth0',
        'location': 'SP A Ethernet Port 0',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'eth',
        'logical_type': '',
        'speed': 10000000000,
        'max_speed': 10000000000,
        'native_parent_id': 'spa',
        'wwn': '',
        'mac_address': '00:50:56:81:E1:50',
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }, {
        'name': 'SP A Ethernet Port 1',
        'storage_id': '12345',
        'native_port_id': 'spa_eth1',
        'location': 'SP A Ethernet Port 1',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'eth',
        'logical_type': '',
        'speed': 10000000000,
        'max_speed': 10000000000,
        'native_parent_id': 'spa',
        'wwn': '',
        'mac_address': '00:50:56:81:E8:4B',
        'ipv4': '192.168.3.111',
        'ipv4_mask': '255.255.255.0',
        'ipv6': None,
        'ipv6_mask': None
    }, {
        'name': 'SP A Ethernet Port 2',
        'storage_id': '12345',
        'native_port_id': 'spa_eth2',
        'location': 'SP A Ethernet Port 2',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'eth',
        'logical_type': '',
        'speed': 10000000000,
        'max_speed': 10000000000,
        'native_parent_id': 'spa',
        'wwn': '',
        'mac_address': '00:50:56:81:11:EF',
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }, {
        'name': 'SP A Ethernet Port 3',
        'storage_id': '12345',
        'native_port_id': 'spa_eth3',
        'location': 'SP A Ethernet Port 3',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'eth',
        'logical_type': '',
        'speed': 10000000000,
        'max_speed': 10000000000,
        'native_parent_id': 'spa',
        'wwn': '',
        'mac_address': '00:50:56:81:DB:5D',
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }, {
        'name': 'SP A Management Port',
        'storage_id': '12345',
        'native_port_id': 'spa_mgmt',
        'location': 'SP A Management Port',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'eth',
        'logical_type': '',
        'speed': 10000000000,
        'max_speed': 10000000000,
        'native_parent_id': 'spa',
        'wwn': '',
        'mac_address': '00:50:56:81:E5:05',
        'ipv4': None,
        'ipv4_mask': None,
        'ipv6': None,
        'ipv6_mask': None
    }, {
        'name': 'SP A FC Port 0',
        'storage_id': '12345',
        'native_port_id': 'spa_fc0',
        'location': 'SP A FC Port 0',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'fc',
        'logical_type': '',
        'speed': 10000000000,
        'max_speed': 10000000000,
        'native_parent_id': 'spa',
        'wwn': 'fffffffffff'
    }
]
GET_ALL_FILESYSTEMS = {
    "entries": [
        {
            "content": {
                "id": "fs_1",
                "type": 1,
                "flrVersion": 1,
                "supportedProtocols": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "name": "fs1",
                "sizeTotal": 5368709120,
                "sizeUsed": 1622450176,
                "sizeAllocated": 283148288,
                "isThinEnabled": True,
                "storageResource": {
                    "id": "res_1"
                },
                "pool": {
                    "id": "pool_1"
                },
                "nasServer": {
                    "id": "nas_1"
                },
                "cifsShare": [
                    {
                        "id": "SMBShare_2"
                    }
                ],
                "nfsShare": [
                    {
                        "id": "NFSShare_2"
                    }
                ]
            }
        },
        {
            "content": {
                "id": "fs_3",
                "type": 1,
                "flrVersion": 2,
                "supportedProtocols": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "name": "ddd",
                "sizeTotal": 107374182400,
                "sizeUsed": 1620303872,
                "sizeAllocated": 283140096,
                "isThinEnabled": True,
                "storageResource": {
                    "id": "res_3"
                },
                "pool": {
                    "id": "pool_1"
                },
                "nasServer": {
                    "id": "nas_1"
                }
            }
        },
        {
            "content": {
                "id": "fs_5",
                "type": 1,
                "flrVersion": 0,
                "supportedProtocols": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "name": "fs_home",
                "sizeTotal": 10737418240,
                "sizeUsed": 1622458368,
                "sizeAllocated": 283156480,
                "isThinEnabled": True,
                "storageResource": {
                    "id": "res_5"
                },
                "pool": {
                    "id": "pool_1"
                },
                "nasServer": {
                    "id": "nas_1"
                }
            }
        },
        {
            "content": {
                "id": "fs_16",
                "type": 1,
                "flrVersion": 0,
                "supportedProtocols": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "name": "fs_boga",
                "sizeTotal": 5368709120,
                "sizeUsed": 1622450176,
                "sizeAllocated": 283148288,
                "isThinEnabled": True,
                "storageResource": {
                    "id": "res_16"
                },
                "pool": {
                    "id": "pool_1"
                },
                "nasServer": {
                    "id": "nas_1"
                },
                "cifsShare": [
                    {
                        "id": "SMBShare_14"
                    }
                ],
                "nfsShare": [
                    {
                        "id": "NFSShare_14"
                    }
                ]
            }
        },
        {
            "content": {
                "id": "fs_20",
                "type": 1,
                "flrVersion": 0,
                "supportedProtocols": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally"
                    ]
                },
                "name": "fs2",
                "sizeTotal": 5368709120,
                "sizeUsed": 1622450176,
                "sizeAllocated": 283148288,
                "isThinEnabled": True,
                "storageResource": {
                    "id": "res_20"
                },
                "pool": {
                    "id": "pool_1"
                },
                "nasServer": {
                    "id": "nas_1"
                },
                "cifsShare": [
                    {
                        "id": "SMBShare_18"
                    }
                ],
                "nfsShare": [
                    {
                        "id": "NFSShare_18"
                    }
                ]
            }
        },
        {
            "content": {
                "id": "fs_22",
                "type": 1,
                "flrVersion": 0,
                "supportedProtocols": 2,
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "name": "FS_MULTI1",
                "sizeTotal": 107374182400,
                "sizeUsed": 1620303872,
                "sizeAllocated": 283140096,
                "isThinEnabled": True,
                "storageResource": {
                    "id": "res_22"
                },
                "pool": {
                    "id": "pool_1"
                },
                "nasServer": {
                    "id": "nas_1"
                },
                "nfsShare": [
                    {
                        "id": "NFSShare_19"
                    }
                ]
            }
        }
    ]
}
filesystem_result = [
    {
        'name': 'fs1',
        'storage_id': '12345',
        'native_filesystem_id': 'fs_1',
        'native_pool_id': 'pool_1',
        'status': 'normal',
        'type': 'thin',
        'total_capacity': 5368709120,
        'used_capacity': 1622450176,
        'free_capacity': 3746258944,
        'worm': 'enterprise',
        'security_mode': 'native'
    }, {
        'name': 'ddd',
        'storage_id': '12345',
        'native_filesystem_id': 'fs_3',
        'native_pool_id': 'pool_1',
        'status': 'normal',
        'type': 'thin',
        'total_capacity': 107374182400,
        'used_capacity': 1620303872,
        'free_capacity': 105753878528,
        'worm': 'compliance',
        'security_mode': 'native'
    }, {
        'name': 'fs_home',
        'storage_id': '12345',
        'native_filesystem_id': 'fs_5',
        'native_pool_id': 'pool_1',
        'status': 'normal',
        'type': 'thin',
        'total_capacity': 10737418240,
        'used_capacity': 1622458368,
        'free_capacity': 9114959872,
        'worm': 'non_worm',
        'security_mode': 'native'
    }, {
        'name': 'fs_boga',
        'storage_id': '12345',
        'native_filesystem_id': 'fs_16',
        'native_pool_id': 'pool_1',
        'status': 'normal',
        'type': 'thin',
        'total_capacity': 5368709120,
        'used_capacity': 1622450176,
        'free_capacity': 3746258944,
        'worm': 'non_worm',
        'security_mode': 'native'
    }, {
        'name': 'fs2',
        'storage_id': '12345',
        'native_filesystem_id': 'fs_20',
        'native_pool_id': 'pool_1',
        'status': 'normal',
        'type': 'thin',
        'total_capacity': 5368709120,
        'used_capacity': 1622450176,
        'free_capacity': 3746258944,
        'worm': 'non_worm',
        'security_mode': 'native'
    }, {
        'name': 'FS_MULTI1',
        'storage_id': '12345',
        'native_filesystem_id': 'fs_22',
        'native_pool_id': 'pool_1',
        'status': 'normal',
        'type': 'thin',
        'total_capacity': 107374182400,
        'used_capacity': 1620303872,
        'free_capacity': 105753878528,
        'worm': 'non_worm',
        'security_mode': 'native'
    }
]
GET_ALL_QTREE = {
    "entries": [
        {
            "content": {
                "id": "qtree_1",
                "hardLimit": 1000,
                "softLimit": 1110,
                "sizeUsed": 20000000,
                "path": "/",
                "filesystem": {
                    "id": "filesystem_1"
                },
                "quotaConfig": {
                    "id": "quotaConfig_1"
                }
            }
        }
    ]
}
qtree_result = [
    {
        'name': '/',
        'storage_id': '12345',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'filesystem_1',
        'path': '/'
    }
]
GET_ALL_CIFSSHARE = {
    "entries": [
        {
            "content": {
                "id": "SMBShare_2",
                "type": 1,
                "name": "fs1",
                "path": "/",
                "filesystem": {
                    "id": "fs_1"
                }
            }
        },
        {
            "content": {
                "id": "SMBShare_14",
                "type": 1,
                "name": "boga",
                "path": "/",
                "filesystem": {
                    "id": "fs_16"
                }
            }
        },
        {
            "content": {
                "id": "SMBShare_18",
                "type": 1,
                "name": "fs2",
                "path": "/",
                "filesystem": {
                    "id": "fs_20"
                }
            }
        }
    ]
}
GET_ALL_NFSSHARE = {
    "entries": [
        {
            "content": {
                "id": "NFSShare_2",
                "type": 1,
                "role": 0,
                "name": "fs1",
                "path": "/",
                "filesystem": {
                    "id": "fs_1"
                }
            }
        },
        {
            "content": {
                "id": "NFSShare_14",
                "type": 1,
                "role": 0,
                "name": "boga",
                "path": "/",
                "filesystem": {
                    "id": "fs_16"
                }
            }
        },
        {
            "content": {
                "id": "NFSShare_18",
                "type": 1,
                "role": 0,
                "name": "fs2",
                "path": "/",
                "filesystem": {
                    "id": "fs_20"
                }
            }
        },
        {
            "content": {
                "id": "NFSShare_19",
                "type": 1,
                "role": 0,
                "name": "FS_MULTI1",
                "path": "/",
                "filesystem": {
                    "id": "fs_22"
                }
            }
        }
    ]
}
share_result = [
    {
        'name': 'fs1',
        'storage_id': '12345',
        'native_share_id': 'SMBShare_2',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_1',
        'path': '/fs1/',
        'protocol': 'cifs'
    }, {
        'name': 'boga',
        'storage_id': '12345',
        'native_share_id': 'SMBShare_14',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_16',
        'path': '/fs_boga/',
        'protocol': 'cifs'
    }, {
        'name': 'fs2',
        'storage_id': '12345',
        'native_share_id': 'SMBShare_18',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_20',
        'path': '/fs2/',
        'protocol': 'cifs'
    }, {
        'name': 'fs1',
        'storage_id': '12345',
        'native_share_id': 'NFSShare_2',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_1',
        'path': '/fs1/',
        'protocol': 'nfs'
    }, {
        'name': 'boga',
        'storage_id': '12345',
        'native_share_id': 'NFSShare_14',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_16',
        'path': '/fs_boga/',
        'protocol': 'nfs'
    }, {
        'name': 'fs2',
        'storage_id': '12345',
        'native_share_id': 'NFSShare_18',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_20',
        'path': '/fs2/',
        'protocol': 'nfs'
    }, {
        'name': 'FS_MULTI1',
        'storage_id': '12345',
        'native_share_id': 'NFSShare_19',
        'native_qtree_id': 'qtree_1',
        'native_filesystem_id': 'fs_22',
        'path': '/FS_MULTI1/',
        'protocol': 'nfs'
    }
]
GET_ALL_QUOTACONFIG = {
    "entries": [
        {
            "content": {
                "id": "quotaConfig_1",
                "isAccessDenyEnabled": True,
                "quotaPolicy": 0,
                "isUserQuotaEnabled": True,
                "filesystem": {
                    "id": "filesystem_1"
                },
                "treeQuota": {
                    "id": "qtree_1"
                }
            }
        }
    ]
}
GET_ALL_USERQUOTA = {
    "entries": [
        {
            "content": {
                "id": "user_1",
                "hardLimit": 1000,
                "softLimit": 1110,
                "sizeUsed": 20000000,
                "path": "/",
                "uid": 1111,
                "filesystem": {
                    "id": "filesystem_1"
                },
                "treeQuota": {
                    "id": "qtree_1"
                }
            }
        },
        {
            "content": {
                "id": "user_2",
                "hardLimit": 1000,
                "softLimit": 1110,
                "sizeUsed": 20000000,
                "path": "/",
                "uid": 22222,
                "filesystem": {
                    "id": "filesystem_1"
                }
            }
        }
    ]
}
quota_result = [
    {
        'native_quota_id': 'qtree_1',
        'type': 'tree',
        'storage_id': '12345',
        'native_filesystem_id': 'filesystem_1',
        'native_qtree_id': 'qtree_1',
        'capacity_hard_limit': 1000,
        'capacity_soft_limit': 1110,
        'used_capacity': 20000000
    }, {
        'native_quota_id': 'user_1',
        'type': 'user',
        'storage_id': '12345',
        'native_filesystem_id': 'filesystem_1',
        'native_qtree_id': 'qtree_1',
        'capacity_hard_limit': 1000,
        'capacity_soft_limit': 1110,
        'used_capacity': 20000000,
        'user_group_name': '1111'
    }, {
        'native_quota_id': 'user_2',
        'type': 'user',
        'storage_id': '12345',
        'native_filesystem_id': 'filesystem_1',
        'native_qtree_id': None,
        'capacity_hard_limit': 1000,
        'capacity_soft_limit': 1110,
        'used_capacity': 20000000,
        'user_group_name': '22222'
    }
]
GET_ETH_PORT_READ_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "spa_eth0": "10000",
                        "spa_eth1": "20000",
                        "spa_eth2": "30000",
                        "spa_eth3": "40000"
                    },
                    "spb": {
                        "spa_eth0": "10000",
                        "spa_eth1": "20000",
                        "spa_eth2": "30000",
                        "spa_eth3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spa": {
                        "spa_eth0": "40000",
                        "spa_eth1": "30000",
                        "spa_eth2": "20000",
                        "spa_eth3": "10000"
                    },
                    "spb": {
                        "spa_eth0": "40000",
                        "spa_eth1": "30000",
                        "spa_eth2": "20000",
                        "spa_eth3": "10000"
                    }
                }
            }
        }
    ]
}
GET_ETH_PORT_READ_THR_PERF_NULL = {
    "entries": []
}
GET_ETH_PORT_WRITE_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "spa_eth0": "90000",
                        "spa_eth1": "80000",
                        "spa_eth2": "70000",
                        "spa_eth3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spa": {
                        "spa_eth0": "60000",
                        "spa_eth1": "70000",
                        "spa_eth2": "80000",
                        "spa_eth3": "90000"
                    }
                }
            }
        }
    ]
}
GET_ETH_PORT_WRITE_THR_PERF_NULL = {
    "entries": []
}
GET_FC_PORT_READ_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "10000",
                        "spa_fc1": "20000",
                        "spa_fc2": "30000",
                        "spa_fc3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "40000",
                        "spa_fc1": "30000",
                        "spa_fc2": "20000",
                        "spa_fc3": "10000"
                    }
                }
            }
        }
    ]
}
GET_FC_PORT_READ_THR_PERF_NULL = {
    "entries": []
}
GET_FC_PORT_WRITE_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "90000",
                        "spa_fc1": "80000",
                        "spa_fc2": "70000",
                        "spa_fc3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "60000",
                        "spa_fc1": "70000",
                        "spa_fc2": "80000",
                        "spa_fc3": "90000"
                    }
                }
            }
        }
    ]
}
GET_FC_PORT_WRITE_THR_PERF_NULL = {
    "entries": []
}
GET_FC_PORT_READ_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "10000",
                        "spa_fc1": "20000",
                        "spa_fc2": "30000",
                        "spa_fc3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "40000",
                        "spa_fc1": "30000",
                        "spa_fc2": "20000",
                        "spa_fc3": "10000"
                    }
                }
            }
        }
    ]
}
GET_FC_PORT_READ_IOPS_PERF_NULL = {
    "entries": []
}
GET_FC_PORT_WRITE_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "spa_fc0": "90000",
                        "spa_fc1": "80000",
                        "spa_fc2": "70000",
                        "spa_fc3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "spa_fc0": "60000",
                        "spa_fc1": "70000",
                        "spa_fc2": "80000",
                        "spa_fc3": "90000"
                    }
                }
            }
        }
    ]
}
GET_FC_PORT_WRITE_IOPS_PERF_NULL = {
    "entries": []
}
GET_VOLUME_READ_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "10000",
                        "volume1": "20000",
                        "volume2": "30000",
                        "volume3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "40000",
                        "volume1": "30000",
                        "volume2": "20000",
                        "volume3": "10000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_READ_THR_PERF_NULL = {
    "entries": []
}
GET_VOLUME_WRITE_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "90000",
                        "volume1": "80000",
                        "volume2": "70000",
                        "volume3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "60000",
                        "volume1": "70000",
                        "volume2": "80000",
                        "volume3": "90000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_WRITE_THR_PERF_NULL = {
    "entries": []
}
GET_VOLUME_READ_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "10000",
                        "volume1": "20000",
                        "volume2": "30000",
                        "volume3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "40000",
                        "volume1": "30000",
                        "volume2": "20000",
                        "volume3": "10000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_READ_IOPS_PERF_NULL = {
    "entries": []
}
GET_VOLUME_WRITE_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "90000",
                        "volume1": "80000",
                        "volume2": "70000",
                        "volume3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "60000",
                        "volume1": "70000",
                        "volume2": "80000",
                        "volume3": "90000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_WRITE_IOPS_PERF_NULL = {
    "entries": []
}
GET_VOLUME_READ_IO_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "10000",
                        "volume1": "20000",
                        "volume2": "30000",
                        "volume3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "40000",
                        "volume1": "30000",
                        "volume2": "20000",
                        "volume3": "10000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_READ_IO_PERF_NULL = {
    "entries": []
}
GET_VOLUME_WRITE_IO_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "90000",
                        "volume1": "80000",
                        "volume2": "70000",
                        "volume3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "60000",
                        "volume1": "70000",
                        "volume2": "80000",
                        "volume3": "90000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_WRITE_IO_PERF_NULL = {
    "entries": []
}
GET_VOLUME_RESPONSE_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "volume0": "90000",
                        "volume1": "80000",
                        "volume2": "70000",
                        "volume3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "volume0": "60000",
                        "volume1": "70000",
                        "volume2": "80000",
                        "volume3": "90000"
                    }
                }
            }
        }
    ]
}
GET_VOLUME_RESPONSE_PERF_NULL = {
    "entries": []
}
GET_DISK_READ_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "DISK0": "10000",
                        "DISK1": "20000",
                        "DISK2": "30000",
                        "DISK3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "DISK0": "40000",
                        "DISK1": "30000",
                        "DISK2": "20000",
                        "DISK3": "10000"
                    }
                }
            }
        }
    ]
}
GET_DISK_READ_THR_PERF_NULL = {
    "entries": []
}
GET_DISK_WRITE_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "DISK0": "90000",
                        "DISK1": "80000",
                        "DISK2": "70000",
                        "DISK3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "DISK0": "60000",
                        "DISK1": "70000",
                        "DISK2": "80000",
                        "DISK3": "90000"
                    }
                }
            }
        }
    ]
}
GET_DISK_WRITE_THR_PERF_NULL = {
    "entries": []
}
GET_DISK_READ_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "DISK0": "10000",
                        "DISK1": "20000",
                        "DISK2": "30000",
                        "DISK3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "DISK0": "40000",
                        "DISK1": "30000",
                        "DISK2": "20000",
                        "DISK3": "10000"
                    }
                }
            }
        }
    ]
}
GET_DISK_READ_IOPS_PERF_NULL = {
    "entries": []
}
GET_DISK_WRITE_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "DISK0": "90000",
                        "DISK1": "80000",
                        "DISK2": "70000",
                        "DISK3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "DISK0": "60000",
                        "DISK1": "70000",
                        "DISK2": "80000",
                        "DISK3": "90000"
                    }
                }
            }
        }
    ]
}
GET_DISK_WRITE_IOPS_PERF_NULL = {
    "entries": []
}
GET_DISK_RESPONSE_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "DISK0": "90000",
                        "DISK1": "80000",
                        "DISK2": "70000",
                        "DISK3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "DISK0": "60000",
                        "DISK1": "70000",
                        "DISK2": "80000",
                        "DISK3": "90000"
                    }
                }
            }
        }
    ]
}
GET_DISK_RESPONSE_PERF_NULL = {
    "entries": []
}
GET_FILE_READ_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "FILE0": "10000",
                        "FILE1": "20000",
                        "FILE2": "30000",
                        "FILE3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "FILE0": "40000",
                        "FILE1": "30000",
                        "FILE2": "20000",
                        "FILE3": "10000"
                    }
                }
            }
        }
    ]
}
GET_FILE_READ_THR_PERF_NULL = {
    "entries": []
}
GET_FILE_WRITE_THR_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "FILE0": "90000",
                        "FILE1": "80000",
                        "FILE2": "70000",
                        "FILE3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "FILE0": "60000",
                        "FILE1": "70000",
                        "FILE2": "80000",
                        "FILE3": "90000"
                    }
                }
            }
        }
    ]
}
GET_FILE_WRITE_THR_PERF_NULL = {
    "entries": []
}
GET_FILE_READ_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "FILE0": "10000",
                        "FILE1": "20000",
                        "FILE2": "30000",
                        "FILE3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "FILE0": "40000",
                        "FILE1": "30000",
                        "FILE2": "20000",
                        "FILE3": "10000"
                    }
                }
            }
        }
    ]
}
GET_FILE_READ_IOPS_PERF_NULL = {
    "entries": []
}
GET_FILE_WRITE_IOPS_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "FILE0": "90000",
                        "FILE1": "80000",
                        "FILE2": "70000",
                        "FILE3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "FILE0": "60000",
                        "FILE1": "70000",
                        "FILE2": "80000",
                        "FILE3": "90000"
                    }
                }
            }
        }
    ]
}
GET_FILE_WRITE_IOPS_PERF_NULL = {
    "entries": []
}
GET_FILE_READ_IO_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "FILE0": "10000",
                        "FILE1": "20000",
                        "FILE2": "30000",
                        "FILE3": "40000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "FILE0": "40000",
                        "FILE1": "30000",
                        "FILE2": "20000",
                        "FILE3": "10000"
                    }
                }
            }
        }
    ]
}
GET_FILE_READ_IO_PERF_NULL = {
    "entries": []
}
GET_FILE_WRITE_IO_PERF = {
    "entries": [
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:47:10.000Z",
                "values": {
                    "spa": {
                        "FILE0": "90000",
                        "FILE1": "80000",
                        "FILE2": "70000",
                        "FILE3": "60000"
                    }
                }
            }
        },
        {
            "content": {
                "queryId": 46,
                "path": "sp.*.net.device.*.bytesOut",
                "timestamp": "2021-07-08T06:46:10.000Z",
                "values": {
                    "spb": {
                        "FILE0": "60000",
                        "FILE1": "70000",
                        "FILE2": "80000",
                        "FILE3": "90000"
                    }
                }
            }
        }
    ]
}
GET_FILE_WRITE_IO_PERF_NULL = {
    "entries": []
}
resource_metrics = {
    'volume': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'responseTime',
        'ioSize', 'readIoSize', 'writeIoSize',
    ],
    'port': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput'
    ],
    'disk': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'responseTime'
    ],
    'filesystem': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'readIoSize', 'writeIoSize'
    ]
}
GET_ALL_INIT = {
    "entries": [
        {
            "content": {
                "id": "init1",
                "type": 1,
                "initiatorId": "fs1",
                "path": "/",
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "parentHost": {
                    "id": "fs_1"
                }
            }
        },
        {
            "content": {
                "id": "init14",
                "type": 1,
                "initiatorId": "boga",
                "path": "/",
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "parentHost": {
                    "id": "fs_16"
                }
            }
        },
        {
            "content": {
                "id": "init11",
                "type": 2,
                "initiatorId": "fs2",
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "parentHost": {
                    "id": "host_20"
                }
            }
        }
    ]
}
GET_ALL_INIT_NULL = {
    "entries": [
    ]
}
INIT_RESULT = [
    {
        'name': 'fs1',
        'storage_id': '12345',
        'native_storage_host_initiator_id': 'init1',
        'wwn': 'fs1',
        'status': 'online',
        'type': 'fc',
        'native_storage_host_id': 'fs_1'
    }, {
        'name': 'boga',
        'storage_id': '12345',
        'native_storage_host_initiator_id': 'init14',
        'wwn': 'boga',
        'status': 'online',
        'type': 'fc',
        'native_storage_host_id': 'fs_16'
    }, {
        'name': 'fs2',
        'storage_id': '12345',
        'native_storage_host_initiator_id': 'init11',
        'wwn': 'fs2',
        'status': 'online',
        'type': 'iscsi',
        'native_storage_host_id': 'host_20'
    }
]
GET_ALL_HOST = {
    "entries": [
        {
            "content": {
                "id": "host1",
                "type": 1,
                "name": "fs1",
                "description": "test",
                "osType": "AIX",
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "parentHost": {
                    "id": "fs_1"
                }
            }
        },
        {
            "content": {
                "id": "host2",
                "type": 1,
                "name": "boga",
                "description": "test",
                "osType": "Citrix XenServer",
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "parentHost": {
                    "id": "fs_16"
                }
            }
        },
        {
            "content": {
                "id": "host3",
                "type": 2,
                "name": "fs2",
                "description": "test",
                "osType": "VMware ESXi 6.5",
                "health": {
                    "value": 5,
                    "descriptionIds": [
                        "ALRT_COMPONENT_OK"
                    ],
                    "descriptions": [
                        "The component is operating normally."
                    ]
                },
                "parentHost": {
                    "id": "host_20"
                }
            }
        }
    ]
}
GET_ALL_HOST_NULL = {
    "entries": [
    ]
}
GET_HOST_IP = {
    "entries": [
        {
            "content": {
                "id": "ip1",
                "address": "1.1.1.1",
                "host": {
                    "id": "host1"
                }
            }
        },
        {
            "content": {
                "id": "ip1",
                "address": "1.1.1.2",
                "host": {
                    "id": "host2"
                }
            }
        },
        {
            "content": {
                "id": "ip1",
                "address": "1.1.1.1",
                "host": {
                    "id": "host3"
                }
            }
        }
    ]
}
HOST_RESULT = [
    {
        'name': 'fs1',
        'description': 'test',
        'storage_id': '12345',
        'native_storage_host_id': 'host1',
        'os_type': 'AIX',
        'status': 'normal',
        'ip_address': '1.1.1.1'
    }, {
        'name': 'boga',
        'description': 'test',
        'storage_id': '12345',
        'native_storage_host_id': 'host2',
        'os_type': 'XenServer',
        'status': 'normal',
        'ip_address': '1.1.1.2'
    }, {
        'name': 'fs2',
        'description': 'test',
        'storage_id': '12345',
        'native_storage_host_id': 'host3',
        'os_type': 'VMware ESX',
        'status': 'normal',
        'ip_address': '1.1.1.1'
    }
]
GET_HOST_LUN = {
    "entries": [
        {
            "content": {
                "id": "1",
                "lun": {
                    "id": "lun1"
                },
                "host": {
                    "id": "host1"
                }
            }
        },
        {
            "content": {
                "id": "2",
                "lun": {
                    "id": "lun2"
                },
                "host": {
                    "id": "host2"
                }
            }
        },
        {
            "content": {
                "id": "3",
                "lun": {
                    "id": "lun3"
                },
                "host": {
                    "id": "host3"
                }
            }
        }
    ]
}
GET_HOST_LUN_NULL = {
    "entries": [
    ]
}
VIEW_RESULT = [
    {
        'name': '1',
        'native_storage_host_id': 'host1',
        'storage_id': '12345',
        'native_volume_id': 'lun1',
        'native_masking_view_id': '1'
    }, {
        'name': '2',
        'native_storage_host_id': 'host2',
        'storage_id': '12345',
        'native_volume_id': 'lun2',
        'native_masking_view_id': '2'
    }, {
        'name': '3',
        'native_storage_host_id': 'host3',
        'storage_id': '12345',
        'native_volume_id': 'lun3',
        'native_masking_view_id': '3'
    }
]


class TestUNITYStorDriver(TestCase):

    @mock.patch.object(RestHandler, 'get_all_pools')
    def test_list_storage_pools(self, mock_pool):
        RestHandler.login = mock.Mock(return_value=None)
        mock_pool.return_value = GET_ALL_POOLS
        pool = UnityStorDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])
        mock_pool.return_value = GET_ALL_ABNORMAL_POOLS
        pool = UnityStorDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_abnormal_result[0])

    @mock.patch.object(RestHandler, 'get_all_disks')
    @mock.patch.object(RestHandler, 'get_storage')
    @mock.patch.object(RestHandler, 'get_capacity')
    @mock.patch.object(RestHandler, 'get_soft_version')
    def test_get_storage(self, mock_version, mock_capa, mock_base, mock_disk):
        RestHandler.login = mock.Mock(return_value=None)
        mock_version.return_value = GET_SOFT_VERSION
        mock_capa.return_value = GET_CAPACITY
        mock_base.return_value = GET_STORAGE_ABNORMAL
        mock_disk.return_value = GET_ALL_DISKS
        storage = UnityStorDriver(**ACCESS_INFO).get_storage(context)
        self.assertDictEqual(storage, storage_abnormal_result)
        mock_base.return_value = GET_STORAGE_NORMAL
        storage = UnityStorDriver(**ACCESS_INFO).get_storage(context)
        self.assertDictEqual(storage, storage_normal_result)

    @mock.patch.object(RestHandler, 'get_all_luns')
    def test_list_volumes(self, mock_lun):
        RestHandler.login = mock.Mock(return_value=None)
        mock_lun.side_effect = [GET_ALL_LUNS, GET_ALL_LUNS_NULL]
        volume = UnityStorDriver(**ACCESS_INFO).list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    def test_parse_alert(self):
        RestHandler.login = mock.Mock(return_value=None)
        trap = UnityStorDriver(**ACCESS_INFO).parse_alert(context, TRAP_INFO)
        trap['occur_time'] = int(1605852610000)
        self.assertEqual(trap, trap_result)
        trap = UnityStorDriver(**ACCESS_INFO).parse_alert(
            context, TRAP_NOT_IN_MAPPPING_INFO)
        trap['occur_time'] = int(1605852610000)
        self.assertEqual(trap, trap_not_in_mapping_result)

    @mock.patch.object(RestHandler, 'remove_alert')
    def test_clear_alert(self, mock_remove):
        RestHandler.login = mock.Mock(return_value=None)
        alert_id = 101
        UnityStorDriver(**ACCESS_INFO).clear_alert(context, alert_id)
        self.assertEqual(mock_remove.call_count, 1)

    @mock.patch.object(RestHandler, 'get_all_alerts')
    def test_list_alerts(self, mock_alert):
        RestHandler.login = mock.Mock(return_value=None)
        mock_alert.side_effect = [GET_ALL_ALERTS, GET_ALL_ALERTS_NULL]
        alert = UnityStorDriver(**ACCESS_INFO).list_alerts(context)
        alert_result[0]['occur_time'] = alert[0]['occur_time']
        self.assertEqual(alert[0], alert_result[0])

    @mock.patch.object(RestHandler, 'call_with_token')
    def test_call_and_login(self, mock_token):
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(status_code=401,
                                                     text='Unauthorized')
            UnityStorDriver(**ACCESS_INFO).rest_handler.login()
        self.assertEqual('Invalid username or password.', str(exc.exception))
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(status_code=401,
                                                     text='Forbidden')
            UnityStorDriver(**ACCESS_INFO).rest_handler.login()
        self.assertEqual('Invalid ip or port.', str(exc.exception))
        with self.assertRaises(Exception) as exc:
            mock_token.return_value = mock.MagicMock(status_code=503)
            UnityStorDriver(**ACCESS_INFO).rest_handler.call('')
        self.assertIn('Exception from Storage Backend', str(exc.exception))
        RestHandler.login = mock.Mock(return_value=None)
        mock_token.return_value = mock.MagicMock(status_code=401)
        UnityStorDriver(**ACCESS_INFO).rest_handler.call('')

    @mock.patch.object(RestHandler, 'call')
    def test_get_rest_info(self, mock_rest):
        RestHandler.login = mock.Mock(return_value=None)
        mock_rest.return_value = mock.MagicMock(status_code=200)
        UnityStorDriver(**ACCESS_INFO).rest_handler.get_rest_info('')
        self.assertEqual(mock_rest.call_count, 1)

    @mock.patch.object(RestHandler, 'get_all_controllers')
    def test_list_controllers(self, mock_controller):
        RestHandler.login = mock.Mock(return_value=None)
        mock_controller.return_value = GET_ALL_CONTROLLERS
        controller = UnityStorDriver(**ACCESS_INFO).list_controllers(context)
        self.assertEqual(controller, controller_result)

    @mock.patch.object(RestHandler, 'get_all_disks')
    def test_list_disks(self, mock_disk):
        RestHandler.login = mock.Mock(return_value=None)
        mock_disk.return_value = GET_ALL_DISKS
        disk = UnityStorDriver(**ACCESS_INFO).list_disks(context)
        self.assertEqual(disk, disk_result)

    @mock.patch.object(RestHandler, 'get_all_ethports')
    @mock.patch.object(RestHandler, 'get_port_interface')
    @mock.patch.object(RestHandler, 'get_all_fcports')
    def test_list_ports(self, mock_fc, mock_ip, mock_eth):
        RestHandler.login = mock.Mock(return_value=None)
        mock_eth.return_value = GET_ALL_ETHPORTS
        mock_ip.return_value = GET_ALL_IP
        mock_fc.return_value = GET_ALL_FCPORTS
        port = UnityStorDriver(**ACCESS_INFO).list_ports(context)
        self.assertEqual(port, port_result)

    @mock.patch.object(RestHandler, 'get_all_filesystems')
    def test_list_filesystems(self, mock_filesystem):
        RestHandler.login = mock.Mock(return_value=None)
        mock_filesystem.return_value = GET_ALL_FILESYSTEMS
        file = UnityStorDriver(**ACCESS_INFO).list_filesystems(context)
        self.assertEqual(file, filesystem_result)

    @mock.patch.object(RestHandler, 'get_all_qtrees')
    def test_list_qtrees(self, mock_qtree):
        RestHandler.login = mock.Mock(return_value=None)
        mock_qtree.return_value = GET_ALL_QTREE
        qtree = UnityStorDriver(**ACCESS_INFO).list_qtrees(context)
        self.assertEqual(qtree, qtree_result)

    @mock.patch.object(RestHandler, 'get_all_nfsshares')
    @mock.patch.object(RestHandler, 'get_all_cifsshares')
    @mock.patch.object(RestHandler, 'get_all_qtrees')
    @mock.patch.object(RestHandler, 'get_all_filesystems')
    def test_list_shares(self, mock_file, mock_qtree, mock_cifs, mock_nfs):
        RestHandler.login = mock.Mock(return_value=None)
        mock_cifs.return_value = GET_ALL_CIFSSHARE
        mock_qtree.return_value = GET_ALL_QTREE
        mock_nfs.return_value = GET_ALL_NFSSHARE
        mock_file.return_value = GET_ALL_FILESYSTEMS
        share = UnityStorDriver(**ACCESS_INFO).list_shares(context)
        self.assertEqual(share, share_result)

    @mock.patch.object(RestHandler, 'get_all_qtrees')
    @mock.patch.object(RestHandler, 'get_all_userquotas')
    def test_list_quotas(self, mock_user, mock_qtree):
        RestHandler.login = mock.Mock(return_value=None)
        mock_user.return_value = GET_ALL_USERQUOTA
        mock_qtree.return_value = GET_ALL_QTREE
        quota = UnityStorDriver(**ACCESS_INFO).list_quotas(context)
        self.assertEqual(quota, quota_result)

    @mock.patch.object(RestHandler, 'get_history_metrics')
    def test_collect_perf_metrics(self, mock_history):
        RestHandler.login = mock.Mock(return_value=None)
        start_time = 1625726770000
        end_time = 1625726830000
        storage_id = '12345'
        mock_history.side_effect = [GET_VOLUME_READ_THR_PERF,
                                    GET_VOLUME_READ_THR_PERF_NULL,
                                    GET_VOLUME_WRITE_THR_PERF,
                                    GET_VOLUME_WRITE_THR_PERF_NULL,
                                    GET_VOLUME_READ_IOPS_PERF,
                                    GET_VOLUME_READ_IOPS_PERF_NULL,
                                    GET_VOLUME_WRITE_IOPS_PERF,
                                    GET_VOLUME_WRITE_IOPS_PERF_NULL,
                                    GET_VOLUME_READ_IO_PERF,
                                    GET_VOLUME_READ_IO_PERF_NULL,
                                    GET_VOLUME_WRITE_IO_PERF,
                                    GET_VOLUME_WRITE_IO_PERF_NULL,
                                    GET_VOLUME_RESPONSE_PERF,
                                    GET_VOLUME_RESPONSE_PERF_NULL,
                                    GET_DISK_READ_THR_PERF,
                                    GET_DISK_READ_THR_PERF_NULL,
                                    GET_DISK_WRITE_THR_PERF,
                                    GET_DISK_WRITE_THR_PERF_NULL,
                                    GET_DISK_READ_IOPS_PERF,
                                    GET_DISK_READ_IOPS_PERF_NULL,
                                    GET_DISK_WRITE_IOPS_PERF,
                                    GET_DISK_WRITE_IOPS_PERF_NULL,
                                    GET_DISK_RESPONSE_PERF,
                                    GET_DISK_RESPONSE_PERF_NULL,
                                    GET_ETH_PORT_READ_THR_PERF,
                                    GET_ETH_PORT_READ_THR_PERF_NULL,
                                    GET_ETH_PORT_WRITE_THR_PERF,
                                    GET_ETH_PORT_WRITE_THR_PERF_NULL,
                                    GET_FC_PORT_READ_THR_PERF,
                                    GET_ETH_PORT_READ_THR_PERF,
                                    GET_ETH_PORT_READ_THR_PERF_NULL,
                                    GET_ETH_PORT_WRITE_THR_PERF,
                                    GET_ETH_PORT_WRITE_THR_PERF_NULL,
                                    GET_FC_PORT_READ_THR_PERF,
                                    GET_FC_PORT_READ_THR_PERF_NULL,
                                    GET_FC_PORT_WRITE_THR_PERF,
                                    GET_FC_PORT_WRITE_THR_PERF_NULL,
                                    GET_FC_PORT_READ_IOPS_PERF,
                                    GET_FC_PORT_READ_IOPS_PERF_NULL,
                                    GET_FC_PORT_WRITE_IOPS_PERF,
                                    GET_FC_PORT_WRITE_IOPS_PERF_NULL,
                                    GET_FILE_READ_THR_PERF,
                                    GET_FILE_READ_THR_PERF_NULL,
                                    GET_FILE_WRITE_THR_PERF,
                                    GET_FILE_WRITE_THR_PERF_NULL,
                                    GET_FILE_READ_IOPS_PERF,
                                    GET_FILE_READ_IOPS_PERF_NULL,
                                    GET_FILE_WRITE_IOPS_PERF,
                                    GET_FILE_WRITE_IOPS_PERF_NULL,
                                    GET_FILE_READ_IO_PERF,
                                    GET_FILE_READ_IO_PERF_NULL,
                                    GET_FILE_WRITE_IO_PERF,
                                    GET_FILE_WRITE_IO_PERF_NULL]
        metrics = UnityStorDriver(**ACCESS_INFO).collect_perf_metrics(
            context, storage_id, resource_metrics, start_time, end_time)
        self.assertEqual(metrics[0][1]['resource_id'], 'volume0')

    @mock.patch.object(RestHandler, 'get_history_metrics')
    def test_latest_perf_timestamp(self, mock_history):
        RestHandler.login = mock.Mock(return_value=None)
        mock_history.return_value = GET_VOLUME_READ_THR_PERF
        last_time = UnityStorDriver(**ACCESS_INFO).get_latest_perf_timestamp(
            context)
        self.assertEqual(last_time, 1625726830000)

    @mock.patch.object(RestHandler, 'get_host_initiators')
    def test_host_initiators(self, mock_init):
        RestHandler.login = mock.Mock(return_value=None)
        mock_init.side_effect = [GET_ALL_INIT, GET_ALL_INIT_NULL]
        initiators = UnityStorDriver(
            **ACCESS_INFO).list_storage_host_initiators(context)
        self.assertEqual(initiators, INIT_RESULT)

    @mock.patch.object(RestHandler, 'get_all_hosts')
    @mock.patch.object(RestHandler, 'get_host_ip')
    def test_hosts(self, mock_ip, mock_host):
        RestHandler.login = mock.Mock(return_value=None)
        mock_host.side_effect = [GET_ALL_HOST, GET_ALL_HOST_NULL]
        mock_ip.return_value = GET_HOST_IP
        hosts = UnityStorDriver(**ACCESS_INFO).list_storage_hosts(context)
        self.assertEqual(hosts, HOST_RESULT)

    @mock.patch.object(RestHandler, 'get_host_lun')
    def test_masking_views(self, mock_view):
        RestHandler.login = mock.Mock(return_value=None)
        mock_view.side_effect = [GET_HOST_LUN, GET_HOST_LUN_NULL]
        views = UnityStorDriver(**ACCESS_INFO).list_masking_views(context)
        self.assertEqual(views, VIEW_RESULT)
