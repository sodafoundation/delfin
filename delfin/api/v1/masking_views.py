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
from delfin.api.views import masking_views


class MaskingViewController(wsgi.Controller):

    def __init__(self):
        super(MaskingViewController, self).__init__()
        self.search_options = ['name', 'id', 'storage_id',
                               'native_storage_host_group_id',
                               'native_storage_port_group_id',
                               'native_storage_volume_group_id',
                               'native_storage_host_id',
                               'native_volume_id',
                               'native_port_id',
                               'native_masking_view_id']

    def _get_masking_view_search_options(self):
        """Return masking view search options allowed ."""
        return self.search_options

    def show(self, req, id):
        ctxt = req.environ['delfin.context']
        query_params = {"storage_id": id}
        query_params.update(req.GET)
        # Update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        marker, limit, offset = api_utils.get_pagination_params(query_params)
        # Strip out options except supported search  options
        api_utils.remove_invalid_options(
            ctxt, query_params, self._get_masking_view_search_options())

        masking_view_lists = db.masking_views_get_all(ctxt, marker, limit,
                                                      sort_keys, sort_dirs,
                                                      query_params, offset)
        return masking_views.build_masking_views(masking_view_lists)


def create_resource():
    return wsgi.Resource(MaskingViewController())
