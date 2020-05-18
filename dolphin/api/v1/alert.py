# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_log import log
from webob import exc

from dolphin import db, cryptor
from dolphin import exception
from dolphin import utils
from dolphin.api import validation
from dolphin.api.common import wsgi
from dolphin.api.schemas import alert as schema_alert
from dolphin.api.views import alert as alert_view
from dolphin.drivers import api as driver_api
from dolphin.i18n import _

LOG = log.getLogger(__name__)


SNMPv3_keys = ('username', 'password', 'auth_enable', 'auth_protocol', 'encryption_enable',
               'encryption_protocol', 'encryption_password', 'engine_id')


class AlertController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.driver_api = driver_api.API()

    @staticmethod
    def exist(ctx, storage_id):
        try:
            db.alert_source_get(ctx, storage_id)
        except exception.AlertSourceNotFound:
            return False

        return True

    @staticmethod
    def decrypt_password(alert_source):
        password = alert_source.get('password', None)
        encryption_password = alert_source.get('encryption_password', None)
        if password:
            alert_source['password'] = cryptor.decode(password)
        if encryption_password:
            alert_source['encryption_password'] = cryptor.decode(encryption_password)

        return alert_source

    @wsgi.response(200)
    @validation.schema(schema_alert.put)
    def put(self, req, id, body):
        """Create a new alert source or update an exist one."""
        ctx = req.environ['dolphin.context']
        alert_source = body

        try:
            alert_source["storage_id"] = id
            db.storage_get(ctx, id)
            alert_source = self._input_check(alert_source)

            if self.exist(ctx, id):
                alert_source = db.alert_source_update(ctx, id, alert_source)
            else:
                alert_source = db.alert_source_create(ctx, alert_source)
        except exception.StorageNotFound as e:
            msg = (_("Alert source cannot be created or updated for a non-exist storage %s.") % id)
            raise exc.HTTPBadRequest(explanation=msg)
        except exception.InvalidInput as e:
            msg = _('Failed to put alert_source: {0}'.format(e))
            raise exc.HTTPBadRequest(explanation=msg)

        return alert_view.build_alert_source(self.decrypt_password(alert_source))

    @staticmethod
    def _input_check(alert_source):
        version = alert_source.get('version')

        if version.lower() == 'snmpv3':
            user_name = alert_source.get('username', None)
            auth_enable_str = alert_source.get('auth_enable', None)
            engine_id = alert_source.get('engine_id', None)
            if not user_name or not auth_enable_str or not engine_id:
                msg = "username, auth_enable and engine_id are required if snmp version is SNMPv3."
                raise exception.InvalidInput(reason=msg)
            auth_enable = utils.bool_from_string(auth_enable_str, True)
            alert_source['auth_enable'] = auth_enable

            if auth_enable:
                auth_protocol = alert_source.get('auth_protocol', None)
                password = alert_source.get('password', None)
                if not auth_protocol or not password:
                    msg = "auth_protocol and password is required if snmp version is SNMPv3 and auth is enabled."
                    raise exception.InvalidInput(reason=msg)
                alert_source['password'] = cryptor.encode(alert_source['password'])

                # In case encryption_enable is not set, False will be used as default.
                encryption_enable = utils.bool_from_string(alert_source.get('encryption_enable', ""), False)
                alert_source['encryption_enable'] = encryption_enable
                if encryption_enable:
                    encryption_protocol = alert_source.get('encryption_protocol', None)
                    encryption_password = alert_source.get('encryption_password', None)
                    if not encryption_protocol or not encryption_password:
                        msg = "encryption_protocol and encryption_password are required if snmp version is SNMPv3 " \
                              "and encryption is enabled."
                        raise exception.InvalidInput(reason=msg)
                    alert_source['encryption_password'] = cryptor.encode(alert_source['encryption_password'])

            # Clear keys for other versions.
            alert_source['community_string'] = None
        else:
            community_string = alert_source.get('community_string', None)
            if not community_string:
                msg = "Community string is required if snmp version is not SNMPv3."
                raise exception.InvalidInput(reason=msg)

            # Clear keys for SNMPv3
            for k in SNMPv3_keys:
                alert_source[k] = None

        return alert_source

    @wsgi.response(200)
    def show(self, req, id):
        ctx = req.environ['dolphin.context']
        try:
            alert_source = db.alert_source_get(ctx, id)
        except exception.AlertSourceNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)
        except Exception as e:
            LOG.error(e)
            raise exc.HTTPBadRequest(explanation=e.msg)

        return alert_view.build_alert_source(self.decrypt_password(alert_source))

    @wsgi.response(200)
    def delete(self, req, id):
        ctx = req.environ['dolphin.context']
        try:
            db.alert_source_delete(ctx, id)
        except exception.AlertSourceNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)


def create_resource():
    return wsgi.Resource(AlertController())
