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
import json

from oslo_config import cfg
from oslo_log import log
from delfin import db
from delfin import context, exception
from delfin.api.common import wsgi
from delfin.common import constants, config
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.tasks import resources
from delfin.api import validation
from delfin.api.schemas import perf_collection
from datetime import datetime

LOG = log.getLogger(__name__)
CONF = cfg.CONF

scheduler_opts = [
    cfg.StrOpt('config_path', default='scheduler',
               help='The config path for scheduler'),
]

CONF.register_opts(scheduler_opts, "scheduler")


class PerformanceController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.task_rpcapi = task_rpcapi.TaskAPI()

    @validation.schema(perf_collection.update)
    def metrics_config(self, req, body, id):
        """
        :param req:
        :param body:
        :param id:
        :return:
        """
        ctxt = req.environ['delfin.context']

        # check storage is registered
        db.storage_get(ctxt, id)

        metrics_config_dict = body
        metrics_config_dict.update(body)

        # get scheduler object
        schedule = config.Scheduler.getInstance()

        # The path of scheduler config file
        config_file = CONF.scheduler.config_path

        try:
            # Load the scheduler configuration file
            data = config.load_json_file(config_file)
            storage_found = False
            for storage in data.get("storages"):
                config_storage_id = storage.get('id')
                if config_storage_id == id:
                    for resource in metrics_config_dict.keys():
                        storage_dict = storage.get(resource)
                        metric_dict = metrics_config_dict.get(resource)
                        storage_dict.update(metric_dict)

                        interval = storage_dict.get('interval')
                        is_historic = storage_dict.get('is_historic')

                        job_id = id + resource

                        if schedule.get_job(job_id):
                            schedule.reschedule_job(
                                job_id=job_id, trigger='interval',
                                seconds=interval)
                        else:
                            schedule.add_job(
                                self.perf_collect, 'interval', args=[
                                    id, interval, is_historic, resource],
                                seconds=interval,
                                next_run_time=datetime.now(), id=job_id)

                        storage_found = True

            if not storage_found:
                temp_dict = {'id': id}
                temp_dict.update(metrics_config_dict)
                data.get("storages").append(temp_dict)

                for resource in metrics_config_dict.keys():
                    resource_dict = metrics_config_dict.get(resource)
                    interval = resource_dict.get('interval')
                    is_historic = resource_dict.get('is_historic')

                    job_id = id + resource

                    schedule.add_job(
                        self.perf_collect, 'interval', args=[
                            id, interval, is_historic, resource],
                        seconds=interval, next_run_time=datetime.now(),
                        id=job_id)

            with open(config_file, "w") as jsonFile:
                json.dump(data, jsonFile)
                jsonFile.close()

        except TypeError as e:
            LOG.error("Error occurred during parsing of config file")
            raise exception.InvalidContentType(e)
        except json.decoder.JSONDecodeError as e:
            msg = ("Not able to open the config file: {0}"
                   .format(config_file))
            LOG.error(msg)
            raise exception.InvalidInput(e.msg)
        else:
            return metrics_config_dict

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
