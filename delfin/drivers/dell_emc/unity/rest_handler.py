# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import threading

import requests
import six
from oslo_log import log as logging

from delfin import cryptor
from delfin import exception
from delfin.drivers.dell_emc.unity import consts
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    REST_AUTH_URL = '/api/types/loginSessionInfo/instances'
    REST_STORAGE_URL = '/api/types/system/instances'
    REST_CAPACITY_URL = '/api/types/systemCapacity/instances'
    REST_SOFT_VERSION_URL = '/api/types/installedSoftwareVersion/instances'
    REST_LUNS_URL = '/api/types/lun/instances'
    REST_POOLS_URL = '/api/types/pool/instances'
    REST_ALERTS_URL = '/api/types/alert/instances'
    REST_DEL_ALERTS_URL = '/api/instances/alert/'
    REST_LOGOUT_URL = '/api/types/loginSessionInfo/action/logout'
    AUTH_KEY = 'EMC-CSRF-TOKEN'
    REST_CONTROLLER_URL = '/api/types/storageProcessor/instances'
    REST_DISK_URL = '/api/types/disk/instances'
    REST_FCPORT_URL = '/api/types/fcPort/instances'
    REST_ETHPORT_URL = '/api/types/ethernetPort/instances'
    REST_IP_URL = '/api/types/ipInterface/instances'
    REST_FILESYSTEM_URL = '/api/types/filesystem/instances'
    REST_NFSSHARE_URL = '/api/types/nfsShare/instances'
    REST_CIFSSHARE_URL = '/api/types/cifsShare/instances'
    REST_QTREE_URL = '/api/types/treeQuota/instances'
    REST_USERQUOTA_URL = '/api/types/userQuota/instances'
    REST_QUOTACONFIG_URL = '/api/types/quotaConfig/instances'
    REST_VIRTUAL_DISK_URL = '/api/types/virtualDisk/instances'
    STATE_SOLVED = 2

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)
        self.session_lock = threading.Lock()

    def login(self):
        """Login dell_emc unity storage array."""
        try:
            with self.session_lock:
                if self.session is None:
                    self.init_http_head()
                self.session.headers.update({"X-EMC-REST-CLIENT": "true"})
                self.session.auth = requests.auth.HTTPBasicAuth(
                    self.rest_username, cryptor.decode(self.rest_password))
                res = self.call_with_token(RestHandler.REST_AUTH_URL)
                if res.status_code == 200:
                    self.session.headers[RestHandler.AUTH_KEY] = \
                        cryptor.encode(res.headers[RestHandler.AUTH_KEY])
                else:
                    LOG.error("Login error.URL: %s,Reason: %s.",
                              RestHandler.REST_AUTH_URL, res.text)
                    if 'Unauthorized' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    elif 'Forbidden' in res.text:
                        raise exception.InvalidIpOrPort()
                    else:
                        raise exception.StorageBackendException(
                            six.text_type(res.text))
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def call_with_token(self, url, data=None, method='GET',
                        calltimeout=consts.DEFAULT_TIMEOUT):
        auth_key = None
        if self.session:
            auth_key = self.session.headers.get(RestHandler.AUTH_KEY, None)
            if auth_key:
                self.session.headers[RestHandler.AUTH_KEY] \
                    = cryptor.decode(auth_key)
        res = self.do_call(url, data, method, calltimeout)
        if auth_key:
            self.session.headers[RestHandler.AUTH_KEY] = auth_key
        return res

    def logout(self):
        try:
            if self.san_address:
                self.call(RestHandler.REST_LOGOUT_URL, None, 'POST')
            if self.session:
                self.session.close()
        except Exception as e:
            err_msg = "Logout error: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def get_rest_info(self, url, data=None, method='GET',
                      calltimeout=consts.DEFAULT_TIMEOUT):
        retry_times = consts.REST_RETRY_TIMES
        while retry_times >= 0:
            try:
                res = self.call(url, data, method, calltimeout)
                if res.status_code == 200:
                    return res.json()
                err_msg = "rest response abnormal,status_code:%s,res.json:%s" \
                          % (res.status_code, res.json())
                LOG.error(err_msg)
            except Exception as e:
                LOG.error(e)
            retry_times -= 1
        return None

    def call(self, url, data=None, method='GET',
             calltimeout=consts.DEFAULT_TIMEOUT):
        try:
            res = self.call_with_token(url, data, method, calltimeout)
            if res.status_code == 401:
                LOG.error("Failed to get token, status_code:%s,error_mesg:%s" %
                          (res.status_code, res.text))
                self.login()
                res = self.call_with_token(url, data, method, calltimeout)
            elif res.status_code == 503:
                raise exception.InvalidResults(res.text)
            return res
        except Exception as e:
            LOG.error("Method:%s,url:%s failed: %s" % (method, url,
                                                       six.text_type(e)))
            raise e

    def get_all_pools(self):
        url = '%s?%s' % (RestHandler.REST_POOLS_URL,
                         'fields=id,name,health,type,sizeFree,'
                         'sizeTotal,sizeUsed,sizeSubscribed')
        result_json = self.get_rest_info(url)
        return result_json

    def get_storage(self):
        url = '%s?%s' % (RestHandler.REST_STORAGE_URL,
                         'fields=name,model,serialNumber,health')
        result_json = self.get_rest_info(url)
        return result_json

    def get_capacity(self):
        url = '%s?%s' % (RestHandler.REST_CAPACITY_URL,
                         'fields=sizeFree,sizeTotal,sizeUsed,'
                         'sizeSubscribed,totalLogicalSize')
        result_json = self.get_rest_info(url)
        return result_json

    def get_soft_version(self):
        url = '%s?%s' % (RestHandler.REST_SOFT_VERSION_URL,
                         'fields=version')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_luns(self, page_number):
        url = '%s?%s&page=%s' % (RestHandler.REST_LUNS_URL,
                                 'fields=id,name,health,type,sizeAllocated,'
                                 'sizeTotal,sizeUsed,pool,wwn,isThinEnabled',
                                 page_number)
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_alerts(self, page_number):
        url = '%s?%s&page=%s' % (RestHandler.REST_ALERTS_URL,
                                 'fields=id,timestamp,severity,component,'
                                 'messageId,message,description,'
                                 'descriptionId,state',
                                 page_number)
        result_json = self.get_rest_info(
            url, None, 'GET', consts.ALERT_TIMEOUT)
        return result_json

    def get_all_alerts_without_state(self, page_number):
        url = '%s?%s&page=%s' % (RestHandler.REST_ALERTS_URL,
                                 'fields=id,timestamp,severity,component,'
                                 'messageId,message,description,'
                                 'descriptionId',
                                 page_number)
        result_json = self.get_rest_info(
            url, None, 'GET', consts.ALERT_TIMEOUT)
        return result_json

    def remove_alert(self, alert_id):
        data = {"state": RestHandler.STATE_SOLVED}
        url = '%s%s/action/modify' % (RestHandler.REST_DEL_ALERTS_URL,
                                      alert_id)
        result_json = self.get_rest_info(url, data, method='POST')
        return result_json

    def get_all_controllers(self):
        url = '%s?%s' % (RestHandler.REST_CONTROLLER_URL,
                         'fields=id,name,health,model,slotNumber,'
                         'manufacturer,memorySize')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_disks(self):
        url = '%s?%s' % (RestHandler.REST_DISK_URL,
                         'fields=id,name,health,model,slotNumber,'
                         'manufacturer,version,emcSerialNumber,wwn,'
                         'rpm,size,diskGroup,diskTechnology')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_fcports(self):
        url = '%s?%s' % (RestHandler.REST_FCPORT_URL,
                         'fields=id,name,health,slotNumber,storageProcessor,'
                         'currentSpeed,wwn')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_ethports(self):
        url = '%s?%s' % (RestHandler.REST_ETHPORT_URL,
                         'fields=id,name,health,portNumber,storageProcessor,'
                         'speed,isLinkUp,macAddress')
        result_json = self.get_rest_info(url)
        return result_json

    def get_port_interface(self):
        url = '%s?%s' % (RestHandler.REST_IP_URL,
                         'fields=id,ipPort,ipProtocolVersion,'
                         'ipAddress,netmask')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_filesystems(self):
        url = '%s?%s' % (RestHandler.REST_FILESYSTEM_URL,
                         'fields=id,name,health,sizeAllocated,accessPolicy,'
                         'sizeTotal,sizeUsed,isThinEnabled,pool,flrVersion')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_filesystems_without_flr(self):
        url = '%s?%s' % (RestHandler.REST_FILESYSTEM_URL,
                         'fields=id,name,health,sizeAllocated,accessPolicy,'
                         'sizeTotal,sizeUsed,isThinEnabled,pool')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_nfsshares(self):
        url = '%s?%s' % (RestHandler.REST_NFSSHARE_URL,
                         'fields=id,filesystem,name,path')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_cifsshares(self):
        url = '%s?%s' % (RestHandler.REST_CIFSSHARE_URL,
                         'fields=id,filesystem,name,path')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_qtrees(self):
        url = '%s?%s' % (RestHandler.REST_QTREE_URL,
                         'fields=id,filesystem,description,path,hardLimit,'
                         'softLimit,sizeUsed,quotaConfig')
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_userquotas(self):
        url = '%s?%s' % (RestHandler.REST_USERQUOTA_URL,
                         'fields=id,filesystem,hardLimit,softLimit,'
                         'sizeUsed,treeQuota,uid')
        result_json = self.get_rest_info(url)
        return result_json

    def get_quota_configs(self):
        url = '%s?%s' % (RestHandler.REST_QUOTACONFIG_URL,
                         'fields=id,filesystem,treeQuota,quotaPolicy')
        result_json = self.get_rest_info(url)
        return result_json

    def get_host_initiators(self, page):
        url = '/api/types/hostInitiator/instances?%s&page=%s' % \
              ('fields=id,health,type,parentHost,initiatorId', page)
        result_json = self.get_rest_info(url)
        return result_json

    def get_all_hosts(self, page):
        url = '/api/types/host/instances?%s&page=%s' \
              % ('fields=id,health,name,description,osType', page)
        result_json = self.get_rest_info(url)
        return result_json

    def get_host_ip(self):
        url = '/api/types/hostIPPort/instances?%s' % \
              ('fields=id,name,address,netmask,host')
        result_json = self.get_rest_info(url)
        return result_json

    def get_host_lun(self, page):
        url = '/api/types/hostLUN/instances?%s&page=%s' % \
              ('fields=id,host,lun', page)
        result_json = self.get_rest_info(url)
        return result_json

    def get_history_metrics(self, path, page):
        url = '/api/types/metricValue/instances?filter=path EQ "%s"&page=%s'\
              % (path, page)
        result_json = self.get_rest_info(url)
        return result_json

    def get_virtual_disks(self):
        url = '%s?%s' % (RestHandler.REST_VIRTUAL_DISK_URL,
                         'fields=health,name,spaScsiId,tierType,sizeTotal,'
                         'id,model,manufacturer,wwn')
        result_json = self.get_rest_info(url)
        return result_json
