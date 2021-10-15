import hashlib
import json

from oslo_log import log
from oslo_utils import units

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.pure.pure import rest_handler

LOG = log.getLogger(__name__)


class StorageDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def list_volumes(self, context):
        volume = []
        volumes_return = self.rest_handler.get_all_rest_volumes()
        if volumes_return:
            volume = self.volume_handler(volumes_return)
        return volume

    def volume_handler(self, volumes_return):
        volume = []
        return_pool = self.rest_handler.get_all_pools()
        for i in range(0, len(volumes_return)):
            volume_dict = dict()
            volume_object = volumes_return[i]
            name = volume_object.get('name')
            volume_dict['native_volume_id'] = name
            volume_dict['name'] = name
            total_capacity = int(int(volume_object.get('size')) / units.Ki)
            volume_dict['total_capacity'] = total_capacity
            used_capacity = int(int(volume_object.get('volumes')) / units.Ki)
            volume_dict['used_capacity'] = used_capacity
            volume_dict['free_capacity'] = total_capacity - used_capacity
            volume_dict['storage_id'] = self.storage_id
            volume_dict['description'] = ""
            volume_dict['status'] = constants.StorageStatus.NORMAL
            volume_dict['type'] = constants.VolumeType.THICK
            volume_dict['native_storage_pool_id'] = ""
            if return_pool:
                for j in return_pool:
                    volumes = j.get('volumes')
                    if name in volumes:
                        volume_dict['native_storage_pool_id'] = j.get('name')
                        break
            volume.append(volume_dict)
        return volume

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        pass

    def get_storage(self, context):
        storage_object = dict()
        result_storage = self.rest_handler.get_storage()
        if result_storage:
            storage_object['model'] = result_storage[0].get('hostname', "")
            total_capacity = int(int(result_storage[0].get('provisioned',
                                                           0)) / units.Ki)
            storage_object['total_capacity'] = total_capacity
            storage_object['raw_capacity'] = total_capacity
            used_capacity = int(int(result_storage[0].get('volumes', 0)) /
                                units.Ki)
            storage_object['used_capacity'] = used_capacity
            storage_object['free_capacity'] = total_capacity - used_capacity

        return_storage_id = self.rest_handler.get_storage_ID()
        storage_object['vendor'] = 'PURE'
        storage_object['name'] = return_storage_id.get('array_name')
        storage_object['serial_number'] = return_storage_id.get('id')
        storage_object['firmware_version'] = return_storage_id.get('version')
        storage_object['description'] = ""
        storage_object['status'] = constants.StorageStatus.NORMAL
        storage_object['location'] = ""
        return storage_object

    def list_alerts(self, context, query_para=None):
        return_alerts = self.rest_handler.get_all_alerts()
        alerts_list = []
        if return_alerts:
            for alerts in return_alerts:
                alerts_model = dict()
                alerts_model['alert_id'] = alerts.get('id')
                severity = alerts.get('current_severity')
                if severity == 'fatal':
                    alerts_model['severity'] = constants.Severity.FATAL
                elif severity == 'critical':
                    alerts_model['severity'] = constants.Severity.CRITICAL
                elif severity == 'major':
                    alerts_model['severity'] = constants.Severity.MAJOR
                elif severity == 'minor':
                    alerts_model['severity'] = constants.Severity.MINOR
                elif severity == 'warning':
                    alerts_model['severity'] = constants.Severity.WARNING
                elif severity == 'informational':
                    alerts_model['severity'] = constants.Severity.INFORMATIONAL
                else:
                    alerts_model['severity'] = constants.Severity.NOT_SPECIFIED

                category = alerts.get('category')
                if category == 'fault':
                    alerts_model['category'] = constants.Category.FAULT
                elif category == 'event':
                    alerts_model['category'] = constants.Category.EVENT
                elif category == 'recovery':
                    alerts_model['category'] = constants.Category.RECOVERY
                else:
                    alerts_model['category'] = constants.Category.NOT_SPECIFIED

                alerts_model['occur_time'] = alerts.get('opened')
                alerts_model['description'] = alerts.get('event')
                alerts_model['location'] = alerts.get('component_name')
                alerts_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alerts_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                alerts_model['alert_name'] = alerts.get('id')
                alerts_model['match_key'] = hashlib.md5(str(alerts.get('id')).
                                                        encode()).hexdigest()
                alerts_list.append(alerts_model)
        return alerts_list

    def list_controllers(self, context):
        list_controllers = []
        return_controllers = self.rest_handler.get_all_controllers()
        if return_controllers:
            for controllers in return_controllers:
                controllers_object = dict()
                name = controllers.get('name')
                controllers_object['name'] = name
                status = controllers.get('status')
                if status == 'ready':
                    controllers_object['status'] = constants.ControllerStatus.\
                        NORMAL
                else:
                    controllers_object['status'] = constants.ControllerStatus.\
                        OFFLINE
                controllers_object['soft_version'] = controllers.get('version')
                controllers_object['storage_id'] = self.storage_id
                controllers_object['id'] = name
                controllers_object['native_controller_id'] = name
                controllers_object['location'] = ""
                controllers_object['cpu_info'] = ""
                controllers_object['memory_size'] = ""
                list_controllers.append(controllers_object)
        return list_controllers

    def list_disks(self, context):
        names = dict()
        return_hardware = self.rest_handler.get_all_hardware()
        if return_hardware:
            for hardware in return_hardware:
                hardware_name = dict()
                hardware_name['speed'] = hardware.get('speed')
                hardware_name['serial_number'] = hardware.get('serial')
                hardware_name['model'] = hardware.get('model')
                name = hardware.get('name')
                names[name] = hardware_name

        list_disk = []
        return_disks = self.rest_handler.get_all_disk()
        if return_disks:
            for drive in return_disks:
                disk = dict()
                drive_name = drive.get('name')
                disk['name'] = drive_name
                physical_type = drive.get('type').lower()
                if physical_type in constants.DiskPhysicalType.ALL:
                    disk['physical_type'] = physical_type
                else:
                    disk['physical_type'] = constants.DiskPhysicalType.UNKNOWN
                status = drive.get('status')
                if status == 'healthy':
                    disk['status'] = constants.DiskStatus.NORMAL
                elif status == 'unhealthy':
                    disk['status'] = constants.DiskStatus.ABNORMAL
                else:
                    disk['status'] = constants.DiskStatus.OFFLINE
                disk['storage_id'] = self.storage_id
                disk['capacity'] = int(int(drive.get('capacity')) / units.Ki)
                hardware_object = names.get(drive_name)
                if hardware_object is not None and hardware_object != "":
                    speed = hardware_object.get('speed')
                    if speed is None:
                        disk['speed'] = ''
                    else:
                        disk['speed'] = int(speed)
                    model = hardware_object.get('model')
                    disk['model'] = model
                    serial_number = hardware_object.get('serial_number')
                    disk['serial_number'] = serial_number
                else:
                    disk['speed'] = 0
                    disk['model'] = ''
                    disk['serial_number'] = ''
                disk['native_disk_id'] = drive_name
                disk['id'] = drive_name
                disk['location'] = drive_name
                disk['logical_type'] = ''
                disk['native_disk_group_id'] = ""
                disk['manufacturer'] = "pure"
                disk['firmware'] = ""
                disk['health_score'] = ""
                list_disk.append(disk)
        LOG.info("list_disk：%s" % (json.dumps(list_disk, ensure_ascii=False)))
        return list_disk

    def list_ports(self, context):
        networks_object = dict()
        self.network_object(networks_object)
        list_port = []
        return_ports = self.rest_handler.get_all_port()
        if return_ports:
            for ports in return_ports:
                port = dict()
                name = ports.get('name')
                wwn = ports.get('wwn')
                if wwn:
                    port['type'] = constants.PortType.FC
                    port['name'] = wwn
                    port['id'] = wwn
                    port['wwn'] = wwn
                else:
                    port['type'] = constants.PortType.ETH
                    iqn = ports.get('iqn')
                    port['name'] = iqn
                    port['id'] = iqn
                    port['wwn'] = ''
                port['native_port_id'] = name
                port['location'] = name
                port['storage_id'] = self.storage_id
                network = networks_object.get(name.lower())
                if network:
                    port['logical_type'] = network.get('logical_type')
                    port['speed'] = network.get('speed')
                    port['mac_address'] = network.get('address')
                    port['ipv4_mask'] = network.get('ipv4_mask')
                else:
                    port['logical_type'] = ''
                    port['speed'] = ''
                    port['mac_address'] = ''
                    port['ipv4_mask'] = ''
                port['connection_status '] = constants.PortConnectionStatus.\
                    CONNECTED
                port['health_status'] = constants.PortHealthStatus.NORMAL
                port['max_speed'] = ''
                port['native_parent_id'] = ""
                port['ipv4'] = ""
                port['ipv6'] = ""
                port['ipv6_mask'] = ""
                list_port.append(port)
        return list_port

    def network_object(self, networks_object):
        return_network = self.rest_handler.get_all_network()
        if return_network:
            for network in return_network:
                network_object = dict()
                network_object['address'] = network.get('address')
                services_list = network.get('services')
                if services_list:
                    services = services_list[0]
                    if services in constants.PortLogicalType.ALL:
                        network_object['logical_type'] = services
                    else:
                        network_object['logical_type'] = ""
                network_object['speed'] = int(int(network.get('speed', 0)) /
                                              units.Ki)
                network_object['ipv4_mask'] = network.get('netmask')
                name = network.get('name')
                networks_object[name] = network_object

    def list_storage_pools(self, context):
        pool_list = []
        return_pools = self.rest_handler.get_capacity_pools()
        if return_pools:
            for pools in return_pools:
                pool_object = dict()
                total_capacity = int(pools.get('size'))
                pool_object['total_capacity'] = total_capacity

                used_capacity = int(pools.get('total_reduction'))
                pool_object['used_capacity'] = used_capacity

                pool_object['free_capacity'] = total_capacity - used_capacity
                pool_object['name'] = pools.get('name')
                pool_object['native_storage_pool_id'] = pools.get('name')
                pool_object['storage_id'] = self.storage_id
                pool_object['description'] = ""
                pool_object['status'] = constants.StoragePoolStatus.NORMAL
                pool_object['storage_type'] = constants.StorageType.BLOCK
                pool_list.append(pool_object)
        return pool_list

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.login()
