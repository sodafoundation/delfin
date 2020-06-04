import unittest

from sqlalchemy.testing import mock
from dolphin.db.sqlalchemy import api
from dolphin import context, exception


class Request:
    def __init__(self):
        self.environ = {'dolphin.context': context.RequestContext()}


class TestSIMDBAPI(unittest.TestCase):
    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_storage_get(self, mock_session):
        fake_storage = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = api.storage_get(context,
                                 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        assert len(result) == 0

        mock_session.return_value.__enter__.return_value.query.return_value \
            = None
        result = api.storage_get(context,
                                 'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        assert result, exception.StorageNotFound(
            id='c5c91c98-91aa-40e6-85ac-37a1d3b32bda')

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_storage_get_all(self, mock_session):
        fake_storage = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = api.storage_get_all(context)
        assert len(result) == 0

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_pool_get(self, mock_session):
        fake_pool = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_pool
        result = api.pool_get(context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_pool_get_all(self, mock_session):
        fake_pool = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_pool
        result = api.pool_get_all(context)
        assert len(result) == 0

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_pools_update(self, mock_session):
        pools = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = pools
        result = api.pools_update(context, pools)
        assert len(result) == 1

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_update(self, mock_session):
        values = {'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = values
        result = api.pool_update(context,
                                 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd',
                                 values)
        assert len(result) == 0

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_volume_get(self, mock_session):
        fake_volume = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = api.pool_get(context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_volume_get_all(self, mock_session):
        fake_volume = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = api.volume_get_all(context)
        assert len(result) == 0

    @mock.patch('dolphin.db.sqlalchemy.api.get_session')
    def test_alert_source_get_all(self, mock_session):
        alert_source = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = alert_source
        result = api.alert_source_get_all(context)
        assert len(result) == 0
