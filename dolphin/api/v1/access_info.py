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
from webob import exc

from dolphin import db
from dolphin import exception
from dolphin.api import validation
from dolphin.api.common import wsgi
from dolphin.api.schemas import access_info as schema_access_info
from dolphin.api.views import access_info as access_info_viewer
from dolphin.drivers import api as driverapi


class AccessInfoController(wsgi.Controller):

    def __init__(self):
        super(AccessInfoController, self).__init__()
        self._view_builder = access_info_viewer.ViewBuilder()
        self.driver_api = driverapi.API()

    def show(self, req, id):
        """Show access information by storage id."""
        ctxt = req.environ['dolphin.context']

        try:
            access_info = db.access_info_get(ctxt, id)
        except exception.AccessInfoNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)

        return self._view_builder.show(access_info)

    @validation.schema(schema_access_info.update)
    def update(self, req, id, body):
        """Update storage access information."""
        ctxt = req.environ.get('dolphin.context')
        try:
            access_info = db.access_info_get(ctxt, id)
            access_info.update(body)
            access_info = self.driver_api.update_access_info(ctxt, access_info)
        except (exception.InvalidCredential,
                exception.InvalidResults,
                exception.StorageDriverNotFound,
                exception.AccessInfoNotFound,
                exception.StorageNotFound,
                exception.StorageBackendException,
                exception.StorageSerialNumberMismatch) as e:
            raise exc.HTTPBadRequest(explanation=e.msg)

        return self._view_builder.show(access_info)


def create_resource():
    return wsgi.Resource(AccessInfoController())
