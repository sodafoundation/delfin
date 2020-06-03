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

from oslo_log import log as logging
import requests
import six

from dolphin import exception
from dolphin.i18n import _
from dolphin.drivers.huawei.oceanstor import consts

LOG = logging.getLogger(__name__)


class RestClient(object):
    """Common class for Huawei OceanStor storage system."""

    def __init__(self, **kwargs):
        # self.configuration = configuration
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', '8088')
        self.san_address = [
            'https://' + host + ':' + port + '/deviceManager/rest/']
        self.san_user = kwargs.get('username')
        self.san_password = kwargs.get('password')
        self.session = None
        self.url = None
        self.device_id = None

    def init_http_head(self):
        self.url = None
        self.session = requests.Session()
        self.session.headers.update({
            "Connection": "keep-alive",
            "Content-Type": "application/json"})
        self.session.verify = False
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
            data = {"username": self.san_user,
                    "password": self.san_password,
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

    def try_login(self):
        try:
            self.login()
        except Exception as err:
            LOG.warning('Login failed. Error: %s.', err)

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
        result = self.call(url, method='GET')

        msg = _('Create lun error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)

        return result['data']

    def get_all_volumes(self):
        url = "/lun"
        result = self.call(url, None, "GET", log_filter_flag=True)
        msg = _('Query resource volume error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)
        return result['data']

    def get_all_pools(self):
        url = "/storagepool"
        result = self.call(url, None, "GET", log_filter_flag=True)
        msg = _('Query resource pool error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)
        return result['data']

    def get_pool_info(self, pool_name=None, pools=None):
        info = {}
        if not pool_name:
            return info

        for pool in pools:
            if pool_name.strip() != pool['NAME']:
                continue

            if pool.get('USAGETYPE') == consts.FILE_SYSTEM_POOL_TYPE:
                break

            info['ID'] = pool['ID']
            info['CAPACITY'] = pool.get('DATASPACE', pool['USERFREECAPACITY'])
            info['TOTALCAPACITY'] = pool.get('USERTOTALCAPACITY', '0')
            info['TIER0CAPACITY'] = pool.get('TIER0CAPACITY', '0')
            info['TIER1CAPACITY'] = pool.get('TIER1CAPACITY', '0')
            info['TIER2CAPACITY'] = pool.get('TIER2CAPACITY', '0')

        return info

    def get_pool_id(self, pool_name):
        pools = self.get_all_pools()
        pool_info = self.get_pool_info(pool_name, pools)

        if not pool_info:
            msg = _('Can not get pool info. pool: %s') % pool_name
            LOG.error(msg)
            raise exception.StorageBackendException(reason=msg)

        return pool_info['ID']
