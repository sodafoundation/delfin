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

from oslo_log import log
from six.moves import http_client
import webob
from webob import exc

from dolphin import db, context
from dolphin.api.common import wsgi

LOG = log.getLogger(__name__)

def build_storages(storages):
    views = [build_storage(storage)
             for storage in storages]
    return dict(storage=views)


def build_storage(storage):
    view = copy.deepcopy(storage)
    return view


class StorageController(wsgi.Controller):

    def index(self, req):

        supported_filters = [
            'name',
            'vendor',
            'model',
            'status',
        ]
        filters = {}
        filters.update(req.GET)
        # update options  other than filters
        if 'sort_key' in filters:
            sort_key = filters['sort_key']
        else:
            sort_key = None
        if 'sort_dir' in filters:
            sort_dir = filters['sort_dir']
        else:
            sort_dir = None
        if 'limit' in filters:
            limit = filters['limit']
        else:
            limit = None
        if 'offset' in filters:
            offset = filters['offset']
        else:
            offset = None
        # strip out options except supported filter options
        unknown_options = [opt for opt in filters
                           if opt not in supported_filters]
        bad_options = ", ".join(unknown_options)
        LOG.debug("Removing options '%(bad_options)s' from query",
                  {"bad_options": bad_options})
        for opt in unknown_options:
            del filters[opt]
        try:
            storages = db.storage_get_all(context, None, limit, sort_key, sort_dir, filters, offset)
        except:
            msg = "Error in storage_get_all query from DB "
            raise exc.HTTPNotFound(explanation=msg)
        return build_storages(storages)

    def show(self, req, id):
        return dict(name="Storage 2")

    def create(self, req, body):
        return dict(name="Storage 3")

    def update(self, req, id, body):
        return dict(name="Storage 4")

    def delete(self, req, id):
        return webob.Response(status_int=http_client.ACCEPTED)

    def sync_all(self, req):
        return dict(name="Sync all storages")

    def sync(self, req, id):
        return dict(name="Sync storage 1")


def create_resource():
    return wsgi.Resource(StorageController())


