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
import time

import six
from oslo_log import log

from delfin import exception, utils
from delfin.common import alert_util
from delfin.common import constants
from delfin.drivers.dell_emc.unity import consts
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertHandler(object):

    OID_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'
    OID_NODE = '1.3.6.1.4.1.1139.103.1.18.1.1'
    OID_COMPONENT = '1.3.6.1.4.1.1139.103.1.18.1.2'
    OID_SYMPTOMID = '1.3.6.1.4.1.1139.103.1.18.1.3'
    OID_SYMPTOMTEXT = '1.3.6.1.4.1.1139.103.1.18.1.4'
    ALERT_LEVEL_MAP = {0: constants.Severity.CRITICAL,
                       1: constants.Severity.CRITICAL,
                       2: constants.Severity.CRITICAL,
                       3: constants.Severity.MAJOR,
                       4: constants.Severity.WARNING,
                       5: constants.Severity.FATAL,
                       6: constants.Severity.INFORMATIONAL,
                       7: constants.Severity.NOT_SPECIFIED
                       }
    TRAP_LEVEL_MAP = {'1.3.6.1.4.1.1139.103.1.18.2.0':
                      constants.Severity.CRITICAL,
                      '1.3.6.1.4.1.1139.103.1.18.2.1':
                      constants.Severity.CRITICAL,
                      '1.3.6.1.4.1.1139.103.1.18.2.2':
                      constants.Severity.CRITICAL,
                      '1.3.6.1.4.1.1139.103.1.18.2.3':
                      constants.Severity.MAJOR,
                      '1.3.6.1.4.1.1139.103.1.18.2.4':
                      constants.Severity.WARNING,
                      '1.3.6.1.4.1.1139.103.1.18.2.5':
                      constants.Severity.FATAL,
                      '1.3.6.1.4.1.1139.103.1.18.2.6':
                      constants.Severity.INFORMATIONAL,
                      '1.3.6.1.4.1.1139.103.1.18.2.7':
                      constants.Severity.NOT_SPECIFIED
                      }
    SECONDS_TO_MS = 1000
    SECONDS_PER_HOUR = 60 * 60
    STATE_SOLVED = 2
    TIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    def parse_alert(context, alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = alert.get(AlertHandler.OID_SYMPTOMID)
            trap_map_desc = consts.TRAP_DESC.get(
                alert.get(AlertHandler.OID_SYMPTOMID))
            if trap_map_desc:
                alert_desc = trap_map_desc[2]
            else:
                alert_desc = alert.get(AlertHandler.OID_SYMPTOMTEXT)
            alert_model['alert_name'] = alert.get(AlertHandler.OID_SYMPTOMTEXT)
            alert_model['severity'] = AlertHandler.TRAP_LEVEL_MAP.get(
                alert.get(AlertHandler.OID_SEVERITY),
                constants.Severity.INFORMATIONAL)
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            occur_time = utils.utcnow_ms()
            alert_model['occur_time'] = occur_time
            alert_model['description'] = alert_desc
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['location'] = alert.get(AlertHandler.OID_NODE)
            alert_model['match_key'] = hashlib.md5(alert.get(
                AlertHandler.OID_SYMPTOMTEXT).encode()).hexdigest()

            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing"))
            raise exception.InvalidResults(msg)

    def parse_queried_alerts(self, alert_model_list, alert_dict, query_para):
        alerts = alert_dict.get('entries')
        for alert in alerts:
            try:
                content = alert.get('content', {})
                if content.get('state') == AlertHandler.STATE_SOLVED:
                    continue
                occur_time = int(time.mktime(time.strptime(
                    content.get('timestamp'),
                    self.TIME_PATTERN)))
                hour_offset = (time.mktime(time.localtime()) - time.mktime(
                    time.gmtime())) / AlertHandler.SECONDS_PER_HOUR
                occur_time = occur_time + (int(hour_offset) *
                                           AlertHandler.SECONDS_PER_HOUR)
                if not alert_util.is_alert_in_time_range(
                        query_para, int(occur_time *
                                        AlertHandler.SECONDS_TO_MS)):
                    continue
                alert_model = {}
                location = ''
                resource_type = constants.DEFAULT_RESOURCE_TYPE
                if content.get('component'):
                    location = content.get('component').get('id')
                alert_model['alert_id'] = content.get('messageId')
                alert_model['alert_name'] = content.get('message')
                alert_model['severity'] = self.ALERT_LEVEL_MAP.get(
                    content.get('severity'),
                    constants.Severity.INFORMATIONAL)
                alert_model['category'] = constants.Category.FAULT
                alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
                alert_model['sequence_number'] = content.get('id')
                alert_model['occur_time'] = int(occur_time *
                                                AlertHandler.SECONDS_TO_MS)
                alert_model['description'] = content.get('description')
                alert_model['resource_type'] = resource_type
                alert_model['location'] = location
                alert_model_list.append(alert_model)
                alert_model['match_key'] = hashlib.md5(
                    content.get('message').encode()).hexdigest()
            except Exception as e:
                LOG.error(e)
                err_msg = "Failed to build alert model as some attributes " \
                          "missing in queried alerts: %s" % (six.text_type(e))
                raise exception.InvalidResults(err_msg)
