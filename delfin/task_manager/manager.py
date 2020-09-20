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
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from oslo_config import cfg
from oslo_log import log
from oslo_utils import importutils
from delfin.common import constants, config
from delfin import manager, exception
from delfin.api.v1.performance import PerformanceController
from delfin.drivers import manager as driver_manager
from delfin.task_manager.tasks import alerts

LOG = log.getLogger(__name__)
CONF = cfg.CONF

scheduler_opts = [
    cfg.StrOpt('config_path', default='scheduler',
               help='The config path for scheduler'),
]

CONF.register_opts(scheduler_opts, "scheduler")


class TaskManager(manager.Manager):
    """manage periodical tasks"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        self.alert_sync = alerts.AlertSyncTask()
        super(TaskManager, self).__init__(*args, **kwargs)

    def periodic_performance_collect(self):
        """
        """
        try:
            # Load the scheduler configuration file
            data = config.load_json_file(CONF.scheduler.config_path)

            # create the object of periodic scheduler
            schedule = BackgroundScheduler()

            # create the objet to StorageController class, so that
            # methods of that class can be called by scheduler
            storage_cls = PerformanceController()

            # parse the scheduler configuration file and start the task
            # for each storage
            for storage in data.get("storages"):
                storage_id = storage.get('id')

                for resource in storage.keys():
                    if resource == 'id':
                        continue

                    resource_type = storage.get(resource)
                    if (resource_type.get('perf_collection') and
                            resource_type.get('interval') > constants.
                            SCHEDULING_MIN_INTERVAL):
                        is_historic = resource_type.get('is_historic')
                        interval = resource_type.get('interval')

                        # add the task to scheduler(basically, it calls the
                        # perf_collect method from PerformanceController class
                        # ) and execute the task immediate and after every
                        # interval
                        schedule.add_job(
                            storage_cls.perf_collect, 'interval', args=[
                                storage_id, interval, is_historic, resource],
                            seconds=interval,
                            next_run_time=datetime.now(), id="pravin1")

        except TypeError as e:
            LOG.error("Error occurred during parsing of config file")
            raise exception.InvalidContentType(e)
        else:
            # start the scheduler
            schedule.start()
            print("get_manager_all_jobs=:", schedule.get_jobs())

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
                                       is_historic, resource_task):
        LOG.debug("Received the performance collection task: {0} request"
                  "for storage_id:{1}".format(resource_task, storage_id))
        cls = importutils.import_class(resource_task)
        device_obj = cls(context, storage_id, interval, is_historic)
        device_obj.collect()
