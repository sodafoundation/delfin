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
import threading

import requests
import six
from oslo_log import log as logging

# from delfin import exception, cryptor
from delfin import exception
from delfin.drivers.hds.vsp import consts

LOG = logging.getLogger(__name__)


class RestHandler(object):
    hdsvsp_auth_token = None
    hdsvsp_session_id = None
    storage_device_id = None
    device_model = None
    serialNumber = None
    hdsvsp_system_url = '/ConfigurationManager/v1/objects/storages'
    hdsvsp_ports_url = '/ConfigurationManager/v1/objects/ports'
    hdsvsp_logout_url = '/ConfigurationManager/v1/objects/sessions/'
    hdsvsp_comm_url = '/ConfigurationManager/v1/objects/storages/'
    hdsvsp_simple_url = '/ConfigurationManager/simple/v1/objects/storage'

    hdsvsp_auth_key = 'Authorization'

    def __init__(self, restclient):
        self.rest_client = restclient
        self.session_lock = threading.Lock()

    def call(self, url, data=None, method=None):
        try:
            res = self.rest_client.do_call(url, data, method,
                                           calltimeout=consts.SOCKET_TIMEOUT)
            if res is not None:
                # 403  The client request has an invalid session key.
                #      The request came from a different IP address
                # 409  Session key is being used.
                if (res.status_code == consts.ERROR_SESSION_INVALID_CODE
                        or res.status_code ==
                        consts.ERROR_SESSION_IS_BEING_USED_CODE):
                    LOG.error("Failed to get token=={0}=={1},get token again"
                              .format(res.status_code, res.text))
                    # if method is logout,return immediately
                    if method == 'DELETE' and RestHandler.\
                            REST_LOGOUT_URL in url:
                        return res
                    self.rest_client.rest_auth_token = None
                    access_session = self.login()
                    if access_session is not None:
                        res = self.rest_client. \
                            do_call(url, data, method,
                                    calltimeout=consts.SOCKET_TIMEOUT)
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

    def get_resinfo_call(self, url, data=None, method=None, resName=None):
        rejson = None
        res = self.call(url, data, method)
        if res is not None:
            if res.status_code == consts.SUCCESS_STATUS_CODES:
                rejson = res.json()
        return rejson

    def login(self):
        try:
            access_session = self.rest_client.rest_auth_token
            if self.rest_client.san_address:
                url = '%s%s/sessions' % \
                      (RestHandler.hdsvsp_comm_url,
                       RestHandler.storage_device_id)
                data = {}

                with self.session_lock:
                    if self.rest_client.rest_auth_token is not None:
                        return self.rest_client.rest_auth_token
                    if self.rest_client.session is None:
                        self.rest_client.init_http_head()
                    self.rest_client.session.auth = requests.auth.\
                        HTTPBasicAuth(self.rest_client.rest_username,
                                      self.rest_client.rest_password)
                    res = self.rest_client. \
                        do_call(url, data, 'POST',
                                calltimeout=consts.SOCKET_TIMEOUT)

                    if res is None:
                        LOG.error('Login res is None')
                        raise exception.InvalidResults('res is None')

                    if res.status_code == consts.SUCCESS_STATUS_CODES:
                        result = res.json()
                        RestHandler.hdsvsp_session_id = result.get('sessionId')
                        access_session = 'Session %s' % result.get('token')
                        self.rest_client.rest_auth_token = access_session
                        self.rest_client.session.headers[
                            RestHandler.hdsvsp_auth_key] = access_session
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
            self.restclient.hdsvsp_auth_token = None
            url = RestHandler.hdsvsp_logout_url
            if RestHandler.hdsvsp_session_id is not None:
                url = '%s%s/sessions/%s' % \
                      (RestHandler.hdsvsp_comm_url,
                       RestHandler.storage_device_id,
                       RestHandler.hdsvsp_session_id)
            if self.restclient.san_address:
                self.call(url, method='DELETE')
        except Exception as err:
            LOG.error('logout error:{}'.format(err))
            raise exception.StorageBackendException(
                reason='Failed to Logout from restful')

    def get_device_id(self):
        try:
            if self.rest_client.session is None:
                self.rest_client.init_http_head()
            storage_systems = self.get_system_info()
            if storage_systems is None:
                return
            system_info = storage_systems.get('data')
            for system in system_info:
                if system.get('model') in consts.VSP_MODEL_NOT_USE_SVPIP:
                    if system.get('ctl1Ip') == self.rest_client.rest_host or \
                            system.get('ctl2Ip') == self.rest_client.rest_host:
                        RestHandler.storage_device_id = system.get(
                            'storageDeviceId')
                        RestHandler.device_model = system.get('model')
                        RestHandler.serialNumber = system.get('serialNumber')
                        break
                elif system.get('svpIp') == self.rest_client.rest_host:
                    RestHandler.storage_device_id = system.get(
                        'storageDeviceId')
                    RestHandler.device_model = system.get('model')
                    RestHandler.serialNumber = system.get('serialNumber')
                    break
            if RestHandler.storage_device_id is None:
                LOG.error("Get device id fail,model or something is wrong")
        except Exception as e:
            LOG.error("Get device id error: %s", six.text_type(e))
            raise e

    def get_storage(self):
        pass

    def get_specific_storage(self):
        rejson = self.get_resinfo_call(RestHandler.hdsvsp_specific_storage_url,
                                       method='GET',
                                       resName='Specific_Storage')
        return rejson

    def get_summary_storage(self):
        rejson = self.get_resinfo_call(RestHandler.hdsvsp_summer_storage_url,
                                       method='GET',
                                       resName='Summer_Storage')
        return rejson

    def get_capacity(self):
        url = '%s%s/total-capacities/instance' % \
              (RestHandler.hdsvsp_comm_url, RestHandler.storage_device_id)
        rejson = self.get_resinfo_call(url,
                                       method='GET',
                                       resName='capacity')
        return rejson

    def get_all_pools(self):
        url = '%s%s/pools' % \
              (RestHandler.hdsvsp_comm_url, RestHandler.storage_device_id)
        rejson = self.get_resinfo_call(url,
                                       method='GET',
                                       resName='pool')
        return rejson

    def get_all_volumes(self):
        url = '%s%s/ldevs' % \
              (RestHandler.hdsvsp_comm_url, RestHandler.storage_device_id)
        rejson = self.get_resinfo_call(url,
                                       method='GET',
                                       resName='volume paginated')
        return rejson

    def get_ports(self):
        rejson = self.get_resinfo_call(RestHandler.hdsvsp_ports_url,
                                       method='GET', resName='ports paginated')
        return rejson

    def get_alerts(self, param):
        url = '%s%s/alerts?%s' % (RestHandler.hdsvsp_comm_url,
                                  RestHandler.storage_device_id,
                                  param)
        rejson = self.get_resinfo_call(url,
                                       method='GET', resName='ports paginated')
        return rejson

    def get_system_info(self):
        rejson = self.get_resinfo_call(RestHandler.hdsvsp_system_url,
                                       method='GET', resName='ports paginated')

        return rejson

    def get_summaries_system(self):
        system_name = None
        url = '%s/%s/storage-summaries/instance' % \
              (RestHandler.hdsvsp_comm_url, RestHandler.storage_device_id)
        rejson = self.get_resinfo_call(url,
                                       method='GET', resName='ports paginated')
        if rejson is not None:
            system_name = rejson.get('name')

        return system_name

    def get_simple_system(self):
        system_name = None
        url = '%ss/%s/storage' % \
              (RestHandler.hdsvsp_simple_url, RestHandler.storage_device_id)
        rejson = self.get_resinfo_call(url,
                                       method='GET', resName='ports paginated')
        if rejson is not None:
            system_name = rejson.get('nickname')
        return system_name

    def get_system_by_snmp(self):
        system_name = None
        url = '%s%s/snmp-settings/instance' % \
              (RestHandler.hdsvsp_comm_url, RestHandler.storage_device_id)
        rejson = self.get_resinfo_call(url,
                                       method='GET', resName='ports paginated')
        if rejson is not None:
            system_name = rejson.get(
                'systemGroupInformation').get('storageSystemName')
        return system_name
