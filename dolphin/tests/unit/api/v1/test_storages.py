import sys
import mock

import pytest

from dolphin import context
from dolphin import exception
from webob import exc

sys.modules['dolphin.cryptor'] = mock.MagicMock()
from dolphin.api.v1.storages import StorageController
from dolphin.task_manager.tasks import task
from tooz import coordination as tooz_coordination


class Request:
    def __init__(self):
        self.environ = {'dolphin.context': context.RequestContext()}


class TestStorageController:
    def test_delete(self, mocker):
        # For StorageController.__init__
        mocker.patch('dolphin.task_manager.rpcapi.TaskAPI.__init__',
                     return_value=None)
        # For StorageController.delete
        mock_remove_storage_resource = mocker.patch(
            'dolphin.task_manager.rpcapi.TaskAPI.remove_storage_resource')
        mock_remove_storage_in_cache = mocker.patch(
            'dolphin.task_manager.rpcapi.TaskAPI.remove_storage_in_cache')
        mocker.patch(
            'dolphin.coordination.Lock.__init__', return_value=None)
        mocker.patch('dolphin.coordination.Lock.__enter__')
        mocker.patch('dolphin.coordination.Lock.__exit__')

        sc = StorageController()
        req = Request()

        # Get storage failed, expect to get exc.HTTPBadRequest
        mocker.patch('dolphin.db.storage_get',
                     side_effect=exception.StorageNotFound(
                         id='83df8a62-9ae4-4ffc-9948-5524cc7cdd64'))
        with pytest.raises(exc.HTTPBadRequest):
            sc.delete(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        mocker.patch('dolphin.db.storage_get')

        # Get any one of task lock failed
        # Expect to get tooz_coordination.LockAcquireFailed
        mocker.patch('dolphin.coordination.Lock.__enter__',
                     side_effect=tooz_coordination.LockAcquireFailed(
                         'can not acquire the lock'))
        with pytest.raises(exc.HTTPBadRequest):
            sc.delete(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        mocker.patch('dolphin.coordination.Lock.__enter__')

        # Get storage successfully, call remove_storage_resource
        # Call count depends on the StorageResourceTask's subclasses' count
        sc.delete(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        expected_count = 0
        for _ in task.StorageResourceTask.__subclasses__():
            expected_count += 1
        assert expected_count == mock_remove_storage_resource.call_count
        assert 1 == mock_remove_storage_in_cache.call_count

    def test_sync(self, mocker):
        # For StorageController.__init__
        mocker.patch('dolphin.task_manager.rpcapi.TaskAPI.__init__',
                     return_value=None)
        # For StorageController.sync
        mock_sync_storage_resource = mocker.patch(
            'dolphin.task_manager.rpcapi.TaskAPI.sync_storage_resource')
        mocker.patch(
            'dolphin.coordination.Lock.__init__', return_value=None)
        mocker.patch('dolphin.coordination.Lock.__enter__')
        mocker.patch('dolphin.coordination.Lock.__exit__')

        sc = StorageController()
        req = Request()

        # Get storage failed, expect to get exc.HTTPBadRequest
        mocker.patch('dolphin.db.storage_get',
                     side_effect=exception.StorageNotFound(
                         id='83df8a62-9ae4-4ffc-9948-5524cc7cdd64'))
        with pytest.raises(exc.HTTPNotFound):
            sc.sync(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        mocker.patch('dolphin.db.storage_get')

        # Get any one of task lock failed
        # Expect to get tooz_coordination.LockAcquireFailed
        mocker.patch('dolphin.coordination.Lock.__enter__',
                     side_effect=tooz_coordination.LockAcquireFailed(
                         'can not acquire the lock'))
        with pytest.raises(exc.HTTPBadRequest):
            sc.sync(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        mocker.patch('dolphin.coordination.Lock.__enter__')

        # Get storage successfully, call sync_storage_resource
        # Call count depends on the StorageResourceTask's subclasses' count
        sc.sync(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        expected_count = 0
        for _ in task.StorageResourceTask.__subclasses__():
            expected_count += 1
        assert expected_count == mock_sync_storage_resource.call_count
