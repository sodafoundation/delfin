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
from oslo_log import log as logging

from delfin import exception
from delfin import ssl_utils
from delfin.i18n import _

LOG = logging.getLogger(__name__)

SOCKET_TIMEOUT = 10


class RestClient(object):

    def __init__(self, **kwargs):
        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        self.rest_host = rest_access.get('host')
        self.rest_port = rest_access.get('port')
        self.rest_username = rest_access.get('username')
        self.rest_password = rest_access.get('password')
        self.san_address = 'https://%s:%s' % \
                           (self.rest_host, str(self.rest_port))
        self.session = None
        self.device_id = None

        self.verify = kwargs.get('verify', False)
        self.rest_auth_token = None

    def init_http_head(self):
        if self.session:
            self.session.close()
        self.session = requests.Session()
        self.session.headers.update({
            "Connection": "keep-alive",
            'Accept': 'application/json',
            "Content-Type": "application/json"})
        if not self.verify:
            self.session.verify = False
        else:
            LOG.debug("Enable certificate verification, ca_path: {0}".format(
                self.verify))
            self.session.verify = self.verify
        self.session.trust_env = False
        self.session.mount("https://",
                           ssl_utils.get_host_name_ignore_adapter())

    def do_call(self, url, data, method,
                calltimeout=SOCKET_TIMEOUT):
        if 'http' not in url:
            if self.san_address:
                url = '%s%s' % (self.san_address, url)

        kwargs = {'timeout': calltimeout}
        if data:
            kwargs['data'] = json.dumps(data)

        if method in ('POST', 'PUT', 'GET', 'DELETE'):
            func = getattr(self.session, method.lower())
        else:
            msg = _("Request method %s is invalid.") % method
            LOG.error(msg)
            raise exception.StorageBackendException(msg)
        res = None
        try:
            res = func(url, **kwargs)
        except requests.exceptions.ConnectTimeout as ct:
            LOG.error('Connect Timeout error for url([{}]{}): {}'.format(
                method, url, ct))
            raise exception.InvalidIpOrPort()
        except requests.exceptions.ReadTimeout as rt:
            LOG.error('Read timed out error for url([{}]{}): {}'.format(
                method, url, rt))
            raise exception.StorageBackendException(six.text_type(rt))
        except requests.exceptions.SSLError as e:
            err_str = six.text_type(e)
            LOG.error('SSLError for url([{}]{}): {}'.format(
                method, url, err_str))
            if 'certificate verify failed' in err_str:
                raise exception.SSLCertificateFailed()
            else:
                raise exception.SSLHandshakeFailed()
        except Exception as err:
            LOG.error('Bad response from server for url([{}]{}): {}'.format(
                method, url, err))
            if 'WSAETIMEDOUT' in str(err):
                raise exception.ConnectTimeout()
            elif 'Failed to establish a new connection' in str(err):
                raise exception.InvalidIpOrPort()
            elif 'Read timed out' in str(err):
                raise exception.StorageBackendException(six.text_type(err))
            else:
                raise exception.BadResponse()

        return res
