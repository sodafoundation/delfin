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
        self.verify = kwargs.get('verify', False)
        self.rest_auth_token = None

    def init_http_head(self):
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
