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
import six
import sys
import sqlalchemy
from sqlalchemy import create_engine
from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import utils as db_utils
from oslo_db.sqlalchemy import session
from oslo_log import log
from oslo_utils import uuidutils
from dolphin.common import sqlalchemyutils
from dolphin.db.sqlalchemy import models
from dolphin.db.sqlalchemy.models import Storage, AccessInfo
from dolphin import exception
from dolphin.i18n import _

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
    :param model: a Dolphin model
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


def access_info_update(context, access_info_id, values):
    """Update a storage access information with the values dictionary."""
    return NotImplemented


def access_info_get(context, storage_id):
    """Get a storage access information."""
    return _access_info_get(context, storage_id)


def _access_info_get(context, storage_id, session=None):
    result = (_access_info_get_query(context, session=session)
              .filter_by(storage_id=storage_id)
              .first())
    if not result:
        raise exception.AccessInfoNotFound(storage_id=storage_id)
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
        if not result:
            raise exception.StorageNotFound(id=storage_id)
    return result


def storage_get(context, storage_id):
    """Retrieve a storage device."""
    return _storage_get(context, storage_id)


def _storage_get(context, storage_id, session=None):
    result = (_storage_get_query(context, session=session)
              .filter_by(id=storage_id)
              .first())
    if not result:
        raise exception.StorageNotFound(id=storage_id)
    return result


def _storage_get_query(context, session=None):
    return model_query(context, models.Storage, session=session)


def storage_get_all(context, marker=None, limit=None, sort_keys=None,
                    sort_dirs=None, filters=None, offset=None):
    session = get_session()
    with session.begin():
        # Generate the query
        print(filters)
        query = _generate_paginate_query(context, session, models.Storage,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset,
                                         )
        # No pool would match, return empty list
        # if query is None:
        #     return []
        return query.all()


@apply_like_filters(model=models.Storage)
def _process_storage_info_filters(query, filters):
    """Common filter processing for Storages queries."""
    if filters:
        if not is_valid_model_filters(models.Storage, filters):
            return
        query = query.filter_by(**filters)
    return query


def volume_get(context, volume_id):
    """Get a volume or raise an exception if it does not exist."""
    return NotImplemented


def volume_get_all(context, marker=None, limit=None, sort_keys=None,
                   sort_dirs=None, filters=None, offset=None):
    """Retrieves all volumes."""
    return NotImplemented


def _pool_get_query(context, session=None):
    return model_query(context, models.Pool, session=session)


def _pool_get(context, pool_id, session=None):
    result = (_pool_get_query(context, session=session)
              .filter_by(id=pool_id)
              .first())
    if not result:
        LOG.error(exception.PoolNotFound(id=pool_id))
    return result


def pool_create(context, values):
    """Create a pool from the values dictionary."""
    if not values.get('id'):
        values['id'] = uuidutils.generate_uuid()
    pool_ref = models.Pool()
    pool_ref.update(values)
    session = get_session()
    with session.begin():
        session.add(pool_ref)
    return _pool_get(context,
                     pool_ref['id'],
                     session=session)


def pools_create(context, pools):
    """Create a pool from the values dictionary."""
    session = get_session()
    pool_refs = []
    with session.begin():
        for pool in pools:
            LOG.debug('adding new pool for original_id {0}:'
                      .format(pool.get('original_id')))
            if not pool.get('id'):
                pool['id'] = uuidutils.generate_uuid()
            pool_ref = models.Pool()
            pool_ref.update(pool)
            pool_refs.append(pool_ref)
        session.add_all(pool_refs)
    return pool_refs


def pools_delete(context, pools_id_list):
    """Delete multiple pools with the pools dictionary."""
    session = get_session()
    with session.begin():
        for id in pools_id_list:
            LOG.debug('deleting pool {0}:'.format(id))
            query = _pool_get_query(context, session)
            result = query.filter_by(id=id).delete()
            if not result:
                LOG.error(exception.PoolNotFound(id=id))
    return


def pool_update(context, pool_id, values):
    """Update a pool withe the values dictionary."""
    session = get_session()
    with session.begin():
        query = _pool_get_query(context, session)
        result = query.filter_by(id=pool_id).update(values)
        if not result:
            raise exception.PoolNotFound(id=pool_id)
    return result


def pools_update(context, pools):
    """Update multiple pools withe the pools dictionary."""
    session = get_session()
    with session.begin():
        pool_refs = []
        for pool in pools:
            LOG.debug('updating pool {0}:'.format(pool.get('id')))
            query = _pool_get_query(context, session)
            result = query.filter_by(id=pool.get('id')
                                     ).update(pool)
            if not result:
                LOG.error(exception.PoolNotFound(id=pool.get(
                    'id')))
            else:
                pool_refs.append(result)
    return pool_refs


def pool_get(context, pool_id):
    """Get a pool or raise an exception if it does not exist."""
    return _pool_get(context, pool_id)


def pool_get_all(context, marker=None, limit=None, sort_keys=None,
                 sort_dirs=None, filters=None, offset=None):
    """Retrieves all storage pools."""
    session = get_session()
    with session.begin():
        # Generate the query
        query = _generate_paginate_query(context, session, models.Pool,
                                         marker, limit, sort_keys, sort_dirs,
                                         filters, offset,
                                         )
        # No pool would match, return empty list
        if query is None:
            return []
        return query.all()


@apply_like_filters(model=models.Pool)
def _process_pool_info_filters(query, filters):
    """Common filter processing for Pools queries."""
    if filters:
        if not is_valid_model_filters(models.Pool, filters):
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


PAGINATION_HELPERS = {
    models.AccessInfo: (_access_info_get_query, _process_access_info_filters,
                        _access_info_get),
    models.Pool: (_pool_get_query, _process_pool_info_filters, _pool_get),
    models.Storage: (_storage_get_query, _process_storage_info_filters, _storage_get),
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
                raise exception.InvalidInput(reason=msg)
            result_dirs.append(sort_dir)
    else:
        result_dirs = [default_dir_value for _sort_key in result_keys]
    # Ensure that the key and direction length match
    while len(result_dirs) < len(result_keys):
        result_dirs.append(default_dir_value)
    # Unless more direction are specified, which is an error
    if len(result_dirs) > len(result_keys):
        msg = _("Sort direction array size exceeds sort key array size.")
        raise exception.InvalidInput(reason=msg)
    # Ensure defaults are included
    for key in default_keys:
        if key not in result_keys:
            result_keys.append(key)
            result_dirs.append(default_dir_value)
    return result_keys, result_dirs


def _generate_paginate_query(context, session, paginate_type, marker,
                             limit, sort_keys, sort_dirs, filters,
                             offset=None,
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
