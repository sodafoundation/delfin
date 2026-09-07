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
import logging
import sys
from unittest import mock, TestCase

import six

from delfin import context
from delfin.common import constants
from delfin.drivers.dell_emc.power_store import consts
from delfin.drivers.utils.rest_client import RestClient

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin.drivers.dell_emc.power_store.power_store import PowerStoreDriver
from delfin.drivers.dell_emc.power_store.rest_handler import RestHandler

ACCESS_INFO = {
    "storage_id": "12345",
    "rest": {
        "host": "192.168.33.241",
        "port": 443,
        "username": "admin",
        "password": "password"
    }
}
clusters = [
    {
        "id": "0",
        "global_id": "PS0234fd139f29",
        "name": "Powerstore1000T",
        "physical_mtu": 1500,
        "master_appliance_id": "A1",
        "primary_appliance_id": "A1",
        "state": "Configured",
        "appliance_count": 1,
        "management_address": "192.168.3.241",
        "compatibility_level": 15,
        "system_time": "2022-11-23T03:46:47.317Z",
        "state_l10n": "Configured"
    }
]
appliance = [
    {
        "id": "A1",
        "name": "Powerstore1000T-appliance-1",
        "model": "PowerStore 1000T",
        "drive_failure_tolerance_level": "Single",
        "service_tag": "4YBRFR3",
        "nodes": [
            {
                "id": "N1"
            },
            {
                "id": "N2"
            }
        ],
        "software_installed": [
            {
                "id": "f412271a-987b-47b5-ae8f-46cb895b822b"
            }
        ],
        "volumes": [
            {
                "id": "c557beb6-8112-4aa5-8be6-178d34dfc961"
            }
        ]
    }
]
appliance_capacity = [{
    "appliance_id": "A1",
    "timestamp": "2022-11-23T06:05:00Z",
    "logical_provisioned": 644245094400,
    "logical_used": 0,
    "logical_used_volume": 0,
    "logical_used_file_system": 0,
    "logical_used_vvol": 0,
    "shared_logical_used_volume": 0,
    "shared_logical_used_file_system": 0,
    "shared_logical_used_vvol": 0,
    "physical_total": 6969013934489,
    "physical_used": 5990644187,
    "data_physical_used": 0,
    "efficiency_ratio": 0.0,
    "data_reduction": 0.0,
    "snapshot_savings": 0.0,
    "thin_savings": 0.0,
    "shared_logical_used": 0,
    "repeat_count": 1,
    "response_definition": "space_metrics_by_appliance",
    "entity": "space_metrics_by_appliance"
}]
pools_data = [{'name': 'Powerstore1000T-appliance-1', 'storage_id': '12345',
               'native_storage_pool_id': 'A1', 'status': 'normal',
               'storage_type': 'block', 'total_capacity': 6969013934489,
               'used_capacity': 5990644187, 'free_capacity': 6963023290302}]
node_info = [
    {
        "appliance_id": "A1",
        "id": "N1",
        "slot": 0,
    },
    {
        "appliance_id": "A1",
        "id": "N2",
        "slot": 1,
    }
]
ip_pool_address = [
    {
        "id": "IP1",
        "name": "Default Management Network (192.168.3.241)",
        "address": "192.168.3.241",
        "appliance_id": None,
        "node_id": None,
        "purposes": [
            "Mgmt_Cluster_Floating"
        ],
    },
    {
        "id": "IP16",
        "name": "Default Management Network (192.168.3.245)",
        "address": "192.168.3.245",
        "appliance_id": None,
        "node_id": None,
        "purposes": [
            "Unused"
        ],
    },
    {
        "id": "IP17",
        "name": "Default Management Network (192.168.3.246)",
        "address": "192.168.3.246",
        "appliance_id": None,
        "network_id": "NW1",
        "node_id": None,
        "purposes": [
            "Unused"
        ],
    },
    {
        "id": "IP2",
        "name": "Default Management Network (192.168.3.242)",
        "address": "192.168.3.242",
        "appliance_id": "A1",
        "network_id": "NW1",
        "node_id": None,
        "purposes": [
            "Mgmt_Appliance_Floating"
        ],
    },
    {
        "id": "IP3",
        "name": "Default Management Network (192.168.3.243)",
        "address": "192.168.3.243",
        "appliance_id": "A1",
        "node_id": "N1",
        "purposes": [
            "Mgmt_Node_CoreOS"
        ],
    },
    {
        "id": "IP4",
        "name": "Default Management Network (192.168.3.244)",
        "address": "192.168.3.244",
        "appliance_id": "A1",
        "node_id": "N2",
        "purposes": [
            "Mgmt_Node_CoreOS"
        ],
    },
    {
        "id": "IP8",
        "name": "Default ICM Network (fd4e:c5b3:1db3::201:44f0:49e5:21c3)",
        "address": "fd4e:c5b3:1db3::201:44f0:49e5:21c3",
        "appliance_id": "A1",
        "node_id": "N1",
        "purposes": [
            "ICM_Node_CoreOS"
        ],
    }
]
hardware_info = [
    {
        "appliance_id": "A1",
        "name": "Drive_0_0_24",
        "parent_id": "c8e719e6d68a4fcc9cb9cf5a808db37f",
        "stale_state": "Not_Stale",
        "status_led_state": "Off",
        "extra_details": {
            "firmware_version": "3.1.11.0",
            "drive_type": "NVMe_NVRAM",
            "size": 8484552704,
            "encryption_status": "Disabled",
            "fips_status": "FIPS_Compliance_None"
        },
        "id": "0bd7eaefeaf141b7b1c041aa439e65d9",
        "is_marked": False,
        "lifecycle_state": "Healthy",
        "part_number": "005053655",
        "serial_number": "1A48F300ADB",
        "slot": 24,
        "type": "Drive",
        "appliance": {
            "id": "A1"
        },
        "children": [],
        "parent": {
            "id": "c8e719e6d68a4fcc9cb9cf5a808db37f"
        },
        "hardware_parent_eth_ports": [],
        "hardware_parent_fc_ports": [],
        "hardware_parent_sas_ports": [],
        "io_module_eth_ports": []
    }, {
        "appliance_id": "A1",
        "name": "Drive_0_0_4",
        "parent_id": "c8e719e6d68a4fcc9cb9cf5a808db37f",
        "stale_state": "Not_Stale",
        "status_led_state": "Off",
        "extra_details": {
            "firmware_version": "VPV1ET0K",
            "drive_type": "NVMe_SSD",
            "size": 1920383410176,
            "encryption_status": "Disabled",
            "fips_status": "FIPS_Compliance_None"
        },
        "id": "3dd4393290cc4665bb0649cb06fbc8ea",
        "is_marked": False,
        "lifecycle_state": "Healthy",
        "part_number": "005052920",
        "serial_number": "PHLP040101AK2P0A",
        "slot": 4,
        "type": "Drive",
        "appliance": {
            "id": "A1"
        },
        "children": [],
        "parent": {
            "id": "c8e719e6d68a4fcc9cb9cf5a808db37f"
        },
        "hardware_parent_eth_ports": [],
        "hardware_parent_fc_ports": [],
        "hardware_parent_sas_ports": [],
        "io_module_eth_ports": []
    }, {
        "appliance_id": "A1",
        "name": "BaseEnclosure-NodeA",
        "parent_id": "c8e719e6d68a4fcc9cb9cf5a808db37f",
        "stale_state": "Not_Stale",
        "status_led_state": "Off",
        "extra_details": {
            "physical_memory_size_gb": 192,
            "cpu_model": "Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz",
            "cpu_cores": 8,
            "cpu_sockets": 2
        },
        "id": "3f75d31ca1dc4d8fb95707c7f996a063",
        "is_marked": False,
        "lifecycle_state": "Healthy",
        "part_number": "110-558-301A-00",
        "serial_number": "FXTSP221300674",
        "slot": 0,
        "type": "Node",
        "appliance": {
            "id": "A1"
        },
        "children": [
            {
                "id": "8ae8e0207f9b4145ab3acaf6963941db"
            }
        ],
        "parent": {
            "id": "c8e719e6d68a4fcc9cb9cf5a808db37f"
        },
        "hardware_parent_eth_ports": [],
        "hardware_parent_fc_ports": [],
        "hardware_parent_sas_ports": [],
        "io_module_eth_ports": []
    }, {
        "appliance_id": "A1",
        "name": "BaseEnclosure-NodeB",
        "parent_id": "c8e719e6d68a4fcc9cb9cf5a808db37f",
        "stale_state": "Not_Stale",
        "status_led_state": "Off",
        "extra_details": {
            "physical_memory_size_gb": 192,
            "cpu_model": "Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz",
            "cpu_cores": 8,
            "cpu_sockets": 2
        },
        "id": "5c93d9044ea94afea7d0ac853b89886c",
        "is_marked": False,
        "lifecycle_state": "Healthy",
        "part_number": "110-558-301A-00",
        "serial_number": "FXTSP221300970",
        "slot": 1,
        "type": "Node",
        "appliance": {
            "id": "A1"
        },
        "children": [
            {
                "id": "ef01e2005bcd4f9a8af4fd076a49e34c"
            }
        ],
        "parent": {
            "id": "c8e719e6d68a4fcc9cb9cf5a808db37f"
        },
        "hardware_parent_eth_ports": [],
        "hardware_parent_fc_ports": [],
        "hardware_parent_sas_ports": [],
        "io_module_eth_ports": []
    },
]
disk_data = [{'name': 'Drive_0_0_4', 'storage_id': '12345',
              'native_disk_id': '3dd4393290cc4665bb0649cb06fbc8ea',
              'serial_number': 'PHLP040101AK2P0A', 'manufacturer': 'DELL EMC',
              'firmware': 'VPV1ET0K', 'capacity': 1920383410176,
              'status': 'normal', 'physical_type': 'nvme-ssd',
              'logical_type': 'unknown', 'location': '4'}]
software_installed = [
    {
        "id": "f412271a-987b-47b5-ae8f-46cb895b822b",
        "build_version": "2.1.1.1",
        "release_version": "2.1.1.1",
        "appliance": {
            "id": "A1"
        }
    },
    {
        "id": "f9c0b631-a14f-4d1b-bb28-831de6e78242",
        "build_version": "2.1.1.1",
        "release_version": "2.1.1.1",
        "appliance": None
    }
]
storage_data = {'model': 'PowerStore 1000T', 'total_capacity': 6969013934489,
                'raw_capacity': 1920383410176, 'used_capacity': 5990644187,
                'free_capacity': 6963023290302, 'vendor': 'DELL EMC',
                'name': 'Powerstore1000T', 'serial_number': 'PS0234fd139f29',
                'firmware_version': '2.1.1.1', 'status': 'normal'}
volume_info = [{
    "app_type": "Business_Applications_ERP_SAP",
    "app_type_l10n": "ERP / SAP",
    "appliance_id": "A1",
    "description": "什么 都不是",
    "state": "Ready",
    "type": "Primary",
    "wwn": "naa.68ccf0980048d7ab86ec9f7fdfa9945d",
    "size": 3221225472,
    "name": "wu-003",
    "id": "022ece9c-4921-46ba-ba4f-91c167a90cbe",
    "appliance": {
        "id": "A1"
    }}, {
    "app_type": "Business_Applications_ERP_SAP",
    "app_type_l10n": "ERP / SAP",
    "appliance_id": "A1",
    "description": "什么 都不是",
    "state": "Ready",
    "type": "Snapshot",
    "wwn": "naa.68ccf0980084d02c7649966d51f07a2d",
    "size": 3221225472,
    "name": "wu-013",
    "id": "030c4053-ccd5-40e7-a96a-5d32ea507468",
    "appliance": {
        "id": "A1"
    }},
]
volume_generate = [
    {
        "volume_id": "022ece9c-4921-46ba-ba4f-91c167a90cbe",
        "appliance_id": "A1",
        "timestamp": "2022-11-22T06:55:00Z",
        "logical_provisioned": 3221225472,
        "logical_used": 0,
        "thin_savings": 0.0,
        "repeat_count": 288,
        "response_definition": "space_metrics_by_volume",
        "entity": "space_metrics_by_volume"
    }
]
volume_data = [{'name': 'wu-003', 'storage_id': '12345',
                'description': '什么 都不是', 'status': 'normal',
                'native_volume_id': '022ece9c-4921-46ba-ba4f-91c167a90cbe',
                'native_storage_pool_id': 'A1',
                'wwn': 'naa.68ccf0980048d7ab86ec9f7fdfa9945d', 'type': 'thin',
                'total_capacity': 3221225472, 'used_capacity': 0,
                'free_capacity': 3221225472}]
alerts_info = [
    {
        "id": "0032b92b-e0bc-4259-b572-db562238b4b4",
        "description_l10n": "Management ports are properly connected to"
                            " different management switches.",
        "severity": "Info",
        "resource_name": "BaseEnclosure-NodeB",
        "resource_type": "hardware",
        "acknowledged_timestamp": None,
        "generated_timestamp": "2022-11-09T06:58:14.479496+00:00",
        "cleared_timestamp": "2022-11-09T06:58:14.479496+00:00",
        "resource_id": "5c93d9044ea94afea7d0ac853b89886c",
        "state": "ACTIVE",
        "raised_timestamp": "2022-11-06T06:18:14.446541+00:00",
        "email_sent_timestamp": None,
        "called_home_timestamp": None,
        "is_acknowledged": False,
        "snmp_sent_timestamp": None
    }, {
        "id": "0032b92b-e0bc-4259-b572-db562238b4b5",
        "description_l10n": "Management ports are properly connected to"
                            " different management switches.",
        "severity": "Info",
        "resource_name": "BaseEnclosure-NodeA",
        "resource_type": "hardware",
        "acknowledged_timestamp": None,
        "generated_timestamp": "2022-11-09T06:58:14.479496+00:00",
        "cleared_timestamp": "2022-11-09T06:58:14.479496+00:00",
        "resource_id": "5c93d9044ea94afea7d0ac853b89886c",
        "state": "CLEARED",
        "raised_timestamp": "2022-11-06T06:18:14.446541+00:00",
        "email_sent_timestamp": None,
        "called_home_timestamp": None,
        "is_acknowledged": False,
        "snmp_sent_timestamp": None
    }
]
alerts_data = [{
    'alert_id': '0032b92b-e0bc-4259-b572-db562238b4b4',
    'occur_time': 1667715494446, 'severity': 'Informational',
    'category': 'Fault', 'location': 'hardware:BaseEnclosure-NodeB',
    'type': 'EquipmentAlarm', 'resource_type': 'hardware',
    'alert_name': 'Management ports are properly connected to different '
                  'management switches.',
    'match_key': '0042968d19d8788229f78abb4f842121',
    'description': 'Management ports are properly connected to different '
                   'management switches.'}]
snmp_alert_data = {
    'alert_id': 'b89d0e0a9cec32fc20a21b05071c9d5e',
    'occur_time': 1667708609278, 'severity': 'Major',
    'category': 'Fault', 'location': 'appliance:Powerstore1000T-appliance-1',
    'type': 'EquipmentAlarm', 'resource_type': 'appliance',
    'alert_name': 'All configured DNS servers are unavailable.',
    'match_key': 'b89d0e0a9cec32fc20a21b05071c9d5e',
    'description': 'All configured DNS servers are unavailable.'
}
controllers_data = [
    {'name': 'NodeA', 'storage_id': '12345',
     'native_controller_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'status': 'normal', 'location': 'NodeA:Slot-0',
     'mgmt_ip': '192.168.3.243',
     'cpu_info': 'Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz',
     'cpu_count': 1, 'memory_size': 206158430208},
    {'name': 'NodeB', 'storage_id': '12345',
     'native_controller_id': '5c93d9044ea94afea7d0ac853b89886c',
     'status': 'normal', 'location': 'NodeB:Slot-1',
     'mgmt_ip': '192.168.3.244',
     'cpu_info': 'Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz',
     'cpu_count': 1, 'memory_size': 206158430208}]
alert_sources_data = [{'host': '192.168.3.243'}, {'host': '192.168.3.244'}]
fc_info = [{
    "appliance_id": "A1",
    "current_speed": "16_Gbps",
    "id": "090d75723f4147808fd5624582708381",
    "is_link_up": False,
    "name": "BaseEnclosure-NodeA-IoModule0-FEPort2",
    "partner_id": "ed8e44cab9484f8c92d488a12e5bc6d8",
    "port_connector_type": "LC",
    "supported_speeds": [
        "Auto",
        "8_Gbps",
        "16_Gbps"
    ],
    "wwn": "58:cc:f0:90:4d:22:19:fb",
    "stale_state": "Not_Stale",
    "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
    "sfp_id": "343b016544744268b383294867424252",
}, {
    "appliance_id": "A1",
    "current_speed": None,
    "id": "210d046f161b4c2ebbcfd3090d706370",
    "is_link_up": False,
    "name": "BaseEnclosure-NodeA-IoModule0-FEPort0",
    "partner_id": "78d83f317dc446a3992b24e7cbe4d9bc",
    "port_connector_type": "LC",
    "supported_speeds": [
        "Auto",
        "8_Gbps",
        "16_Gbps"
    ],
    "wwn": "58:cc:f0:90:4d:20:19:fb",
    "stale_state": "Not_Stale",
    "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
    "sfp_id": "16416450ec514ca089cdf83764b1cfec",
}]
hardware_port_info = [{
    "appliance_id": "A1",
    "name": "BaseEnclosure-NodeB-IoModule0-SFP2",
    "parent_id": "ffc6bc05bcd84d7095d380d72c88fc0b",
    "stale_state": "Not_Stale",
    "status_led_state": None,
    "extra_details": {
        "mode": "Multi_Mode",
        "supported_protocol": "FC",
        "connector_type": "LC",
        "supported_speeds": [
            "4_Gbps",
            "8_Gbps",
            "16_Gbps"
        ]
    },
    "id": "343b016544744268b383294867424252",
    "is_marked": None,
    "lifecycle_state": "Healthy",
    "part_number": "019-078-045",
    "serial_number": "P66DEY1         ",
    "slot": 2,
    "type": "SFP",
    "appliance": {
        "id": "A1"
    },
    "children": [],
    "parent": {
        "id": "ffc6bc05bcd84d7095d380d72c88fc0b"
    },
    "hardware_parent_eth_ports": [],
    "hardware_parent_fc_ports": [],
    "hardware_parent_sas_ports": [],
    "io_module_eth_ports": []
}, {
    "appliance_id": "A1",
    "name": "BaseEnclosure-NodeA-IoModule0-SFP0",
    "parent_id": "2f44d24b4332475d90edab9d316c6d9b",
    "stale_state": "Not_Stale",
    "status_led_state": None,
    "extra_details": {
        "mode": "Multi_Mode",
        "supported_protocol": "FC",
        "connector_type": "LC",
        "supported_speeds": [
            "4_Gbps",
            "8_Gbps",
            "16_Gbps"
        ]
    },
    "id": "16416450ec514ca089cdf83764b1cfec",
    "is_marked": None,
    "lifecycle_state": "Healthy",
    "part_number": "019-078-045",
    "serial_number": "P66DD3H         ",
    "slot": 0,
    "type": "SFP",
    "appliance": {
        "id": "A1"
    },
    "children": [],
    "parent": {
        "id": "2f44d24b4332475d90edab9d316c6d9b"
    },
    "hardware_parent_eth_ports": [],
    "hardware_parent_fc_ports": [],
    "hardware_parent_sas_ports": [],
    "io_module_eth_ports": []
}, {
    "appliance_id": "A1",
    "name": "BaseEnclosure-NodeA-4PortCard-SFP1",
    "parent_id": "fd5cb1c32a434ecbba63f79060fa605b",
    "stale_state": "Not_Stale",
    "status_led_state": None,
    "extra_details": {
        "mode": "Unknown",
        "supported_protocol": "Unknown",
        "connector_type": "Unknown",
        "supported_speeds": []
    },
    "id": "e387bf548a8b45a1831982857407adb1",
    "is_marked": None,
    "lifecycle_state": "Empty",
    "part_number": None,
    "serial_number": None,
    "slot": 1,
    "type": "SFP",
    "appliance": {
        "id": "A1"
    },
    "children": [],
    "parent": {
        "id": "fd5cb1c32a434ecbba63f79060fa605b"
    },
    "hardware_parent_eth_ports": [],
    "hardware_parent_fc_ports": [],
    "hardware_parent_sas_ports": [],
    "io_module_eth_ports": []
}, {
    "appliance_id": "A1",
    "name": "BaseEnclosure-NodeA-EmbeddedModule-SFP0",
    "parent_id": "9ba194e115454c3db22a7da88164379e",
    "stale_state": "Not_Stale",
    "status_led_state": None,
    "extra_details": {
        "mode": "Unknown",
        "supported_protocol": "Unknown",
        "connector_type": "Unknown",
        "supported_speeds": []
    },
    "id": "66696ff8755b4e8ca8c853021b7e668f",
    "is_marked": None,
    "lifecycle_state": "Empty",
    "part_number": None,
    "serial_number": None,
    "slot": 0,
    "type": "SFP",
    "appliance": {
        "id": "A1"
    },
    "children": [],
    "parent": {
        "id": "9ba194e115454c3db22a7da88164379e"
    },
    "hardware_parent_eth_ports": [],
    "hardware_parent_fc_ports": [],
    "hardware_parent_sas_ports": [],
    "io_module_eth_ports": []
}, {
    "appliance_id": "A1",
    "name": "BaseEnclosure-NodeB-EmbeddedModule-SFP0",
    "parent_id": "0585c10b69de44258bee4a23ec91c601",
    "stale_state": "Not_Stale",
    "status_led_state": None,
    "extra_details": {
        "mode": "Unknown",
        "supported_protocol": "Unknown",
        "connector_type": "Unknown",
        "supported_speeds": []
    },
    "id": "ea2b7ebba6784d35bfd123e255078947",
    "is_marked": None,
    "lifecycle_state": "Empty",
    "part_number": None,
    "serial_number": None,
    "slot": 0,
    "type": "SFP",
    "appliance": {
        "id": "A1"
    },
    "children": [],
    "parent": {
        "id": "0585c10b69de44258bee4a23ec91c601"
    },
    "hardware_parent_eth_ports": [],
    "hardware_parent_fc_ports": [],
    "hardware_parent_sas_ports": [],
    "io_module_eth_ports": []
}]
perf_fc_info = [{
    "appliance_id": "A1",
    "current_speed": None,
    "id": "090d75723f4147808fd5624582708381",
    "is_link_up": False,
    "name": "BaseEnclosure-NodeA-IoModule0-FEPort2",
    "partner_id": "ed8e44cab9484f8c92d488a12e5bc6d8",
    "port_connector_type": "LC",
    "supported_speeds": [
        "Auto",
        "8_Gbps",
        "16_Gbps"
    ],
    "wwn": "58:cc:f0:90:4d:22:19:fb",
    "stale_state": "Not_Stale",
    "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
}]
eth_info = [{
    "id": "0133e5496e6b4671b37bb2fc94be1a25",
    "name": "BaseEnclosure-NodeA-4PortCard-FEPort1",
    "appliance_id": "A1",
    "current_mtu": 1500,
    "current_speed": None,
    "hardware_parent_id": "fd5cb1c32a434ecbba63f79060fa605b",
    "is_link_up": False,
    "mac_address": "0c48c6c9d455",
    "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
    "partner_id": "dddae67b03fc49b796bc27cb23932c84",
    "sfp_id": "e387bf548a8b45a1831982857407adb1",
    "port_connector_type": "Unknown",
    "stale_state": "Not_Stale",
    "supported_speeds": [
        "Auto"
    ],
}, {
    "id": "0235963690ab404c8e6a3485d5a58198",
    "name": "BaseEnclosure-NodeB-EmbeddedModule-ServicePort",
    "appliance_id": "A1",
    "current_mtu": 1500,
    "current_speed": None,
    "hardware_parent_id": "0585c10b69de44258bee4a23ec91c601",
    "is_link_up": False,
    "mac_address": "006016d7a783",
    "node_id": "5c93d9044ea94afea7d0ac853b89886c",
    "sfp_id": None,
    "partner_id": "de32885d015e4922a571db515a1b8659",
    "port_connector_type": "RJ45",
    "port_index": 1,
    "stale_state": "Not_Stale",
    "supported_speeds": [
        "Auto",
        "10_Mbps",
        "100_Mbps",
        "1_Gbps"
    ],
}]
sas_info = [
    {
        "appliance_id": "A1",
        "id": "7774e11064704ccc9b90d1d2c3c7da2c",
        "is_link_up": False,
        "name": "BaseEnclosure-NodeA-EmbeddedModule-BEPort0",
        "partner_id": "87f9ddbef894406aa7c43501f3d6a008",
        "speed": None,
        "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
        "sfp_id": "66696ff8755b4e8ca8c853021b7e668f"
    },
    {
        "appliance_id": "A1",
        "id": "87f9ddbef894406aa7c43501f3d6a008",
        "is_link_up": False,
        "name": "BaseEnclosure-NodeB-EmbeddedModule-BEPort0",
        "partner_id": "7774e11064704ccc9b90d1d2c3c7da2c",
        "speed": None,
        "node_id": "5c93d9044ea94afea7d0ac853b89886c",
        "sfp_id": "ea2b7ebba6784d35bfd123e255078947"
    }]
ports_data = [
    {'name': 'BaseEnclosure-NodeA-IoModule0-FEPort2', 'storage_id': '12345',
     'native_port_id': '090d75723f4147808fd5624582708381',
     'location': 'Powerstore1000T-appliance-1:BaseEnclosure-'
                 'NodeA-IoModule0-FEPort2',
     'connection_status': 'disconnected', 'health_status': 'normal',
     'type': 'fc', 'speed': 16000000000, 'max_speed': 16000000000,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'wwn': '58:cc:f0:90:4d:22:19:fb'},
    {'name': 'BaseEnclosure-NodeA-IoModule0-FEPort0', 'storage_id': '12345',
     'native_port_id': '210d046f161b4c2ebbcfd3090d706370',
     'location': 'Powerstore1000T-appliance-1:BaseEnclosure-'
                 'NodeA-IoModule0-FEPort0',
     'connection_status': 'disconnected', 'health_status': 'normal',
     'type': 'fc', 'speed': None, 'max_speed': 16000000000,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'wwn': '58:cc:f0:90:4d:20:19:fb'},
    {'name': 'BaseEnclosure-NodeA-4PortCard-FEPort1', 'storage_id': '12345',
     'native_port_id': '0133e5496e6b4671b37bb2fc94be1a25',
     'location': 'Powerstore1000T-appliance-1:BaseEnclosure-'
                 'NodeA-4PortCard-FEPort1',
     'connection_status': 'disconnected', 'health_status': 'unknown',
     'type': 'eth', 'speed': None, 'max_speed': None,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'mac_address': '0c48c6c9d455'},
    {'name': 'BaseEnclosure-NodeB-EmbeddedModule-ServicePort',
     'storage_id': '12345',
     'native_port_id': '0235963690ab404c8e6a3485d5a58198',
     'location': 'Powerstore1000T-appliance-1:BaseEnclosure-NodeB-'
                 'EmbeddedModule-ServicePort',
     'connection_status': 'disconnected', 'health_status': 'unknown',
     'type': 'eth', 'speed': None, 'max_speed': 1000000000,
     'native_parent_id': '5c93d9044ea94afea7d0ac853b89886c',
     'mac_address': '006016d7a783'},
    {'name': 'BaseEnclosure-NodeA-EmbeddedModule-BEPort0',
     'storage_id': '12345',
     'native_port_id': '7774e11064704ccc9b90d1d2c3c7da2c',
     'location': 'Powerstore1000T-appliance-1:BaseEnclosure-NodeA-'
                 'EmbeddedModule-BEPort0',
     'connection_status': 'disconnected', 'health_status': 'unknown',
     'type': 'sas', 'speed': None,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063'},
    {'name': 'BaseEnclosure-NodeB-EmbeddedModule-BEPort0',
     'storage_id': '12345',
     'native_port_id': '87f9ddbef894406aa7c43501f3d6a008',
     'location': 'Powerstore1000T-appliance-1:BaseEnclosure-NodeB-'
                 'EmbeddedModule-BEPort0',
     'connection_status': 'disconnected', 'health_status': 'unknown',
     'type': 'sas', 'speed': None,
     'native_parent_id': '5c93d9044ea94afea7d0ac853b89886c'}]
alert = {
    '1.3.6.1.2.1.1.3.0': '1669372584',
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.205.1.2.2',
    '1.3.6.1.4.1.1139.205.1.1.1': '0x01800103',
    '1.3.6.1.4.1.1139.205.1.1.2':
        'All configured DNS servers are unavailable.',
    '1.3.6.1.4.1.1139.205.1.1.3':
        'DNS servers availability status. (fully_unavailable)',
    '1.3.6.1.4.1.1139.205.1.1.4': 'appliance',
    '1.3.6.1.4.1.1139.205.1.1.5': 'A1',
    '1.3.6.1.4.1.1139.205.1.1.6': 'Powerstore1000T-appliance-1',
    '1.3.6.1.4.1.1139.205.1.1.7': 'ACTIVE',
    '1.3.6.1.4.1.1139.205.1.1.10': '2022-11-06T04:23:29.278Z',
    '1.3.6.1.4.1.1139.205.1.1.11': '',
    '1.3.6.1.4.1.1139.205.1.1.8': 'A1',
    '1.3.6.1.4.1.1139.205.1.1.9': '2022-11-25T10:36:16.822Z',
    'transport_address': '192.168.3.241',
    'storage_id': '38825735-0c48-481f-9551-95076950eebf',
    'controller_name': 'NodeA'
}
resource_metrics = {
    constants.ResourceType.STORAGE: consts.STORAGE_CAP,
    constants.ResourceType.STORAGE_POOL: consts.STORAGE_POOL_CAP,
    constants.ResourceType.VOLUME: consts.VOLUME_CAP,
    constants.ResourceType.CONTROLLER: consts.CONTROLLER_CAP,
    constants.ResourceType.PORT: consts.PORT_CAP,
    constants.ResourceType.FILESYSTEM: consts.FILE_SYSTEM_CAP
}
host_info = [
    {
        "id": "52c74385-b5a1-4af0-b9c6-18c47a04e27d",
        "name": "hg02",
        "host_initiators": [
            {
                "port_name": "11:00:22:a4:24:b5:32:25",
                "port_type": "FC",
                "active_sessions": [],
                "chap_mutual_username": None,
                "chap_single_username": None
            }
        ],
        "os_type": "HP-UX",
        "description": "hp",
        "host_group_id": None,
        "type": "External",
        "host_virtual_volume_mappings": [],
        "mapped_hosts": [
            {
                "id": "36cb8bf8-f9c1-4592-a7fd-fed5b0e29885"
            },
            {
                "id": "7ea3ce7d-9d0f-4bc2-a207-b9283dcacb81"
            },
            {
                "id": "db678691-7bfa-49e4-81a1-53dfb2188f8a"
            }
        ]
    },
    {
        "id": "aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f",
        "name": "host01",
        "host_initiators": [
            {
                "port_name": "iqn.2001-05.com.exampld:name2",
                "port_type": "iSCSI",
                "active_sessions": [],
                "chap_mutual_username": None,
                "chap_single_username": None
            },
            {
                "port_name": "iqn.2001-05.com.exampld:name1",
                "port_type": "iSCSI",
                "active_sessions": [],
                "chap_mutual_username": None,
                "chap_single_username": None
            }
        ],
        "os_type": "ESXi",
        "description": "host",
        "host_group_id": "ea01240f-4692-44f4-817b-924efd2c8519",
        "type": "External",
        "mapped_hosts": []
    }
]
initiators_info = [
    {'port_name': '11:00:22:a4:24:b5:32:25',
     'id': '11:00:22:a4:24:b5:32:25',
     'host_id': '52c74385-b5a1-4af0-b9c6-18c47a04e27d',
     'port_type': 'FC'
     },
    {'port_name': 'iqn.2001-05.com.exampld:name2',
     'id': 'iqn.2001-05.com.exampld:name2',
     'host_id': 'aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f',
     'port_type': 'iSCSI'
     }
]
initiators_data = [
    {'native_storage_host_initiator_id': '11:00:22:a4:24:b5:32:25',
     'native_storage_host_id': '52c74385-b5a1-4af0-b9c6-18c47a04e27d',
     'name': '11:00:22:a4:24:b5:32:25', 'type': 'fc', 'status': 'unknown',
     'wwn': '11:00:22:a4:24:b5:32:25', 'storage_id': '12345'}, {
        'native_storage_host_initiator_id': 'iqn.2001-05.com.exampld:name2',
        'native_storage_host_id': 'aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f',
        'name': 'iqn.2001-05.com.exampld:name2', 'type': 'iscsi',
        'status': 'unknown', 'wwn': 'iqn.2001-05.com.exampld:name2',
        'storage_id': '12345'}, {
        'native_storage_host_initiator_id': 'iqn.2001-05.com.exampld:name1',
        'native_storage_host_id': 'aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f',
        'name': 'iqn.2001-05.com.exampld:name1', 'type': 'iscsi',
        'status': 'unknown', 'wwn': 'iqn.2001-05.com.exampld:name1',
        'storage_id': '12345'}]
initiators_upgrade_data = [
    {'native_storage_host_initiator_id': '11:00:22:a4:24:b5:32:25',
     'native_storage_host_id': '52c74385-b5a1-4af0-b9c6-18c47a04e27d',
     'name': '11:00:22:a4:24:b5:32:25', 'type': 'fc', 'status': 'unknown',
     'wwn': '11:00:22:a4:24:b5:32:25', 'storage_id': '12345'},
    {'native_storage_host_initiator_id': 'iqn.2001-05.com.exampld:name2',
     'native_storage_host_id': 'aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f',
     'name': 'iqn.2001-05.com.exampld:name2', 'type': 'iscsi',
     'status': 'unknown', 'wwn': 'iqn.2001-05.com.exampld:name2',
     'storage_id': '12345'}]
host_data = [{'name': 'hg02', 'storage_id': '12345',
              'native_storage_host_id': '52c74385-b5a1-4af0-b9c6-18c47a04e27d',
              'description': 'hp', 'os_type': 'HP-UX', 'status': 'normal'},
             {'name': 'host01', 'storage_id': '12345',
              'native_storage_host_id': 'aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f',
              'description': 'host', 'os_type': 'VMware ESX',
              'status': 'normal'}]
host_group_info = [
    {
        "id": "ea01240f-4692-44f4-817b-924efd2c8519",
        "name": "hg01",
        "description": "hg",
        "hosts": [
            {
                "id": "aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f"
            }
        ]
    }
]
host_group_data = {
    'storage_host_groups': [
        {
            'native_storage_host_group_id':
                'ea01240f-4692-44f4-817b-924efd2c8519',
            'name': 'hg01', 'description': 'hg', 'storage_id': '12345'
        }],
    'storage_host_grp_host_rels': [{
        'native_storage_host_group_id': 'ea01240f-4692-44f4-817b-924efd2c8519',
        'storage_id': '12345',
        'native_storage_host_id': 'aa0793ff-5ee5-4593-8fdd-c28a58f7cf4f'}
    ]
}
volume_groups_info = [
    {
        "description": "null_volume_g",
        "name": "null_vg",
        "id": "0d434c72-5f1c-43b3-8a63-6a0cb5fd7cd9",
        "volumes": []
    },
    {
        "description": "vg",
        "name": "vg02",
        "id": "2018dec2-bb56-48aa-a2d3-c4402d57faf4",
        "volumes": [
            {
                "id": "1e387f96-ec3a-4bba-8298-ab6764f7d772"
            },
            {
                "id": "c73a7790-cd04-4ac1-b01d-32a7ac5d84d7"
            },
            {
                "id": "286e0694-800e-47e8-b0de-5262c57e9a30"
            }
        ]
    }]
volume_group_data = {
    'volume_groups': [
        {'name': 'null_vg', 'storage_id': '12345',
         'native_volume_group_id': '0d434c72-5f1c-43b3-8a63-6a0cb5fd7cd9',
         'description': 'null_volume_g'},
        {'name': 'vg02', 'storage_id': '12345',
         'native_volume_group_id': '2018dec2-bb56-48aa-a2d3-c4402d57faf4',
         'description': 'vg'}],
    'vol_grp_vol_rels': [
        {'storage_id': '12345',
         'native_volume_group_id': '2018dec2-bb56-48aa-a2d3-c4402d57faf4',
         'native_volume_id': '1e387f96-ec3a-4bba-8298-ab6764f7d772'},
        {'storage_id': '12345',
         'native_volume_group_id': '2018dec2-bb56-48aa-a2d3-c4402d57faf4',
         'native_volume_id': 'c73a7790-cd04-4ac1-b01d-32a7ac5d84d7'},
        {'storage_id': '12345',
         'native_volume_group_id': '2018dec2-bb56-48aa-a2d3-c4402d57faf4',
         'native_volume_id': '286e0694-800e-47e8-b0de-5262c57e9a30'}]}
masking_info = [
    {
        "host_group_id": None,
        "host_id": "52c74385-b5a1-4af0-b9c6-18c47a04e27d",
        "id": "36cb8bf8-f9c1-4592-a7fd-fed5b0e29885",
        "logical_unit_number": 3,
        "volume_id": "40ce0f3c-d250-4efc-b78a-1b1c768788f4",
    },
    {
        "host_group_id": "ea01240f-4692-44f4-817b-924efd2c8519",
        "host_id": None,
        "id": "3d5c3954-853e-481e-b7de-821854697ed2",
        "logical_unit_number": 2,
        "volume_id": "40ce0f3c-d250-4efc-b78a-1b1c768788f4",
    }
]
masking_data = [
    {'native_masking_view_id': '36cb8bf8-f9c1-4592-a7fd-fed5b0e29885',
     'name': '36cb8bf8-f9c1-4592-a7fd-fed5b0e29885',
     'native_volume_id': '40ce0f3c-d250-4efc-b78a-1b1c768788f4',
     'storage_id': '12345',
     'native_storage_host_id': '52c74385-b5a1-4af0-b9c6-18c47a04e27d'},
    {'native_masking_view_id': '3d5c3954-853e-481e-b7de-821854697ed2',
     'name': '3d5c3954-853e-481e-b7de-821854697ed2',
     'native_volume_id': '40ce0f3c-d250-4efc-b78a-1b1c768788f4',
     'storage_id': '12345',
     'native_storage_host_group_id': 'ea01240f-4692-44f4-817b-924efd2c8519'}]
filesystems_info = [{
    "id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee",
    "access_policy": "Native",
    "default_hard_limit": 1048576,
    "default_soft_limit": 1048576,
    "filesystem_type": "Primary",
    "locking_policy": "Advisory",
    "name": "test-f",
    "nas_server_id": "63996302-335c-69d7-f8cf-9e521753d873",
    "size_total": 5497558138880,
    "size_used": 1623195648,
}]
filesystems_data = [
    {'native_filesystem_id': '6399654a-36d7-2ed5-2e1e-86754c57b7ee',
     'name': 'test-f', 'type': 'thin', 'status': 'normal',
     'storage_id': '12345', 'total_capacity': 5497558138880,
     'used_capacity': 1623195648, 'free_capacity': 5495934943232,
     'security_mode': 'native'}]
nas_service_info = [{
    "id": "63996302-335c-69d7-f8cf-9e521753d873",
    "name": "test"
}]
quotas_tree_info = [{
    "id": "00000003-0066-0000-0100-000000000000",
    "file_system_id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee",
    "path": "/ques",
    "description": "",
    "is_user_quotas_enforced": True,
    "state": "Ok",
    "hard_limit": 1048576,
    "soft_limit": 1048576,
    "remaining_grace_period": -1,
    "size_used": 0,
    "grace_period": 604800
}]
user_quotas = [{
    "id": "00000003-0066-0000-0000-000001000000",
    "uid": 1,
    "hard_limit": 1048576,
    "remaining_grace_period": -1,
    "size_used": 0,
    "soft_limit": 1048576,
    "state": "Ok",
    "tree_quota_id": None,
    "unix_name": None,
    "windows_name": None,
    "windows_sid": None,
    "file_system_id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee",
    "file_system": {
        "id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee"
    },
    "tree_quota": None
}]
nfs_info = [
    {
        "id": "6399654d-dd66-0173-9886-86754c57b7ee",
        "name": "nfx-test",
        "description": None,
        "path": "/test-f",
        "is_no_SUID": False,
        "file_system": {
            "id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee"
        }
    },
    {
        "id": "639969bf-cd76-c446-5b99-86754c57b7ee",
        "name": "test200",
        "description": None,
        "path": "/f_tdjc",
        "is_no_SUID": False,
        "file_system": {
            "id": "63996981-1381-2c75-2797-86754c57b7ee"
        }
    },
    {
        "id": "63a2a88f-4ac8-6d08-0b89-86754c57b7ee",
        "name": "nfs",
        "description": None,
        "path": "/fs-01",
        "is_no_SUID": False,
        "file_system": {
            "id": "63a2a7ee-a6c5-b413-eb0a-86754c57b7ee"
        }
    },
    {
        "id": "63a3c04f-6529-5e00-ea38-86754c57b7ee",
        "name": "nfs-02",
        "description": None,
        "path": "/test-f01",
        "is_no_SUID": False,
        "file_system": {
            "id": "63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee"
        }
    },
    {
        "id": "63aea932-ec10-1ea4-c191-86754c57b7ee",
        "name": "1230-nfs",
        "description": None,
        "path": "/1230-fs",
        "is_no_SUID": False,
        "file_system": {
            "id": "63aea92f-5c8d-2661-c162-86754c57b7ee"
        }
    }
]
smb_info = [
    {
        "id": "6399654d-a337-9c17-8cb5-86754c57b7ee",
        "file_system_id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee",
        "description": None,
        "is_ABE_enabled": True,
        "is_branch_cache_enabled": True,
        "is_continuous_availability_enabled": True,
        "is_encryption_enabled": True,
        "name": "smb-test",
        "offline_availability": "Manual",
        "path": "/test-f",
        "umask": "022",
        "file_system": {
            "id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee"
        }
    },
    {
        "id": "639969d4-742b-cdda-5593-86754c57b7ee",
        "file_system_id": "63996981-1381-2c75-2797-86754c57b7ee",
        "description": None,
        "is_ABE_enabled": False,
        "is_branch_cache_enabled": False,
        "is_continuous_availability_enabled": False,
        "is_encryption_enabled": False,
        "name": "smb200",
        "offline_availability": "None",
        "path": "/f_tdjc",
        "umask": "022",
        "file_system": {
            "id": "63996981-1381-2c75-2797-86754c57b7ee"
        }
    },
    {
        "id": "63a3c04f-fea3-92e2-a73a-86754c57b7ee",
        "file_system_id": "63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee",
        "description": None,
        "is_ABE_enabled": False,
        "is_branch_cache_enabled": False,
        "is_continuous_availability_enabled": False,
        "is_encryption_enabled": False,
        "name": "smb-02",
        "offline_availability": "Documents",
        "path": "/test-f01",
        "umask": "022",
        "file_system": {
            "id": "63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee"
        }
    },
    {
        "id": "63aea653-7579-e0ac-b818-86754c57b7ee",
        "file_system_id": "63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee",
        "description": None,
        "is_ABE_enabled": False,
        "is_branch_cache_enabled": False,
        "is_continuous_availability_enabled": False,
        "is_encryption_enabled": False,
        "name": "1230-snm",
        "offline_availability": "Programs",
        "path": "/test-f01",
        "umask": "022",
        "file_system": {
            "id": "63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee"
        }
    },
    {
        "id": "63aea932-5ced-a5dc-1862-86754c57b7ee",
        "file_system_id": "63aea92f-5c8d-2661-c162-86754c57b7ee",
        "description": None,
        "is_ABE_enabled": False,
        "is_branch_cache_enabled": False,
        "is_continuous_availability_enabled": False,
        "is_encryption_enabled": False,
        "name": "1230-smb",
        "offline_availability": "None",
        "path": "/1230-fs",
        "umask": "022",
        "file_system": {
            "id": "63aea92f-5c8d-2661-c162-86754c57b7ee"
        }
    }
]
shares_data = [
    {'native_share_id': '6399654d-dd66-0173-9886-86754c57b7ee',
     'name': 'nfx-test', 'storage_id': '12345',
     'native_filesystem_id': '6399654a-36d7-2ed5-2e1e-86754c57b7ee',
     'native_qtree_id': '48452a5a7a620559759631caf7d34398',
     'protocol': 'nfs', 'path': '/test-f'},
    {'native_share_id': '639969bf-cd76-c446-5b99-86754c57b7ee',
     'name': 'test200', 'storage_id': '12345',
     'native_filesystem_id': '63996981-1381-2c75-2797-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'nfs', 'path': '/f_tdjc'},
    {'native_share_id': '63a2a88f-4ac8-6d08-0b89-86754c57b7ee',
     'name': 'nfs', 'storage_id': '12345',
     'native_filesystem_id': '63a2a7ee-a6c5-b413-eb0a-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'nfs', 'path': '/fs-01'},
    {'native_share_id': '63a3c04f-6529-5e00-ea38-86754c57b7ee',
     'name': 'nfs-02', 'storage_id': '12345',
     'native_filesystem_id': '63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'nfs',
     'path': '/test-f01'},
    {'native_share_id': '63aea932-ec10-1ea4-c191-86754c57b7ee',
     'name': '1230-nfs', 'storage_id': '12345',
     'native_filesystem_id': '63aea92f-5c8d-2661-c162-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'nfs',
     'path': '/1230-fs'},
    {'native_share_id': '6399654d-a337-9c17-8cb5-86754c57b7ee',
     'name': 'smb-test', 'storage_id': '12345',
     'native_filesystem_id': '6399654a-36d7-2ed5-2e1e-86754c57b7ee',
     'native_qtree_id': '48452a5a7a620559759631caf7d34398',
     'protocol': 'cifs', 'path': '/test-f'},
    {'native_share_id': '639969d4-742b-cdda-5593-86754c57b7ee',
     'name': 'smb200', 'storage_id': '12345',
     'native_filesystem_id': '63996981-1381-2c75-2797-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'cifs',
     'path': '/f_tdjc'},
    {'native_share_id': '63a3c04f-fea3-92e2-a73a-86754c57b7ee',
     'name': 'smb-02', 'storage_id': '12345',
     'native_filesystem_id': '63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'cifs',
     'path': '/test-f01'},
    {'native_share_id': '63aea653-7579-e0ac-b818-86754c57b7ee',
     'name': '1230-snm', 'storage_id': '12345',
     'native_filesystem_id': '63a3c04c-bcf0-9ae9-8fd2-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'cifs',
     'path': '/test-f01'},
    {'native_share_id': '63aea932-5ced-a5dc-1862-86754c57b7ee',
     'name': '1230-smb', 'storage_id': '12345',
     'native_filesystem_id': '63aea92f-5c8d-2661-c162-86754c57b7ee',
     'native_qtree_id': None, 'protocol': 'cifs',
     'path': '/1230-fs'}]
quotas_data = [
    {'native_quota_id': '00000003-0066-0000-0100-000000000000', 'type': 'tree',
     'storage_id': '12345',
     'native_filesystem_id': '6399654a-36d7-2ed5-2e1e-86754c57b7ee',
     'native_qtree_id': '48452a5a7a620559759631caf7d34398',
     'capacity_hard_limit': 1048576, 'capacity_soft_limit': 1048576,
     'used_capacity': 0},
    {'native_quota_id': '00000003-0066-0000-0000-000001000000', 'type': 'user',
     'storage_id': '12345',
     'native_filesystem_id': '6399654a-36d7-2ed5-2e1e-86754c57b7ee',
     'native_qtree_id': '48452a5a7a620559759631caf7d34398',
     'capacity_hard_limit': 1048576, 'capacity_soft_limit': 1048576,
     'used_capacity': 0, 'user_group_name': 1}]
qtress_data = [{'native_qtree_id': '48452a5a7a620559759631caf7d34398',
                'name': 'NAS Servers Name:test@File Systems Name:test-f',
                'storage_id': '12345',
                'native_filesystem_id': '6399654a-36d7-2ed5-2e1e-86754c57b7ee',
                'path': 'NAS Servers Name:test@File Systems Name:test-f',
                'security_mode': 'native'}]
cluster_perf_info = [
    {
        "timestamp": "2022-11-28T02:59:20Z",
        "cluster_id": "0",
        "avg_read_latency": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_write_size": 0.0,
        "avg_io_size": 0.0,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_cluster",
        "entity": "performance_metrics_by_cluster"
    },
    {
        "timestamp": "2022-11-28T02:59:40Z",
        "cluster_id": "0",
        "avg_read_latency": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_write_size": 0.0,
        "avg_io_size": 0.0,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_cluster",
        "entity": "performance_metrics_by_cluster"
    }
]
appliance_perf_info = [
    {
        "appliance_id": "A1",
        "timestamp": "2022-11-28T02:59:40Z",
        "avg_read_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_write_size": 0.0,
        "avg_io_size": 0.0,
        "read_iops": 0.0,
        "write_iops": 0.0,
        "total_iops": 0.0,
        "read_bandwidth": 0.0,
        "write_bandwidth": 0.0,
        "total_bandwidth": 0.0,
        "io_workload_cpu_utilization": 9.419034756121814E-4,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_appliance",
        "entity": "performance_metrics_by_appliance"
    },
    {
        "appliance_id": "A1",
        "timestamp": "2022-11-28T03:00:00Z",
        "avg_read_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_write_size": 0.0,
        "avg_io_size": 0.0,
        "read_iops": 0.0,
        "write_iops": 0.0,
        "total_iops": 0.0,
        "read_bandwidth": 0.0,
        "write_bandwidth": 0.0,
        "total_bandwidth": 0.0,
        "io_workload_cpu_utilization": 6.913627946170662E-4,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_appliance",
        "entity": "performance_metrics_by_appliance"
    }
]
perf_volume_info = [{
    "app_type": "Business_Applications_ERP_SAP",
    "app_type_l10n": "ERP / SAP",
    "appliance_id": "A1",
    "description": "什么 都不是",
    "state": "Ready",
    "type": "Primary",
    "wwn": "naa.68ccf0980048d7ab86ec9f7fdfa9945d",
    "size": 3221225472,
    "name": "wu-003",
    "id": "022ece9c-4921-46ba-ba4f-91c167a90cbe",
    "appliance": {
        "id": "A1"
    }}
]
volume_perf_info = [
    {
        "volume_id": "022ece9c-4921-46ba-ba4f-91c167a90cbe",
        "timestamp": "2022-11-28T02:59:40Z",
        "avg_read_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_write_size": 0.0,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "avg_io_size": 0.0,
        "appliance_id": "A1",
        "repeat_count": 195,
        "response_definition": "performance_metrics_by_volume",
        "entity": "performance_metrics_by_volume"
    }
]
perf_node_info = [
    {
        "appliance_id": "A1",
        "id": "N1",
        "slot": 0,
    }
]
controllers_perf_info = [
    {
        "timestamp": "2022-11-28T03:00:00Z",
        "node_id": "N1",
        "appliance_id": "A1",
        "avg_read_latency": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_write_size": 0.0,
        "avg_io_size": 0.0,
        "io_workload_cpu_utilization": 6.839733981557592E-4,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "current_logins": 0,
        "unaligned_write_bandwidth": 0.0,
        "unaligned_read_bandwidth": 0.0,
        "unaligned_read_iops": 0.0,
        "unaligned_write_iops": 0.0,
        "unaligned_bandwidth": 0.0,
        "unaligned_iops": 0.0,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_node",
        "entity": "performance_metrics_by_node"
    },
    {
        "timestamp": "2022-11-28T03:00:20Z",
        "node_id": "N1",
        "appliance_id": "A1",
        "avg_read_latency": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_write_size": 0.0,
        "avg_io_size": 0.0,
        "io_workload_cpu_utilization": 9.434143408848538E-4,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "current_logins": 0,
        "unaligned_write_bandwidth": 0.0,
        "unaligned_read_bandwidth": 0.0,
        "unaligned_read_iops": 0.0,
        "unaligned_write_iops": 0.0,
        "unaligned_bandwidth": 0.0,
        "unaligned_iops": 0.0,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_node",
        "entity": "performance_metrics_by_node"
    }
]
fc_perf_info = [
    {
        "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
        "timestamp": "2022-11-28T03:00:00Z",
        "appliance_id": "A1",
        "avg_read_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_write_size": 0.0,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "current_logins": 0,
        "unaligned_write_bandwidth": 0.0,
        "unaligned_read_bandwidth": 0.0,
        "unaligned_read_iops": 0.0,
        "unaligned_write_iops": 0.0,
        "unaligned_bandwidth": 0.0,
        "unaligned_iops": 0.0,
        "avg_io_size": 0.0,
        "fe_port_id": "090d75723f4147808fd5624582708381",
        "dumped_frames_ps": 0.0,
        "loss_of_signal_count_ps": 0.0,
        "invalid_crc_count_ps": 0.0,
        "loss_of_sync_count_ps": 0.0,
        "invalid_tx_word_count_ps": 0.0,
        "prim_seq_prot_err_count_ps": 0.0,
        "link_failure_count_ps": 0.0,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_fe_fc_port",
        "entity": "performance_metrics_by_fe_fc_port"
    },
    {
        "node_id": "3f75d31ca1dc4d8fb95707c7f996a063",
        "timestamp": "2022-11-28T03:00:20Z",
        "appliance_id": "A1",
        "avg_read_latency": 0.0,
        "avg_read_size": 0.0,
        "avg_latency": 0.0,
        "avg_write_latency": 0.0,
        "avg_write_size": 0.0,
        "read_iops": 0.0,
        "read_bandwidth": 0.0,
        "total_iops": 0.0,
        "total_bandwidth": 0.0,
        "write_iops": 0.0,
        "write_bandwidth": 0.0,
        "current_logins": 0,
        "unaligned_write_bandwidth": 0.0,
        "unaligned_read_bandwidth": 0.0,
        "unaligned_read_iops": 0.0,
        "unaligned_write_iops": 0.0,
        "unaligned_bandwidth": 0.0,
        "unaligned_iops": 0.0,
        "avg_io_size": 0.0,
        "fe_port_id": "090d75723f4147808fd5624582708381",
        "dumped_frames_ps": 0.0,
        "loss_of_signal_count_ps": 0.0,
        "invalid_crc_count_ps": 0.0,
        "loss_of_sync_count_ps": 0.0,
        "invalid_tx_word_count_ps": 0.0,
        "prim_seq_prot_err_count_ps": 0.0,
        "link_failure_count_ps": 0.0,
        "repeat_count": 1,
        "response_definition": "performance_metrics_by_fe_fc_port",
        "entity": "performance_metrics_by_fe_fc_port"
    }
]
filesystems_perf_info = [{
    "file_system_id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee",
    "timestamp": "2022-11-28T03:00:00Z",
    "read_iops": 0.0,
    "write_iops": 0.0,
    "total_iops": 2,
    "read_bandwidth": 0.0,
    "write_bandwidth": 0.0,
    "total_bandwidth": 0.0,
    "avg_read_latency": 1024,
    "avg_write_latency": 0,
    "avg_latency": 0.0,
    "avg_read_size": 0,
    "avg_write_size": 0,
    "avg_size": 156.3,
    "repeat_count": 1,
    "response_definition": "performance_metrics_by_file_system",
    "entity": "performance_metrics_by_file_system"
}, {
    "file_system_id": "6399654a-36d7-2ed5-2e1e-86754c57b7ee",
    "timestamp": "2022-11-28T03:00:20Z",
    "read_iops": 0.0,
    "write_iops": 0.0,
    "total_iops": 0.0,
    "read_bandwidth": 0.0,
    "write_bandwidth": 0.0,
    "total_bandwidth": 0.0,
    "avg_read_latency": 0,
    "avg_write_latency": 0,
    "avg_latency": 0.0,
    "avg_read_size": 0,
    "avg_write_size": 0,
    "avg_size": 0.0,
    "repeat_count": 1,
    "response_definition": "performance_metrics_by_file_system",
    "entity": "performance_metrics_by_file_system"
}]

LOG = logging.getLogger(__name__)


def create_driver():
    RestHandler.login = mock.Mock(
        return_value={None})
    return PowerStoreDriver(**ACCESS_INFO)


class test_PowerStoreDriver(TestCase):
    driver = create_driver()

    def test_init(self):
        RestClient.do_call = mock.Mock(return_value={None})
        PowerStoreDriver(**ACCESS_INFO)

    def test_get_storage(self):
        RestHandler.get_storage_pools = mock.Mock(return_value=pools_data)
        RestHandler.get_disks = mock.Mock(return_value=disk_data)
        RestHandler.rest_call = mock.Mock(
            side_effect=[clusters, appliance, software_installed])
        storages = self.driver.get_storage(context)
        self.assertEqual(storages, storage_data)

    def test_get_storage_error(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[None])
        try:
            storages = self.driver.get_storage(context)
        except Exception as e:
            LOG.error(six.text_type(e))
            storages = {}
        self.assertDictEqual(storages, {})

    def test_get_storage_pools(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[appliance, appliance_capacity])
        pools = self.driver.list_storage_pools(context)
        self.assertListEqual(pools, pools_data)

    def test_get_disks(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[hardware_info])
        disks = self.driver.list_disks(context)
        self.assertListEqual(disks, disk_data)

    def test_list_volumes(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[volume_info, volume_generate])
        volumes = self.driver.list_volumes(context)
        self.assertListEqual(volumes, volume_data)

    def test_list_alerts(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[alerts_info])
        query_para = {'begin_time': 1667292765000, 'end_time': 1668502365000}
        alerts = self.driver.list_alerts(context, query_para)
        self.assertListEqual(alerts, alerts_data)

    def test_parse_alerts(self):
        alerts = self.driver.parse_alert(context, alert)
        self.assertDictEqual(alerts, snmp_alert_data)

    def test_list_controllers(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[node_info, ip_pool_address, hardware_info])
        controllers = self.driver.list_controllers(context)
        self.assertListEqual(controllers, controllers_data)

    def test_get_alert_sources(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[node_info, ip_pool_address, hardware_info])
        alert_sources = self.driver.get_alert_sources(context)
        self.assertListEqual(alert_sources, alert_sources_data)

    def test_list_ports(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[hardware_port_info, appliance, fc_info, eth_info,
                         sas_info])
        ports = self.driver.list_ports(context)
        self.assertListEqual(ports, ports_data)

    def test_reset_connection(self):
        return_value = __class__
        return_value.status_code = 400
        return_value.text = 'error'
        RestClient.do_call = mock.Mock(return_value=return_value)
        res = None
        try:
            self.driver.reset_connection(context)
        except Exception as e:
            LOG.info(six.text_type(e))
            res = {}
        self.assertEqual(res, {})

    def test_get_access_url(self):
        url = self.driver.get_access_url()
        self.assertEqual(url, url)

    def test_collect_perf_metrics(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[clusters, cluster_perf_info,
                         appliance, appliance_perf_info,
                         perf_volume_info, volume_perf_info,
                         hardware_info, perf_node_info, controllers_perf_info,
                         perf_fc_info, fc_perf_info,
                         filesystems_info, filesystems_perf_info])
        collect = self.driver.collect_perf_metrics(context, ACCESS_INFO.get(
            'storage_id'), resource_metrics, 1669604280000, 1669604580000)
        self.assertEqual(collect[0].values.get(1669604340000), 0)

    def test_get_capabilities(self):
        capabilities = self.driver.get_capabilities(context)
        self.assertDictEqual(capabilities.get('resource_metrics'),
                             resource_metrics)

    def test_get_latest_perf_timestamp(self):
        RestHandler.rest_call = mock.Mock(side_effect=[clusters])
        perf_timestamp = self.driver.get_latest_perf_timestamp(context)
        self.assertEqual(perf_timestamp, perf_timestamp)

    def test_list_storage_host_initiators(self):
        RestHandler.rest_call = mock.Mock(side_effect=[[], host_info])
        initiators = self.driver.list_storage_host_initiators(context)
        self.assertEqual(initiators, initiators_data)

    def test_list_storage_host_initiators_upgrade(self):
        RestHandler.rest_call = mock.Mock(side_effect=[initiators_info])
        initiators = self.driver.list_storage_host_initiators(context)
        self.assertEqual(initiators, initiators_upgrade_data)

    def test_list_storage_hosts(self):
        RestHandler.rest_call = mock.Mock(side_effect=[host_info])
        hosts = self.driver.list_storage_hosts(context)
        self.assertEqual(hosts, host_data)

    def test_list_storage_host_groups(self):
        RestHandler.rest_call = mock.Mock(side_effect=[host_group_info])
        host_groups = self.driver.list_storage_host_groups(context)
        self.assertEqual(host_groups, host_group_data)

    def test_list_volume_groups(self):
        RestHandler.rest_call = mock.Mock(side_effect=[volume_groups_info])
        volume_groups = self.driver.list_volume_groups(context)
        self.assertEqual(volume_groups, volume_group_data)

    def test_list_masking_views(self):
        RestHandler.rest_call = mock.Mock(side_effect=[masking_info])
        masking_views = self.driver.list_masking_views(context)
        self.assertEqual(masking_views, masking_data)

    def test_list_filesystems(self):
        RestHandler.rest_call = mock.Mock(side_effect=[filesystems_info])
        filesystems = self.driver.list_filesystems(context)
        self.assertListEqual(filesystems, filesystems_data)

    def test_list_quotas(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[nas_service_info, filesystems_info,
                         quotas_tree_info, user_quotas])
        quotas = self.driver.list_quotas(context)
        self.assertListEqual(quotas, quotas_data)

    def test_list_qtrees(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[nas_service_info, filesystems_info])
        qtrees = self.driver.list_qtrees(context)
        self.assertListEqual(qtrees, qtress_data)

    def test_list_shares(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[nas_service_info, filesystems_info,
                         nfs_info, smb_info])
        shares = self.driver.list_shares(context)
        self.assertListEqual(shares, shares_data)
