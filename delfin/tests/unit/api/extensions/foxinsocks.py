# Copyright 2020 The SODA Authors.
# Copyright 2011 OpenStack LLC.
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

from delfin.api import extensions


class FoxInSocksController(object):

    def index(self, req):
        return "Try to say this Mr. Knox, sir..."


class Foxinsocks(extensions.ExtensionDescriptor):
    """The Fox In Socks Extension."""

    name = "Fox In Socks"
    alias = "FOXNSOX"
    namespace = "http://www.fox.in.socks/api/ext/pie/v1.0"
    updated = "2011-01-22T13:25:27-06:00"

    def __init__(self, ext_mgr):
        ext_mgr.register(self)

    def get_resources(self):
        resources = []
        resource = extensions.ResourceExtension('foxnsocks',
                                                FoxInSocksController())
        resources.append(resource)
        return resources

    def get_controller_extensions(self):
        return []
