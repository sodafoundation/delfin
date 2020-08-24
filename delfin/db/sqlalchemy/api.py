# Copyright 2020 The SODA Authors.
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

import sys

import six
import sqlalchemy
from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_log import log
from oslo_utils import uuidutils, timeutils
from sqlalchemy import create_engine

from delfin import exception
from delfin.common import sqlalchemyutils
from delfin.db.sqlalchemy import models
from delfin.db.sqlalchemy.models import Storage, AccessInfo
from delfin.i18n import _

CONF = cfg.CONF
LOG = log.getLogger(__name__)
_FACADE = None

_DEFAULT_SQL_CONNECTION = 'sqlite:///'
db_options.set_defaults(cfg.CONF,
                        connection=_DEFAULT_SQL_CONNECTION)


def apply_sorting(model, query, sort_key, sort_dir):
    if sort_dir.lower() not in ('desc', 'asc'):
        msg = (("Wrong sorting data provided: sort key is '%(sort_key)s' "
                "and sort order is '%(sort_dir)s'.") %
               {"sort_key": sort_key, "sort_dir": sort_dir})
        raise exception.InvalidInput(msg)

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


def _process_model_like_filter(model, query, filters):
    """Applies regex expression filtering to a query.

    :param model: model to apply filters to
    :param query: query to apply filters to
    :param filters: dictionary of filters with regex values
    :returns: the updated query.
    """
    if query is None:
        return query

    for key in sorted(filters):
        column_attr = getattr(model, key)
        if 'property' == type(column_attr).__name__:
            continue
        value = filters[key]
        if not (isinstance(value, (six.string_types, int))):
            continue
        query = query.filter(
            column_attr.op('LIKE')(u'%%%s%%' % value))
    return query


def apply_like_filters(model):
    def decorator_filters(process_exact_filters):
        def _decorator(query, filters):
            exact_filters = filters.copy()
            regex_filters = {}
            for key, value in filters.items():
                # NOTE(tommylikehu): For inexact match, the filter keys
                # are in the format of 'key~=value'
                if key.endswith('~'):
                    exact_filters.pop(key)
                    regex_filters[key.rstrip('~')] = value
            query = process_exact_filters(query, exact_filters)
            return _process_model_like_filter(model, query, regex_filters)

        return _decorator

    return decorator_filters


def is_valid_model_filters(model, filters, exclude_list=None):
    """Return True if filter values exist on the model

    :param model: a Delfin model
    :param filters: dictionary of filters
    """
    for key in filters.keys():
        if exclude_list and key in exclude_list:
            continue
        if key == 'metadata':
            if not isinstance(filters[key], dict):
                LOG.debug("Metadata filter value is not valid dictionary")
                return False
            continue
        try:
            key = key.rstrip('~')
            getattr(model, key)
        except AttributeError:
            LOG.debug("'%s' filter key is not valid.", key)
            return False
    return True


def access_info_create(context, values):
    """Create a storage access information."""
    if not values.get('storage_id'):
        values['storage_id'] = uuidutils.generate_uuid()

    access_info_ref = models.AccessInfo()
    access_info_ref.update(values)

    session = get_session()
    with session.begin():
        session.add(access_info_ref)

    return _access_info_get(context,
                            access_info_ref['storage_id'],
                            session=session)


def access_info_update(context, storage_id, values):
    """Update a storage access information with the values dictionary."""
    session = get_session()
    with session.begin():
        _access_info_get(context, storage_id, session).update(values)
        return _access_info_get(context, storage_id, session)


def access_info_delete(context, storage_id):
    """Delete a storage access information."""
    _access_info_get_query(context). \
        filter_by(storage_id=storage_id).delete()


def access_info_get(context, storage_id):
    """Get a storage access information."""
    return _access_info_get(context, storage_id)


def _access_info_get(context, storage_id, session=None):
    result = (_access_info_get_query(context, session=session)
              .filter_by(storage_id=storage_id)
              .first())

    if not result:
        raise exception.AccessInfoNotFound(storage_id)

    return result


def _access_info_get_query(context, session=None):
    return model_query(context, models.AccessInfo, session=session)


def access_info_get_all(context, marker=None, limit=None, sort_keys=None,
                        sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage access information."""
    session = get_session()
    with session.begin():
        query = _generate_paginate_query(context, session, models.AccessInfo,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset,
                                         )
        if query is None:
            return []
        return query.all()


@apply_like_filters(model=models.AccessInfo)
def _process_access_info_filters(query, filters):
    """Common filter processing for AccessInfo queries."""
    if filters:
        if not is_valid_model_filters(models.AccessInfo, filters):
            return
        query = query.filter_by(**filters)

    return query


def storage_create(context, values):
    """Add a storage device from the values dictionary."""
    if not values.get('id'):
        values['id'] = uuidutils.generate_uuid()

    storage_ref = models.Storage()
    storage_ref.update(values)

    session = get_session()
    with session.begin():
        session.add(storage_ref)

    return _storage_get(context,
                        storage_ref['id'],
                        session=session)


def storage_update(context, storage_id, values):
    """Update a storage device with the values dictionary."""
    session = get_session()
    with session.begin():
        query = _storage_get_query(context, session)
        result = query.filter_by(id=storage_id).update(values)
    return result


def storage_get(context, storage_id):
    """Retrieve a storage device."""
    return _storage_get(context, storage_id)


def _storage_get(context, storage_id, session=None):
    result = (_storage_get_query(context, session=session)
              .filter_by(id=storage_id)
              .first())

    if not result:
        raise exception.StorageNotFound(storage_id)

    return result


def _storage_get_query(context, session=None):
    read_deleted = context.read_deleted
    kwargs = dict()

    if read_deleted in ('no', 'n', False):
        kwargs['deleted'] = False
    elif read_deleted in ('yes', 'y', True):
        kwargs['deleted'] = True

    return model_query(context, models.Storage, session=session, **kwargs)


def storage_get_all(context, marker=None, limit=None, sort_keys=None,
                    sort_dirs=None, filters=None, offset=None):
    session = get_session()
    with session.begin():
        # Generate the query
        query = _generate_paginate_query(context, session, models.Storage,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset,
                                         )
        # No storages   match, return empty list
        if query is None:
            return []
        return query.all()


@apply_like_filters(model=models.Storage)
def _process_storage_info_filters(query, filters):
    """Common filter processing for Storages queries."""
    if filters:
        if not is_valid_model_filters(models.Storage, filters):
            return
        query = query.filter_by(**filters)
    return query


def storage_delete(context, storage_id):
    """Delete a storage device."""
    delete_info = {'deleted': True, 'deleted_at': timeutils.utcnow()}
    _storage_get_query(context).filter_by(id=storage_id).update(delete_info)


def _volume_get_query(context, session=None):
    return model_query(context, models.Volume, session=session)


def _volume_get(context, volume_id, session=None):
    result = (_volume_get_query(context, session=session)
              .filter_by(id=volume_id)
              .first())

    if not result:
        raise exception.VolumeNotFound(volume_id)

    return result


def volume_create(context, values):
    """Create a volume."""
    if not values.get('id'):
        values['id'] = uuidutils.generate_uuid()

    vol_ref = models.Volume()
    vol_ref.update(values)

    session = get_session()
    with session.begin():
        session.add(vol_ref)

    return _volume_get(context,
                       vol_ref['id'],
                       session=session)


def volumes_create(context, volumes):
    """Create multiple volumes."""
    session = get_session()
    vol_refs = []
    with session.begin():

        for vol in volumes:
            LOG.debug('adding new volume for native_volume_id {0}:'
                      .format(vol.get('native_volume_id')))
            if not vol.get('id'):
                vol['id'] = uuidutils.generate_uuid()

            vol_ref = models.Volume()
            vol_ref.update(vol)
            vol_refs.append(vol_ref)

        session.add_all(vol_refs)

    return vol_refs


def volumes_delete(context, volumes_id_list):
    """Delete multiple volumes."""
    session = get_session()
    with session.begin():
        for vol_id in volumes_id_list:
            LOG.debug('deleting volume {0}:'.format(vol_id))
            query = _volume_get_query(context, session)
            result = query.filter_by(id=vol_id).delete()

            if not result:
                LOG.error(exception.VolumeNotFound(vol_id))
    return


def volume_update(context, vol_id, values):
    """Update a volume."""
    session = get_session()
    with session.begin():
        _volume_get(context, vol_id, session).update(values)
    return _volume_get(context, vol_id, session)


def volumes_update(context, volumes):
    """Update multiple volumes."""
    session = get_session()
    with session.begin():
        for vol in volumes:
            LOG.debug('updating volume {0}:'.format(vol.get('id')))
            query = _volume_get_query(context, session)
            result = query.filter_by(id=vol.get('id')
                                     ).update(vol)

            if not result:
                LOG.error(exception.VolumeNotFound(vol.get('id')))


def volume_get(context, volume_id):
    """Get a volume or raise an exception if it does not exist."""
    return _volume_get(context, volume_id)


def volume_get_all(context, marker=None, limit=None, sort_keys=None,
                   sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage volumes."""
    session = get_session()
    with session.begin():
        # Generate the query
        query = _generate_paginate_query(context, session, models.Volume,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset)
        # No volume would match, return empty list
        if query is None:
            return []
        return query.all()


@apply_like_filters(model=models.Volume)
def _process_volume_info_filters(query, filters):
    """Common filter processing for volumes queries."""
    if filters:
        if not is_valid_model_filters(models.Volume, filters):
            return
        query = query.filter_by(**filters)

    return query


def volume_delete_by_storage(context, storage_id):
    """Delete all the volumes of a device"""
    _volume_get_query(context).filter_by(storage_id=storage_id).delete()


def _storage_pool_get_query(context, session=None):
    return model_query(context, models.StoragePool, session=session)


def _storage_pool_get(context, storage_pool_id, session=None):
    result = (_storage_pool_get_query(context, session=session)
              .filter_by(id=storage_pool_id)
              .first())

    if not result:
        raise exception.StoragePoolNotFound(storage_pool_id)

    return result


def storage_pool_create(context, values):
    """Create a storage_pool from the values dictionary."""
    if not values.get('id'):
        values['id'] = uuidutils.generate_uuid()

    storage_pool_ref = models.StoragePool()
    storage_pool_ref.update(values)

    session = get_session()
    with session.begin():
        session.add(storage_pool_ref)

    return _storage_pool_get(context,
                             storage_pool_ref['id'],
                             session=session)


def storage_pools_create(context, storage_pools):
    """Create a storage_pool from the values dictionary."""
    session = get_session()
    storage_pool_refs = []
    with session.begin():

        for storage_pool in storage_pools:
            LOG.debug('adding new storage_pool for native_storage_pool_id {0}:'
                      .format(storage_pool.get('native_storage_pool_id')))
            if not storage_pool.get('id'):
                storage_pool['id'] = uuidutils.generate_uuid()

            storage_pool_ref = models.StoragePool()
            storage_pool_ref.update(storage_pool)
            storage_pool_refs.append(storage_pool_ref)

        session.add_all(storage_pool_refs)

    return storage_pool_refs


def storage_pools_delete(context, storage_pools_id_list):
    """Delete multiple storage_pools with the storage_pools dictionary."""
    session = get_session()
    with session.begin():
        for storage_pool_id in storage_pools_id_list:
            LOG.debug('deleting storage_pool {0}:'.format(storage_pool_id))
            query = _storage_pool_get_query(context, session)
            result = query.filter_by(id=storage_pool_id).delete()

            if not result:
                LOG.error(exception.StoragePoolNotFound(storage_pool_id))

    return


def storage_pool_update(context, storage_pool_id, values):
    """Update a storage_pool withe the values dictionary."""
    session = get_session()

    with session.begin():
        query = _storage_pool_get_query(context, session)
        result = query.filter_by(id=storage_pool_id).update(values)

        if not result:
            raise exception.StoragePoolNotFound(storage_pool_id)

    return result


def storage_pools_update(context, storage_pools):
    """Update multiple storage_pools withe the storage_pools dictionary."""
    session = get_session()

    with session.begin():
        storage_pool_refs = []

        for storage_pool in storage_pools:
            LOG.debug('updating storage_pool {0}:'.format(
                storage_pool.get('id')))
            query = _storage_pool_get_query(context, session)
            result = query.filter_by(id=storage_pool.get('id')
                                     ).update(storage_pool)

            if not result:
                LOG.error(exception.StoragePoolNotFound(storage_pool.get(
                    'id')))
            else:
                storage_pool_refs.append(result)

    return storage_pool_refs


def storage_pool_get(context, storage_pool_id):
    """Get a storage_pool or raise an exception if it does not exist."""
    return _storage_pool_get(context, storage_pool_id)


def storage_pool_get_all(context, marker=None, limit=None, sort_keys=None,
                         sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage storage_pools."""
    session = get_session()
    with session.begin():
        # Generate the query
        query = _generate_paginate_query(context, session, models.StoragePool,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset,
                                         )
        # No storage_pool would match, return empty list
        if query is None:
            return []
        return query.all()


def storage_pool_delete_by_storage(context, storage_id):
    """Delete all the storage_pools of a storage device"""
    _storage_pool_get_query(context).filter_by(storage_id=storage_id).delete()


@apply_like_filters(model=models.StoragePool)
def _process_storage_pool_info_filters(query, filters):
    """Common filter processing for storage_pools queries."""
    if filters:
        if not is_valid_model_filters(models.StoragePool, filters):
            return
        query = query.filter_by(**filters)

    return query


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


def is_orm_value(obj):
    """Check if object is an ORM field or expression."""
    return isinstance(obj, (sqlalchemy.orm.attributes.InstrumentedAttribute,
                            sqlalchemy.sql.expression.ColumnElement))


def model_query(context, model, *args, **kwargs):
    """Query helper for model query.

    :param context: context to query under
    :param model: model to query. Must be a subclass of ModelBase.
    :param session: if present, the session to use
    """
    session = kwargs.pop('session') or get_session()
    return db_utils.model_query(
        model=model, session=session, args=args, **kwargs)


def alert_source_get(context, storage_id):
    """Get an alert source or raise an exception if it does not exist."""
    return _alert_source_get(context, storage_id)


def _alert_source_get(context, storage_id, session=None):
    result = (_alert_source_get_query(context, session=session)
              .filter_by(storage_id=storage_id)
              .first())

    if not result:
        raise exception.AlertSourceNotFound(storage_id)

    return result


def _alert_source_get_query(context, session=None):
    return model_query(context, models.AlertSource, session=session)


@apply_like_filters(model=models.AlertSource)
def _process_alert_source_filters(query, filters):
    """Common filter processing for alert source queries."""
    if filters:
        if not is_valid_model_filters(models.AlertSource, filters):
            return
        query = query.filter_by(**filters)

    return query


def alert_source_create(context, values):
    """Add an alert source configuration."""
    alert_source_ref = models.AlertSource()
    alert_source_ref.update(values)

    session = get_session()
    with session.begin():
        session.add(alert_source_ref)

    return _alert_source_get(context,
                             alert_source_ref['storage_id'],
                             session=session)


def alert_source_update(context, storage_id, values):
    """Update an alert source configuration."""
    session = get_session()
    with session.begin():
        _alert_source_get(context, storage_id, session).update(values)
        return _alert_source_get(context, storage_id, session)


def alert_source_delete(context, storage_id):
    session = get_session()
    with session.begin():
        query = _alert_source_get_query(context, session)
        result = query.filter_by(storage_id=storage_id).delete()
        if not result:
            LOG.error("Cannot delete non-exist alert source[storage_id=%s]." %
                      storage_id)
            raise exception.AlertSourceNotFound(storage_id)
        else:
            LOG.info("Delete alert source[storage_id=%s] successfully." %
                     storage_id)


def alert_source_get_all(context, marker=None, limit=None, sort_keys=None,
                         sort_dirs=None, filters=None, offset=None):
    session = get_session()
    with session.begin():
        query = _generate_paginate_query(context, session, models.AlertSource,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset)
        if query is None:
            return []
        return query.all()


PAGINATION_HELPERS = {
    models.AccessInfo: (_access_info_get_query, _process_access_info_filters,
                        _access_info_get),
    models.StoragePool: (_storage_pool_get_query,
                         _process_storage_pool_info_filters,
                         _storage_pool_get),
    models.Storage: (_storage_get_query, _process_storage_info_filters,
                     _storage_get),
    models.AlertSource: (_alert_source_get_query,
                         _process_alert_source_filters,
                         _alert_source_get),
    models.Volume: (_volume_get_query, _process_volume_info_filters,
                    _volume_get),
}


def process_sort_params(sort_keys, sort_dirs, default_keys=None,
                        default_dir='asc'):
    """Process the sort parameters to include default keys.

    Creates a list of sort keys and a list of sort directions. Adds the default
    keys to the end of the list if they are not already included.

    When adding the default keys to the sort keys list, the associated
    direction is:
    1) The first element in the 'sort_dirs' list (if specified), else
    2) 'default_dir' value (Note that 'asc' is the default value since this is
    the default in sqlalchemy.utils.paginate_query)

    :param sort_keys: List of sort keys to include in the processed list
    :param sort_dirs: List of sort directions to include in the processed list
    :param default_keys: List of sort keys that need to be included in the
                         processed list, they are added at the end of the list
                         if not already specified.
    :param default_dir: Sort direction associated with each of the default
                        keys that are not supplied, used when they are added
                        to the processed list
    :returns: list of sort keys, list of sort directions
    :raise exception.InvalidInput: If more sort directions than sort keys
                                   are specified or if an invalid sort
                                   direction is specified
    """
    if default_keys is None:
        default_keys = ['created_at']

    # Determine direction to use for when adding default keys
    if sort_dirs and len(sort_dirs):
        default_dir_value = sort_dirs[0]
    else:
        default_dir_value = default_dir

    # Create list of keys (do not modify the input list)
    if sort_keys:
        result_keys = list(sort_keys)
    else:
        result_keys = []

    # If a list of directions is not provided, use the default sort direction
    # for all provided keys.
    if sort_dirs:
        result_dirs = []
        # Verify sort direction
        for sort_dir in sort_dirs:
            if sort_dir not in ('asc', 'desc'):
                msg = _("Unknown sort direction, must be 'desc' or 'asc'.")
                raise exception.InvalidInput(msg)
            result_dirs.append(sort_dir)
    else:
        result_dirs = [default_dir_value for _sort_key in result_keys]

    # Ensure that the key and direction length match
    while len(result_dirs) < len(result_keys):
        result_dirs.append(default_dir_value)
    # Unless more direction are specified, which is an error
    if len(result_dirs) > len(result_keys):
        msg = _("Sort direction array size exceeds sort key array size.")
        raise exception.InvalidInput(msg)

    # Ensure defaults are included
    for key in default_keys:
        if key not in result_keys:
            result_keys.append(key)
            result_dirs.append(default_dir_value)

    return result_keys, result_dirs


def _generate_paginate_query(context, session, paginate_type, marker,
                             limit, sort_keys, sort_dirs, filters,
                             offset=None
                             ):
    """Generate the query to include the filters and the paginate options.

    Returns a query with sorting / pagination criteria added or None
    if the given filters will not yield any results.

    :param context: context to query under
    :param session: the session to use
    :param marker: the last item of the previous page; we returns the next
                    results after this value.
    :param limit: maximum number of items to return
    :param sort_keys: list of attributes by which results should be sorted,
                      paired with corresponding item in sort_dirs
    :param sort_dirs: list of directions in which results should be sorted,
                      paired with corresponding item in sort_keys
    :param filters: dictionary of filters; values that are in lists, tuples,
                    or sets cause an 'IN' operation, while exact matching
                    is used for other values, see _process_volume_filters
                    function for more information
    :param offset: number of items to skip
    :param paginate_type: type of pagination to generate
    :returns: updated query or None
    """
    get_query, process_filters, get = PAGINATION_HELPERS[paginate_type]

    sort_keys, sort_dirs = process_sort_params(sort_keys,
                                               sort_dirs,
                                               default_dir='desc')
    query = get_query(context, session=session)

    if filters:
        query = process_filters(query, filters)
        if query is None:
            return None

    marker_object = None
    if marker is not None:
        marker_object = get(context, marker, session)

    return sqlalchemyutils.paginate_query(query, paginate_type, limit,
                                          sort_keys,
                                          marker=marker_object,
                                          sort_dirs=sort_dirs,
                                          offset=offset)
