# Copyright 2020 The SODA Authors.
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

import six
from oslo_log import log

from delfin import context
from delfin.drivers import driver
from delfin.drivers.hpe.hpe_3par import alert_handler
from delfin.drivers.hpe.hpe_3par import component_handler
from delfin.drivers.hpe.hpe_3par import rest_handler
from delfin.drivers.hpe.hpe_3par import ssh_handler
from delfin.drivers.utils.rest_client import RestClient

LOG = log.getLogger(__name__)


# Hpe3parStor Driver
class Hpe3parStorDriver(driver.StorageDriver):
    """Hpe3parStorDriver implement Hpe 3par Stor driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rest_client = RestClient(**kwargs)
        self.rest_client.verify = kwargs.get('verify', False)
        self.rest_handler = rest_handler.RestHandler(self.rest_client)
        self.rest_handler.login()

        self.ssh_handler = ssh_handler.SSHHandler(**kwargs)
        self.version = self.ssh_handler.login(context)

        self.comhandler = component_handler.ComponentHandler(
            rest_handler=self.rest_handler, ssh_handler=self.ssh_handler)

        self.alert_handler = alert_handler.AlertHandler(
            rest_handler=self.rest_handler, ssh_handler=self.ssh_handler)

    def reset_connection(self, context, **kwargs):
        try:
            self.rest_handler.logout()
        except Exception as e:
            LOG.warning('logout failed when resetting connection, '
                        'reason is %s' % six.text_type(e))
        self.rest_client.verify = kwargs.get('verify', False)
        self.rest_handler.login()

    def close_connection(self):
        self.rest_handler.logout()

    def get_storage(self, context):
        return self.comhandler.get_storage(context)

    def list_storage_pools(self, context):
        self.comhandler.set_storage_id(self.storage_id)
        return self.comhandler.list_storage_pools(context)

    def list_volumes(self, context):
        self.comhandler.set_storage_id(self.storage_id)
        return self.comhandler.list_volumes(context)

    def list_controllers(self, context):
        return self.comhandler.list_controllers(self.storage_id)

    def list_ports(self, context):
        return self.comhandler.list_ports(self.storage_id)

    def list_disks(self, context):
        return self.comhandler.list_disks(self.storage_id)

    def list_alerts(self, context, query_para=None):
        return self.alert_handler.list_alerts(context, query_para)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, alert):
        return self.alert_handler.clear_alert(context, alert)

    def list_filesystems(self, context):
        pass

    def list_qtrees(self, context):
        pass

    def list_shares(self, context):
        pass
