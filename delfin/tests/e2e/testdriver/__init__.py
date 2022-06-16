# Copyright 2021 The SODA Authors.
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

import random
import datetime
import json
import time
from oslo_log import log

from delfin import exception
from delfin.common import constants
from delfin.common.constants import ResourceType, StorageMetric
from delfin.drivers import driver
from delfin import cryptor


LOG = log.getLogger(__name__)

MIN_STORAGE, MAX_STORAGE = 1, 10
MIN_PERF_VALUES, MAX_PERF_VALUES = 1, 4


class TestDriver(driver.StorageDriver):
    """FakeStorageDriver shows how to implement the StorageDriver,
    it also plays a role as faker to fake data for being tested by clients.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        access_info = kwargs
        if access_info is None:
            raise exception.InvalidInput('Input access_info is missing')

        self.array_json = access_info.get("extra_attributes").get("path")

        with open(self.array_json) as f:
            data = json.load(f)

        # Verify Host & Port
        f_host = data.get("access_info").get("rest").get("host")
        f_port = data.get("access_info").get("rest").get("port")
        f_user = data.get("access_info").get("rest").get("username")
        f_pass = data.get("access_info").get("rest").get("password")
        a_host = access_info.get("rest").get("host")
        a_port = access_info.get("rest").get("port")
        a_user = access_info.get("rest").get("username")
        a_pass = access_info.get("rest").get("password")
        a_pass = cryptor.decode(a_pass)
        if f_host != a_host:
            raise exception.InvalidIpOrPort
        if f_port != a_port:
            raise exception.InvalidIpOrPort
        if f_user != a_user:
            raise exception.InvalidUsernameOrPassword
        if f_pass != a_pass:
            raise exception.InvalidUsernameOrPassword

    def reset_connection(self, context, **kwargs):
        pass

    def get_storage(self, context):
        with open(self.array_json) as f:
            data = json.load(f)
            return data.get('storage')

    def _return_json(self, key):
        with open(self.array_json) as f:
            data = json.load(f)
            values = data.get(key)
            for value in values:
                value['storage_id'] = self.storage_id
            return values

    def list_storage_pools(self, ctx):
        return self._return_json('storage_pools')

    def list_volumes(self, ctx):
        return self._return_json('volumes')

    def list_controllers(self, ctx):
        return self._return_json('controllers')

    def list_ports(self, ctx):
        return self._return_json('ports')

    def list_disks(self, ctx):
        return self._return_json('disks')

    def list_quotas(self, ctx):
        return self._return_json('quotas')

    def list_filesystems(self, ctx):
        return self._return_json('filesystems')

    def list_qtrees(self, ctx):
        return self._return_json('qtrees')

    def list_shares(self, ctx):
        return self._return_json('shares')

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        pass

    def clear_alert(self, context, alert):
        pass

    def list_alerts(self, context, query_para=None):
        alert_list = [{
            "storage_id": self.storage_id,
            'alert_id': str(random.randint(1111111, 9999999)),
            'sequence_number': 100,
            'alert_name': 'SNMP connect failed',
            'category': 'Fault',
            'severity': 'Major',
            'type': 'OperationalViolation',
            'location': 'NetworkEntity=entity1',
            'description': "SNMP connection to the storage failed.",
            'recovery_advice': "Check snmp configurations.",
            'occur_time': int(time.time())
        }, {
            "storage_id": self.storage_id,
            'alert_id': str(random.randint(1111111, 9999999)),
            'sequence_number': 101,
            'alert_name': 'Link state down',
            'category': 'Fault',
            'severity': 'Critical',
            'type': 'CommunicationsAlarm',
            'location': 'NetworkEntity=entity2',
            'description': "Backend link has gone down",
            'recovery_advice': "Recheck the network configuration setting.",
            'occur_time': int(time.time())
        }, {
            "storage_id": self.storage_id,
            'alert_id': str(random.randint(1111111, 9999999)),
            'sequence_number': 102,
            'alert_name': 'Power failure',
            'category': 'Fault',
            'severity': 'Fatal',
            'type': 'OperationalViolation',
            'location': 'NetworkEntity=entity3',
            'description': "Power failure occurred. ",
            'recovery_advice': "Investigate power connection.",
            'occur_time': int(time.time())
        }, {
            "storage_id": self.storage_id,
            'alert_id': str(random.randint(1111111, 9999999)),
            'sequence_number': 103,
            'alert_name': 'Communication failure',
            'category': 'Fault',
            'severity': 'Critical',
            'type': 'CommunicationsAlarm',
            'location': 'NetworkEntity=network1',
            'description': "Communication link gone down",
            'recovery_advice': "Consult network administrator",
            'occur_time': int(time.time())
        }]
        return alert_list

    def _get_volume_range(self, start, end):
        volume_list = []

        for i in range(start, end):
            total, used, free = self._get_random_capacity()
            v = {
                "name": "fake_vol_" + str(i),
                "storage_id": self.storage_id,
                "description": "Fake Volume",
                "status": "normal",
                "native_volume_id": "fake_original_id_" + str(i),
                "wwn": "fake_wwn_" + str(i),
                "total_capacity": total,
                "used_capacity": used,
                "free_capacity": free,
            }
            volume_list.append(v)
        return volume_list

    def _get_random_performance(self):
        def get_random_timestamp_value():
            rtv = {}
            for i in range(MIN_PERF_VALUES, MAX_PERF_VALUES):
                timestamp = int(float(datetime.datetime.now().timestamp()
                                      ) * 1000)
                rtv[timestamp] = random.uniform(1, 100)
            return rtv

        # The sample performance_params after filling looks like,
        # performance_params = {timestamp1: value1, timestamp2: value2}
        performance_params = {}
        for key in constants.DELFIN_ARRAY_METRICS:
            performance_params[key] = get_random_timestamp_value()
        return performance_params

    def collect_array_metrics(self, ctx, storage_id, interval, is_history):
        rd_array_count = random.randint(MIN_STORAGE, MAX_STORAGE)
        LOG.info("Fake_array_metrics number for %s: %d" % (
            storage_id, rd_array_count))
        array_metrics = []
        labels = {'storage_id': storage_id, 'resource_type': 'array'}
        fake_metrics = self._get_random_performance()

        for _ in range(rd_array_count):
            for key in constants.DELFIN_ARRAY_METRICS:
                m = constants.metric_struct(name=key, labels=labels,
                                            values=fake_metrics[key])
                array_metrics.append(m)

        return array_metrics

    @staticmethod
    def get_capabilities(context, filters=None):
        """Get capability of supported driver."""
        return {
            'is_historic': False,
            'resource_metrics': {
                ResourceType.STORAGE: {
                    StorageMetric.THROUGHPUT.name: {
                        "unit": StorageMetric.THROUGHPUT.unit,
                        "description": StorageMetric.THROUGHPUT.description
                    },
                    StorageMetric.RESPONSE_TIME.name: {
                        "unit": StorageMetric.RESPONSE_TIME.unit,
                        "description": StorageMetric.RESPONSE_TIME.description
                    },
                    StorageMetric.READ_RESPONSE_TIME.name: {
                        "unit": StorageMetric.READ_RESPONSE_TIME.unit,
                        "description":
                            StorageMetric.READ_RESPONSE_TIME.description
                    },
                    StorageMetric.WRITE_RESPONSE_TIME.name: {
                        "unit": StorageMetric.WRITE_RESPONSE_TIME.unit,
                        "description":
                            StorageMetric.WRITE_RESPONSE_TIME.description
                    },
                    StorageMetric.IOPS.name: {
                        "unit": StorageMetric.IOPS.unit,
                        "description": StorageMetric.IOPS.description
                    },
                    StorageMetric.READ_THROUGHPUT.name: {
                        "unit": StorageMetric.READ_THROUGHPUT.unit,
                        "description":
                            StorageMetric.READ_THROUGHPUT.description
                    },
                    StorageMetric.WRITE_THROUGHPUT.name: {
                        "unit": StorageMetric.WRITE_THROUGHPUT.unit,
                        "description":
                            StorageMetric.WRITE_THROUGHPUT.description
                    },
                    StorageMetric.READ_IOPS.name: {
                        "unit": StorageMetric.READ_IOPS.unit,
                        "description": StorageMetric.READ_IOPS.description
                    },
                    StorageMetric.WRITE_IOPS.name: {
                        "unit": StorageMetric.WRITE_IOPS.unit,
                        "description": StorageMetric.WRITE_IOPS.description
                    },
                }
            }
        }
