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
from oslo_log import log

from delfin import db
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.tasks import telemetry

LOG = log.getLogger(__name__)


class PerformanceCollectionHandler(object):
    def __init__(self):
        self.task_rpcapi = task_rpcapi.TaskAPI()

    def __call__(self, ctx, task_id):
        # Handles performance collection from driver and dispatch
        try:
            task = db.task_get(ctx, task_id)
            LOG.debug('Collecting performance metrics for task id: %s'
                      % task['id'])
            current_time = int(datetime.utcnow().timestamp())
            db.task_update(ctx, task_id, {'last_run_time': current_time})

            # Times are epoch time in miliseconds
            end_time = current_time * 1000
            start_time = end_time - (task['interval'] * 1000)
            self.task_rpcapi.collect_telemetry(ctx, task['storage_id'],
                                               telemetry.TelemetryTask.
                                               __module__ + '.' +
                                               'PerformanceCollectionTask',
                                               task['args'],
                                               start_time, end_time)
        except Exception as e:
            LOG.error("Failed to collect performance metrics for "
                      "task id :{0}, reason:{1}".format(task_id,
                                                        six.text_type(e)))
        else:
            LOG.debug("Performance collection done for storage id :{0}"
                      ",task id :{1} and interval(in sec):{2}"
                      .format(task['storage_id'], task_id, task['interval']))
