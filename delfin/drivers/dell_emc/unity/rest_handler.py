# Copyright 2021 The SODA Authors.
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
import threading

import requests
import six
from oslo_log import log as logging

from delfin import cryptor
from delfin import exception
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_AUTH_URL = '/api/types/loginSessionInfo/instances'
    REST_STORAGE_URL = '/api/types/system/instances'
    REST_CAPACITY_URL = '/api/types/systemCapacity/instances'
    REST_SOFT_VERSION_URL = '/api/types/installedSoftwareVersion/instances'
    REST_LUNS_URL = '/api/types/lun/instances'
    REST_POOLS_URL = '/api/types/pool/instances'
    REST_ALERTS_URL = '/api/types/alert/instances'
    REST_DEL_ALERTS_URL = '/api/instances/alert/'
    REST_LOGOUT_URL = '/api/types/loginSessionInfo/action/logout'
    AUTH_KEY = 'EMC-CSRF-TOKEN'
    STATE_SOLVED = 2

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)
        self.session_lock = threading.Lock()

    def login(self):
        """Login dell_emc unity storage array."""
        try:
            with self.session_lock:
                data = {}
                if self.session is None:
                    self.init_http_head()
                self.session.headers.update({"X-EMC-REST-CLIENT": "true"})
                self.session.auth = requests.auth.HTTPBasicAuth(
                    self.rest_username, cryptor.decode(self.rest_password))
                res = self.call_with_token(
                    RestHandler.REST_AUTH_URL, data, 'GET')
                if res.status_code == 200:
                    self.session.headers[RestHandler.AUTH_KEY] = \
                        cryptor.encode(res.headers[RestHandler.AUTH_KEY])
                else:
                    LOG.error("Login error.URL: %s,Reason: %s.",
                              RestHandler.REST_AUTH_URL, res.text)
                    if 'Unauthorized' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    elif 'Forbidden' in res.text:
                        raise exception.InvalidIpOrPort()
                    else:
                        raise exception.StorageBackendException(
                            six.text_type(res.text))
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def call_with_token(self, url, data, method):
        auth_key = None
        if self.session:
            auth_key = self.session.headers.get(RestHandler.AUTH_KEY, None)
            if auth_key:
                self.session.headers[RestHandler.AUTH_KEY] \
                    = cryptor.decode(auth_key)
        res = self.do_call(url, data, method)
        if auth_key:
            self.session.headers[RestHandler.AUTH_KEY] = auth_key
        return res

    def logout(self):
        try:
            if self.san_address:
                self.call(RestHandler.REST_LOGOUT_URL, method='POST')
            if self.session:
                self.session.close()
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def get_rest_info(self, url, data=None, method='GET'):
        result_json = None
        res = self.call(url, data, method)
        if res.status_code == 200:
            result_json = res.json()
        return result_json

    def call(self, url, data=None, method=None):
        try:
            res = self.call_with_token(url, data, method)
            if res.status_code == 401:
                LOG.error("Failed to get token, status_code:%s,error_mesg:%s" %
                          (res.status_code, res.text))
                self.login()
                res = self.call_with_token(url, data, method)
            elif res.status_code == 503:
                raise exception.InvalidResults(res.text)
            return res
        except Exception as e:
            LOG.error("Method:%s,url:%s failed: %s" % (method, url,
                                                       six.text_type(e)))
            raise e

    def get_all_pools(self):
        url = '%s?%s' % (RestHandler.REST_POOLS_URL,
                         'fields=id,name,health,type,sizeFree,'
                         'sizeTotal,sizeUsed,sizeSubscribed')
        result_json = self.get_rest_info(url)
        return result_json

    def get_storage(self):
        url = '%s?%s' % (RestHandler.REST_STORAGE_URL,
                         'fields=name,model,serialNumber,health')
        result_json = self.get_rest_info(url)
        return result_json

    def get_capacity(self):
        url = '%s?%s' % (RestHandler.REST_CAPACITY_URL,
                         'fields=sizeFree,sizeTotal,sizeUsed,'
                         'sizeSubscribed,totalLogicalSize')
        result_json = self.get_rest_info(url)
        return result_json

    def get_soft_version(self):
        url = '%s?%s' % (RestHandler.REST_SOFT_VERSION_URL,
                         'fields=version')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_luns(self, page_number):
        url = '%s?%s&page=%s' % (RestHandler.REST_LUNS_URL,
                                 'fields=id,name,health,type,sizeAllocated,'
                                 'sizeTotal,sizeUsed,pool,wwn,isThinEnabled',
                                 page_number)
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_alerts(self, page_number):
        url = '%s?%s&page=%s' % (RestHandler.REST_ALERTS_URL,
                                 'fields=id,timestamp,severity,component,'
                                 'messageId,message,description,'
                                 'descriptionId,state',
                                 page_number)
        result_json = self.get_rest_info(url)
        return result_json

    def remove_alert(self, alert_id):
        data = {"state": RestHandler.STATE_SOLVED}
        url = '%s%s/action/modify' % (RestHandler.REST_DEL_ALERTS_URL,
                                      alert_id)
        result_json = self.get_rest_info(url, data, method='POST')
        return result_json
