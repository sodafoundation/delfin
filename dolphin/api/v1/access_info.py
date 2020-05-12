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
from dolphin.api import validation
from webob import exc

from dolphin import db, cryptor
from dolphin import exception
from dolphin.api.common import wsgi, LOG
from dolphin.api.views import access_info as access_info_viewer
from dolphin.drivers import api as driverapi
from dolphin.api.views import storages as storage_view
from dolphin.i18n import _
from dolphin.api.schemas import access_info as schema_access_info


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
        # Get existing access_info and storage from DB
        try:
            access_info_present = db.access_info_get(ctxt, id)
            storage_present = db.storage_get(ctxt, id)
            access_info_updated_dict = access_info_present.to_dict()
            access_info_updated_dict.update(body)
            # Discover storage with new access info
            storage = self.driver_api.discover_storage(ctxt, access_info_updated_dict)
            if storage['serial_number'] != storage_present.serial_number:
                reason = (_("Existing storage serial Number is not matching \
                with th new storage serial number: '%s'  ") % storage['serial_number'])
                raise exception.StorageSerialNumberMismatch(reason=reason)
            db.storage_update(ctxt, id, storage)
            access_info_updated_dict['password'] = cryptor.encode(
                access_info_updated_dict['password'])
            db.access_info_update(ctxt, id, access_info_updated_dict)
        except (exception.InvalidCredential,
                exception.StorageDriverNotFound,
                exception.AccessInfoNotFound,
                exception.StorageNotFound,
                exception.StorageSerialNumberMismatch) as e:
            raise exc.HTTPBadRequest(explanation=e.message)
        except Exception as e:
            msg = _('Failed to to update  access info: {0}'.format(e))
            LOG.error(msg)
            raise exc.HTTPBadRequest(explanation=msg)
        return storage_view.build_storage(storage)


def create_resource():
    return wsgi.Resource(AccessInfoController())
