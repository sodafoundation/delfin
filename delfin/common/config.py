# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright 2012 Red Hat, Inc.
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

"""Command-line flag library.

Emulates gflags by wrapping cfg.ConfigOpts.

The idea is to move fully to cfg eventually, and this wrapper is a
stepping stone.

"""

import socket

from oslo_config import cfg
from oslo_log import log
from oslo_middleware import cors
from oslo_utils import netutils


CONF = cfg.CONF
log.register_options(CONF)


core_opts = [
    cfg.StrOpt('state_path',
               default='/var/lib/delfin',
               help="Top-level directory for maintaining delfin's state."),
]

CONF.register_cli_opts(core_opts)

global_opts = [
    cfg.HostAddressOpt('my_ip',
                       default=netutils.get_my_ipv4(),
                       sample_default='<your_ip>',
                       help='IP address of this host.'),
    cfg.HostAddressOpt('host',
                       default=socket.gethostname(),
                       sample_default='<your_hostname>',
                       help='Name of this node.  This can be an opaque '
                            'identifier. It is not necessarily a hostname, '
                            'FQDN, or IP address.'),
    cfg.ListOpt('delfin_api_ext_list',
                default=[],
                help='Specify list of extensions to load when using '
                     'delfin_api_extension option with '
                     'delfin.api.contrib.select_extensions.'),
    cfg.ListOpt('delfin_api_extension',
                default=['delfin.api.contrib.standard_extensions'],
                help='The delfin api extensions to load.'),
    cfg.BoolOpt('monkey_patch',
                default=False,
                help='Whether to log monkey patching.'),
    cfg.ListOpt('monkey_patch_modules',
                default=[],
                help='List of modules or decorators to monkey patch.'),
    cfg.IntOpt('service_down_time',
               default=60,
               help='Maximum time since last check-in for up service.'),
    cfg.StrOpt('task_manager',
               default='delfin.task_manager.manager.TaskManager',
               help='Full class name for the task manager.'),
    cfg.StrOpt('delfin_task_topic',
               default='delfin-task',
               help='The topic task manager nodes listen on.'),
    cfg.StrOpt('delfin_alert_topic',
               default='delfin-alert',
               help='The topic alert manager nodes listen on.'),
    cfg.StrOpt('alert_manager',
               default='delfin.alert_manager.trap_receiver.TrapReceiver',
               help='Full class name for the trap receiver.'),
    cfg.StrOpt('delfin_cryptor',
               default='delfin.cryptor._Base64',
               help='cryptor type'),
    cfg.IntOpt('sync_task_expiration',
               default=1800,
               help='Sync task expiration in seconds.'),
    cfg.BoolOpt('snmp_validation_enabled',
                default=True,
                help='Whether alert source configuration to be validated '
                     'through snmp connectivity.'),
]

CONF.register_opts(global_opts)


storage_driver_opts = [
    cfg.StrOpt('ca_path',
               default='',
               help='"": Disable SSL certificate verification, '
                    '/path/to/file: Use SSL certificate from file location')
]

CONF.register_opts(storage_driver_opts, group='storage_driver')


def set_middleware_defaults():
    """Update default configuration options for oslo.middleware."""
    cors.set_defaults(
        allow_headers=['X-Auth-Token',
                       'X-OpenStack-Request-ID',
                       'X-Identity-Status',
                       'X-Roles',
                       'X-Service-Catalog',
                       'X-User-Id',
                       'X-Tenant-Id'],
        expose_headers=['X-Auth-Token',
                        'X-OpenStack-Request-ID',
                        'X-Subject-Token',
                        'X-Service-Token'],
        allow_methods=['GET',
                       'PUT',
                       'POST',
                       'DELETE',
                       'PATCH']
    )
