import hashlib
import time

import six
from oslo_log import log as logging
from operator import itemgetter
from itertools import groupby
from delfin import exception
from delfin.common import constants, alert_util
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools
from delfin.drivers.hpe.hpe_msa import consts

try:
    import xml.etree.cElementTree as Et
except ImportError:
    import xml.etree.ElementTree as Et

LOG = logging.getLogger(__name__)

ssh = {
        "host": "192.168.3.212",
        "port": 22,
        "username": "manage",
        "password": "manage@Z",
        "pub_key": "ddddddddddddddddddddddddd"
    }

class SSHHandler(object):

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    def login(self):
        try:
            self.ssh_pool.do_exec('show pools')
        except Exception as e:
            LOG.error("Failed to login msa  %s" %
                      (six.text_type(e)))
            raise e

    def get_storage(self, storage_id):
        try:
            system_info = self.ssh_pool.do_exec('show system')
            system_data = self.handle_xml_to_dict(system_info, 'system')
            version_info = self.ssh_pool.do_exec('show version')
            version_arr = self.handle_xml_to_json(version_info, 'versions')
            version_id = ""
            if version_arr:
                version_id = version_arr[0].get('bundle-version')
            if system_data:
                pools_list = self.list_storage_pools(storage_id)
                total_capacity = 0
                if pools_list:
                    for pool in pools_list:
                        total_capacity += int(pool.get('total_capacity'))
                disks_list = self.list_storage_disks(storage_id)
                raw_capacity = 0
                if disks_list:
                    for disk in disks_list:
                        raw_capacity += int(disk.get('capacity'))
                volumes_list = self.list_storage_volume(storage_id)
                volume_all_size = 0
                if volumes_list:
                    for volume in volumes_list:
                        volume_all_size += int(volume.get('total_capacity'))
                health = system_data.get('health')
                status = constants.StorageStatus.OFFLINE
                if health == 'OK':
                    status = constants.StorageStatus.NORMAL
                elif health == 'Degraded':
                    status = constants.StorageStatus.DEGRADED
                serial_num = system_data.get('midplane-serial-number')
                storage_map = {
                    'name': system_data.get('system-name'),
                    'vendor': consts.StorageVendor.HPE_MSA_VENDOR,
                    'model': system_data.get('product-id'),
                    'status': status,
                    'serial_number': serial_num,
                    'firmware_version': version_id,
                    'location': system_data.get('system-location'),
                    'raw_capacity': int(raw_capacity),
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(volume_all_size),
                    'free_capacity': int(total_capacity - volume_all_size)
                }
                return storage_map
        except Exception as e:
            err_msg = "Failed to get system info : %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_disks(self, storage_id):
        try:
            disk_info = self.ssh_pool.do_exec('show disks')
            disk_detail = self.handle_xml_to_json(disk_info, 'drives')
            disks_arr = []
            if disk_detail:
                for data in disk_detail:
                    health = data.get('health')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    size = self.parse_string_to_bytes(data.get('size'))
                    physical_type = consts.DiskPhysicalType.\
                        DISK_PHYSICAL_TYPE.get(data.get('description'),
                                               constants.DiskPhysicalType.
                                               UNKNOWN)
                    rpm = data.get('rpm')
                    if rpm:
                        rpm = int(rpm) * consts.RpmSpeed.RPM_SPEED
                    data_map = {
                        'native_disk_id': data.get('location'),
                        'name': data.get('location'),
                        'physical_type': physical_type,
                        'status': status,
                        'storage_id': storage_id,
                        'native_disk_group_id': data.get('disk-group'),
                        'serial_number': data.get('serial-number'),
                        'manufacturer': data.get('vendor'),
                        'model': data.get('model'),
                        'speed': rpm,
                        'capacity': int(size),
                        'health_score': status
                    }
                    disks_arr.append(data_map)
            return disks_arr
        except Exception as e:
            err_msg = "Failed to get storage disk: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_ports(self, storage_id):
        try:
            ports_info = self.ssh_pool.do_exec('show ports')
            ports_split = ports_info.split('\n')
            ports_array = ports_split[1:len(ports_split) - 1]
            ports_xml_data = ''.join(ports_array)
            xml_element = Et.fromstring(ports_xml_data)
            ports_json = []
            for element_data in xml_element.iter('OBJECT'):
                property_name = element_data.get('basetype')
                if property_name != 'status':
                    msg = {}
                    for child in element_data.iter('PROPERTY'):
                        msg[child.get('name')] = child.text
                    ports_json.append(msg)
            ports_elements_info = []
            for i in range(0, len(ports_json) - 1, 2):
                port_element = ports_json[i].copy()
                port_element.update(ports_json[i + 1])
                ports_elements_info.append(port_element)
            list_ports = []
            for data in ports_elements_info:
                status = constants.PortHealthStatus.NORMAL
                conn_status = constants.PortConnectionStatus.CONNECTED
                if data.get('health') != 'OK':
                    status = constants.PortHealthStatus.ABNORMAL
                    conn_status = constants.PortConnectionStatus.\
                        DISCONNECTED
                wwn = None
                port_type = constants.PortType.FC
                location_port_type = data.get('port-type')
                if location_port_type:
                    location_port_type = location_port_type.upper()
                if location_port_type == 'ISCSI':
                    port_type = constants.PortType.ETH
                else:
                    target_id = data.get('target-id')
                    if target_id:
                        wwn = target_id
                location = '%s_%s' % (data.get('port'),
                                      location_port_type)
                speed = data.get('configured-speed', None)
                max_speed = 0
                if speed != 'Auto' and speed is not None:
                    max_speed = self.parse_string_to_bytes(speed)
                data_map = {
                    'native_port_id': data.get('durable-id'),
                    'name': data.get('port'),
                    'type': port_type,
                    'connection_status': conn_status,
                    'health_status': status,
                    'location': location,
                    'storage_id': storage_id,
                    'speed': max_speed,
                    'max_speed': max_speed,
                    'mac_address': data.get('mac-address'),
                    'ipv4': data.get('ip-address'),
                    'wwn': wwn
                }
                list_ports.append(data_map)
            return list_ports
        except Exception as e:
            err_msg = "Failed to get storage ports: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_controller(self, storage_id):
        try:
            controller_info = self.ssh_pool\
                .do_exec('show controllers')
            controller_detail = self.handle_xml_to_json(
                controller_info, 'controllers')
            controller_arr = []
            for data in controller_detail:
                health = data.get('health')
                status = constants.StoragePoolStatus.OFFLINE
                if health == 'OK':
                    status = constants.StoragePoolStatus.NORMAL
                cpu_info = data.get('sc-cpu-type')
                memory_size = data.get('system-memory-size')
                if memory_size is not None:
                    memory_size = memory_size + "MB"
                system_memory_size = self.parse_string_to_bytes(
                    memory_size)
                data_map = {
                    'native_controller_id': data.get('controller-id'),
                    'name': data.get('durable-id'),
                    'storage_id': storage_id,
                    'status': status,
                    'location': data.get('position'),
                    'soft_version': data.get('sc-fw'),
                    'cpu_info': cpu_info,
                    'memory_size': int(system_memory_size)
                }
                controller_arr.append(data_map)
            return controller_arr
        except Exception as e:
            err_msg = "Failed to get storage controllers: %s"\
                      % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_volume(self, storage_id):
        try:
            volume_infos = self.ssh_pool.do_exec('show volumes')
            volume_detail = self.handle_xml_to_json(volume_infos, 'volumes')
            pools_info = self.ssh_pool.do_exec('show pools')
            pool_detail = self.handle_xml_to_json(pools_info, 'pools')
            list_volumes = []
            for data in volume_detail:
                health = data.get('health')
                status = constants.StoragePoolStatus.OFFLINE
                if health == 'OK':
                    status = constants.StoragePoolStatus.NORMAL
                total_size = self.parse_string_to_bytes(data.get('total-size'))
                total_avail = self.parse_string_to_bytes(
                    data.get('allocated-size'))
                native_storage_pool_id = ''
                if pool_detail:
                    native_storage_pool_id = pool_detail[0]. \
                        get('serial-number')
                    for pools in pool_detail:
                        if data.get('virtual-disk-name') == pools.\
                                get('name'):
                            native_storage_pool_id = pools.\
                                get('serial-number')
                blocks = data.get('blocks')
                if blocks is not None:
                    blocks = int(blocks)
                volume_map = {
                    'name': data.get('volume-name'),
                    'storage_id': storage_id,
                    'description': data.get('volume-name'),
                    'status': status,
                    'native_volume_id': str(data.get('durable-id')),
                    'native_storage_pool_id': native_storage_pool_id,
                    'wwn': str(data.get('wwn')),
                    'type': data.get('volume-type'),
                    'total_capacity': int(total_size),
                    'free_capacit': int(total_size - total_avail),
                    'used_capacity': int(total_avail),
                    'blocks': int(blocks),
                    'compressed': True,
                    'deduplicated': True
                }
                list_volumes.append(volume_map)
            return list_volumes
        except Exception as e:
            err_msg = "Failed to get storage volume: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_pools(self, storage_id):
        try:
            pool_infos = self.ssh_pool.do_exec('show pools')
            pool_detail = self.handle_xml_to_json(pool_infos, 'pools')
            volume_list = self.list_storage_volume(storage_id)
            pools_list = []
            if pool_detail:
                for data in pool_detail:
                    volume_size = 0
                    blocks = 0
                    if volume_list:
                        for volume in volume_list:
                            if volume.get('native_storage_pool_id') == data.\
                                    get('serial-number'):
                                volume_size += volume.get('total_capacity')
                                blocks += volume.get('blocks')
                    health = data.get('health')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    total_size = self.parse_string_to_bytes(
                        data.get('total-size'))
                    pool_map = {
                        'name': data.get('name'),
                        'storage_id': storage_id,
                        'native_storage_pool_id': data.get('serial-number'),
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_size),
                        'subscribed_capacity': int(blocks),
                        'used_capacity': volume_size,
                        'free_capacity': int(total_size - volume_size)
                    }
                    pools_list.append(pool_map)
            return pools_list
        except Exception as e:
            err_msg = "Failed to get storage pool: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    @staticmethod
    def parse_string_to_bytes(value):
        capacity = 0
        if value:
            if value.isdigit():
                capacity = float(value)
            else:
                if value == '0B':
                    capacity = 0
                else:
                    unit = value[-2:]
                    capacity = float(value[:-2]) * int(
                        Tools.change_capacity_to_bytes(unit))
        return capacity

    @staticmethod
    def handle_xml_to_json(detail_info, element):
        detail_arr = []
        detail_data = detail_info.split('\n')
        detail = detail_data[1:len(detail_data) - 1]
        detail_xml = ''.join(detail)
        xml_element = Et.fromstring(detail_xml)
        for children in xml_element.iter('OBJECT'):
            property_name = children.get('basetype')
            if element == property_name:
                msg = {}
                for child in children.iter('PROPERTY'):
                    msg[child.get('name')] = child.text
                detail_arr.append(msg)
        return detail_arr

    def list_alerts(self, query_para):
        alert_list = []
        try:
            alert_infos = self.ssh_pool.do_exec('show events error')
            alert_json = self.handle_xml_to_json(alert_infos, 'events')
            for alert_map in alert_json:
                now = time.time()
                occur_time = int(round(now * consts.SecondsNumber
                                       .SECONDS_TO_MS))
                time_stamp = alert_map.get('time-stamp-numeric')
                if time_stamp is not None:
                    occur_time = int(time_stamp)
                    if not alert_util.is_alert_in_time_range(query_para,
                                                             occur_time):
                        continue
                event_code = alert_map.get('event-code')
                event_id = alert_map.get('event-id')
                location = alert_map.get('message')
                resource_type = alert_map.get('event-code')
                severity = alert_map.get('severity')
                additional_info = str(alert_map.get('additional-information'))
                match_key = None
                if event_code:
                    match_key = event_code
                if severity:
                    match_key += severity
                if location:
                    match_key += location
                description = None
                if additional_info:
                    description = additional_info
                if severity == 'Informational' or severity == 'RESOLVED':
                    continue
                alert_model = {
                    'alert_id': event_id,
                    'alert_name': event_code,
                    'severity': severity,
                    'category': constants.Category.FAULT,
                    'type': 'EquipmentAlarm',
                    'sequence_number': event_id,
                    'occur_time': occur_time,
                    'description': description,
                    'resource_type': resource_type,
                    'location': location,
                    'time': alert_map.get('time-stamp'),
                    'match_key': hashlib.md5(match_key.encode()).hexdigest()
                }
                alert_list.append(alert_model)
            alert_list_data = SSHHandler.get_last_alert_data(alert_list)
            return alert_list_data
        except Exception as e:
            err_msg = "Failed to get storage alert: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    @staticmethod
    def get_last_alert_data(alert_json):
        alert_list = []
        alert_json.sort(key=itemgetter('alert_name', 'location', 'severity'))
        for key, item in groupby(alert_json, key=itemgetter(
                'alert_name', 'location', 'severity')):
            i = 0
            for alert_info in item:
                if i == 0:
                    alert_list.append(alert_info)
                    break
                i = i + 1
        return alert_list

    @staticmethod
    def parse_alert(alert):
        try:
            alert_model = dict()
            alert_id = None
            description = None
            severity = consts.TrapSeverity.TRAP_SEVERITY_MAP.get('8')
            sequence_number = None
            event_type = None
            for alert_key, alert_value in alert.items():
                if consts.AlertOIDNumber.OID_ERR_ID in alert_key:
                    alert_id = str(alert_value)
                elif consts.AlertOIDNumber.OID_EVENT_TYPE in alert_key:
                    event_type = alert_value
                elif consts.AlertOIDNumber.OID_EVENT_DESC in alert_key:
                    description = alert_value
                elif consts.AlertOIDNumber.OID_SEVERITY in alert_key:
                    severity = consts.TrapSeverity.TRAP_SEVERITY_MAP\
                        .get(alert.get(consts.AlertOIDNumber.OID_SEVERITY),
                             constants.Severity.INFORMATIONAL)
                elif consts.AlertOIDNumber.OID_EVENT_ID in alert_key:
                    sequence_number = alert_value
            if description:
                desc_arr = description.split(",")
                if desc_arr:
                    alert_id = SSHHandler.split_by_char_and_number(
                        desc_arr[0], ":", 1)
                    if len(desc_arr) > 2:
                        description = desc_arr[1]
            alert_model['alert_id'] = str(alert_id)
            alert_model['alert_name'] = event_type
            alert_model['severity'] = severity
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['sequence_number'] = sequence_number
            now = time.time()
            alert_model['occur_time'] = int(round(now * consts.
                                                  SecondsNumber.SECONDS_TO_MS))
            alert_model['description'] = description
            alert_model['location'] = description
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = "Failed to build alert model: %s." % (six.text_type(e))
            raise exception.InvalidResults(msg)

    @staticmethod
    def split_by_char_and_number(split_str, split_char, arr_number):
        split_value = ''
        if split_str:
            tmp_value = split_str.split(split_char, 1)
            if arr_number == 1 and len(tmp_value) > 1:
                split_value = tmp_value[arr_number].strip()
            elif arr_number == 0:
                split_value = tmp_value[arr_number].strip()
        return split_value

    @staticmethod
    def handle_xml_to_dict(xml_info, element):
        msg = {}
        xml_split = xml_info.split('\n')
        xml_data = xml_split[1:len(xml_split) - 1]
        detail_xml = ''.join(xml_data)
        xml_element = Et.fromstring(detail_xml)
        for children in xml_element.iter('OBJECT'):
            property_name = children.get('basetype')
            if element == property_name:
                for child in children.iter('PROPERTY'):
                    msg[child.get('name')] = child.text
        return msg
