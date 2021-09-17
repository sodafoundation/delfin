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
periodical task manager for metric collection tasks**
"""
import datetime

import six
from oslo_log import log
from oslo_config import cfg
from apscheduler.schedulers.background import BackgroundScheduler
from oslo_utils import uuidutils

from delfin import context as ctxt
from delfin import manager
from delfin.coordination import ConsistentHashing, GroupMembership
from delfin.task_manager.scheduler import schedule_manager
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import FailedJobHandler
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import JobHandler
from delfin.task_manager import metrics_rpcapi as task_rpcapi
from delfin import db
from oslo_service import service as oslo_ser
from delfin import service


metrics_topic_opts = [
    cfg.IntOpt('process_cleanup_interval',
               default=60,
               help='Background process cleanup call interval in sec'),
    cfg.IntOpt('task_cleanup_delay',
               default=60,
               help='Delay for task cleanup before killing child in sec'),
    cfg.IntOpt('group_change_detect_interval',
               default=30,
               help='Tooz group change detect interval in sec'),
    cfg.IntOpt('max_storages_in_child',
               default=5,
               help='Max storages handled by one child process'),
    cfg.IntOpt('max_childs_in_node',
               default=100000,
               help='Max processes that can be spawned before forcing fail'),
]

CONF = cfg.CONF
CONF.register_opts(metrics_topic_opts)
LOG = log.getLogger(__name__)


class MetricsTaskManager(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(MetricsTaskManager, self).__init__(*args, **kwargs)
        partitioner = ConsistentHashing()
        partitioner.start()
        partitioner.join_group()
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.executor_map = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.watch_job_id = None
        self.cleanup_job_id = None
        self.group = None
        self.watcher = None
        self.schedule_boot_jobs(self.host)

    def stop(self):
        """Cleanup periodic jobs"""
        if self.watch_job_id:
            self.scheduler.remove_job(self.watch_job_id)
        if self.cleanup_job_id:
            self.scheduler.remove_job(self.cleanup_job_id)
        if self.group and self.watcher:
            self.watcher.delete_group(self.group)
        if self.watcher:
            self.watcher.stop()
        self.watch_job_id = None
        self.cleanup_job_id = None
        self.group = None
        self.watcher = None
        self.scheduler.shutdown()

    def on_process_join(self, event):
        LOG.info('Member %s joined the group %s' % (event.member_id,
                                                    event.group_id))
        host = event.group_id.decode('utf-8')
        if self.watcher:
            LOG.info('Processes in current node {0}'
                     .format(self.watcher.get_members(host)))

    def on_process_leave(self, event):
        LOG.info('Member %s left the group %s' % (event.member_id,
                                                  event.group_id))
        executor_topic = event.member_id.decode('utf-8')
        name = executor_topic.split(':')[1]
        if name in self.executor_map.keys():
            host = event.group_id.decode('utf-8')
            LOG.info("Re-create process {0} in {1} that is handling tasks"
                     .format(executor_topic, host))
            launcher = self._create_process(executor_topic, host)
            self.executor_map[name]["launcher"] = launcher
            context = ctxt.get_admin_context()
            for storage in self.executor_map[name]["storages"]:
                for task_id in storage["task_ids"]:
                    LOG.info("Re-scheduling task {0} of storage {1}"
                             .format(task_id, storage["storage_id"]))
                    self.task_rpcapi.assign_job_local(
                        context, task_id, executor_topic)

                for f_task_id in storage["failed_task_ids"]:
                    LOG.info("Re-scheduling failed task {0} of storage {1}"
                             .format(f_task_id, storage["storage_id"]))
                    self.task_rpcapi.assign_failed_job_local(
                        context, f_task_id, executor_topic)

    def schedule_boot_jobs(self, executor):
        """Schedule periodic collection if any task is currently assigned to
        this executor """
        try:
            filters = {'executor': executor,
                       'deleted': False}
            context = ctxt.get_admin_context()
            tasks = db.task_get_all(context, filters=filters)
            failed_tasks = db.failed_task_get_all(context, filters=filters)
            LOG.info("Scheduling boot time jobs for this executor: total "
                     "jobs to be handled :%s" % len(tasks))
            for task in tasks:
                self.assign_job(context, task['id'], executor)
                LOG.debug('Periodic collection job assigned for id: '
                          '%s ' % task['id'])
            for failed_task in failed_tasks:
                self.assign_failed_job(context, failed_task['id'], executor)
                LOG.debug('Failed job assigned for id: '
                          '%s ' % failed_task['id'])

        except Exception as e:
            LOG.error("Failed to schedule boot jobs for this executor "
                      "reason: %s.",
                      six.text_type(e))
        else:
            LOG.debug("Boot job scheduling completed.")

    def _init_watchers(self, group):
        watcher = GroupMembership(agent_id=group)
        watcher.start()
        watcher.create_group(group)
        LOG.info('Created child process membership group {0}.'
                 'Initial members of group: {1}'
                 .format(group, watcher.get_members(group)))

        watcher.register_watcher_func(group,
                                      self.on_process_join,
                                      self.on_process_leave)
        self.group = group
        self.watcher = watcher
        self.watch_job_id = uuidutils.generate_uuid()
        self.scheduler.add_job(watcher.watch_group_change, 'interval',
                               seconds=CONF.group_change_detect_interval,
                               next_run_time=datetime.datetime.now(),
                               id=self.watch_job_id)
        LOG.info('Created watch for group membership change for group {0}.'
                 .format(group))
        self.cleanup_job_id = uuidutils.generate_uuid()
        self.scheduler.add_job(self.process_cleanup, 'interval',
                               seconds=CONF.process_cleanup_interval,
                               next_run_time=datetime.datetime.now(),
                               id=self.cleanup_job_id)
        LOG.info('Created process cleanup background job for group {0}.'
                 .format(group))

    def process_cleanup(self):
        LOG.info('Periodic process cleanup called')
        executor_names = self.executor_map.keys()

        # Collect all names to delete
        names_to_delete = []
        for name in executor_names:
            if len(self.executor_map[name]["storages"]) == 0:
                delay = self.executor_map[name]["cleanup_delay"]
                if delay < 0:
                    LOG.info("Cleanup delay for local executor {0} expired"
                             .format(name))
                    names_to_delete.append(name)
                else:
                    LOG.info("Delay cleanup for local executor {0} for {1}"
                             .format(name, delay))
                    delay = delay - CONF.process_cleanup_interval
                    self.executor_map[name]["cleanup_delay"] = delay
        # Delete names
        for name in names_to_delete:
            self.executor_map[name]["launcher"].stop()
            self.executor_map.pop(name)

    def _create_process(self, topic=None, host=None):
        metrics_task_server = service. \
            MetricsService.create(binary='delfin-task',
                                  topic=topic,
                                  host=host,
                                  manager='delfin.'
                                          'task_manager.'
                                          'metrics_manager.'
                                          'MetricsTaskManagerLocal',
                                  coordination=True)
        launcher = oslo_ser.ProcessLauncher(CONF)
        launcher.launch_service(metrics_task_server, workers=1)
        return launcher

    def _get_local_executor(self, context, task_id, failed_task_id, executor):
        executor_names = self.executor_map.keys()
        task = task_id if task_id else failed_task_id
        job = db.task_get(context, task)
        storage_id = job['storage_id']

        # Return existing executor_topic
        for name in executor_names:
            no_of_storages = len(self.executor_map[name]["storages"])
            if no_of_storages and (no_of_storages <
                                   CONF.max_storages_in_child):
                executor_topic = "{0}:{1}".format(executor, name)
                LOG.info("Selecting existing local executor {0} for task {1}"
                         .format(executor_topic, task))
                storage = None
                for storage_exec in self.executor_map[name]["storages"]:
                    if storage_exec["storage_id"] == storage_id:
                        LOG.info("The storage {0} for task {1} in executor"
                                 .format(storage_id, task))
                        storage = storage_exec
                        break
                if not storage:
                    LOG.info("The storage {0} for task {1} not in executor."
                             " Creating the storage entry in executor."
                             .format(storage_id, task))
                    storage = {
                        "storage_id": storage_id,
                        "task_ids": [],
                        "failed_task_ids": []
                    }
                    self.executor_map[name]["storages"].append(storage)

                if task_id:
                    storage["task_ids"].append(task_id)
                if failed_task_id:
                    storage["failed_task_ids"].append(failed_task_id)
                return executor_topic

        # Return executor_topic after creating one
        for index in range(CONF.max_childs_in_node):
            name = "executor_{0}".format(index + 1)
            if name not in executor_names:
                executor_topic = "{0}:{1}".format(executor, name)
                LOG.info("Create a new local executor {0} for {1}"
                         .format(executor_topic, task))
                launcher = self._create_process(
                    topic=executor_topic, host=executor)
                self.executor_map[name] = {
                    "storages": [],
                    "launcher": None,
                    "cleanup_delay": 0
                }
                storage = {
                    "storage_id": storage_id,
                    "task_ids": [],
                    "failed_task_ids": []
                }
                if task_id:
                    storage["task_ids"].append(task_id)
                if failed_task_id:
                    storage["failed_task_ids"].append(failed_task_id)
                self.executor_map[name]["storages"].append(storage)
                self.executor_map[name]["launcher"] = launcher
                return executor_topic

        msg = "Reached maximum number of ({0}) local executors".\
            format(CONF.max_childs_in_node)
        LOG.error(msg)
        raise RuntimeError(msg)

    def _check_and_stop_executor(self, name, local_executor, storage):
        tasks_count = len(storage["task_ids"])
        failed_tasks_count = len(storage["failed_task_ids"])
        if tasks_count == 0 and failed_tasks_count == 0:
            LOG.info("Stop and remove local executor {0}"
                     .format(local_executor))
            self.executor_map[name]["storages"].remove(storage)
            self.executor_map[name]["cleanup_delay"] = \
                CONF.task_cleanup_delay

    def assign_job(self, context, task_id, executor):
        if not self.watch_job_id:
            self._init_watchers(executor)
        local_executor = self._get_local_executor(
            context, task_id, None, executor)
        self.task_rpcapi.assign_job_local(context, task_id, local_executor)

    def remove_job(self, context, task_id, executor):
        for name in self.executor_map.keys():
            for storage in self.executor_map[name]["storages"]:
                if task_id in storage["task_ids"]:
                    local_executor = "{0}:{1}".format(executor, name)
                    self.task_rpcapi.remove_job_local(
                        context, task_id, local_executor)
                    storage["task_ids"].remove(task_id)
                    return self._check_and_stop_executor(
                        name, local_executor, storage)

    def assign_failed_job(self, context, failed_task_id, executor):
        if not self.watch_job_id:
            self._init_watchers(executor)

        local_executor = self._get_local_executor(
            context, None, failed_task_id, executor)
        self.task_rpcapi.assign_failed_job_local(
            context, failed_task_id, local_executor)

    def remove_failed_job(self, context, failed_task_id, executor):
        for name in self.executor_map.keys():
            for storage in self.executor_map[name]["storages"]:
                if failed_task_id in storage["failed_task_ids"]:
                    local_executor = "{0}:{1}".format(executor, name)
                    self.task_rpcapi.remove_failed_job_local(
                        context, failed_task_id, local_executor)
                    storage["failed_task_ids"].remove(failed_task_id)
                    return self._check_and_stop_executor(
                        name, local_executor, storage)


class MetricsTaskManagerLocal(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(MetricsTaskManagerLocal, self).__init__(*args, **kwargs)

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
