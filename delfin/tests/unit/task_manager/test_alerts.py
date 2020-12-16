# Copyright 2020 The SODA Authors.
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

import unittest
from unittest import mock

from oslo_utils import importutils


def fake_alert_list():
    return [{
        'alert_id': '19660818',
        'sequence_number': 10,
        'alert_name': 'SNMP connect failed',
        'category': 'Fault',
        'severity': 'Major',
        'type': 'OperationalViolation',
        'location': 'NetworkEntity=storage1',
        'description': "SNMP connection to the storage failed. "
                       "SNMP traps from storage will not be received.",
        'recovery_advice': "1. The network connection is abnormal. "
                           "2. SNMP authentication parameters "
                           "are invalid.",
        'occur_time': 13445566900
    }]


def fake_storage_info(ctx, storage_id):
    return {
        'id': storage_id,
        'name': 'storage1',
        'vendor': 'fake vendor',
        'model': 'fake model',
        'serial_number': 'serial-1234',
    }


def empty_alert_list():
    return []


def list_alert_exception(self, ctx, fake_storage_id, query_para):
    raise NotImplementedError()


class TestAlertSyncTask(unittest.TestCase):
    ALERT_TASK_CLASS = 'delfin.task_manager.tasks.alerts.AlertSyncTask'

    def _get_alert_sync_task(self):
        alert_task_class = importutils.import_class(
            self.ALERT_TASK_CLASS)
        alert_sync_task = alert_task_class()
        return alert_sync_task

    @mock.patch('delfin.db.storage_get', fake_storage_info)
    @mock.patch('delfin.drivers.api.API.list_alerts')
    @mock.patch('delfin.exporter.base_exporter.AlertExporterManager')
    def test_sync_alerts(self, mock_alert_export, mock_list_alerts):
        ctx = {}
        query_para = {}
        fake_storage_id = 'abcd-1234-5678'
        mock_list_alerts.return_value = fake_alert_list()

        alert_sync_task_inst = self._get_alert_sync_task()
        alert_sync_task_inst.sync_alerts(ctx, fake_storage_id, query_para)
        self.assertTrue(mock_alert_export.called)

    @mock.patch('delfin.db.storage_get', fake_storage_info)
    @mock.patch('delfin.drivers.api.API.list_alerts')
    @mock.patch('delfin.common.alert_util.fill_storage_attributes')
    def test_sync_alerts_empty(self, mock_fill_storage_attributes,
                               mock_list_alerts):
        ctx = {}
        query_para = {}
        fake_storage_id = 'abcd-1234-5678'
        mock_list_alerts.return_value = empty_alert_list()

        alert_sync_task_inst = self._get_alert_sync_task()
        alert_sync_task_inst.sync_alerts(ctx, fake_storage_id, query_para)

        # Verify that when no alerts, filling, exporting alert is not triggered
        self.assertFalse(mock_fill_storage_attributes.called)

    @mock.patch('delfin.db.storage_get', fake_storage_info)
    @mock.patch('delfin.drivers.api.API.list_alerts',
                list_alert_exception)
    @mock.patch('delfin.db.storage_get', fake_storage_info)
    @mock.patch('delfin.drivers.api.API.list_alerts', list_alert_exception)
    @mock.patch('delfin.common.alert_util.fill_storage_attributes')
    def test_sync_alerts_not_implemented(self, mock_fill_storage_attributes):
        ctx = {}
        query_para = {}
        fake_storage_id = 'abcd-1234-5678'

        alert_sync_task_inst = self._get_alert_sync_task()
        alert_sync_task_inst.sync_alerts(ctx, fake_storage_id, query_para)

        # Verify that during error, filling, exporting alert is not triggered
        self.assertFalse(mock_fill_storage_attributes.called)
