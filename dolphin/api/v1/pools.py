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
from dolphin.i18n import _


class PoolController(wsgi.Controller):
    def _verify_storage(self, context, storage_id):
        try:
            db.storage_get(context, storage_id)
        except exception.StorageNotFound:
            msg = _("storage  '%s' not found.") % storage_id
            raise exc.HTTPNotFound(explanation=msg)

    def _get_pools_search_options(self):
        """Return pools search options allowed ."""
        return ('name', 'status', 'id', 'storage_id')

    def _show(self, req, pool_id, storage_id=None):
        ctxt = req.environ['dolphin.context']
        if storage_id:
            self._verify_storage(ctxt,storage_id)
        try:
            pool = db.pool_get(ctxt, pool_id)
        except exception.StorageNotFound as e:
            raise exc.HTTPNotFound(explanation=e.message)
        return pool_view.build_pool(pool)

    def _index(self, req, storage_id=None):
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
        common.remove_invalid_options(ctxt, query_params,
                                      self._get_pools_search_options())
        if storage_id:
            query_params['storage_id'] = storage_id
        try:
            pools = db.pool_get_all(ctxt, marker, limit, sort_keys, sort_dirs,
                                    query_params, offset)
        except  exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=six.text_type(e))
        except Exception as e:
            msg = "Error in list pool Query "
            raise exc.HTTPNotFound(explanation=msg)
        return pool_view.build_pools(pools)

    def list_pool(self, req, storage_id):
        """Return a list of pools for storage."""
        return self._index(req, storage_id)

    def show_pool(self, req, id, storage_id):
        return self._show(req, id,storage_id)

    def index(self, req):
        return self._index(req)

    def show(self, req, id):
        return self._show(req, id)




def create_resource():
    return wsgi.Resource(PoolController())
