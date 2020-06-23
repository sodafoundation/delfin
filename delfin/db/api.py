# Copyright 2020 The SODA Authors.
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

Functions in this module are imported into the delfin.db namespace. Call these
functions from delfin.db namespace, not the delfin.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface. Currently, many of these objects are sqlalchemy objects that
implement a dictionary interface. However, a future goal is to have all of
these objects be simple dictionaries.


**Related Flags**

:backend:  string to lookup in the list of LazyPluggable backends.
           `sqlalchemy` is the only supported backend right now.

:connection:  string specifying the sqlalchemy connection to use, like:
              `sqlite:///var/lib/delfin/delfin.sqlite`.

:enable_new_services:  when adding a new service to the database, is it in the
                       storage_pool of available hardware (Default: True)

"""
from oslo_config import cfg
from oslo_db import api as db_api

db_opts = [
    cfg.StrOpt('db_backend',
               default='sqlalchemy',
               help='The backend to use for database.'),
]

CONF = cfg.CONF
CONF.register_opts(db_opts, "database")

_BACKEND_MAPPING = {'sqlalchemy': 'delfin.db.sqlalchemy.api'}
IMPL = db_api.DBAPI(CONF.database.db_backend, backend_mapping=_BACKEND_MAPPING,
                    lazy=True)


def register_db():
    """Create database and tables."""
    IMPL.register_db()


def storage_get(context, storage_id):
    """Retrieve a storage device."""
    return IMPL.storage_get(context, storage_id)


def storage_get_all(context, marker=None, limit=None, sort_keys=None,
                    sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage devices.

    If no sort parameters are specified then the returned volumes are sorted
    first by the 'created_at' key and then by the 'id' key in descending
    order.

    :param context: context of this request, it's helpful to trace the request
    :param marker: the last item of the previous page, used to determine the
                   next page of results to return
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys, for example
                      'desc' for descending order
    :param filters: dictionary of filters
    :param offset: number of items to skip
    :returns: list of storage
    """
    return IMPL.storage_get_all(context, marker, limit, sort_keys, sort_dirs,
                                filters, offset)


def storage_create(context, values):
    """Add a storage device from the values dictionary."""
    return IMPL.storage_create(context, values)


def storage_update(context, storage_id, values):
    """Update a storage device with the values dictionary."""
    return IMPL.storage_update(context, storage_id, values)


def storage_delete(context, storage_id):
    """Delete a storage device."""
    return IMPL.storage_delete(context, storage_id)


def volume_create(context, values):
    """Create a volume from the values dictionary."""
    return IMPL.volume_create(context, values)


def volumes_create(context, values):
    """Create multiple volumes."""
    return IMPL.volumes_create(context, values)


def volume_update(context, volume_id, values):
    """Update a volume with the values dictionary."""
    return IMPL.volume_update(context, volume_id, values)


def volumes_update(context, values):
    """Update multiple volumes."""
    return IMPL.volumes_update(context, values)


def volumes_delete(context, values):
    """Delete multiple volumes."""
    return IMPL.volumes_delete(context, values)


def volume_get(context, volume_id):
    """Get a volume or raise an exception if it does not exist."""
    return IMPL.volume_get(context, volume_id)


def volume_get_all(context, marker=None, limit=None, sort_keys=None,
                   sort_dirs=None, filters=None, offset=None):
    """Retrieves all volumes.

    If no sort parameters are specified then the returned volumes are sorted
    first by the 'created_at' key and then by the 'id' key in descending
    order.

    :param context: context of this request, it's helpful to trace the request
    :param marker: the last item of the previous page, used to determine the
                   next page of results to return
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys, for example
                      'desc' for descending order
    :param filters: dictionary of filters
    :param offset: number of items to skip
    :returns: list of volumes
    """
    return IMPL.volume_get_all(context, marker, limit, sort_keys,
                               sort_dirs, filters, offset)


def volume_delete_by_storage(context, storage_id):
    """Delete all the volumes of a device."""
    return IMPL.volume_delete_by_storage(context, storage_id)


def storage_pool_create(context, storage_pool):
    """Add a storage_storage_pool."""
    return IMPL.storage_pool_create(context, storage_pool)


def storage_pools_create(context, storage_pools):
    """Add multiple storage_pools."""
    return IMPL.storage_pools_create(context, storage_pools)


def storage_pool_update(context, storage_pool_id, storage_pool):
    """Update a storage_pool."""
    return IMPL.storage_pool_update(context, storage_pool_id, storage_pool)


def storage_pools_update(context, storage_pools):
    """Update multiple storage_pools"""
    return IMPL.storage_pools_update(context, storage_pools)


def storage_pools_delete(context, storage_pools):
    """Delete storage_pools."""
    return IMPL.storage_pools_delete(context, storage_pools)


def storage_pool_get(context, storage_pool_id):
    """Get a storage_pool or raise an exception if it does not exist."""
    return IMPL.storage_pool_get(context, storage_pool_id)


def storage_pool_get_all(context, marker=None, limit=None, sort_keys=None,
                         sort_dirs=None, filters=None, offset=None):
    """Retrieves all  storage_pools.

    If no sort parameters are specified then the returned volumes are sorted
    first by the 'created_at' key and then by the 'id' key in descending
    order.

    :param context: context of this request, it's helpful to trace the request
    :param marker: the last item of the previous page, used to determine the
                   next page of results to return
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys, for example
                      'desc' for descending order
    :param filters: dictionary of filters
    :param offset: number of items to skip
    :returns: list of  storage_pools
    """
    return IMPL.storage_pool_get_all(context, marker, limit,
                                     sort_keys, sort_dirs, filters, offset)


def storage_pool_delete_by_storage(context, storage_id):
    """Delete all the storage_pool of a device."""
    return IMPL.storage_pool_delete_by_storage(context, storage_id)


def disk_create(context, values):
    """Create a disk from the values dictionary."""
    return IMPL.disk_create(context, values)


def disk_update(context, disk_id, values):
    """Update a disk withe the values dictionary."""
    return IMPL.disk_create(context, disk_id, values)


def disk_get(context, disk_id):
    """Get a disk or raise an exception if it does not exist."""
    return IMPL.disk_get(context, disk_id)


def disk_get_all(context, marker=None, limit=None, sort_keys=None,
                 sort_dirs=None, filters=None, offset=None):
    """Retrieves all disks.

    If no sort parameters are specified then the returned volumes are sorted
    first by the 'created_at' key and then by the 'id' key in descending
    order.

    :param context: context of this request, it's helpful to trace the request
    :param marker: the last item of the previous page, used to determine the
                   next page of results to return
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys, for example
                      'desc' for descending order
    :param filters: dictionary of filters
    :param offset: number of items to skip
    :returns: list of disks
    """
    return IMPL.disk_get_all(context, marker, limit, sort_keys, sort_dirs,
                             filters, offset)


def access_info_create(context, values):
    """Create a storage access information that used to connect
    to a specific storage device.
    """
    return IMPL.access_info_create(context, values)


def access_info_update(context, storage_id, values):
    """Update a storage access information with the values dictionary."""
    return IMPL.access_info_update(context, storage_id, values)


def access_info_get(context, storage_id):
    """Get a storage access information."""
    return IMPL.access_info_get(context, storage_id)


def access_info_delete(context, storage_id):
    """Delete a storage access information."""
    return IMPL.access_info_delete(context, storage_id)


def access_info_get_all(context, marker=None, limit=None, sort_keys=None,
                        sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage access information.

    If no sort parameters are specified then the returned volumes are sorted
    first by the 'created_at' key and then by the 'id' key in descending
    order.

    :param context: context of this request, it's helpful to trace the request
    :param marker: the last item of the previous page, used to determine the
                   next page of results to return
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys, for example
                      'desc' for descending order
    :param filters: dictionary of filters
    :param offset: number of items to skip
    :returns: list of storage accesses
    """
    return IMPL.access_info_get_all(context, marker, limit,
                                    sort_keys, sort_dirs, filters, offset)


def is_orm_value(obj):
    """Check if object is an ORM field."""
    return IMPL.is_orm_value(obj)


def alert_source_create(context, values):
    """Create an alert source."""
    return IMPL.alert_source_create(context, values)


def alert_source_update(context, storage_id, values):
    """Update an alert source."""
    return IMPL.alert_source_update(context, storage_id, values)


def alert_source_get(context, storage_id):
    """Get an alert source."""
    return IMPL.alert_source_get(context, storage_id)


def alert_source_delete(context, storage_id):
    """Delete an alert source."""
    return IMPL.alert_source_delete(context, storage_id)


def alert_source_get_all(context, marker=None, limit=None, sort_keys=None,
                         sort_dirs=None, filters=None, offset=None):
    """Retrieves all alert sources.

    If no sort parameters are specified then the returned alert sources are
    sorted first by the 'created_at' key in descending order.

    :param context: context of this request, it's helpful to trace the request
    :param marker: the last item of the previous page, used to determine the
                   next page of results to return
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys, for example
                      'desc' for descending order
    :param filters: dictionary of filters
    :param offset: number of items to skip
    :returns: list of storage accesses
    """
    return IMPL.alert_source_get_all(context, marker, limit, sort_keys,
                                     sort_dirs, filters, offset)
