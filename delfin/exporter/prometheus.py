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

metrics_name = ['response_time', 'throughput', 'read_throughput',
                'write_throughput', 'bandwidth', 'read_bandwidth',
                'write_bandwidth']


class PrometheusExporter(object):
    # Print metrics in Prometheus format.
    def _write_to_prometheus_format(self, f, metric, labels, value, timestamp):
        f.write("# HELP storage_%s storage metric for %s\n" % (metric, metric))
        f.write("# TYPE storage_%s gauge\n" % metric)
        for label in labels:
            if label is None:
                f.write("storage_%s %f\n" % (metric, labels[label]))
            else:
                f.write("storage_%s{%s} %f %d\n" % (metric, labels[label],
                                                    value, timestamp))

    def push_to_prometheus(self, storage_metrics):
        f = open("/var/lib/delfin/delfin_exporter.txt", "w+")

        storage_metric = {}
        for metric in storage_metrics:

            storage_id = metric.get('storage_id')
            resource_type = metric.get('resource_type')
            native_port_id = metric.get('native_port_id')
            native_controller_id = metric.get('native_controller_id')
            type = metric.get('type', 'RAW')
            unit = metric.get('unit', 'IOPS')
            value_type = metric.get('value_type', 'gauge')

            storage_labels = (
                    "storage_id=\"%s\",resource_type=\"%s\","
                    "native_port_id=\"%s\",native_controller_id="
                    "\"%s\",type=\"%s\",unit=\"%s\",value_type="
                    "\"%s\"" % (storage_id, resource_type,
                                native_port_id, native_controller_id,
                                type, unit, value_type)
            )

            storage_metric[storage_labels] = storage_labels
            for name in metrics_name:
                for timestamp, value in metric.get(name).items():
                    self._write_to_prometheus_format(f, name, storage_metric,
                                                     value, timestamp)
        f.close()
