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
"""

**periodical task manager**

"""
import json
import time

import schedule
from oslo_config import cfg
from oslo_log import log
from oslo_utils import importutils

from delfin import manager, exception
from delfin.drivers import manager as driver_manager
from delfin.task_manager.tasks import alerts
from delfin.api.v1.storages import StorageController

LOG = log.getLogger(__name__)
CONF = cfg.CONF
# CONF.import_opt('periodic_interval', 'delfin.service')

scheduler_opts = [
    cfg.StrOpt('config_path',
               default='scheduler',
               help='The scheduler configuration file'),
]

CONF.register_opts(scheduler_opts, "scheduler")

RUN_IMMEDIATE = 0


class TaskManager(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        self.alert_sync = alerts.AlertSyncTask()
        super(TaskManager, self).__init__(*args, **kwargs)

    def _run_scheduler(self, interval, storage_id, is_history, resource,
                       tag=''):
        schedule_obj = StorageController()
        schedule.every(interval).seconds.do(
            schedule_obj.perf_collect, storage_id, interval,
            is_history, resource).tag(tag)

        if tag:
            schedule.run_pending()
            schedule.clear(tag)

    def periodic_performance_collect(self):
        LOG.info("Scheduled perf-sync operation starting.")
        try:
            with open(CONF.scheduler.config_path) as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise exception.ConfigNotFound(e)

        for (item, storage) in data.items():
            storage_id = storage.get('id')
            for resource in storage.keys():

                if resource == "id":
                    continue

                resource_type = storage.get(resource)
                if (resource_type.get('perf_collection') and
                        resource_type.get('interval') > 5):
                    is_history = resource_type.get('history_collection')
                    interval = resource_type.get('interval')

                    # run immediately
                    self._run_scheduler(RUN_IMMEDIATE, storage_id, is_history,
                                        resource, 'RUN_IMMEDIATE')
                    # run with interval
                    self._run_scheduler(interval, storage_id, is_history,
                                        resource)

        while True:
            schedule.run_pending()

    def sync_storage_resource(self, context, storage_id, resource_task):
        LOG.debug("Received the sync_storage task: {0} request for storage"
                  " id:{1}".format(resource_task, storage_id))
        cls = importutils.import_class(resource_task)
        device_obj = cls(context, storage_id)
        device_obj.sync()

    def remove_storage_resource(self, context, storage_id, resource_task):
        cls = importutils.import_class(resource_task)
        device_obj = cls(context, storage_id)
        device_obj.remove()

    def remove_storage_in_cache(self, context, storage_id):
        LOG.info('Remove storage device in memory for storage id:{0}'
                 .format(storage_id))
        drivers = driver_manager.DriverManager()
        drivers.remove_driver(storage_id)

    def sync_storage_alerts(self, context, storage_id, query_para):
        LOG.info('Alert sync called for storage id:{0}'
                 .format(storage_id))
        self.alert_sync.sync_alerts(context, storage_id, query_para)

    def performance_metrics_collection(self, context, storage_id, interval,
                                       is_history, resource_task):
        LOG.debug("Received the performance collection task: {0} request"
                  "for storage_id:{1}".format(resource_task, storage_id))
        cls = importutils.import_class(resource_task)
        device_obj = cls(context, storage_id, interval, is_history)
        device_obj.collect()
