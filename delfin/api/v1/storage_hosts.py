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
from delfin.api.views import storage_hosts as storage_host_view


class StorageHostController(wsgi.Controller):

    def __init__(self):
        super(StorageHostController, self).__init__()
        self.search_options = ['name', 'status', 'id', 'storage_id',
                               'native_storage_host_id']

    def _get_storage_host_search_options(self):
        """Return storage host search options allowed ."""
        return self.search_options

    def _fill_storage_host_initiators(self, ctxt, storage_host, storage_id):
        """Fills initiator list for storage host."""

        storage_host_initiators = db.storage_host_initiators_get_all(
            ctxt, filters={"storage_id": storage_id,
                           "native_storage_host_id":
                               storage_host['native_storage_host_id']})
        storage_host_initiator_list = []
        for storage_host_initiator in storage_host_initiators:
            storage_host_initiator_list.append(
                storage_host_initiator['native_storage_host_initiator_id'])
        return storage_host_initiator_list

    def show(self, req, id):
        ctxt = req.environ['delfin.context']
        query_params = {"storage_id": id}
        query_params.update(req.GET)
        # Update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        marker, limit, offset = api_utils.get_pagination_params(query_params)
        # Strip out options except supported search  options
        api_utils.remove_invalid_options(
            ctxt, query_params, self._get_storage_host_search_options())

        storage_hosts = db.storage_hosts_get_all(ctxt, marker, limit,
                                                 sort_keys, sort_dirs,
                                                 query_params, offset)
        for storage_host in storage_hosts:
            storage_host['storage_host_initiators'] \
                = self._fill_storage_host_initiators(ctxt, storage_host, id)

        return storage_host_view.build_storage_hosts(storage_hosts)


def create_resource():
    return wsgi.Resource(StorageHostController())
