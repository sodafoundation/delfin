# Copyright 2021 The SODA Authors.
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
from delfin.api.views import qtrees as qtree_view


class QtreeController(wsgi.Controller):

    def __init__(self):
        super(QtreeController, self).__init__()
        self.search_options = ['name', 'state', 'id', 'storage_id',
                               'native_filesystem_id', 'quota_id',
                               'native_qtree_id']

    def _get_qtrees_search_options(self):
        """Return qtrees search options allowed ."""
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
                                         self._get_qtrees_search_options())

        qtrees = db.qtree_get_all(ctxt, marker, limit, sort_keys,
                                  sort_dirs, query_params, offset)
        return qtree_view.build_qtrees(qtrees)

    def show(self, req, id):
        ctxt = req.environ['delfin.context']
        qtree = db.qtree_get(ctxt, id)
        return qtree_view.build_qtree(qtree)


def create_resource():
    return wsgi.Resource(QtreeController())
