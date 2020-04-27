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

from six.moves import http_client
import webob
from webob import exc
from oslo_log import log

from dolphin.api.common import wsgi
from dolphin.drivers import manager as drivermanager
from dolphin.db.sqlalchemy import api as db
from dolphin import exception
from dolphin import utils
from dolphin.i18n import _
from dolphin import context
from dolphin.task_manager import rpcapi as task_rpcapi

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
        self.task_rpcapi = task_rpcapi.TaskAPI()

    def index(self, req):
        return dict(name="Storage 1")

    def show(self, req, id):
        return dict(name="Storage 2")

    def create(self, req, body):
        """
        This function for registering the new storage device
        :param req:
        :param body: "It contains the all input parameters"
        :return:
        """
        # Check if body is valid
        if not self.is_valid_body(body, 'storages'):
            msg = _("Storage entity not found in request body")
            raise exc.HTTPUnprocessableEntity(explanation=msg)

        storage = body['storages']

        # validate the body has all required parameters
        required_parameters = ('hostip', 'vendor', 'model', 'username',
                               'password')
        validate_parameters(storage, required_parameters)

        # validate the hostip
        if not utils.is_valid_ip_address(storage['hostip'], ip_version='4'):
            msg = _("Invalid hostip: {0}. Please provide a "
                    "valid hostip".format(storage['hostip']))
            LOG.error(msg)
            raise exception.InvalidHost(msg)

        # get dolphin.context. Later may be validated context parameters
        context = req.environ.get('dolphin.context')

        driver = drivermanager.DriverManager()
        try:
            device_info = driver.register_storage(context, storage)
            status = ''
            if device_info.get('status') == 'available':
                status = device_info.get('status')
        except AttributeError as e:
            LOG.error(e)
            raise exception.DolphinException(e)
        except Exception as e:
            msg = _('Failed to register device in driver :{0}'.format(e))
            LOG.error(e)
            raise exception.DolphinException(msg)

        if status == 'available':
            try:
                storage['storage_id'] = device_info.get('id')

                db.access_info_create(context, storage)

                db.storage_create(context, device_info)
            except AttributeError as e:
                LOG.error(e)
                raise exception.DolphinException(e)
            except Exception as e:
                msg = _('Failed to create device entry in DB: {0}'
                        .format(e))
                LOG.exception(msg)
                raise exception.DolphinException(msg)

        else:
            msg = _('Device registration failed with status: {0}'
                    .format(status))
            LOG.error(msg)
            raise exception.DolphinException(msg)

        return device_info

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
        except exception.NotFound as e:
            LOG.error(e)
            raise exception.DolphinException(e)

        tasks = (
            'pool_task',
            'volume_task'
        )
        for task in tasks:
            self.task_rpcapi.sync_storage_resource(context, id, task)

        return dict(name="Sync storage 1")


def create_resource():
    return wsgi.Resource(StorageController())
