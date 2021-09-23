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
Subprocess metrics manager for metric collection tasks**
"""

from oslo_log import log
from oslo_config import cfg

from delfin.coordination import GroupMembership
from delfin import manager
from delfin.task_manager.scheduler import schedule_manager
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import FailedJobHandler
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import JobHandler


CONF = cfg.CONF
LOG = log.getLogger(__name__)


class SubprocessManager(manager.Manager):
    """manage periodical collection tasks in subprocesses"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(SubprocessManager, self).__init__(*args, **kwargs)

    def init_scheduler(self, topic, host):
        scheduler = schedule_manager.SchedulerManager()
        scheduler.start()
        watcher = GroupMembership(topic)
        watcher.start()
        watcher.join_group(host)

    def assign_job_local(self, context, task_id):
        instance = JobHandler.get_instance(context, task_id)
        instance.schedule_job(task_id)

    def remove_job_local(self, context, task_id):
        instance = JobHandler.get_instance(context, task_id)
        instance.remove_job(task_id)

    def assign_failed_job_local(self, context, failed_task_id):
        instance = FailedJobHandler.get_instance(context, failed_task_id)
        instance.schedule_failed_job(failed_task_id)

    def remove_failed_job_local(self, context, failed_task_id):
        instance = FailedJobHandler.get_instance(context, failed_task_id)
        instance.remove_failed_job(failed_task_id)
