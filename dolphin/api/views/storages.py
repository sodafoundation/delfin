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


class ViewBuilder(object):
    def __init__(self, base_url):
        """Initialize ViewBuilder.

        :param base_url: url of the root wsgi application
        """
        self.base_url = base_url

    def build_storages(self, storages):
        views = [self._build_storage(storages[key])
                 for key in sorted(list(storages.keys()))]
        return dict(storage=views)

    def _build_storage(self, storage):
        view = copy.deepcopy(storage)
        return view

    def build_post_storages(self, structure):
        return dict(storages=structure)
