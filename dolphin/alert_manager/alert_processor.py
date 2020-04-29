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

from dolphin.drivers.manager import DriverManager

LOG = log.getLogger(__name__)


class AlertProcessor(object):
    """Alert model translation and export functions"""

    @staticmethod
    def process_alert_info(alert):
        """Fills alert model using driver manager interface."""

        # Get driver context/storage_id from resource manager using source ip addr
        # TBD : Currently using source ip addr as identifier.
        # But device might choose different ip ( (other than resister ip) to send trap which is yet to be handled
        storage_id = ''

        # context to be made use of in future
        context = {}

        alert_model = DriverManager().parse_alert(context, storage_id, alert)
        AlertProcessor._export_alert_model(alert_model)

    @staticmethod
    def _export_alert_model(alert_model):
        """Exports the filled alert model to the export manager."""
