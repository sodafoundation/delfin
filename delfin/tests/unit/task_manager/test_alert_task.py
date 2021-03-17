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
from unittest import mock

from delfin import context
from delfin import db
from delfin import exception
from delfin import test
from delfin.common import constants
from delfin.task_manager.tasks import alerts

fake_storage = {
    'id': '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6',
    'name': 'fake_driver',
    'description': 'it is a fake driver.',
    'vendor': 'fake_vendor',
    'model': 'fake_model',
    'status': 'normal',
    'serial_number': '2102453JPN12KA000011',
    'firmware_version': '1.0.0',
    'location': 'HK',
    'total_capacity': 1024 * 1024,
    'used_capacity': 3126,
    'free_capacity': 1045449,
}

fake_alerts = [
    {
        'alert_id': '1050',
        'alert_name': 'SAMPLE_ALERT_NAME',
        'severity': constants.Severity.WARNING,
        'category': constants.Category.NOT_SPECIFIED,
        'type': constants.EventType.EQUIPMENT_ALARM,
        'sequence_number': 79,
        'description': 'Diagnostic event trace triggered.',
        'recovery_advice': 'NA',
        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
        'location': 'Array id=000192601409,Component type=location1 '
                    'Group,Component name=comp1,Event source=symmetrix',
    },
    {
        'alert_id': '2000',
        'alert_name': 'SAMPLE_ALERT_NAME_2',
        'severity': constants.Severity.CRITICAL,
        'category': constants.Category.RECOVERY,
        'type': constants.EventType.PROCESSING_ERROR_ALARM,
        'sequence_number': 50,
        'description': 'This is a fake alert.',
        'recovery_advice': 'NA',
        'resource_type': constants.DEFAULT_RESOURCE_TYPE,
        'location': 'Array id=000192601409,Component type=location1 '
                    'Group,Component name=comp1,Event source=symmetrix',
    },
]


class TestAlertTask(test.TestCase):

    @mock.patch.object(db, 'storage_get',
                       mock.Mock(return_value=fake_storage))
    @mock.patch('delfin.exporter.base_exporter.AlertExporterManager.dispatch')
    @mock.patch('delfin.common.alert_util.fill_storage_attributes')
    @mock.patch('delfin.drivers.api.API.list_alerts')
    def test_sync_alerts(self, mock_list_alerts,
                         mock_fill_storage_attributes, mock_dispatch):
        task = alerts.AlertSyncTask()
        storage_id = fake_storage['id']
        # No alert
        mock_list_alerts.return_value = []
        task.sync_alerts(context, storage_id, None)
        self.assertEqual(db.storage_get.call_count, 1)
        self.assertEqual(mock_list_alerts.call_count, 1)
        self.assertEqual(mock_dispatch.call_count, 0)
        self.assertEqual(mock_fill_storage_attributes.call_count, 0)
        # Has alert
        mock_list_alerts.return_value = fake_alerts
        task.sync_alerts(context, storage_id, None)
        self.assertEqual(db.storage_get.call_count, 2)
        self.assertEqual(mock_list_alerts.call_count, 2)
        self.assertEqual(mock_dispatch.call_count, 1)
        self.assertEqual(mock_fill_storage_attributes.call_count,
                         len(fake_alerts))

    @mock.patch('delfin.drivers.api.API.clear_alert')
    def test_clear_alerts(self, mock_clear_alert):
        task = alerts.AlertSyncTask()
        storage_id = fake_storage['id']
        task.clear_alerts(context, storage_id, [])
        self.assertEqual(mock_clear_alert.call_count, 0)

        sequence_number_list = ['sequence_number_1', 'sequence_number_2']
        task.clear_alerts(context, storage_id, sequence_number_list)
        self.assertEqual(mock_clear_alert.call_count,
                         len(sequence_number_list))

        mock_clear_alert.side_effect = \
            exception.AccessInfoNotFound(storage_id)
        ret = task.clear_alerts(context, storage_id, sequence_number_list)
        self.assertEqual(ret, [])

        mock_clear_alert.side_effect = \
            exception.Invalid('Fake exception')
        ret = task.clear_alerts(context, storage_id, sequence_number_list)
        self.assertEqual(ret, sequence_number_list)
