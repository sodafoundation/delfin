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
Client side of the metrics task manager RPC API.
"""

from oslo_config import cfg
from oslo_log import log

from delfin import db
from delfin import exception
from delfin.common import constants
from delfin.task_manager import metrics_rpcapi

LOG = log.getLogger(__name__)
CONF = cfg.CONF


def create_perf_job(context, storage_id, capabilities):
    # Add it to db
    # Check resource_metric attribute availability and
    # check if resource_metric is empty
    if 'resource_metrics' not in capabilities \
            or not bool(capabilities.get('resource_metrics')):
        raise exception.EmptyResourceMetrics()

    task = dict()
    task.update(storage_id=storage_id)
    task.update(args=capabilities.get('resource_metrics'))
    task.update(interval=capabilities.get('collect_interval')
                if capabilities.get('collect_interval')
                else CONF.telemetry.performance_collection_interval)
    task.update(method=constants.TelemetryCollection.PERFORMANCE_TASK_METHOD)
    db.task_create(context=context, values=task)
    # Add it to RabbitMQ
    filters = {'storage_id': storage_id}
    task_id = db.task_get_all(context, filters=filters)[0].get('id')
    metrics_rpcapi.TaskAPI().create_perf_job(context, task_id)


def delete_perf_job(context, storage_id):
    # Delete it from scheduler
    filters = {'storage_id': storage_id}
    tasks = db.task_get_all(context, filters=filters)
    failed_tasks = db.failed_task_get_all(context, filters=filters)
    for task in tasks:
        metrics_rpcapi.TaskAPI().remove_job(context, task.get('id'),
                                            task.get('executor'))
    for failed_task in failed_tasks:
        metrics_rpcapi.TaskAPI().remove_failed_job(context,
                                                   failed_task.get('id'),
                                                   failed_task.get('executor'))

    # Soft delete tasks
    db.task_delete_by_storage(context, storage_id)
    db.failed_task_delete_by_storage(context, storage_id)
