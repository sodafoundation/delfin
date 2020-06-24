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


from oslo_log import log

from delfin import exception
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for huawei oceanstor driver"""
    default_me_category = 'storage-subsystem'

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

        try:
            alert_model = {}
            # These information are sourced from device registration info
            alert_model['me_dn'] = alert['storage_id']
            alert_model['me_name'] = alert['storage_name']
            alert_model['manufacturer'] = alert['vendor']
            alert_model['product_name'] = alert['model']

            # Fill default values for alert attributes
            alert_model['category'] = alert['hwIsmReportingAlarmFaultCategory']
            alert_model['location'] = alert['hwIsmReportingAlarmLocationInfo']
            alert_model['event_type'] = alert['hwIsmReportingAlarmFaultType']
            alert_model['severity'] = alert['hwIsmReportingAlarmFaultLevel']
            alert_model['probable_cause'] \
                = alert['hwIsmReportingAlarmAdditionInfo']
            alert_model['me_category'] = self.default_me_category
            alert_model['occur_time'] = alert['hwIsmReportingAlarmFaultTime']
            alert_model['alarm_id'] = alert['hwIsmReportingAlarmAlarmID']
            alert_model['alarm_name'] = alert['hwIsmReportingAlarmFaultTitle']
            alert_model['device_alert_sn'] = \
                alert['hwIsmReportingAlarmSerialNo']

            # Trap info does not have clear_type
            # Below fields filling to be updated
            alert_model['clear_type'] = ""
            alert_model['match_key'] = ""
            alert_model['native_me_dn'] = ""
            return alert_model
        except Exception:
            msg = (_("Failed to build alert model as some attributes missing "
                     "in alert message."))
            raise exception.InvalidResults(msg)

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
