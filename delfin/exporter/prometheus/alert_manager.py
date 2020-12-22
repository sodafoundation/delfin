# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
from oslo_config import cfg

CONF = cfg.CONF
alert_mngr_opts = [

    cfg.StrOpt('alert_manager_host', default='localhost',
               help='The prometheus alert manager host'),
    cfg.StrOpt('alert_manager_port', default='9093',
               help='The prometheus alert manager port'),
]

CONF.register_opts(alert_mngr_opts, "PROMETHEUS_ALERT_MANAGER_EXPORTER")
alert_cfg = CONF.PROMETHEUS_ALERT_MANAGER_EXPORTER


class PrometheusAlertExporter(object):
    alerts = []
    model_key = ['alert_id', 'alert_name', 'sequence_number', 'category',
                 'severity', 'type', 'location', 'recovery_advice',
                 'storage_id', 'storage_name', 'vendor',
                 'model', 'serial_number', 'occur_time']

    def push_prometheus_alert(self, alerts):

        host = alert_cfg.alert_manager_host
        port = alert_cfg.alert_manager_port
        for alert in alerts:
            print(alert)
            dict = {}
            dict["labels"] = {}
            dict["annotations"] = {}
            for key in self.model_key:
                dict["labels"][key] = str(alert.get(key))

            dict["annotations"]["summary"] = alert.get("description")

            self.alerts.append(dict)
            requests.post('http://' + host + ":" + port + '/api/v1/alerts',
                          json=self.alerts)
