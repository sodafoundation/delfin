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
from oslo_log import log
LOG = log.getLogger(__name__)


def get_view_builder(req):
    LOG.info("GET view Successful")
    return ViewBuilder(req.application_url)


def get_post_view_builder(req, body):
    LOG.info("POST view successful")
    return ViewBuilder(req.application_url, body)


class ViewBuilder(object):
    """POC : Please remove argument 'body' when calling GET """
    def __init__(self, base_url, body):
        """Initialize ViewBuilder.

        :param base_url: url of the root wsgi application
        """

    # self.base_url = base_url

    def build_storages(self, storages):
        views = copy.deepcopy(storages)
        return dict(storages=views)
