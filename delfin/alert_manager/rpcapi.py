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
Client side of the alert manager RPC API.
"""

import oslo_messaging as messaging
from oslo_config import cfg

from delfin import rpc

CONF = cfg.CONF


class AlertAPI(object):
    """Client side of the alert manager rpc API.

    API version history:
        1.0 - Initial version.
    """

    RPC_API_VERSION = '1.0'

    def __init__(self):
        super(AlertAPI, self).__init__()
        target = messaging.Target(topic=CONF.delfin_alert_topic,
                                  version=self.RPC_API_VERSION)
        self.client = rpc.get_client(target, version_cap=self.RPC_API_VERSION)

    def sync_snmp_config(self, ctxt, snmp_config_to_del, snmp_config_to_add):
        call_context = self.client.prepare(version='1.0', fanout=True)
        return call_context.cast(ctxt,
                                 'sync_snmp_config',
                                 snmp_config_to_del=snmp_config_to_del,
                                 snmp_config_to_add=snmp_config_to_add)

    def check_snmp_config(self, ctxt, snmp_config):
        call_context = self.client.prepare(version='1.0')
        return call_context.cast(ctxt,
                                 'check_snmp_config',
                                 snmp_config=snmp_config)
