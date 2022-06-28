# Copyright 2022 The SODA Authors.
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
import six
from oslo_log import log as logging

from delfin import exception, cryptor
from delfin.drivers.pure.flasharray import consts
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_STORAGE_URL = '/api/1.17/array?space=true'
    REST_ARRAY_URL = '/api/1.17/array'
    REST_VOLUME_URL = '/api/1.17/volume?space=true&limit=500&token=' \
                      'aWQgPSA5ODA1Mg=='
    REST_VOLUME_TOKEN_URL = '/api/1.17/volume?space=true&limit=20&token='
    REST_PORT_URL = '/api/1.17/port'
    REST_NETWORK_URL = '/api/1.17/network'
    REST_DISK_URL = '/api/1.17/drive'
    REST_HARDWARE_URL = '/api/1.17/hardware'
    REST_CONTROLLERS_URL = '/api/1.17/array?controllers=true'
    REST_ALERTS_URL = '/api/1.17/message?flagged=true&open=true'
    REST_AUTH_URL = '/api/1.17/auth/apitoken'
    REST_SESSION_URL = '/api/1.17/auth/session'
    REST_HOST_URL = '/api/1.17/host'
    REST_HOST_PERSONALITY_URL = '/api/1.17/host?personality=true'
    REST_HOST_CONNECT_URL = '/api/1.17/host?connect=true'
    REST_HGROUP_CONNECT_URL = '/api/1.17/hgroup?connect=true'
    REST_HGROUP_URL = '/api/1.17/hgroup'
    REST_VOLUME_GROUP_URL = '/api/1.17/vgroup'
    REST_ARRAY_HISTORICAL_URL = '/api/1.17/array?action=monitor&historical=1h'
    REST_VOLUME_HISTORICAL_URL =\
        '/api/1.17/volume?action=monitor&historical=1h'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)

    def login(self):
        try:
            data = {'username': self.rest_username, 'password': cryptor.decode(
                self.rest_password)}
            self.init_http_head()
            token_res = self.do_call(RestHandler.REST_AUTH_URL, data,
                                     method='POST')
            if token_res.json().get('msg') == consts.LOGIN_PASSWORD_ERR:
                LOG.error("Login error, Obtaining the token is abnormal. "
                          "status_code:%s, URL: %s",
                          token_res.status_code, RestHandler.REST_AUTH_URL)
                raise exception.InvalidUsernameOrPassword(
                    'Obtaining the token is abnormal')
            if token_res.status_code != consts.SUCCESS_STATUS_CODE or not \
                    token_res.json().get('api_token'):
                LOG.error("Login error, Obtaining the token is abnormal. "
                          "status_code:%s, URL: %s",
                          token_res.status_code, RestHandler.REST_AUTH_URL)
                raise exception.StorageBackendException(
                    'Obtaining the token is abnormal')
            session_res = self.do_call(RestHandler.REST_SESSION_URL,
                                       token_res.json(), method='POST')
            if session_res.status_code != consts.SUCCESS_STATUS_CODE or not \
                    session_res.json().get('username'):
                LOG.error("Login error, Obtaining the session is abnormal."
                          "status_code:%s, URL: %s", session_res.status_code,
                          RestHandler.REST_SESSION_URL)
                raise exception.StorageBackendException(
                    'Obtaining the session is abnormal.')
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e
        finally:
            data = None
            token_res = None

    def logout(self):
        res = self.do_call(RestHandler.REST_SESSION_URL, None, method='DELETE')
        if res.status_code != consts.SUCCESS_STATUS_CODE\
                or not res.json().get('username'):
            LOG.error("Logout error, Deleting a Token Exception."
                      "status_code:%s, URL: %s",
                      res.status_code, RestHandler.REST_SESSION_URL)
            raise exception.StorageBackendException(res.text)

    def rest_call(self, url, data=None, method='GET'):
        result_json = None
        res = self.do_call(url, data, method)
        if res.status_code == consts.SUCCESS_STATUS_CODE:
            result_json = res.json()
        elif res.status_code == consts.PERMISSION_DENIED_STATUS_CODE:
            self.login()
            the_second_time_res = self.do_call(url, data, method)
            if the_second_time_res.status_code == consts.SUCCESS_STATUS_CODE:
                result_json = the_second_time_res.json()
        return result_json

    def get_volumes(self, url=REST_VOLUME_URL, data=None, volume_list=None,
                    count=consts.DEFAULT_COUNT_GET_VOLUMES_INFO):
        if volume_list is None:
            volume_list = []
        res = self.do_call(url, data, 'GET')
        if res.status_code == consts.SUCCESS_STATUS_CODE:
            result_json = res.json()
            volume_list.extend(result_json)
            next_token = res.headers.get(consts.CUSTOM_TOKEN)
            if next_token:
                url = '%s%s' % (RestHandler.REST_VOLUME_TOKEN_URL, next_token)
                self.get_volumes(url, data, volume_list)
        elif res.status_code == consts.PERMISSION_DENIED_STATUS_CODE:
            self.login()
            if count < consts.RE_LOGIN_TIMES:
                count = count + consts.CONSTANT_ONE
                self.get_volumes(url, data, volume_list, count)
        return volume_list
