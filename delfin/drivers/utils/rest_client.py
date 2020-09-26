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
import ssl
import six
import requests
from oslo_log import log as logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from delfin import exception
from delfin import ssl_utils
from delfin.drivers.hpe.hpe_3par import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


class HostNameIgnoringAdapter(HTTPAdapter):

    def cert_verify(self, conn, url, verify, cert):
        conn.assert_hostname = False
        return super(HostNameIgnoringAdapter, self).cert_verify(
            conn, url, verify, cert)

    def init_poolmanager(self, connections, maxsize, block=False,
                         **pool_kwargs):
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize,
                                       block=block, strict=False,
                                       ssl_version=ssl.PROTOCOL_TLSv1,
                                       **pool_kwargs)


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
        self.session.mount("https://", ssl_utils.HostNameIgnoreAdapter())

    def do_call(self, url, data, method,
                calltimeout=consts.SOCKET_TIMEOUT):
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
            LOG.error('Connect Timeout err: {}'.format(ct))
            raise exception.InvalidIpOrPort()
        except requests.exceptions.SSLError as e:
            LOG.error('SSLError for %s %s' % (method, url))
            err_str = six.text_type(e)
            if 'wrong ssl version' in err_str or \
                    'sslv3 alert handshake failure' in err_str:
                raise exception.WrongTlsVersion()
            elif 'no cipher match' in err_str:
                raise exception.CipherNotMatch()
            elif 'certificate verify failed' in err_str:
                raise exception.SSLCertificateFailed()
            else:
                raise e
        except Exception as err:
            LOG.exception('Bad response from server: %(url)s.'
                          ' Error: %(err)s', {'url': url, 'err': err})
            if 'WSAETIMEDOUT' in str(err):
                raise exception.ConnectTimeout()
            elif 'Failed to establish a new connection' in str(err):
                LOG.error('Failed to establish: {}'.format(err))
                raise exception.InvalidIpOrPort()
            else:
                raise exception.BadResponse()

        return res
