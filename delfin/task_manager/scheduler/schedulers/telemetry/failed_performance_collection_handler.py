# Copyright 2021 The SODA Authors.
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
from oslo_config import cfg
from oslo_log import log

from delfin.drivers import api as driver_api
from delfin.exporter import base_exporter
from delfin.i18n import _
from delfin.task_manager.scheduler import scheduler

CONF = cfg.CONF

telemetry_opts = [
    cfg.IntOpt('max_failed_task_retry_count', default=5,
               help='default value (in integer) for maximum number of retries '
                    'for failed task execution'),
]
CONF.register_opts(telemetry_opts)
LOG = log.getLogger(__name__)


class FailedPerformanceCollectionHandler(object):
    def __init__(self, storage_id, args, task_id,
                 job_id, start_time, end_time):
        self.retry_count = 0
        self.storage_id = storage_id
        self.task_id = task_id
        self.job_id = job_id
        self.args = args
        self.start_time = start_time
        self.end_time = end_time
        self.driver_api = driver_api.API()
        self.perf_exporter = base_exporter.PerformanceExporterManager()
        self.scheduler_instance = scheduler.Scheduler.get_instance()

    def __call__(self, ctx):
        # pull performance collection info
        try:
            perf_metrics = self.driver_api \
                .collect_perf_metrics(ctx, self.storage_id,
                                      self.args,
                                      self.start_time, self.end_time)

            self.perf_exporter.dispatch(ctx, perf_metrics)
        except Exception as e:
            LOG.error(e)
            msg = _("Failed to collect performance metrics for storage "
                    "id:{0}, reason:{1}".format(self.storage_id,
                                                six.text_type(e)))
            LOG.error(msg)
        else:
            LOG.info("Successfully completed Performance metrics collection "
                     "for storage id :{0} ".format(self.storage_id))
            self._clean_failed_task()
            return

        if self.retry_count >= CONF.TELEMETRY.max_failed_task_retry_count:
            msg = _(
                "Failed to collect performance metrics of task instance "
                "id:{0} for start time:{1} and end time:{2} with "
                "maximum retry. Giving up on "
                "retry".format(self.task_id, self.start_time,
                               self.end_time))
            LOG.error(msg)
            self._clean_failed_task()
            return

        self.retry_count = self.retry_count + 1

    def _clean_failed_task(self):
        self.scheduler_instance.pause_job(self.job_id)
