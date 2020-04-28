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

import six
from six.moves import http_client
import webob
from webob import exc

from oslo_log import log

from dolphin.api.common import wsgi
from dolphin.api.schemas import storages as schema_storages
from dolphin.api import validation
from dolphin.api.views import storages as storage_view
from dolphin import context
from dolphin import db
from dolphin.drivers import manager as drivermanager
from dolphin import exception
from dolphin.i18n import _
from dolphin.task_manager import rpcapi as task_rpcapi
from dolphin import utils

LOG = log.getLogger(__name__)


def validate_parameters(data, required_parameters,
                        fix_response=False):
    if fix_response:
        exc_response = exc.HTTPBadRequest
    else:
        exc_response = exc.HTTPUnprocessableEntity

    for parameter in required_parameters:
        if parameter not in data:
            msg = _("Required parameter %s not found.") % parameter
            raise exc_response(explanation=msg)
        if not data.get(parameter):
            msg = _("Required parameter %s is empty.") % parameter
            raise exc_response(explanation=msg)


class StorageController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.task_rpcapi = task_rpcapi.TaskAPI()

    def index(self, req):

        supported_filters = ['name', 'vendor', 'model', 'status']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys = (lambda x: [x] if x is not None else x)(query_params.get('sort_key'))
        sort_dirs = (lambda x: [x] if x is not None else x)(query_params.get('sort_dir'))
        limit = query_params.get('limit', None)
        offset = query_params.get('offset', None)
        marker = query_params.get('marker', None)
        # strip out options except supported filter options
        filters = query_params
        unknown_options = [opt for opt in filters
                           if opt not in supported_filters]
        bad_options = ", ".join(unknown_options)
        LOG.debug("Removing options '%(bad_options)s' from query",
                  {"bad_options": bad_options})
        for opt in unknown_options:
            del filters[opt]
        try:
            storages = db.storage_get_all(context, marker, limit, sort_keys, sort_dirs, filters, offset)
        except  exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=six.text_type(e))
        except Exception as e:
            msg = "Error in storage_get_all query from DB "
            raise exc.HTTPNotFound(explanation=msg)
        return storage_view.build_storages(storages)

    def show(self, req, id):
        return dict(name="Storage 2")

    @validation.schema(schema_storages.create)
    def create(self, req, body):
        """Register a new storage device."""
        # ctxt = req.environ['dolphin.context']
        ctxt = context.get_admin_context()
        driver = drivermanager.DriverManager()
        try:
            storage = driver.register_storage(ctxt, body)
        except exception.DolphinException as e:
            LOG.error(e)
            raise e
        # except Exception as e:
        #     msg = _('Failed to register device in driver :{0}'.format(e))
        #     LOG.error(e)
        #     raise exception.DolphinException(msg)
        return storage_view.build_storage(storage)

    def update(self, req, id, body):
        return dict(name="Storage 4")

    def delete(self, req, id):
        return webob.Response(status_int=http_client.ACCEPTED)

    def sync_all(self, req):
        return dict(name="Sync all storages")

    def sync(self, req, id):
        """
        :param req:
        :param id:
        :return:
        """
        # validate the id
        context = req.environ.get('dolphin.context')
        # admin_context = context.RequestContext('admin', 'fake', True)
        try:
            device = db.access_info_get(context, id)
        except Exception as e:
            LOG.error(e)
            raise exception.AccessInfoNotFound(e)

        tasks = (
            'pool_task',
            'volume_task'
        )
        for task in tasks:
            self.task_rpcapi.sync_storage_resource(context, id, task)

        return dict(name="Sync storage 1")


def create_resource():
    return wsgi.Resource(StorageController())
