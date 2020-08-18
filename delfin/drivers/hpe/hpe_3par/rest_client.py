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

import json

import requests

from oslo_log import log as logging

from delfin import exception
from delfin.drivers.hpe.hpe_3par import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class RestClient(object):
    """Common class for Hpe 3parStor storage system."""
    # https://<storage_system>:8080/api/v1/credentials
    REST_AUTH_URL = '/api/v1/credentials'  # POST
    REST_LOGOUT_URL = '/api/v1/credentials/'  # DELETE <session key>
    REST_STORAGE_URL = '/api/v1/system'  # GET
    # GET  /api/v1/spacereporter  body cpg:cpgname
    REST_CAPACITY_URL = '/api/v1/capacity'
    REST_POOLS_URL = '/api/v1/cpgs'  # GET
    REST_VOLUMES_URL = '/api/v1/volumes'  # GET
    # category==LIFECYCLE 1  ALERT 2
    # GET    /api/v1/eventlog
    REST_ALERTS_URL = '/api/v1/eventlog?query="category EQ 2"'
    # X-HP3PAR-WSAPI-SessionKey
    REST_AUTH_KEY = 'X-HP3PAR-WSAPI-SessionKey'

    def __init__(self, **kwargs):

        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        self.rest_host = rest_access.get('host')
        self.rest_port = rest_access.get('port')
        self.rest_username = rest_access.get('username')
        self.rest_password = rest_access.get('password')
        # Lists of addresses to try, for authorization
        self.san_address = 'https://' + self.rest_host + ':' + \
                           str(self.rest_port)
        self.session = None
        self.device_id = None
        # test
        self.enable_verify = False
        self.ca_path = 'certificate verification file path'
        self.REST_AUTH_TOKEN = None

    def init_http_head(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Connection": "keep-alive",
            'Accept': 'application/json',
            "Content-Type": "application/json"})
        self.session.verify = False
        if not self.enable_verify:
            self.session.verify = False
        else:
            LOG.debug("Enable certificate verification, ca_path: {0}".format(
                self.ca_path))
            self.session.verify = self.ca_path
        self.session.trust_env = False

    def do_call(self, url, data, method,
                calltimeout=consts.SOCKET_TIMEOUT):
        """Send requests to Hpe3par storage server.
        """
        if 'http' not in url:
            if self.san_address:
                url = self.san_address + url

        kwargs = {'timeout': calltimeout}
        if data:
            kwargs['data'] = json.dumps(data)

        if method in ('POST', 'PUT', 'GET', 'DELETE'):
            func = getattr(self.session, method.lower())
        else:
            msg = _("Request method %s is invalid.") % method
            LOG.error(msg)
            raise exception.StorageBackendException(reason=msg)
        res = None
        try:
            res = func(url, **kwargs)
        except requests.exceptions.ConnectTimeout as ct:
            LOG.error('ConnectTimeout err: {}'.format(ct))
            raise exception.ConnectTimeout()
        except Exception as err:
            LOG.exception('Bad response from server: %(url)s.'
                          ' Error: %(err)s', {'url': url, 'err': err})
            if 'WSAETIMEDOUT' in str(err):
                raise exception.ConnectTimeout()
            else:
                raise exception.BadResponse()

        return res

    def call(self, url, data=None, method=None):
        """Send requests to server.
        If fail, try another RestURL.
        Increase the judgment of token invalidation
        """

        if self.session is None:
            self.init_http_head()
            if self.REST_AUTH_TOKEN is not None:
                # set taken in the header，key is X-HP3PAR-WSAPI-SessionKey
                self.session.headers[
                    RestClient.REST_AUTH_KEY] = self.REST_AUTH_TOKEN

        res = self.do_call(url, data, method)

        # Judge whether the access failure is caused by
        # the token invalidation.
        # If the token fails, it will be retrieved again,
        # and the token will be accessed again
        if res is not None:
            # 403  The client request has an invalid session key.
            #      The request came from a different IP address
            # 409  Session key is being used.
            if (res.status_code == consts.ERROR_SESSION_INVALID_CODE
                    or res.status_code ==
                    consts.ERROR_SESSION_IS_BEING_USED_CODE):
                LOG.error(
                    "Failed to get token=={0}=={1}".format(res.status_code,
                                                           res.text))
                LOG.error("Failed to get token，relogin，Get token again！！！")
                # delete REST_AUTH_TOKEN，Recapture token
                try:
                    self.logout()
                except Exception as err:
                    LOG.error('logout error:{}'.format(err))

                self.REST_AUTH_TOKEN = None
                access_session = self.login()
                # if get token，Revisit url
                if access_session is not None:
                    res = self.do_call(url, data, method)
        else:
            LOG.error('login res is None')
        return res

    def get_resinfo_call(self, url, data=None, method=None, resName=None):
        rejson = None

        # visit url
        res = self.call(url, data, method)
        if res is not None:
            if res.status_code == consts.SUCCESS_STATUS_CODES:
                rejson = res.json()
        return rejson

    def login(self):
        """Login Hpe3par storage array."""
        access_session = self.REST_AUTH_TOKEN

        if access_session is None:
            if self.san_address:
                url = RestClient.REST_AUTH_URL

                data = {"user": self.rest_username,
                        "password": self.rest_password
                        }
                self.init_http_head()
                res = self.do_call(url, data, 'POST',
                                   calltimeout=consts.SOCKET_TIMEOUT)

                if res is not None:
                    # check login status 201
                    if res.status_code == consts.LOGIN_SUCCESS_STATUS_CODES:
                        result = res.json()

                        access_session = result.get('key')
                        self.REST_AUTH_TOKEN = access_session
                        # set taken in the header，
                        # key is X-HP3PAR-WSAPI-SessionKey
                        self.session.headers[
                            RestClient.REST_AUTH_KEY] = access_session
                    else:
                        LOG.error("Login error. URL: %(url)s\n"
                                  "Reason: %(reason)s.",
                                  {"url": url, "reason": res.text})
                        if 'invalid username or password' in res.text:
                            raise exception.InvalidUsernameOrPassword()
                        else:
                            raise exception.Invalid()
                else:
                    LOG.error('login res is None')
                    raise exception.InvalidResults('res is None')
            else:
                LOG.error('login Parameter error')
        else:
            LOG.error(
                "No login required！self.access_session have value=={}".format(
                    access_session))

        if access_session is None:
            msg = _("Failed to login with all rest URLs.")
            LOG.error(msg)
            raise exception.BadRequest(reason=msg)
        return access_session

    def logout(self):
        """Logout the session."""
        try:
            url = RestClient.REST_LOGOUT_URL
            if self.REST_AUTH_TOKEN is not None:
                url = url + self.REST_AUTH_TOKEN
            self.REST_AUTH_TOKEN = None
            if self.san_address:
                self.call(url, method='DELETE')
        except Exception as err:
            LOG.error('logout error:{}'.format(err))
            raise exception.StorageBackendException(
                reason='Failed to Logout from restful')

    def get_storage(self):
        rejson = self.get_resinfo_call(RestClient.REST_STORAGE_URL,
                                       method='GET', resName='storage')
        return rejson

    def get_capacity(self):
        rejson = self.get_resinfo_call(RestClient.REST_CAPACITY_URL,
                                       method='GET', resName='capacity')
        return rejson

    def get_all_pools(self):
        rejson = self.get_resinfo_call(RestClient.REST_POOLS_URL, method='GET',
                                       resName='pool')
        return rejson

    def get_all_volumes(self):
        rejson = self.get_resinfo_call(RestClient.REST_VOLUMES_URL,
                                       method='GET',
                                       resName='volume paginated')
        return rejson

    def get_all_alerts(self):
        rejson = self.get_resinfo_call(RestClient.REST_ALERTS_URL,
                                       method='GET', resName='pool')
        return rejson
