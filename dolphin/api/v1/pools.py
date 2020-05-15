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
from dolphin.i18n import _


class PoolController(wsgi.Controller):
    def __init__(self):
        super(PoolController, self).__init__()
        self.search_options = ['name', 'status', 'id', 'storage_id']

    def _is_storage_valid(self, context, pool, storage_id):
        """verify the storage and pool association  ."""
        try:
            if pool.storage_id != storage_id:
                return False
            db.storage_get(context, storage_id)
        except exception.StorageNotFound:
            msg = _("storage  '%s' not found.") % storage_id
            raise exc.HTTPNotFound(explanation=msg)

    def _get_pools_search_options(self):
        """Return pools search options allowed ."""
        return self.search_options

    def _show(self, req, pool_id, storage_id=None):
        ctxt = req.environ['dolphin.context']
        try:
            pool = db.pool_get(ctxt, pool_id)
            if storage_id and not self._is_storage_valid(ctxt, pool, storage_id):
                err_msg = _('Given pool %s does not have a valid '
                            'storage.') % pool_id
                raise exception.InvalidStorage(reason=err_msg)
        except exception.PoolNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)
        except exception.InvalidStorage as e:
            raise exc.HTTPConflict(explanation=e.msg)
        return pool_view.build_pool(pool)

    def _index(self, req, storage_id=None):
        ctxt = req.environ['dolphin.context']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        limit, offset, marker = api_utils.get_pagination_params(query_params)
        # strip out options except supported search  options
        api_utils.remove_invalid_options(ctxt, query_params,
                                         self._get_pools_search_options())
        if storage_id:
            query_params['storage_id'] = storage_id
        try:
            pools = db.pool_get_all(ctxt, marker, limit, sort_keys, sort_dirs,
                                    query_params, offset)
        except  exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=six.text_type(e))
        except Exception as e:
            msg = "Error in list pool query "
            raise exc.HTTPNotFound(explanation=msg)
        return pool_view.build_pools(pools)

    def list_pools(self, req, storage_id):
        """Return a list of pools for storage."""
        return self._index(req, storage_id)

    def show_pool(self, req, id, storage_id):
        """Return a detail of a pool associated with storage."""
        return self._show(req, id, storage_id)

    def index(self, req):
        return self._index(req)

    def show(self, req, id):
        return self._show(req, id)


def create_resource():
    return wsgi.Resource(PoolController())
