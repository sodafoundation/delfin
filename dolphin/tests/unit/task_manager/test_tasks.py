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


import unittest
from unittest import mock
from dolphin import test, context, coordination
from dolphin.task_manager.tasks import task


class TestStorageDeviceTask(unittest.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.drivers.api.API.get_storage')
    def test_sync_successful(self, mock_get_storage, mock_session, get_lock):
        storage_obj = task.StorageDeviceTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_obj.sync()

        self.assertTrue(get_lock.called)
        self.assertTrue(mock_session.called)
        mock_get_storage.assert_called_with(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')

    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.db.storage_update')
    def test_sync_unsuccessful(self, mock_s_update, mock_session, get_lock):
        storage_obj = task.StorageDeviceTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_obj.sync()

        self.assertTrue(get_lock.called)
        self.assertTrue(mock_session.called)
        self.assertTrue(mock_s_update.called)

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.db.storage_delete')
    @mock.patch('dolphin.db.alert_source_delete')
    def test_successful_remove(self, mock_alert_del, mock_strg_del,
                               mock_session):
        storage_obj = task.StorageDeviceTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        storage_obj.remove()

        self.assertTrue(mock_session.called)
        mock_strg_del.assert_called_with(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        mock_alert_del.assert_called_with(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')


class TestStoragePoolTask(unittest.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.drivers.api.API.list_pools')
    @mock.patch('dolphin.db.pool_get_all')
    def test_sync_successful(self, mock_list_pools, mock_pool_get_all,
                             mock_session, get_lock):
        pool_obj = task.StoragePoolTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        pool_obj.sync()
        self.assertTrue(mock_list_pools.called)
        self.assertTrue(mock_pool_get_all.called)
        self.assertTrue(get_lock.called)
        self.assertTrue(mock_session.called)

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.db.pool_delete_by_storage')
    def test_remove(self, mock_pool_del, mock_session):
        pool_obj = task.StoragePoolTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        pool_obj.remove()


class TestStorageVolumeTask(unittest.TestCase):
    @mock.patch.object(coordination.LOCK_COORDINATOR, 'get_lock')
    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.drivers.api.API.list_volumes')
    @mock.patch('dolphin.db.volume_get_all')
    def test_sync_successful(self, mock_list_vols, mock_vol_get_all,
                             mock_session, get_lock):
        vol_obj = task.StorageVolumeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        vol_obj.sync()
        self.assertTrue(mock_list_vols.called)
        self.assertTrue(mock_vol_get_all.called)
        self.assertTrue(get_lock.called)
        self.assertTrue(mock_session.called)

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    @mock.patch('dolphin.db.volume_delete_by_storage')
    def test_remove(self, mock_vol_del, mock_session):
        vol_obj = task.StorageVolumeTask(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        vol_obj.remove()
