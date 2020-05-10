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

from dolphin import context
from dolphin import db
from dolphin import exception
from dolphin.drivers import api as driver_manager

LOG = log.getLogger(__name__)


class AlertProcessor(object):
    """Alert model translation and export functions"""

    def __init__(self):
        self.driver_manager = driver_manager.API()

    def process_alert_info(self, alert):
        """Fills alert model using driver manager interface."""

        ctxt = context.get_admin_context()

        # Trap source ip should be configured as part of alert source configuration.
        # Incoming source ip will be mapped with Trap source ip in db and
        # storage id will be obtained
        # As config flow not exists now Currently source ip is mapped with access_info ip address

        # First retrieve access_info from source ip and get storage info using storage id
        filters = {'host': alert['transport_address']}
        access_info = db.access_info_get_all(ctxt, filters=filters)
        if not access_info:
            msg = "Access information could not be found with host %s." % alert['transport_address']
            raise exception.AccessInfoNotFound(message=msg)

        # For given source ip, there should be unique access_info
        if len(access_info) != 1:
            msg = "Failed to get unique access information with host %s." % alert['transport_address']
            raise exception.InvalidResults(message=msg)

        filters = {'id': access_info[0]['storage_id']}
        storages = db.storage_get_all(context, filters=filters)
        if not storages:
            raise exception.StorageNotFound(id=access_info[0]['storage_id'])

        # Fill storage specific info
        alert['storage_id'] = storages[0]['id']
        alert['storage_name'] = storages[0]['name']
        alert['vendor'] = storages[0]['vendor']
        alert['model'] = storages[0]['model']
        alert['location'] = storages[0]['location']

        try:
            alert_model = self.driver_manager.parse_alert(context, storages[0]['id'], alert)
        except Exception as e:
            LOG.error(e)
            raise exception.InvalidResults(message="Failed to fill the alert model from driver.")

        self._export_alert_model(alert_model)

    def _export_alert_model(self, alert_model):
        """Exports the filled alert model to the export manager."""
        LOG.info('Alert model to be exported: %s.', alert_model)

