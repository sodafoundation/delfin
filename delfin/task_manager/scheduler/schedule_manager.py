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

from datetime import datetime

import six
from oslo_config import cfg
from oslo_log import log
from oslo_utils import uuidutils

from delfin import context
from delfin.common import constants
from delfin.task_manager.scheduler import scheduler
from delfin.task_manager.scheduler.schedulers.telemetry import telemetry_job

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class SchedulerManager(object):
    def __init__(self):
        self.schedule_instance = scheduler.Scheduler.get_instance()

    def start(self):
        """ Initialise the schedulers for periodic job creation
        """
        ctxt = context.get_admin_context()
        try:

            # Create a jobs for periodic scheduling
            periodic_scheduler_job_id = uuidutils.generate_uuid()
            self.schedule_instance.add_job(
                telemetry_job.TelemetryJob(ctxt), 'interval', args=[ctxt],
                seconds=constants.TelemetryCollection.PERIODIC_JOB_INTERVAL,
                next_run_time=datetime.now(),
                id=periodic_scheduler_job_id)
        except Exception as e:
            LOG.error("Failed to initialize periodic tasks, reason: %s.",
                      six.text_type(e))
        else:
            # start the scheduler
            self.schedule_instance.start()
