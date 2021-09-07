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

import abc

import six
from oslo_log import log

from delfin import context, db
from delfin.common.constants import TelemetryTaskStatus
from delfin.drivers import api as driver_api
from delfin.exporter import base_exporter
from delfin.i18n import _

LOG = log.getLogger(__name__)


class TelemetryTask(object):
    @abc.abstractmethod
    def collect(self, ctx, storage_id, args, start_time, end_time):
        pass

    @abc.abstractmethod
    def remove_telemetry(self, ctx, storage_id):
        pass


class PerformanceCollectionTask(TelemetryTask):
    def __init__(self):
        self.driver_api = driver_api.API()
        self.perf_exporter = base_exporter.PerformanceExporterManager()

    def collect(self, ctx, storage_id, args, start_time, end_time):
        try:
            LOG.debug("Performance collection for storage [%s] with start time"
                      " [%s] and end time [%s]"
                      % (storage_id, start_time, end_time))
            perf_metrics = self.driver_api \
                .collect_perf_metrics(ctx, storage_id,
                                      args,
                                      start_time, end_time)

            # Fill extra labels to metric by fetching metadata from resource DB
            try:
                storage_details = db.storage_get(ctx, storage_id)
                for m in perf_metrics:
                    m.labels["name"] = storage_details.name
                    m.labels["serial_number"] = storage_details.serial_number
            except Exception as e:
                msg = _('Failed to add extra labels to performance '
                        'metrics: {0}'.format(e))
                LOG.error(msg)
                return TelemetryTaskStatus.TASK_EXEC_STATUS_FAILURE

            self.perf_exporter.dispatch(context, perf_metrics)
            return TelemetryTaskStatus.TASK_EXEC_STATUS_SUCCESS
        except Exception as e:
            LOG.error("Failed to collect performance metrics for "
                      "storage id :{0}, reason:{1}".format(storage_id,
                                                           six.text_type(e)))
            return TelemetryTaskStatus.TASK_EXEC_STATUS_FAILURE


