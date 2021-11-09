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

from delfin.common import constants
from delfin import cryptor
from delfin import exception
from delfin.drivers.huawei.oceanstor import consts
from delfin.ssl_utils import HostNameIgnoreAdapter
from delfin.i18n import _

LOG = logging.getLogger(__name__)


def _get_timestamp_values(metric, value):
    timestamp = int(metric['CMO_STATISTIC_TIMESTAMP']) * 1000
    return {timestamp: value}


def _get_selection(selection):
    selected_metrics = []
    ids = ''
    for key, value in consts.OCEANSTOR_METRICS.items():
        if selection.get(key):
            selected_metrics.append(key)
            if ids:
                ids = ids + ',' + value
            else:
                ids = value
    return selected_metrics, ids


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
            raise exception.StorageBackendException(msg)

        try:
            res = func(url, **kwargs)
        except requests.exceptions.SSLError as e:
            LOG.error('SSLError exception from server: %(url)s.'
                      ' Error: %(err)s', {'url': url, 'err': e})
            err_str = six.text_type(e)
            if 'certificate verify failed' in err_str:
                raise exception.SSLCertificateFailed()
            else:
                raise exception.SSLHandshakeFailed()
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
                    "password": cryptor.decode(self.rest_password),
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
                raise exception.StorageBackendException(msg)
            break

        if device_id is None:
            msg = _("Failed to login with all rest URLs.")
            LOG.error(msg)
            raise exception.StorageBackendException(msg)

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
                       params=None, log_filter_flag=False,
                       page_size=consts.QUERY_PAGE_SIZE):
        if params:
            url = "{0}?{1}".format(url, params)
        else:
            url = "{0}?".format(url)

        result_list = []
        start, end = 0, page_size
        msg = _('Query resource volume error')
        while True:
            url_p = "{0}range=[{1}-{2}]".format(url, start, end)
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
            raise exception.StorageBackendException(msg)

    def _assert_data_in_result(self, result, msg):
        if 'data' not in result:
            err_msg = _('%s "data" is not in result.') % msg
            LOG.error(err_msg)
            raise exception.StorageBackendException(err_msg)

    def get_storage(self):
        url = "/system/"
        result = self.call(url, method='GET', log_filter_flag=True)

        msg = _('Get storage error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)

        return result['data']

    def get_all_controllers(self):
        url = "/controller"
        result = self.call(url, method='GET', log_filter_flag=True)

        msg = _('Get controller error.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)

        return result['data']

    def get_all_ports(self):
        url = "/fc_port"
        fc_ports = self.paginated_call(
            url, None, "GET", log_filter_flag=True)

        url = "/fcoe_port"
        fcoe_ports = self.paginated_call(
            url, None, "GET", log_filter_flag=True)

        url = "/eth_port"
        eth_ports = self.paginated_call(
            url, None, "GET", log_filter_flag=True)

        url = "/pcie_port"
        pcie_ports = self.paginated_call(
            url, None, "GET", log_filter_flag=True)

        url = "/bond_port"
        bond_ports = self.paginated_call(
            url, None, "GET", log_filter_flag=True)

        url = "/sas_port"
        sas_ports = self.paginated_call(
            url, None, "GET", log_filter_flag=True)

        return fc_ports + fcoe_ports + eth_ports\
            + pcie_ports + bond_ports + sas_ports

    def get_all_volumes(self):
        url = "/lun"
        return self.paginated_call(url, None, "GET", log_filter_flag=True)

    def get_all_disks(self):
        url = "/disk"
        return self.paginated_call(url, None, "GET", log_filter_flag=True)

    def get_all_pools(self):
        url = "/storagepool"
        return self.paginated_call(url, None, "GET", log_filter_flag=True)

    def get_all_filesystems(self):
        url = "/filesystem"
        return self.paginated_call(url, None, "GET", log_filter_flag=True)

    def get_all_qtrees(self, filesystems):
        url = "/quotatree"
        qt_list = []
        for fs in filesystems:
            params = "PARENTTYPE=40&PARENTID={0}&".format(fs['ID'])
            qt = self.paginated_call(url, None, "GET",
                                     params=params, log_filter_flag=True)
            qt_list.extend(qt)
        return qt_list

    def get_all_filesystem_quotas(self, fs_id):
        url = "/FS_QUOTA"
        params = "PARENTTYPE=40&PARENTID={0}&".format(fs_id)
        return self.paginated_call(url, None, "GET",
                                   params=params, log_filter_flag=True)

    def get_all_qtree_quotas(self, qt_id):
        url = "/FS_QUOTA"
        params = "PARENTTYPE=16445&PARENTID={0}&".format(qt_id)
        return self.paginated_call(url, None, "GET",
                                   params=params, log_filter_flag=True)

    def get_all_shares(self):
        url = "/CIFSHARE"
        cifs = self.paginated_call(url, None, "GET", log_filter_flag=True)

        url = "/NFSHARE"
        nfs = self.paginated_call(url, None, "GET", log_filter_flag=True)

        url = "/FTP_SHARE_AUTH_CLIENT"
        ftps = self.paginated_call(url, None, "GET", log_filter_flag=True)

        return cifs + nfs + ftps

    def get_all_mapping_views(self):
        url = "/mappingview"
        view = self.paginated_call(url, None, "GET", log_filter_flag=True)
        return view

    def get_all_associate_resources(self, url, obj_type, obj_id):
        params = "ASSOCIATEOBJTYPE={0}&ASSOCIATEOBJID={1}&".format(obj_type,
                                                                   obj_id)
        return self.paginated_call(url, None, "GET",
                                   params=params, log_filter_flag=True)

    def get_all_associate_mapping_views(self, obj_type, obj_id):
        url = "/mappingview/associate"
        return self.get_all_associate_resources(url, obj_type, obj_id)

    def get_all_associate_hosts(self, obj_type, obj_id):
        url = "/host/associate"
        return self.get_all_associate_resources(url, obj_type, obj_id)

    def get_all_associate_volumes(self, obj_type, obj_id):
        url = "/lun/associate"
        return self.get_all_associate_resources(url, obj_type, obj_id)

    def get_all_associate_ports(self, obj_type, obj_id):
        eth_ports = self.get_all_associate_resources(
            "/eth_port/associate", obj_type, obj_id)
        fc_ports = self.get_all_associate_resources(
            "/fc_port/associate", obj_type, obj_id)
        fcoe_ports = self.get_all_associate_resources(
            "/fcoe_port/associate", obj_type, obj_id)

        return eth_ports + fc_ports + fcoe_ports

    def get_all_hosts(self):
        url = "/host"
        host = self.paginated_call(url, None, "GET", log_filter_flag=True)
        return host

    def get_all_initiators(self):
        url = "/fc_initiator"
        fc_i = self.paginated_call(url, None, "GET", log_filter_flag=True)
        url = "/iscsi_initiator"
        iscsi_i = self.paginated_call(url, None, "GET", log_filter_flag=True)
        url = "/ib_initiator"
        ib_i = self.paginated_call(url, None, "GET", log_filter_flag=True)
        return fc_i + iscsi_i + ib_i

    def get_all_host_groups(self):
        url = "/hostgroup"
        hostg = self.paginated_call(url, None, "GET", log_filter_flag=True)
        return hostg

    def get_all_port_groups(self):
        url = "/portgroup"
        portg = self.paginated_call(url, None, "GET", log_filter_flag=True)
        return portg

    def get_all_volume_groups(self):
        url = "/lungroup"
        lungroup = self.paginated_call(url, None, "GET", log_filter_flag=True)
        return lungroup

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

    def _get_performance_switch(self):
        url = "/performance_statistic_switch"
        result = self.call(url, method='GET', log_filter_flag=True)

        msg = _('Get performance_statistic_switch failed.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)
        return result['data']

    def _set_performance_switch(self, value):
        url = "/performance_statistic_switch"
        data = {"CMO_PERFORMANCE_SWITCH": value}
        result = self.call(url, data, method='PUT', log_filter_flag=True)

        msg = _('Set performance_statistic_switch failed.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)
        return result['data']

    def _get_performance_strategy(self):
        url = "/performance_statistic_strategy"
        result = self.call(url, method='GET', log_filter_flag=True)

        msg = _('Get performance_statistic_strategy failed.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)
        return result['data']

    def _set_performance_strategy(self, hist_enable=1, hist_duration=60,
                                  auto_stop=0, duration=5, max_duration=0):
        url = "/performance_statistic_strategy"
        data = {
            "CMO_STATISTIC_ARCHIVE_SWITCH": hist_enable,
            "CMO_STATISTIC_ARCHIVE_TIME": hist_duration,
            "CMO_STATISTIC_AUTO_STOP": auto_stop,
            "CMO_STATISTIC_INTERVAL": duration,
            "CMO_STATISTIC_MAX_TIME": max_duration
        }
        result = self.call(url, data, method='PUT', log_filter_flag=True)

        msg = _('Set performance_statistic_strategy failed.')
        self._assert_rest_result(result, msg)
        self._assert_data_in_result(result, msg)
        return result['data']

    def _get_metrics(self, resource_type, resource_id, metrics_ids):
        url = "/performace_statistic/cur_statistic_data"
        params = "CMO_STATISTIC_UUID={0}:{1}&CMO_STATISTIC_DATA_ID_LIST={2}&"\
                 "timeConversion=0&"\
            .format(resource_type, resource_id, metrics_ids)
        return self.paginated_call(url, None, "GET",
                                   params=params, log_filter_flag=True)

    def enable_metrics_collection(self):
        return self._set_performance_switch('1')

    def disable_metrics_collection(self):
        return self._set_performance_switch('0')

    def configure_metrics_collection(self):
        self.disable_metrics_collection()
        self._set_performance_strategy(hist_enable=1, hist_duration=300,
                                       auto_stop=0, duration=60,
                                       max_duration=0)
        self.enable_metrics_collection()

    def get_pool_metrics(self, storage_id, selection):
        pools = self.get_all_pools()
        pool_metrics = []

        select_metrics, select_ids = _get_selection(selection)
        for pool in pools:
            try:
                metrics = self._get_metrics(pool['TYPE'], pool['ID'],
                                            select_ids)
                for metric in metrics:
                    data_list = metric['CMO_STATISTIC_DATA_LIST'].split(",")
                    for index, key in enumerate(select_metrics):
                        data = int(data_list[index])
                        if key in consts.CONVERT_TO_MILLI_SECOND_LIST:
                            data = data * 1000
                        labels = {
                            'storage_id': storage_id,
                            'resource_type': 'pool',
                            'resource_id': pool['ID'],
                            'resource_name': pool['NAME'],
                            'type': 'RAW',
                            'unit': consts.POOL_CAP[key]['unit']
                        }
                        values = _get_timestamp_values(metric, data)
                        m = constants.metric_struct(name=key, labels=labels,
                                                    values=values)
                        pool_metrics.append(m)
            except Exception as ex:
                msg = "Failed to get metrics for pool:{0} error: {1}" \
                    .format(pool['NAME'], ex)
                LOG.error(msg)
        return pool_metrics

    def get_volume_metrics(self, storage_id, selection):
        volumes = self.get_all_volumes()
        volume_metrics = []

        select_metrics, select_ids = _get_selection(selection)
        for volume in volumes:
            try:
                metrics = self._get_metrics(volume['TYPE'], volume['ID'],
                                            select_ids)
                for metric in metrics:
                    data_list = metric['CMO_STATISTIC_DATA_LIST'].split(",")
                    for index, key in enumerate(select_metrics):
                        data = int(data_list[index])
                        if key in consts.CONVERT_TO_MILLI_SECOND_LIST:
                            data = data * 1000
                        labels = {
                            'storage_id': storage_id,
                            'resource_type': 'volume',
                            'resource_id': volume['ID'],
                            'resource_name': volume['NAME'],
                            'type': 'RAW',
                            'unit': consts.VOLUME_CAP[key]['unit']
                        }
                        values = _get_timestamp_values(metric, data)
                        m = constants.metric_struct(name=key, labels=labels,
                                                    values=values)
                        volume_metrics.append(m)
            except Exception as ex:
                msg = "Failed to get metrics for volume:{0} error: {1}" \
                    .format(volume['NAME'], ex)
                LOG.error(msg)

        return volume_metrics

    def get_controller_metrics(self, storage_id, selection):
        controllers = self.get_all_controllers()
        controller_metrics = []

        select_metrics, select_ids = _get_selection(selection)
        for controller in controllers:
            try:
                metrics = self._get_metrics(controller['TYPE'],
                                            controller['ID'],
                                            select_ids)
                for metric in metrics:
                    data_list = metric['CMO_STATISTIC_DATA_LIST'].split(",")
                    for index, key in enumerate(select_metrics):
                        data = int(data_list[index])
                        if key in consts.CONVERT_TO_MILLI_SECOND_LIST:
                            data = data * 1000
                        labels = {
                            'storage_id': storage_id,
                            'resource_type': 'controller',
                            'resource_id': controller['ID'],
                            'resource_name': controller['NAME'],
                            'type': 'RAW',
                            'unit': consts.CONTROLLER_CAP[key]['unit']
                        }
                        values = _get_timestamp_values(metric, data)
                        m = constants.metric_struct(name=key, labels=labels,
                                                    values=values)
                        controller_metrics.append(m)
            except Exception as ex:
                msg = "Failed to get metrics for controller:{0} error: {1}" \
                    .format(controller['NAME'], ex)
                LOG.error(msg)

        return controller_metrics

    def get_port_metrics(self, storage_id, selection):
        ports = self.get_all_ports()
        port_metrics = []

        select_metrics, select_ids = _get_selection(selection)
        for port in ports:
            # ETH_PORT collection not supported
            if port['TYPE'] == 213:
                continue
            try:
                metrics = self._get_metrics(port['TYPE'], port['ID'],
                                            select_ids)
                for metric in metrics:
                    data_list = metric['CMO_STATISTIC_DATA_LIST'].split(",")
                    for index, key in enumerate(select_metrics):
                        data = int(data_list[index])
                        if key in consts.CONVERT_TO_MILLI_SECOND_LIST:
                            data = data * 1000
                        labels = {
                            'storage_id': storage_id,
                            'resource_type': 'port',
                            'resource_id': port['ID'],
                            'resource_name': port['NAME'],
                            'type': 'RAW',
                            'unit': consts.PORT_CAP[key]['unit']
                        }
                        values = _get_timestamp_values(metric, data)
                        m = constants.metric_struct(name=key, labels=labels,
                                                    values=values)
                        port_metrics.append(m)
            except Exception as ex:
                msg = "Failed to get metrics for port:{0} error: {1}" \
                    .format(port['NAME'], ex)
                LOG.error(msg)

        return port_metrics

    def get_disk_metrics(self, storage_id, selection):
        disks = self.get_all_disks()
        disk_metrics = []

        select_metrics, select_ids = _get_selection(selection)
        for disk in disks:
            try:
                metrics = self._get_metrics(disk['TYPE'], disk['ID'],
                                            select_ids)
                for metric in metrics:
                    data_list = metric['CMO_STATISTIC_DATA_LIST'].split(",")
                    for index, key in enumerate(select_metrics):
                        data = int(data_list[index])
                        if key in consts.CONVERT_TO_MILLI_SECOND_LIST:
                            data = data * 1000
                        labels = {
                            'storage_id': storage_id,
                            'resource_type': 'disk',
                            'resource_id': disk['ID'],
                            'type': 'RAW',
                            'unit': consts.DISK_CAP[key]['unit'],
                            'resource_name':
                                disk['MODEL'] + ':' + disk['SERIALNUMBER']
                        }
                        values = _get_timestamp_values(metric, data)
                        m = constants.metric_struct(name=key, labels=labels,
                                                    values=values)
                        disk_metrics.append(m)
            except Exception as ex:
                msg = "Failed to get metrics for disk:{0} error: {1}"\
                    .format(disk['ID'], ex)
                LOG.error(msg)

        return disk_metrics
