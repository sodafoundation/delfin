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

from oslo_log import log as logging

from delfin import exception
from delfin.drivers.hpe.hpe_3par import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class RestHandler(object):
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

    def __init__(self, restclient):
        self.restclient = restclient

    def call(self, url, data=None, method=None):
        """Send requests to server.
        If fail, try another RestURL.
        Increase the judgment of token invalidation
        """

        if self.restclient.session is None:
            self.restclient.init_http_head()
            if self.restclient.rest_auth_token is not None:
                # set taken in the header，key is X-HP3PAR-WSAPI-SessionKey
                self.restclient.session.headers[RestHandler.REST_AUTH_KEY] = \
                    self.restclient.rest_auth_token

        res = self.restclient.do_call(url, data, method,
                                      calltimeout=consts.SOCKET_TIMEOUT)
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

                self.restclient.rest_auth_token = None
                access_session = self.login()
                # if get token，Revisit url
                if access_session is not None:
                    res = self.restclient. \
                        do_call(url, data, method,
                                calltimeout=consts.SOCKET_TIMEOUT)
        else:
            LOG.error('login res is None')
        return res

    def get_resinfo_call(self, url, data=None, method=None):
        rejson = None
        # visit url
        res = self.call(url, data, method)
        if res is not None:
            if res.status_code == consts.SUCCESS_STATUS_CODES:
                rejson = res.json()
        return rejson

    def login(self):
        """Login Hpe3par storage array."""
        access_session = self.restclient.rest_auth_token

        if access_session is None:
            if self.restclient.san_address:
                url = RestHandler.REST_AUTH_URL

                data = {"user": self.restclient.rest_username,
                        "password": self.restclient.rest_password
                        }
                self.restclient.init_http_head()
                res = self.restclient. \
                    do_call(url, data, 'POST',
                            calltimeout=consts.SOCKET_TIMEOUT)

                if res is not None:
                    # check login status 201
                    if res.status_code == consts.LOGIN_SUCCESS_STATUS_CODES:
                        result = res.json()

                        access_session = result.get('key')
                        self.restclient.rest_auth_token = access_session
                        # set taken in the header，
                        # key is X-HP3PAR-WSAPI-SessionKey
                        self.restclient.session.headers[
                            RestHandler.REST_AUTH_KEY] = access_session
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
            url = RestHandler.REST_LOGOUT_URL
            if self.restclient.rest_auth_token is not None:
                url = url + self.restclient.rest_auth_token
            self.restclient.rest_auth_token = None
            if self.restclient.san_address:
                self.call(url, method='DELETE')
        except Exception as err:
            LOG.error('logout error:{}'.format(err))
            raise exception.StorageBackendException(
                reason='Failed to Logout from restful')

    def get_storage(self):
        rejson = self.get_resinfo_call(RestHandler.REST_STORAGE_URL,
                                       method='GET')
        return rejson

    def get_capacity(self):
        rejson = self.get_resinfo_call(RestHandler.REST_CAPACITY_URL,
                                       method='GET')
        return rejson

    def get_all_pools(self):
        rejson = self.get_resinfo_call(RestHandler.REST_POOLS_URL,
                                       method='GET')
        return rejson

    def get_all_volumes(self):
        rejson = self.get_resinfo_call(RestHandler.REST_VOLUMES_URL,
                                       method='GET')
        return rejson
