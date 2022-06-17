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
    import defusedxml.cElementTree as Et
except ImportError:
    import defusedxml.ElementTree as Et

LOG = logging.getLogger(__name__)


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
            controller_info = self.ssh_pool.do_exec('show controllers')
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
                    memory_size += "MB"
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
                    occur_time = int(time_stamp) * consts.SecondsNumber\
                        .SECONDS_TO_MS
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
            alert_last_index = 0
            alert_list.append(list(item)[alert_last_index])
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

    def list_storage_host_initiators(self, storage_id):
        try:
            initiator_list = []
            host_groups_info = self.ssh_pool.do_exec("show initiators")
            host_groups_json = self.handle_xml_to_json(host_groups_info,
                                                       "initiator")
            type_switch = {
                consts.InitiatorType.ISCSI_INITIATOR_TYPE:
                    consts.InitiatorType.ISCSI_INITIATOR_DESCRIPTION,
                consts.InitiatorType.FC_INITIATOR_TYPE:
                    consts.InitiatorType.FC_INITIATOR_DESCRIPTION,
            }
            for initiator in host_groups_json:
                description = type_switch.get(
                    initiator.get('host-bus-type-numeric'),
                    consts.InitiatorType.UNKNOWN_INITIATOR_DESCRIPTION)
                initiator_item = {
                    "name": initiator.get('nickname'),
                    "type": description,
                    "alias": initiator.get('durable-id'),
                    "storage_id": storage_id,
                    "native_storage_host_initiator_id":
                        initiator.get('durable-id'),
                    "wwn": initiator.get('id'),
                    "status": constants.InitiatorStatus.ONLINE,
                    "native_storage_host_id": initiator.get('host-id')
                }
                initiator_list.append(initiator_item)
            return initiator_list
        except Exception as e:
            LOG.error("Failed to get initiator "
                      "from msa storage_id: %s" % storage_id)
            raise e

    def list_storage_hosts(self, storage_id):
        try:
            hosts_info = self.ssh_pool.do_exec('show host-groups')
            host_list = []
            hosts = self.handle_xml_to_json(hosts_info, 'host')
            host_set = set()
            for host in hosts:
                status = constants.HostStatus.NORMAL
                os_type = constants.HostOSTypes.HP_UX
                host_member_count = int(host.get('member-count'))
                if host_member_count > 0:
                    serial_number = host.get('serial-number')
                    if serial_number not in host_set:
                        host_set.add(host.get('serial-number'))
                        host_dict = {
                            "name": host.get('name'),
                            "description": host.get('durable-id'),
                            "storage_id": storage_id,
                            "native_storage_host_id":
                                host.get('serial-number'),
                            "os_type": os_type,
                            "status": status
                        }
                        host_list.append(host_dict)
            return host_list
        except Exception as e:
            LOG.error("Failed to get host "
                      "from msa storage_id: %s" % storage_id)
            raise e

    def list_storage_host_groups(self, storage_id):
        try:
            host_groups_info = self.ssh_pool.do_exec('show host-groups')
            host_group_list = []
            storage_host_grp_relation_list = []
            host_groups = self.handle_xml_to_json(
                host_groups_info, 'host-group')
            host_info_list = self.handle_xml_to_json(host_groups_info, 'host')
            for host_group in host_groups:
                member_count = int(host_group.get('member-count'))
                if member_count > 0:
                    hosts_list = []
                    storage_host_group_id = host_group.get('serial-number')
                    for host_info in host_info_list:
                        host_id = host_info.get('serial-number')
                        host_group_id = host_info.get('host-group')
                        if host_id != 'NOHOST' and \
                                host_group_id == storage_host_group_id:
                            hosts_list.append(host_id)
                            storage_host_group_relation = {
                                'storage_id': storage_id,
                                'native_storage_host_group_id':
                                    storage_host_group_id,
                                'native_storage_host_id': host_id
                            }
                            storage_host_grp_relation_list.\
                                append(storage_host_group_relation)
                    host_group_map = {
                        "name": host_group.get('name'),
                        "description": host_group.get('durable-id'),
                        "storage_id": storage_id,
                        "native_storage_host_group_id": storage_host_group_id,
                        "storage_hosts": ','.join(hosts_list)
                    }
                    host_group_list.append(host_group_map)
            storage_host_groups_result = {
                'storage_host_groups': host_group_list,
                'storage_host_grp_host_rels':
                    storage_host_grp_relation_list
            }
            return storage_host_groups_result
        except Exception as e:
            LOG.error("Failed to get host_group from msa "
                      "storage_id: %s" % storage_id)
            raise e

    def list_volume_groups(self, storage_id):
        try:
            volume_group_list = []
            volume_group_relation_list = []
            volume_groups_info = self.ssh_pool.do_exec('show volume-groups')
            volume_groups_json = self.handle_xml_to_json(
                volume_groups_info, 'volume-groups')
            volumes_json = self.handle_xml_to_json(
                volume_groups_info, 'volumes')
            for volume_group in volume_groups_json:
                volumes_list = []
                durable_id = volume_group.get('durable-id')
                if volumes_json:
                    for volume_info in volumes_json:
                        group_key = volume_info.get('group-key')
                        volume_id = volume_info.get('durable-id')
                        if group_key == durable_id:
                            volumes_list.append(volume_id)
                            volume_group_relation = {
                                'storage_id': storage_id,
                                'native_volume_group_id': durable_id,
                                'native_volume_id': volume_id
                            }
                            volume_group_relation_list.\
                                append(volume_group_relation)
                volume_groups_map = {
                    "name": volume_group.get('group-name'),
                    "description": volume_group.get('durable-id'),
                    "storage_id": storage_id,
                    "native_volume_group_id": durable_id,
                    "volumes": ','.join(volumes_list)
                }
                volume_group_list.append(volume_groups_map)
            volume_group_result = {
                'volume_groups': volume_group_list,
                'vol_grp_vol_rels': volume_group_relation_list
            }
            return volume_group_result
        except Exception as e:
            LOG.error("Failed to get volume_group"
                      " from msa storage_id: %s" % storage_id)
            raise e

    def list_port_groups(self, storage_id):
        try:
            port_group_list = []
            port_group_relation_list = []
            storage_view_info = self.ssh_pool.do_exec('show maps all ')
            storage_port_list = self.list_storage_ports(storage_id)
            storage_host_view = self.handle_xml_to_json(
                storage_view_info, 'volume-view-mappings')
            reduce_set = set()
            for storage_view in storage_host_view:
                port_number = storage_view.get('ports')
                port_group_dict = self.get_port_group_id_and_name(
                    port_number, storage_port_list)
                native_port_group_id = port_group_dict.get(
                    'native_port_group_id')
                native_port_group_name = port_group_dict.get(
                    'native_port_group_name')
                if native_port_group_name:
                    native_port_group_id = "port_group_" + \
                                           native_port_group_id
                    if native_port_group_id in reduce_set:
                        continue
                    reduce_set.add(native_port_group_id)
                    port_group_map = {
                        'name': native_port_group_id,
                        'description': native_port_group_id,
                        'storage_id': storage_id,
                        'native_port_group_id': native_port_group_id,
                        'ports': native_port_group_name
                    }
                    port_ids = native_port_group_name.split(',')
                    for port_id in port_ids:
                        port_group_relation = {
                            'storage_id': storage_id,
                            'native_port_group_id': native_port_group_id,
                            'native_port_id': port_id
                        }
                        port_group_relation_list.append(
                            port_group_relation)
                    port_group_list.append(port_group_map)
                result = {
                    'port_groups': port_group_list,
                    'port_grp_port_rels': port_group_relation_list
                }
                return result
        except Exception as e:
            LOG.error("Failed to get port_group"
                      " from msa storage_id: %s" % storage_id)
            raise e

    @staticmethod
    def get_port_group_id_and_name(port_number, storage_port_list):
        native_port_group_id = []
        native_port_group_name = []
        if port_number:
            port_codes = port_number.split(',')
            for port_code in port_codes:
                for port in storage_port_list:
                    port_name = port.get('name')
                    durable_id = port.get('native_port_id')
                    if port_code in port_name:
                        native_port_group_id.append(port_name)
                        native_port_group_name.append(durable_id)
        port_group_dict = {
            'native_port_group_id': ''.join(native_port_group_id),
            'native_port_group_name': ','.join(native_port_group_name)
        }
        return port_group_dict

    def list_masking_views(self, storage_id):
        try:
            views_list = []
            storage_view_info = self.ssh_pool.do_exec('show maps all ')
            if storage_view_info:
                storage_port_list = self.list_storage_ports(storage_id)
                host_list = self.list_storage_hosts(storage_id)
                initiators_list = self.list_storage_host_initiators(storage_id)
                host_group_list = self.list_storage_host_groups(storage_id)
                storage_host_group = host_group_list.get('storage_host_groups')
                storage_host_view = self.handle_xml_to_json(
                    storage_view_info, 'volume-view-mappings')
                views_list.extend(
                    self.get_storage_view_list(storage_host_view, 'volume',
                                               storage_id, storage_port_list,
                                               host_list, initiators_list,
                                               storage_host_group))
                storage_host_volume_groups_view = self.handle_xml_to_json(
                    storage_view_info, 'volume-group-view-mappings')
                views_list.extend(self.get_storage_view_list(
                    storage_host_volume_groups_view, 'group',
                    storage_id, storage_port_list, host_list, initiators_list,
                    storage_host_group))
            return views_list
        except Exception as e:
            LOG.error("Failed to get view "
                      "from msa storage_id: %s" % storage_id)
            raise e

    def get_storage_view_list(self, storage_view_list, vol_type, storage_id,
                              storage_port_list, host_list, initiators_list,
                              storage_host_groups):
        views_list = []
        if storage_view_list:
            native_volume_group_name = 'native_volume_group_id'\
                if vol_type == 'group' else 'native_volume_id'
            for host_view in storage_view_list:
                access = host_view.get('access')
                if access != 'not-mapped':
                    mapped_id = host_view.get('mapped-id')
                    native_masking_view_id = host_view.get('durable-id')
                    volume_id = host_view.get('parent-id')
                    port_number = host_view.get('ports')
                    view_name = host_view.get('nickname')
                    host_group_name = 'native_storage_host_group_id'\
                        if '.*.*' in view_name else 'native_storage_host_id'
                    native_port_group_dict = \
                        self.get_port_group_id_and_name(port_number,
                                                        storage_port_list)
                    native_port_group_id = native_port_group_dict.get(
                        'native_port_group_id')
                    native_storage_host_id = self.get_storage_host_id(
                        host_list, mapped_id, initiators_list,
                        storage_host_groups, view_name)
                    view_map = {
                        "name": view_name,
                        "description": view_name,
                        "storage_id": storage_id,
                        "native_masking_view_id":
                            native_masking_view_id + volume_id,
                        native_volume_group_name: volume_id,
                        host_group_name: native_storage_host_id
                    }
                    if native_port_group_id:
                        view_map['native_port_group_id'] = \
                            "port_group_" + native_port_group_id
                    views_list.append(view_map)
            return views_list

    @staticmethod
    def get_storage_host_id(host_list, mapped_id, initiators_list,
                            storage_host_groups, view_name):
        for host_value in host_list:
            host_durable_id = host_value.get('description')
            if host_durable_id == mapped_id:
                native_storage_host_id = \
                    host_value.get('native_storage_host_id')
                return native_storage_host_id

        for initiators in initiators_list:
            initiators_durable_id = initiators.get(
                'native_storage_host_initiator_id')
            if initiators_durable_id == mapped_id:
                native_storage_host_id = \
                    initiators.get('native_storage_host_id')
                return native_storage_host_id

        group_name = view_name.split('.')[0]
        for host_group in storage_host_groups:
            if group_name == host_group.get('name'):
                native_storage_host_id = \
                    host_group.get('native_storage_host_group_id')
                return native_storage_host_id
