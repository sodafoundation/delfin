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
from sqlalchemy import MetaData, create_engine
from dolphin.db.sqlalchemy import models
from dolphin.db.sqlalchemy.models import Storage, ConnectionParams

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
    engine = create_engine(_DEFAULT_SQL_CONNECTION, echo=False)
    models = (Storage,
              ConnectionParams
              )
    engine = create_engine(CONF.database.connection, echo=False)
    for model in models:
        model.metadata.create_all(engine)


def storage_get(storage_id):
    this_session = get_session()
    this_session.begin()
    storage_by_id = this_session.query(Storage) \
        .filter(Storage.id == storage_id) \
        .first()


def register_info_create(register_info):
    register_ref = models.ConnectionParams()
    register_ref.storage_id = register_info.storage_id
    register_ref.hostname = register_info.hostname
    register_ref.password = register_info.password
    return register_ref


def storage_create(storage, register_info):
    storage_ref = models.Storage()
    storage_ref.id = storage.id
    storage_ref.name = storage.name
    storage_ref.model = storage.model
    storage_ref.vendor = storage.vendor
    storage_ref.description = storage.description
    storage_ref.location = storage.location
    storage_ref.connection_param = register_info_create(register_info)
    this_session = get_session()
    this_session.begin()
    this_session.add(storage_ref)
    this_session.commit()
    return storage_ref
