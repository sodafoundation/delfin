import datetime
import hashlib

from oslo_log import log
from oslo_utils import units

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.pure.flasharray import rest_handler, consts

LOG = log.getLogger(__name__)


class PureFlashArrayDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()

    def list_volumes(self, context):
        list_volumes = []
        volumes = self.rest_handler.get_volumes()
        if volumes:
            pools = self.rest_handler.rest_call(
                self.rest_handler.REST_POOLS_URL)
            for volume in volumes:
                volume_name = volume.get('name')
                total_capacity = int(volume.get('size',
                                                consts.DEFAULT_CAPACITY))
                used_capacity = int(volume.get('volumes',
                                               consts.DEFAULT_CAPACITY))
                native_storage_pool_id = None
                if pools:
                    for pool in pools:
                        pool_volumes = pool.get('volumes')
                        if volume_name in pool_volumes:
                            native_storage_pool_id = pool.get('name')
                            break
                volume_dict = {
                    'native_volume_id': volume_name,
                    'name': volume_name,
                    'total_capacity': total_capacity,
                    'used_capacity': used_capacity,
                    'free_capacity': total_capacity - used_capacity,
                    'storage_id': self.storage_id,
                    'status': constants.StorageStatus.NORMAL,
                    'type': constants.VolumeType.THIN if
                    volume.get('thin_provisioning') is not None
                    else constants.VolumeType.THICK,
                    'native_storage_pool_id': native_storage_pool_id
                }
                list_volumes.append(volume_dict)
        return list_volumes

    def add_trap_config(self, context, trap_config):
        pass

    def clear_alert(self, context, alert):
        pass

    def get_storage(self, context):
        storages = self.rest_handler.rest_call(
            self.rest_handler.REST_STORAGE_URL)
        total_capacity = None
        used_capacity = None
        if storages:
            for storage in storages:
                total_capacity = int(storage.get('provisioned',
                                                 consts.DEFAULT_CAPACITY))
                used_capacity = int(storage.get('volumes',
                                                consts.DEFAULT_CAPACITY))
                break

        arrays = self.rest_handler.rest_call(self.rest_handler.REST_ARRAY_URL)
        storage_name = None
        serial_number = None
        version = None
        if arrays:
            storage_name = arrays.get('array_name')
            serial_number = arrays.get('id')
            version = arrays.get('version')

        storage_result = {
            'model': consts.DEFAULT_GET_STORAGE_MODEL,
            'total_capacity': total_capacity,
            'raw_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': total_capacity - used_capacity,
            'vendor': 'PURE',
            'name': storage_name,
            'serial_number': serial_number,
            'firmware_version': version,
            'status': constants.StorageStatus.NORMAL
        }
        return storage_result

    def list_alerts(self, context, query_para=None):
        alerts = self.rest_handler.rest_call(self.rest_handler.REST_ALERTS_URL)
        alerts_list = []
        if alerts:
            for alert in alerts:
                alerts_model = dict()
                alerts_model['alert_id'] = alert.get('id')
                alerts_model['severity'] = consts.SEVERITY_MAP.get(
                    alert.get('current_severity'),
                    constants.Severity.NOT_SPECIFIED)
                alerts_model['category'] = consts.CATEGORY_MAP.get(
                    alert.get('category'), constants.Category.NOT_SPECIFIED)
                time = alert.get('opened')
                alerts_model['occur_time'] = int(datetime.datetime.strptime(
                    time, '%Y-%m-%dT%H:%M:%SZ').timestamp()
                    * consts.DEFAULT_LIST_ALERTS_TIME_CONVERSION) \
                    if time is not None else None
                alerts_model['description'] = alert.get('event')
                alerts_model['location'] = alert.get('component_name')
                alerts_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alerts_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                alerts_model['alert_name'] = alert.get('id')
                alerts_model['match_key'] = hashlib.md5(str(alert.get('id')).
                                                        encode()).hexdigest()
                alerts_list.append(alerts_model)
        return alerts_list

    def list_controllers(self, context):
        list_controllers = []
        controllers = self.rest_handler.rest_call(
            self.rest_handler.REST_CONTROLLERS_URL)
        if controllers:
            for controller in controllers:
                controllers_dict = dict()
                controller_name = controller.get('name')
                controllers_dict['name'] = controller_name
                controllers_dict['status'] = consts.CONTROLLER_STATUS_MAP. \
                    get(controller.get('status'),
                        constants.ControllerStatus.UNKNOWN)
                controllers_dict['soft_version'] = controller.get('version')
                controllers_dict['storage_id'] = self.storage_id
                controllers_dict['id'] = controller_name
                controllers_dict['native_controller_id'] = controller_name
                controllers_dict['location'] = controller_name
                list_controllers.append(controllers_dict)
        return list_controllers

    def list_disks(self, context):
        hardware_dict = self.get_hardware()
        list_disks = []
        disks = self.rest_handler.rest_call(self.rest_handler.REST_DISK_URL)
        if disks:
            for disk in disks:
                disk_dict = dict()
                drive_name = disk.get('name')
                disk_dict['name'] = drive_name
                physical_type = disk.get('type', "").lower()
                disk_dict['physical_type'] = physical_type \
                    if physical_type in constants.DiskPhysicalType.ALL else \
                    constants.DiskPhysicalType.UNKNOWN
                disk_dict['status'] = consts.DISK_STATUS_MAP. \
                    get(disk.get('status'), constants.DiskStatus.OFFLINE)
                disk_dict['storage_id'] = self.storage_id
                disk_dict['capacity'] = int(disk.get('capacity',
                                                     consts.DEFAULT_CAPACITY))
                hardware_object = hardware_dict.get(drive_name, {})
                speed = hardware_object.get('speed')
                disk_dict['speed'] = int(speed) if speed is not None else None
                disk_dict['model'] = hardware_object.get('model')
                disk_dict['serial_number'] = hardware_object. \
                    get('serial_number')

                disk_dict['native_disk_id'] = drive_name
                disk_dict['id'] = drive_name
                disk_dict['location'] = drive_name
                disk_dict['manufacturer'] = "PURE"
                disk_dict['firmware'] = ""
                list_disks.append(disk_dict)
        return list_disks

    def get_hardware(self):
        hardware_dict = dict()
        hardware = self.rest_handler.rest_call(
            self.rest_handler.REST_HARDWARE_URL)
        if hardware:
            for hardware_value in hardware:
                hardware_map = dict()
                hardware_map['speed'] = hardware_value.get('speed')
                hardware_map['serial_number'] = hardware_value.get('serial')
                hardware_map['model'] = hardware_value.get('model')
                hardware_dict[hardware_value.get('name')] = hardware_map
        return hardware_dict

    def list_ports(self, context):
        list_ports = []
        networks = self.get_network()
        ports = self.get_ports()
        hardware_dict = self.rest_handler.rest_call(
            self.rest_handler.REST_HARDWARE_URL)
        if not hardware_dict:
            return list_ports
        for hardware in hardware_dict:
            hardware_result = dict()
            hardware_name = hardware.get('name')
            if 'FC' in hardware_name:
                hardware_result['type'] = constants.PortType.FC
            elif 'ETH' in hardware_name:
                hardware_result['type'] = constants.PortType.ETH
            elif 'SAS' in hardware_name:
                hardware_result['type'] = constants.PortType.SAS
            else:
                continue
            hardware_result['name'] = hardware_name
            hardware_result['native_port_id'] = hardware_name
            hardware_result['storage_id'] = self.storage_id
            hardware_result['location'] = hardware_name
            speed = hardware.get('speed')
            if speed is None:
                hardware_result['connection_status'] = \
                    constants.PortConnectionStatus.UNKNOWN
                hardware_result['health_status'] = constants.PortHealthStatus.\
                    UNKNOWN
            elif speed == consts.CONSTANT_ZERO:
                hardware_result['connection_status'] = \
                    constants.PortConnectionStatus.DISCONNECTED
                hardware_result['health_status'] = constants.PortHealthStatus.\
                    ABNORMAL
                hardware_result['speed'] = speed
            else:
                hardware_result['connection_status'] = \
                    constants.PortConnectionStatus.CONNECTED
                hardware_result['health_status'] = constants.PortHealthStatus.\
                    NORMAL
                hardware_result['speed'] = int(speed)

            port = ports.get(hardware_name)
            if port:
                hardware_result['wwn'] = port.get('wwn')

            network = networks.get(hardware_name)
            if network:
                hardware_result['address'] = network.get('address')
                hardware_result['logical_type'] = network.get('logical_type')
                hardware_result['ipv4_mask'] = network.get('ipv4_mask')
            list_ports.append(hardware_result)
        return list_ports

    def get_ports(self):
        ports_dict = dict()
        ports = self.rest_handler.rest_call(self.rest_handler.REST_PORT_URL)
        if ports:
            for port in ports:
                port_dict = dict()
                port_name = port.get('name')
                wwn = port.get('wwn')
                port_dict['wwn'] = self.get_splice_wwn(wwn)\
                    if wwn is not None else port.get('iqn')
                ports_dict[port_name] = port_dict
        return ports_dict

    @staticmethod
    def get_splice_wwn(wwn):
        wwn_list = list(wwn)
        wwn_splice = wwn_list[0]
        for serial in range(1, len(wwn_list)):
            if serial % consts.SPLICE_WWN_SERIAL == consts.CONSTANT_ZERO:
                wwn_splice = '{}{}'.format(wwn_splice, consts.SPLICE_WWN_COLON)
            wwn_splice = '{}{}'.format(wwn_splice, wwn_list[serial])
        return wwn_splice

    def get_network(self):
        networks_object = dict()
        networks = self.rest_handler.rest_call(
            self.rest_handler.REST_NETWORK_URL)
        if networks:
            for network in networks:
                network_dict = dict()
                network_dict['address'] = network.get('address')
                services_list = network.get('services')
                if services_list:
                    for services in services_list:
                        network_dict['logical_type'] = services if \
                            services in constants.PortLogicalType.ALL else None
                        break
                network_dict['ipv4_mask'] = network.get('netmask')
                network_name = network.get('name').upper()
                networks_object[network_name] = network_dict
        return networks_object

    def list_storage_pools(self, context):
        pool_list = []
        pools = self.rest_handler.rest_call(
            self.rest_handler.REST_POOLS_CAPACITY_URL)
        if pools:
            for pool in pools:
                pool_result = dict()
                total_capacity = int(pool.get('size', consts.DEFAULT_CAPACITY))
                if total_capacity == consts.DEFAULT_CAPACITY:
                    continue
                pool_result['total_capacity'] = total_capacity
                used_capacity = int(pool.get('total_reduction',
                                             consts.DEFAULT_CAPACITY))
                pool_result['used_capacity'] = used_capacity
                pool_result['free_capacity'] = total_capacity - used_capacity
                pool_result['name'] = pool.get('name')
                pool_result['native_storage_pool_id'] = pool.get('name')
                pool_result['storage_id'] = self.storage_id
                pool_result['status'] = constants.StoragePoolStatus.NORMAL
                pool_result['storage_type'] = constants.StorageType.BLOCK
                pool_list.append(pool_result)
        return pool_list

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.login()
