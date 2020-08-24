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
from delfin.common import constants
from delfin.drivers.huawei.oceanstor import oid_mapper
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for huawei oceanstor driver"""
    def __init__(self):
        self.oid_mapper = oid_mapper.OidMapper()

    TIME_PATTERN = "%Y-%m-%d,%H:%M:%S.%f"

    # Translation of trap severity to alert model severity
    # Values are: criticalAlarm=1, majorAlarm=2, minorAlarm=3, warningAlarm=4
    SEVERITY_MAP = {"1": constants.Severity.CRITICAL,
                    "2": constants.Severity.MAJOR,
                    "3": constants.Severity.MINOR,
                    "4": constants.Severity.WARNING}

    # Translation of trap alert category to alert model category
    # Values are: faultAlarm=1, resumeAlarm=2, eventAlarm=3
    CATEGORY_MAP = {"1": constants.Category.FAULT,
                    "2": constants.Category.RECOVERY,
                    "3": constants.Category.EVENT}

    # Translation of trap alert category to alert type
    # Values are: communicationQuality=1, equipmentFault=2, processError=3
    #             serviceQuality=4, environmentFault=5, performanceLimit=6
    TYPE_MAP = {
        "1": constants.EventType.COMMUNICATIONS_ALARM,
        "2": constants.EventType.EQUIPMENT_ALARM,
        "3": constants.EventType.PROCESSING_ERROR_ALARM,
        "4": constants.EventType.QUALITY_OF_SERVICE_ALARM,
        "5": constants.EventType.ENVIRONMENTAL_ALARM,
        "6": constants.EventType.QUALITY_OF_SERVICE_ALARM}

    # Translation of severity of queried alerts to alert model severity
    QUERY_ALERTS_SEVERITY_MAP = {2: constants.Severity.INFORMATIONAL,
                                 3: constants.Severity.WARNING,
                                 5: constants.Severity.MAJOR,
                                 6: constants.Severity.CRITICAL}

    # Translation of alert category of queried alerts to alert model category
    QUERY_ALERTS_CATEGORY_MAP = {0: constants.Category.EVENT,
                                 1: constants.Category.FAULT,
                                 2: constants.Category.RECOVERY}

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

    def parse_alert(self, context, alert):
        """Parse alert data and fill the alert model."""
        # Check for mandatory alert attributes
        alert = self.oid_mapper.map_oids(alert)
        LOG.info("Get alert from storage: %s", alert)

        for attr in self._mandatory_alert_attributes:
            if not alert.get(attr):
                msg = "Mandatory information %s missing in alert message. " \
                      % attr
                raise exception.InvalidInput(msg)

        try:
            alert_model = dict()
            # These information are sourced from device registration info
            alert_model['alert_id'] = alert['hwIsmReportingAlarmAlarmID']
            alert_model['alert_name'] = alert['hwIsmReportingAlarmFaultTitle']
            alert_model['severity'] = self.SEVERITY_MAP.get(
                alert['hwIsmReportingAlarmFaultLevel'],
                constants.Severity.NOT_SPECIFIED)
            alert_model['category'] = self.CATEGORY_MAP.get(
                alert['hwIsmReportingAlarmFaultCategory'],
                constants.Category.NOT_SPECIFIED)
            alert_model['type'] = self.TYPE_MAP.get(
                alert['hwIsmReportingAlarmFaultType'],
                constants.EventType.NOT_SPECIFIED)
            alert_model['sequence_number'] \
                = alert['hwIsmReportingAlarmSerialNo']
            occur_time = datetime.strptime(
                alert['hwIsmReportingAlarmFaultTime'],
                self.TIME_PATTERN)
            alert_model['occur_time'] = int(occur_time.timestamp() * 1000)

            description = alert['hwIsmReportingAlarmAdditionInfo']
            if self._is_hex(description):
                description = bytes.fromhex(description[2:]).decode('ascii')
            alert_model['description'] = description

            recovery_advice = alert['hwIsmReportingAlarmRestoreAdvice']
            if self._is_hex(recovery_advice):
                recovery_advice = bytes.fromhex(
                    recovery_advice[2:]).decode('ascii')

            alert_model['recovery_advice'] = recovery_advice

            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
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

    def parse_queried_alerts(self, alert_list):
        """Parses list alert data and fill the alert model."""
        # List contains all the current alarms of given storage id
        alert_model_list = []
        for alert in alert_list:
            try:
                alert_model = dict()
                alert_model['alert_id'] = alert['eventID']
                alert_model['alert_name'] = alert['name']
                alert_model['severity'] = self.QUERY_ALERTS_SEVERITY_MAP.get(
                    alert['level'], constants.Severity.NOT_SPECIFIED)
                alert_model['category'] = self.QUERY_ALERTS_CATEGORY_MAP.get(
                    alert['eventType'], constants.Category.NOT_SPECIFIED)
                alert_model['type'] = constants.EventType.NOT_SPECIFIED
                alert_model['sequence_number'] = alert['sequence']
                occur_time = alert['startTime']
                alert_model['occur_time'] = int(occur_time * 1000)
                alert_model['description'] = alert['description']

                alert_model['recovery_advice'] = alert['suggestion']

                alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
                alert_model['location'] = alert['location']

                alert_model_list.append(alert_model)
            except Exception as e:
                LOG.error(e)
                msg = (_("Failed to build alert model as some attributes"
                         " missing in queried alerts."))
                raise exception.InvalidResults(msg)
        return alert_model_list

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

    def _is_hex(self, value):
        try:
            int(value, 16)
        except ValueError:
            return False
        return True
