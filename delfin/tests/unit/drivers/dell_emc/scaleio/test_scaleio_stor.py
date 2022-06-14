# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from delfin import context
from unittest import TestCase, mock


from delfin.drivers.dell_emc.scaleio.scaleio_stor import ScaleioStorageDriver
from delfin.drivers.dell_emc.scaleio.rest_handler import RestHandler
from delfin.tests.unit.drivers.dell_emc.scaleio import test_constans


sys.modules['delfin.cryptor'] = mock.Mock()

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "scaleio",
    "rest": {
        "host": "8.44.162.250",
        "port": 443,
        "username": "admin",
        "password": "Pbu4@123"
    }
}


class TestScaleIOStorDriver(TestCase):
    RestHandler.login = mock.Mock(return_value=None)

    def test_get_storage(self):
        RestHandler.get_rest_info = mock.Mock(side_effect=[
            test_constans.SYSTEM_INFO, test_constans.SYSTEM_DETAIL])
        RestHandler.list_disks = mock.Mock(side_effect=[test_constans.
                                           SYSTEM_STORAGE_DISK])
        system_storage = ScaleioStorageDriver(**ACCESS_INFO).\
            get_storage(context)
        self.assertEqual(system_storage, test_constans.SYSTEM_STORAGE)

    def test_list_storage_pool(self):
        RestHandler.get_rest_info = mock.Mock(side_effect=[
            test_constans.SYSTEM_STORAGE_POOL_INFO,
            test_constans.SYSTEM_POOL_DETAIL])
        storage_pool = ScaleioStorageDriver(**ACCESS_INFO)\
            .list_storage_pools(context)
        self.assertEqual(storage_pool, test_constans.SYSTEM_STORAGE_POOL)

    def test_list_volume(self):
        RestHandler.get_rest_info = mock.Mock(side_effect=[
            test_constans.SYSTEM_STORAGE_VOLUME_INFO,
            test_constans.SYSTEM_VOLUME_DETAIL])
        storage_volumes = ScaleioStorageDriver(**ACCESS_INFO)\
            .list_volumes(context)
        self.assertEqual(storage_volumes, test_constans.SYSTEM_STORAGE_VOLUME)

    def test_list_alert(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[test_constans.SYSTEM_ALERT_INFO])
        storage_alert = ScaleioStorageDriver(**ACCESS_INFO).\
            list_alerts(context)
        alert_result = test_constans.SYSTEM_ALERT
        alert_result[0]['occur_time'] = storage_alert[0]['occur_time']
        self.assertEqual(storage_alert, alert_result)

    def test_list_storage_host_initiators(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[test_constans.SYSTEM_INITIATORS_INFO])
        RestHandler.list_storage_hosts = mock.Mock(
            side_effect=[test_constans.SYSTEM_HOST])
        storage_initiators = ScaleioStorageDriver(**ACCESS_INFO). \
            list_storage_host_initiators(context)
        self.assertEqual(storage_initiators, test_constans.SYSTEM_INITIATORS)

    def test_list_masking_views(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[test_constans.SYSTEM_STORAGE_VOLUME_INFO])
        storage_mapping = ScaleioStorageDriver(**ACCESS_INFO). \
            list_masking_views(context)
        self.assertEqual(storage_mapping, test_constans.SYSTEM_VIEW_MAPPING)

    def test_list_hosts(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[test_constans.SYSTEM_HOST_INFO])
        storage_host = ScaleioStorageDriver(**ACCESS_INFO)\
            .list_storage_hosts(context)
        self.assertEqual(storage_host, test_constans.SYSTEM_HOST)

    def test_parse_alert(self):
        trap_alert = test_constans.SYSTEM_TRAP_ALERT
        storage_trap_alert = ScaleioStorageDriver(**ACCESS_INFO).\
            parse_alert(context, trap_alert)
        trap_alert_result = test_constans.SYSTEM_TRAP
        trap_alert_result['occur_time'] = storage_trap_alert['occur_time']
        self.assertEqual(storage_trap_alert, trap_alert_result)
