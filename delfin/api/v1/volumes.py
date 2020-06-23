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

from delfin import db
from delfin.api import api_utils
from delfin.api.common import wsgi
from delfin.api.views import volumes as volume_view


class VolumeController(wsgi.Controller):

    def __init__(self):
        super(VolumeController, self).__init__()
        self.search_options = ['name', 'status', 'id', 'storage_id', 'wwn',
                               'native_volume_id', 'native_storage_pool_id']

    def _get_volumes_search_options(self):
        """Return volumes search options allowed ."""
        return self.search_options

    def index(self, req):
        ctxt = req.environ['delfin.context']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        marker, limit, offset = api_utils.get_pagination_params(query_params)
        # strip out options except supported search  options
        api_utils.remove_invalid_options(ctxt, query_params,
                                         self._get_volumes_search_options())

        volumes = db.volume_get_all(ctxt, marker, limit, sort_keys,
                                    sort_dirs, query_params, offset)
        return volume_view.build_volumes(volumes)

    def show(self, req, id):
        ctxt = req.environ['delfin.context']
        volume = db.volume_get(ctxt, id)
        return volume_view.build_volume(volume)


def create_resource():
    return wsgi.Resource(VolumeController())
