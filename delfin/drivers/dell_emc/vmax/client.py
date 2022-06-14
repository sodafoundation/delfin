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
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.dell_emc.vmax import constants as consts
from delfin.drivers.dell_emc.vmax import rest, perf_utils

LOG = log.getLogger(__name__)

EMBEDDED_UNISPHERE_ARRAY_COUNT = 1


class VMAXClient(object):
    """ Client class for communicating with VMAX storage """

    def __init__(self, **kwargs):
        self.uni_version = None
        self.array_id = {}
        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        self.rest = rest.VMaxRest()
        self.rest.set_rest_credentials(rest_access)
        self.reset_connection(**kwargs)

    def reset_connection(self, **kwargs):
        """ Reset connection to VMAX storage with new configs """
        self.rest.verify = kwargs.get('verify', False)
        self.rest.establish_rest_session()

    def init_connection(self, access_info):
        """ Given the access_info get a connection to VMAX storage """
        try:
            ver, self.uni_version = self.rest.get_uni_version()
            LOG.info('Connected to Unisphere Version: {0}'.format(ver))
        except exception.InvalidUsernameOrPassword as e:
            msg = "Failed to connect VMAX. Reason: {}".format(e.msg)
            LOG.error(msg)
            raise e
        except (exception.SSLCertificateFailed,
                exception.SSLHandshakeFailed) as e:
            msg = ("Failed to connect to VMAX: {}".format(e))
            LOG.error(msg)
            raise
        except Exception as err:
            msg = ("Failed to connect to VMAX. Host or Port is not correct: "
                   "{}".format(err))
            LOG.error(msg)
            raise exception.InvalidIpOrPort()

        if not self.uni_version:
            msg = "Invalid input. Failed to get vmax unisphere version"
            raise exception.InvalidInput(msg)

    def add_storage(self, access_info):
        storage_name = access_info.get('storage_name')

        try:
            # Get array details from unisphere
            array = self.rest.get_array_detail(version=self.uni_version)
            if not array:
                msg = "Failed to get array details"
                raise exception.InvalidInput(msg)

            if len(array['symmetrixId']) == EMBEDDED_UNISPHERE_ARRAY_COUNT:
                if not storage_name:
                    storage_name = array['symmetrixId'][0]
                elif storage_name != array['symmetrixId'][0]:
                    msg = "Invalid storage_name. Expected: {}". \
                        format(array['symmetrixId'])
                    raise exception.InvalidInput(msg)
            else:
                if not storage_name:
                    msg = "Input storage_name is missing. Supported ids: {}". \
                        format(array['symmetrixId'])
                    raise exception.InvalidInput(msg)

                array_ids = array.get('symmetrixId', list())
                if storage_name not in array_ids:
                    msg = "Failed to get VMAX array id from Unisphere"
                    raise exception.InvalidInput(msg)

            self.array_id[access_info['storage_id']] = storage_name

        except Exception:
            LOG.error("Failed to add storage from VMAX")
            raise

    def get_array_details(self, storage_id):
        try:
            array_id = self.array_id.get(storage_id)
            # Get the VMAX array properties
            return self.rest.get_vmax_array_details(version=self.uni_version,
                                                    array=array_id)
        except Exception:
            LOG.error("Failed to get array details from VMAX")
            raise

    def get_storage_capacity(self, storage_id):
        try:
            storage_info = self.rest.get_system_capacity(
                self.array_id[storage_id], self.uni_version)

            total_capacity = 0
            used_capacity = 0
            free_capacity = 0
            raw_capacity = 0
            subscribed_capacity = 0
            if int(self.uni_version) < 90:
                physical_capacity = storage_info.get('physicalCapacity')
                total_cap = storage_info.get('total_usable_cap_gb')
                used_cap = storage_info.get('total_allocated_cap_gb')
                subscribed_cap = storage_info.get('total_subscribed_cap_gb')
                total_raw = physical_capacity.get('total_capacity_gb')
                free_cap = total_cap - used_cap

                total_capacity = int(total_cap * units.Gi)
                used_capacity = int(used_cap * units.Gi)
                free_capacity = int(free_cap * units.Gi)
                raw_capacity = int(total_raw * units.Gi)
                subscribed_capacity = int(subscribed_cap * units.Gi)

            else:
                system_capacity = storage_info['system_capacity']
                physical_capacity = storage_info.get('physicalCapacity')
                total_cap = system_capacity.get('usable_total_tb')
                used_cap = system_capacity.get('usable_used_tb')
                subscribed_cap = system_capacity.get('subscribed_total_tb')
                total_raw = physical_capacity.get('total_capacity_gb')
                free_cap = total_cap - used_cap

                total_capacity = int(total_cap * units.Ti)
                used_capacity = int(used_cap * units.Ti)
                free_capacity = int(free_cap * units.Ti)
                raw_capacity = int(total_raw * units.Gi)
                subscribed_capacity = int(subscribed_cap * units.Ti)

            return total_capacity, used_capacity, free_capacity,\
                raw_capacity, subscribed_capacity

        except Exception:
            LOG.error("Failed to get capacity from VMAX")
            raise

    def list_storage_pools(self, storage_id):
        try:
            # Get list of SRP pool names
            pools = self.rest.get_srp_by_name(
                self.array_id[storage_id],
                self.uni_version, srp='')['srpId']

            pool_list = []
            for pool in pools:
                pool_info = self.rest.get_srp_by_name(
                    self.array_id[storage_id],
                    self.uni_version, srp=pool)

                total_cap = 0
                used_cap = 0
                subscribed_cap = 0
                if int(self.uni_version) < 90:
                    total_cap = pool_info['total_usable_cap_gb'] * units.Gi
                    used_cap = pool_info['total_allocated_cap_gb'] * units.Gi
                    subscribed_cap = \
                        pool_info['total_subscribed_cap_gb'] * units.Gi
                else:
                    srp_cap = pool_info['srp_capacity']
                    total_cap = srp_cap['usable_total_tb'] * units.Ti
                    used_cap = srp_cap['usable_used_tb'] * units.Ti
                    subscribed_cap = srp_cap['subscribed_total_tb'] * units.Ti

                p = {
                    "name": pool,
                    "storage_id": storage_id,
                    "native_storage_pool_id": pool_info["srpId"],
                    "description": "Dell EMC VMAX Pool",
                    "status": constants.StoragePoolStatus.NORMAL,
                    "storage_type": constants.StorageType.BLOCK,
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(total_cap - used_cap),
                    "subscribed_capacity": int(subscribed_cap),
                }

                pool_list.append(p)

            return pool_list

        except Exception:
            LOG.error("Failed to get pool metrics from VMAX")
            raise

    def list_volumes(self, storage_id):

        try:
            # Get default SRPs assigned for the array
            default_srps = self.rest.get_default_srps(
                self.array_id[storage_id], version=self.uni_version)
            # List all volumes except data volumes
            volumes = self.rest.get_volume_list(
                self.array_id[storage_id], version=self.uni_version,
                params={'data_volume': 'false'})

            # TODO: Update constants.VolumeStatus to make mapping more precise
            switcher = {
                'Ready': constants.VolumeStatus.AVAILABLE,
                'Not Ready': constants.VolumeStatus.AVAILABLE,
                'Mixed': constants.VolumeStatus.AVAILABLE,
                'Write Disabled': constants.VolumeStatus.AVAILABLE,
                'N/A': constants.VolumeStatus.ERROR,
            }

            volume_list = []
            for volume in volumes:
                # Get volume details
                vol = self.rest.get_volume(self.array_id[storage_id],
                                           self.uni_version, volume)

                emulation_type = vol['emulation']
                total_cap = vol['cap_mb'] * units.Mi
                used_cap = (total_cap * vol['allocated_percent']) / 100.0
                free_cap = total_cap - used_cap

                status = switcher.get(vol.get('status'),
                                      constants.VolumeStatus.AVAILABLE)

                description = "Dell EMC VMAX volume"
                if vol['type'] == 'TDEV':
                    description = "Dell EMC VMAX 'thin device' volume"

                name = volume
                if vol.get('volume_identifier'):
                    name = volume + ':' + vol['volume_identifier']

                v = {
                    "name": name,
                    "storage_id": storage_id,
                    "description": description,
                    "status": status,
                    "native_volume_id": vol['volumeId'],
                    "wwn": vol['wwn'],
                    "type": constants.VolumeType.THIN,
                    "total_capacity": int(total_cap),
                    "used_capacity": int(used_cap),
                    "free_capacity": int(free_cap),
                }

                if vol['num_of_storage_groups'] == 1:
                    sg = vol['storageGroupId'][0]
                    sg_info = self.rest.get_storage_group(
                        self.array_id[storage_id], self.uni_version, sg)
                    v['native_storage_pool_id'] = \
                        sg_info.get('srp', default_srps[emulation_type])
                    v['compressed'] = sg_info.get('compression', False)
                else:
                    v['native_storage_pool_id'] = default_srps[emulation_type]

                volume_list.append(v)

            return volume_list

        except Exception:
            LOG.error("Failed to get list volumes from VMAX")
            raise

    def list_controllers(self, storage_id):
        try:
            # Get list of Directors
            directors = self.rest.get_director_list(self.array_id[storage_id],
                                                    self.uni_version)
            controller_list = []
            for director in directors:
                director_info = self.rest.get_director(
                    self.array_id[storage_id], self.uni_version, director)

                status = constants.ControllerStatus.NORMAL
                if "OFF" in director_info.get('availability', '').upper():
                    status = constants.ControllerStatus.OFFLINE

                controller = {
                    'name': director_info['directorId'],
                    'storage_id': storage_id,
                    'native_controller_id': director_info['directorId'],
                    'status': status,
                    'location':
                        'slot_' +
                        str(director_info.get('director_slot_number')),
                    'soft_version': None,
                    'cpu_info': 'Cores-'
                                + str(director_info.get('num_of_cores')),
                    'memory_size': None

                }
                controller_list.append(controller)
            return controller_list

        except Exception:
            LOG.error("Failed to get controller metrics from VMAX")
            raise

    def list_ports(self, storage_id):
        try:
            # Get list of Directors
            directors = self.rest.get_director_list(self.array_id[storage_id],
                                                    self.uni_version)
        except Exception:
            LOG.error("Failed to get director list,"
                      " while getting port metrics from VMAX")
            raise
        switcher = {
            'A': constants.PortLogicalType.MANAGEMENT,
            'B': constants.PortLogicalType.SERVICE,
            'C': constants.PortLogicalType.BACKEND,
        }
        port_list = []
        for director in directors:
            try:
                port_keys = self.rest.get_port_list(
                    self.array_id[storage_id], self.uni_version, director)
                for port_key in port_keys:
                    port_info = self.rest.get_port(
                        self.array_id[storage_id], self.uni_version,
                        director, port_key['portId'])['symmetrixPort']

                    connection_status = \
                        constants.PortConnectionStatus.CONNECTED
                    if port_info.get('port_status',
                                     '').upper().find('OFF') != -1:
                        connection_status = \
                            constants.PortConnectionStatus.DISCONNECTED

                    port_type = constants.PortType.OTHER
                    if port_info.get('type', '').upper().find('FIBRE') != -1:
                        port_type = constants.PortType.FC
                    if port_info.get('type', '').upper().find('ETH') != -1:
                        port_type = constants.PortType.ETH

                    name = "{0}:{1}".format(port_key['directorId'],
                                            port_key['portId'])

                    director_emulation = port_key['directorId'][4]
                    logical_type = switcher.get(
                        director_emulation, constants.PortLogicalType.OTHER)
                    if logical_type == constants.PortLogicalType.OTHER:
                        port_prefix = port_key['directorId'][:2]
                        if port_prefix in ['FA', 'FE', 'EA', 'EF', 'SE']:
                            logical_type = constants.PortLogicalType.FRONTEND
                        if port_prefix in ['DA', 'DF', 'DX']:
                            logical_type = constants.PortLogicalType.BACKEND

                    speed = int(port_info.get('negotiated_speed',
                                              '0')) * units.Gi
                    max_speed = int(port_info.get('max_speed',
                                                  '0')) * units.Gi
                    port_dict = {
                        'name': name,
                        'storage_id': storage_id,
                        'native_port_id': port_key['portId'],
                        'location': 'director_' + port_key['directorId'],
                        'connection_status': connection_status,
                        'health_status': constants.PortHealthStatus.NORMAL,
                        'type': port_type,
                        'logical_type': logical_type,
                        'speed': speed,
                        'max_speed': max_speed,
                        'native_parent_id': port_key['directorId'],
                        'wwn': port_info.get('identifier', None),
                        'mac_address': None,
                        'ipv4': port_info.get('ipv4_address'),
                        'ipv4_mask': port_info.get('ipv4_netmask'),
                        'ipv6': port_info.get('ipv6_address'),
                        'ipv6_mask': None,
                    }
                    port_list.append(port_dict)

            except Exception:
                LOG.error("Failed to get port list for director: {}"
                          .format(director))

            return port_list

    def list_disks(self, storage_id):
        if int(self.uni_version) < 91:
            return []
        try:
            # Get list of Disks
            disks = self.rest.get_disk_list(self.array_id[storage_id],
                                            self.uni_version)
            disk_list = []
            for disk in disks:
                disk_info = self.rest.get_disk(
                    self.array_id[storage_id], self.uni_version, disk)

                disk_item = {
                    'name': disk,
                    'storage_id': storage_id,
                    'native_disk_id': disk,
                    'manufacturer': disk_info['vendor'],
                    'capacity': int(disk_info['capacity']) * units.Gi,
                }
                disk_list.append(disk_item)
            return disk_list

        except Exception:
            LOG.error("Failed to get disk details from VMAX")
            raise

    def list_storage_host_initiators(self, storage_id):
        try:
            # Get list of initiators
            initiators = self.rest.get_initiator_list(
                self.array_id[storage_id], self.uni_version)

            initiator_list = []
            for initiator in initiators:
                initiator_info = self.rest.get_initiator(
                    self.array_id[storage_id], self.uni_version, initiator)
                type_string = initiator_info.get('type', '').upper()
                initiator_type = constants.InitiatorType.UNKNOWN
                if 'FIBRE' in type_string:
                    initiator_type = constants.InitiatorType.FC
                if 'ISCSI' in type_string:
                    initiator_type = constants.InitiatorType.ISCSI

                initiator_status = constants.InitiatorStatus.ONLINE
                if not initiator_info.get('on_fabric', False):
                    initiator_status = constants.InitiatorStatus.OFFLINE

                initiator_item = {
                    'name': initiator,
                    'storage_id': storage_id,
                    'native_storage_host_initiator_id': initiator,
                    'alias': initiator_info.get('alias'),
                    'wwn': initiator_info.get('initiatorId'),
                    'type': initiator_type,
                    'status': initiator_status,
                    'native_storage_host_id': initiator_info.get('host'),
                }
                initiator_list.append(initiator_item)
            return initiator_list

        except Exception:
            LOG.error("Failed to get host initiator details from VMAX")
            raise

    def list_storage_hosts(self, storage_id):
        try:
            # Get list of storage hosts
            hosts = self.rest.get_host_list(self.array_id[storage_id],
                                            self.uni_version)
            host_list = []
            for host in hosts:
                host_info = self.rest.get_host(
                    self.array_id[storage_id], self.uni_version, host)

                host_item = {
                    'storage_id': storage_id,
                    'native_storage_host_id': host_info.get('hostId'),
                    'name': host_info.get('hostId'),
                    'os_type': constants.HostOSTypes.UNKNOWN,
                    'status': constants.HostStatus.NORMAL,
                }
                host_list.append(host_item)
            return host_list

        except Exception:
            LOG.error("Failed to get storage host details from VMAX")
            raise

    def list_storage_host_groups(self, storage_id):
        try:
            # Get list of storage host groups
            host_groups = self.rest.get_host_group_list(
                self.array_id[storage_id], self.uni_version)
            host_group_list = []
            storage_host_grp_relation_list = []
            for host_group in host_groups:
                host_group_info = self.rest.get_host_group(
                    self.array_id[storage_id], self.uni_version, host_group)
                host_group_item = {
                    'name': host_group,
                    'storage_id': storage_id,
                    'native_storage_host_group_id': host_group,
                }
                host_group_list.append(host_group_item)

                for storage_host in host_group_info['host']:
                    storage_host_group_relation = {
                        'storage_id': storage_id,
                        'native_storage_host_group_id': host_group,
                        'native_storage_host_id': storage_host.get('hostId')
                    }
                    storage_host_grp_relation_list \
                        .append(storage_host_group_relation)

            result = {
                'storage_host_groups': host_group_list,
                'storage_host_grp_host_rels': storage_host_grp_relation_list
            }

            return result

        except Exception:
            LOG.error("Failed to get storage host group details from VMAX")
            raise

    def list_port_groups(self, storage_id):
        try:
            # Get list of port groups
            port_groups = self.rest.get_port_group_list(
                self.array_id[storage_id], self.uni_version)
            port_group_list = []
            port_group_relation_list = []
            for port_group in port_groups:
                port_group_info = self.rest.get_port_group(
                    self.array_id[storage_id], self.uni_version, port_group)
                port_group_item = {
                    'name': port_group,
                    'storage_id': storage_id,
                    'native_port_group_id': port_group,
                }
                port_group_list.append(port_group_item)

                for port in port_group_info['symmetrixPortKey']:
                    port_name = port['directorId'] + ':' + port['portId']
                    port_group_relation = {
                        'storage_id': storage_id,
                        'native_port_group_id': port_group,
                        'native_port_id': port_name
                    }
                    port_group_relation_list.append(port_group_relation)
            result = {
                'port_groups': port_group_list,
                'port_grp_port_rels': port_group_relation_list
            }
            return result

        except Exception:
            LOG.error("Failed to get port group details from VMAX")
            raise

    def list_volume_groups(self, storage_id):
        try:
            # Get list of volume groups
            volume_groups = self.rest.get_volume_group_list(
                self.array_id[storage_id], self.uni_version)
            volume_group_list = []
            volume_group_relation_list = []
            for volume_group in volume_groups:
                # volume_group_info = self.rest.get_volume_group(
                #     self.array_id, self.uni_version, volume_group)

                volume_group_item = {
                    'name': volume_group,
                    'storage_id': storage_id,
                    'native_volume_group_id': volume_group,
                }
                volume_group_list.append(volume_group_item)

                # List all volumes except data volumes
                volumes = self.rest.get_volume_list(
                    self.array_id[storage_id], version=self.uni_version,
                    params={'data_volume': 'false',
                            'storageGroupId': volume_group})
                if not volumes:
                    continue
                for volume in volumes:
                    volume_group_relation = {
                        'storage_id': storage_id,
                        'native_volume_group_id': volume_group,
                        'native_volume_id': volume
                    }
                    volume_group_relation_list.append(volume_group_relation)

            result = {
                'volume_groups': volume_group_list,
                'vol_grp_vol_rels': volume_group_relation_list
            }
            return result

        except Exception:
            LOG.error("Failed to get volume group details from VMAX")
            raise

    def list_masking_views(self, storage_id):
        try:
            # Get list of masking_views
            masking_views = self.rest.get_masking_view_list(
                self.array_id[storage_id], self.uni_version)
            masking_view_list = []
            for masking_view in masking_views:
                mv_info = self.rest.get_masking_view(
                    self.array_id[storage_id], self.uni_version, masking_view)

                masking_view_item = {
                    'name': masking_view,
                    'storage_id': storage_id,
                    'native_masking_view_id': mv_info['maskingViewId'],
                    'native_storage_host_id': mv_info.get('hostId'),
                    'native_storage_host_group_id': mv_info.get(
                        'hostGroupId'),
                    'native_volume_group_id': mv_info.get('storageGroupId'),
                    'native_port_group_id': mv_info.get('portGroupId'),
                }
                masking_view_list.append(masking_view_item)
            return masking_view_list

        except Exception:
            LOG.error("Failed to get masking views details from VMAX")
            raise

    def list_alerts(self, storage_id, query_para):
        """Get all alerts from an array."""
        return self.rest.get_alerts(query_para, version=self.uni_version,
                                    array=self.array_id[storage_id])

    def clear_alert(self, storage_id, sequence_number):
        """Clear alert for given sequence number."""
        return self.rest.clear_alert(sequence_number,
                                     version=self.uni_version,
                                     array=self.array_id[storage_id])

    def get_storage_metrics(self, storage_id, metrics, start_time, end_time):
        """Get performance metrics."""
        try:
            perf_list = self.rest.get_storage_metrics(
                self.array_id[storage_id], metrics, start_time, end_time)

            return perf_utils.construct_metrics(storage_id,
                                                consts.STORAGE_METRICS,
                                                consts.STORAGE_CAP,
                                                perf_list)
        except Exception:
            LOG.error("Failed to get STORAGE metrics for VMAX")
            raise

    def get_pool_metrics(self, storage_id, metrics, start_time, end_time):
        """Get performance metrics."""
        try:
            perf_list = self.rest.get_pool_metrics(
                self.array_id[storage_id], metrics, start_time, end_time)

            metrics_array = perf_utils.construct_metrics(
                storage_id, consts.POOL_METRICS, consts.POOL_CAP, perf_list)

            return metrics_array
        except Exception:
            LOG.error("Failed to get STORAGE POOL metrics for VMAX")
            raise

    def get_port_metrics(self, storage_id, metrics, start_time, end_time):
        """Get performance metrics."""
        try:
            be_perf_list, fe_perf_list, rdf_perf_list = \
                self.rest.get_port_metrics(self.array_id[storage_id],
                                           metrics, start_time, end_time)

            metrics_array = []
            metrics_list = perf_utils.construct_metrics(
                storage_id, consts.BEPORT_METRICS,
                consts.PORT_CAP, be_perf_list)
            metrics_array.extend(metrics_list)

            metrics_list = perf_utils.construct_metrics(
                storage_id, consts.FEPORT_METRICS,
                consts.PORT_CAP, fe_perf_list)
            metrics_array.extend(metrics_list)

            metrics_list = perf_utils.construct_metrics(
                storage_id, consts.RDFPORT_METRICS,
                consts.PORT_CAP, rdf_perf_list)
            metrics_array.extend(metrics_list)
            return metrics_array
        except Exception:
            LOG.error("Failed to get PORT metrics for VMAX")
            raise

    def get_controller_metrics(self, storage_id,
                               metrics, start_time, end_time):
        """Get performance metrics."""
        try:
            be_perf_list, fe_perf_list, rdf_perf_list = self.rest.\
                get_controller_metrics(self.array_id[storage_id],
                                       metrics, start_time, end_time)

            metrics_array = []
            metrics_list = perf_utils.construct_metrics(
                storage_id, consts.BEDIRECTOR_METRICS,
                consts.CONTROLLER_CAP, be_perf_list)
            metrics_array.extend(metrics_list)

            metrics_list = perf_utils.construct_metrics(
                storage_id, consts.FEDIRECTOR_METRICS,
                consts.CONTROLLER_CAP, fe_perf_list)
            metrics_array.extend(metrics_list)

            metrics_list = perf_utils.construct_metrics(
                storage_id, consts.RDFDIRECTOR_METRICS,
                consts.CONTROLLER_CAP, rdf_perf_list)
            metrics_array.extend(metrics_list)

            return metrics_array
        except Exception:
            LOG.error("Failed to get CONTROLLER metrics for VMAX")
            raise

    def get_disk_metrics(self, storage_id, metrics, start_time, end_time):
        """Get disk performance metrics."""
        if int(self.uni_version) < 91:
            return []

        try:
            perf_list = self.rest.get_disk_metrics(
                self.array_id[storage_id], metrics, start_time, end_time)

            metrics_array = perf_utils.construct_metrics(
                storage_id, consts.DISK_METRICS, consts.DISK_CAP, perf_list)

            return metrics_array
        except Exception:
            LOG.error("Failed to get DISK metrics for VMAX")
            raise
