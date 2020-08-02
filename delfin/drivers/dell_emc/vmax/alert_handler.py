# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime

from oslo_log import log

from delfin import exception
from delfin.alert_manager import alert_processor
from delfin.drivers.dell_emc.vmax import alert_mapper

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for vmax driver"""

    # Translation of trap severity to alert model severity
    SEVERITY_MAP = {"emergency": alert_processor.Severity.FATAL,
                    "alert": alert_processor.Severity.CRITICAL,
                    "critical": alert_processor.Severity.CRITICAL,
                    "error": alert_processor.Severity.MAJOR,
                    "warning": alert_processor.Severity.WARNING,
                    "notify": alert_processor.Severity.WARNING,
                    "info": alert_processor.Severity.INFORMATIONAL,
                    "debug": alert_processor.Severity.INFORMATIONAL,
                    "mark": alert_processor.Severity.INFORMATIONAL}

    # Translation of trap resource type to alert model resource type
    RESOURCE_TYPE_MAP = {
        "hub": alert_processor.ResourceType.NETWORK,
        "switch": alert_processor.ResourceType.NETWORK,
        "gateway": alert_processor.ResourceType.NETWORK,
        "converter": alert_processor.ResourceType.NETWORK,
        "hba": alert_processor.ResourceType.NETWORK,
        "proxy-agent": alert_processor.ResourceType.NETWORK,
        "storage-device": alert_processor.ResourceType.STORAGE,
        "host": alert_processor.ResourceType.SERVER,
        "storage-subsystem": alert_processor.ResourceType.STORAGE,
        "module": alert_processor.ResourceType.OTHER,
        "swdriver": alert_processor.ResourceType.OTHER,
        "storage-access-device": alert_processor.ResourceType.STORAGE,
        "wdm": alert_processor.ResourceType.OTHER,
        "ups": alert_processor.ResourceType.OTHER,
        "other": alert_processor.ResourceType.OTHER}

    # Attributes mandatory in alert info to proceed with model filling
    _mandatory_alert_attributes = ('emcAsyncEventCode',
                                   'connUnitEventSeverity',
                                   'connUnitEventType', 'connUnitEventDescr',
                                   'connUnitType',
                                   'emcAsyncEventComponentType',
                                   'emcAsyncEventComponentName',
                                   'emcAsyncEventSource')

    def __init__(self):
        pass

    """
    Alert Model	Description
    Part of the fields filled from delfin resource info and other from driver
    *****Filled from delfin resource info***********************
    storage_id	Id of the storage system on behalf of which alert is generated
    storage_name	Name of the storage system on behalf of which alert is
                    generated
    manufacturer	Vendor of the device
    product_name	Product or the model name
    serial_number	Serial number of the alert generating source
    ****************************************************
    *****Filled from driver side ***********************
    alert_id	Unique identification for a given alert type
    alert_name	Unique name for a given alert type
    severity	Severity of the alert
    category	Category of alert generated
    type	Type of the alert generated
    sequence_number	Sequence number for the alert, uniquely identifies a
                              given alert instance used for clearing the alert
    occur_time	Time at which alert is generated from device
    detailed_info	Possible cause description or other details about the alert
    recovery_advice	Some suggestion for handling the given alert
    resource_type	Resource type of device/source generating alert
    location	Detailed info about the tracing the alerting device such as
                slot, rack, component, parts etc
    *****************************************************
    """

    def parse_alert(self, context, alert):
        """Parse alert data got from alert manager and fill the alert model."""

        # Check for mandatory alert attributes
        for attr in self._mandatory_alert_attributes:
            if not alert.get(attr):
                msg = "Mandatory information %s missing in alert message. " \
                      % attr
                raise exception.InvalidInput(msg)

        alert_model = {}

        # Fill alarm id and fill alarm_name with corresponding mapping names
        alert_model['alert_id'] = alert['emcAsyncEventCode']
        alert_model['alert_name'] = alert_mapper.alarm_id_name_mapping.get(
            alert_model['alert_id'], alert_model['alert_id'])

        alert_model['severity'] = self.SEVERITY_MAP.get(
            alert['connUnitEventSeverity'],
            alert_processor.Severity.INFORMATIONAL)

        alert_model['category'] = alert_processor.Category.NOT_SPECIFIED
        alert_model['type'] = alert['connUnitEventType']

        alert_model['sequence_number'] = alert['connUnitEventId']

        # trap info do not contain occur time, update with received time
        # Get date and time. Format will be like : Wed May 20 01:53:29 2020
        curr_time = datetime.now()
        alert_model['occur_time'] = curr_time.strftime('%c')
        alert_model['detailed_info'] = alert['connUnitEventDescr']
        alert_model['recovery_advice'] = 'None'
        alert_model['resource_type'] = self.RESOURCE_TYPE_MAP.get(
            alert['connUnitType'], alert_processor.ResourceType.OTHER)

        # Location is name-value pair having component type and component name
        component_type = alert_mapper.component_type_mapping.get(
            alert.get('emcAsyncEventComponentType'), "")
        alert_model['location'] = 'Array id=' \
                                  + alert['connUnitName'] \
                                  + ',Component type=' \
                                  + component_type \
                                  + ',Component name=' \
                                  + alert['emcAsyncEventComponentName'] \
                                  + ',Event source=' \
                                  + alert['emcAsyncEventSource']

        return alert_model

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
