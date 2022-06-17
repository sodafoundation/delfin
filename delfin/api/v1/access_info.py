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

from delfin import db
from delfin import cryptor
from delfin.api import validation
from delfin.api.common import wsgi
from delfin.api.schemas import access_info as schema_access_info
from delfin.api.views import access_info as access_info_viewer
from delfin.db.sqlalchemy.models import AccessInfo
from delfin.common import constants
from delfin.drivers import api as driverapi


class AccessInfoController(wsgi.Controller):

    def __init__(self):
        super(AccessInfoController, self).__init__()
        self._view_builder = access_info_viewer.ViewBuilder()
        self.driver_api = driverapi.API()

    def show(self, req, id):
        """Show access information by storage id."""
        ctxt = req.environ['delfin.context']
        access_info = db.access_info_get(ctxt, id)
        return self._view_builder.show(access_info)

    def _cm_access_info_update(self, ctxt, access_info, body):
        access_info_dict = copy.deepcopy(access_info)
        unused = ['created_at', 'updated_at', 'storage_name',
                  'storage_id', 'extra_attributes']
        access_info_dict = AccessInfo.to_dict(access_info_dict)
        for field in unused:
            if access_info_dict.get(field):
                access_info_dict.pop(field)
        for access in constants.ACCESS_TYPE:
            if access_info_dict.get(access):
                access_info_dict.pop(access)

        access_info_list = db.access_info_get_all(
            ctxt, filters=access_info_dict)

        for cm_access_info in access_info_list:
            if cm_access_info['storage_id'] == access_info['storage_id']:
                continue
            for access in constants.ACCESS_TYPE:
                if cm_access_info.get(access):
                    cm_access_info[access]['password'] = cryptor.decode(
                        cm_access_info[access]['password'])
                if body.get(access):
                    cm_access_info[access].update(body[access])
            self.driver_api.update_access_info(ctxt, cm_access_info)

    @validation.schema(schema_access_info.update)
    def update(self, req, id, body):
        """Update storage access information."""
        ctxt = req.environ.get('delfin.context')
        access_info = db.access_info_get(ctxt, id)
        self._cm_access_info_update(ctxt, access_info, body)
        for access in constants.ACCESS_TYPE:
            if access_info.get(access):
                access_info[access]['password'] = cryptor.decode(
                    access_info[access]['password'])
            if body.get(access):
                access_info[access].update(body[access])
        access_info = self.driver_api.update_access_info(ctxt, access_info)
        return self._view_builder.show(access_info)

    def show_all(self, req):
        """Show all access information."""
        ctxt = req.environ.get('delfin.context')
        access_infos = db.access_info_get_all(ctxt)
        return self._view_builder.show_all(access_infos)


def create_resource():
    return wsgi.Resource(AccessInfoController())
