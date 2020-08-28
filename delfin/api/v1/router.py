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

from delfin.api import common
from delfin.api import extensions
from delfin.api.v1 import access_info
from delfin.api.v1 import alert_source
from delfin.api.v1 import alerts
from delfin.api.v1 import storage_pools
from delfin.api.v1 import storages
from delfin.api.v1 import volumes


class APIRouter(common.APIRouter):

    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper):
        mapper.redirect("", "/")

        self.resources['storages'] = storages.create_resource()
        mapper.resource("storage", "storages",
                        controller=self.resources['storages'],
                        member={'sync': 'POST'})

        mapper.connect("storages", "/storages/sync",
                       controller=self.resources['storages'],
                       action="sync_all",
                       conditions={"method": ["POST"]})

        self.resources['access_info'] = access_info.create_resource()
        mapper.connect("storages", "/storages/{id}/access-info",
                       controller=self.resources['access_info'],
                       action="show",
                       conditions={"method": ["GET"]})

        mapper.connect("storages", "/storages/{id}/access-info",
                       controller=self.resources['access_info'],
                       action="update",
                       conditions={"method": ["PUT"]})

        self.resources['alert_sources'] = alert_source.create_resource()
        mapper.connect("storages", "/storages/{id}/alert-source",
                       controller=self.resources['alert_sources'],
                       action="put",
                       conditions={"method": ["PUT"]})
        mapper.connect("storages", "/storages/{id}/alert-source",
                       controller=self.resources['alert_sources'],
                       action="show",
                       conditions={"method": ["GET"]})
        mapper.connect("storages", "/storages/{id}/alert-source",
                       controller=self.resources['alert_sources'],
                       action="delete",
                       conditions={"method": ["DELETE"]})

        self.resources['alerts'] = alerts.create_resource()
        mapper.connect("storages", "/storages/{id}/alerts/{sequence_number}",
                       controller=self.resources['alerts'],
                       action="delete",
                       conditions={"method": ["DELETE"]})

        mapper.connect("storages", "/storages/{id}/alerts",
                       controller=self.resources['alerts'],
                       action="show",
                       conditions={"method": ["GET"]})

        self.resources['storage-pools'] = storage_pools.create_resource()
        mapper.resource("storage-pool", "storage-pools",
                        controller=self.resources['storage-pools'])

        self.resources['volumes'] = volumes.create_resource()
        mapper.resource("volume", "volumes",
                        controller=self.resources['volumes'])
