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
import abc


@six.add_metaclass(abc.ABCMeta)
class StorageDriver(object):

    def __init__(self, **kwargs):
        """
        :param kwargs:  A dictionary, include access information. Pay
            attention that it's not safe to save username and password
            in memory, so suggest each driver use them to get session
            instead of save them in memory directly.
        """
        self.storage_id = kwargs.get('storage_id', None)

    def delete_storage(self, context):
        """Cleanup storage device information from driver"""
        pass

    def add_storage(self, kwargs):
        """Add storage device information to driver"""
        pass

    @abc.abstractmethod
    def reset_connection(self, context, **kwargs):
        """ Reset connection with backend with new args """
        pass

    @abc.abstractmethod
    def get_storage(self, context):
        """Get storage device information from storage system"""
        pass

    @abc.abstractmethod
    def list_storage_pools(self, context):
        """List all storage pools from storage system."""
        pass

    @abc.abstractmethod
    def list_volumes(self, context):
        """List all storage volumes from storage system."""
        pass

    def list_controllers(self, context):
        """List all storage controllers from storage system."""
        raise NotImplementedError(
            "Driver API list_controllers() is not Implemented")

    def list_ports(self, context):
        """List all ports from storage system."""
        raise NotImplementedError(
            "Driver API list_ports() is not Implemented")

    def list_disks(self, context):
        """List all disks from storage system."""
        raise NotImplementedError(
            "Driver API list_disks() is not Implemented")

    @abc.abstractmethod
    def add_trap_config(self, context, trap_config):
        """Config the trap receiver in storage system."""
        pass

    @abc.abstractmethod
    def remove_trap_config(self, context, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    @staticmethod
    def parse_alert(context, alert):
        """Parse alert data got from snmp trap server."""

        """
        Alert Model	Description
        *****Filled from driver side ***********************
        alert_id	Unique identification for a given alert type
        alert_name	Unique name for a given alert type
        severity	Severity of the alert
        category	Category of alert generated
        type	Type of the alert generated
        sequence_number	Sequence number for the alert, uniquely identifies a
                                  given alert instance used for
                                  clearing the alert
        occur_time	Time at which alert is generated from device in epoch
                    format
        description	Possible cause description or other details about
                                the alert
        recovery_advice	Some suggestion for handling the given alert
        resource_type	Resource type of device/source generating alert
        location	Detailed info about the tracing the alerting device such as
                    slot, rack, component, parts etc
        *****************************************************
        """

        pass

    @abc.abstractmethod
    def list_alerts(self, context, query_para=None):
        """List all current alerts from storage system."""
        """
        query_para is an optional para which contains 'begin_time' and
        'end_time' (in milliseconds) which is to be used to filter
        alerts at driver
        """
        pass

    @abc.abstractmethod
    def clear_alert(self, context, sequence_number):
        """Clear alert from storage system."""
        pass

    def collect_perf_metrics(self, context, storage_id,
                             resource_metrics, start_time, end_time):
        """Collect performance metrics from storage system."""

        """
        Input:
        context: context information
        storage_id: storage identifier
        resource_metrics: dictionary represents the collection configuration
        Example:
        resource_metrics =
              {'storagePool':
                        ['readThroughput', 'writeThroughput', 'responseTime'],
                'volume':
                        ['readThroughput', 'writeThroughput']}
        start_time	Time from which the performance metric to be collected
                    It is in epoch format in milliseconds
        end_time	Time until which the performance metric to be collected
                    It is in epoch format in milliseconds

        Response: List of metric with details
                Format : [[Metric(name=metric_1,
                             labels={'key_1': value_1,
                                     'key_2': value_2,},
                             values={timestamp_0: value_0,
                                     timestamp_n: value_n,})]
        Example:
        [[Metric(name='responseTime',
                     labels={'storage_id': '1f8d6982-2ac2-4fa9-95ef-78f359de',
                             'resource_type': 'storagePool'},
                     values={1616560337249: 96.12081735538251}),
          Metric(name='throughput',
                     labels={'storage_id': '1f8d6982-2ac2-4fa9-95ef-78f359de',
                             'resource_type': 'storagePool'},
                     values={1616560337249: 90.08194398331271})]
        """
        pass

    def list_quotas(self, context):
        """List all quotas from storage system."""
        raise NotImplementedError(
            "Driver API list_quotas() is not Implemented")

    def list_filesystems(self, context):
        """List all filesystems from storage system."""
        raise NotImplementedError(
            "Driver API list_filesystems() is not Implemented")

    def list_qtrees(self, context):
        """List all qtrees from storage system."""
        raise NotImplementedError(
            "Driver API list_qtrees() is not Implemented")

    def list_shares(self, context):
        """List all shares from storage system."""
        raise NotImplementedError(
            "Driver API list_shares() is not Implemented")

    @staticmethod
    def get_capabilities(context, filters=None):
        """Get capability of driver:
        is_historic (bool): required
        performance_metric_retention_window (int): optional, default is None
        collect_interval (int): optional, default is
            TelemetryCollection.DEF_PERFORMANCE_COLLECTION_INTERVAL
            in common/constants.py
        failed_job_collect_interval (int): optional, default is
            TelemetryCollection.FAILED_JOB_SCHEDULE_INTERVAL
            in common/constants.py
        resource_metrics (dict): required, please refer to
            STORAGE_CAPABILITIES_SCHEMA
            in api/schemas/storage_capabilities_schema.py.

        For example:
        {
            'is_historic': True,
            'performance_metric_retention_window': 4500,
            'collect_interval': 900
            'failed_job_collect_interval': 900,
            'resource_metrics': {
                'storage': {
                    'iops': {
                        'unit': 'IOPS',
                        'description': 'Read/write operations per second'
                    },
                    ...
                },
                ...
            }
        }
        """
        pass

    def list_storage_host_initiators(self, context):
        """List all storage initiators from storage system."""
        """
        *********Model description**********
        native_storage_host_initiator_id: Native id at backend side(mandatory)
        native_storage_host_id: Native id of host at backend side if associated
        name: Name of the initiator
        description: Description of the initiator
        alias: Alias of the initiator
        type: initiator type (fc, iscsi, nvme_over_roce)
        status: Health status(normal, offline, abnormal, unknown)
        wwn: Worldwide name
        storage_id: Storage id at delfin side
        """
        raise NotImplementedError(
            "Driver API list_storage_host_initiators() is not Implemented")

    def list_storage_hosts(self, context):
        """List all storage hosts from storage system."""
        """
        *********Model description**********
        native_storage_host_id: Native id of host at backend side(mandatory)
        name: Name of the host
        description: Description of the host
        os_type: operating system type
        status: Health status(normal, offline, abnormal, unknown)
        ip_address: Ip address of the host
        storage_id: Storage id at delfin side
        """
        raise NotImplementedError(
            "Driver API list_storage_hosts() is not Implemented")

    def list_storage_host_groups(self, context):
        """
        Returns a dict with following
        'storage_host_groups': <List storage host groups from storage system>,
        'storage_host_grp_host_rels': <List host groups to host relation>,
        """
        """
        ********* storage_host_groups Model description**********
        native_storage_host_group_id: Native id of host grp at backend side
                                      (mandatory)
        name: Name of the host grp
        description: Description of the host grp
        storage_hosts: List of associated hosts if any(, separated list)
        storage_id: Storage id at delfin side
        """
        raise NotImplementedError(
            "Driver API list_storage_host_groups() is not Implemented")

    def list_port_groups(self, context):
        """
        Returns a dict with following
        'port_groups': <List port groups from storage system>,
        'port_grp_port_rels': <List port groups to port relation>,
        """
        """
        ********* port_groups Model description**********
        native_port_group_id: Native id of port grp at backend side (mandatory)
        name: Name of the port grp
        description: Description of the port grp
        ports: List of associated ports if any(, separated list)
        storage_id: Storage id at delfin side
        """
        raise NotImplementedError(
            "Driver API list_port_groups() is not Implemented")

    def list_volume_groups(self, context):
        """
        Returns a dict with following
        'volume_groups': <List volume groups from storage system>,
        'vol_grp_vol_rels': <List volume groups to port relation>,
        """
        """
        ********* volume_groups Model description**********
        native_volume_group_id: Native id of volume grp at backend side
                                (mandatory)
        name: Name of the volume grp
        description: Description of the volume grp
        volumes: List of associated volumes if any(, separated list)
        storage_id: Storage id at delfin side
        """
        raise NotImplementedError(
            "Driver API list_volume_groups() is not Implemented")

    def list_masking_views(self, context):
        """List all masking views from storage system."""
        """
        *********Model description**********
        native_masking_view_id: Native id of volume grp at backend side
                                (mandatory)
        name: Name of the masking view
        description: Description of the masking view
        native_storage_host_group_id: Native id of host grp at backend side
        native_port_group_id: Native id of port grp at backend side
        native_volume_group_id: Native id of volume grp at backend side
        native_storage_host_id: Native id of host at backend side
        native_volume_id: Native id of volume at backend side
        storage_id: Storage id at delfin side

        Masking view filling guidelines:
        Driver can have different backend scenarios such as
         - Direct host -> direct volume mapping
         - Direct host -> direct volume -> direct port mapping
         - Direct host -> volume group mapping
         - Host grp -> volume group mapping
         - Host grp -> direct volume(s) mapping
         So driver need to fill in group to item order based on availability
         as given below
        From host side: Mandatorily one of the (native_storage_host_group_id
                        | native_storage_host_id)
        From volume side: Mandatorily one of the (native_volume_group_id
                                                 | native_volume_id)
        From port side: Optionally (native_port_group_id)
        """
        raise NotImplementedError(
            "Driver API list_masking_views() is not Implemented")

    def get_alert_sources(self, context):
        return []

    def get_latest_perf_timestamp(self, context):
        """Get the timestamp of the latest performance data of the device"""
        pass
