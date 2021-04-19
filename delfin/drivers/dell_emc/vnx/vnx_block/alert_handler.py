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
from oslo_log import log as logging
from oslo_utils import units

from delfin import exception
from delfin.common import constants
from delfin.drivers.dell_emc.vnx.vnx_block import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class AlertHandler(object):

    def __init__(self, navi_handler):
        self.navi_handler = navi_handler

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
            alert_model['occur_time'] = int(time.time() * units.k)
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

    def handle_alerts(self, alerts):
        alert_list = []
        for alert in alerts:
            alert_model = {
                'alert_id': AlertHandler.check_event_code(
                    alert.get('event_code')),
                'alert_name': alert.get('message'),
                'severity': consts.SEVERITY_MAP.get(
                    alert.get('event_code')[0:2]),
                'category': constants.Category.FAULT,
                'type': constants.EventType.EQUIPMENT_ALARM,
                'occur_time': alert.get('log_time_stamp'),
                'description': alert.get('message'),
                'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                'match_key': hashlib.md5(
                    alert.get('message', '').encode()).hexdigest()
            }
            alert_list.append(alert_model)
        return alert_list

    def list_alerts(self, query_para):
        alert_lists = []
        domains = self.navi_handler.get_domain()
        host_ip_list = []
        if domains:
            for domain in domains:
                host_ip = domain.get('ip_address')
                if host_ip:
                    host_ip_list.append(host_ip)
        else:
            host_ip_list.append(self.navi_handler.navi_host)
        for host_ip in host_ip_list:
            alerts = self.navi_handler.get_log(host_ip, query_para)
            alert_list = self.handle_alerts(alerts)
            if alert_list:
                alert_lists.extend(alert_list)
        alert_lists = self.remove_duplication_alert(alert_lists)
        return alert_lists

    def get_sort_key(self, alert):
        return '%s%s%s' % (
            alert.get('alert_id'), alert.get('description'),
            str(alert.get('occur_time')))

    def remove_duplication_alert(self, alert_lists):
        try:
            if alert_lists:
                alert_lists.sort(key=self.get_sort_key, reverse=True)
                alert = alert_lists[-1]
                for i in range(len(alert_lists) - 2, -1, -1):
                    main_alert_key = '%s%s' % (
                        alert.get('alert_id'), alert.get('description'))
                    other_alert_key = '%s%s' % (alert_lists[i].get('alert_id'),
                                                alert_lists[i].get(
                                                    'description'))
                    if main_alert_key == other_alert_key:
                        if alert.get('occur_time') > alert_lists[i].get(
                                'occur_time'):
                            alert_lists.remove(alert_lists[i])
                        else:
                            alert_lists.remove(alert)
                            alert = alert_lists[i]
                    else:
                        alert = alert_lists[i]
            return alert_lists
        except Exception as e:
            err_msg = "remove duplication failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def check_event_code(event_code):
        if '0x' not in event_code:
            event_code = '0x%s' % event_code
        return event_code
