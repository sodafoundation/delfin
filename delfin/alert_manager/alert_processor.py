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

from delfin import context
from delfin import db
from delfin import exception
from delfin.drivers import api as driver_manager
from delfin.exporter import base_exporter

LOG = log.getLogger(__name__)


class AlertProcessor(object):
    """Alert model translation and export functions"""

    def __init__(self):
        self.driver_manager = driver_manager.API()

    def process_alert_info(self, alert):
        """Fills alert model using driver manager interface."""
        ctxt = context.RequestContext()
        storage = db.storage_get(ctxt, alert['storage_id'])
        # Fill storage specific info
        alert['storage_name'] = storage['name']
        alert['vendor'] = storage['vendor']
        alert['model'] = storage['model']

        try:
            alert_model = self.driver_manager.parse_alert(context,
                                                          alert['storage_id'],
                                                          alert)
        except Exception as e:
            LOG.error(e)
            raise exception.InvalidResults(
                "Failed to fill the alert model from driver.")

        self._export_alert_model(alert_model)

    def _export_alert_model(self, alert_model):
        """Exports the filled alert model to the export manager."""

        # Export to base exporter which handles dispatch for all exporters
        base_exporter.dispatch_alert_model(alert_model)
