# Copyright 2014 IBM Corp.
# Copyright 2015 Clinton Knight
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

import re
import six

from dolphin.api.common import versioned_method
from dolphin import exception
from dolphin.i18n import _
from dolphin import utils

# Define the minimum and maximum version of the API across all of the
# REST API. The format of the version is:
# X.Y where:
#
# - X will only be changed if a significant backwards incompatible API
# change is made which affects the API as whole. That is, something
# that is only very very rarely incremented.
#
# - Y when you make any change to the API. Note that this includes
# semantic changes which may not affect the input or output formats or
# even originate in the API code layer. We are not distinguishing
# between backwards compatible and backwards incompatible changes in
# the versioning system. It must be made clear in the documentation as
# to what is a backwards compatible change and what is a backwards
# incompatible one.

#
# You must update the API version history string below with a one or
# two line description as well as update rest_api_version_history.rst
REST_API_VERSION_HISTORY = """

    REST API Version History:

    * 1.0  - Initial version. Includes all V1 APIs and extensions in Kilo.
    * 2.0  - Versions API updated to reflect beginning of microversions epoch.
    * 2.1  - Share create() doesn't ignore availability_zone field of share.
    * 2.2  - Snapshots become optional feature.
    * 2.3  - Share instances admin API
    * 2.4  - Consistency Group support
    * 2.5  - Share Migration admin API
    * 2.6  - Return share_type UUID instead of name in Share API
    * 2.7  - Rename old extension-like API URLs to core-API-like
    * 2.8  - Attr "is_public" can be set for share using API "manage"
    * 2.9  - Add export locations API
    * 2.10 - Field 'access_rules_status' was added to shares and share
            instances.
    * 2.11 - Share Replication support
    * 2.12 - Manage/unmanage snapshot API.
    * 2.13 - Add "cephx" auth type to allow_access
    * 2.14 - 'Preferred' attribute in export location metadata
    * 2.15 - Added Share migration 'migration_cancel',
            'migration_get_progress', 'migration_complete' APIs, renamed
            'migrate_share' to 'migration_start' and added notify parameter
             to 'migration_start'.
    * 2.16 - Add user_id in share show/create/manage API.
    * 2.17 - Added project_id and user_id fields to the JSON response of
             snapshot show/create/manage API.
    * 2.18 - Add gateway to the JSON response of share network show API.
    * 2.19 - Share snapshot instances admin APIs
            (list/show/detail/reset-status).
    * 2.20 - Add MTU to the JSON response of share network show API.
    * 2.21 - Add access_key to the response of access_list API.
    * 2.22 - Updated migration_start API with 'preserve-metadata', 'writable',
            'nondisruptive' and 'new_share_network_id' parameters, renamed
            'force_host_copy' to 'force_host_assisted_migration', removed
            'notify' parameter and removed previous migrate_share API support.
            Updated reset_task_state API to accept 'None' value.
    * 2.23 - Added share_type to filter results of scheduler-stats/pools API.
    * 2.24 - Added optional create_share_from_snapshot_support extra spec,
             which was previously inferred from the 'snapshot_support' extra
             spec. Also made the 'snapshot_support' extra spec optional.
    * 2.25 - Added quota-show detail API.
    * 2.26 - Removed 'nova_net_id' parameter from share_network API.
    * 2.27 - Added share revert to snapshot API.
    * 2.28 - Added transitional states to access rules and replaced all
             transitional access_rules_status values of
             shares (share_instances) with 'syncing'. Share action API
             'access_allow' now accepts rules even when a share or any of
             its instances may have an access_rules_status set to 'error'.
    * 2.29 - Updated migration_start API adding mandatory parameter
             'preserve_snapshots' and changed 'preserve_metadata', 'writable',
             'nondisruptive' to be mandatory as well. All previous
             migration_start APIs prior to this microversion are now
             unsupported.
    * 2.30 - Added cast_rules_to_readonly field to share_instances.
    * 2.31 - Convert consistency groups to share groups.
    * 2.32 - Added mountable snapshots APIs.
    * 2.33 - Added 'created_at' and 'updated_at' to the response of
             access_list API.
    * 2.34 - Added 'availability_zone_id' and 'consistent_snapshot_support'
             fields to 'share_group' object.
    * 2.35 - Added support to retrieve shares filtered by export_location_id
             and export_location_path.
    * 2.36 - Added like filter support in ``shares``, ``snapshots``,
             ``share-networks``, ``share-groups`` list APIs.
    * 2.37 - Added /messages APIs.
    * 2.38 - Support IPv6 validation in allow_access API to enable IPv6 in
             dolphin.
    * 2.39 - Added share-type quotas.
    * 2.40 - Added share group and share group snapshot quotas.
    * 2.41 - Added 'description' in share type create/list APIs.
    * 2.42 - Added ``with_count`` in share list API to get total count info.
    * 2.43 - Added filter search by extra spec for share type list.
    * 2.44 - Added 'ou' field to 'security_service' object.
    * 2.45 - Added access metadata for share access and also introduced
             the GET /share-access-rules API. The prior API to retrieve
             access rules will not work with API version >=2.45.
    * 2.46 - Added 'is_default' field to 'share_type' and 'share_group_type'
             objects.
    * 2.47 - Export locations for non-active share replicas are no longer
             retrievable through the export locations APIs:
             GET /v2/{tenant_id}/shares/{share_id}/export_locations and
             GET /v2/{tenant_id}/shares/{share_id}/export_locations/{
             export_location_id}. A new API is introduced at this
             version: GET /v2/{tenant_id}/share-replicas/{
             replica_id}/export-locations to allow retrieving individual
             replica export locations if available.
    * 2.48 - Added support for extra-spec "availability_zones" within Share
             types along with validation in the API.
    * 2.49 - Added Manage/Unmanage Share Server APIs. Updated Manage/Unmanage
             Shares and Snapshots APIs to work in
             ``driver_handles_shares_servers`` enabled mode.
    * 2.50 - Added update share type API to Share Type APIs. Through this API
             we can update the ``name``, ``description`` and/or
             ``share_type_access:is_public`` fields of the share type.
    * 2.51 - Added Share Network with multiple Subnets. Updated Share Networks
             to handle with one or more subnets in different availability
             zones.
"""

# The minimum and maximum versions of the API supported
# The default api version request is defined to be the
# minimum version of the API supported.
_MIN_API_VERSION = "2.0"
_MAX_API_VERSION = "2.51"
DEFAULT_API_VERSION = _MIN_API_VERSION


# NOTE(cyeoh): min and max versions declared as functions so we can
# mock them for unittests. Do not use the constants directly anywhere
# else.
def min_api_version():
    return APIVersionRequest(_MIN_API_VERSION)


def max_api_version():
    return APIVersionRequest(_MAX_API_VERSION)


class APIVersionRequest(utils.ComparableMixin):
    """This class represents an API Version Request.

    This class includes convenience methods for manipulation
    and comparison of version numbers as needed to implement
    API microversions.
    """

    def __init__(self, version_string=None, experimental=False):
        """Create an API version request object."""
        self._ver_major = None
        self._ver_minor = None
        self._experimental = experimental

        if version_string is not None:
            match = re.match(r"^([1-9]\d*)\.([1-9]\d*|0)$",
                             version_string)
            if match:
                self._ver_major = int(match.group(1))
                self._ver_minor = int(match.group(2))
            else:
                raise exception.InvalidAPIVersionString(version=version_string)

    def __str__(self):
        """Debug/Logging representation of object."""
        params = {
            'major': self._ver_major,
            'minor': self._ver_minor,
            'experimental': self._experimental,
        }
        return ("API Version Request Major: %(major)s, Minor: %(minor)s, "
                "Experimental: %(experimental)s" % params)

    def is_null(self):
        return self._ver_major is None and self._ver_minor is None

    def _cmpkey(self):
        """Return the value used by ComparableMixin for rich comparisons."""
        return self._ver_major, self._ver_minor

    @property
    def experimental(self):
        return self._experimental

    @experimental.setter
    def experimental(self, value):
        if type(value) != bool:
            msg = _('The experimental property must be a bool value.')
            raise exception.InvalidParameterValue(err=msg)
        self._experimental = value

    def matches_versioned_method(self, method):
        """Compares this version to that of a versioned method."""

        if type(method) != versioned_method.VersionedMethod:
            msg = _('An API version request must be compared '
                    'to a VersionedMethod object.')
            raise exception.InvalidParameterValue(err=msg)

        return self.matches(method.start_version,
                            method.end_version,
                            method.experimental)

    def matches(self, min_version, max_version, experimental=False):
        """Compares this version to the specified min/max range.

        Returns whether the version object represents a version
        greater than or equal to the minimum version and less than
        or equal to the maximum version.

        If min_version is null then there is no minimum limit.
        If max_version is null then there is no maximum limit.
        If self is null then raise ValueError.

        :param min_version: Minimum acceptable version.
        :param max_version: Maximum acceptable version.
        :param experimental: Whether to match experimental APIs.
        :returns: boolean
        """

        if self.is_null():
            raise ValueError
        # NOTE(cknight): An experimental request should still match a
        # non-experimental API, so the experimental check isn't just
        # looking for equality.
        if not self.experimental and experimental:
            return False

        if isinstance(min_version, six.string_types):
            min_version = APIVersionRequest(version_string=min_version)
        if isinstance(max_version, six.string_types):
            max_version = APIVersionRequest(version_string=max_version)

        if not (min_version or max_version):
            return True
        elif (min_version and max_version and
              max_version.is_null() and min_version.is_null()):
            return True

        elif not max_version or max_version.is_null():
            return min_version <= self
        elif not min_version or min_version.is_null():
            return self <= max_version
        else:
            return min_version <= self <= max_version

    def get_string(self):
        """Returns a string representation of this object.

        If this method is used to create an APIVersionRequest,
        the resulting object will be an equivalent request.
        """
        if self.is_null():
            raise ValueError
        return ("%(major)s.%(minor)s" %
                {'major': self._ver_major, 'minor': self._ver_minor})
