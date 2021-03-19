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
import hashlib
import time

import six
from oslo_log import log as logging

from delfin import exception
from delfin.common import constants
from delfin.drivers.hpe.hpe_3par import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for Hpe3 parstor driver"""

    OID_MESSAGECODE = '1.3.6.1.4.1.12925.1.7.1.8.1'
    OID_SEVERITY = '1.3.6.1.4.1.12925.1.7.1.2.1'
    OID_STATE = '1.3.6.1.4.1.12925.1.7.1.9.1'
    OID_ID = '1.3.6.1.4.1.12925.1.7.1.7.1'
    OID_TIMEOCCURRED = '1.3.6.1.4.1.12925.1.7.1.3.1'
    OID_DETAILS = '1.3.6.1.4.1.12925.1.7.1.6.1'
    OID_COMPONENT = '1.3.6.1.4.1.12925.1.7.1.5.1'

    # Translation of trap severity to alert model severity
    SEVERITY_MAP = {"1": constants.Severity.CRITICAL,
                    "2": constants.Severity.MAJOR,
                    "3": constants.Severity.MINOR,
                    "4": constants.Severity.WARNING,
                    "0": constants.Severity.FATAL,
                    "5": constants.Severity.INFORMATIONAL,
                    "6": constants.Severity.NOT_SPECIFIED}

    # Translation of trap alert category to alert model category
    CATEGORY_MAP = {"0": constants.Category.NOT_SPECIFIED,
                    "1": constants.Category.FAULT,
                    "2": constants.Category.RECOVERY,
                    "3": constants.Category.RECOVERY,
                    "4": constants.Category.RECOVERY,
                    "5": constants.Category.RECOVERY}

    ALERT_KEY_MAP = {"Id": "sequence_number",
                     "State": "category",
                     "MessageCode": "message_code",
                     "Time": "occur_time",
                     "Severity": "severity",
                     "Type": "alert_name",
                     "Message": "description",
                     "Component": "location"
                     }

    ALERT_LEVEL_MAP = {"Critical": constants.Severity.CRITICAL,
                       "Major": constants.Severity.MAJOR,
                       "Minor": constants.Severity.MINOR,
                       "Degraded": constants.Severity.WARNING,
                       "Fatal": constants.Severity.FATAL,
                       "Informational": constants.Severity.INFORMATIONAL,
                       "Debug": constants.Severity.NOT_SPECIFIED
                       }

    # Attributes expected in alert info to proceed with model filling
    _mandatory_alert_attributes = (
        OID_MESSAGECODE,
        OID_SEVERITY,
        OID_STATE,
        OID_ID,
        OID_TIMEOCCURRED,
        OID_DETAILS,
        OID_COMPONENT
    )

    # Convert received time to epoch format
    TIME_PATTERN = '%Y-%m-%d %H:%M:%S CST'

    def __init__(self, rest_handler=None, ssh_handler=None):
        self.rest_handler = rest_handler
        self.ssh_handler = ssh_handler

    @staticmethod
    def parse_alert(context, alert):
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
            alert_model['alert_name'] = AlertHandler.get_alert_type(alert.get(
                AlertHandler.OID_MESSAGECODE))
            alert_model['severity'] = AlertHandler.SEVERITY_MAP.get(
                alert.get(AlertHandler.OID_SEVERITY),
                constants.Severity.NOT_SPECIFIED)
            alert_model['category'] = AlertHandler.CATEGORY_MAP.get(
                alert.get(AlertHandler.OID_STATE),
                constants.Category.NOT_SPECIFIED)
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            alert_model['sequence_number'] = alert.get(AlertHandler.OID_ID)
            alert_model['occur_time'] = AlertHandler.get_time_stamp(
                alert.get(AlertHandler.OID_TIMEOCCURRED))
            alert_model['description'] = alert.get(AlertHandler.OID_DETAILS)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['location'] = alert.get(AlertHandler.OID_COMPONENT)
            alert_model['match_key'] = hashlib.md5(
                alert.get(AlertHandler.OID_DETAILS, '').encode()).hexdigest()
            if alert.get(AlertHandler.OID_STATE) == '5':
                alert_model['clear_category'] = constants.ClearType.AUTOMATIC
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

    def clear_alert(self, context, alert):
        """Clear alert from storage system.
           Remove command: removealert
        """
        try:
            if alert:
                self.ssh_handler.remove_alerts(alert)
                LOG.info("Clear alert %s successfully." % alert)
        except exception.DelfinException as e:
            err_msg = "Remove alert %s failed: %s" % (alert, e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Remove alert %s failed: %s" % (alert, six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def judge_alert_time(map, query_para):
        if len(map) <= 1:
            return False
        if query_para is None and len(map) > 1:
            return True
        occur_time = AlertHandler.get_time_stamp(map.get('occur_time'))
        if query_para.get('begin_time') and query_para.get('end_time'):
            if occur_time >= int(query_para.get('begin_time')) and \
                    occur_time <= int(query_para.get('end_time')):
                return True
        elif query_para.get('begin_time'):
            if occur_time >= int(query_para.get('begin_time')):
                return True
        elif query_para.get('end_time'):
            if occur_time <= int(query_para.get('end_time')):
                return True
        return False

    def handle_alters(self, alertlist, query_para):
        map = {}
        alert_list = []
        for alertinfo in alertlist:
            strline = alertinfo
            if strline is not None and strline != '':
                strinfo = strline.split(': ', 1)
                strinfo[0] = strinfo[0].replace(" ", "")
                key = self.ALERT_KEY_MAP.get(
                    strinfo[0]) and self.ALERT_KEY_MAP.get(
                    strinfo[0]) or ''
                value = self.ALERT_KEY_MAP.get(
                    strinfo[0]) and strinfo[1] or ''
                map[key] = value
            elif AlertHandler.judge_alert_time(map, query_para):
                severity = self.ALERT_LEVEL_MAP.get(map.get('severity'))
                category = map.get('category') == 'New' and 'Fault' or ''
                occur_time = AlertHandler.get_time_stamp(map.get('occur_time'))
                alert_id = map.get('message_code') and str(int(map.get(
                    'message_code'), 16)) or ''
                alert_model = {
                    'alert_id': alert_id,
                    'alert_name': map.get('alert_name'),
                    'severity': severity,
                    'category': category,
                    'type': constants.EventType.EQUIPMENT_ALARM,
                    'sequence_number': map.get('sequence_number'),
                    'occur_time': occur_time,
                    'description': map.get('description'),
                    'resource_type': constants.DEFAULT_RESOURCE_TYPE,
                    'location': map.get('location')
                }
                alert_list.append(alert_model)
                map = {}
        return alert_list

    def list_alerts(self, context, query_para):
        try:
            # Get list of Hpe3parStor alerts
            try:
                reslist = self.ssh_handler.get_all_alerts()
            except Exception as e:
                err_msg = "Failed to ssh Hpe3parStor: %s" % \
                          (six.text_type(e))
                LOG.error(err_msg)
                raise exception.SSHException(err_msg)

            alertlist = reslist.split('\n')

            return self.handle_alters(alertlist, query_para)
        except exception.DelfinException as e:
            err_msg = "Get alerts failed: %s" % (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Get alert failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    @staticmethod
    def get_time_stamp(time_str):
        """ Time stamp to time conversion
        """
        time_stamp = ''
        try:
            if time_str is not None:
                # Convert to time array first
                time_array = time.strptime(time_str, AlertHandler.TIME_PATTERN)
                # Convert to timestamps to milliseconds
                time_stamp = int(time.mktime(time_array) * 1000)
        except Exception as e:
            LOG.error(e)

        return time_stamp

    @staticmethod
    def get_alert_type(message_code):
        """
        Get alert type

        :param str message_code: alert's message_code.
        :return: returns alert's type
        """
        re = ''
        try:
            if message_code is not None:
                message_key = \
                    (hex(int(message_code))).replace('0x', '0x0')
                re = consts.HPE3PAR_ALERT_CODE.get(message_key)
        except Exception as e:
            LOG.error(e)

        return re
