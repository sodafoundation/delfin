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
from oslo_log import log

from delfin import manager
from delfin.leader_election.distributor import task_distributor

LOG = log.getLogger(__name__)


class PerfJobManager(manager.Manager):
    """Generate job to job distributor"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(PerfJobManager, self).__init__(*args, **kwargs)

    def add_new_job(self, context, task_id):
        distributor = task_distributor.TaskDistributor(context)
        distributor.distribute_new_job(task_id)
