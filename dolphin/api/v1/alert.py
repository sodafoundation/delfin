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


SNMPv3_keys = ('username', 'auth_key', 'auth_enabled', 'auth_protocol',
               'encryption_enabled', 'privacy_protocol', 'privacy_key',
               'engine_id')


class AlertController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.driver_api = driver_api.API()

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

            if self._exist(ctx, id):
                alert_source = db.alert_source_update(ctx, id, alert_source)
            else:
                alert_source = db.alert_source_create(ctx, alert_source)
        except exception.StorageNotFound as e:
            msg = (_("Alert source cannot be created or updated for a"
                     " non-existing storage %s.") % id)
            raise exc.HTTPBadRequest(explanation=msg)
        except exception.InvalidInput as e:
            raise exc.HTTPBadRequest(explanation=e.msg)

        return alert_view.build_alert_source(alert_source.to_dict())

    @wsgi.response(200)
    def show(self, req, id):
        ctx = req.environ['dolphin.context']
        try:
            alert_source = db.alert_source_get(ctx, id)
        except exception.AlertSourceNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)

        return alert_view.build_alert_source(alert_source.to_dict())

    @wsgi.response(200)
    def delete(self, req, id):
        ctx = req.environ['dolphin.context']
        try:
            db.alert_source_delete(ctx, id)
        except exception.AlertSourceNotFound as e:
            raise exc.HTTPNotFound(explanation=e.msg)

    def _input_check(self, alert_source):
        version = alert_source.get('version')

        if version.lower() == 'snmpv3':
            user_name = alert_source.get('username', None)
            auth_enabled_str = alert_source.get('auth_enabled', None)
            engine_id = alert_source.get('engine_id', None)
            if not user_name or not auth_enabled_str or not engine_id:
                msg = "If snmp version is SNMPv3, then username, auth_enabled" \
                      " and engine_id are required."
                raise exception.InvalidInput(reason=msg)
            auth_enabled = utils.bool_from_string(auth_enabled_str, True)
            alert_source['auth_enabled'] = auth_enabled

            if auth_enabled:
                auth_protocol = alert_source.get('auth_protocol', None)
                auth_key = alert_source.get('auth_key', None)
                if not auth_protocol or not auth_key:
                    msg = "If snmp version is SNMPv3 and auth is enabled, then " \
                          "auth_protocol and auth_key is required."
                    raise exception.InvalidInput(reason=msg)
                alert_source['auth_key'] = cryptor.encode(alert_source['auth_key'])

                # If encryption_enabled is not set, False will be used as default.
                encryption_enabled = utils.bool_from_string(
                    alert_source.get('encryption_enabled', ""),
                    False)
                alert_source['encryption_enabled'] = encryption_enabled
                if encryption_enabled:
                    privacy_protocol = alert_source.get('privacy_protocol', None)
                    privacy_key = alert_source.get('privacy_key', None)
                    if not privacy_protocol or not privacy_key:
                        msg = "If snmp version is SNMPv3 and encryption is " \
                              "enabled, privacy_protocol and privacy_key are" \
                              " required."
                        raise exception.InvalidInput(reason=msg)
                    alert_source['privacy_key'] = cryptor.encode(
                        alert_source['privacy_key'])

            # Clear keys for other versions.
            alert_source['community_string'] = None
        else:
            community_string = alert_source.get('community_string', None)
            if not community_string:
                msg = "If snmp version is SNMPv1 or SNMPv2c, " \
                      "community_string is required."
                raise exception.InvalidInput(reason=msg)

            # Clear keys for SNMPv3
            for k in SNMPv3_keys:
                alert_source[k] = None

        return alert_source

    def _exist(self, ctx, storage_id):
        try:
            db.alert_source_get(ctx, storage_id)
        except exception.AlertSourceNotFound:
            return False

        return True

    def _decrypt_auth_key(self, alert_source):
        auth_key = alert_source.get('auth_key', None)
        privacy_key = alert_source.get('privacy_key', None)
        if auth_key:
            alert_source['auth_key'] = cryptor.decode(auth_key)
        if privacy_key:
            alert_source['privacy_key'] = cryptor.decode(privacy_key)

        return alert_source


def create_resource():
    return wsgi.Resource(AlertController())
