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

from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.dell_emc.vmax import client
from delfin.drivers.dell_emc.vmax.alert_handler import snmp_alerts
from delfin.drivers.dell_emc.vmax.alert_handler import unisphere_alerts

LOG = log.getLogger(__name__)


class VMAXStorageDriver(driver.StorageDriver):
    """VMAXStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = client.VMAXClient(**kwargs)
        self.client.init_connection(kwargs)

    def reset_connection(self, context, **kwargs):
        self.client.reset_connection(**kwargs)

    def get_storage(self, context):
        # Get the VMAX model
        array_details = self.client.get_array_details()
        model = array_details['model']
        ucode = array_details['ucode']
        display_name = array_details['display_name']

        # Get Storage details for capacity info
        total_capacity, used_capacity, free_capacity,\
            raw_capacity, subscribed_capacity = \
            self.client.get_storage_capacity()

        storage = {
            # Unisphere Rest API do not provide Array name .
            # Generate  name  by combining model and symmetrixId
            'name': display_name,
            'vendor': 'Dell EMC',
            'description': '',
            'model': model,
            'firmware_version': ucode,
            'status': constants.StorageStatus.NORMAL,
            'serial_number': self.client.array_id,
            'location': '',
            'total_capacity': total_capacity,
            'used_capacity': used_capacity,
            'free_capacity': free_capacity,
            'raw_capacity': raw_capacity,
            'subscribed_capacity': subscribed_capacity
        }
        LOG.info("get_storage(), successfully retrieved storage details")
        return storage

    def list_storage_pools(self, context):
        return self.client.list_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.client.list_volumes(self.storage_id)

    def list_controllers(self, context):
        pass

    def list_ports(self, context):
        pass

    def list_disks(self, context):
        pass

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return snmp_alerts.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, sequence_number):
        return self.client.clear_alert(sequence_number)

    def list_alerts(self, context, query_para):
        alert_list = self.client.list_alerts(query_para)
        alert_model_list = unisphere_alerts.AlertHandler()\
            .parse_queried_alerts(alert_list)
        return alert_model_list

    def collect_perf_metrics(self, context, storage_id,
                             resource_metrics, start_time,
                             end_time):
        # Get interval in seconds
        interval = (end_time - start_time) / 1000
        return self.client.get_array_performance_metrics(self.storage_id,
                                                         interval=interval)
