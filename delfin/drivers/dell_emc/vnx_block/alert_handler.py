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

import six
from oslo_log import log as logging
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for vnx stor driver"""

    OID_MESSAGECODE = '1.3.6.1.4.1.1981.1.4.51.3.6.1.4.1.1981.1.4.51.3.6.1.4.1.1981.1.4.51.3.6.1.4.1.1981.1.4.5'
    OID_DETAILS = '1.3.6.1.4.1.1981.1.4.6'

    # Translation of trap severity to alert model severity
    SEVERITY_MAP = {"76": constants.Severity.CRITICAL,
                    "75": constants.Severity.MAJOR,
                    "74": constants.Severity.MINOR,
                    "73": constants.Severity.WARNING,
                    "72": constants.Severity.WARNING,
                    "77": constants.Severity.FATAL,
                    "71": constants.Severity.INFORMATIONAL,
                    "70": constants.Severity.INFORMATIONAL}

    # Attributes expected in alert info to proceed with model filling
    _mandatory_alert_attributes = (
        OID_MESSAGECODE,
        OID_DETAILS
    )

    def __init__(self, navi_handler=None):
        self.navi_handler = navi_handler

    @staticmethod
    def parse_alert(alert):
        """Parse alert data got from alert manager and fill the alert model."""
        # Check for mandatory alert attributes
        for attr in AlertHandler._mandatory_alert_attributes:
            if not alert.get(attr):
                msg = "Mandatory information %s missing in alert message. " \
                      % attr
                raise exception.InvalidInput(msg)

        try:
            alert_model = dict()
            # These information are sourced from device registration info
            alert_model['alert_id'] = alert.get(AlertHandler.OID_MESSAGECODE)
            alert_model['alert_name'] = alert.get(AlertHandler.OID_DETAILS)
            alert_model['severity'] = AlertHandler.SEVERITY_MAP.get(
                alert.get(AlertHandler.OID_MESSAGECODE)[0:2])
            alert_model['category'] = constants.Category.EVENT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['occur_time'] = time.time() * units.k
            alert_model['description'] = alert.get(AlertHandler.OID_DETAILS)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE

            return alert_model

        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing "
                     "in alert message."))
            raise exception.InvalidResults(msg)

    def handle_alters(self, alertlist):
        alert_list = []
        for alertinfo in alertlist:
            alert_model = {
                'alert_id': alertinfo.get('event_code'),
                'alert_name': alertinfo.get('message'),
                'severity': self.SEVERITY_MAP.get(
                    alertinfo.get('event_code')[0:2]),
                'category': constants.Category.EVENT,
                'type': constants.EventType.EQUIPMENT_ALARM,
                'occur_time': alertinfo.get('log_time_stamp'),
                'description': alertinfo.get('message'),
                'resource_type': constants.DEFAULT_RESOURCE_TYPE
            }
            alert_list.append(alert_model)
        return alert_list

    def list_alerts(self, query_para):
        try:
            alert_lists = []
            host_ip = self.navi_handler.navi_host
            # Get list of EmcVnxStor alerts
            domains = self.navi_handler.get_domain()
            if domains:
                for domain in domains:
                    host_ip = domain.get('ip_address')
                    reslist = self.navi_handler.get_log(host_ip, query_para)
                    alert_list = self.handle_alters(reslist)
                    if alert_list:
                        alert_lists.extend(alert_list)
            else:
                reslist = self.navi_handler.get_log(host_ip, query_para)
                alert_list = self.handle_alters(reslist)
                if alert_list:
                    alert_lists.extend(alert_list)
            if alert_lists:
                alert_lists = self.arrange_alerts(alert_lists)
            return alert_lists
        except Exception as e:
            err_msg = "Get alert failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def sort_alert(self, s):
        return '%s%s%s' % (
            s.get('alert_id'), s.get('description'), str(s.get('occur_time')))

    def arrange_alerts(self, alert_lists):
        try:
            if alert_lists:
                alert_lists.sort(key=self.sort_alert, reverse=True)
            obj = alert_lists[-1]
            for i in range(len(alert_lists) - 2, -1, -1):
                obj_key = '%s%s' % (
                    obj.get('alert_id'), obj.get('description'))
                tmp_key = '%s%s' % (alert_lists[i].get('alert_id'),
                                    alert_lists[i].get('description'))
                if obj_key == tmp_key:
                    if obj.get('occur_time') > alert_lists[i].get(
                            'occur_time'):
                        alert_lists.remove(alert_lists[i])
                    else:
                        alert_lists.remove(obj)
                        obj = alert_lists[i]
                else:
                    obj = alert_lists[i]
            return alert_lists
        except Exception as e:
            err_msg = "arrange alert failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)
