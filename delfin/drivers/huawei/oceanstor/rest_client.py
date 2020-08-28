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
import six
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from oslo_log import log as logging

from delfin import exception
from delfin.drivers.huawei.oceanstor import consts
from delfin.ssl_utils import HostNameIgnoreAdapter
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class RestClient(object):
    """Common class for Huawei OceanStor storage system."""

    def __init__(self, **kwargs):

        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        self.rest_host = rest_access.get('host')
        self.rest_port = rest_access.get('port')
        self.rest_username = rest_access.get('username')
        self.rest_password = rest_access.get('password')

        # Lists of addresses to try, for authorization
        address = 'https://%(host)s:%(port)s/deviceManager/rest/' % \
                  {'host': self.rest_host, 'port': str(self.rest_port)}
        self.san_address = [address]
        self.session = None
        self.url = None
        self.device_id = None
        self.verify = None
        urllib3.disable_warnings(InsecureRequestWarning)
        self.reset_connection(**kwargs)

    def reset_connection(self, **kwargs):
        self.verify = kwargs.get('verify', False)
        try:
            self.login()
        except Exception as ex:
            msg = "Failed to login to OceanStor: {}".format(ex)
            LOG.error(msg)
            raise exception.InvalidCredential(msg)

    def init_http_head(self):
        self.url = None
        self.session = requests.Session()
        self.session.headers.update({
            "Connection": "keep-alive",
            "Content-Type": "application/json"})
        if not self.verify:
            self.session.verify = False
        else:
            LOG.debug("Enable certificate verification, verify: {0}".format(
                self.verify))
            self.session.verify = self.verify
            self.session.mount("https://", HostNameIgnoreAdapter())

        self.session.trust_env = False

    def do_call(self, url, data, method,
                calltimeout=consts.SOCKET_TIMEOUT, log_filter_flag=False):
        """Send requests to Huawei storage server.

        Send HTTPS call, get response in JSON.
        Convert response into Python Object and return it.
        """
        if self.url:
            url = self.url + url

        kwargs = {'timeout': calltimeout}
        if data:
            kwargs['data'] = json.dumps(data)

        if method in ('POST', 'PUT', 'GET', 'DELETE'):
            func = getattr(self.session, method.lower())
        else:
            msg = _("Request method %s is invalid.") % method
            LOG.error(msg)
            raise exception.StorageBackendException(reason=msg)

        try:
            res = func(url, **kwargs)
        except requests.exceptions.SSLError as ssl_exc:
            LOG.exception('SSLError exception from server: %(url)s.'
                          ' Error: %(err)s', {'url': url, 'err': ssl_exc})
            return {"error": {"code": consts.ERROR_CONNECT_TO_SERVER,
                              "description": "Retry with valid certificate."}}
        except Exception as err:
            LOG.exception('Bad response from server: %(url)s.'
                          ' Error: %(err)s', {'url': url, 'err': err})
            return {"error": {"code": consts.ERROR_CONNECT_TO_SERVER,
                              "description": "Connect to server error."}}

        try:
            res.raise_for_status()
        except requests.HTTPError as exc:
            return {"error": {"code": exc.response.status_code,
                              "description": six.text_type(exc)}}

        res_json = res.json()
        if not log_filter_flag:
            LOG.info('\n\n\n\nRequest URL: %(url)s\n\n'
                     'Call Method: %(method)s\n\n'
                     'Request Data: %(data)s\n\n'
                     'Response Data:%(res)s\n\n',
                     {'url': url,
                      'method': method,
                      'data': data,
                      'res': res_json})

        return res_json

    def login(self):
        """Login Huawei storage array."""
        device_id = None
        for item_url in self.san_address:
            url = item_url + "xx/sessions"
            data = {"username": self.rest_username,
                    "password": self.rest_password,
                    "scope": "0"}
            self.init_http_head()
            result = self.do_call(url, data, 'POST',
                                  calltimeout=consts.LOGIN_SOCKET_TIMEOUT,
                                  log_filter_flag=True)

            if (result['error']['code'] != 0) or ("data" not in result):
                LOG.error("Login error. URL: %(url)s\n"
                          "Reason: %(reason)s.",
                          {"url": item_url, "reason": result})
                continue

            LOG.debug('Login success: %(url)s', {'url': item_url})
            device_id = result['data']['deviceid']
            self.device_id = device_id
            self.url = item_url + device_id
            self.session.headers['iBaseToken'] = result['data']['iBaseToken']
            if (result['data']['accountstate']
                    in (consts.PWD_EXPIRED, consts.PWD_RESET)):
                self.logout()
                msg = _("Password has expired or has been reset, "
                        "please change the password.")
                LOG.error(msg)
                raise exception.StorageBackendException(reason=msg)
            break

        if device_id is None:
            msg = _("Failed to login with all rest URLs.")
            LOG.error(msg)
            raise exception.StorageBackendException(reason=msg)

        return device_id

    def call(self, url, data=None, method=None, log_filter_flag=False):
        """Send requests to server.

        If fail, try another RestURL.
        """
        device_id = None
        old_url = self.url
        result = self.do_call(url, data, method,
                              log_filter_flag=log_filter_flag)
        error_code = result['error']['code']
        if (error_code == consts.ERROR_CONNECT_TO_SERVER
                or error_code == consts.ERROR_UNAUTHORIZED_TO_SERVER):
            LOG.error("Can't open the recent url, relogin.")
            device_id = self.login()

        if device_id is not None:
            LOG.debug('Replace URL: \n'
                      'Old URL: %(old_url)s\n,'
                      'New URL: %(new_url)s\n.',
                      {'old_url': old_url,
                       'new_url': self.url})
            result = self.do_call(url, data, method,
                                  log_filter_flag=log_filter_flag)
            if result['error']['code'] in consts.RELOGIN_ERROR_PASS:
                result['error']['code'] = 0
        return result

    def paginated_call(self, url, data=None, method=None,
                       log_filter_flag=False,
                       page_size=consts.QUERY_PAGE_SIZE):
        result_list = []
        start, end = 0, page_size
        msg = _('Query resource volume error')
        while True:
            url_p = '{0}?range=[{1}-{2}]'.format(url, start, end)
            start, end = end, end + page_size
            result = self.call(url_p, data, method, log_filter_flag)
            self._assert_rest_result(result, msg)

            # Empty data if this is first page, OR last page got all data
            if 'data' not in result:
                break

            result_list.extend(result['data'])
            # Check if this is last page
            if len(result['data']) < page_size:
                break

        return result_list

    def logout(self):
        """Logout the session."""
        url = "/sessions"
        if self.url:
            result = self.do_call(url, None, "DELETE")
            self._assert_rest_result(result, _('Logout session error.'))

    def _assert_rest_result(self, result, err_str):
        if result['error']['code'] != 0:
            msg = (_('%(err)s\nresult: %(res)s.') % {'err': err_str,
                                                     'res': result})
            LOG.error(msg)
            raise exception.StorageBackendException(reason=msg)

    def _assert_data_in_result(self, result, msg):
        if 'data' not in result:
            err_msg = _('%s "data" is not in result.') % msg
            LOG.error(err_msg)
            raise exception.StorageBackendException(reason=err_msg)

    def get_storage(self):
        url = "/system/"
        result = self.call(url, method='GET', log_filter_flag=True)

        msg = _('Get storage error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)

        return result['data']

    def get_controller(self):
        url = "/controller"
        result = self.call(url, method='GET', log_filter_flag=True)

        msg = _('Get controller error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)

        return result['data']

    def get_all_volumes(self):
        url = "/lun"
        return self.paginated_call(url, None, "GET", log_filter_flag=True)

    def get_all_pools(self):
        url = "/storagepool"
        return self.paginated_call(url, None, "GET", log_filter_flag=True)

    def clear_alert(self, sequence_number):
        url = "/alarm/currentalarm?sequence=%s" % sequence_number

        # Result always contains error code and description
        result = self.call(url, method="DELETE", log_filter_flag=True)
        if result['error']['code']:
            msg = 'Clear alert failed with reason: %s.' \
                  % result['error']['description']
            raise exception.InvalidResults(msg)
        return result

    def list_alerts(self):
        url = "/alarm/currentalarm"
        result_list = self.paginated_call(url,
                                          None,
                                          "GET",
                                          log_filter_flag=True)
        return result_list
