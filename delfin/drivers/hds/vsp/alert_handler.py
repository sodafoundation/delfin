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
import datetime

from oslo_log import log

from delfin import exception
from delfin.common import constants
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertHandler(object):
    default_me_category = 'storage-subsystem'

    REFCODE_OID = '1.3.6.1.4.1.116.5.11.4.2.3'
    DESC_OID = '1.3.6.1.4.1.116.5.11.4.2.7'
    TRAP_TIME_OID = '1.3.6.1.4.1.116.5.11.4.2.6'
    TRAP_DATE_OID = '1.3.6.1.4.1.116.5.11.4.2.5'
    TRAP_NICKNAME_OID = '1.3.6.1.4.1.116.5.11.4.2.2'
    LOCATION_OID = '1.3.6.1.4.1.116.5.11.4.2.4'

    _mandatory_alert_attributes = (REFCODE_OID,
                                   DESC_OID,
                                   TRAP_TIME_OID,
                                   TRAP_DATE_OID,
                                   TRAP_NICKNAME_OID,
                                   LOCATION_OID)

    def __init__(self):
        pass

    def parse_alert(self, context, alert):
        for attr in AlertHandler._mandatory_alert_attributes:
            if not alert.get(attr):
                msg = "Mandatory information %s missing in alert message. " \
                      % attr
                raise exception.InvalidInput(msg)

        try:
            alert_model = dict()
            alert_model['alert_id'] = alert.get(AlertHandler.REFCODE_OID)
            alert_model['alert_name'] = alert.get(AlertHandler.DESC_OID)
            alert_model['severity'] = constants.Severity.INFORMATIONAL
            alert_model['category'] = constants.Category.NOT_SPECIFIED
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            aler_time = '%s%s' % (alert.get(AlertHandler.TRAP_DATE_OID),
                                  alert.get(AlertHandler.TRAP_TIME_OID))
            pattern = '%Y-%m-%d%H:%M:%S'
            occur_time = datetime.strptime(
                aler_time,
                pattern)
            alert_model['occur_time'] = int(occur_time.timestamp() * 1000)
            alert_model['description'] = alert.get(AlertHandler.DESC_OID)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['location'] = alert.get(AlertHandler.LOCATION_OID)

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

    def clear_alert(self, context, sshclient, alert):
        pass
