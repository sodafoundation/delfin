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
from pyasn1.type.univ import OctetString

from delfin import db, cryptor
from delfin import exception
from delfin.alert_manager import rpcapi
from delfin.api import validation
from delfin.api.common import wsgi
from delfin.api.schemas import alert_source as schema_alert
from delfin.api.views import alert_source as alert_view
from delfin.common import constants

LOG = log.getLogger(__name__)

SNMPv3_keys = ('username', 'auth_key', 'security_level', 'auth_protocol',
               'privacy_protocol', 'privacy_key', 'engine_id')


class AlertSourceController(wsgi.Controller):
    def __init__(self):
        super().__init__()
        self.alert_rpcapi = rpcapi.AlertAPI()

    @wsgi.response(200)
    @validation.schema(schema_alert.put)
    def put(self, req, id, body):
        """Create a new alert source or update an exist one."""
        ctx = req.environ['delfin.context']
        alert_source = body

        alert_source["storage_id"] = id
        db.storage_get(ctx, id)
        alert_source = self._input_check(alert_source)

        snmp_config_to_del = self._get_snmp_config_brief(ctx, id)
        if snmp_config_to_del is not None:
            alert_source = db.alert_source_update(ctx, id, alert_source)
        else:
            alert_source = db.alert_source_create(ctx, alert_source)
        snmp_config_to_add = alert_source
        self.alert_rpcapi.sync_snmp_config(ctx, snmp_config_to_del,
                                           snmp_config_to_add)

        return alert_view.build_alert_source(alert_source.to_dict())

    @wsgi.response(200)
    def show(self, req, id):
        ctx = req.environ['delfin.context']
        alert_source = db.alert_source_get(ctx, id)

        return alert_view.build_alert_source(alert_source.to_dict())

    @wsgi.response(200)
    def delete(self, req, id):
        ctx = req.environ['delfin.context']

        snmp_config_to_del = self._get_snmp_config_brief(ctx, id)
        if snmp_config_to_del is not None:
            self.alert_rpcapi.sync_snmp_config(ctx, snmp_config_to_del,
                                               None)
            db.alert_source_delete(ctx, id)
        else:
            raise exception.AlertSourceNotFound(id)

    def _input_check(self, alert_source):
        version = alert_source.get('version')

        if version.lower() == 'snmpv3':
            user_name = alert_source.get('username')
            security_level = alert_source.get('security_level')
            engine_id = alert_source.get('engine_id')

            # Validate engine_id, check octet string can be formed from it
            if engine_id:
                try:
                    OctetString.fromHexString(engine_id)
                except (TypeError, ValueError):
                    msg = "engine_id should be a set of octets in " \
                          "hexadecimal format."
                    raise exception.InvalidInput(msg)

            if not user_name or not security_level:
                msg = "If snmp version is SNMPv3, then username, " \
                      "security_level are required."
                raise exception.InvalidInput(msg)

            if security_level == constants.SecurityLevel.AUTHNOPRIV\
                    or security_level == constants.SecurityLevel.AUTHPRIV:
                auth_protocol = alert_source.get('auth_protocol')
                auth_key = alert_source.get('auth_key')
                if not auth_protocol or not auth_key:
                    msg = "If snmp version is SNMPv3 and security_level is " \
                          "authPriv or authNoPriv, auth_protocol and " \
                          "auth_key are required."
                    raise exception.InvalidInput(msg)
                alert_source['auth_key'] = cryptor.encode(
                    alert_source['auth_key'])

                if security_level == constants.SecurityLevel.AUTHPRIV:
                    privacy_protocol = alert_source.get('privacy_protocol')
                    privacy_key = alert_source.get('privacy_key')
                    if not privacy_protocol or not privacy_key:
                        msg = "If snmp version is SNMPv3 and security_level" \
                              " is authPriv, privacy_protocol and " \
                              "privacy_key are  required."
                        raise exception.InvalidInput(msg)
                    alert_source['privacy_key'] = cryptor.encode(
                        alert_source['privacy_key'])
                else:
                    alert_source['privacy_key'] = None
                    alert_source['privacy_protocol'] = None
            else:
                alert_source['auth_key'] = None
                alert_source['auth_protocol'] = None
                alert_source['privacy_key'] = None
                alert_source['privacy_protocol'] = None

            # Clear keys for other versions.
            alert_source['community_string'] = None
        else:
            community_string = alert_source.get('community_string')
            if not community_string:
                msg = "If snmp version is SNMPv1 or SNMPv2c, " \
                      "community_string is required."
                raise exception.InvalidInput(msg)
            alert_source['community_string'] = cryptor.encode(
                alert_source['community_string'])

            # Clear keys for SNMPv3
            for k in SNMPv3_keys:
                alert_source[k] = None

        return alert_source

    def _get_snmp_config_brief(self, ctx, storage_id):
        """
        Get snmp configuration that will be used to delete from trap receiver.
        Only community_index(storage_id) required for snmp v1/v2 deletion,
        user_name and engine_id are required for snmp v3. So here we only get
        those required parameters. Return None if configuration not found.
        """
        try:
            alert_source = db.alert_source_get(ctx, storage_id)
            snmp_config = {"storage_id": alert_source["storage_id"],
                           "version": alert_source["version"]}
            if snmp_config["version"].lower() == "snmpv3":
                snmp_config["username"] = alert_source["username"]
                snmp_config["engine_id"] = alert_source["engine_id"]
            return snmp_config
        except exception.AlertSourceNotFound:
            return None

    def _decrypt_auth_key(self, alert_source):
        auth_key = alert_source.get('auth_key', None)
        privacy_key = alert_source.get('privacy_key', None)
        if auth_key:
            alert_source['auth_key'] = cryptor.decode(auth_key)
        if privacy_key:
            alert_source['privacy_key'] = cryptor.decode(privacy_key)

        return alert_source


def create_resource():
    return wsgi.Resource(AlertSourceController())
