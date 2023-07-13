# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2010-2011 OpenStack Foundation
# Copyright 2012 Justin Santa Barbara
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

"""Implementation of paginate query."""
import datetime

from oslo_log import log as logging
from six.moves import range
import sqlalchemy
import sqlalchemy.sql as sa_sql
from sqlalchemy.sql import type_api

from delfin.db import api
from delfin import exception
from delfin.i18n import _


LOG = logging.getLogger(__name__)

_TYPE_SCHEMA = {
    'datetime': datetime.datetime(1900, 1, 1),
    'big_integer': 0,
    'integer': 0,
    'string': ''
}


def _get_default_column_value(model, column_name):
    """Return the default value of the columns from DB table.

    In postgreDB case, if no right default values are being set, an
    psycopg2.DataError will be thrown.
    """
    attr = getattr(model, column_name)
    # Return the default value directly if the model contains. Otherwise return
    # a default value which is not None.
    if attr.default and isinstance(attr.default, type_api.TypeEngine):
        return attr.default.arg

    attr_type = attr.type
    return _TYPE_SCHEMA[attr_type.__visit_name__]


# TODO(wangxiyuan): Use oslo_db.sqlalchemy.utils.paginate_query once it is
# stable and afforded by the minimum version in requirement.txt.
# copied from glance/db/sqlalchemy/api.py
def paginate_query(query, model, limit, sort_keys, marker=None,
                   sort_dir=None, sort_dirs=None, offset=None):
    """Returns a query with sorting / pagination criteria added.

    Pagination works by requiring a unique sort_key, specified by sort_keys.
    (If sort_keys is not unique, then we risk looping through values.)
    We use the last row in the previous page as the 'marker' for pagination.
    So we must return values that follow the passed marker in the order.
    With a single-valued sort_key, this would be easy: sort_key > X.
    With a compound-values sort_key, (k1, k2, k3) we must do this to repeat
    the lexicographical ordering:
    (k1 > X1) or (k1 == X1 && k2 > X2) or (k1 == X1 && k2 == X2 && k3 > X3)

    We also have to cope with different sort_directions.

    Typically, the id of the last row is used as the client-facing pagination
    marker, then the actual marker object must be fetched from the db and
    passed in to us as marker.

    :param query: the query object to which we should add paging/sorting
    :param model: the ORM model class
    :param limit: maximum number of items to return
    :param sort_keys: array of attributes by which results should be sorted
    :param marker: the last item of the previous page; we returns the next
                    results after this value.
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param sort_dirs: per-column array of sort_dirs, corresponding to sort_keys
    :param offset: the number of items to skip from the marker or from the
                    first element.

    :rtype: sqlalchemy.orm.query.Query
    :return: The query with sorting/pagination added.
    """

    if sort_dir and sort_dirs:
        raise AssertionError('Both sort_dir and sort_dirs specified.')

    # Default the sort direction to ascending
    if sort_dirs is None and sort_dir is None:
        sort_dir = 'asc'

    # Ensure a per-column sort direction
    if sort_dirs is None:
        sort_dirs = [sort_dir for _ in sort_keys]

    if len(sort_dirs) != len(sort_keys):
        raise AssertionError(
            'sort_dirs length is not equal to sort_keys length.')

    # Add sorting
    for current_sort_key, current_sort_dir in zip(sort_keys, sort_dirs):
        sort_dir_func = {
            'asc': sqlalchemy.asc,
            'desc': sqlalchemy.desc,
        }[current_sort_dir]

        try:
            sort_key_attr = getattr(model, current_sort_key)
        except AttributeError:
            raise exception.InvalidInput('Invalid sort key')
        if not api.is_orm_value(sort_key_attr):
            raise exception.InvalidInput('Invalid sort key')
        query = query.order_by(sort_dir_func(sort_key_attr))

    # Add pagination
    if marker is not None:
        marker_values = []
        for sort_key in sort_keys:
            v = getattr(marker, sort_key)
            if v is None:
                v = _get_default_column_value(model, sort_key)
            marker_values.append(v)

        # Build up an array of sort criteria as in the docstring
        criteria_list = []
        for i in range(0, len(sort_keys)):
            crit_attrs = []
            for j in range(0, i):
                model_attr = getattr(model, sort_keys[j])
                default = _get_default_column_value(model, sort_keys[j])
                attr = sa_sql.expression.case([(model_attr.isnot(None),
                                                model_attr), ],
                                              else_=default)
                crit_attrs.append((attr == marker_values[j]))

            model_attr = getattr(model, sort_keys[i])
            default = _get_default_column_value(model, sort_keys[i])
            attr = sa_sql.expression.case([(model_attr.isnot(None),
                                            model_attr), ],
                                          else_=default)
            if sort_dirs[i] == 'desc':
                crit_attrs.append((attr < marker_values[i]))
            elif sort_dirs[i] == 'asc':
                crit_attrs.append((attr > marker_values[i]))
            else:
                raise ValueError(_("Unknown sort direction, "
                                   "must be 'desc' or 'asc'"))

            criteria = sqlalchemy.sql.and_(*crit_attrs)
            criteria_list.append(criteria)

        f = sqlalchemy.sql.or_(*criteria_list)
        query = query.filter(f)

    if limit is not None:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query
