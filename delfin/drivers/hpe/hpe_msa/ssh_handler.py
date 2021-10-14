import six

from oslo_log import log as logging
from delfin import exception
from delfin.common import constants, alert_util
from delfin.drivers.utils.ssh_client import SSHPool
from delfin.drivers.utils.tools import Tools

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET

LOG = logging.getLogger(__name__)


class SSHHandler():

    SECONDS_TO_MS = 1000

    DISK_PHYSICAL_TYPE = {
        'fc': constants.DiskPhysicalType.FC,
        'SAS': constants.DiskPhysicalType.SAS
    }

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    def login(self):
        try:
            result = self.ssh_pool.do_exec('show pools')
            if 'is not a recognized command' in result:
                raise exception.InvalidIpOrPort()
        except Exception as e:
            LOG.error("Failed to login msa storwize_svc %s" %
                      (six.text_type(e)))
            raise e

    def get_storage(self, storage_id):
        try:
            result = self.ssh_pool.do_exec('show system')
            list = self.analysisDataToList(result, 'system')
            version_result = self.ssh_pool.do_exec('show version')
            version_list = self.analysisDataToList(version_result,
                                                   'versions')
            if list:
                pool_list = self.list_storage_pools(storage_id)
                total_capacity = 0
                for pool in pool_list:
                    total_capacity += int(pool['total_capacity'])
                disk_list = self.list_storage_disks(storage_id)
                disk_all = 0
                for disk in disk_list:
                    disk_all += int(disk['capacity'])
                volume_list = self.list_storage_volume(storage_id)
                volume_all = 0
                for volume in volume_list:
                    volume_all += int(volume['total_capacity'])
                health = list[0]['health']
                status = constants.StoragePoolStatus.OFFLINE
                if health == 'OK':
                    status = constants.StoragePoolStatus.NORMAL
                dataMap = {
                    'name': list[0]['system-name'],
                    'vendor': list[0]['vendor-name'],
                    'model': list[0]['product-id'],
                    'status': status,
                    'serial_number': list[0]['midplane-serial-number'],
                    'firmware_version': version_list[0]['bundle-version'],
                    'location': list[0]['system-location'],
                    'raw_capacity': int(disk_all),
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(volume_all),
                    'free_capacity': int(total_capacity - volume_all)
                }
            return dataMap
        except Exception as e:
            err_msg = "Failed to get storage : %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_disks(self, storage_id):
        try:
            result = self.ssh_pool.do_exec('show disks')
            list = self.analysisDataToList(result, 'drives')
            list_disks = []
            if list:
                for data in list:
                    health = data['health']
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    size = self.parse_string(data['size'])
                    physical_type = SSHHandler.DISK_PHYSICAL_TYPE.\
                        get(data.get('description'),
                            constants.DiskPhysicalType.UNKNOWN)
                    dataMap = {
                       'native_disk_id': data['location'],
                       'name': data['location'],
                       'physical_type': physical_type,
                       'status': status,
                       'storage_id': storage_id,
                       'native_disk_group_id': data['disk-group'],
                       'serial_number': data['serial-number'],
                       'manufacturer': data['vendor'],
                       'model': data['model'],
                       'speed': data['rpm'],
                       'capacity': int(size),
                       'health_score': status
                    }
                    list_disks.append(dataMap)
            return list_disks
        except Exception as e:
            err_msg = "Failed to get storage disk: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_ports(self, storage_id):
        try:
            result = self.ssh_pool.do_exec('show ports')
            result_info = result.split('\n')
            result_list = result_info[1:len(result_info) - 1]
            result_xml = ''.join(result_list)
            root_elem = ET.fromstring(result_xml)
            list_port_detail = []
            for ch in root_elem.iter("OBJECT"):
                propertyName = ch.get('basetype')
                if propertyName != 'status':
                    msg = {}
                    for child in ch.iter("PROPERTY"):
                        msg[child.get('name')] = child.text
                    list_port_detail.append(msg)
            list_all_ports = []
            for i in range(0, len(list_port_detail)-1, 2):
                aa = list_port_detail[i].copy()
                aa.update(list_port_detail[i+1])
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
                    location = '%s_%s' % (data.get('port'),
                                          data.get('durable-id'))
                    port_type = constants.PortType.FC
                    if data.get('port-type') == 'iSCSI':
                        port_type = constants.PortType.ETH
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
            result = self.ssh_pool.do_exec('show controllers')
            list = self.analysisDataToList(result, 'controllers')
            list_controllers = []
            if list:
                for data in list:
                    health = data.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    cpu_info = str(data['sc-cpu-type'])
                    system_memory_size = self.parse_string(
                        data['system-memory-size']+"MB")
                    dataMap = {
                        'native_controller_id': data['controller-id'],
                        'name': data['durable-id'],
                        'storage_id': storage_id,
                        'status': status,
                        'location': data['position'],
                        'soft_version': data['sc-fw'],
                        'cpu_info': cpu_info,
                        'memory_size': int(system_memory_size)
                    }
                    list_controllers.append(dataMap)
            return list_controllers
        except Exception as e:
            err_msg = "Failed to get storage controllers: %s"\
                      % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_volume(self, storage_id):
        try:
            result = self.ssh_pool.do_exec('show volumes')
            list = self.analysisDataToList(result, 'volumes')
            result_pools = self.ssh_pool.do_exec('show pools')
            list_pools = self.analysisDataToList(result_pools, 'pools')
            list_volumes = []
            if list:
                for data in list:
                    health = data.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    total_size = self.parse_string(data['total-size'])
                    total_avail = self.parse_string(data['allocated-size'])
                    native_storage_pool_id = list_pools[0].\
                        get("serial-number")
                    for pools in list_pools:
                        if data.get("virtual-disk-name") == pools.\
                                get("name"):
                            native_storage_pool_id = pools.\
                                get("serial-number")
                    dataMap = {
                        'name': data['volume-name'],
                        'storage_id': storage_id,
                        'description': data['volume-name'],
                        'status': status,
                        'native_volume_id': str(data['durable-id']),
                        'native_storage_pool_id': native_storage_pool_id,
                        'wwn': str(data['wwn']),
                        'type': data['volume-type'],
                        'total_capacity': int(total_size),
                        'free_capacit': int(total_avail),
                        'used_capacity': int(total_size - total_avail),
                        'blocks': int(data.get("blocks")),
                        'compressed': True,
                        'deduplicated': True
                    }
                    list_volumes.append(dataMap)
            return list_volumes
        except Exception as e:
            err_msg = "Failed to get storage volume: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def list_storage_pools(self, storage_id):
        try:
            result = self.ssh_pool.do_exec('show pools')
            list = self.analysisDataToList(result, 'pools')
            volume_list = self.list_storage_volume(storage_id)
            pools_list = []
            if list:
                for data in list:
                    volume_size = 0
                    blocks = 0
                    for volume in volume_list:
                        if volume.get("native_storage_pool_id") == data.\
                                get("serial-number"):
                            volume_size += volume.get("total_capacity")
                            blocks += volume.get("blocks")
                    health = data.get('health', '')
                    status = constants.StoragePoolStatus.OFFLINE
                    if health == 'OK':
                        status = constants.StoragePoolStatus.NORMAL
                    total_size = self.parse_string(data['total-size'])
                    dataMap = {
                        'name': data['name'],
                        'storage_id': storage_id,
                        'native_storage_pool_id': data['serial-number'],
                        'description': '',
                        'status': status,
                        'storage_type': constants.StorageType.BLOCK,
                        'total_capacity': int(total_size),
                        'subscribed_capacity': int(blocks),
                        'used_capacity': volume_size,
                        'free_capacity': int(total_size - volume_size)
                    }
                pools_list.append(dataMap)
            return pools_list
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

    def analysisDataToList(self, result, dataName):
        list_xml = []
        result_info = result.split('\n')
        result_list = result_info[1:len(result_info) - 1]
        result_xml = ''.join(result_list)
        root_elem = ET.fromstring(result_xml)
        for ch in root_elem.iter("OBJECT"):
            propertyName = ch.get('basetype')
            if dataName == propertyName:
                msg = {}
                for child in ch.iter("PROPERTY"):
                    msg[child.get('name')] = child.text
                list_xml.append(msg)
        return list_xml

    def list_storage_error(self, query_para):
        alert_list = []
        try:
            result = self.ssh_pool.do_exec('show events error')
            list = self.analysisDataToList(result, 'events')
            if list:
                for alert_map in list:
                    occur_time = int(alert_map.get('time-stamp-numeric')) * \
                                 self.SECONDS_TO_MS
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
            return self.distinct2(alert_list)
        except Exception as e:
            err_msg = "Failed to get storage error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def distinct2(self, result_list):
        exist_questions = set()
        result = []
        for item in result_list:
            question = item['resource_type']
            if question not in exist_questions:
                exist_questions.add(question)
                result.append(item)
        return result


