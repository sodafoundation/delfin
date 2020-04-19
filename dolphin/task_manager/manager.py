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
from dolphin import coordination
from dolphin import context
from dolphin.db.sqlalchemy import api
from dolphin.driver_manager import manager as dm

LOG = log.getLogger(__name__)
CONF = cfg.CONF
CONF.import_opt('periodic_interval', 'dolphin.service')


class TaskManager(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        super(TaskManager, self).__init__(*args, **kwargs)
        self.task_rpcapi = task_rpcapi.TaskAPI()

    """Periodical task, this task will use coordination for distribute synchronization."""

    @periodic_task.periodic_task(spacing=2, run_immediately=True)
    @coordination.synchronized('lock-task-example')
    def _task_example(self, context):
        LOG.info("Produce task, say hello ...")
        self.task_rpcapi.say_hello(context)

    def say_hello(self, context, request_spec=None,
                  filter_properties=None):
        try:
            LOG.info("Consume say hello task ...")
        except Exception as ex:
            pass

    @periodic_task.periodic_task(spacing=15, run_immediately=True)
    @coordination.synchronized('lock-task-example')
    def periodic_pool_task(self, context):
        if api.get_registered_device_list():
            device_list = api.get_registered_device_list()
            for device in device_list:
                self.task_rpcapi.pool_storage(context, device)

    @periodic_task.periodic_task(spacing=5, run_immediately=True)
    @coordination.synchronized('lock-task-example')
    def periodic_volume_task(self, context):
        if api.get_registered_device_list():
            device_list = api.get_registered_device_list()
            for device in device_list:
                self.task_rpcapi.volume_storage(context, device)

    def volume_storage(self, context, request_spec=None, filter_properties=None):
        # 1. Call the list volumes
        try:
            obj = dm.Driver()
            obj.list_volumes(context, request_spec)
            LOG.info("%s Volume", request_spec)
        except Exception as ex:
            print "In volume exception. Please handle it"
            pass

        # 2. Update the data to DB

    def pool_storage(self, context, request_spec=None, filter_properties=None):
        # 1. call the list pool
        try:
            obj = dm.Driver()
            obj.list_pools(context, request_spec)
            LOG.info("%s pool", request_spec)
        except Exception as ex:
            print "In pool exception. Please handle it"
            pass

        # 2. Update to the DB