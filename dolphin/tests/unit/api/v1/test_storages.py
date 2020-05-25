import sys
import mock

import pytest

from dolphin import context
from dolphin import exception

sys.modules['dolphin.cryptor'] = mock.MagicMock()
from dolphin.api.v1.storages import StorageController
from dolphin.task_manager.tasks import task


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

        sc = StorageController()
        req = Request()

        # Get storage successfully, call remove_storage_resource
        # Call count depends on the StorageResourceTask's subclasses' count
        mocker.patch('dolphin.db.storage_get')
        sc.delete(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        expected_count = 0
        for _ in task.StorageResourceTask.__subclasses__():
            expected_count += 1
        assert expected_count == mock_remove_storage_resource.call_count
        assert 1 == mock_remove_storage_in_cache.call_count

        # Get storage failed, raise exception,
        # do not call remove_storage_resource
        mock_remove_storage_resource.reset_mock()
        mocker.patch('dolphin.db.storage_get',
                     side_effect=exception.StorageNotFound(
                         id='83df8a62-9ae4-4ffc-9948-5524cc7cdd64'))
        with pytest.raises(Exception):
            sc.delete(req, '83df8a62-9ae4-4ffc-9948-5524cc7cdd64')
        assert 0 == mock_remove_storage_resource.call_count
