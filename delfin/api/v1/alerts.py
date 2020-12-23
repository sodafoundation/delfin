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

from oslo_log import log

from delfin import db
from delfin import exception
from delfin.api import validation
from delfin.api.common import wsgi
from delfin.api.schemas import alerts as schema_alerts
from delfin.api.views import alerts as alerts_view
from delfin.common import alert_util
from delfin.drivers import api as driver_manager
from delfin.task_manager import rpcapi as task_rpcapi

LOG = log.getLogger(__name__)


class AlertController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.driver_manager = driver_manager.API()

    @wsgi.response(200)
    def show(self, req, id):
        ctx = req.environ['delfin.context']

        query_para = {}
        query_para.update(req.GET)

        try:
            begin_time = None
            end_time = None

            if query_para.get('begin_time'):
                begin_time = int(query_para.get('begin_time'))

            if query_para.get('end_time'):
                end_time = int(query_para.get('end_time'))
        except Exception:
            msg = "begin_time and end_time should be integer values in " \
                  "milliseconds."
            raise exception.InvalidInput(msg)

        # When both begin_time and end_time are provided, end_time should
        # be greater than begin_time
        if begin_time and end_time and end_time <= begin_time:
            msg = "end_time should be greater than begin_time."
            raise exception.InvalidInput(msg)

        storage = db.storage_get(ctx, id)
        alert_list = self.driver_manager.list_alerts(ctx, id, query_para)

        # Update storage attributes in each alert model
        for alert in alert_list:
            alert_util.fill_storage_attributes(alert, storage)

        return alerts_view.build_alerts(alert_list)

    @wsgi.response(200)
    def delete(self, req, id, sequence_number):
        ctx = req.environ['delfin.context']
        _ = db.storage_get(ctx, id)
        self.driver_manager.clear_alert(ctx, id, sequence_number)

    @validation.schema(schema_alerts.post)
    @wsgi.response(200)
    def sync(self, req, id, body):
        ctx = req.environ['delfin.context']

        # begin_time and end_time are optional parameters
        begin_time = body.get('begin_time')
        end_time = body.get('end_time')

        # When both begin_time and end_time are provided, end_time should
        # be greater than begin_time
        if begin_time and end_time and end_time <= begin_time:
            msg = "end_time should be greater than begin_time."
            raise exception.InvalidInput(msg)

        # Check for the storage existence
        _ = db.storage_get(ctx, id)

        query_para = {'begin_time': body.get('begin_time'),
                      'end_time': body.get('end_time')}

        # Trigger asynchronous alert syncing from storage backend
        self.task_rpcapi.sync_storage_alerts(ctx, id, query_para)


def create_resource():
    return wsgi.Resource(AlertController())
