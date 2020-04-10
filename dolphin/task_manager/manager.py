# Copyright (c) 2014 NetApp Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""

**periodical task manager**

"""

from oslo_config import cfg
from oslo_log import log
from oslo_service import periodic_task

from dolphin import manager
from dolphin.task_manager import rpcapi as task_rpcapi

LOG = log.getLogger(__name__)
CONF = cfg.CONF
CONF.import_opt('periodic_interval', 'dolphin.service')


class TaskManager(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(TaskManager, self).__init__(*args, **kwargs)
        self.task_rpcapi = task_rpcapi.TaskAPI()

    @periodic_task.periodic_task(spacing=2, run_immediately=True)
    def _task_example(self, context):
        LOG.debug("task example ...")
        self.task_rpcapi.say_hello()
