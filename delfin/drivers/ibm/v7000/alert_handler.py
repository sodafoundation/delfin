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
import time

from oslo_log import log
from delfin.common import constants
from delfin import exception

LOG = log.getLogger(__name__)


class AlertHandler(object):
    default_me_category = 'storage-subsystem'

    OID_ERR_ID = '1.3.6.1.4.1.2.6.190.4.3'
    OID_ERR_CODE = '1.3.6.1.4.1.2.6.190.4.4'
    OID_SEQ_NUMBER = '1.3.6.1.4.1.2.6.190.4.9'
    OID_LAST_TIME = '1.3.6.1.4.1.2.6.190.4.10'
    OID_OBJ_TYPE = '1.3.6.1.4.1.2.6.190.4.11'
    OID_OBJ_ID = '1.3.6.1.4.1.2.6.190.4.12'
    OID_OBJ_NAME = '1.3.6.1.4.1.2.6.190.4.19'
    OID_ERR_DESC = '1.3.6.1.4.1.2.6.190.4.13'

    _mandatory_alert_attributes = (
        OID_ERR_ID,
        OID_ERR_CODE,
        OID_SEQ_NUMBER,
        OID_LAST_TIME,
        OID_OBJ_TYPE,
        OID_OBJ_ID,
        OID_OBJ_NAME
    )

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
            alert_model['alert_id'] = alert.get(AlertHandler.OID_ERR_CODE)
            alert_model['alert_name'] = alert.get(AlertHandler.OID_ERR_DESC)
            alert_model['severity'] = constants.Severity.INFORMATIONAL
            alert_model['category'] = constants.Category.NOT_SPECIFIED
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['sequence_number'] = alert.get(
                AlertHandler.OID_SEQ_NUMBER)
            pattern = '%Y-%m-%d %H:%M:%S'
            occur_time = int(time.mktime(time.strptime(
                AlertHandler.OID_LAST_TIME,
                pattern)))
            alert_model['occur_time'] = int(occur_time * 1000)
            alert_model['description'] = alert.get(AlertHandler.OID_ERR_DESC)
            alert_model['resource_type'] = alert.get(AlertHandler.OID_OBJ_TYPE)
            alert_model['location'] = alert.get(AlertHandler.OID_OBJ_NAME)
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = ("Failed to build alert model as some "
                   "attributes missing in alert message.")
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
