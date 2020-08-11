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
from delfin.drivers.hds.vsp import consts
from delfin.i18n import _

LOG = logging.getLogger(__name__)


# restClient of hdsvsp
class RestClient(object):
    """Common class for Hpe hdsvsp storage system."""
    hdsvsp_Auth_Token = None
    hdsvsp_Session_Id = None
    # hdsvsp_Auth_Url = '/ConfigurationManager/v1/objects/sessions/'
    # POST    /api/v1/credentials
    hdsvsp_Auth_Url = '/ConfigurationManager/v1/objects/sessions/ -d'
    # GET    /api/v1/system
    hdsvsp_Specific_Storage_Url = '/ConfigurationManager/v1/\
                                  objects/storages/instance'
    # GET
    hdsvsp_Summer_Storage_Url = '/ConfigurationManager/v1/\
                                objects/storage-summaries/instance'
    # GET    /api/v1/capacity
    hdsvsp_Capacity_Url = '/ConfigurationManager/v1/objects/\
                          total-capacities/instance'
    # GET    /api/v1/cpgs
    hdsvsp_Pools_Url = '/ConfigurationManager/v1/objects/pools'
    # GET    /api/v1/volumes
    hdsvsp_Volumes_Url = '/ConfigurationManager/v1/objects/ldevs'
    # GET
    hdsvsp_Ports_Url = '/ConfigurationManager/v1/objects/ports'
    hdsvsp_Logout_Url = '/ConfigurationManager/v1/objects/sessions/'
    hdsvsp_Alert_Url = '/ConfigurationManager/v1/objects/sessions/'

    hdsvsp_Auth_Key = 'Authorization:Session'  # X-HP3PAR-WSAPI-SessionKey

    def __init__(self, **kwargs):

        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        host = rest_access.get('host')
        port = rest_access.get('port')
        self.san_user = rest_access.get('username')
        self.san_password = rest_access.get('password')
        self.san_address = 'https://' + host + ':' + port
        self.session = None
        self.url = self.san_address
        self.enable_verify = False
        self.ca_path = 'certificate verification file path'

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
            # if not self.assert_hostname:
            #     self.session.mount("https://", HostNameIgnoreAdapter())
        self.session.trust_env = False

    def do_call(self, url, data, method,
                calltimeout=consts.SOCKET_TIMEOUT):
        """Send requests to hdsvsp storage server.
        """
        if 'http' not in url:
            if self.url:
                url = self.url + url

        LOG.info('obj url=={0}'.format(url))
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
            raise exception.ConnectTimeout(reason=ct)
        except Exception as err:
            LOG.exception('Bad response from server: %(url)s.'
                          ' Error: %(err)s', {'url': url, 'err': err})
            raise err

        return res

    def call(self, url, data=None, method=None):
        """Send requests to server.
        If fail, try another RestURL.
        """
        accessSession = None

        if self.session is None:
            self.init_http_head()
            if RestClient.hdsvsp_Auth_Token is not None:
                self.session.headers[RestClient.hdsvsp_Auth_Key] = \
                    RestClient.hdsvsp_Auth_Token

        LOG.info('url=={0}{1}{2}'.format(url, '==session.headers==',
                                         self.session.headers))

        res = self.do_call(url, data, method)
        # status_code=401 "Failed to get token via session"
        if res is not None:
            if res.status_code == 401:
                LOG.error("Failed to get token via session=={0}=={1}"
                          .format(res.status_code, res.text))
                LOG.error("Failed to get token via session，relogin，\
                          Get token again！！！")
                try:
                    self.logout()
                except Exception as err:
                    LOG.error('logout error:{}'.format(err))
                RestClient.hdsvsp_Auth_Token = None
                accessSession = self.login()
                if accessSession is not None:
                    res = self.do_call(url, data, method)
        else:
            LOG.error('login res is None')
        return res

    def get_resinfo_call(self, url, data=None, method=None, resName=None):
        LOG.info('')
        LOG.info('hds vsp get {0}{1}{2}'.format(resName,
                                                '=================', url))
        rejson = None

        self.login()
        res = self.call(url, data, method)
        if res is not None:
            LOG.info(res.status_code)
            if res.status_code == 200:
                rejson = res.json()
            else:
                LOG.info("--------------------")
                LOG.info(res)
                LOG.info("--------------------")
                LOG.info(res.text)
                LOG.info("--------------------")
        return rejson

    def login(self):
        LOG.info('')
        LOG.info('hds vsp login===')
        accessSession = RestClient.hdsvsp_Auth_Token

        LOG.info('REST_AUTH_TOKEN=={0}'.format(accessSession))
        if accessSession is None:
            if self.san_address:
                url = RestClient.hdsvsp_Auth_Url
                LOG.info('login url=={0}'.format(url))

                data = {"user": self.san_user,
                        "password": self.san_password,
                        "sessionType": 1}
                LOG.info('login data=={0}'.format(data))
                self.init_http_head()
                res = self.do_call(url, data, 'PUT',
                                   calltimeout=consts.LOGIN_SOCKET_TIMEOUT)
                LOG.info('login res=={0}'.format(res))
                # print (res)
                if res is not None:
                    if res.status_code == 201:
                        result = res.json()
                        accessSession = result['token']
                        RestClient.hdsvsp_Session_Id = result['sessionId']
                        self.session.headers[
                            RestClient.hdsvsp_Auth_Key] = accessSession
                        LOG.info('Login success: %(url)s', {'url': url})
                        # LOG.info('session.headers', self.session.headers)
                    else:
                        LOG.error("Login error. URL: %(url)s\n"
                                  "Reason: %(reason)s.",
                                  {"url": url, "reason": res.text})
                        if 'user.login.user_or_value_invalid' in res.text:
                            raise exception.NotAuthorized(reason='')
                        else:
                            raise exception.Invalid(reason=res.text)
                else:
                    LOG.error('login res is None')
                    raise exception.InvalidResults(reason='res is None')
            else:
                LOG.error('login Parameter error')
        else:
            LOG.error(
                "==No login required！self.accessSession have value=={}".format(
                    accessSession))

        if accessSession is None:
            msg = _("Failed to login with all rest URLs.")
            LOG.error(msg)
            raise exception.BadRequest(reason=msg)
        LOG.info('RestClient.REST_AUTH_TOKEN=={0}'.format(accessSession))
        LOG.info('')
        return accessSession

    def logout(self):
        LOG.info('hds vsp Logout the session=================')
        try:
            RestClient.hdsvsp_Auth_Token = None
            url = RestClient.hdsvsp_Logout_Url
            if RestClient.hdsvsp_Session_Id is not None:
                url = url + str(RestClient.hdsvsp_Session_Id)
            if self.url:
                res = self.call(url, method='DELETE')
                if res is not None:
                    LOG.info("Logout re:{0}".format(res))
                    LOG.info(res.text)
        except Exception as err:
            LOG.error('logout error:{}'.format(err))
            raise exception.StorageBackendException(
                reason='Failed to Logout from restful')

    def get_storage(self):
        rejson = ""
#        specificjson = self.get_specific_storage()
#        summaryjson = self.get_summary_storage()
#        capacityjson = self.get_capacity()
        return rejson

    def get_specific_storage(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Specific_Storage_Url,
                                       method='GET',
                                       resName='Specific_Storage')
        return rejson

    def get_summary_storage(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Summer_Storage_Url,
                                       method='GET',
                                       resName='Summer_Storage')
        return rejson

    def get_capacity(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Capacity_Url,
                                       method='GET',
                                       resName='capacity')
        return rejson

    def get_all_pools(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Pools_Url,
                                       method='GET',
                                       resName='pool')
        return rejson

    def get_all_volumes(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Volumes_Url,
                                       method='GET',
                                       resName='volume paginated')
        return rejson

    def get_ports(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Ports_Url,
                                       method='GET', resName='ports paginated')
        return rejson

    def get_alerts(self):
        rejson = self.get_resinfo_call(RestClient.hdsvsp_Alert_Url,
                                       method='GET', resName='ports paginated')
        return rejson
    """
    def paginated_call(self, url, data=None, method=None, resName=None,
                       page_size=consts.QUERY_PAGE_SIZE):
        rejson = None
        start, end = 0, page_size

        while True:
            url_p = '{0}?range=[{1}-{2}]'.format(url, start, end)
            start, end = end, end + page_size
            result = self.get_resinfo_call(url_p, data, method, resName)

            # Empty data if this is first page, OR last page got all data
            if result is None:
                break
            if rejson is None:
                rejson = result
            else:
                rejson['total'] = rejson['total'] + result['total']
                rejson['members'].extend(result['members'])
            # Check if this is last page
            if result['total'] < page_size:
                break

        return rejson
      """
