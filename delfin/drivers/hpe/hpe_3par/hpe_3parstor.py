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

from oslo_log import log

from delfin import context
from delfin.drivers import driver
from delfin.drivers.hpe.hpe_3par import alert_handler
from delfin.drivers.hpe.hpe_3par import component_handler
from delfin.drivers.hpe.hpe_3par import rest_handler
from delfin.drivers.hpe.hpe_3par import ssh_handler
from delfin.drivers.utils.rest_client import RestClient
from delfin.drivers.utils.ssh_client import SSHClient

LOG = log.getLogger(__name__)


# Hpe3parStor Driver
class Hpe3parStorDriver(driver.StorageDriver):
    """Hpe3parStorDriver implement Hpe 3par Stor driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # init rest client
        self.restclient = RestClient(**kwargs)
        self.resthanlder = rest_handler.RestHandler(self.restclient)
        self.resthanlder.login()
        # init ssh client
        self.sshclient = SSHClient(**kwargs)
        self.sshhanlder = ssh_handler.SSHHandler(self.sshclient)
        self.version = self.sshhanlder.login(context)
        # init component handler
        self.comhandler = component_handler.ComponentHandler(
            resthanlder=self.resthanlder, sshhanlder=self.sshhanlder)
        # init component handler
        self.alert_handler = alert_handler.AlertHandler(
            resthanlder=self.resthanlder, sshhanlder=self.sshhanlder)

    def reset_connection(self, context, **kwargs):
        self.resthanlder.logout()
        self.restclient.verify = kwargs.get('verify', False)
        self.resthanlder.login()

    def get_storage(self, context):
        # get storage info
        return self.comhandler.get_storage(context)

    def list_storage_pools(self, context):
        # Get list of Hpe3parStor pool details
        self.comhandler.set_storage_id(self.storage_id)
        return self.comhandler.list_storage_pools(context)

    def list_volumes(self, context):
        self.comhandler.set_storage_id(self.storage_id)
        return self.comhandler.list_volumes(context)

    def list_alerts(self, context):
        # Get list of Hpe3parStor alerts
        return self.alert_handler.list_alerts(context)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        return self.alert_handler.parse_alert(context, alert)

    def clear_alert(self, context, alert):
        return self.alert_handler.clear_alert(context, alert)
