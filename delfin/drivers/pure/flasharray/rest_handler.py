import six
from oslo_log import log as logging

from delfin import exception, cryptor
from delfin.drivers.pure.flasharray import consts
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_STORAGE_URL = '/api/1.17/array?space=true'
    REST_ARRAY_URL = '/api/1.17/array'
    REST_VOLUME_URL = '/api/1.17/volume?space=true&limit=20&token=aWQgPSA5OD' \
                      'A1Mg=='
    REST_VOLUME_TOKEN_URL = '/api/1.17/volume?space=true&limit=20&token='
    REST_VOLUME_ID_URL = '/api/1.17/volume/'
    REST_POOLS_URL = '/api/1.17/vgroup'
    REST_POOLS_CAPACITY_URL = '/api/1.17/vgroup?space=true'
    REST_PORT_URL = '/api/1.17/port'
    REST_NETWORK_URL = '/api/1.17/network'
    REST_DISK_URL = '/api/1.17/drive'
    REST_HARDWARE_URL = '/api/1.17/hardware'
    REST_CONTROLLERS_URL = '/api/1.17/array?controllers=true'
    REST_ALERTS_URL = '/api/1.17/message?flagged=true'
    REST_AUTH_URL = '/api/1.17/auth/apitoken'
    REST_SESSION_URL = '/api/1.17/auth/session'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)

    def login(self):
        try:
            data = {'username': self.rest_username, 'password': cryptor.decode(
                self.rest_password)}
            self.init_http_head()
            token_res = self.get_token(RestHandler.REST_AUTH_URL, data,
                                       method='POST')
            if token_res.status_code != consts.SUCCESS_STATUS_CODE:
                LOG.error("Login error. status_code:%s, URL: %s, Reason: %s.",
                          token_res.status_code, RestHandler.REST_AUTH_URL,
                          token_res.text)
                raise exception.StorageBackendException(token_res.text)
            else:
                api_token = token_res.json().get('api_token')
                if not api_token:
                    LOG.error("Login error. status_code:%s, URL: %s, Reason: "
                              "%s", token_res.status_code,
                              RestHandler.REST_AUTH_URL,
                              'The API token does not exist')
                    raise exception.InvalidResults('The API token does not '
                                                   'exist')
                session_res = self.get_token(RestHandler.REST_SESSION_URL,
                                             token_res.json(), method='POST')
                if session_res.status_code == consts.SUCCESS_STATUS_CODE:
                    username = session_res.json().get('username')
                    if not username:
                        LOG.error("Login error. status_code:%s, URL: %s, "
                                  "Reason: %s", session_res.status_code,
                                  RestHandler.REST_SESSION_URL,
                                  'The API session does not exist')
                        raise exception.InvalidResults('The API session does '
                                                       'not exist')
                else:
                    LOG.error("Login error. status_code:%s,"
                              " URL: %s, Reason: %s.", session_res.status_code,
                              RestHandler.REST_AUTH_URL, session_res.text)
                    raise exception.StorageBackendException(
                        session_res.text)
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def logout(self):
        res = self.get_token(RestHandler.REST_SESSION_URL, method='DELETE')
        if res.status_code == consts.SUCCESS_STATUS_CODE:
            username = res.json().get('username')
            if not username:
                raise exception.InvalidResults('The returned username'
                                               ' is empty')
        else:
            LOG.error("Logout error.status_code:%s, URL: %s, Reason: %s.",
                      res.status_code, RestHandler.REST_SESSION_URL, res.text)
            raise exception.StorageBackendException(res.text)

    def rest_call(self, url, data=None, method='GET'):
        result_json = None
        res = self.do_call(url, data, method)
        if res.status_code == consts.SUCCESS_STATUS_CODE:
            result_json = res.json()
        elif res.status_code == consts.PERMISSION_DENIED_STATUS_CODE:
            self.login()
            self.rest_call(url, data, method)
        return result_json

    def get_token(self, url, data=None, method='GET'):
        res = self.do_call(url, data, method)
        return res

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
                token = next_token[consts.DEFAULT_LIST_GET_VOLUMES_INFO]
                if token:
                    url = '%s%s' % (RestHandler.REST_VOLUME_TOKEN_URL, token)
                    self.get_volumes(url, data, volume_list)
        elif res.status_code == consts.PERMISSION_DENIED_STATUS_CODE:
            self.login()
            if count < consts.RE_LOGIN_TIMES:
                count = count + consts.CONSTANT_ONE
                self.get_volumes(url, data, volume_list, count)
        return volume_list
