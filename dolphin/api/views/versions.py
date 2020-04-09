# Copyright 2010-2011 OpenStack LLC.
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
import re

from six.moves import urllib


def get_view_builder(req):
    return ViewBuilder(req.application_url)


_URL_SUFFIX = {'v1.0': 'v1', 'v2.0': 'v2'}


class ViewBuilder(object):
    def __init__(self, base_url):
        """Initialize ViewBuilder.

        :param base_url: url of the root wsgi application
        """
        self.base_url = base_url

    def build_versions(self, versions):
        views = [self._build_version(versions[key])
                 for key in sorted(list(versions.keys()))]
        return dict(versions=views)

    def _build_version(self, version):
        view = copy.deepcopy(version)
        view['links'] = self._build_links(version)
        return view

    def _build_links(self, version_data):
        """Generate a container of links that refer to the provided version."""
        links = copy.deepcopy(version_data.get('links', {}))
        version = _URL_SUFFIX.get(version_data['id'])
        links.append({'rel': 'self',
                      'href': self._generate_href(version=version)})
        return links

    def _generate_href(self, version='v1', path=None):
        """Create a URL that refers to a specific version_number."""
        base_url = self._get_base_url_without_version()
        href = urllib.parse.urljoin(base_url, version).rstrip('/') + '/'
        if path:
            href += path.lstrip('/')
        return href

    def _get_base_url_without_version(self):
        """Get the base URL with out the /v1 suffix."""
        return re.sub('v[1-9]+/?$', '', self.base_url)
