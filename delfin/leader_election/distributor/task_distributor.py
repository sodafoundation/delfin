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
from delfin.coordination import ConsistentHashing
from delfin.task_manager import metrics_rpcapi as task_rpcapi

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class TaskDistributor(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.task_rpcapi = task_rpcapi.TaskAPI()

    def distribute_new_job(self, task_id):
        partitioner = ConsistentHashing()
        partitioner.start()
        executor = partitioner.get_task_executor(task_id)
        try:
            db.task_update(self.ctx, task_id, {'executor': executor})
            LOG.info('Distribute a new job, id: %s' % task_id)
            self.task_rpcapi.assign_job(self.ctx, task_id, executor)
        except Exception as e:
            LOG.error('Failed to distribute the new job, reason: %s',
                      six.text_type(e))
            raise e

    def distribute_failed_job(self, failed_task_id, executor):

        try:
            db.failed_task_update(self.ctx, failed_task_id,
                                  {'executor': executor})
            LOG.info('Distribute a failed job, id: %s' % failed_task_id)
            self.task_rpcapi.assign_failed_job(self.ctx, failed_task_id,
                                               executor)
        except Exception as e:
            LOG.error('Failed to distribute failed job, reason: %s',
                      six.text_type(e))
            raise e
