# Copyright 2012, Red Hat, Inc.
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

"""
Client side of the task manager RPC API.
"""

from oslo_config import cfg
import oslo_messaging as messaging
from oslo_serialization import jsonutils

from dolphin import rpc
from dolphin.coordination import LOG

CONF = cfg.CONF


class TaskAPI(object):
    """Client side of the task rpc API.

    API version history:

        1.0 - Initial version.
    """

    RPC_API_VERSION = '1.0'

    def __init__(self):
        super(TaskAPI, self).__init__()
        target = messaging.Target(topic=CONF.dolphin_task_topic,
                                  version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    def get_volumes(self, context, request_spec=None, filter_properties=None):
        request_spec_p = jsonutils.to_primitive(request_spec)
        call_context = self.client.prepare(version='1.0')
        return call_context.cast(context, 'get_volumes',
                                 request_spec=request_spec_p,
                                 filter_properties=filter_properties
                                 )

    def get_pools(self, context, request_spec=None, filter_properties=None):
        request_spec_p = jsonutils.to_primitive(request_spec)
        call_context = self.client.prepare(version='1.0')
        return call_context.cast(context, 'get_pools',
                                 request_spec=request_spec_p,
                                 filter_properties=filter_properties
                                 )
