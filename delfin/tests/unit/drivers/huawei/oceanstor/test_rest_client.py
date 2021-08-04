# Copyright 2020 The SODA Authors.
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

from unittest import TestCase, mock
from unittest.mock import call

from requests.sessions import Session

from delfin import exception
from delfin.common import config # noqa
from delfin.drivers.huawei.oceanstor.rest_client import RestClient


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "huawei",
    "model": "oceanstor",
    "rest": {
        "host": "10.0.0.1",
        "port": 1234,
        "username": "user",
        "password": "cGFzc3dvcmQ="
    },
    "extra_attributes": {
        "array_id": "00112233"
    }
}

RESP = {
    "error": {
        "code": 0
    },
    "data": {
        "data": "dummy",
        "deviceid": "0123456",
        "iBaseToken": "112233",
        "accountstate": "GREEN"
    }
}


class TestOceanStorRestClient(TestCase):

    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):

        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        mock_resp.content = content
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    # @mock.patch.object(RestClient, 'login')
    @mock.patch.object(Session, 'post')
    def test_init(self, mock_rest):
        mock_resp = self._mock_response(json_data=RESP)
        mock_rest.return_value = mock_resp
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        self.assertEqual(rest_client.rest_host, "10.0.0.1")
        self.assertEqual(rest_client.rest_port, 1234)
        self.assertEqual(rest_client.session.headers['iBaseToken'], '112233')

    @mock.patch.object(RestClient, 'login')
    def test_reset_connection(self, mock_login):
        mock_login.return_value = None
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        self.assertEqual(rest_client.rest_host, "10.0.0.1")
        self.assertEqual(rest_client.rest_port, 1234)

        mock_login.side_effect = exception.StorageBackendException
        with self.assertRaises(Exception) as exc:
            RestClient(**kwargs)
        self.assertIn('The credentials are invalid',
                      str(exc.exception))

    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_get_storage(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_storage()
        self.assertEqual(data['data'], 'dummy')

        mock_call.return_value = {
            "error": {
                "code": 0
            }
        }
        with self.assertRaises(Exception) as exc:
            rest_client.get_storage()
        self.assertIn('Exception from Storage Backend',
                      str(exc.exception))

        mock_call.return_value['error']['code'] = 1
        with self.assertRaises(Exception) as exc:
            rest_client.get_storage()
        self.assertIn('Exception from Storage Backend',
                      str(exc.exception))

    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_get_controller(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_controllers()
        self.assertEqual(data['data'], 'dummy')
        mock_call.assert_called_with("/controller",
                                     log_filter_flag=True, method='GET')

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_pools(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_pools()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/storagepool", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_hosts(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_hosts()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/host", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_host_groups(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_host_groups()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/hostgroup", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_port_groups(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_port_groups()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/portgroup", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_volume_groups(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_volume_groups()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/lungroup", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_volumes(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_volumes()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/lun", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_initiators(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.side_effects = ["", "", ""]
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        rest_client.get_all_initiators()
        call1 = call("/fc_initiator", None, 'GET', log_filter_flag=True)
        call2 = call("/iscsi_initiator", None, 'GET', log_filter_flag=True)
        call3 = call("/ib_initiator", None, 'GET', log_filter_flag=True)

        calls = [call1, call2, call3]
        mock_call.assert_has_calls(calls)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_all_mapping_views(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_mapping_views()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/mappingview", None,
                                     'GET', log_filter_flag=True)

    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_volumes(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.get_all_volumes()
        self.assertEqual(data['data']['data'], 'dummy')
        mock_call.assert_called_with("/lun", None, 'GET',
                                     log_filter_flag=True)

    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_enable_metrics_collection(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.enable_metrics_collection()
        self.assertEqual(data['data'], 'dummy')
        mock_call.assert_called_with("/performance_statistic_switch",
                                     {'CMO_PERFORMANCE_SWITCH': '1'},
                                     log_filter_flag=True, method='PUT')

    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_disable_metrics_collection(self, mock_login, mock_call):
        mock_login.return_value = None
        mock_call.return_value = RESP
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        data = rest_client.disable_metrics_collection()
        self.assertEqual(data['data'], 'dummy')
        mock_call.assert_called_with("/performance_statistic_switch",
                                     {'CMO_PERFORMANCE_SWITCH': '0'},
                                     log_filter_flag=True, method='PUT')

    @mock.patch.object(RestClient, 'disable_metrics_collection')
    @mock.patch.object(RestClient, 'enable_metrics_collection')
    @mock.patch.object(RestClient, 'call')
    @mock.patch.object(RestClient, 'login')
    def test_configure_metrics_collection(self, mock_login, mock_call,
                                          mock_en, mock_di):
        mock_login.return_value = None
        mock_call.return_value = RESP
        mock_en.return_value = None
        mock_di.return_value = None
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        rest_client.configure_metrics_collection()
        data = {
            "CMO_STATISTIC_ARCHIVE_SWITCH": 1,
            "CMO_STATISTIC_ARCHIVE_TIME": 300,
            "CMO_STATISTIC_AUTO_STOP": 0,
            "CMO_STATISTIC_INTERVAL": 60,
            "CMO_STATISTIC_MAX_TIME": 0
        }
        mock_call.assert_called_with("/performance_statistic_strategy",
                                     data,
                                     log_filter_flag=True, method='PUT')

    @mock.patch.object(RestClient, 'get_all_pools')
    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_pool_metrics(self, mock_login, mock_call,
                              mock_pools):
        mock_login.return_value = None
        mock_call.return_value = [{'CMO_STATISTIC_DATA_LIST': '12,25',
                                   'CMO_STATISTIC_TIMESTAMP': 0}]
        mock_pools.return_value = [
            {'ID': '123', 'TYPE': '100', 'NAME': 'pool'}
        ]
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        metrics = rest_client.get_pool_metrics('', {'iops': {'unit': 'IOPS'}})
        mock_call.assert_called_with(
            "/performace_statistic/cur_statistic_data",
            None, 'GET', log_filter_flag=True,
            params='CMO_STATISTIC_UUID=100:123&CMO_STATISTIC_DATA_ID_LIST=22&'
                   'timeConversion=0&'
        )
        expected_label = {
            'storage_id': '',
            'resource_type': 'pool',
            'resource_id': '123',
            'type': 'RAW',
            'unit': 'IOPS',
            'resource_name': 'pool'
        }
        self.assertEqual(metrics[0].name, 'iops')
        self.assertDictEqual(metrics[0].labels, expected_label)
        self.assertListEqual(list(metrics[0].values.values()), [12])

    @mock.patch.object(RestClient, 'get_all_volumes')
    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_volume_metrics(self, mock_login, mock_call,
                                mock_volumes):
        mock_login.return_value = None
        mock_call.return_value = [{'CMO_STATISTIC_DATA_LIST': '12,25',
                                   'CMO_STATISTIC_TIMESTAMP': 0}]
        mock_volumes.return_value = [
            {'ID': '123', 'TYPE': '100', 'NAME': 'volume'}
        ]
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        metrics = rest_client.get_volume_metrics(
            '', {'iops': {'unit': 'IOPS'}})
        mock_call.assert_called_with(
            "/performace_statistic/cur_statistic_data",
            None, 'GET', log_filter_flag=True,
            params='CMO_STATISTIC_UUID=100:123&CMO_STATISTIC_DATA_ID_LIST=22&'
                   'timeConversion=0&'
        )
        expected_label = {
            'storage_id': '',
            'resource_type': 'volume',
            'resource_id': '123',
            'type': 'RAW',
            'unit': 'IOPS',
            'resource_name': 'volume'
        }
        self.assertEqual(metrics[0].name, 'iops')
        self.assertDictEqual(metrics[0].labels, expected_label)
        self.assertListEqual(list(metrics[0].values.values()), [12])

    @mock.patch.object(RestClient, 'get_all_controllers')
    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_controller_metrics(self, mock_login, mock_call,
                                    mock_controllers):
        mock_login.return_value = None
        mock_call.return_value = [{'CMO_STATISTIC_DATA_LIST': '12,25',
                                   'CMO_STATISTIC_TIMESTAMP': 0}]
        mock_controllers.return_value = [
            {'ID': '123', 'TYPE': '100', 'NAME': 'controller'}
        ]
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        metrics = rest_client.get_controller_metrics(
            '', {'iops': {'unit': 'IOPS'}})
        mock_call.assert_called_with(
            "/performace_statistic/cur_statistic_data",
            None, 'GET', log_filter_flag=True,
            params='CMO_STATISTIC_UUID=100:123&CMO_STATISTIC_DATA_ID_LIST=22&'
                   'timeConversion=0&'
        )
        expected_label = {
            'storage_id': '',
            'resource_type': 'controller',
            'resource_id': '123',
            'type': 'RAW',
            'unit': 'IOPS',
            'resource_name': 'controller'
        }
        self.assertEqual(metrics[0].name, 'iops')
        self.assertDictEqual(metrics[0].labels, expected_label)
        self.assertListEqual(list(metrics[0].values.values()), [12])

    @mock.patch.object(RestClient, 'get_all_ports')
    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_port_metrics(self, mock_login, mock_call,
                              mock_ports):
        mock_login.return_value = None
        mock_call.return_value = [{'CMO_STATISTIC_DATA_LIST': '12,25',
                                   'CMO_STATISTIC_TIMESTAMP': 0}]
        mock_ports.return_value = [
            {'ID': '123', 'TYPE': '100', 'NAME': 'port'}
        ]
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        metrics = rest_client.get_port_metrics('', {'iops': {'unit': 'IOPS'}})
        mock_call.assert_called_with(
            "/performace_statistic/cur_statistic_data",
            None, 'GET', log_filter_flag=True,
            params='CMO_STATISTIC_UUID=100:123&CMO_STATISTIC_DATA_ID_LIST=22&'
                   'timeConversion=0&'
        )
        expected_label = {
            'storage_id': '',
            'resource_type': 'port',
            'resource_id': '123',
            'type': 'RAW',
            'unit': 'IOPS',
            'resource_name': 'port'
        }
        self.assertEqual(metrics[0].name, 'iops')
        self.assertDictEqual(metrics[0].labels, expected_label)
        self.assertListEqual(list(metrics[0].values.values()), [12])

    @mock.patch.object(RestClient, 'get_all_disks')
    @mock.patch.object(RestClient, 'paginated_call')
    @mock.patch.object(RestClient, 'login')
    def test_get_disk_metrics(self, mock_login, mock_call,
                              mock_disks):
        mock_login.return_value = None
        mock_call.return_value = [{'CMO_STATISTIC_DATA_LIST': '12,25',
                                   'CMO_STATISTIC_TIMESTAMP': 0}]
        mock_disks.return_value = [
            {'ID': '123', 'TYPE': '100', 'MODEL': 'disk', 'SERIALNUMBER': '0'}
        ]
        kwargs = ACCESS_INFO
        rest_client = RestClient(**kwargs)
        metrics = rest_client.get_disk_metrics('', {'iops': {'unit': 'IOPS'}})
        mock_call.assert_called_with(
            "/performace_statistic/cur_statistic_data",
            None, 'GET', log_filter_flag=True,
            params='CMO_STATISTIC_UUID=100:123&CMO_STATISTIC_DATA_ID_LIST=22&'
                   'timeConversion=0&'
        )
        expected_label = {
            'storage_id': '',
            'resource_type': 'disk',
            'resource_id': '123',
            'resource_name': 'disk:0',
            'type': 'RAW',
            'unit': 'IOPS',
        }
        self.assertEqual(metrics[0].name, 'iops')
        self.assertDictEqual(metrics[0].labels, expected_label)
        self.assertListEqual(list(metrics[0].values.values()), [12])
