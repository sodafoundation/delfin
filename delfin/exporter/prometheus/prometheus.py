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
import datetime
import glob
import os
import six

from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)

grp = cfg.OptGroup('PROMETHEUS_EXPORTER')
METRICS_CACHE_DIR = '/var/lib/delfin/metrics'
# Metrics file retention time
RETENTION_TIME_SEC = 3600
prometheus_opts = [
    cfg.StrOpt('metrics_dir', default=METRICS_CACHE_DIR,

               help='The temp directory to keep incoming metrics'),
    cfg.StrOpt('timezone',
               default='local',
               help='time zone of prometheus server '
               ),
]
cfg.CONF.register_opts(prometheus_opts, group=grp)

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


class PrometheusExporter(object):

    def __init__(self):
        self.metrics_dir = cfg.CONF.PROMETHEUS_EXPORTER.metrics_dir

    def check_metrics_dir_exists(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            return True
        except Exception as e:
            msg = six.text_type(e)
            LOG.error("Error while creating metrics directory. Reason: %s",
                      msg)
            return False

    # Print metrics in Prometheus format.
    def _write_to_prometheus_format(self, f, metric,
                                    labels, prom_labels, values):
        f.write("# HELP %s  metric for resource %s and instance %s\n"
                % (metric, labels.get('resource_type'),
                   labels.get('resource_id')))
        f.write("# TYPE %s gauge\n" % metric)

        for timestamp, value in values.items():
            f.write("%s{%s} %f %d\n" % (metric, prom_labels,
                                        value, timestamp))

    def get_file_age(self, path):
        # Getting ctime of the file/folder
        # Time will be in seconds
        ctime = os.stat(path).st_ctime
        # Returning the time
        return ctime

    def clean_old_metric_files(self, metrics_dir):
        os.chdir(metrics_dir)
        files = glob.glob("*.prom")
        for file in files:
            file_age = datetime.datetime.now().timestamp() \
                - self.get_file_age(file)
            if file_age >= RETENTION_TIME_SEC:
                LOG.info("Removing metric file %s"
                         " as it crossed the retention period", file)
                os.remove(file)

    def push_to_prometheus(self, storage_metrics):
        if not self.check_metrics_dir_exists(self.metrics_dir):
            return
        try:
            self.clean_old_metric_files(self.metrics_dir)
        except Exception:
            LOG.error('Error while cleaning old metrics files')
        time_stamp = str(datetime.datetime.now().timestamp())
        temp_file_name = os.path.join(self.metrics_dir,
                                      time_stamp + ".prom.temp")
        actual_file_name = os.path.join(self.metrics_dir,
                                        time_stamp + ".prom")
        # make a temp  file with current timestamp
        with open(temp_file_name, "w") as f:
            for metric in storage_metrics:
                name = metric.name
                labels = metric.labels
                values = metric.values
                storage_id = labels.get('storage_id')
                storage_name = labels.get('name')
                storage_sn = labels.get('serial_number')
                resource_type = labels.get('resource_type')
                resource_id = labels.get('resource_id')
                unit = labels.get('unit')
                m_type = labels.get('type', 'RAW')
                value_type = labels.get('value_type', 'gauge')
                prom_labels = (
                    "storage_id=\"%s\","
                    "storage_name=\"%s\","
                    "storage_sn=\"%s\","
                    "resource_type=\"%s\","
                    "resource_id=\"%s\","
                    "type=\"%s\","
                    "unit=\"%s\","
                    "value_type=\"%s\"" %
                    (storage_id, storage_name, storage_sn, resource_type,
                        resource_id,
                        m_type, unit, value_type))
                name = labels.get('resource_type') + '_' + name
                self._write_to_prometheus_format(f, name, labels, prom_labels,
                                                 values)
        # this is done so that the exporter server never see an incomplete file
        try:
            f.close()
            os.renames(temp_file_name, actual_file_name)
            LOG.info('A new metric file %s has been generated',
                     actual_file_name)
        except Exception:
            LOG.error('Error while renaming the temporary metric file')
