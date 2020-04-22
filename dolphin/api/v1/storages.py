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

from six.moves import http_client
import webob

from dolphin import db
from dolphin.api.common import wsgi


def build_storages(storages):
    views = [build_storage(storage)
             for storage in storages]
    return dict(storage=views)


def build_storage(storage):
    view = copy.deepcopy(storage)
    return view

class StorageController(wsgi.Controller):

    def index(self, req):
        storage_all = db.storage_get_all()
        search_opts = [
            'name',
            'vendor',
            'model',
            'status',
        ]
        for search_opt in search_opts:
            if search_opt in req.GET:
                value = req.GET[search_opt]
                storage_all = [s for s in storage_all if s[search_opt] == value]
            if len(storage_all) == 0:
                break
        return build_storages(storage_all)

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


