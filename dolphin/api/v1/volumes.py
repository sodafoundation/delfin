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

from dolphin.api.common import wsgi


class VolumeController(wsgi.Controller):

    def index(self, req):
        return dict(name="Storage volume 1")

    def show(self, req, id):
        return dict(name="Storage volume 2")


def create_resource():
    return wsgi.Resource(VolumeController())
