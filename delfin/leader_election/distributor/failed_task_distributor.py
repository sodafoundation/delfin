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

from delfin import db
from delfin.common.constants import TelemetryCollection
from delfin.task_manager import metrics_rpcapi as task_rpcapi

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class FailedTaskDistributor(object):
    def __init__(self, ctx):
        # create the object of periodic scheduler
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.ctx = ctx

    def __call__(self):
        """
        :return:
        """

        try:
            # Remove jobs from scheduler when marked for delete
            filters = {'deleted': True}
            failed_tasks = db.failed_task_get_all(self.ctx, filters=filters)
            LOG.debug("Total failed_tasks found deleted "
                      "in this cycle:%s" % len(failed_tasks))
            for failed_task in failed_tasks:
                self.task_rpcapi.remove_failed_job(self.ctx, failed_task['id'],
                                                   failed_task['executor'])
        except Exception as e:
            LOG.error("Failed to remove periodic scheduling job , reason: %s.",
                      six.text_type(e))
        try:
            # Create the object of periodic scheduler
            failed_tasks = db.failed_task_get_all(self.ctx)

            for failed_task in failed_tasks:
                # Todo Get executor for the job
                # update task table with executor topic

                LOG.debug('Assigning failed task for for id: '
                          '%s' % failed_task['id'])
                self.task_rpcapi.assign_failed_job(self.ctx, failed_task['id'],
                                                   failed_task['executor'])

                LOG.info('Assigned failed task for  id: '
                         '%s ' % failed_task['id'])
        except Exception as e:
            LOG.error("Failed to schedule retry tasks for performance "
                      "collection, reason: %s", six.text_type(e))
        else:
            LOG.info("Schedule collection completed")

    @classmethod
    def job_interval(cls):
        return TelemetryCollection.FAILED_JOB_SCHEDULE_INTERVAL
