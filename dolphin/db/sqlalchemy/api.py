# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright (c) 2014 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Implementation of SQLAlchemy backend."""

from functools import wraps
import sys
from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import session
from oslo_log import log
from oslo_utils import uuidutils
from sqlalchemy import create_engine, update
from dolphin.db.sqlalchemy import models
from dolphin.db.sqlalchemy.models import Storage, RegistryContext

CONF = cfg.CONF
LOG = log.getLogger(__name__)
_FACADE = None

_DEFAULT_SQL_CONNECTION = 'sqlite:///'
db_options.set_defaults(cfg.CONF,
                        connection=_DEFAULT_SQL_CONNECTION)


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = session.EngineFacade.from_config(cfg.CONF)
    return _FACADE


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def register_db():
    """Create database and tables."""
    models = (Storage,
              RegistryContext
              )
    engine = create_engine(CONF.database.connection, echo=False)
    for model in models:
        model.metadata.create_all(engine)


def storage_access_create(context, values):
    """Create a storage access."""
    register_ref = models.StorageAccess()
    this_session = get_session()
    this_session.begin()
    register_ref.update(values)
    this_session.add(register_ref)
    this_session.commit()
    return register_ref


def storage_access_update(context, storage_access_id, values):
    """Update a storage access with the values dictionary."""
    return NotImplemented


def storage_access_get(context, storage_id):
    """Get a storage access."""
    this_session = get_session()
    this_session.begin()
    storage_access = this_session.query(StorageAccess) \
        .filter(StorageAccess.storage_id == storage_id) \
        .first()
    return storage_access


def storage_access_get_all(context, marker=None, limit=None, sort_keys=None,
                             sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage accesses."""
    this_session = get_session()
    this_session.begin()
    if filters.get('hostname', False):
        storage_access = this_session.query(StorageAccess.hostname).all()
    else:
        storage_access = this_session.query(StorageAccess).all()
    return storage_access


def storage_create(context, values):
    """Add a storage device from the values dictionary."""
    storage_ref = models.Storage()
    this_session = get_session()
    this_session.begin()
    storage_ref.update(values)
    this_session.add(storage_ref)
    this_session.commit()
    return storage_ref


def storage_update(context, storage_id, values):
    """Update a storage device with the values dictionary."""
    return NotImplemented


def storage_get(context, storage_id):
    """Retrieve a storage device."""
    this_session = get_session()
    this_session.begin()
    storage_by_id = this_session.query(Storage) \
        .filter(Storage.id == storage_id) \
        .first()
    return storage_by_id


def storage_get_all(context, marker=None, limit=None, sort_keys=None,
                    sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage devices."""

    this_session = get_session()
    this_session.begin()
    # TODO: need to handle all input parameters
    all_storages = this_session.query(Storage).all()
    return all_storages


def volume_create(context, values):
    """Create a volume from the values dictionary."""
    return NotImplemented


def volume_update(context, volume_id, values):
    """Update a volume with the values dictionary."""
    return NotImplemented


def volume_get(context, volume_id):
    """Get a volume or raise an exception if it does not exist."""
    return NotImplemented


def volume_get_all(context, marker=None, limit=None, sort_keys=None,
                   sort_dirs=None, filters=None, offset=None):
    """Retrieves all volumes."""
    return NotImplemented


def pool_create(context, values):
    """Create a pool from the values dictionary."""
    return NotImplemented


def pool_update(context, pool_id, values):
    """Update a pool withe the values dictionary."""
    return NotImplemented


def pool_get(context, pool_id):
    """Get a pool or raise an exception if it does not exist."""
    return NotImplemented


def pool_get_all(context, marker=None, limit=None, sort_keys=None,
                 sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage pools."""
    return NotImplemented


def disk_create(context, values):
    """Create a disk from the values dictionary."""
    return NotImplemented


def disk_update(context, disk_id, values):
    """Update a disk withe the values dictionary."""
    return NotImplemented


def disk_get(context, disk_id):
    """Get a disk or raise an exception if it does not exist."""
    return NotImplemented


def disk_get_all(context, marker=None, limit=None, sort_keys=None,
                 sort_dirs=None, filters=None, offset=None):
    """Retrieves all disks."""
    return NotImplemented
