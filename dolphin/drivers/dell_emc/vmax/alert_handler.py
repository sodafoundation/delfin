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

from dolphin import exception
from dolphin.drivers.dell_emc.vmax import alert_mapper

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for vmax driver"""
    default_category = 'New'
    default_event_type = 'unknown'
    default_probable_cause = 'Not available'
    default_severity = 'unknown'
    default_me_category = 'storage-subsystem'
    default_location = 'unknown'

    # Mandatory attributes expected in alert info to proceed with model filling
    mandatory_alert_attributes = ('storage_id', 'storage_name', 'vendor',
                                  'model', 'connUnitName', 'emcAsyncEventCode')

    def __init__(self):
        pass

    """
    Alert model contains below fields
    category : Type of the reported notification
    occur_time : Time of occurrence of alert. When trap does not contain it,
                 it will be filled with receive time
    match_key : This info uniquely identifies the fault point. Several infos
                such as source system id, location, alarm id together can be
                used to construct this
    me_dn : Unique id at resource module (management system) side. me stands
            for management element here
    me_name : Unique name at resource module (management system) side
    native_me_dn : Unique id of the device at source system that reports the
                   alarm
    location : Alarm location information. It helps to locate the lowest unit
               where fault is originated(Name-value pairs)
               ex: Location = subtrack, No = 1, Slot No = 5.
                   shelf Id = 1, board type = ADSL
    event_type : Basic classification of the alarm. Probable values such as
                 status, configuration, topology ....
    alarm_id : Identification of alarm
    alarm_name : Name of the alarm, might need translation from alarm id
    severity : Severity of alarm. Helps admin to decide on action to be taken
               Probable values: Critical, Major, Minor, Warning, Info
    device_alert_sn : Sequence number of alert generated. This will be helpful
                      during alert clearing process
    manufacturer : Vendor of the device
    Product_name : Name of the product
    probable_cause : Probable reason for alert generation
    clear_type : Alarm clearance type such as manual, automatic, reset clear
    me_category : Resource category of the device generating the alarm
                  Probable value: Network,Server,Storage..
    """

    def parse_alert(self, context, alert):
        """Parse alert data got from alert manager and fill the alert model."""

        # Check for mandatory alert attributes
        for attr in self.mandatory_alert_attributes:
            if not alert.get(attr):
                msg = "Mandatory information %s missing in alert message. " \
                      % attr
                raise exception.ValidationError(detail=msg)

        alert_model = {}
        # These information are sourced from device registration info
        alert_model['me_dn'] = alert['storage_id']
        alert_model['me_name'] = alert['storage_name']
        alert_model['manufacturer'] = alert['vendor']
        alert_model['product_name'] = alert['model']

        # Fill default values for alert attributes
        alert_model['category'] = self.default_category
        alert_model['location'] = self.default_location
        alert_model['event_type'] = self.default_event_type
        alert_model['severity'] = self.default_severity
        alert_model['probable_cause'] = self.default_probable_cause
        alert_model['me_category'] = self.default_me_category

        # Trap info does not have clear_type and alert sequence number
        # TBD : Below fields filling to be updated
        alert_model['clear_type'] = ""
        alert_model['device_alert_sn'] = ""
        alert_model['match_key'] = ""

        # trap info do not contain occur time, update with received time
        # Get date and time. Format will be like : Wed May 20 01:53:29 2020
        curr_time = datetime.now()
        alert_model['occur_time'] = curr_time.strftime('%c')

        # Fill all the alert model fields
        if alert.get('category'):
            alert_model['category'] = alert['category']

        # Array id is used to fill unique id at source system side
        alert_model['native_me_dn'] = alert['connUnitName']

        # Location is name-value pair having component type and component name
        if alert.get('emcAsyncEventComponentType') \
                and alert.get('emcAsyncEventComponentName'):
            component_type = alert_mapper.component_type_mapping.get(
                alert.get('emcAsyncEventComponentType'), "")
            alert_model['location'] = 'Component type: ' \
                                      + component_type \
                                      + ',Component name: ' \
                                      + alert['emcAsyncEventComponentName']

        if alert.get('connUnitEventType'):
            alert_model['event_type'] = alert['connUnitEventType']

        if alert.get('connUnitEventSeverity'):
            alert_model['severity'] = alert['connUnitEventSeverity']

        if alert.get('connUnitEventDescr'):
            alert_model['probable_cause'] = alert['connUnitEventDescr']

        # Fill alarm id and fill alarm_name with corresponding mapping names
        alert_model['alarm_id'] = alert['emcAsyncEventCode']
        alert_model['alarm_name'] = alert_mapper.alarm_id_name_mapping.get(
            alert_model['alarm_id'], alert_model['alarm_id'])

        if alert.get('connUnitType'):
            alert_model['me_category'] = alert['connUnitType']

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
