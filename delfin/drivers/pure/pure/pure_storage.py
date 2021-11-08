import hashlib

from oslo_log import log
from oslo_utils import units

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.pure.pure import rest_handler

LOG = log.getLogger(__name__)


class PureStorageDriver(driver.StorageDriver):
    SEVERITY_MAP = {'fatal': constants.Severity.FATAL,
                    'critical': constants.Severity.CRITICAL,
                    'major': constants.Severity.MAJOR,
                    'minor': constants.Severity.MINOR,
                    'warning': constants.Severity.WARNING,
                    'informational': constants.Severity.INFORMATIONAL,
                    'NotSpecified': constants.Severity.NOT_SPECIFIED}
    CATEGORY_MAP = {'fault': constants.Category.FAULT,
                    'event': constants.Category.EVENT,
                    'recovery': constants.Category.RECOVERY,
                    'notSpecified': constants.Category.NOT_SPECIFIED}
    CONTROLLER_STATUS_MAP = {'normal': constants.ControllerStatus.NORMAL,
                             'ready': constants.ControllerStatus.NORMAL,
                             'offline': constants.ControllerStatus.OFFLINE,
                             'fault': constants.ControllerStatus.FAULT,
                             'degraded': constants.ControllerStatus.DEGRADED,
                             'unknown': constants.ControllerStatus.UNKNOWN,
                             'unready': constants.ControllerStatus.UNKNOWN}
    DISK_STATUS_MAP = {'normal': constants.DiskStatus.NORMAL,
                       'healthy': constants.DiskStatus.NORMAL,
                       'abnormal': constants.DiskStatus.ABNORMAL,
                       'unhealthy': constants.DiskStatus.ABNORMAL,
                       'offline': constants.DiskStatus.OFFLINE}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def list_volumes(self, context):
        list_volumes = []
        volumes = self.rest_handler.get_volumes()
        if volumes:
            pools = self.rest_handler.get_pools()
            for volume in volumes:
                name = volume.get('name')
                total_capacity = int(int(volume.get('size')) / units.Ki)
                used_capacity = int(int(volume.get('volumes')) / units.Ki)
                native_storage_pool_id = None
                if pools:
                    for pool in pools:
                        pool_volumes = pool.get('volumes')
                        if name in pool_volumes:
                            native_storage_pool_id = pool.get('name')
                            break
                volume_dict = {
                    'native_volume_id': name,
                    'name': name,
                    'total_capacity': total_capacity,
                    'used_capacity': used_capacity,
                    'free_capacity': total_capacity - used_capacity,
                    'storage_id': self.storage_id,
                    'status': constants.StorageStatus.NORMAL,
                    'type': constants.VolumeType.THICK,
                    'native_storage_pool_id': native_storage_pool_id
                }
                list_volumes.append(volume_dict)
        return list_volumes

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        pass

    def get_storage(self, context):
        result_storage = self.rest_handler.get_storage()
        model = None
        total_capacity = None
        used_capacity = None
        if result_storage:
            for storage in result_storage:
                model = storage.get('hostname')
                total_capacity = int(int(storage.get('provisioned',
                                                     0)) / units.Ki)
                used_capacity = int(int(storage.get('volumes', 0)) /
                                    units.Ki)
                break

        storage_id = self.rest_handler.get_storage_id()
        name = None
        serial_number = None
        version = None
        if storage_id:
            name = storage_id.get('array_name')
            serial_number = storage_id.get('id')
            version = storage_id.get('version')
        storage = {
            'model': model,
            'total_capacity': total_capacity,
            'raw_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': total_capacity - used_capacity,
            'vendor': 'PURE',
            'name': name,
            'serial_number': serial_number,
            'firmware_version': version,
            'status': constants.StorageStatus.NORMAL,
            'location': name
        }
        return storage

    def list_alerts(self, context, query_para=None):
        return_alerts = self.rest_handler.get_alerts()
        alerts_list = []
        if return_alerts:
            for alerts in return_alerts:
                alerts_model = dict()
                alerts_model['alert_id'] = alerts.get('id')
                alerts_model['severity'] = PureStorageDriver.SEVERITY_MAP.get(
                    alerts.get('current_severity'),
                    constants.Severity.NOT_SPECIFIED)
                alerts_model['category'] = PureStorageDriver.CATEGORY_MAP.get(
                    alerts.get('category'), constants.Category.NOT_SPECIFIED)

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
        controllers = self.rest_handler.get_controllers()
        if controllers:
            for controller in controllers:
                controllers_object = dict()
                name = controller.get('name')
                controllers_object['name'] = name
                controllers_object['status'] = PureStorageDriver.\
                    CONTROLLER_STATUS_MAP.get(controller.get('status'),
                                              constants.ControllerStatus.
                                              UNKNOWN)
                controllers_object['soft_version'] = controller.get('version')
                controllers_object['storage_id'] = self.storage_id
                controllers_object['id'] = name
                controllers_object['native_controller_id'] = name
                controllers_object['location'] = name
                list_controllers.append(controllers_object)
        return list_controllers

    def list_disks(self, context):
        names = dict()
        hardware = self.rest_handler.get_hardware()
        if hardware:
            for hardware_value in hardware:
                hardware_name = dict()
                hardware_name['speed'] = hardware_value.get('speed')
                hardware_name['serial_number'] = hardware_value.get('serial')
                hardware_name['model'] = hardware_value.get('model')
                name = hardware_value.get('name')
                names[name] = hardware_name

        list_disks = []
        disks = self.rest_handler.get_disks()
        if disks:
            for drive in disks:
                disk = dict()
                drive_name = drive.get('name')
                disk['name'] = drive_name
                physical_type = drive.get('type').lower()
                disk['physical_type'] = physical_type \
                    if physical_type in constants.DiskPhysicalType.ALL else\
                    constants.DiskPhysicalType.UNKNOWN
                status = drive.get('status')
                disk['status'] = PureStorageDriver.DISK_STATUS_MAP.\
                    get(status, constants.DiskStatus.OFFLINE)
                disk['storage_id'] = self.storage_id
                disk['capacity'] = int(int(drive.get('capacity')) / units.Ki)

                hardware_object = names.get(drive_name, {})
                speed = hardware_object.get('speed')
                disk['speed'] = int(speed) if speed is not None else None
                disk['model'] = hardware_object.get('model')
                disk['serial_number'] = hardware_object.get('serial_number')

                disk['native_disk_id'] = drive_name
                disk['id'] = drive_name
                disk['location'] = drive_name
                disk['manufacturer'] = "pure"
                disk['firmware'] = ""
                list_disks.append(disk)
        return list_disks

    def list_ports(self, context):
        networks = self.get_network()
        list_ports = []
        ports = self.rest_handler.get_ports()
        if ports:
            for port in ports:
                port_result = dict()
                name = port.get('name')
                wwn = port.get('wwn')
                if wwn:
                    port_result['type'] = constants.PortType.FC
                    port_result['name'] = wwn
                    port_result['id'] = wwn
                    port_result['wwn'] = wwn
                else:
                    port_result['type'] = constants.PortType.ETH
                    iqn = port.get('iqn')
                    port_result['name'] = iqn
                    port_result['id'] = iqn
                    port_result['wwn'] = ''
                port_result['native_port_id'] = name
                port_result['location'] = name
                port_result['storage_id'] = self.storage_id
                network = networks.get(name.lower(), {})
                port_result['logical_type'] = network.get('logical_type')
                port_result['speed'] = network.get('speed')
                port_result['mac_address'] = network.get('address')
                port_result['ipv4_mask'] = network.get('ipv4_mask')
                port_result['connection_status '] = constants.\
                    PortConnectionStatus.CONNECTED
                port_result['health_status'] = constants.PortHealthStatus.\
                    NORMAL
                list_ports.append(port_result)
        return list_ports

    def get_network(self):
        networks_object = dict()
        networks = self.rest_handler.get_networks()
        if networks:
            for network in networks:
                network_object = dict()
                network_object['address'] = network.get('address')
                services_list = network.get('services')
                if services_list:
                    for services in services_list:
                        network_object['logical_type'] = services if \
                            services in constants.PortLogicalType.ALL else None
                        break
                network_object['speed'] = int(int(network.get('speed', 0)) /
                                              units.Ki)
                network_object['ipv4_mask'] = network.get('netmask')
                name = network.get('name')
                networks_object[name] = network_object
        return networks_object

    def list_storage_pools(self, context):
        pool_list = []
        pools = self.rest_handler.get_capacity_pools()
        if pools:
            for pool in pools:
                pool_result = dict()
                total_capacity = int(pool.get('size'))
                pool_result['total_capacity'] = total_capacity

                used_capacity = int(pool.get('total_reduction'))
                pool_result['used_capacity'] = used_capacity

                pool_result['free_capacity'] = total_capacity - used_capacity
                pool_result['name'] = pool.get('name')
                pool_result['native_storage_pool_id'] = pool.get('name')
                pool_result['storage_id'] = self.storage_id
                pool_result['description'] = ""
                pool_result['status'] = constants.StoragePoolStatus.NORMAL
                pool_result['storage_type'] = constants.StorageType.BLOCK
                pool_list.append(pool_result)
        return pool_list

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.login()
