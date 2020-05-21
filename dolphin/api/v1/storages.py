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

import copy
import six
from six.moves import http_client
import webob
from webob import exc

from oslo_log import log

from dolphin.api.common import wsgi
from dolphin.api.schemas import storages as schema_storages
from dolphin.api import validation, api_utils
from dolphin.api.views import storages as storage_view
from dolphin import context
from dolphin import coordination
from dolphin import cryptor
from dolphin import db
from dolphin.drivers import api as driverapi
from dolphin import exception
from dolphin.i18n import _
from dolphin.task_manager import rpcapi as task_rpcapi
from dolphin import utils
from dolphin.task_manager.tasks import task

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
        self.driver_api = driverapi.API()
        self.search_options = ['name', 'vendor', 'model', 'status', 'serial_number']

    def _get_storages_search_options(self):
        """Return storages search options allowed ."""
        return self.search_options

    def index(self, req):
        ctxt = req.environ['dolphin.context']
        supported_filters = ['name', 'vendor', 'model', 'status']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        marker, limit, offset = api_utils.get_pagination_params(query_params)
        # strip out options except supported search  options
        api_utils.remove_invalid_options(ctxt, query_params,
                                         self._get_storages_search_options())
        try:
            storages = db.storage_get_all(context, marker, limit, sort_keys,
                                          sort_dirs, query_params, offset)
        except  exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=six.text_type(e))
        except Exception as e:
            msg = _("Error in list storage query.")
            raise exc.HTTPNotFound(explanation=msg)
        return storage_view.build_storages(storages)

    def show(self, req, id):
        try:
            storage = db.storage_get(context, id)
        except exception.StorageNotFound as e:
            raise exc.HTTPNotFound(explanation=e.message)
        return storage_view.build_storage(storage)


    @wsgi.response(201)
    @validation.schema(schema_storages.create)
    @coordination.synchronized('storage-create-{body[host]}-{body[port]}')
    def create(self, req, body):
        """Register a new storage device."""
        ctxt = req.environ['dolphin.context']
        access_info_dict = body

        if self._is_registered(ctxt, access_info_dict):
            msg = _("Storage has been registered.")
            raise exc.HTTPBadRequest(explanation=msg)

        try:
            storage = self.driver_api.discover_storage(ctxt, access_info_dict)
            storage = db.storage_create(context, storage)

            # Need to encode the password before saving.
            access_info_dict['storage_id'] = storage['id']
            access_info_dict['password'] = cryptor.encode(access_info_dict['password'])
            db.access_info_create(context, access_info_dict)
        except (exception.InvalidCredential,
                exception.StorageDriverNotFound,
                exception.AccessInfoNotFound,
                exception.StorageNotFound) as e:
            raise exc.HTTPBadRequest(explanation=e.message)
        except Exception as e:
            msg = _('Failed to register storage: {0}'.format(e))
            LOG.error(msg)
            raise exc.HTTPBadRequest(explanation=msg)

        return storage_view.build_storage(storage)

    def update(self, req, id, body):
        return dict(name="Storage 4")

    def delete(self, req, id):
        return webob.Response(status_int=http_client.ACCEPTED)

    def sync_all(self, req):
        return dict(name="Sync all storages")

    @wsgi.response(202)
    def sync(self, req, id):
        """
        :param req:
        :param id:
        :return:
        """
        # validate the id
        ctxt = req.environ['dolphin.context']
        try:
            storage = db.storage_get(ctxt, id)
        except exception.StorageNotFound as e:
            LOG.error(e)
            raise exc.HTTPNotFound(explanation=e.msg)
        else:
            for subclass in task.StorageResourceTask.__subclasses__():
                self.task_rpcapi.sync_storage_resource(
                    ctxt,
                    storage['id'],
                    subclass.__module__ + '.' + subclass.__name__
                )

        return

    def _is_registered(self, context, access_info):
        access_info_dict = copy.deepcopy(access_info)

        # Remove unrelated query fields
        access_info_dict.pop('username', None)
        access_info_dict.pop('password', None)
        access_info_dict.pop('vendor', None)
        access_info_dict.pop('model', None)

        # Check if storage is registered
        if db.access_info_get_all(context,
                                  filters=access_info_dict):
            return True
        return False


def create_resource():
    return wsgi.Resource(StorageController())
