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

    VMAX_MANUFACTURER = 'VMAX_MANUFACTURER'

    def __init__(self):
        pass

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def parse_alert(self, context, alert):
        """Parse alert data got from alert manager and fill the alert model attributes."""
        alert_model = {}
        alert_model['alarm_name'] = alert['snmpTrapOID']
        alert_model['manufacturer'] = self.VMAX_MANUFACTURER

        today = date.today()
        alert_model['received_time'] = today.strftime("%b-%d-%Y")

        # Fill all the alert model fields
        '''
        self.category=
        self.serial_no=
        self.occur_time=

        self.match_key=
        self.me_name=
        self.me_dn=
        self.moi=
        self.event_type=
        self.alarm_name=
        self.alarm_id
        self.severity=
        self.device_alert_sn=
        self.manufacturer=
        self.product_name=
        self.probable_cause=
        self.clear_type=
        self.native_me_dn=
        self.me_category=
        self.me_type=
        '''
        return alert_model

    def clear_alert(self, context, storage_id, alert):
        """Clear alert from storage system."""
        pass
