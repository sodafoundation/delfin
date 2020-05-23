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


import six
from webob import exc

from dolphin import db, exception
from dolphin.api import api_utils
from dolphin.api.common import wsgi
from dolphin.api.views import pools as pool_view


class PoolController(wsgi.Controller):
    def __init__(self):
        super(PoolController, self).__init__()
        self.search_options = ['name', 'status', 'id', 'storage_id']

    def _get_pools_search_options(self):
        """Return pools search options allowed ."""
        return self.search_options

    def show(self, req, pool_id):
        ctxt = req.environ['dolphin.context']
        try:
            pool = db.pool_get(ctxt, pool_id)
        except exception.PoolNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)
        return pool_view.build_pool(pool)

    def index(self, req):
        ctxt = req.environ['dolphin.context']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        marker, limit, offset = api_utils.get_pagination_params(query_params)
        # strip out options except supported search  options
        api_utils.remove_invalid_options(ctxt, query_params,
                                         self._get_pools_search_options())
        try:
            pools = db.pool_get_all(ctxt, marker, limit, sort_keys, sort_dirs,
                                    query_params, offset)
        except exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=six.text_type(e))
        return pool_view.build_pools(pools)


def create_resource():
    return wsgi.Resource(PoolController())
