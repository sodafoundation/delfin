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

    @abc.abstractmethod
    def add_trap_config(self, context, trap_config):
        """Config the trap receiver in storage system."""
        pass

    @abc.abstractmethod
    def remove_trap_config(self, context, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    @abc.abstractmethod
    def parse_alert(self, context, alert):
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

    def list_alerts(self, context):
        """List all current alerts from storage system."""
        pass

    @abc.abstractmethod
    def clear_alert(self, context, sequence_number):
        """Clear alert from storage system."""
        pass
