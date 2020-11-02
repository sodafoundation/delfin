# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
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

from delfin import cryptor, ssl_utils
from delfin import exception
from delfin.drivers.dell_emc.unity import consts

LOG = logging.getLogger(__name__)


class RestHandler(object):
    REST_AUTH_URL = '/api/types/loginSessionInfo/instances'
    REST_LOGOUT_URL = '/api/types/loginSessionInfo/action/logout'
    REST_STORAGE_URL = '/api/types/system/instances'
    REST_CAPACITY_URL = '/api/types/systemCapacity/instances'
    REST_POOLS_URL = '/api/types/pool/instances'
    REST_LUNS_URL = '/api/types/lun/instances'
    REST_FILESYSTEM_URL = '/api/types/filesystem/instances'
    REST_ALERTS_URL = '/api/types/alert/instances'
    REST_DEL_ALERTS_URL = '/api/instances/alert/'
    REST_AUTH_KEY = 'EMC-CSRF-TOKEN'

    def __init__(self, rest_client):
        self.rest_client = rest_client

    def call(self, url, data=None, method=None, params=None):
        try:
            res = self.rest_client.do_call(url, data, method,
                                           calltimeout=consts.SOCKET_TIMEOUT,
                                           params=params)
            if res is not None:
                if (res.status_code == consts.ERROR_SESSION_INVALID_CODE
                        or res.status_code ==
                        consts.ERROR_SESSION_IS_BEING_USED_CODE):
                    LOG.error(
                        "Failed to get token=={0}=={1},get it again".format(
                            res.status_code, res.text))
                    if method == 'DELETE' and RestHandler.\
                            REST_LOGOUT_URL in url:
                        return res
                    self.rest_client.rest_auth_token = None
                    access_session = self.login()
                    # if get token，Revisit url
                    if access_session is not None:
                        res = self.rest_client. \
                            do_call(url, data, method,
                                    calltimeout=consts.SOCKET_TIMEOUT,
                                    params=params)
                    else:
                        LOG.error('Login res is None')
                elif res.status_code == 503:
                    raise exception.InvalidResults(res.text)
            else:
                LOG.error('Rest exec failed')

            return res

        except Exception as e:
            err_msg = "Get RestHandler.call failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_resinfo_call(self, url, data=None, method=None, params=None):
        rejson = None
        res = self.call(url, data, method, params)
        if res is not None:
            if res.status_code == consts.SUCCESS_STATUS_CODES:
                rejson = res.json()
        return rejson

    def init_rest_client(self):
        if self.rest_client.session:
            self.rest_client.session.close()
        self.rest_client.session = requests.Session()
        self.rest_client.session.headers.update({
            'Accept': 'application/json',
            "Content-Type": "application/json",
            "X-EMC-REST-CLIENT": "true"})
        self.rest_client.session.auth = requests.auth.HTTPBasicAuth(
            self.rest_client.rest_username,
            cryptor.decode(self.rest_client.rest_password))
        if not self.rest_client.verify:
            self.rest_client.session.verify = False
        else:
            LOG.debug("Enable certificate verification, ca_path: {0}".format(
                self.rest_client.verify))
            self.rest_client.session.verify = self.rest_client.verify
        self.rest_client.session.trust_env = False
        self.rest_client.session.mount("https://",
                                       ssl_utils.HostNameIgnoreAdapter())

    def login(self):
        try:
            access_session = self.rest_client.rest_auth_token
            if self.rest_client.rest_auth_token is None:
                url = RestHandler.REST_AUTH_URL
                data = {}
                self.init_rest_client()
                res = self.rest_client. \
                    do_call(url, data, 'GET',
                            calltimeout=consts.SOCKET_TIMEOUT)

                if res is None:
                    LOG.error('Login res is None')
                    raise exception.InvalidResults('res is None')

                if res.status_code == 200:
                    access_session = res.headers['EMC-CSRF-TOKEN']
                    self.rest_client.rest_auth_token = access_session
                    self.rest_client.session.headers[
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
            if self.rest_client.rest_auth_token is not None:
                url = '%s%s' % (url, self.rest_client.rest_auth_token)
            self.rest_client.rest_auth_token = None
            if self.rest_client.san_address:
                self.call(url, method='POST')
            if self.rest_client.session:
                self.rest_client.session.close()
        except exception.DelfinException as e:
            err_msg = "Logout error: %s" % (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_storage(self):
        params = {
            "fields": "name,model,serialNumber,health"
        }
        rejson = self.get_resinfo_call(RestHandler.REST_STORAGE_URL,
                                       method='GET', params=params)
        return rejson

    def get_capacity(self):
        params = {
            "fields": "sizeFree,sizeTotal,sizeUsed,"
                      "sizeSubscribed,totalLogicalSize"
        }
        rejson = self.get_resinfo_call(RestHandler.REST_CAPACITY_URL,
                                       method='GET', params=params)
        return rejson

    def get_all_pools(self):
        params = {
            "fields": "id,name,health,type,sizeFree,"
                      "sizeTotal,sizeUsed,sizeSubscribed"
        }
        rejson = self.get_resinfo_call(RestHandler.REST_POOLS_URL,
                                       method='GET', params=params)
        return rejson

    def get_all_luns(self):
        params = {
            "fields": "id,name,health,type,sizeAllocated,"
                      "sizeTotal,sizeUsed,pool,wwn,isThinEnabled"
        }
        rejson = self.get_resinfo_call(RestHandler.REST_LUNS_URL,
                                       method='GET', params=params)
        return rejson

    def get_all_filesystem(self):
        params = {
            "fields": "id,name,health,type,sizeAllocated,"
                      "sizeTotal,sizeUsed,pool,wwn,isThinEnabled"
        }
        rejson = self.get_resinfo_call(RestHandler.REST_FILESYSTEM_URL,
                                       method='GET', params=params)
        return rejson

    def get_all_alerts(self):
        params = {
            "fields": "id,timestamp,severity,component,"
                      "messageId,message,description,descriptionId"
        }
        rejson = self.get_resinfo_call(RestHandler.REST_ALERTS_URL,
                                       method='GET', params=params)
        return rejson

    def remove_alert(self, alert_id):
        url = RestHandler.REST_DEL_ALERTS_URL % alert_id
        rejson = self.get_resinfo_call(url, method='DELETE')
        return rejson
