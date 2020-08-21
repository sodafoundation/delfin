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
from delfin.common import constants

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for unisphere alerts"""

    # Alert Id and name are not part of queried alerts
    DEFAULT_UNISPHERE_ALERT_NAME = "Unisphere alert about vmax"
    DEFAULT_UNISPHERE_ALERT_ID = 0xFFFFFFFF

    # Translation of queried alert severity to alert model severity
    SEVERITY_MAP = {"FATAL": constants.Severity.FATAL,
                    "CRITICAL": constants.Severity.CRITICAL,
                    "WARNING": constants.Severity.WARNING,
                    "NORMAL": constants.Severity.INFORMATIONAL,
                    "INFORMATION": constants.Severity.INFORMATIONAL}

    def __init__(self):
        pass

    def parse_queried_alerts(self, alert_list):
        """Parse queried alerts and convert to alert model."""

        alert_model_list = []
        for alert in alert_list:
            try:
                alert_model = dict()
                alert_model['alert_id'] = self.DEFAULT_UNISPHERE_ALERT_ID
                alert_model['alert_name'] = self.DEFAULT_UNISPHERE_ALERT_NAME

                alert_model['severity'] = self.SEVERITY_MAP.get(
                    alert['severity'], constants.Severity.NOT_SPECIFIED)

                # category and type are not part of queried alerts
                alert_model['category'] = constants.Category.EVENT
                alert_model['type'] = constants.EventType.EQUIPMENT_ALARM

                alert_model['sequence_number'] = alert['alertId']
                alert_model['occur_time'] = alert['created_date_milliseconds']
                alert_model['description'] = alert['description']
                alert_model['recovery_advice'] = 'None'
                alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE

                # Location is name-value pair
                alert_model['location'] = 'type=' + alert['type']
                alert_model_list.append(alert_model)
            except Exception as e:
                LOG.error(e)
                msg = ("Failed to build alert model as some attributes "
                       "missing in alert message")
                raise exception.InvalidResults(msg)
        return alert_model_list

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
