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
from delfin.alert_manager import alert_processor
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for huawei oceanstor driver"""

    # Translation of trap severity to alert model severity
    SEVERITY_MAP = {"criticalAlarm": alert_processor.Severity.CRITICAL,
                    "majorAlarm": alert_processor.Severity.MAJOR,
                    "minorAlarm": alert_processor.Severity.MINOR,
                    "warningAlarm": alert_processor.Severity.WARNING}

    # Translation of trap alert category to alert model category
    CATEGORY_MAP = {"faultAlarm": alert_processor.Category.FAULT,
                    "recoveryAlarm": alert_processor.Category.RECOVERY,
                    "eventAlarm": alert_processor.Category.EVENT}

    # Attributes expected in alert info to proceed with model filling
    _mandatory_alert_attributes = ('hwIsmReportingAlarmAlarmID',
                                   'hwIsmReportingAlarmFaultTitle',
                                   'hwIsmReportingAlarmFaultLevel',
                                   'hwIsmReportingAlarmNodeCode',
                                   'hwIsmReportingAlarmFaultType',
                                   'hwIsmReportingAlarmAdditionInfo',
                                   'hwIsmReportingAlarmSerialNo',
                                   'hwIsmReportingAlarmFaultCategory',
                                   'hwIsmReportingAlarmRestoreAdvice',
                                   'hwIsmReportingAlarmFaultTime'
                                   )

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

        try:
            alert_model = {}
            # These information are sourced from device registration info
            alert_model['alert_id'] = alert['hwIsmReportingAlarmAlarmID']
            alert_model['alert_name'] = alert['hwIsmReportingAlarmFaultTitle']
            alert_model['severity'] = self.SEVERITY_MAP.get(
                alert['hwIsmReportingAlarmFaultLevel'],
                alert_processor.Severity.NOT_SPECIFIED)
            alert_model['category'] = self.CATEGORY_MAP.get(
                alert['hwIsmReportingAlarmFaultCategory'],
                alert_processor.Category.NOT_SPECIFIED)
            alert_model['type'] = alert['hwIsmReportingAlarmFaultType']
            alert_model['sequence_number'] \
                = alert['hwIsmReportingAlarmSerialNo']
            alert_model['occur_time'] = alert['hwIsmReportingAlarmFaultTime']
            alert_model['detailed_info'] \
                = alert['hwIsmReportingAlarmAdditionInfo']
            alert_model['recovery_advice'] \
                = alert['hwIsmReportingAlarmRestoreAdvice']
            alert_model['resource_type'] = alert_processor.ResourceType.STORAGE
            alert_model['location'] = 'Node code=' \
                                      + alert['hwIsmReportingAlarmNodeCode']

            if alert.get('hwIsmReportingAlarmLocationInfo'):
                alert_model['location'] \
                    = alert_model['location'] + ',' + alert[
                    'hwIsmReportingAlarmLocationInfo']

            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing "
                     "in alert message."))
            raise exception.InvalidResults(msg)

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        # Currently not implemented
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        # Currently not implemented
        pass

    def clear_alert(self, context, storage_id, alert):
        # Currently not implemented
        """Clear alert from storage system."""
        pass
