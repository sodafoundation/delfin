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
from dolphin.db.sqlalchemy.models import Storage, RegistryContext

CONF = cfg.CONF
LOG = log.getLogger(__name__)
_FACADE = None

_DEFAULT_SQL_CONNECTION = 'sqlite:///'
db_options.set_defaults(cfg.CONF,
                        connection=_DEFAULT_SQL_CONNECTION)


def apply_sorting(model, query, sort_key, sort_dir):
    if sort_dir.lower() not in ('desc', 'asc'):
        msg = _("Wrong sorting data provided: sort key is '%(sort_key)s' "
                "and sort direction is '%(sort_dir)s'.") % {
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
    engine = create_engine(_DEFAULT_SQL_CONNECTION, echo=False)
    models = (Storage,
              RegistryContext
              )
    engine = create_engine(CONF.database.connection, echo=False)
    for model in models:
        model.metadata.create_all(engine)


def registry_context_create(values):
    register_ref = models.RegistryContext()
    this_session = get_session()
    this_session.begin()
    register_ref.update(values)
    this_session.add(register_ref)
    this_session.commit()
    return register_ref


def registry_context_get(storage_id):
    this_session = get_session()
    this_session.begin()
    registry_context = this_session.query(RegistryContext) \
        .filter(RegistryContext.storage_id == storage_id) \
        .first()
    return registry_context


def registry_context_get_all(filter=None):
    this_session = get_session()
    this_session.begin()
    if filter == 'hostname':
        registry_context = this_session.query(RegistryContext.hostname).all()
    else:
        registry_context = this_session.query(RegistryContext).all()
    return registry_context


def storage_create(values):
    storage_ref = models.Storage()
    this_session = get_session()
    this_session.begin()
    storage_ref.update(values)
    this_session.add(storage_ref)
    this_session.commit()
    return storage_ref


def storage_get(storage_id):
    this_session = get_session()
    this_session.begin()
    storage_by_id = this_session.query(Storage) \
        .filter(Storage.id == storage_id) \
        .first()
    return storage_by_id


def storage_get_all(context, marker=None, limit=None, sort_key=None,
                    sort_dir=None, filters=None, offset=None):
    this_session = get_session()
    this_session.begin()
    if not sort_key:
        sort_key = 'created_at'
    if not sort_dir:
        sort_dir = 'desc'
    this_session = get_session()
    this_session.begin()
    query = this_session.query(models.Storage)
    if limit:
        offset = filters.get('offset', 0)
        query = query.limit(limit).offset(offset)

    if filters:

        for attr, value in filters.items():
            query = query.filter(getattr(models.Storage, attr).like("%%%s%%" % value))
    try:
        query = apply_sorting(models.Storage, query, sort_key, sort_dir)
    except AttributeError:
        msg = "Wrong sorting key provided - '%s'." % sort_key
        raise exception.InvalidInput(reason=msg)

    # Returns list of storages  that satisfy filters.
    storages_all = query.all()
    if storages_all:
        return storages_all
    else:
        raise exception.NotFound()
