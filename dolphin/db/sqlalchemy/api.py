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

from dolphin import exception
from dolphin.db.sqlalchemy import models
from dolphin.db.sqlalchemy.models import Storage, AccessInfo
from dolphin.exception import InvalidInput

CONF = cfg.CONF
LOG = log.getLogger(__name__)
_FACADE = None

_DEFAULT_SQL_CONNECTION = 'sqlite:///'
db_options.set_defaults(cfg.CONF,
                        connection=_DEFAULT_SQL_CONNECTION)


def apply_sorting(model, query, sort_key, sort_dir):
    if sort_dir.lower() not in ('desc', 'asc'):
        msg = ("Wrong sorting data provided: sort key is '%(sort_key)s' "
               "and sort order is '%(sort_dir)s'.") % {
                  "sort_key": sort_key, "sort_dir": sort_dir}
        raise exception.InvalidInput(reason=msg)

    sort_attr = getattr(model, sort_key)
    sort_method = getattr(sort_attr, sort_dir.lower())
    return query.order_by(sort_method())


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
              AccessInfo
              )
    engine = create_engine(CONF.database.connection, echo=False)
    for model in models:
        model.metadata.create_all(engine)


def access_info_create(context, values):
    """Create a storage access information."""
    register_ref = models.AccessInfo()
    this_session = get_session()
    this_session.begin()
    register_ref.update(values)
    this_session.add(register_ref)
    this_session.commit()
    return register_ref


def access_info_update(context, access_info_id, values):
    """Update a storage access information with the values dictionary."""
    return NotImplemented


def access_info_get(context, storage_id):
    """Get a storage access information."""
    this_session = get_session()
    this_session.begin()
    access_info = this_session.query(AccessInfo) \
        .filter(AccessInfo.storage_id == storage_id) \
        .first()
    return access_info


def access_info_get_all(context, marker=None, limit=None, sort_keys=None,
                        sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage access information."""
    this_session = get_session()
    this_session.begin()
    if filters.get('hostname', False):
        access_info = this_session.query(AccessInfo.hostname).all()
    else:
        access_info = this_session.query(AccessInfo).all()
    return access_info


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
    this_session = get_session()
    this_session.begin()
    if not sort_keys:
        sort_keys = ['created_at']
    if not sort_dirs:
        sort_dirs = ['desc']
    this_session = get_session()
    this_session.begin()
    query = this_session.query(models.Storage)

    if filters:

        for attr, value in filters.items():
            query = query.filter(getattr(models.Storage, attr).like("%%%s%%" % value))
    try:
        for (sort_key, sort_dir) in zip(sort_keys, sort_dirs):
            query = apply_sorting(models.Storage, query, sort_key, sort_dir)
    except AttributeError:
        msg = "Wrong sorting keys provided - '%s'." % sort_keys
        raise exception.InvalidInput(reason=msg)

    if limit:
        query = query.limit(limit)

    # Returns list of storages  that satisfy filters.
    return query.all()


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
