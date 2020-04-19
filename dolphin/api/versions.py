    # Copyright 2010 OpenStack LLC.
# Copyright 2015 Clinton Knight
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

from oslo_config import cfg

from dolphin.api import extensions
from dolphin.api import common
from dolphin.api.common import wsgi
from dolphin.api.views import versions as views_versions

CONF = cfg.CONF

_LINKS = [{
    'rel': 'describedby',
    'type': 'text/html',
    'href': 'http://docs.openstack.org/',
}]

_MEDIA_TYPES = [{
    'base': 'application/json',
    'type': 'application/vnd.common.share+json;version=1',
}]

_KNOWN_VERSIONS = {
    'v1.0': {
        'id': 'v1.0',
        'status': 'CUREENT',
        'version': '',
        'min_version': '',
        'updated': '202004-10T11:33:21Z',
        'links': _LINKS,
        'media-types': _MEDIA_TYPES,
    },
}


class VersionsRouter(common.APIRouter):
    """Route versions requests."""

    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper):
        self.resources['versions'] = create_resource()
        mapper.connect('versions', '/',
                       controller=self.resources['versions'],
                       action='all')
        mapper.redirect('', '/')


class VersionsController(wsgi.Controller):

    def __init__(self):
        super(VersionsController, self).__init__(None)

    @wsgi.response(300)
    def all(self, req):
        """Return all known versions."""
        builder = views_versions.get_view_builder(req)
        known_versions = copy.deepcopy(_KNOWN_VERSIONS)
        return builder.build_versions(known_versions)


def create_resource():
    return wsgi.Resource(VersionsController())
