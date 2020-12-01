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
import threading

import requests
import six
from oslo_log import log as logging

from delfin import cryptor
from delfin import exception
from delfin.drivers.hitachi.vsp import consts
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    COMM_URL = '/ConfigurationManager/v1/objects/storages'
    LOGOUT_URL = '/ConfigurationManager/v1/objects/sessions/'

    AUTH_KEY = 'Authorization'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)
        self.session_lock = threading.Lock()
        self.session_id = None
        self.storage_device_id = None
        self.device_model = None
        self.serial_number = None

    def call(self, url, data=None, method=None,
             calltimeout=consts.SOCKET_TIMEOUT):
        try:
            res = self.do_call(url, data, method, calltimeout)
            if (res.status_code == consts.ERROR_SESSION_INVALID_CODE
                    or res.status_code ==
                    consts.ERROR_SESSION_IS_BEING_USED_CODE):
                LOG.error("Failed to get token=={0}=={1},get token again"
                          .format(res.status_code, res.text))
                # if method is logout,return immediately
                if method == 'DELETE' and RestHandler. \
                        LOGOUT_URL in url:
                    return res
                self.rest_auth_token = None
                access_session = self.login()
                if access_session is not None:
                    res = self. \
                        do_call(url, data, method, calltimeout)
                else:
                    LOG.error('Login error,get access_session failed')
            elif res.status_code == 503:
                raise exception.InvalidResults(res.text)

            return res

        except Exception as e:
            err_msg = "Get RestHandler.call failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def get_rest_info(self, url, timeout=consts.SOCKET_TIMEOUT, data=None):
        result_json = None
        res = self.call(url, data, 'GET', timeout)
        if res.status_code == 200:
            result_json = res.json()
        return result_json

    def login(self):
        try:
            self.get_device_id()
            access_session = self.rest_auth_token
            if self.san_address:
                url = '%s/%s/sessions' % \
                      (RestHandler.COMM_URL,
                       self.storage_device_id)
                data = {}

                with self.session_lock:
                    if self.session is None:
                        self.init_http_head()
                    self.session.auth = \
                        requests.auth.HTTPBasicAuth(
                            self.rest_username,
                            cryptor.decode(self.rest_password))
                    res = self. \
                        do_call(url, data, 'POST', 10)
                    if res.status_code == 200:
                        result = res.json()
                        self.session_id = result.get('sessionId')
                        access_session = 'Session %s' % result.get('token')
                        self.rest_auth_token = access_session
                        self.session.headers[
                            RestHandler.AUTH_KEY] = access_session
                    else:
                        LOG.error("Login error. URL: %(url)s\n"
                                  "Reason: %(reason)s.",
                                  {"url": url, "reason": res.text})
                        if 'authentication failed' in res.text:
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
            url = RestHandler.LOGOUT_URL
            if self.session_id is not None:
                url = '%s/%s/sessions/%s' % \
                      (RestHandler.COMM_URL,
                       self.storage_device_id,
                       self.session_id)
                if self.san_address:
                    self.call(url, method='DELETE')
                    self.session_id = None
                    self.storage_device_id = None
                    self.device_model = None
                    self.serial_number = None
                    self.session = None
                    self.rest_auth_token = None
            else:
                LOG.error('logout error:session id not found')
        except Exception as err:
            LOG.error('logout error:{}'.format(err))
            raise exception.StorageBackendException(
                reason='Failed to Logout from restful')

    def get_device_id(self):
        try:
            if self.session is None:
                self.init_http_head()
            storage_systems = self.get_system_info()
            system_info = storage_systems.get('data')
            for system in system_info:
                if system.get('model') in consts.SUPPORTED_VSP_SERIES:
                    if system.get('ctl1Ip') == self.rest_host or \
                            system.get('ctl2Ip') == self.rest_host:
                        self.storage_device_id = system.get('storageDeviceId')
                        self.device_model = system.get('model')
                        self.serial_number = system.get('serialNumber')
                        break
                elif system.get('svpIp') == self.rest_host:
                    self.storage_device_id = system.get('storageDeviceId')
                    self.device_model = system.get('model')
                    self.serial_number = system.get('serialNumber')
                    break
            if self.storage_device_id is None:
                LOG.error("Get device id fail,model or something is wrong")
        except Exception as e:
            LOG.error("Get device id error: %s", six.text_type(e))
            raise e

    def get_firmware_version(self):
        url = '%s/%s' % \
              (RestHandler.COMM_URL, self.storage_device_id)
        result_json = self.get_rest_info(url)
        if result_json is None:
            return None
        firmware_version = result_json.get('dkcMicroVersion')

        return firmware_version

    def get_capacity(self):
        url = '%s/%s/total-capacities/instance' % \
              (RestHandler.COMM_URL, self.storage_device_id)
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_pools(self):
        url = '%s/%s/pools' % \
              (RestHandler.COMM_URL, self.storage_device_id)
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_volumes(self):
        url = '%s/%s/ldevs?ldevOption=defined&count=%s' % \
              (RestHandler.COMM_URL, self.storage_device_id,
               consts.MAX_LDEV_NUMBER_OF_RESTAPI)
        result_json = self.get_rest_info(url)
        return result_json

    def get_system_info(self):
        result_json = self.get_rest_info(RestHandler.COMM_URL, timeout=10)

        return result_json
