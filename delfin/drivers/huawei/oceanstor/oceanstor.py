# Copyright 2020 The SODA Authors.
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

from oslo_log import log
from delfin.common import constants
from delfin.drivers.huawei.oceanstor import rest_client, consts, alert_handler
from delfin.drivers import driver
from delfin import exception

LOG = log.getLogger(__name__)


class OceanStorDriver(driver.StorageDriver):
    """OceanStorDriver implement Huawei OceanStor driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = rest_client.RestClient(**kwargs)
        self.sector_size = consts.SECTORS_SIZE

    def reset_connection(self, context, **kwargs):
        self.client.reset_connection(**kwargs)

    def get_storage(self, context):

        storage = self.client.get_storage()

        # Get firmware version
        controller = self.client.get_all_controllers()
        firmware_ver = controller[0]['SOFTVER']

        # Get status
        status = constants.StorageStatus.OFFLINE
        if storage['RUNNINGSTATUS'] == consts.STATUS_STORAGE_NORMAL:
            status = constants.StorageStatus.NORMAL

        # Keep sector_size for use in list pools
        self.sector_size = int(storage['SECTORSIZE'])

        total_cap = int(storage['TOTALCAPACITY']) * self.sector_size
        used_cap = int(storage['USEDCAPACITY']) * self.sector_size
        free_cap = int(storage['userFreeCapacity']) * self.sector_size
        raw_cap = int(storage['MEMBERDISKSCAPACITY']) * self.sector_size

        s = {
            'name': 'OceanStor',
            'vendor': 'Huawei',
            'description': 'Huawei OceanStor Storage',
            'model': storage['NAME'],
            'status': status,
            'serial_number': storage['ID'],
            'firmware_version': firmware_ver,
            'location': storage['LOCATION'],
            'total_capacity': total_cap,
            'used_capacity': used_cap,
            'free_capacity': free_cap,
            'raw_capacity': raw_cap
        }
        LOG.info("get_storage(), successfully retrieved storage details")
        return s

    def list_storage_pools(self, context):
        try:
            # Get list of OceanStor pool details
            pools = self.client.get_all_pools()

            pool_list = []
            for pool in pools:
                # Get pool status
                status = constants.StoragePoolStatus.OFFLINE
                if pool['RUNNINGSTATUS'] == consts.STATUS_POOL_ONLINE:
                    status = constants.StoragePoolStatus.NORMAL

                # Get pool storage_type
                storage_type = constants.StorageType.BLOCK
                if pool.get('USAGETYPE') == consts.FILE_SYSTEM_POOL_TYPE:
                    storage_type = constants.StorageType.FILE

                total_cap = \
                    int(pool['USERTOTALCAPACITY']) * self.sector_size
                used_cap = \
                    int(pool['USERCONSUMEDCAPACITY']) * self.sector_size
                free_cap = \
                    int(pool['USERFREECAPACITY']) * self.sector_size

                p = {
                    'name': pool['NAME'],
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': pool['ID'],
                    'description': 'Huawei OceanStor Pool',
                    'status': status,
                    'storage_type': storage_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from OceanStor: {}".format(err))
            raise exception.StorageBackendException(
                'Failed to get pool metrics from OceanStor')

    def _get_orig_pool_id(self, pools, volume):
        for pool in pools:
            if volume['PARENTNAME'] == pool['NAME']:
                return pool['ID']
        return ''

    def list_volumes(self, context):
        try:
            # Get all volumes in OceanStor
            volumes = self.client.get_all_volumes()
            pools = self.client.get_all_pools()

            volume_list = []
            for volume in volumes:
                # Get pool id of volume
                orig_pool_id = self._get_orig_pool_id(pools, volume)
                compressed = False
                if volume['ENABLECOMPRESSION'] != 'false':
                    compressed = True

                deduplicated = False
                if volume['ENABLEDEDUP'] != 'false':
                    deduplicated = True

                status = constants.VolumeStatus.ERROR
                if volume['RUNNINGSTATUS'] == consts.STATUS_VOLUME_READY:
                    status = constants.VolumeStatus.AVAILABLE

                vol_type = constants.VolumeType.THICK
                if volume['ALLOCTYPE'] == consts.THIN_LUNTYPE:
                    vol_type = constants.VolumeType.THIN

                sector_size = int(volume['SECTORSIZE'])
                total_cap = int(volume['CAPACITY']) * sector_size
                used_cap = int(volume['ALLOCCAPACITY']) * sector_size

                v = {
                    'name': volume['NAME'],
                    'storage_id': self.storage_id,
                    'description': 'Huawei OceanStor volume',
                    'status': status,
                    'native_volume_id': volume['ID'],
                    'native_storage_pool_id': orig_pool_id,
                    'wwn': volume['WWN'],
                    'type': vol_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': None,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                }

                volume_list.append(v)

            return volume_list

        except Exception as err:
            LOG.error(
                "Failed to get list volumes from OceanStor: {}".format(err))
            raise exception.StorageBackendException(
                'Failed to get list volumes from OceanStor')

    def list_controllers(self, context):
        try:
            # Get list of OceanStor controller details
            controllers = self.client.get_all_controllers()

            controller_list = []
            for controller in controllers:
                status = constants.ControllerStatus.NORMAL
                if controller['RUNNINGSTATUS'] == consts.STATUS_CTRLR_UNKNOWN:
                    status = constants.ControllerStatus.UNKNOWN
                if controller['RUNNINGSTATUS'] == consts.STATUS_CTRLR_OFFLINE:
                    status = constants.ControllerStatus.OFFLINE

                c = {
                    'name': controller['NAME'],
                    'storage_id': self.storage_id,
                    'native_controller_id': controller['ID'],
                    'status': status,
                    'location': controller['LOCATION'],
                    'soft_version': controller['SOFTVER'],
                    'cpu_info': controller['CPUINFO'],
                    'memory_size': controller['MEMORYSIZE'],
                }
                controller_list.append(c)

            return controller_list

        except Exception as err:
            LOG.error("Failed to get controller metrics from OceanStor: {}"
                      .format(err))
            raise exception.StorageBackendException(
                reason='Failed to get controller metrics from OceanStor')

    def list_ports(self, context):
        try:
            # Get list of OceanStor port details
            ports = self.client.get_all_ports()
            logic_type_dict = {
                consts.PORT_LOGICTYPE_HOST: constants.PortLogicalType.SERVICE,
                consts.PORT_LOGICTYPE_EXPANSION: constants.PortLogicalType.OTHER,
                consts.PORT_LOGICTYPE_MANAGEMENT: constants.PortLogicalType.MANAGEMENT,
                consts.PORT_LOGICTYPE_INTERNAL: constants.PortLogicalType.INTERNAL,
                consts.PORT_LOGICTYPE_MAINTENANCE: constants.PortLogicalType.MAINTENANCE,
                consts.PORT_LOGICTYPE_SERVICE: constants.PortLogicalType.SERVICE,
                consts.PORT_LOGICTYPE_MAINTENANCE2: constants.PortLogicalType.MAINTENANCE,
                consts.PORT_LOGICTYPE_INTERCONNECT: constants.PortLogicalType.INTERCONNECT,
            }

            port_list = []
            for port in ports:
                port_type = constants.PortType.OTHER
                health_status = constants.PortHealthStatus.ABNORMAL
                conn_status = constants.PortConnectionStatus.CONNECTED

                logical_type = logic_type_dict.get(
                    port.get('LOGICTYPE'), constants.PortLogicalType.OTHER)

                if port['HEALTHSTATUS'] == consts.PORT_HEALTH_UNKNOWN:
                    health_status = constants.PortHealthStatus.UNKNOWN
                if port['HEALTHSTATUS'] == consts.PORT_HEALTH_NORMAL:
                    health_status = constants.PortHealthStatus.UNKNOWN

                if port['RUNNINGSTATUS'] == consts.PORT_RUNNINGSTS_UNKNOWN:
                    conn_status = constants.PortConnectionStatus.UNKNOWN
                if port['RUNNINGSTATUS'] == consts.PORT_RUNNINGSTS_LINKDOWN:
                    conn_status = constants.PortConnectionStatus.DISCONNECTED

                speed = port.get('RUNSPEED')        # ether -1 or M bits/sec
                if speed != -1:
                    speed = None
                max_speed = port.get('MAXSPEED')


                # FC
                if port['TYPE'] == consts.PORT_TYPE_FC:
                    port_type = constants.PortType.FC
                    max_speed = port['MAXSUPPORTSPEED']     # in 1000 M bits/s

                # FCoE
                if port['TYPE'] == consts.PORT_TYPE_FCOE:
                    port_type = constants.PortType.FCOE

                # Ethernet
                if port['TYPE'] == consts.PORT_TYPE_ETH:
                    port_type = constants.PortType.ETH
                    max_speed = port['maxSpeed']        # in M bits/s
                    speed = port['SPEED']               # in M bits/s

                # PCIE
                if port['TYPE'] == consts.PORT_TYPE_PCIE:
                    port_type = constants.PortType.OTHER
                    speed = port['PCIESPEED']
                    logical_type = constants.PortLogicalType.OTHER

                # SAS
                if port['TYPE'] == consts.PORT_TYPE_SAS:
                    port_type = constants.PortType.SAS

                # BOND
                if port['TYPE'] == consts.PORT_TYPE_BOND:
                    port_type = constants.PortType.OTHER

                p = {
                    'name': port['NAME'],
                    'storage_id': self.storage_id,
                    'native_port_id': port['ID'],
                    'location': port.get('LOCATION'),
                    'connection_status': conn_status,
                    'health_status': health_status,
                    'type': port_type,
                    'logical_type': logical_type,
                    'speed': speed,
                    'max_speed': max_speed,
                    'native_parent_id': port.get('PARENTID'),
                    'wwn': port.get('WWN'),
                    'mac_address': port.get('MACADDRESS'),
                    'ipv4': port.get('IPV4ADDR'),
                    'ipv4_mask': port.get('IPV4MASK'),
                    'ipv6': port.get('IPV6ADDR'),
                    'ipv6_mask': port.get('IPV6MASK'),
                }
                port_list.append(p)

            return port_list

        except Exception as err:
            LOG.error(
                "Failed to get port metrics from OceanStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get port metrics from OceanStor')

    def list_disks(self, context):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, sequence_number):
        return self.client.clear_alert(sequence_number)

    def list_alerts(self, context, query_para):
        # First query alerts and then translate to model
        alert_list = self.client.list_alerts()
        alert_model_list = alert_handler.AlertHandler()\
            .parse_queried_alerts(alert_list, query_para)
        return alert_model_list
