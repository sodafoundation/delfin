# Copyright 2021 The SODA Authors.
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
import hashlib

from oslo_log import log as logging

from delfin import exception, utils
from delfin.common import constants
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class AlertHandler(object):

    @staticmethod
    def parse_alert(alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = AlertHandler.check_event_code(
                alert.get(consts.OID_MESSAGECODE))
            alert_model['alert_name'] = alert.get(consts.OID_DETAILS)
            alert_model['severity'] = consts.TRAP_LEVEL_MAP.get(
                alert.get(consts.OID_SEVERITY),
                constants.Severity.INFORMATIONAL)
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['occur_time'] = utils.utcnow_ms()
            alert_model['description'] = alert.get(consts.OID_DETAILS)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['match_key'] = hashlib.md5(
                alert.get(consts.OID_DETAILS, '').encode()).hexdigest()
            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing "
                     "in alert message."))
            raise exception.InvalidResults(msg)

    @staticmethod
    def check_event_code(event_code):
        if '0x' not in event_code:
            event_code = '0x%s' % event_code
        return event_code
