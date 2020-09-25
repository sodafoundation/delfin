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


from delfin.common import constants

""""
The metrics received from driver is should be in this format 
storage_metrics = [Metric(name='response_time',
     labels={'storage_id': '1', 'resource_type': 'array'},
     values={16009988175: 74.10422968341392, 16009988180: 74.10422968341392}),
     Metric(name='throughput',
     labels={'storage_id': '1', 'resource_type': 'array'},
     values={16009988188: 68.57886608255163, 16009988190: 68.57886608255163}),
     Metric(name='read_throughput',
     labels={'storage_id': '1', 'resource_type': 'array'},
     values={1600998817585: 76.60140757331934}),
     Metric(name='write_throughput',
     labels={'storage_id': '1', 'resource_type': 'array'},
     values={1600998817585: 20.264160223426305})]
"""

unit_of_metric = {'response_time': 'ms', 'throughput': 'IOPS',
                  'read_throughput': 'IOPS', 'write_throughput': 'IOPS',
                  'bandwidth': 'MBps', 'read_bandwidth': 'MBps',
                  'write_bandwidth': 'MBps'
                  }


class PrometheusExporter(object):

    # Print metrics in Prometheus format.
    def _write_to_prometheus_format(self, f, metric, labels, values):
        f.write("# HELP storage_%s storage metric for %s\n" % (metric, metric))
        f.write("# TYPE storage_%s gauge\n" % metric)

        for timestamp, value in values.items():
            f.write("storage_%s{%s} %f %d\n" % (metric, labels,
                                                value, timestamp))

    def push_to_prometheus(self, storage_metrics):
        with open(constants.PROMETHEUS_EXPORTER_FILE, "a+") as f:
            for metric in storage_metrics:
                name = metric.name
                labels = metric.labels
                values = metric.values
                storage_id = labels.get('storage_id')
                resource_type = labels.get('resource_type')
                unit = unit_of_metric.get(name)
                value_type = labels.get('value_type', 'gauge')
                storage_labels = (
                        "storage_id=\"%s\",resource_type=\"%s\","
                        "type=\"%s\",unit=\"%s\",value_type=\"%s\"" %
                        (storage_id, resource_type, 'RAW', unit, value_type))

                self._write_to_prometheus_format(f, name, storage_labels,
                                                 values)
