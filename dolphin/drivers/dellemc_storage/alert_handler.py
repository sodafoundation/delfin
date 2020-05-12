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

from datetime import date

from oslo_log import log

LOG = log.getLogger(__name__)


class AlertHandler(object):
    """Alert handling functions for vmax driver"""
    default_category = 'New'

    def __init__(self):
        pass

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def parse_alert(self, context, alert):
        """Parse alert data got from alert manager and fill the alert model."""
        alert_model = {}

        alert_model['me_dn'] = alert['storage_id']
        alert_model['me_name'] = alert['storage_name']
        alert_model['location_info'] = alert['location']
        alert_model['manufacturer'] = alert['vendor']
        alert_model['product_name'] = alert['model']

        # Fill all the alert model fields
        alert_model = {}
        if alert.get('category'):
            alert_model['category'] = alert['category']
        else:
            alert_model['category'] = self.default_category

        # trap info do not contain occur time
        today = date.today()
        alert_model['occur_time'] = today.strftime("%b-%d-%Y")

        # These information are sourced from device registration info
        alert_model['me_dn'] = alert['storage_id']
        alert_model['me_name'] = alert['storage_name']
        alert_model['location_info'] = alert['location']
        alert_model['manufacturer'] = alert['vendor']
        alert_model['product_name'] = alert['model']

        if alert.get('connUnitName'):
            alert_model['native_me_dn'] = alert['connUnitName']

        if alert.get('connUnitEventType'):
            alert_model['event_type'] = alert['connUnitEventType']

        if alert.get('emcAsyncEventCode'):
            alert_model['alarm_id'] = alert['emcAsyncEventCode']
            alert_model['alarm_name'] = alert['emcAsyncEventCode']

        if alert.get('connUnitEventSeverity'):
            alert_model['severity'] = alert['connUnitEventSeverity']

        if alert.get('connUnitEventDescr'):
            alert_model['probable_cause'] = alert['connUnitEventDescr']

        if alert.get('connUnitType'):
            alert_model['me_category'] = alert['connUnitType']

        # trap info does not have clear_type value
        alert_model['clear_type'] = ""

        return alert_model

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
