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

from dolphin.api import extensions
from dolphin.api import common
from dolphin.api import versions
from dolphin.api.v1 import storages
from dolphin.api.v1 import access_info
from dolphin.api.v1 import pools
from dolphin.api.v1 import volumes


class APIRouter(common.APIRouter):

    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper):
        self.resources['versions'] = versions.create_resource()
        mapper.connect("versions", "/",
                       controller=self.resources['versions'],
                       action='index')

        mapper.redirect("", "/")

        self.resources['storages'] = storages.create_resource()
        mapper.resource("storage", "storages",
                        controller=self.resources['storages'],
                        collection={'sync_all': 'POST'},
                        member={'sync': 'POST'})

        self.resources['access_info'] = access_info.create_resource()
        mapper.connect("storages", "/storages/{id}/access-info",
                       controller=self.resources['access_info'],
                       action="show",
                       conditions={"method": ["GET"]})

        mapper.connect("storages", "/storages/{id}/access-info",
                       controller=self.resources['access_info'],
                       action="update",
                       conditions={"method": ["PUT"]})
        self.resources['pools'] = pools.create_resource()
        mapper.resource("pool", "pools",
                        controller=self.resources['pools'])

        self.resources['volumes'] = volumes.create_resource()
        mapper.resource("volume", "volumes",
                        controller=self.resources['volumes'])
