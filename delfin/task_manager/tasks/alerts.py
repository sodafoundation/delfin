# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import six
from oslo_log import log

from delfin import db
from delfin.common import alert_util
from delfin.drivers import api as driver_manager
from delfin.exporter import base_exporter
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertSyncTask(object):

    def __init__(self):
        self.driver_manager = driver_manager.API()
        self.alert_export_manager = base_exporter.AlertExporterManager()

    def sync_alerts(self, ctx, storage_id, query_para):
        """ Syncs all alerts from storage side to exporter """

        LOG.info('Syncing alerts for storage id:{0}'.format(storage_id))
        try:
            storage = db.storage_get(ctx, storage_id)

            current_alert_list = self.driver_manager.list_alerts(ctx,
                                                                 storage_id,
                                                                 query_para)
            if not len(current_alert_list):
                # No alerts to sync
                LOG.info('No alerts to sync from storage device for '
                         'storage id:{0}'.format(storage_id))
                return

            for alert in current_alert_list:
                alert_util.fill_storage_attributes(alert, storage)
            self.alert_export_manager.dispatch(ctx, current_alert_list)
            LOG.info('Syncing storage alerts successful for storage id:{0}'
                     .format(storage_id))
        except Exception as e:
            msg = _('Failed to sync alerts from storage device: {0}'
                    .format(six.text_type(e)))
            LOG.error(msg)
