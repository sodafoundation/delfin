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

from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime
import six

from oslo_log import log
from oslo_config import cfg
from oslo_utils import uuidutils
from oslo_service import service as oslo_ser

from delfin import context as ctxt
from delfin.coordination import ConsistentHashing, GroupMembership
from delfin import db
from delfin import exception
from delfin import manager
from delfin import service
from delfin.task_manager.scheduler import schedule_manager
from delfin.task_manager import subprocess_rpcapi as rpcapi
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import FailedJobHandler
from delfin.task_manager.scheduler.schedulers.telemetry.job_handler \
    import JobHandler

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class MetricsTaskManager(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(MetricsTaskManager, self).__init__(*args, **kwargs)
        scheduler = schedule_manager.SchedulerManager()
        scheduler.start()
        partitioner = ConsistentHashing()
        partitioner.start()
        partitioner.join_group()
        self.watch_job_id = None
        self.cleanup_job_id = None
        self.group = None
        self.watcher = None
        self.scheduler = None
        self.rpcapi = rpcapi.SubprocessAPI()
        self.executor_map = {}
        self.enable_sub_process = CONF.telemetry.enable_dynamic_subprocess
        if self.enable_sub_process:
            self.scheduler = BackgroundScheduler()
            self.scheduler.start()
        self.schedule_boot_jobs(self.host)

    def assign_job(self, context, task_id, executor):
        if not self.enable_sub_process:
            instance = JobHandler.get_instance(context, task_id)
            instance.schedule_job(task_id)
        else:
            if not self.watch_job_id:
                self.init_watchers(executor)
            local_executor = self.get_local_executor(
                context, task_id, None, executor)
            self.rpcapi.assign_job_local(context, task_id, local_executor)

    def remove_job(self, context, task_id, executor):
        if not self.enable_sub_process:
            instance = JobHandler.get_instance(context, task_id)
            instance.remove_job(task_id)
        else:
            job = db.task_get(context, task_id)
            storage_id = job['storage_id']
            for name in self.executor_map.keys():
                if storage_id in self.executor_map[name]["storages"]:
                    local_executor = "{0}:{1}".format(executor, name)
                    self.rpcapi.remove_job_local(
                        context, task_id, local_executor)
                    tasks, failed_tasks = self.get_all_tasks(storage_id)
                    if len(failed_tasks) == 0 and len(tasks) == 0:
                        self.stop_executor(name, local_executor, storage_id)

    def assign_failed_job(self, context, failed_task_id, executor):
        if not self.enable_sub_process:
            instance = FailedJobHandler.get_instance(context, failed_task_id)
            instance.schedule_failed_job(failed_task_id)
        else:
            if not self.watch_job_id:
                self.init_watchers(executor)

            local_executor = self.get_local_executor(
                context, None, failed_task_id, executor)
            self.rpcapi.assign_failed_job_local(
                context, failed_task_id, local_executor)

    def remove_failed_job(self, context, failed_task_id, executor):
        if not self.enable_sub_process:
            instance = FailedJobHandler.get_instance(context, failed_task_id)
            instance.remove_failed_job(failed_task_id)
        else:
            job = db.failed_task_get(context, failed_task_id)
            storage_id = job['storage_id']
            for name in self.executor_map.keys():
                if storage_id in self.executor_map[name]["storages"]:
                    local_executor = "{0}:{1}".format(executor, name)
                    self.rpcapi.remove_failed_job_local(
                        context, failed_task_id, local_executor)
                    tasks, failed_tasks = self.get_all_tasks(storage_id)
                    if len(failed_tasks) == 0 and len(tasks) == 0:
                        self.stop_executor(name, local_executor, storage_id)

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

    def init_watchers(self, group):
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
                               seconds=CONF.telemetry.
                               group_change_detect_interval,
                               next_run_time=datetime.datetime.now(),
                               id=self.watch_job_id,
                               misfire_grace_time=int(
                                   CONF.telemetry.
                                   group_change_detect_interval / 2))
        LOG.info('Created watch for group membership change for group {0}.'
                 .format(group))
        self.cleanup_job_id = uuidutils.generate_uuid()
        self.scheduler.add_job(self.process_cleanup, 'interval',
                               seconds=CONF.telemetry.process_cleanup_interval,
                               next_run_time=datetime.datetime.now(),
                               id=self.cleanup_job_id,
                               misfire_grace_time=int(
                                   CONF.telemetry.
                                   process_cleanup_interval / 2))
        LOG.info('Created process cleanup background job for group {0}.'
                 .format(group))

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
            launcher = self.create_process(executor_topic, host)
            self.executor_map[name]["launcher"] = launcher
            context = ctxt.get_admin_context()
            for storage_id in self.executor_map[name]["storages"]:
                tasks, failed_tasks = self.get_all_tasks(storage_id)
                for task in tasks:
                    LOG.info("Re-scheduling task {0} of storage {1}"
                             .format(task['id'], storage_id))
                    self.rpcapi.assign_job_local(
                        context, task['id'], executor_topic)

                for f_task in failed_tasks:
                    LOG.info("Re-scheduling failed failed task {0},"
                             " of storage {1}"
                             .format(f_task['id'], storage_id))
                    self.rpcapi.assign_failed_job_local(
                        context, f_task['id'], executor_topic)

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
                    delay = delay - CONF.telemetry.process_cleanup_interval
                    self.executor_map[name]["cleanup_delay"] = delay
        # Delete names
        for name in names_to_delete:
            self.executor_map[name]["launcher"].stop()
            self.executor_map.pop(name)

    def create_process(self, topic=None, host=None):
        metrics_task_server = service. \
            MetricsService.create(binary='delfin-task',
                                  topic=topic,
                                  host=host,
                                  manager='delfin.'
                                          'task_manager.'
                                          'subprocess_manager.'
                                          'SubprocessManager',
                                  coordination=False)
        launcher = oslo_ser.ProcessLauncher(CONF)
        launcher.launch_service(metrics_task_server, workers=1)
        return launcher

    def get_local_executor(self, context, task_id, failed_task_id, executor):
        executor_names = self.executor_map.keys()
        storage_id = None
        if task_id:
            job = db.task_get(context, task_id)
            storage_id = job['storage_id']
        elif failed_task_id:
            job = db.failed_task_get(context, failed_task_id)
            storage_id = job['storage_id']
        else:
            raise exception.InvalidInput("Missing task id")

        # Storage already exists
        for name in executor_names:
            executor_topic = "{0}:{1}".format(executor, name)
            if storage_id in self.executor_map[name]["storages"]:
                return executor_topic

        # Return existing executor_topic
        for name in executor_names:
            no_of_storages = len(self.executor_map[name]["storages"])
            if no_of_storages and (no_of_storages <
                                   CONF.telemetry.max_storages_in_child):
                executor_topic = "{0}:{1}".format(executor, name)
                LOG.info("Selecting existing local executor {0} for {1}"
                         .format(executor_topic, storage_id))
                self.executor_map[name]["storages"].append(storage_id)
                return executor_topic

        # Return executor_topic after creating one
        for index in range(CONF.telemetry.max_childs_in_node):
            name = "executor_{0}".format(index + 1)
            if name not in executor_names:
                executor_topic = "{0}:{1}".format(executor, name)
                LOG.info("Create a new local executor {0} for {1}"
                         .format(executor_topic, storage_id))
                launcher = self.create_process(
                    topic=executor_topic, host=executor)
                time.sleep(10)
                self.executor_map[name] = {
                    "storages": [storage_id],
                    "launcher": launcher,
                    "cleanup_delay": 0
                }
                return executor_topic

        msg = "Reached maximum number of ({0}) local executors". \
            format(CONF.telemetry.max_childs_in_node)
        LOG.error(msg)
        raise RuntimeError(msg)

    def get_all_tasks(self, storage_id):
        filters = {'storage_id': storage_id,
                   'deleted': False}
        context = ctxt.get_admin_context()
        tasks = db.task_get_all(context, filters=filters)
        failed_tasks = db.failed_task_get_all(context, filters=filters)
        return tasks, failed_tasks

    def stop_executor(self, name, local_executor, storage_id):
        LOG.info("Stop and remove local executor {0}"
                 .format(local_executor))
        if storage_id in self.executor_map[name]["storages"]:
            self.executor_map[name]["storages"].remove(storage_id)
        self.executor_map[name]["cleanup_delay"] = \
            CONF.telemetry.task_cleanup_delay

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
        if self.scheduler:
            self.scheduler.shutdown()
        self.watch_job_id = None
        self.cleanup_job_id = None
        self.group = None
        self.watcher = None
