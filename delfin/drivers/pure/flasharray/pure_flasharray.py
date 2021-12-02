import datetime
import hashlib

from oslo_log import log

from delfin import exception, utils
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.pure.flasharray import rest_handler, consts
from delfin.i18n import _

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
            for volume in volumes:
                volume_name = volume.get('name')
                total_capacity = int(volume.get('size',
                                                consts.DEFAULT_CAPACITY))
                used_capacity = int(volume.get('volumes',
                                               consts.DEFAULT_CAPACITY))
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
                    else constants.VolumeType.THICK
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
                used_capacity = int(storage.get('total',
                                                consts.DEFAULT_CAPACITY))
                total_capacity = int(storage.get('capacity',
                                                 consts.DEFAULT_CAPACITY))
                break
        raw_capacity = consts.DEFAULT_CAPACITY
        disks = self.rest_handler.rest_call(self.rest_handler.REST_DISK_URL)
        if disks:
            for disk in disks:
                raw_capacity = raw_capacity + int(disk.get(
                    'capacity', consts.DEFAULT_CAPACITY))
        arrays = self.rest_handler.rest_call(self.rest_handler.REST_ARRAY_URL)
        storage_name = None
        serial_number = None
        version = None
        if arrays:
            storage_name = arrays.get('array_name')
            serial_number = arrays.get('id')
            version = arrays.get('version')
        model = None
        status = constants.StorageStatus.NORMAL
        controllers = self.rest_handler.rest_call(
            self.rest_handler.REST_CONTROLLERS_URL)
        if controllers:
            for controller in controllers:
                if controller.get('mode') == consts.CONTROLLER_PRIMARY:
                    model = controller.get('model')
                if controller.get('status') != consts.NORMAL_CONTROLLER_STATUS:
                    status = constants.StorageStatus.ABNORMAL
        if not all((storages, arrays, controllers)):
            LOG.error('get_storage error, Unable to obtain data.')
            raise exception.StorageBackendException('Unable to obtain data')
        storage_result = {
            'model': model,
            'total_capacity': total_capacity,
            'raw_capacity': raw_capacity,
            'used_capacity': used_capacity,
            'free_capacity': total_capacity - used_capacity,
            'vendor': 'PURE',
            'name': storage_name,
            'serial_number': serial_number,
            'firmware_version': version,
            'status': status
        }
        return storage_result

    def list_alerts(self, context, query_para=None):
        alerts = self.rest_handler.rest_call(self.rest_handler.REST_ALERTS_URL)
        alerts_list = []
        if alerts:
            for alert in alerts:
                alerts_model = dict()
                time = alert.get('opened')
                timestamp = int(datetime.datetime.strptime(
                    time, '%Y-%m-%dT%H:%M:%SZ').timestamp()
                    * consts.DEFAULT_LIST_ALERTS_TIME_CONVERSION)\
                    if time is not None else None
                if query_para is not None:
                    try:
                        start_time = int(query_para.get('start_time'))
                        end_time = int(query_para.get('end_time'))
                    except Exception as e:
                        LOG.error(e)
                        msg = (_("Time conversion error"))
                        raise exception.InvalidResults(msg)
                    if timestamp is None or timestamp < start_time or \
                            timestamp > end_time:
                        continue
                alerts_model['occur_time'] = timestamp
                alerts_model['alert_id'] = alert.get('id')
                alerts_model['severity'] = consts.SEVERITY_MAP.get(
                    alert.get('current_severity'),
                    constants.Severity.NOT_SPECIFIED)
                alerts_model['category'] = constants.Category.FAULT
                component_name = alert.get('component_name')
                alerts_model['location'] = component_name
                alerts_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alerts_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                event = alert.get('event')
                alerts_model['alert_name'] = event
                alerts_model['sequence_number'] = alert.get('id')
                alerts_model['match_key'] = hashlib.md5(str(alert.get('id')).
                                                        encode()).hexdigest()
                alerts_model['description'] = '({}:{}): {}'.\
                    format(alert.get('component_type'), component_name, event)
                alerts_list.append(alerts_model)
        return alerts_list

    @staticmethod
    def parse_alert(context, alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = alert.get(consts.PARSE_ALERT_ALERT_ID)
            alert_model['severity'] = consts.PARSE_ALERT_SEVERITY_MAP.get(
                alert.get(consts.PARSE_ALERT_SEVERITY),
                constants.Severity.NOT_SPECIFIED)
            alert_model['category'] = constants.Category.FAULT
            alert_model['occur_time'] = utils.utcnow_ms()
            alert_model['description'] = '({}:{}): {}'.format(alert.get(
                consts.PARSE_ALERT_STORAGE_NAME),
                alert.get(consts.PARSE_ALERT_CONTROLLER_NAME),
                alert.get(consts.PARSE_ALERT_DESCRIPTION))
            alert_model['location'] = alert.get(
                consts.PARSE_ALERT_CONTROLLER_NAME)
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['alert_name'] = alert.get(
                consts.PARSE_ALERT_ALERT_NAME)
            alert_model['sequence_number'] = alert.get(
                consts.PARSE_ALERT_ALERT_ID)
            alert_model['match_key'] = hashlib.md5(str(alert.get(
                consts.PARSE_ALERT_ALERT_ID)).encode()).hexdigest()
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing"))
            raise exception.InvalidResults(msg)

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
                disk_type = disk.get('type')
                if disk_type == consts.DISK_TYPE_NVRAM:
                    continue
                disk_dict = dict()
                drive_name = disk.get('name')
                disk_dict['name'] = drive_name
                physical_type = disk_type.lower() if disk_type is not None \
                    else None
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
        hardware_dist = self.get_port_hardware()
        ports = self.get_ports()
        networks = self.rest_handler.rest_call(
            self.rest_handler.REST_NETWORK_URL)
        if networks:
            for network in networks:
                network_dict = dict()
                network_name = network.get('name').upper()
                if 'FC' in network_name:
                    network_dict['type'] = constants.PortType.FC
                elif 'ETH' in network_name:
                    network_dict['type'] = constants.PortType.ETH
                elif 'SAS' in network_name:
                    network_dict['type'] = constants.PortType.SAS
                else:
                    continue
                network_dict['storage_id'] = self.storage_id
                network_dict['name'] = network_name
                network_dict['native_port_id'] = network_name
                network_dict['location'] = network_name
                network_dict['mac_address'] = network.get('hwaddr')
                services_list = network.get('services')
                if services_list:
                    for services in services_list:
                        network_dict['logical_type'] = services if \
                            services in constants.PortLogicalType.ALL else None
                        break
                network_dict['ipv4_mask'] = network.get('netmask')
                network_dict['ipv4'] = network.get('address')
                port = ports.get(network_name)
                if port:
                    network_dict['wwn'] = port.get('wwn')
                hardware = hardware_dist.get(network_name)
                if hardware:
                    network_dict['connection_status'] = hardware.get(
                        'connection_status')
                    network_dict['health_status'] = hardware.get(
                        'health_status')
                    network_dict['speed'] = hardware.get('speed')
                list_ports.append(network_dict)
        return list_ports

    def get_port_hardware(self):
        hardware_name_dict = dict()
        hardware_dict = self.rest_handler.rest_call(
            self.rest_handler.REST_HARDWARE_URL)
        if hardware_dict:
            for hardware in hardware_dict:
                hardware_result = dict()
                hardware_name = hardware.get('name')
                hardware_result['name'] = hardware_name
                speed = hardware.get('speed')
                if speed is None:
                    hardware_result['connection_status'] = \
                        constants.PortConnectionStatus.UNKNOWN
                    hardware_result['health_status'] = constants.\
                        PortHealthStatus.UNKNOWN
                elif speed == consts.CONSTANT_ZERO:
                    hardware_result['connection_status'] = \
                        constants.PortConnectionStatus.DISCONNECTED
                    hardware_result['health_status'] = constants.\
                        PortHealthStatus.ABNORMAL
                    hardware_result['speed'] = speed
                else:
                    hardware_result['connection_status'] = \
                        constants.PortConnectionStatus.CONNECTED
                    hardware_result['health_status'] = constants.\
                        PortHealthStatus.NORMAL
                    hardware_result['speed'] = int(speed)
                hardware_name_dict[hardware_name] = hardware_result
        return hardware_name_dict

    def get_ports(self):
        ports_dict = dict()
        ports = self.rest_handler.rest_call(self.rest_handler.REST_PORT_URL)
        if ports:
            for port in ports:
                port_dict = dict()
                port_name = port.get('name')
                wwn = port.get('wwn')
                port_dict['wwn'] = self.get_splice_wwn(wwn) \
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

    def list_storage_pools(self, context):
        return []

    def remove_trap_config(self, context, trap_config):
        pass

    def reset_connection(self, context, **kwargs):
        self.rest_handler.logout()
        self.rest_handler.login()

    @staticmethod
    def get_access_url():
        return 'https://{ip}'
