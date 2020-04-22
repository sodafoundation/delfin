# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Defines interface for DB access.

The underlying driver is loaded as a :class:`LazyPluggable`.

Functions in this module are imported into the dolphin.db namespace. Call these
functions from dolphin.db namespace, not the dolphin.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface. Currently, many of these objects are sqlalchemy objects that
implement a dictionary interface. However, a future goal is to have all of
these objects be simple dictionaries.


**Related Flags**

:backend:  string to lookup in the list of LazyPluggable backends.
           `sqlalchemy` is the only supported backend right now.

:connection:  string specifying the sqlalchemy connection to use, like:
              `sqlite:///var/lib/dolphin/dolphin.sqlite`.

:enable_new_services:  when adding a new service to the database, is it in the
                       pool of available hardware (Default: True)

"""
from oslo_config import cfg
from oslo_db import api as db_api

db_opts = [
    cfg.StrOpt('db_backend',
               default='sqlalchemy',
               help='The backend to use for database.'),

]

CONF = cfg.CONF
CONF.register_opts(db_opts)

_BACKEND_MAPPING = {'sqlalchemy': 'dolphin.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def register_db():
    IMPL.register_db()


def storage_get(storage_id):
    return IMPL.storage_get(storage_id)


def storage_get_all():
    return IMPL.storage_get_all()


def storage_create(values):
    return IMPL.storage_create(values)


def volume_create(values):
    return IMPL.volume_create(values)


def volume_get(volume_id):
    return IMPL.volume_get(volume_id)


def volume_get_all(storage_id):
    return IMPL.volume_get_all(storage_id)


def pool_create(values):
    return IMPL.pool_create(values)


def pool_get(pool_id):
    return IMPL.pool_get(pool_id)


def pool_get_all(storage_id):
    return IMPL.pool_get_all(storage_id)


def registry_context_create(values):
    return IMPL.registry_context_create(values)


def registry_context_update(values):
    return IMPL.registry_context_update(register_info)


def registry_context_get(storage_id):
    return IMPL.registry_context_get(storage_id)


def registry_context_get_all():
    return IMPL.registry_context_get_all()
