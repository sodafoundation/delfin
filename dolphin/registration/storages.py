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

import copy

from oslo_config import cfg

from dolphin.api import extensions
from dolphin.api import common
from dolphin.api.common import wsgi
from dolphin.api.views import storages as views_storages

CONF = cfg.CONF

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


class StoragesController(wsgi.Controller):

    def __init__(self):
        super(StoragesController, self).__init__(None)

    @wsgi.response(200)
    def create(self, req, body):
        """Return all known versions."""
        print "POST call"
        register_storage = {'id': body.get('id'), 'name': body.get('name')}
        builder = views_storages.get_view_builder(req)
        return builder.build_post_storages(register_storage)

    @wsgi.response(200)
    def index(self, req):
        """Returns a detailed list of storages."""
        builder = views_storages.get_view_builder(req)
        known_storages = copy.deepcopy(_KNOWN_STORAGES)
        return builder.build_storages(known_storages)


def create_resource():
    return wsgi.Resource(StoragesController())
