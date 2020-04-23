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

from dolphin.api.common import wsgi
from dolphin.resource_manager import storages


class StorageController(wsgi.Controller):

    def index(self, req):
        return dict(name="Storage 1")

    def show(self, req, id):
        return dict(name="Storage 2")

    def create(self, req, body):
        """
        :param req:
        :param body:
        :return:
        """
        # Check if body is valid
        if not self.is_valid_body(body, 'storages'):
            msg = "Storage entity not found in request body"
            raise exc.HTTPUnprocessableEntity(explanation=msg)

        return storages.register(self, req, body)

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


