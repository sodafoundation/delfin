# Copyright 2020 The SODA Authors.
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

import requests
import six
from oslo_log import log as logging

from delfin import cryptor
from delfin import exception
from delfin import ssl_utils
from delfin.drivers.dell_emc.unity import consts
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_AUTH_URL = '/api/types/loginSessionInfo/instances'
    REST_LOGOUT_URL = '/api/types/loginSessionInfo/action/logout'
    REST_STORAGE_URL = '/api/types/system/instances'
    REST_CAPACITY_URL = '/api/types/systemCapacity/instances'
    REST_POOLS_URL = '/api/types/pool/instances'
    REST_LUNS_URL = '/api/types/lun/instances'
    REST_ALERTS_URL = '/api/types/alert/instances'
    REST_DEL_ALERTS_URL = '/api/instances/alert/'
    REST_DISK_URL = '/api/types/disk/instances'
    REST_SOFT_VERSION_URL = '/api/types/installedSoftwareVersion/instances'
    REST_AUTH_KEY = 'EMC-CSRF-TOKEN'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)

    def call(self, url, data=None, method=None):
        try:
            res = self.do_call(url, data, method,
                               calltimeout=consts.SOCKET_TIMEOUT)
            if (res.status_code == consts.ERROR_SESSION_INVALID_CODE
                    or res.status_code ==
                    consts.ERROR_SESSION_IS_BEING_USED_CODE):
                LOG.error(
                    "Failed to get token=={0}=={1},get it again".format(
                        res.status_code, res.text))
                if RestHandler.REST_LOGOUT_URL in url:
                    return res
                self.rest_auth_token = None
                access_session = self.login()
                # if get token，Revisit url
                if access_session is not None:
                    res = self. \
                        do_call(url, data, method,
                                calltimeout=consts.SOCKET_TIMEOUT)
                else:
                    LOG.error('Login session is none')
            elif res.status_code == 503:
                raise exception.InvalidResults(res.text)
            return res
        except Exception as e:
            err_msg = "Get restHandler.call failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def get_rest_info(self, url, data=None, method='GET'):
        result_json = None
        res = self.call(url, data, method)
        if res.status_code == 200:
            result_json = res.json()
        return result_json

    def init_rest_client(self):
        if self.session:
            self.session.close()
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            "Content-Type": "application/json",
            "X-EMC-REST-CLIENT": "true"})
        self.session.auth = requests.auth.HTTPBasicAuth(
            self.rest_username,
            cryptor.decode(self.rest_password))
        if not self.verify:
            self.session.verify = False
        else:
            LOG.debug("Enable certificate verification, ca_path: {0}".format(
                self.verify))
            self.session.verify = self.verify
        self.session.trust_env = False
        self.session.mount("https://", ssl_utils.HostNameIgnoreAdapter())

    def login(self):
        try:
            access_session = self.rest_auth_token
            if self.rest_auth_token is None:
                url = RestHandler.REST_AUTH_URL
                data = {}
                self.init_rest_client()
                res = self. \
                    do_call(url, data, 'GET',
                            calltimeout=consts.SOCKET_TIMEOUT)
                if res.status_code == 200:
                    access_session = res.headers['EMC-CSRF-TOKEN']
                    self.rest_auth_token = access_session
                    self.session.headers[
                        RestHandler.REST_AUTH_KEY] = access_session
                else:
                    LOG.error("Login error. URL: %(url)s\n"
                              "Reason: %(reason)s.",
                              {"url": url, "reason": res.text})
                    if 'invalid username or password' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    else:
                        raise exception.BadResponse(res.text)
            else:
                LOG.error('Login Parameter error')
            return access_session
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def logout(self):
        try:
            url = RestHandler.REST_LOGOUT_URL
            if self.rest_auth_token is not None:
                url = '%s/%s' % (url, self.rest_auth_token)
            self.rest_auth_token = None
            if self.san_address:
                self.call(url, method='POST')
            if self.session:
                self.session.close()
        except exception.DelfinException as e:
            err_msg = "Logout error: %s" % (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

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

    def get_all_pools(self):
        url = '%s?%s' % (RestHandler.REST_POOLS_URL,
                         'fields=id,name,health,type,sizeFree,'
                         'sizeTotal,sizeUsed,sizeSubscribed')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_luns(self, page_size):
        url = '%s?%s&page=%s' % (RestHandler.REST_LUNS_URL,
                                 'fields=id,name,health,type,sizeAllocated,'
                                 'sizeTotal,sizeUsed,pool,wwn,isThinEnabled',
                                 page_size)
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_alerts(self, page_size):
        url = '%s?%s&page=%s' % (RestHandler.REST_ALERTS_URL,
                                 'fields=id,timestamp,severity,component,'
                                 'messageId,message,description,descriptionId',
                                 page_size)
        result_json = self.get_rest_info(url)
        return result_json

    def get_soft_version(self):
        url = '%s?%s' % (RestHandler.REST_SOFT_VERSION_URL,
                         'fields=version')
        result_json = self.get_rest_info(url)
        return result_json

    def get_disk_info(self):
        url = '%s?%s' % (RestHandler.REST_DISK_URL,
                         'fields=rawSize')
        result_json = self.get_rest_info(url)
        return result_json

    def remove_alert(self, alert_id):
        url = RestHandler.REST_DEL_ALERTS_URL % alert_id
        result_json = self.get_rest_info(url, method='DELETE')
        return result_json
