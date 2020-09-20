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

from oslo_config import cfg
from oslo_log import log
from delfin import context
from delfin.api.common import wsgi
from delfin.common import constants
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.tasks import resources

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class PerformanceController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.task_rpcapi = task_rpcapi.TaskAPI()

    def perf_collect(self, storage_id, interval, is_historic, resource):
        """
        This function received the request from scheduler to create tasks
        and push those tasks to rabbitmq.
        :param storage_id: The registered storage_id
        :param interval: collection interval period
        :param is_historic: to enable historic collection
        :param resource: resource type, ex: array, pool, volume etc.
        :return:
        """
        ctxt = context.RequestContext()

        LOG.debug("Request received to create perf_collect task for storage_"
                  "id :{0} and resource_type:{1}".format(storage_id, resource)
                  )

        self.task_rpcapi.performance_metrics_collection(
            ctxt, storage_id, interval, is_historic,
            resources.PerformanceCollectionTask.__module__ +
            '.' + constants.RESOURCE_CLASS_TYPE.get(resource))


def create_resource():
    return wsgi.Resource(PerformanceController())
