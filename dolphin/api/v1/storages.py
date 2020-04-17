# Copyright 2010 OpenStack LLC.
# Copyright 2015 Clinton Knight
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg

from dolphin.api import extensions
from dolphin.api import common
from dolphin.api.common import wsgi
from oslo_log import log
from dolphin.api.views import storages as views_storages
import webob
from webob import exc

CONF = cfg.CONF
LOG = log.getLogger(__name__)

_KNOWN_STORAGES = {
    "id": "string",
    "name": "EMC-VMAX-123456",
    "description": "VMAX storage lab1",
    "manufacturer": "EMC",
    "model": "VMAX",
    "status": "Available",
    "firmware": "v3.1",
    "serialNo": "12345678",
    "location": "string",
    "createdAt": "string",
    "updatedAt": "string",
    "totalCapacity": 0,
    "usedCapacity": 0,
    "availbaleCapacity": 0
}


class StoragesRouter(common.APIRouter):
    """Route versions requests."""

    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper):
        """POC : Use this connect for GET method"""
        self.resources['storages'] = create_resource()
        mapper.connect("storages", '/storages',
                       controller=self.resources['storages'],
                       action='all')
        mapper.redirect('', '/storages')

        """POC : Use this connect for POST method and comment the above one"""
        self.resources['storages'] = create_resource()
        mapper.connect('storages', '/storages',
                       controller=self.resources['storages'],
                       action='create')
        mapper.redirect('', '/storages')


class StoragesController(wsgi.Controller):

    def __init__(self):
        super(StoragesController, self).__init__(None)

    @wsgi.response(200)
    def all(self, req):
        """Return all known storages."""
        builder = views_storages.get_view_builder(req)
        LOG.info("Consume Storages task ...")
        return builder.build_storages(_KNOWN_STORAGES)

    @wsgi.response(200)
    def create(self, req, body):
        if not self.is_valid_body(body, 'storages'):
            LOG.error("Not a valid body")
            raise exc.HTTPUnprocessableEntity()
            
        storage = body['storages']
        new_storage = views_storages.get_post_view_builder(req, storage)
        return new_storage.build_storages(storage)


def create_resource():
    return wsgi.Resource(StoragesController())
