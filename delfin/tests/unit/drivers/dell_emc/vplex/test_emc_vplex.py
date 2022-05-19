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
from unittest import TestCase, mock

from delfin import context
from delfin.drivers.dell_emc.vplex.rest_handler import RestHandler
from delfin.drivers.dell_emc.vplex.vplex_stor import VplexStorageDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vplex",
    "rest": {
        "host": "8.44.162.250",
        "port": 443,
        "username": "service",
        "password": "Abcdef@123"
    }
}

TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.21.0',
    '1.3.6.1.4.1.1139.21.1.5.0': 'this is test',
    '1.3.6.1.4.1.1139.21.1.3.0': '123321'
}

trap_result = {
    'alert_id': '123321',
    'alert_name': 'this is test',
    'severity': 'Informational',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1614067724000,
    'description': 'this is test',
    'resource_type': 'Storage',
    'location': '',
    'match_key': '8c6d115258631625b625486f81b09532'
}

GET_ALL_CLUSTER = {
    "context": [{
        "children": [{
            "name": "cluster-1",
            "type": "cluster"
        }
        ]
    }
    ]
}

GET_ALL_LUNS = {
    "context": [
        {
            "children": [
                {
                    "name": "device_VPLEX_LUN0_1_vol",
                    "type": "virtual-volume"
                }
            ]
        }
    ]
}

GET_LUN = {
    "context": [
        {
            "attributes": [
                {
                    "name": "capacity",
                    "value": "644245094400B"
                },
                {
                    "name": "health-state",
                    "value": "ok"
                },
                {
                    "name": "operational-status",
                    "value": "ok"
                },
                {
                    "name": "supporting-device",
                    "value": "device__VPLEX_LUN0_1"
                },
                {
                    "name": "thin-enabled",
                    "value": "unavailable"
                },
                {
                    "name": "vpd-id",
                    "value": "VPD83T3:60000000000000000000000000000000"
                }
            ]
        }
    ]
}
volume_result = [{
    'name': 'device_VPLEX_LUN0_1_vol',
    'storage_id': '12345',
    'description': 'EMC VPlex volume',
    'status': 'normal',
    'native_volume_id': 'VPD83T3:60000000000000000000000000000000',
    'native_storage_pool_id': 'device__VPLEX_LUN0_1',
    'type': 'thick',
    'total_capacity': 644245094400,
    'used_capacity': 644245094400,
    'free_capacity': 0,
    'wwn': '60000000000000000000000000000000'
}
]

GET_ALL_POOLS = {
    "context": [
        {
            "children": [
                {
                    "name": "Device_KLM_test01",
                    "type": "local-device"
                }
            ]
        }
    ]
}

GET_POOL = {
    "context": [
        {
            "attributes": [
                {
                    "name": "capacity",
                    "value": "732212254720B"
                },
                {
                    "name": "health-state",
                    "value": "ok"
                },
                {
                    "name": "operational-status",
                    "value": "ok"
                },
                {
                    "name": "system-id",
                    "value": "Device_KLM_test01"
                },
                {
                    "name": "virtual-volume",
                    "value": "Volume_CLARiiON0041_KLM_test01"
                }
            ]
        }
    ]
}

pool_result = [
    {
        'name': 'Device_KLM_test01',
        'storage_id': '12345',
        'native_storage_pool_id': 'Device_KLM_test01',
        'description': 'EMC VPlex Pool',
        'status': 'normal',
        'storage_type': 'block',
        'total_capacity': 732212254720,
        'used_capacity': 732212254720,
        'free_capacity': 0
    }
]

GET_HEALH_CHECK = {
    "context": None,
    "message": "health-check -l",
    "exception": None,
    "custom-data": "Product Version: 6.1.0.01.00.13\n"
                   "Product Type: Local\n"
}

GET_CLUSTER = {
    "context": [
        {
            "type": "cluster",
            "parent": "/clusters",
            "attributes": [
                {
                    "name": "health-state",
                    "value": "major-failure"
                },
                {
                    "name": "operational-status",
                    "value": "degraded"
                },
                {
                    "name": "top-level-assembly",
                    "value": "FNM00000000000"
                }
            ],
        }
    ]
}

storage_result = {
    'name': 'cluster-1',
    'vendor': 'DELL EMC',
    'description': 'EMC VPlex Storage',
    'status': 'degraded',
    'serial_number': 'FNM00000000000',
    'firmware_version': ' 6.1.0.01.00.13',
    'model': 'EMC VPLEX  Local',
    'location': '',
    'raw_capacity': 12754334882201,
    'total_capacity': 11654823254425,
    'used_capacity': 8983009998929,
    'free_capacity': 2671813255496
}

GET_ALL_STORAGE_VOLUME_SUMMARY = {
    "custom-data": "Capacity                total         11.6T\n\n"
}

GET_ALL_POOLS_SUMMARY = {
    "custom-data": "total capacity    1.88T  total capacity    "
                   "8.68T  total capacity    10.6T\n\n"
}

GET_ALL_LUNS_SUMMARY = {
    "custom-data": "Total virtual-volume capacity is 8.17T."
}

GET_ALL_ENGINE_DIRECTOR = {
    "context": [
        {
            "type": "director",
            "parent": "/engines/engine-1-1/directors",
            "attributes": [
                {
                    "name": "director-id",
                    "value": "0x00000000472029e9"
                },
                {
                    "name": "communication-status",
                    "value": "ok"
                },
                {
                    "name": "name",
                    "value": "director-1-1-A"
                }
            ]
        }
    ]
}

controllers_result = [
    {
        'native_controller_id': '0x00000000472029e9',
        'name': 'director-1-1-A',
        'status': 'normal',
        'location': '',
        'storage_id': '12345',
        'soft_version': '161.1.0.78.0',
        'cpu_info': '',
        'memory_size': ''
    }
]

GET_VERSION_VERBOSE = {
    "context": None,
    "message": "getsysinfo",
    "exception": None,
    "custom-data": "What:     Mgmt Server Software\nVersion:  161.1.0.78\n	"
                   "For director /engines/engine-1-1/directors/director-1-1-A:"
                   "\n	"
                   "What:     O/S\n	"
                   "Version:  161.1.0.11 (SLES11)\n\n	"
                   "What:     NSFW\n	"
                   "Version:  161.1.0.78.0\n\n	"
                   "What:      ZPEM\n	"
                   "Version:  161.1.0.78.0-0\n	"
                   "What:     Director Software\n	"
                   "Version:  161.1.0.78.0\n\n	"
                   "What:     SSD Model: P30056-0000000000000 000000000\n	"
                   "Version:  0005\n"
}

GET_ALL_CLUSTER_EXPORT_PORT = {
    "context": [
        {
            "type": "fc-target-port",
            "parent": "/clusters/cluster-1/exports/ports",
            "attributes": [
                {
                    "name": "director-id",
                    "value": "0x00000000472029e9"
                },
                {
                    "name": "enabled",
                    "value": "true"
                },
                {
                    "name": "export-status",
                    "value": "ok"
                },
                {
                    "name": "name",
                    "value": "P00000000472029E9-A0-FC00"
                },
                {
                    "name": "node-wwn",
                    "value": "0x50001440472029e9"
                },
                {
                    "name": "port-id",
                    "value": None
                },
                {
                    "name": "port-wwn",
                    "value": "0x500014428029e900"
                }
            ]
        }
    ]
}

GET_ALL_ENGINE_DIRECTOR_HARDWARE_PORT = {
    "context": [
        {
            "type": "fc-port",
            "parent": "/engines/engine-1-1/directors/director-1-1-A/"
                      "hardware/ports",
            "attributes": [
                {
                    "name": "address",
                    "value": "0x500014428029e900"
                },
                {
                    "name": "current-speed",
                    "value": "8Gbits/s"
                },
                {
                    "name": "enabled",
                    "value": "true"
                },
                {
                    "name": "max-speed",
                    "value": "8Gbits/s"
                },
                {
                    "name": "name",
                    "value": "A0-FC00"
                },
                {
                    "name": "node-wwn",
                    "value": "0x50001440472029e9"
                },
                {
                    "name": "operational-status",
                    "value": "ok"
                },
                {
                    "name": "port-status",
                    "value": "up"
                },
                {
                    "name": "port-wwn",
                    "value": "0x500014428029e900"
                },
                {
                    "name": "protocols",
                    "value": [
                        "fc"
                    ]
                },
                {
                    "name": "role",
                    "value": "front-end"
                },
                {
                    "name": "target-port",
                    "value": "P00000000472029E9-A0-FC00"
                }
            ]
        }
    ]
}

ports_result = [
    {
        'native_port_id': 'P00000000472029E9-A0-FC00',
        'name': 'P00000000472029E9-A0-FC00',
        'type': 'fc',
        'logical_type': 'frontend',
        'connection_status': 'connected',
        'health_status': 'normal',
        'location': '',
        'storage_id': '12345',
        'native_parent_id': '0x00000000472029e9',
        'speed': 8000000000,
        'max_speed': 8000000000,
        'wwn': '0x500014428029e900',
        'mac_address': '',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': '',
        'ipv6_mask': ''
    }
]

GET_STORAGE_VIEW = {
    "context": [
        {
            "type": "storage-view",
            "parent": "/clusters/cluster-1/exports/storage-views",
            "attributes": [
                {
                    "name": "caw-enabled",
                    "value": "true"
                },
                {
                    "name": "controller-tag",
                    "value": None
                },
                {
                    "name": "initiators",
                    "value": ["CHEN_LINUX"]
                },
                {
                    "name": "name",
                    "value": "CHEN_LINUX"
                },
                {
                    "name": "operational-status",
                    "value": "ok"
                },
                {
                    "name": "port-name-enabled-status",
                    "value": ["P0000000047302920-B0-FC00,true,ok"
                              ]
                },
                {
                    "name": "ports",
                    "value": [
                        "P0000000047302920-B0-FC00"
                    ]
                },
                {
                    "name": "scsi-spc-version",
                    "value": "2"
                },
                {
                    "name": "virtual-volumes",
                    "value": [
                        "(0,device_wcj_hp_3_c1_vol,123,16G)",
                        "(1,dg_ocr,456,100G)"
                    ]
                },
                {
                    "name": "write-same-16-enabled",
                    "value": "true"
                },
                {
                    "name": "xcopy-enabled",
                    "value": "true"
                }
            ],
            "children": []
        }
    ]
}

GET_INITIATORS_PORT = {
    "context": [
        {
            "type": "fc-initiator-port",
            "parent": "/clusters/cluster-1/exports/initiator-ports",
            "attributes": [
                {
                    "name": "name",
                    "value": "CHEN_LINUX"
                },
                {
                    "name": "node-wwn",
                    "value": "0x21000024ff7fb74d"
                },
                {
                    "name": "port-wwn",
                    "value": "0x21000024ff7fb74d"
                },
                {
                    "name": "scsi-spc-version",
                    "value": "2"
                },
                {
                    "name": "suspend-on-detach",
                    "value": None
                },
                {
                    "name": "target-ports",
                    "value": [
                        "P0000000047302920-B0-FC03",
                        "P0000000047302920-B0-FC01"
                    ]
                },
                {
                    "name": "type",
                    "value": "default"
                }
            ],
            "children": []
        }
    ]
}

list_port_groups_result = {
    'port_groups': [
        {
            'name': 'port_group_CHEN_LINUX',
            'description': 'port_group_CHEN_LINUX',
            'storage_id': '12345',
            'native_port_group_id': 'port_group_CHEN_LINUX',
            'ports': [
                'P0000000047302920-B0-FC00'
            ]
        }
    ],
    'port_grp_port_rels': [
        {
            "storage_id": "12345",
            "native_port_group_id": "port_group_CHEN_LINUX",
            "native_port_id": "P0000000047302920-B0-FC00"
        }
    ]
}

list_storage_host_initiators_result = [
    {
        'name': 'CHEN_LINUX',
        'type': 'fc',
        'storage_id': '12345',
        'native_storage_host_initiator_id': '0x21000024ff7fb74d',
        'wwn': '0x21000024ff7fb74d',
        'alias': '0x21000024ff7fb74d',
        'status': 'online',
        'native_storage_host_id': '0x21000024ff7fb74d'
    }
]

list_storage_hosts_result = [
    {
        'name': 'CHEN_LINUX',
        'os_type': 'Unknown',
        'storage_id': '12345',
        'native_storage_host_id': '0x21000024ff7fb74d',
        'status': 'normal'
    }
]

list_masking_views_result = [
    {
        'name': 'CHEN_LINUX',
        'description': 'CHEN_LINUX',
        'storage_id': '12345',
        'native_masking_view_id': 'CHEN_LINUX123',
        'native_port_group_id': 'port_group_CHEN_LINUX',
        'native_volume_id': '123',
        'native_storage_host_id': '0x21000024ff7fb74d'
    },
    {
        'name': 'CHEN_LINUX',
        'description': 'CHEN_LINUX',
        'storage_id': '12345',
        'native_masking_view_id': 'CHEN_LINUX',
        'native_port_group_id': 'port_group_CHEN_LINUX',
        'native_volume_id': '456',
        'native_storage_host_id': '0x21000024ff7fb74d'
    }
]


class TestVplexStorDriver(TestCase):
    RestHandler.login = mock.Mock(return_value=None)

    def test_parse_alert(self):
        trap = VplexStorageDriver(**ACCESS_INFO).parse_alert(context,
                                                             TRAP_INFO)
        trap_result['occur_time'] = trap['occur_time']
        self.assertDictEqual(trap, trap_result)

    @mock.patch.object(RestHandler, 'get_cluster_resp')
    @mock.patch.object(RestHandler, 'get_virtual_volume_resp')
    @mock.patch.object(RestHandler, 'get_virtual_volume_by_name_resp')
    def test_list_volumes(self, mock_name, mock_volume, mock_cluster):
        mock_cluster.return_value = GET_ALL_CLUSTER
        mock_volume.return_value = GET_ALL_LUNS
        mock_name.return_value = GET_LUN
        volume = VplexStorageDriver(**ACCESS_INFO).list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    @mock.patch.object(RestHandler, 'get_cluster_resp')
    @mock.patch.object(RestHandler, 'get_devcie_resp')
    @mock.patch.object(RestHandler, 'get_device_by_name_resp')
    def test_list_storage_pools(self, mock_name, mock_device, mock_cluster):
        mock_cluster.return_value = GET_ALL_CLUSTER
        mock_device.return_value = GET_ALL_POOLS
        mock_name.return_value = GET_POOL
        pool = VplexStorageDriver(**ACCESS_INFO).list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])

    def test_get_storage(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[GET_HEALH_CHECK, GET_ALL_CLUSTER, GET_CLUSTER,
                         GET_ALL_STORAGE_VOLUME_SUMMARY, GET_ALL_POOLS_SUMMARY,
                         GET_ALL_LUNS_SUMMARY])
        storage = VplexStorageDriver(**ACCESS_INFO).get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_alerts(self):
        with self.assertRaises(Exception) as exc:
            VplexStorageDriver(**ACCESS_INFO).list_alerts(context)
        self.assertEqual('list_alerts is not supported in model VPLEX',
                         str(exc.exception))

    @mock.patch.object(RestHandler, 'get_version_verbose')
    @mock.patch.object(RestHandler, 'get_engine_director_resp')
    def test_list_controller(self, mock_controller, mocke_version):
        mocke_version.return_value = GET_VERSION_VERBOSE
        mock_controller.return_value = GET_ALL_ENGINE_DIRECTOR
        controllers = VplexStorageDriver(**ACCESS_INFO). \
            list_controllers(context)
        self.assertDictEqual(controllers[0], controllers_result[0])

    @mock.patch.object(RestHandler, 'get_cluster_export_port_resp')
    @mock.patch.object(RestHandler, 'get_engine_director_hardware_port_resp')
    def test_list_port(self, mock_hardware_port, mock_export_port):
        mock_hardware_port.return_value = GET_ALL_ENGINE_DIRECTOR_HARDWARE_PORT
        mock_export_port.return_value = GET_ALL_CLUSTER_EXPORT_PORT
        ports = VplexStorageDriver(**ACCESS_INFO).list_ports(context)
        self.assertDictEqual(ports[0], ports_result[0])

    @mock.patch.object(RestHandler, 'get_storage_views')
    def test_list_port_groups(self, mock_storage_view):
        mock_storage_view.return_value = GET_STORAGE_VIEW
        list_port_groups = VplexStorageDriver(**ACCESS_INFO).\
            list_port_groups(context)
        port_groups_result = {
            'port_groups': list_port_groups.get('port_groups'),
            'port_grp_port_rels': list_port_groups.get('port_grp_port_rels')
        }
        self.assertDictEqual(port_groups_result, list_port_groups_result)

    @mock.patch.object(RestHandler, 'get_initiators_resp')
    def test_list_storage_hosts(self, mock_storage_view):
        mock_storage_view.return_value = GET_INITIATORS_PORT
        list_storage_hosts = VplexStorageDriver(**ACCESS_INFO). \
            list_storage_hosts(context)
        self.assertDictEqual(list_storage_hosts[0],
                             list_storage_hosts_result[0])

    @mock.patch.object(RestHandler, 'get_storage_views')
    @mock.patch.object(VplexStorageDriver, 'list_storage_hosts')
    def test_list_masking_views(self, mock_storage_view, mock_storage_hosts):
        mock_storage_view.return_value = list_storage_hosts_result
        mock_storage_hosts.return_value = GET_STORAGE_VIEW
        list_masking_views = VplexStorageDriver(**ACCESS_INFO). \
            list_masking_views(context)
        self.assertDictEqual(list_masking_views[0],
                             list_masking_views_result[0])

    @mock.patch.object(RestHandler, 'get_initiators_resp')
    def test_list_storage_host_initiators(self, mock_initiators_port):
        mock_initiators_port.return_value = GET_INITIATORS_PORT
        list_storage_host_initiators = VplexStorageDriver(**ACCESS_INFO). \
            list_storage_host_initiators(context)
        self.assertDictEqual(list_storage_host_initiators[0],
                             list_storage_host_initiators_result[0])
