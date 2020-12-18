from unittest import mock

from delfin import context, exception
from delfin import test
from delfin.db import api as db_api
from delfin.db.sqlalchemy import api, models

ctxt = context.get_admin_context()


class TestSIMDBAPI(test.TestCase):

    @mock.patch('sqlalchemy.create_engine', mock.Mock())
    def test_register_db(self):
        db_api.register_db()

    def test_get_session(self):
        api.get_session()

    def test_get_engine(self):
        api.get_engine()

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_get(self, mock_session):
        fake_storage = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = db_api.storage_get(ctxt,
                                    'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_update(self, mock_session):
        fake_storage = models.Storage()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = db_api.storage_update(ctxt,
                                       'c5c91c98-91aa-40e6-85ac-37a1d3b32bda',
                                       fake_storage)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_delete(self, mock_session):
        fake_storage = models.Storage()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = db_api.storage_delete(ctxt,
                                       'c5c91c98-91aa-40e6-85ac-37a1d3b32bda')
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_create(self, mock_session):
        fake_storage = models.Storage()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = db_api.storage_create(ctxt, fake_storage)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_get_all(self, mock_session):
        fake_storage = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage
        result = db_api.storage_get_all(ctxt)
        assert len(result) == 0

        mock_session.return_value.__enter__.return_value.query = fake_storage
        result = db_api.storage_get_all(ctxt, filters={'status': 'Normal'})
        assert len(result) == 0

        result = db_api.storage_get_all(ctxt, limit=1)
        assert len(result) == 0

        result = db_api.storage_get_all(ctxt, offset=3)
        assert len(result) == 0

        result = db_api.storage_get_all(ctxt, sort_dirs=['desc'],
                                        sort_keys=['name'])
        assert len(result) == 0

        self.assertRaises(exception.InvalidInput, api.storage_get_all,
                          ctxt, sort_dirs=['desc', 'asc'],
                          sort_keys=['name'])

        self.assertRaises(exception.InvalidInput, api.storage_get_all,
                          ctxt, sort_dirs=['desc_err'],
                          sort_keys=['name'])

        result = db_api.storage_get_all(ctxt, sort_dirs=['desc'],
                                        sort_keys=['name', 'id'])
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pool_get(self, mock_session):
        fake_storage_pool = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage_pool
        result = db_api.storage_pool_get(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pool_get_all(self, mock_session):
        fake_storage_pool = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage_pool
        result = api.storage_pool_get_all(context)
        assert len(result) == 0

        result = db_api.storage_pool_get_all(context,
                                             filters={'status': 'Normal'})
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pools_update(self, mock_session):
        storage_pools = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = storage_pools
        result = db_api.storage_pools_update(context, storage_pools)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pool_update(self, mock_session):
        values = {'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = values
        result = db_api.storage_pool_update(
            context, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd', values)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pools_delete(self, mock_session):
        fake_storage_pools = [models.StoragePool().id]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage_pools
        result = db_api.storage_pools_delete(context, fake_storage_pools)
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pools_create(self, mock_session):
        fake_storage_pools = [models.StoragePool()]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage_pools
        result = db_api.storage_pools_create(context, fake_storage_pools)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_storage_pool_create(self, mock_session):
        fake_storage_pool = models.StoragePool()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_storage_pool
        result = db_api.storage_pool_create(context, fake_storage_pool)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volume_get(self, mock_session):
        fake_volume = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = db_api.volume_get(ctxt,
                                   'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volumes_update(self, mock_session):
        volumes = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = volumes
        result = db_api.volumes_update(ctxt, volumes)
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volume_update(self, mock_session):
        volumes = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = volumes
        result = db_api.volume_update(ctxt,
                                      'c5c91c98-91aa-40e6-85ac-37a1d3b32bd',
                                      volumes)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volumes_delete(self, mock_session):
        fake_volume = ['c5c91c98-91aa-40e6-85ac-37a1d3b32bd']
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = db_api.volumes_delete(ctxt, fake_volume)
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volumes_create(self, mock_session):
        fake_volume = [models.Volume()]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = db_api.volumes_create(ctxt, fake_volume)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volume_create(self, mock_session):
        fake_volume = models.Volume()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = db_api.volume_create(ctxt, fake_volume)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_volume_get_all(self, mock_session):
        fake_volume = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_volume
        result = db_api.volume_get_all(ctxt)
        assert len(result) == 0

        result = db_api.volume_get_all(ctxt, filters={'status': 'Normal'})
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controller_get(self, mock_session):
        fake_controller = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_controller
        result = db_api.controller_get(ctxt,
                                       'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controllers_update(self, mock_session):
        controllers = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = controllers
        result = db_api.controllers_update(ctxt, controllers)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controller_update(self, mock_session):
        controllers = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = controllers
        result = db_api.controller_update(
            ctxt, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd', controllers)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controllers_delete(self, mock_session):
        fake_controller = ['c5c91c98-91aa-40e6-85ac-37a1d3b32bd']
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_controller
        result = db_api.controllers_delete(ctxt, fake_controller)
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controllers_create(self, mock_session):
        fake_controller = [models.Volume()]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_controller
        result = db_api.controllers_create(ctxt, fake_controller)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controller_create(self, mock_session):
        fake_controller = models.Volume()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_controller
        result = db_api.controller_create(ctxt, fake_controller)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_controller_get_all(self, mock_session):
        fake_controller = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_controller
        result = db_api.controller_get_all(ctxt)
        assert len(result) == 0

        result = db_api.controller_get_all(ctxt, filters={'status': 'Normal'})
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_port_get(self, mock_session):
        fake_port = {}
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_port
        result = db_api.port_get(ctxt,
                                 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_ports_update(self, mock_session):
        ports = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = ports
        result = db_api.ports_update(ctxt, ports)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_port_update(self, mock_session):
        ports = [{'id': 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd'}]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = ports
        result = db_api.port_update(ctxt,
                                    'c5c91c98-91aa-40e6-85ac-37a1d3b32bd',
                                    ports)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_ports_delete(self, mock_session):
        fake_port = ['c5c91c98-91aa-40e6-85ac-37a1d3b32bd']
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_port
        result = db_api.ports_delete(ctxt, fake_port)
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_ports_create(self, mock_session):
        fake_port = [models.Volume()]
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_port
        result = db_api.ports_create(ctxt, fake_port)
        assert len(result) == 1

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_port_create(self, mock_session):
        fake_port = models.Volume()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_port
        result = db_api.port_create(ctxt, fake_port)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_port_get_all(self, mock_session):
        fake_port = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_port
        result = db_api.port_get_all(ctxt)
        assert len(result) == 0

        result = db_api.port_get_all(ctxt, filters={'status': 'Normal'})
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_access_info_get_all(self, mock_session):
        fake_access_info = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_access_info
        result = db_api.access_info_get_all(ctxt)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_access_info_get(self, mock_session):
        fake_access_info = models.AccessInfo()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_access_info
        result = db_api.access_info_get(ctxt,
                                        'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_access_info_create(self, mock_session):
        fake_access_info = models.AccessInfo()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_access_info
        result = db_api.access_info_create(ctxt, fake_access_info)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_access_info_update(self, mock_session):
        fake_access_info = models.AccessInfo()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_access_info
        result = db_api.access_info_update(
            ctxt, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd', fake_access_info)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_alert_source_get_all(self, mock_session):
        fake_alert_source = []
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_alert_source
        result = db_api.alert_source_get_all(ctxt)
        assert len(result) == 0

        result = db_api.alert_source_get_all(ctxt,
                                             filters={'status': 'Normal'})
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_alert_source_update(self, mock_session):
        fake_alert_source = models.AlertSource()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_alert_source
        result = db_api.alert_source_update(
            ctxt, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd', fake_alert_source)
        assert len(result) == 0

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_alert_source_delete(self, mock_session):
        fake_alert_source = models.AlertSource()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_alert_source
        result = db_api.alert_source_delete(
            ctxt, 'c5c91c98-91aa-40e6-85ac-37a1d3b32bd')
        assert result is None

    @mock.patch('delfin.db.sqlalchemy.api.get_session')
    def test_alert_source_create(self, mock_session):
        fake_alert_source = models.AlertSource()
        mock_session.return_value.__enter__.return_value.query.return_value \
            = fake_alert_source
        result = db_api.alert_source_create(ctxt, fake_alert_source)
        assert len(result) == 0
