import time

import six
from oslo_log import log as logging

from delfin import exception
from delfin.common import constants, alert_util
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


LOG = logging.getLogger(__name__)


class SSHHandler():

    OID_ERR_ID = '1.3.6.1.3.94.1.11.1.1'
    OID_EVENT_TYPE = '1.3.6.1.3.94.1.11.1.7'
    OID_LAST_TIME = '1.3.6.1.3.94.1.11.1.4'
    OID_EVENT_DESC = '1.3.6.1.3.94.1.11.1.9'
    OID_EVENT_ID = '1.3.6.1.3.94.1.11.1.3'
    OID_SEVERITY = '1.3.6.1.3.94.1.11.1.6'

    TRAP_SEVERITY_MAP = {
        '1': 'unknown',
        '2': 'emergency',
        '3': 'alert',
        '4': constants.Severity.CRITICAL,
        '5': 'error',
        '6': constants.Severity.WARNING,
        '7': 'notify',
        '8': constants.Severity.INFORMATIONAL,
        '9': 'debug',
        '10': 'mark'
    }

    SEVERITY_MAP = {"warning": "Warning",
                    "informational": "Informational",
                    "error": "Major"
                    }

    SECONDS_TO_MS = 1000

    DISK_PHYSICAL_TYPE = {
        'fc': constants.DiskPhysicalType.FC,
        'SAS': constants.DiskPhysicalType.SAS
    }

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    def login(self):
        try:
            pool_info = self.ssh_pool.do_exec('show pools')
            if 'is not a recognized command' in pool_info:
                raise exception.InvalidIpOrPort()
        except Exception as e:
            LOG.error("Failed to login msa  %s" %
                      (six.text_type(e)))
            raise e

    def get_storage(self, storage_id):
        try:
            system_info = self.ssh_pool.do_exec('show system')
            system_data = self.handle_detail(system_info, 'system')
            version_info = self.ssh_pool.do_exec('show version')
            version_arr = self.handle_detail(version_info, 'versions')
            if version_arr:
                version_id = version_arr[0]\
                    .get('bundle-version')
            if system_data:
                pool_arr = self.list_storage_pools(storage_id)
                total_capacity = 0
                for pool in pool_arr:
                    total_capacity += int(pool.get('total_capacity'))
                disk_arr = self.list_storage_disks(storage_id)
                disk_all = 0
                for disk in disk_arr:
                    disk_all += int(disk.get('capacity'))
                volume_arr = self.list_storage_volume(storage_id)
                volume_all = 0
                for volume in volume_arr:
                    volume_all += int(volume.get('total_capacity'))
                for storage_info in system_data:
                    health = storage_info.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    ser_num = storage_info.get('midplane-serial-number', '')
                    storage_map = {
                        'name': storage_info.get('system-name', ''),
                        'vendor': storage_info.get('vendor-name', ''),
                        'model': storage_info.get('product-id', ''),
                        'status': status,
                        'serial_number': ser_num,
                        'firmware_version': version_id,
                        'location': storage_info.get('system-location', ''),
                        'raw_capacity': int(disk_all),
                        'total_capacity': int(total_capacity),
                        'used_capacity': int(volume_all),
                        'free_capacity': int(total_capacity - volume_all)
                    }
            return storage_map
        except Exception as e:
            err_msg = "Failed to get storage : %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_disks(self, storage_id):
        try:
            disk_info = self.ssh_pool.do_exec('show disks')
            disk_detail = self.handle_detail(disk_info, 'drives')
            disks_arr = []
            if disk_detail:
                for data in disk_detail:
                    health = data['health']
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    size = self.parse_string(data.get('size'))
                    physical_type = SSHHandler.DISK_PHYSICAL_TYPE.\
                        get(data.get('description'),
                            constants.DiskPhysicalType.UNKNOWN)
                    data_map = {
                        'native_disk_id': data.get('location', ''),
                        'name': data.get('location', ''),
                        'physical_type': physical_type,
                        'status': status,
                        'storage_id': storage_id,
                        'native_disk_group_id': data.get('disk-group', ''),
                        'serial_number': data.get('serial-number', ''),
                        'manufacturer': data.get('vendor', ''),
                        'model': data.get('model', ''),
                        'speed': data.get('rpm', ''),
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
            ports_arr = ports_info.split('\n')
            ports_array = ports_arr[1:len(ports_arr) - 1]
            ports_xml = ''.join(ports_array)
            xml_element = ET.fromstring(ports_xml)
            port_detail = []
            for ch in xml_element.iter("OBJECT"):
                property_name = ch.get('basetype')
                if property_name != 'status':
                    msg = {}
                    for child in ch.iter("PROPERTY"):
                        msg[child.get('name')] = child.text
                    port_detail.append(msg)
            list_all_ports = []
            for i in range(0, len(port_detail) - 1, 2):
                aa = port_detail[i].copy()
                aa.update(port_detail[i + 1])
                list_all_ports.append(aa)
            list_ports = []
            if list_all_ports:
                for data in list_all_ports:
                    status = constants.PortHealthStatus.NORMAL
                    conn_status = constants.PortConnectionStatus.CONNECTED
                    if data.get('health') != 'OK':
                        status = constants.PortHealthStatus.ABNORMAL
                        conn_status = constants.PortConnectionStatus.\
                            DISCONNECTED
                    port_type = constants.PortType.FC
                    if data.get('port-type') == 'iSCSI':
                        port_type = constants.PortType.ETH
                    location = '%s_%s' % (data.get('port'),
                                          data.get('port-type').upper())
                    speed = data.get('configured-speed', None)
                    max_speed = 0
                    if speed != 'Auto' and speed is not None:
                        max_speed = self.parse_string(speed)
                    speed = data.get('configured-speed')
                    dataMap = {
                        'native_port_id': data.get('durable-id', ''),
                        'name': data.get('port', ''),
                        'type': port_type,
                        'connection_status': conn_status,
                        'health_status': status,
                        'location': location,
                        'storage_id': storage_id,
                        'speed': max_speed,
                        'max_speed': max_speed,
                        'wwn': '',
                        'mac_address': data.get('mac-address', ''),
                        'ipv4': data.get('ip-address', '')
                    }
                    list_ports.append(dataMap)
            return list_ports
        except Exception as e:
            err_msg = "Failed to get storage ports: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_controller(self, storage_id):
        try:
            controller_info = self.ssh_pool\
                .do_exec('show controllers')
            controller_detail = self.handle_detail(controller_info,
                                                   'controllers')
            controller_arr = []
            if controller_detail:
                for data in controller_detail:
                    health = data.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    cpu_info = str(data.get('sc-cpu-type', ''))
                    memory_size = data.get('system-memory-size') + "MB"
                    system_memory_size = self.parse_string(
                        memory_size)
                    data_map = {
                        'native_controller_id': data.get('controller-id', ''),
                        'name': data.get('durable-id', ''),
                        'storage_id': storage_id,
                        'status': status,
                        'location': data.get('position', ''),
                        'soft_version': data.get('sc-fw', ''),
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
            volume_detail = self.handle_detail(volume_infos, 'volumes')
            pools_info = self.ssh_pool.do_exec('show pools')
            pool_detail = self.handle_detail(pools_info, 'pools')
            list_volumes = []
            if volume_detail:
                for data in volume_detail:
                    health = data.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    total_size = self.parse_string(data.get('total-size'))
                    total_avail = self.parse_string(data.get('allocated-size'))
                    native_storage_pool_id = ''
                    for pools in pool_detail:
                        if data.get("virtual-disk-name") == pools.\
                                get("name"):
                            native_storage_pool_id = pools.\
                                get("serial-number")
                    data_map = {
                        'name': data.get('volume-name', ''),
                        'storage_id': storage_id,
                        'description': data.get('volume-name', ''),
                        'status': status,
                        'native_volume_id': str(data.get('durable-id', '')),
                        'native_storage_pool_id': native_storage_pool_id,
                        'wwn': str(data.get('wwn', '')),
                        'type': data.get('volume-type', ''),
                        'total_capacity': int(total_size),
                        'free_capacit': int(total_avail),
                        'used_capacity': int(total_size - total_avail),
                        'blocks': int(data.get("blocks")),
                        'compressed': True,
                        'deduplicated': True
                    }
                    list_volumes.append(data_map)
            return list_volumes
        except Exception as e:
            err_msg = "Failed to get storage volume: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_pools(self, storage_id):
        try:
            pool_infos = self.ssh_pool.do_exec('show pools')
            pool_detail = self.handle_detail(pool_infos, 'pools')
            volume_arr = self.list_storage_volume(storage_id)
            pool_arr = []
            if pool_detail:
                for data in pool_detail:
                    volume_size = 0
                    blocks = 0
                    for volume in volume_arr:
                        if volume.get("native_storage_pool_id") == data.\
                                get("serial-number"):
                            volume_size += volume.get("total_capacity")
                            blocks += volume.get("blocks")
                    health = data.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    total_size = self.parse_string(data.get('total-size'))
                    data_map = {
                        'name': data.get('name', ''),
                        'storage_id': storage_id,
                        'native_storage_pool_id': data.get('serial-number',
                                                           ''),
                        'description': '',
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_size),
                        'subscribed_capacity': int(blocks),
                        'used_capacity': volume_size,
                        'free_capacity': int(total_size - volume_size)
                    }
                pool_arr.append(data_map)
            return pool_arr
        except Exception as e:
            err_msg = "Failed to get storage pool: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def parse_string(self, value):
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

    def handle_detail(self, deltail_info, element):
        detail_arr = []
        detail_data = deltail_info.split('\n')
        detail = detail_data[1:len(detail_data) - 1]
        detail_xml = ''.join(detail)
        xml_element = ET.fromstring(detail_xml)
        for ch in xml_element.iter("OBJECT"):
            property_name = ch.get('basetype')
            if element == property_name:
                msg = {}
                for child in ch.iter("PROPERTY"):
                    msg[child.get('name')] = child.text
                detail_arr.append(msg)
        return detail_arr

    def list_storage_error(self, query_para):
        alert_list = []
        try:
            error_infos = self.ssh_pool.do_exec('show events error')
            err_arr = self.handle_detail(error_infos, 'events')
            if err_arr:
                for alert_map in err_arr:
                    time_stamp = alert_map.get('time-stamp-numeric')
                    occur_time = int(time_stamp) * self.SECONDS_TO_MS
                    if not alert_util.is_alert_in_time_range(query_para,
                                                             occur_time):
                        continue
                    alert_name = alert_map.get('message', '')
                    event_id = alert_map.get('event-id')
                    location = alert_map.get('serial-number', '')
                    resource_type = alert_map.get('event-code', '')
                    severity = alert_map.get('severity')
                    if severity == 'Informational' or severity is None:
                        continue
                    alert_model = {
                        'alert_id': event_id,
                        'alert_name': alert_name,
                        'severity': severity,
                        'category': constants.Category.FAULT,
                        'type': 'EquipmentAlarm',
                        'sequence_number': alert_map.get('event-code'),
                        'occur_time': occur_time,
                        'description': alert_name,
                        'resource_type': resource_type,
                        'location': location
                    }
                    alert_list.append(alert_model)
            return self.repeated_err(alert_list)
        except Exception as e:
            err_msg = "Failed to get storage error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def repeated_err(self, detail_info):
        exist_questions = set()
        detail_arr = []
        for item in detail_info:
            question = item['resource_type']
            if question not in exist_questions:
                exist_questions.add(question)
                detail_arr.append(item)
        return detail_arr

    @staticmethod
    def parse_alert(alert):
        try:
            alert_model = dict()
            alert_id = ''
            description = ''
            severity = SSHHandler.TRAP_SEVERITY_MAP.get('8')
            seq_num = ''
            event_type = ''
            for alert_key, alert_value in alert.items():
                if SSHHandler.OID_ERR_ID in alert_key:
                    alert_id = str(alert_value)
                elif SSHHandler.OID_EVENT_TYPE in alert_key:
                    event_type = alert_value
                elif SSHHandler.OID_EVENT_DESC in alert_key:
                    description = alert_value
                elif SSHHandler.OID_SEVERITY in alert_key:
                    severity = SSHHandler.TRAP_SEVERITY_MAP\
                        .get(alert.get(SSHHandler.OID_SEVERITY),
                             constants.Severity.INFORMATIONA)
                elif SSHHandler.OID_EVENT_ID in alert_key:
                    seq_num = alert_value
            if len(description) > 0:
                desc_arr = description.split(",")
                if desc_arr:
                    alert_id = SSHHandler.handle_split(desc_arr[0], ":", 1)
                    if len(desc_arr) > 2:
                        description = desc_arr[1]
            alert_model['alert_id'] = str(alert_id)
            alert_model['alert_name'] = event_type
            alert_model['severity'] = severity
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['sequence_number'] = seq_num
            now = time.time()
            alert_model['occur_time'] = int(round(now * SSHHandler.
                                            SECONDS_TO_MS))
            alert_model['description'] = description
            alert_model['resource_type'] = ''
            alert_model['location'] = description
            print(alert_model)
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = ("Failed to build alert model as some attributes missing "
                   "in alert message:%s.") % (six.text_type(e))
            raise exception.InvalidResults(msg)

    @staticmethod
    def handle_split(split_str, split_char, arr_number):
        split_value = ''
        if split_str is not None and split_str != '':
            tmp_value = split_str.split(split_char, 1)
            if arr_number == 1 and len(tmp_value) > 1:
                split_value = tmp_value[arr_number].strip()
            elif arr_number == 0:
                split_value = tmp_value[arr_number].strip()
        return split_value
