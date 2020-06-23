# Copyright 2020 The SODA Authors.
# Copyright 2010 OpenStack Foundation
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
import six

from oslo_config import cfg
from oslo_log import log
from oslo_utils import strutils

from delfin.common import constants
from delfin import exception
from delfin.i18n import _

api_common_opts = [
    cfg.IntOpt('api_max_limit',
               default=1000,
               help='The maximum number of items that a collection '
                    'resource returns in a single response'),

]

CONF = cfg.CONF
CONF.register_opts(api_common_opts)

LOG = log.getLogger(__name__)


def remove_invalid_options(context, search_options, allowed_search_options):
    """Remove search options that are not valid for API/context."""
    unknown_options = [opt for opt in search_options
                       if opt not in allowed_search_options]
    bad_options = ", ".join(unknown_options)
    LOG.debug("Removing options '%(bad_options)s' from query",
              {"bad_options": bad_options})
    for opt in unknown_options:
        del search_options[opt]


def validate_integer(value, name, min_value=None, max_value=None):
    """Make sure that value is a valid integer, potentially within range.

    :param value: the value of the integer
    :param name: the name of the integer
    :param min_value: the min_value of the integer
    :param max_value: the max_value of the integer
    :returns: integer
    """
    try:
        value = strutils.validate_integer(value, name, min_value, max_value)
        return value
    except ValueError as e:
        raise exception.InvalidInput(six.text_type(e))


def get_pagination_params(params, max_limit=None):
    """Return marker, limit, offset tuple from request.

    :param params: `wsgi.Request`'s GET dictionary, possibly containing
                   'marker',  'limit', and 'offset' variables. 'marker' is the
                   id of the last element the client has seen, 'limit' is the
                   maximum number of items to return and 'offset' is the number
                   of items to skip from the marker or from the first element.
                   If 'limit' is not specified, or > max_limit, we default to
                   max_limit. Negative values for either offset or limit will
                   cause delfin.InvalidInput() exceptions to be raised. If no
                   offset is present we'll default to 0 and if no marker is
                   present we'll default to None.
    :param max_limit: Max value 'limit' return value can take
    :returns: Tuple (marker, limit, offset)
    """
    max_limit = max_limit or CONF.api_max_limit
    limit = _get_limit_param(params, max_limit)
    marker = _get_marker_param(params)
    offset = _get_offset_param(params)
    return marker, limit, offset


def _get_limit_param(params, max_limit=None):
    """Extract integer limit from request's dictionary or fail.

   Defaults to max_limit if not present and returns max_limit if present
   'limit' is greater than max_limit.
    """
    max_limit = max_limit or CONF.osapi_max_limit
    try:
        limit = int(params.pop('limit', max_limit))
    except ValueError:
        msg = _('limit param must be an integer')
        raise exception.InvalidInput(msg)
    if limit < 0:
        msg = _('limit param must be positive')
        raise exception.InvalidInput(msg)
    limit = min(limit, max_limit)
    return limit


def _get_marker_param(params):
    """Extract marker id from request's dictionary (defaults to None)."""
    return params.pop('marker', None)


def _get_offset_param(params):
    """Extract offset id from request's dictionary (defaults to 0) or fail."""
    offset = params.pop('offset', 0)
    return validate_integer(offset,
                            'offset',
                            0,
                            constants.DB_MAX_INT)


def get_sort_params(params, default_key='created_at', default_dir='desc'):
    """Retrieves sort keys/directions parameters.

    Processes the parameters to create a list of sort keys and sort directions
    that correspond to either the 'sort' parameter or the 'sort_key' and
    'sort_dir' parameter values. The value of the 'sort' parameter is a comma-
    separated list of sort keys, each key is optionally appended with
    ':<sort_direction>'.

    The sort parameters are removed from the request parameters by this
    function.

    :param params: query parameters in the request
    :param default_key: default sort key value, added to the list if no
                        sort keys are supplied
    :param default_dir: default sort dir value, added to the list if the
                        corresponding key does not have a direction
                        specified
    :returns: list of sort keys, list of sort dirs

    """

    sort_keys = []
    sort_dirs = []
    if 'sort' in params:
        for sort in params.pop('sort').strip().split(','):
            sort_key, _sep, sort_dir = sort.partition(':')
            if not sort_dir:
                sort_dir = default_dir
            sort_keys.append(sort_key.strip())
            sort_dirs.append(sort_dir.strip())
    else:
        sort_key = params.pop('sort_key', default_key)
        sort_dir = params.pop('sort_dir', default_dir)
        sort_keys.append(sort_key.strip())
        sort_dirs.append(sort_dir.strip())
    return sort_keys, sort_dirs
