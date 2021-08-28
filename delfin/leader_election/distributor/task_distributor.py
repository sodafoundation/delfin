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


class TaskDistributor(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.task_rpcapi = task_rpcapi.TaskAPI()

        # Reset last run time of tasks to restart scheduling and
        # start the failed task job
        task_list = db.task_get_all(ctx)
        for task in task_list:
            db.task_update(ctx, task['id'], {'last_run_time': None})

    def __call__(self):
        """ Schedule the collection tasks based on interval """

        try:
            # Remove jobs from scheduler when marked for delete
            filters = {'deleted': True}
            tasks = db.task_get_all(self.ctx, filters=filters)
            LOG.debug("Total tasks found deleted "
                      "in this cycle:%s" % len(tasks))
            for task in tasks:
                self.task_rpcapi.remove_job(self.ctx, task['id'],
                                            task['executor'])
        except Exception as e:
            LOG.error("Failed to remove periodic scheduling job , reason: %s.",
                      six.text_type(e))

        try:

            filters = {'last_run_time': None}
            tasks = db.task_get_all(self.ctx, filters=filters)
            LOG.debug("Distributing performance collection jobs: total "
                      "jobs to be handled:%s" % len(tasks))
            for task in tasks:
                # Todo Get executor for the job
                executor = CONF.host
                db.task_update(self.ctx, task['id'], {'executor': executor})
                LOG.info('Assigning executor for collection job for id: '
                         '%s' % task['id'])
                self.task_rpcapi.assign_job(self.ctx, task['id'], executor)

                LOG.debug('Periodic collection job assigned for id: '
                          '%s ' % task['id'])
        except Exception as e:
            LOG.error("Failed to distribute periodic collection, reason: %s.",
                      six.text_type(e))
        else:
            LOG.debug("Periodic job distribution completed.")

    def distribute_new_job(self, task_id):
        executor = CONF.host
        try:
            db.task_update(self.ctx, task_id, {'executor': executor})
            LOG.info('Distribute a new job, id: %s' % task_id)
            self.task_rpcapi.assign_job(self.ctx, task_id, executor)
        except Exception as e:
            LOG.error('Failed to distribute the new job, reason: %s',
                      six.text_type(e))

    @classmethod
    def job_interval(cls):
        return TelemetryCollection.PERIODIC_JOB_INTERVAL
