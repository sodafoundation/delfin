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

import six
from oslo_log import log as logging

from delfin import cryptor
from delfin import exception
from delfin.drivers.hpe.hpe_3par import consts
from delfin.drivers.utils.tools import Tools

LOG = logging.getLogger(__name__)


class RestHandler(object):
    """Common class for Hpe 3parStor storage system."""

    REST_AUTH_URL = '/api/v1/credentials'
    REST_LOGOUT_URL = '/api/v1/credentials/'
    REST_STORAGE_URL = '/api/v1/system'

    REST_CAPACITY_URL = '/api/v1/capacity'
    REST_POOLS_URL = '/api/v1/cpgs'
    REST_VOLUMES_URL = '/api/v1/volumes'

    REST_ALERTS_URL = '/api/v1/eventlog?query="category EQ 2"'

    REST_HOSTS_URL = '/api/v1/hosts'

    REST_AUTH_KEY = 'X-HP3PAR-WSAPI-SessionKey'

    REST_CPGSTATISTICS_URL = '/api/v1/systemreporter' \
                             '/attime/cpgstatistics/hires?' \
                             'query="sampleTime GE %s AND sampleTime LE %s"'

    session_lock = None

    def __init__(self, rest_client):
        self.rest_client = rest_client
        self.session_lock = threading.Lock()

    def call(self, url, data=None, method=None):
        """Send requests to server.
        If fail, try another RestURL.
        Increase the judgment of token invalidation
        """
        try:
            res = self.call_with_token(url, data, method,
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
                    LOG.error("Failed to get token,relogin,Get token again")
                    # if method is logout,return immediately
                    if method == 'DELETE' and RestHandler.\
                            REST_LOGOUT_URL in url:
                        return res
                    self.rest_client.rest_auth_token = None
                    access_session = self.login()
                    # if get token，Revisit url
                    if access_session is not None:
                        res = self.call_with_token(
                            url, data, method,
                            calltimeout=consts.SOCKET_TIMEOUT)
                    else:
                        LOG.error('Login res is None')
                elif res.status_code == 503:
                    raise exception.InvalidResults(res.text)
            else:
                LOG.error('Rest exec failed')

            return res
        except exception.DelfinException as e:
            err_msg = "Call failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e
        except Exception as e:
            err_msg = "Get RestHandler.call failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def get_resinfo_call(self, url, data=None, method=None):
        rejson = None
        res = self.call(url, data, method)
        if res is not None:
            if res.status_code == consts.SUCCESS_STATUS_CODES:
                rejson = res.json()
            else:
                if res.text and 'unsupported' in res.text:
                    LOG.warning('rest api error: {}'.format(res.text))
                else:
                    raise exception.StorageBackendException(res.text)
        return rejson

    def login(self):
        """Login Hpe3par storage array."""
        try:
            access_session = self.rest_client.rest_auth_token
            if self.rest_client.san_address:
                url = RestHandler.REST_AUTH_URL

                data = {"user": self.rest_client.rest_username,
                        "password": cryptor.decode(
                            self.rest_client.rest_password)
                        }

                self.session_lock.acquire()

                if self.rest_client.rest_auth_token is not None:
                    return self.rest_client.rest_auth_token
                self.rest_client.init_http_head()
                res = self.rest_client. \
                    do_call(url, data, 'POST',
                            calltimeout=consts.SOCKET_TIMEOUT)

                if res is None:
                    LOG.error('Login res is None')
                    raise exception.InvalidResults('res is None')

                if res.status_code == consts. \
                        LOGIN_SUCCESS_STATUS_CODES:
                    result = res.json()

                    access_session = result.get('key')
                    self.rest_client.rest_auth_token = cryptor.encode(
                        access_session)
                    self.rest_client.session.headers[
                        RestHandler.REST_AUTH_KEY] = cryptor.encode(
                        access_session)
                else:
                    LOG.error("Login error. URL: %(url)s\n"
                              "Reason: %(reason)s.",
                              {"url": url, "reason": res.text})
                    if 'invalid username or password' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    elif 'maximum number of server connections' in res.text:
                        raise exception.StorageMaxUserCountException(res.text)
                    else:
                        raise exception.StorageBackendException(
                            six.text_type(res.text))
            else:
                LOG.error('Login Parameter error')

            return access_session
        except exception.DelfinException as e:
            err_msg = "Login error: %s" % (e.msg)
            LOG.error(err_msg)
            raise e
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise exception.StorageBackendException(six.text_type(e))
        finally:
            self.session_lock.release()

    def logout(self):
        """Logout the session."""
        try:
            url = RestHandler.REST_LOGOUT_URL
            if self.rest_client.rest_auth_token is not None:
                url = '%s%s' % (
                    url, cryptor.decode(self.rest_client.rest_auth_token))
            self.rest_client.rest_auth_token = None
            if self.rest_client.san_address:
                self.call(url, method='DELETE')
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

    def call_with_token(self, url, data=None, method='GET',
                        calltimeout=consts.SOCKET_TIMEOUT):
        with self.session_lock:
            auth_key = None
            if self.rest_client.session:
                auth_key = self.rest_client.session.headers.get(
                    RestHandler.REST_AUTH_KEY, None)
                if auth_key:
                    self.rest_client.session.headers[
                        RestHandler.REST_AUTH_KEY] = cryptor.decode(auth_key)
            res = self.rest_client.do_call(url, data, method, calltimeout)
            if auth_key:
                self.rest_client.session.headers[
                    RestHandler.REST_AUTH_KEY] = auth_key
        return res

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

    def get_pool_metrics(self, start_time, end_time):
        start_time_str = Tools.timestamp_to_utc_time_str(
            start_time, consts.REST_COLLEC_TTIME_PATTERN)
        end_time_str = Tools.timestamp_to_utc_time_str(
            end_time, consts.REST_COLLEC_TTIME_PATTERN)
        url = RestHandler.REST_CPGSTATISTICS_URL % (
            start_time_str, end_time_str)
        rejson = self.get_resinfo_call(url, method='GET')
        return rejson

    def list_storage_host(self):
        rejson = self.get_resinfo_call(RestHandler.REST_HOSTS_URL,
                                       method='GET')
        return rejson
