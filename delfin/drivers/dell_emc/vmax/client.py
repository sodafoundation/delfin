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
from datetime import datetime

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
        self.array_id = None
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

        self.array_id = access_info.get('extra_attributes', {}). \
            get('array_id', None)

        try:
            # Get array details from unisphere
            array = self.rest.get_array_detail(version=self.uni_version)
            if not array:
                msg = "Failed to get array details"
                raise exception.InvalidInput(msg)

            if len(array['symmetrixId']) == EMBEDDED_UNISPHERE_ARRAY_COUNT:
                if not self.array_id:
                    self.array_id = array['symmetrixId'][0]
                elif self.array_id != array['symmetrixId'][0]:
                    msg = "Invalid array_id. Expected id: {}". \
                        format(array['symmetrixId'])
                    raise exception.InvalidInput(msg)
            else:
                # Get first local array id
                array_ids = array.get('symmetrixId', list())
                for array_id in array_ids:
                    array_info = self.rest.get_array_detail(
                        version=self.uni_version, array=array_id)
                    if array_info.get('local'):
                        LOG.info("Adding local VMAX array {}".
                                 format(array_id))
                        if not self.array_id:
                            self.array_id = array_id
                        break
                    else:
                        LOG.info("Skipping remote VMAX array {}".
                                 format(array_id))
            if not self.array_id:
                msg = "Failed to get VMAX array id from Unisphere"
                raise exception.InvalidInput(msg)
        except Exception:
            LOG.error("Failed to init_connection to VMAX")
            raise

        if not self.array_id:
            msg = "Input array_id is missing. Supported ids: {}". \
                format(array['symmetrixId'])
            raise exception.InvalidInput(msg)

    def get_array_details(self):
        try:
            # Get the VMAX array properties
            return self.rest.get_vmax_array_details(version=self.uni_version,
                                                    array=self.array_id)
        except Exception:
            LOG.error("Failed to get array details from VMAX")
            raise

    def get_storage_capacity(self):
        try:
            storage_info = self.rest.get_system_capacity(
                self.array_id, self.uni_version)

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
                subscribed_cap = system_capacity.get(
                    'subscribed_allocated_tb')
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
                self.array_id, self.uni_version, srp='')['srpId']

            pool_list = []
            for pool in pools:
                pool_info = self.rest.get_srp_by_name(
                    self.array_id, self.uni_version, srp=pool)

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
                    subscribed_cap = \
                        srp_cap['subscribed_allocated_tb'] * units.Ti

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
            LOG.error("Failed to get pool info from VMAX")
            raise

    def list_volumes(self, storage_id):

        try:
            # Get default SRPs assigned for the array
            default_srps = self.rest.get_default_srps(
                self.array_id, version=self.uni_version)
            # List all volumes except data volumes
            volumes = self.rest.get_volume_list(
                self.array_id, version=self.uni_version,
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
                vol = self.rest.get_volume(self.array_id,
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
                        self.array_id, self.uni_version, sg)
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
            directors = self.rest.get_director_list(self.array_id,
                                                    self.uni_version)
            controller_list = []
            for director in directors:
                director_info = self.rest.get_director(
                    self.array_id, self.uni_version, director)

                if director_info.get('num_of_ports') == 0:
                    continue

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
                    'cpu_info': 'number_of_cores_'
                                + str(director_info.get('num_of_cores')),
                    'memory_size': None

                }
                controller_list.append(controller)
            return controller_list

        except Exception:
            LOG.error("Failed to get controller info from VMAX")
            raise

    def list_ports(self, storage_id):
        try:
            # Get list of Directors
            directors = self.rest.get_director_list(self.array_id,
                                                    self.uni_version)
        except Exception:
            LOG.error("Failed to get director list,"
                      " while getting port info from VMAX")
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
                    self.array_id, self.uni_version, director)
                for port_key in port_keys:
                    port_info = self.rest.get_port(
                        self.array_id, self.uni_version,
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
                    if port_info.get('type', '').upper().find('GIGE') != -1:
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
                        'native_port_id': name,
                        'location': name,
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
            disks = self.rest.get_disk_list(self.array_id,
                                            self.uni_version)
            disk_list = []
            for disk in disks:
                disk_info = self.rest.get_disk(
                    self.array_id, self.uni_version, disk)

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

    def list_alerts(self, query_para):
        """Get all alerts from an array."""
        return self.rest.get_alerts(version=self.uni_version,
                                    array=self.array_id)

    def clear_alert(self, sequence_number):
        """Clear alert for given sequence number."""
        return self.rest.clear_alert(sequence_number, version=self.uni_version,
                                     array=self.array_id)

    def get_storage_metrics(self, storage_id, metrics, start_time, end_time):
        """Get performance metrics."""
        try:
            perf_list = self.rest.get_storage_metrics(
                self.array_id, metrics, start_time, end_time)

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
                self.array_id, metrics, start_time, end_time)

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
                self.rest.get_port_metrics(self.array_id,
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
                get_controller_metrics(self.array_id,
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
                self.array_id, metrics, start_time, end_time)

            metrics_array = perf_utils.construct_metrics(
                storage_id, consts.DISK_METRICS, consts.DISK_CAP, perf_list)

            return metrics_array
        except Exception:
            LOG.error("Failed to get DISK metrics for VMAX")
            raise

    def get_latest_perf_timestamp(self, context):
        """Get the latest time within 30 minutes before and
        after the current time"""
        current_time = int(datetime.now().timestamp())
        try:
            start_time = (current_time - constants.TelemetryCollection.
                          MAX_TOLERABLE_TIME_DIFF) * 1000

            end_time = (current_time + constants.TelemetryCollection.
                        MAX_TOLERABLE_TIME_DIFF) * 1000
            perf_list = self.rest.get_storage_metrics(
                self.array_id, consts.METRICS_FOR_COLLECT_TIMESTAMP,
                start_time, end_time)
            timestamp_list = []
            for perf in perf_list:
                timestamp_list.extend(
                    [collected_metrics.get('timestamp', 0)
                     for collected_metrics in perf.get('metrics', [])])
            if timestamp_list and max(timestamp_list):
                return max(timestamp_list)
            return current_time * 1000
        except Exception as e:
            LOG.error(f'Get latest performance data timestamp failed: {e}')
            return current_time * 1000
