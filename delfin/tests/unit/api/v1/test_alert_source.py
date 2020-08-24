# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest import mock

from oslo_utils import importutils

from delfin.common import config # noqa
from delfin import cryptor
from delfin import exception
from delfin.tests.unit.api import fakes


class AlertSourceControllerTestCase(unittest.TestCase):
    ALERT_CONTROLLER_CLASS = 'delfin.api.v1.alert_source.AlertSourceController'

    @mock.patch('delfin.alert_manager.rpcapi.AlertAPI', mock.Mock())
    def _get_alert_controller(self):
        alert_controller_class = importutils.import_class(
            self.ALERT_CONTROLLER_CLASS)
        alert_controller = alert_controller_class()
        return alert_controller

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_authpriv_config_create_success(self, mock_alert_source_get,
                                                   mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'host': '127.0.0.1',
                                 'community_string': None,
                                 'version': 'snmpv3',
                                 'engine_id': '800000d30300000e112245',
                                 'security_level': None,
                                 'username': 'test1',
                                 'auth_protocol': 'HMACMD5',
                                 'privacy_protocol': 'DES',
                                 'port': 161,
                                 'context_name': "",
                                 'retry_num': 1,
                                 'expiration': 1,
                                 "created_at": '2020-06-15T09:50:31.698956',
                                 "updated_at": '2020-06-15T09:50:31.698956'
                                 }
        mock_alert_source_update.return_value = fakes.fake_v3_alert_source()
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()

        output_alert_source = alert_controller_inst.put(req, fake_storage_id,
                                                        body=body)
        self.assertDictEqual(expected_alert_source, output_alert_source)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_config_noauthnopriv_create_success(self,
                                                       mock_alert_source_get,
                                                       mock_alert_source_update
                                                       ):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = fakes. \
            fake_v3_alert_source_noauth_nopriv()
        mock_alert_source_get.return_value = fakes. \
            fake_v3_alert_source_noauth_nopriv()
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'host': '127.0.0.1',
                                 'community_string': None,
                                 'version': 'snmpv3',
                                 'engine_id': '800000d30300000e112245',
                                 'security_level': 'noAuthnoPriv',
                                 'username': 'test1',
                                 'auth_protocol': None,
                                 'privacy_protocol': None,
                                 'port': 161,
                                 'context_name': "",
                                 'retry_num': 1,
                                 'expiration': 1,
                                 "created_at": '2020-06-15T09:50:31.698956',
                                 "updated_at": '2020-06-15T09:50:31.698956'
                                 }

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'noAuthnoPriv'

        output_alert_source = alert_controller_inst.put(req, fake_storage_id,
                                                        body=body)
        self.assertDictEqual(expected_alert_source, output_alert_source)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_config_authnopriv_create_success(self,
                                                     mock_alert_source_get,
                                                     mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = fakes. \
            fake_v3_alert_source_auth_nopriv()
        mock_alert_source_get.return_value = fakes. \
            fake_v3_alert_source_auth_nopriv()
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'host': '127.0.0.1',
                                 'community_string': None,
                                 'version': 'snmpv3',
                                 'engine_id': '800000d30300000e112245',
                                 'security_level': 'authNoPriv',
                                 'username': 'test1',
                                 'auth_protocol': 'HMACMD5',
                                 'privacy_protocol': None,
                                 'port': 161,
                                 'context_name': "",
                                 'retry_num': 1,
                                 'expiration': 1,
                                 "created_at": '2020-06-15T09:50:31.698956',
                                 "updated_at": '2020-06-15T09:50:31.698956'
                                 }
        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'authNoPriv'

        output_alert_source = alert_controller_inst.put(req, fake_storage_id,
                                                        body=body)
        self.assertDictEqual(expected_alert_source, output_alert_source)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v2_config_success(self, mock_alert_source_get,
                                   mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        return_v2_alert_source = fakes.fake_v2_alert_source()
        return_v2_alert_source['community_string'] = cryptor.encode(
            return_v2_alert_source['community_string'])
        mock_alert_source_update.return_value = return_v2_alert_source
        mock_alert_source_get.return_value = return_v2_alert_source
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'host': '127.0.0.1',
                                 'community_string': 'public',
                                 'version': 'snmpv2c',
                                 'engine_id': None,
                                 'security_level': None,
                                 'username': None,
                                 'auth_protocol': None,
                                 'privacy_protocol': None,
                                 'port': 161,
                                 'context_name': "",
                                 'retry_num': 1,
                                 'expiration': 1,
                                 "created_at": '2020-06-15T09:50:31.698956',
                                 "updated_at": '2020-06-15T09:50:31.698956'
                                 }
        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v2_alert_source_config()

        output_alert_source = alert_controller_inst.put(req, fake_storage_id,
                                                        body=body)
        self.assertDictEqual(expected_alert_source, output_alert_source)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_delete')
    @mock.patch('delfin.db.alert_source_get')
    def test_delete_v3_config_success(self, mock_alert_source_get,
                                      mock_alert_source_delete):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_delete.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        alert_controller_inst.delete(req, fake_storage_id)
        self.assertTrue(mock_alert_source_delete.called)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_delete')
    @mock.patch('delfin.db.alert_source_get',
                fakes.alert_source_get_exception)
    def test_delete_v3_config_failure(self, mock_alert_source_delete):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_delete.return_value = {}

        alert_controller_inst = self._get_alert_controller()
        self.assertRaisesRegex(exception.AlertSourceNotFound, "Alert source "
                                                              "for storage "
                                                              "abcd-1234-5678 "
                                                              "could not be "
                                                              "found",
                               alert_controller_inst.delete, req,
                               fake_storage_id)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_get')
    def test_show_v3_config(self, mock_alert_source_get):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'host': '127.0.0.1',
                                 'community_string': None,
                                 'version': 'snmpv3',
                                 'engine_id': '800000d30300000e112245',
                                 'security_level': None,
                                 'username': 'test1',
                                 'auth_protocol': 'HMACMD5',
                                 'privacy_protocol': 'DES',
                                 'port': 161,
                                 'context_name': "",
                                 'retry_num': 1,
                                 'expiration': 1,
                                 "created_at": '2020-06-15T09:50:31.698956',
                                 "updated_at": '2020-06-15T09:50:31.698956'
                                 }
        alert_controller_inst = self._get_alert_controller()
        output_alert_source = alert_controller_inst.show(req, fake_storage_id)
        self.assertDictEqual(expected_alert_source, output_alert_source)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_authpriv_no_priv_key(self,
                                         mock_alert_source_get,
                                         mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'authPriv'
        body['privacy_key'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input for "
                                                       "field/attribute "
                                                       "privacy_key",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_authpriv_no_priv_protocol(self,
                                              mock_alert_source_get,
                                              mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'authPriv'
        body['privacy_protocol'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input for "
                                                       "field/attribute "
                                                       "privacy_protocol",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_authnopriv_no_auth_protocol(self,
                                                mock_alert_source_get,
                                                mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'authNoPriv'
        body['auth_protocol'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input for "
                                                       "field/attribute "
                                                       "auth_protocol",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_v3_authnopriv_no_auth_key(self,
                                           mock_alert_source_get,
                                           mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'authNoPriv'
        body['auth_key'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input for "
                                                       "field/attribute "
                                                       "auth_key",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_without_username(self, mock_alert_source_get,
                                  mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['username'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input "
                                                       "received. Invalid "
                                                       "input for "
                                                       "field/attribute "
                                                       "username.",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_without_engine_id(self, mock_alert_source_get,
                                   mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v3_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['engine_id'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input "
                                                       "received. Invalid "
                                                       "input for "
                                                       "field/attribute "
                                                       "engine_id..",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    def test_put_without_community_str(self, mock_alert_source_get,
                                       mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = {}
        mock_alert_source_get.return_value = fakes.fake_v2_alert_source()

        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v2_alert_source_config()
        body['community_string'] = ''

        self.assertRaisesRegex(exception.InvalidInput, "Invalid input "
                                                       "received. Invalid "
                                                       "input for "
                                                       "field/attribute "
                                                       "community_string.",
                               alert_controller_inst.put, req, fake_storage_id,
                               body=body)

    @mock.patch('delfin.db.storage_get', mock.Mock())
    @mock.patch('delfin.db.alert_source_update')
    @mock.patch('delfin.db.alert_source_get')
    @mock.patch('pysnmp.entity.rfc3413.oneliner.cmdgen.CommandGenerator'
                '.getCmd', fakes.fake_getcmd_success)
    def test_put_v3_snmp_validation_success(self,
                                            mock_alert_source_get,
                                            mock_alert_source_update):
        req = fakes.HTTPRequest.blank('/storages/fake_id/alert-source')
        fake_storage_id = 'abcd-1234-5678'
        mock_alert_source_update.return_value = fakes. \
            fake_v3_alert_source_auth_nopriv()
        mock_alert_source_get.return_value = fakes. \
            fake_v3_alert_source_auth_nopriv()
        expected_alert_source = {'storage_id': 'abcd-1234-5678',
                                 'host': '127.0.0.1',
                                 'community_string': None,
                                 'version': 'snmpv3',
                                 'engine_id': '800000d30300000e112245',
                                 'security_level': 'authNoPriv',
                                 'username': 'test1',
                                 'auth_protocol': 'HMACMD5',
                                 'privacy_protocol': None,
                                 'port': 161,
                                 'context_name': "",
                                 'retry_num': 1,
                                 'expiration': 1,
                                 "created_at": '2020-06-15T09:50:31.698956',
                                 "updated_at": '2020-06-15T09:50:31.698956'
                                 }
        alert_controller_inst = self._get_alert_controller()
        body = fakes.fake_v3_alert_source_config()
        body['security_level'] = 'authNoPriv'

        output_alert_source = alert_controller_inst.put(req, fake_storage_id,
                                                        body=body)
        self.assertDictEqual(expected_alert_source, output_alert_source)
