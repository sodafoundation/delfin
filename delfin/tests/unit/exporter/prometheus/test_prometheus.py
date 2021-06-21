# Copyright 2021 The SODA Authors.
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
import glob
import os
from unittest import TestCase

from delfin.exporter.prometheus import prometheus
from delfin.common.constants import metric_struct

fake_metrics = [metric_struct(name='throughput',
                              labels={'storage_id': '12345',
                                      'resource_type': 'storage',
                                      'resource_id': 'storage0',
                                      'type': 'RAW', 'unit': 'MB/s'},
                              values={1622808000000: 61.9388895680357})]


class TestPrometheusExporter(TestCase):

    def test_push_to_prometheus(self):
        prometheus_obj = prometheus.PrometheusExporter()
        prometheus_obj.metrics_dir = os.getcwd()
        prometheus_obj.push_to_prometheus(fake_metrics)
        self.assertTrue(glob.glob(prometheus_obj.metrics_dir + '/' + '*.prom'))
