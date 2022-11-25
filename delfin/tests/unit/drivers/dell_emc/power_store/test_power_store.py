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
              'status': 'normal', 'physical_type': 'ssd',
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
    'match_key': 'be5bca77c99bdf8800b34a9905b84622',
    'description': 'Management ports are properly connected to different '
                   'management switches.'}]
snmp_alert_data = {
    'alert_id': '0032b92b-e0bc-4259-b572-db562238b4b4',
    'occur_time': 1667715494446, 'severity': 'Informational',
    'category': 'Fault', 'location': 'hardware:BaseEnclosure-NodeB',
    'type': 'EquipmentAlarm', 'resource_type': 'hardware',
    'alert_name': 'Management ports are properly connected to different '
                  'management switches.',
    'match_key': 'be5bca77c99bdf8800b34a9905b84622',
    'description': 'Management ports are properly connected to different '
                   'management switches.'}
controllers_data = [
    {'name': 'NodeA', 'storage_id': '12345',
     'native_controller_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'status': 'normal', 'location': 0,
     'cpu_info': 'Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz',
     'cpu_count': 1, 'memory_size': 206158430208},
    {'name': 'NodeB', 'storage_id': '12345',
     'native_controller_id': '5c93d9044ea94afea7d0ac853b89886c',
     'status': 'normal', 'location': 1,
     'cpu_info': 'Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz',
     'cpu_count': 1, 'memory_size': 206158430208}]
fc_info = [{
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
        "node_id": "3f75d31ca1dc4d8fb95707c7f996a063"
    },
    {
        "appliance_id": "A1",
        "id": "87f9ddbef894406aa7c43501f3d6a008",
        "is_link_up": False,
        "name": "BaseEnclosure-NodeB-EmbeddedModule-BEPort0",
        "partner_id": "7774e11064704ccc9b90d1d2c3c7da2c",
        "speed": None,
        "node_id": "5c93d9044ea94afea7d0ac853b89886c"
    }]
ports_data = [
    {'name': 'BaseEnclosure-NodeA-IoModule0-FEPort2', 'storage_id': '12345',
     'native_port_id': '090d75723f4147808fd5624582708381',
     'location': 'A1:BaseEnclosure-NodeA-IoModule0-FEPort2',
     'connection_status': 'disconnected', 'health_status': 'abnormal',
     'type': 'fc', 'speed': None, 'max_speed': 16000000000,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'wwn': '58:cc:f0:90:4d:22:19:fb'},
    {'name': 'BaseEnclosure-NodeA-IoModule0-FEPort0', 'storage_id': '12345',
     'native_port_id': '210d046f161b4c2ebbcfd3090d706370',
     'location': 'A1:BaseEnclosure-NodeA-IoModule0-FEPort0',
     'connection_status': 'disconnected', 'health_status': 'abnormal',
     'type': 'fc', 'speed': None, 'max_speed': 16000000000,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'wwn': '58:cc:f0:90:4d:20:19:fb'},
    {'name': 'BaseEnclosure-NodeA-4PortCard-FEPort1', 'storage_id': '12345',
     'native_port_id': '0133e5496e6b4671b37bb2fc94be1a25',
     'location': 'A1:BaseEnclosure-NodeA-4PortCard-FEPort1',
     'connection_status': 'disconnected', 'health_status': 'abnormal',
     'type': 'eth', 'speed': None, 'max_speed': None,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063',
     'mac_address': '0c48c6c9d455'},
    {'name': 'BaseEnclosure-NodeB-EmbeddedModule-ServicePort',
     'storage_id': '12345',
     'native_port_id': '0235963690ab404c8e6a3485d5a58198',
     'location': 'A1:BaseEnclosure-NodeB-EmbeddedModule-ServicePort',
     'connection_status': 'disconnected', 'health_status': 'abnormal',
     'type': 'eth', 'speed': None, 'max_speed': 1000000000,
     'native_parent_id': '5c93d9044ea94afea7d0ac853b89886c',
     'mac_address': '006016d7a783'},
    {'name': 'BaseEnclosure-NodeA-EmbeddedModule-BEPort0',
     'storage_id': '12345',
     'native_port_id': '7774e11064704ccc9b90d1d2c3c7da2c',
     'location': 'A1:BaseEnclosure-NodeA-EmbeddedModule-BEPort0',
     'connection_status': 'disconnected', 'health_status': 'abnormal',
     'type': 'sas', 'speed': None,
     'native_parent_id': '3f75d31ca1dc4d8fb95707c7f996a063'},
    {'name': 'BaseEnclosure-NodeB-EmbeddedModule-BEPort0',
     'storage_id': '12345',
     'native_port_id': '87f9ddbef894406aa7c43501f3d6a008',
     'location': 'A1:BaseEnclosure-NodeB-EmbeddedModule-BEPort0',
     'connection_status': 'disconnected', 'health_status': 'abnormal',
     'type': 'sas', 'speed': None,
     'native_parent_id': '5c93d9044ea94afea7d0ac853b89886c'}]
resource_metrics = {
    constants.ResourceType.STORAGE: consts.STORAGE_CAP,
    constants.ResourceType.STORAGE_POOL: consts.STORAGE_POOL_CAP,
    constants.ResourceType.VOLUME: consts.VOLUME_CAP,
    constants.ResourceType.CONTROLLER: consts.CONTROLLER_CAP,
    constants.ResourceType.PORT: consts.PORT_CAP
}

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
        RestHandler.rest_call = mock.Mock(
            side_effect=[alerts_info])
        alert = {
            consts.PARSE_ALERT_DESCRIPTION:
                'Management ports are properly connected to'
                ' different management switches.',
            consts.PARSE_ALERT_TIME: 1667717925
        }
        alerts = self.driver.parse_alert(context, alert)
        self.assertDictEqual(alerts, snmp_alert_data)

    def test_list_controllers(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[hardware_info])
        controllers = self.driver.list_controllers(context)
        self.assertListEqual(controllers, controllers_data)

    def test_list_ports(self):
        RestHandler.rest_call = mock.Mock(
            side_effect=[fc_info, eth_info, sas_info])
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
