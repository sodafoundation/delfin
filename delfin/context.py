# Copyright 2020 The SODA Authors.
# Copyright 2011 OpenStack LLC.
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

"""RequestContext: context for requests that persist through all of delfin."""

import copy

from oslo_context import context
from oslo_utils import timeutils
import six

from delfin.i18n import _


class RequestContext(context.RequestContext):
    """Security context and request information.

    Represents the user taking a given action within the system.

    """

    def __init__(self, user_id=None, project_id=None, is_admin=None,
                 read_deleted="no", roles=None, remote_address=None,
                 timestamp=None, request_id=None, auth_token=None,
                 overwrite=True, quota_class=None,
                 service_catalog=None, **kwargs):
        """Initialize RequestContext.

        :param read_deleted: 'no' indicates deleted records are hidden, 'yes'
            indicates deleted records are visible, 'only' indicates that
            *only* deleted records are visible.

        :param overwrite: Set to False to ensure that the greenthread local
            copy of the index is not overwritten.

        :param kwargs: Extra arguments that might be present, but we ignore
            because they possibly came in from older rpc messages.
        """

        user = kwargs.pop('user', None)
        tenant = kwargs.pop('tenant', None)
        super(RequestContext, self).__init__(
            auth_token=auth_token,
            user=user_id or user,
            tenant=project_id or tenant,
            domain=kwargs.pop('domain', None),
            user_domain=kwargs.pop('user_domain', None),
            project_domain=kwargs.pop('project_domain', None),
            is_admin=is_admin,
            read_only=kwargs.pop('read_only', False),
            show_deleted=kwargs.pop('show_deleted', False),
            request_id=request_id,
            resource_uuid=kwargs.pop('resource_uuid', None),
            overwrite=overwrite,
            roles=roles)

        self.user_id = self.user
        self.project_id = self.tenant

        self.read_deleted = read_deleted
        self.remote_address = remote_address
        if not timestamp:
            timestamp = timeutils.utcnow()
        if isinstance(timestamp, six.string_types):
            timestamp = timeutils.parse_strtime(timestamp)
        self.timestamp = timestamp
        if service_catalog:
            self.service_catalog = [s for s in service_catalog
                                    if s.get('type') in ('compute', 'volume')]
        else:
            self.service_catalog = []

        self.quota_class = quota_class

    def _get_read_deleted(self):
        return self._read_deleted

    def _set_read_deleted(self, read_deleted):
        if read_deleted not in ('no', 'yes', 'only'):
            raise ValueError(_("read_deleted can only be one of 'no', "
                               "'yes' or 'only', not %r") % read_deleted)
        self._read_deleted = read_deleted

    def _del_read_deleted(self):
        del self._read_deleted

    read_deleted = property(_get_read_deleted, _set_read_deleted,
                            _del_read_deleted)

    def to_dict(self):
        values = super(RequestContext, self).to_dict()
        values.update({
            'user_id': getattr(self, 'user_id', None),
            'project_id': getattr(self, 'project_id', None),
            'read_deleted': getattr(self, 'read_deleted', None),
            'remote_address': getattr(self, 'remote_address', None),
            'timestamp': self.timestamp.isoformat() if hasattr(
                self, 'timestamp') else None,
            'quota_class': getattr(self, 'quota_class', None),
            'service_catalog': getattr(self, 'service_catalog', None)})
        return values

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def elevated(self, read_deleted=None, overwrite=False):
        """Return a version of this context with admin flag set."""
        ctx = copy.deepcopy(self)
        ctx.is_admin = True

        if 'admin' not in ctx.roles:
            ctx.roles.append('admin')

        if read_deleted is not None:
            ctx.read_deleted = read_deleted

        return ctx


def get_admin_context(read_deleted="no"):
    return RequestContext(user_id=None,
                          project_id=None,
                          is_admin=True,
                          read_deleted=read_deleted,
                          overwrite=False)
