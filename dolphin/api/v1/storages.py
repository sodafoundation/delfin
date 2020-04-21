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
from os_service_types import exc
from dolphin import context
from six.moves import http_client
import webob

from dolphin.api.common import wsgi, LOG
from dolphin.db.sqlalchemy import api as db
from dolphin.resource_manager import storages
from dolphin.task_manager import manager as taskmanager


class StorageController(wsgi.Controller):

    def index(self, req):
        return storages.get_all()

    def show(self, req, id):
        return dict(name="Storage 2")

    def create(self, req, body):

        return storages.register(self, req, body)

    def update(self, req, id, body):
        return dict(name="Storage 4")

    def delete(self, req, id):
        return webob.Response(status_int=http_client.ACCEPTED)

    def sync_all(self, req):
        taskmgr = taskmanager.TaskManager()
        ctxt = context.RequestContext()
        return taskmgr.storage_device_details(ctxt, req)

    def sync(self, req, id):
        return dict(name="Sync storage 1")


def create_resource():
    return wsgi.Resource(StorageController())
