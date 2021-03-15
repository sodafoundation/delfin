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

import six

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

        except exception.DelfinException as err:
            err_msg = "Failed to get controller metrics from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get controller metrics from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_ports(self, context):
        try:
            # Get list of OceanStor port details
            ports = self.client.get_all_ports()

            port_list = []
            for port in ports:
                health_status = constants.PortHealthStatus.ABNORMAL
                conn_status = constants.PortConnectionStatus.CONNECTED

                logical_type = consts.PortLogicTypeMap.get(
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
                if speed == '-1':
                    speed = None
                max_speed = port.get('MAXSPEED')

                port_type = consts.PortTypeMap.get(port['TYPE'],
                                                   constants.PortType.OTHER)
                # FC
                if port['TYPE'] == consts.PORT_TYPE_FC:
                    max_speed = port['MAXSUPPORTSPEED']     # in 1000 M bits/s

                # Ethernet
                if port['TYPE'] == consts.PORT_TYPE_ETH:
                    max_speed = port['maxSpeed']        # in M bits/s
                    speed = port['SPEED']               # in M bits/s

                # PCIE
                if port['TYPE'] == consts.PORT_TYPE_PCIE:
                    speed = port['PCIESPEED']
                    logical_type = constants.PortLogicalType.OTHER

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

        except exception.DelfinException as err:
            err_msg = "Failed to get port metrics from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get port metrics from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_disks(self, context):
        try:
            # Get list of OceanStor disks details
            disks = self.client.get_all_disks()

            disk_list = []
            for disk in disks:
                status = constants.DiskStatus.NORMAL
                if disk['RUNNINGSTATUS'] == consts.DISK_STATUS_OFFLINE:
                    status = constants.DiskStatus.OFFLINE
                if disk['RUNNINGSTATUS'] == consts.DISK_STATUS_UNKNOWN:
                    status = constants.DiskStatus.ABNORMAL

                physical_type = consts.DiskPhysicalTypeMap.get(
                    disk['DISKTYPE'], constants.DiskPhysicalType.UNKNOWN)

                logical_type = consts.DiskLogicalTypeMap.get(
                    disk['LOGICTYPE'], constants.DiskLogicalType.UNKNOWN)

                health_score = disk['HEALTHMARK']

                capacity = int(disk['SECTORS']) * int(disk['SECTORSIZE'])

                d = {
                    'name': disk['MODEL'] + ':' + disk['SERIALNUMBER'],
                    'storage_id': self.storage_id,
                    'native_disk_id': disk['ID'],
                    'serial_number': disk['SERIALNUMBER'],
                    'manufacturer': disk['MANUFACTURER'],
                    'model': disk['MODEL'],
                    'firmware': disk['FIRMWAREVER'],
                    'speed': int(disk['SPEEDRPM']),
                    'capacity': capacity,
                    'status': status,
                    'physical_type': physical_type,
                    'logical_type': logical_type,
                    'health_score': health_score,
                    'native_disk_group_id': None,
                    'location': disk['LOCATION'],
                }
                disk_list.append(d)

            return disk_list

        except exception.DelfinException as err:
            err_msg = "Failed to get disk metrics from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get disk metrics from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def _list_quotas(self, quotas, fs_id, qt_id):
        q_type = {
            consts.QUOTA_TYPE_TREE: constants.QuotaType.TREE,
            consts.QUOTA_TYPE_USER: constants.QuotaType.USER,
            consts.QUOTA_TYPE_GROUP: constants.QuotaType.GROUP,
        }
        q_list = []
        for qt in quotas:
            chq, csq, fhq, fsq = None, None, None, None
            uc, fc = None, None
            if qt['SPACEHARDQUOTA'] != consts.QUOTA_NOT_ENABLED:
                chq = qt['SPACEHARDQUOTA']
            if qt['SPACESOFTQUOTA'] != consts.QUOTA_NOT_ENABLED:
                csq = qt['SPACESOFTQUOTA']
            if qt['FILEHARDQUOTA'] != consts.QUOTA_NOT_ENABLED:
                fhq = qt['FILEHARDQUOTA']
            if qt['FILESOFTQUOTA'] != consts.QUOTA_NOT_ENABLED:
                fsq = qt['FILESOFTQUOTA']
            if qt['SPACEUSED'] != consts.QUOTA_NOT_ENABLED:
                uc = qt['SPACEUSED']
            if qt['FILEUSED'] != consts.QUOTA_NOT_ENABLED:
                fc = qt['FILEUSED']
            q = {
                "native_quota_id": qt['ID'],
                "type": q_type.get(qt['QUOTATYPE']),
                "storage_id": self.storage_id,
                "native_filesystem_id": fs_id,
                "native_qtree_id": qt_id,
                "capacity_hard_limit": chq,
                "capacity_soft_limit": csq,
                "file_hard_limit": fhq,
                "file_soft_limit": fsq,
                "file_count": fc,
                "used_capacity": uc,
                "user_group_name": qt['USRGRPOWNERNAME'],
            }
            q_list.append(q)
            return q_list

    def list_quotas(self, context):
        try:
            # Get list of OceanStor quotas details
            quotas_list = []
            filesystems = self.client.get_all_filesystems()
            for fs in filesystems:
                fs_id = fs["ID"]
                quotas = self.client.get_all_filesystem_quotas(fs_id)
                if quotas:
                    qs = self._list_quotas(quotas, fs_id, None)
                    quotas_list.extend(qs)

            qtrees = self.client.get_all_qtrees(filesystems)
            for qt in qtrees:
                qt_id = qt["ID"]
                quotas = self.client.get_all_qtree_quotas(qt_id)
                if quotas:
                    qs = self._list_quotas(quotas, None, qt_id)
                    quotas_list.extend(qs)

            return quotas_list

        except exception.DelfinException as err:
            err_msg = "Failed to get quotas from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get quotas from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_filesystems(self, context):
        try:
            # Get list of OceanStor filesystems details
            fss = self.client.get_all_filesystems()

            fs_list = []
            worm_type = {
                consts.FS_WORM_COMPLIANCE: constants.WORMType.COMPLIANCE,
                consts.FS_WORM_AUDIT_LOG: constants.WORMType.AUDIT_LOG,
                consts.FS_WORM_ENTERPRISE: constants.WORMType.ENTERPRISE
            }
            for fs in fss:
                status = constants.FilesystemStatus.FAULTY
                if fs['HEALTHSTATUS'] == consts.FS_HEALTH_NORMAL:
                    status = constants.FilesystemStatus.NORMAL
                fs_type = constants.FSType.THICK
                if fs['ALLOCTYPE'] == consts.FS_TYPE_THIN:
                    fs_type = constants.FSType.THIN

                pool_id = None
                if fs['PARENTTYPE'] == consts.PARENT_TYPE_POOL:
                    pool_id = fs['PARENTID']

                sector_size = int(fs['SECTORSIZE'])
                total_cap = int(fs['CAPACITY']) * sector_size
                used_cap = int(fs['ALLOCCAPACITY']) * sector_size
                free_cap = int(fs['AVAILABLECAPCITY']) * sector_size

                compressed = False
                if fs['ENABLECOMPRESSION'] != 'false':
                    compressed = True

                deduplicated = False
                if fs['ENABLEDEDUP'] != 'false':
                    deduplicated = True

                f = {
                    'name': fs['NAME'],
                    'storage_id': self.storage_id,
                    'native_filesystem_id': fs['ID'],
                    'native_pool_id': pool_id,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                    'worm': worm_type.get(fs['WORMTYPE'],
                                          constants.WORMType.NON_WORM),
                    'status': status,
                    'type': fs_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                }
                fs_list.append(f)

            return fs_list

        except exception.DelfinException as err:
            err_msg = "Failed to get filesystems from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get filesystems from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_qtrees(self, context):
        try:
            # Get list of OceanStor qtrees details
            filesystems = self.client.get_all_filesystems()
            qts = self.client.get_all_qtrees(filesystems)
            security_mode = {
                consts.SECURITY_STYLE_MIXED: constants.NASSecurityMode.MIXED,
                consts.SECURITY_STYLE_NATIVE: constants.NASSecurityMode.NATIVE,
                consts.SECURITY_STYLE_NTFS: constants.NASSecurityMode.NTFS,
                consts.SECURITY_STYLE_UNIX: constants.NASSecurityMode.UNIX,
            }

            qt_list = []
            for qt in qts:
                fs_id = None
                if qt['PARENTTYPE'] == consts.PARENT_OBJECT_TYPE_FS:
                    fs_id = qt['PARENTID']
                q = {
                    'name': qt['NAME'],
                    'storage_id': self.storage_id,
                    'native_qtree_id': qt['ID'],
                    'native_filesystem_id': fs_id,
                    'security_mode': security_mode.get(qt['securityStyle']),
                }
                qt_list.append(q)

            return qt_list

        except exception.DelfinException as err:
            err_msg = "Failed to get qtrees from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get qtrees from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def list_shares(self, context):
        try:
            # Get list of OceanStor shares details
            ss = self.client.get_all_shares()

            s_list = []
            for s in ss:

                protocol = None
                if s.get('type') == consts.SHARE_NFS:
                    protocol = constants.ShareProtocol.NFS
                if s.get('subType'):
                    protocol = constants.ShareProtocol.CIFS
                if s.get('ACCESSNAME'):
                    protocol = constants.ShareProtocol.FTP

                s = {
                    'name': s['NAME'],
                    'storage_id': self.storage_id,
                    'native_share_id': s['ID'],
                    'native_filesystem_id': s['FSID'],
                    'path': s['SHAREPATH'],
                    'protocol': protocol
                }
                s_list.append(s)

            return s_list

        except exception.DelfinException as err:
            err_msg = "Failed to get shares from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise err

        except Exception as err:
            err_msg = "Failed to get shares from OceanStor: %s" %\
                      (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, sequence_number):
        return self.client.clear_alert(sequence_number)

    def list_alerts(self, context, query_para):
        # First query alerts and then translate to model
        alert_list = self.client.list_alerts()
        alert_model_list = alert_handler.AlertHandler()\
            .parse_queried_alerts(alert_list, query_para)
        return alert_model_list
