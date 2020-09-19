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

import random

import decorator
import math
import six
import time
from oslo_config import cfg
from oslo_log import log
from oslo_utils import uuidutils

from delfin import exception
from delfin.drivers import driver

CONF = cfg.CONF

fake_opts = [
    cfg.StrOpt('fake_pool_range',
               default='1-100',
               help='The range of pool number for one device.'),
    cfg.StrOpt('fake_volume_range',
               default='1-2000',
               help='The range of volume number for one device.'),
    cfg.StrOpt('fake_api_time_range',
               default='0.1-0.5',
               help='The range of time cost for each API.'),
    cfg.StrOpt('fake_page_query_limit',
               default='500',
               help='The limitation of volumes for each query.'),
]

CONF.register_opts(fake_opts, "fake_driver")

LOG = log.getLogger(__name__)

MIN_WAIT, MAX_WAIT = 0.1, 0.5
MIN_POOL, MAX_POOL = 1, 100
MIN_VOLUME, MAX_VOLUME = 1, 2000
PAGE_LIMIT = 500


def get_range_val(range_str, t):
    try:
        rng = range_str.split('-')
        if len(rng) != 2:
            raise exception.InvalidInput
        min_val = t(rng[0])
        max_val = t(rng[1])
        return min_val, max_val
    except Exception:
        LOG.error("Invalid range: {0}".format(range_str))
        raise exception.InvalidInput


def wait_random(low, high):
    @decorator.decorator
    def _wait(f, *a, **k):
        rd = random.randint(0, 100)
        secs = low + (high - low) * rd / 100
        time.sleep(secs)
        return f(*a, **k)

    return _wait


class FakeStorageDriver(driver.StorageDriver):
    """FakeStorageDriver shows how to implement the StorageDriver,
    it also plays a role as faker to fake data for being tested by clients.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global MIN_WAIT, MAX_WAIT, MIN_POOL, MAX_POOL, MIN_VOLUME, MAX_VOLUME
        global PAGE_LIMIT
        MIN_WAIT, MAX_WAIT = get_range_val(
            CONF.fake_driver.fake_api_time_range, float)
        MIN_POOL, MAX_POOL = get_range_val(
            CONF.fake_driver.fake_pool_range, int)
        MIN_VOLUME, MAX_VOLUME = get_range_val(
            CONF.fake_driver.fake_volume_range, int)
        PAGE_LIMIT = int(CONF.fake_driver.fake_page_query_limit)

    def reset_connection(self, context, **kwargs):
        pass

    @wait_random(MIN_WAIT, MAX_WAIT)
    def get_storage(self, context):
        # Do something here
        sn = six.text_type(uuidutils.generate_uuid())
        total, used, free = self._get_random_capacity()
        raw = random.randint(3004960000, 4194960000)
        subscribed = random.randint(4194960000, 4294960000)
        return {
            'name': 'fake_driver',
            'description': 'fake driver.',
            'vendor': 'fake_vendor',
            'model': 'fake_model',
            'status': 'normal',
            'serial_number': sn,
            'firmware_version': '1.0.0',
            'location': 'HK',
            'total_capacity': total,
            'used_capacity': used,
            'free_capacity': free,
            'raw_capacity': raw,
            'subscribed_capacity': subscribed
        }

    @wait_random(MIN_WAIT, MAX_WAIT)
    def list_storage_pools(self, ctx):
        rd_pools_count = random.randint(MIN_POOL, MAX_POOL)
        LOG.info("###########fake_pools number for %s: %d" % (self.storage_id,
                                                              rd_pools_count))
        pool_list = []
        for idx in range(rd_pools_count):
            total, used, free = self._get_random_capacity()
            p = {
                "name": "fake_pool_" + str(idx),
                "storage_id": self.storage_id,
                "native_storage_pool_id": "fake_original_id_" + str(idx),
                "description": "Fake Pool",
                "status": "normal",
                "total_capacity": total,
                "used_capacity": used,
                "free_capacity": free,
            }
            pool_list.append(p)
        return pool_list

    def list_volumes(self, ctx):
        # Get a random number as the volume count.
        # rd_volumes_count = random.randint(MIN_VOLUME, MAX_VOLUME)
        rd_volumes_count = random.randint(MIN_VOLUME, MAX_VOLUME)
        LOG.info("###########fake_volumes number for %s: %d" % (
            self.storage_id, rd_volumes_count))
        loops = math.ceil(rd_volumes_count / PAGE_LIMIT)
        volume_list = []
        for idx in range(loops):
            start = idx * PAGE_LIMIT
            end = (idx + 1) * PAGE_LIMIT
            if idx == (loops - 1):
                end = rd_volumes_count
            vs = self._get_volume_range(start, end)
            volume_list = volume_list + vs
        return volume_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        pass

    def clear_alert(self, context, alert):
        pass

    def list_alerts(self, context, query_para=None):
        alert_list = [{
            'alert_id': '19660818',
            'sequence_number': 100,
            'alert_name': 'SNMP connect failed',
            'category': 'Fault',
            'severity': 'Major',
            'type': 'OperationalViolation',
            'location': 'NetworkEntity=entity1',
            'description': "SNMP connection to the storage failed.",
            'recovery_advice': "Check snmp configurations.",
            'occur_time': 13445566902
        }, {
            'alert_id': '19660819',
            'sequence_number': 101,
            'alert_name': 'Link state down',
            'category': 'Fault',
            'severity': 'Critical',
            'type': 'CommunicationsAlarm',
            'location': 'NetworkEntity=entity2',
            'description': "Backend link has gone down",
            'recovery_advice': "Recheck the network configuration setting.",
            'occur_time': 13445566900
        }, {
            'alert_id': '19660820',
            'sequence_number': 102,
            'alert_name': 'Power failure',
            'category': 'Fault',
            'severity': 'Fatal',
            'type': 'OperationalViolation',
            'location': 'NetworkEntity=entity3',
            'description': "Power failure occurred. ",
            'recovery_advice': "Investigate power connection.",
            'occur_time': 13445558900
        }, {
            'alert_id': '19660821',
            'sequence_number': 103,
            'alert_name': 'Communication failure',
            'category': 'Fault',
            'severity': 'Critical',
            'type': 'CommunicationsAlarm',
            'location': 'NetworkEntity=network1',
            'description': "Communication link gone down",
            'recovery_advice': "Consult network administrator",
            'occur_time': 17445544900
        }]
        return alert_list

    @wait_random(MIN_WAIT, MAX_WAIT)
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

    def _get_random_capacity(self):
        total = random.randint(1004960000, 3004960000)
        used = int(random.randint(0, 100) * total / 100)
        free = total - used
        return total, used, free
