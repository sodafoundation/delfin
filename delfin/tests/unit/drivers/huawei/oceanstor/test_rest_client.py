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

from unittest import TestCase, mock
from requests.sessions import Session

from delfin import exception
from delfin.common import config # noqa
from delfin.drivers.huawei.oceanstor.rest_client import RestClient


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "huawei",
    "model": "oceanstor",
    "rest": {
        "host": "10.0.0.1",
        "port": 1234,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    },
    "extra_attributes": {
        "array_id": "00112233"
    }
}

RESP = {
    "error": {
        "code": 0
    },
    "data": {
        "data": "dummy",
        "deviceid": "0123456",
        "iBaseToken": "112233",
        "accountstate": "GREEN"
    }
}


class TestOceanStorRestClient(TestCase):

    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):

        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        mock_resp.content = content
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    # @mock.patch.object(RestClient, 'login')
    @mock.patch.object(Session, 'post')
    def test_init(self, mock_rest):
        mock_resp = self._mock_response(json_data=RESP)
        mock_rest.return_value = mock_resp
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        self.assertEqual(rest_client.rest_host, "10.0.0.1")
        self.assertEqual(rest_client.rest_port, 1234)
        self.assertEqual(rest_client.session.headers['iBaseToken'], '112233')

    @mock.patch.object(RestClient, 'login')
    def test_reset_connection(self, mock_login):
        mock_login.return_value = None
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        self.assertEqual(rest_client.rest_host, "10.0.0.1")
        self.assertEqual(rest_client.rest_port, 1234)

        mock_login.side_effect = exception.StorageBackendException
        with self.assertRaises(Exception) as exc:
            RestClient(**kwargs)
        self.assertIn('The credentials are invalid',
                      str(exc.exception))

    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_get_storage(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_storage()
        self.assertEqual(data['data'], 'dummy')

        mock_call.return_value = {
            "error": {
                "code": 0
            }
        }
        with self.assertRaises(Exception) as exc:
            rest_client.get_storage()
        self.assertIn('Exception from Storage Backend',
                      str(exc.exception))

        mock_call.return_value['error']['code'] = 1
        with self.assertRaises(Exception) as exc:
            rest_client.get_storage()
        self.assertIn('Exception from Storage Backend',
                      str(exc.exception))

    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_get_controller(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_controller()
        self.assertEqual(data['data'], 'dummy')
        mock_call.assert_called_with("/controller",
                                     log_filter_flag=True, method='GET')

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_pools(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_pools()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/storagepool", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_volumes(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_volumes()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/lun", None, 'GET',
                                     log_filter_flag=True)
