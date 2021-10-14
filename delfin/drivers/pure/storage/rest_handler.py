import six
from oslo_log import log as logging

from delfin import exception, cryptor
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_STORAGE_URL = '/api/1.17/array?space=true'
    REST_STORAGE_ID_URL = '/api/1.17/array'
    REST_VOLUME_URL = '/api/1.17/volume?space=true&limit=20&token=aWQgPSA5ODA1Mg=='
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
    HTTPS = 'https://'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)
        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input pure_rest_access is missing')
        self.host = rest_access.get('host')
        self.port = rest_access.get('port')
        self.username = rest_access.get('username')
        self.password = rest_access.get('password')

    def login(self):
        try:
            data = {'username': self.username, 'password': cryptor.decode(self.password)}
            token = self.get_rest_login(RestHandler.REST_AUTH_URL, data, method='POST')
            api_token = token.get('api_token')
            if api_token is None and api_token == '':
                raise exception.InvalidInput('api_token fail to get')
            user = self.get_rest_login(RestHandler.REST_SESSION_URL, token, method='POST')
            username = user.get('username')
            if username is None and username == '':
                raise exception.InvalidInput('session fail to get')
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise exception.InvalidInput('login failure')

    def logout(self):
        user = self.get_rest_login(RestHandler.REST_SESSION_URL, method='DELETE')
        username = user.get('username')
        if username is None and username == '':
            raise exception.InvalidInput('delete fail to get')

    def get_all_rest_volumes(self):
        url = '%s%s:%s%s' % (RestHandler.HTTPS, self.host, self.port, RestHandler.REST_VOLUME_URL)
        result_json = self.get_rest_volumes_info(url)
        return result_json

    def get_all_rest_volumes_id(self, name):
        result_json = self.get_rest_info('{}{}'.format(RestHandler.REST_VOLUME_ID_URL, name))
        return result_json

    def get_storage(self):
        result_json = self.get_rest_info(RestHandler.REST_STORAGE_URL)
        return result_json

    def get_storage_ID(self):
        result_json = self.get_rest_info(RestHandler.REST_STORAGE_ID_URL)
        return result_json

    def get_all_pools(self):
        result_json = self.get_rest_info(RestHandler.REST_POOLS_URL)
        return result_json

    def get_capacity_pools(self):
        result_json = self.get_rest_info(RestHandler.REST_POOLS_CAPACITY_URL)
        return result_json

    def get_all_port(self):
        result_json = self.get_rest_info(RestHandler.REST_PORT_URL)
        return result_json

    def get_all_network(self):
        result_json = self.get_rest_info(RestHandler.REST_NETWORK_URL)
        return result_json

    def get_all_disk(self):
        result_json = self.get_rest_info(RestHandler.REST_DISK_URL)
        return result_json

    def get_all_hardware(self):
        result_json = self.get_rest_info(RestHandler.REST_HARDWARE_URL)
        return result_json

    def get_all_controllers(self):
        result_json = self.get_rest_info(RestHandler.REST_CONTROLLERS_URL)
        return result_json

    def get_all_alerts(self):
        result_json = self.get_rest_info(RestHandler.REST_ALERTS_URL)
        return result_json

    # 请求远程方法
    def get_rest_info(self, url, data=None, method='GET'):
        result_json = None
        # 请求远程接口
        res = self.do_call(url, data, method)
        if res.status_code == 200:
            result_json = res.json()
        elif res.status_code == 401:
            self.login()
            self.get_rest_info(url, data, method)
        return result_json

    def get_rest_login(self, url, data=None, method='GET'):
        self.init_http_head()
        # 请求远程接口
        res = self.do_call(url, data, method)
        result_json = res.json()
        return result_json

    def get_rest_volumes_info(self, url, data=None, volume_list=None):
        if volume_list is None:
            volume_list = []
        # 请求远程接口
        res = self.do_call(url, data, 'GET')
        if res.status_code == 200:
            result_json = res.json()
            volume_list.extend(result_json)
            next_token = res.headers._store.get('x-next-token')
            if next_token:
                token = next_token[1]
                if token:
                    url = '%s%s:%s%s%s' % (RestHandler.HTTPS, self.host, self.port,
                                           RestHandler.REST_VOLUME_TOKEN_URL, token)
                    self.get_rest_volumes_info(url, data, volume_list)
        elif res.status_code == 401:
            self.login()
            self.get_rest_volumes_info(url, data, volume_list)
        return volume_list
