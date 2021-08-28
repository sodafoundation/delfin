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

"""
Client side of the metrics task manager RPC API.
"""

import oslo_messaging as messaging
from oslo_config import cfg
from oslo_log import log

from delfin import rpc
from delfin import db
from delfin import exception
from delfin.common import constants

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class PerfJobManager(object):
    """Client side of the metrics task rpc API.

    API version history:

        1.0 - Initial version.
    """

    RPC_API_VERSION = '1.0'

    def __init__(self):
        pass
        self.target = messaging.Target(topic=CONF.host,
                                       version=self.RPC_API_VERSION)
        self.client = rpc.get_client(self.target,
                                     version_cap=self.RPC_API_VERSION)

    def get_client(self, topic):
        target = messaging.Target(topic=topic,
                                  version=self.RPC_API_VERSION)
        return rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    def create_perf_job(self, context, storage_id, capabilities):
        # Add it to db
        # Check resource_metric attribute availability and
        # check if resource_metric is empty
        if 'resource_metrics' not in capabilities \
                or not bool(capabilities.get('resource_metrics')):
            raise exception.EmptyResourceMetrics()

        task = dict()
        task.update(storage_id=storage_id)
        task.update(args=capabilities.get('resource_metrics'))
        task.update(interval=CONF.telemetry.performance_collection_interval)
        task.update(method=
                    constants.TelemetryCollection.PERFORMANCE_TASK_METHOD)
        db.task_create(context=context, values=task)
        # Add it to RabbitMQ
        filters = {'storage_id': storage_id}
        task_id = db.task_get_all(context, filters=filters)[0].get('id')
        LOG.info('ly>>>>>>task_id is %s' % task_id)
        call_context = self.client.prepare(version='1.0')
        return call_context.cast(context,
                                 'add_new_job',
                                 task_id=task_id)

    def remove_perf_job(self, context, task_id, executor):
        pass
