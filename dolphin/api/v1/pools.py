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
import json

import six
from webob import exc

from dolphin import db, exception
from dolphin.api import common_utils as common
from dolphin.api.common import wsgi
from dolphin.api.views import pools as pool_view


class PoolController(wsgi.Controller):

    def index(self, req):
        ctxt = req.environ['dolphin.context']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys = (lambda x: [x] if x is not None else x)(query_params.get('sort_key'))
        sort_dirs = (lambda x: [x] if x is not None else x)(query_params.get('sort_dir'))
        limit = query_params.get('limit', None)
        offset = query_params.get('offset', None)
        marker = query_params.get('marker', None)
        # strip out options except supported search  options
        common.remove_invalid_options(ctxt,query_params, self._get_pools_search_options())
        try:
            pools = db.pool_get_all(ctxt, marker, limit, sort_keys, sort_dirs, query_params, offset)
        except  exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=six.text_type(e))
        except Exception as e:
            msg = "Error in list pool Query "
            raise exc.HTTPNotFound(explanation=msg)
        return pool_view.build_pools(pools)

    def show(self, req, id):
        return dict(name="Storage pool 2")

    def _get_pools_search_options(self):
        """Return pools search options allowed ."""
        return ('name', 'status', 'id', 'storage_id')

def create_resource():
    return wsgi.Resource(PoolController())


