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
import glob
import os

import six
from flask import Flask
from oslo_config import cfg
import sys
from oslo_log import log

LOG = log.getLogger(__name__)

app = Flask(__name__)

grp = cfg.OptGroup('PROMETHEUS_EXPORTER')
METRICS_CACHE_DIR = '/var/lib/delfin/metrics'
prometheus_opts = [
    cfg.StrOpt('metric_server_ip', default='0.0.0.0',
               help='The exporter server host  ip'),
    cfg.IntOpt('metric_server_port', default=8195,
               help='The exporter server port'),
    cfg.StrOpt('metrics_dir', default=METRICS_CACHE_DIR,

               help='The temp directory to keep incoming metrics'),
]
cfg.CONF.register_opts(prometheus_opts, group=grp)
cfg.CONF(sys.argv[1:])


@app.route("/metrics", methods=['GET'])
def getfile():
    """Read the earliest metric file from the
    available *.prom files
    """
    try:
        if not os.path.exists(cfg.CONF.PROMETHEUS_EXPORTER.metrics_dir):
            LOG.error('No metrics cache folder exists')
            return ''
        os.chdir(cfg.CONF.PROMETHEUS_EXPORTER.metrics_dir)
    except OSError as e:
        LOG.error('Error opening metrics folder')
        raise Exception(e)
    try:
        files = glob.glob("*.prom")
        data = ''
        if files:
            files.sort(key=os.path.getmtime)
            # Read only earliest file in one scrape to /metrics
            file_name = os.path.join(cfg.CONF.PROMETHEUS_EXPORTER.metrics_dir,
                                     files[0])

            with open(file_name, "r") as f:
                data = f.read()
            # Remove a metric file after reading it
            LOG.info('Metric file %s has been read', file_name)
            os.remove(file_name)
            LOG.info('Metric file %s has been deleted', file_name)
    except Exception as e:
        msg = six.text_type(e)
        LOG.error('Error while reading metrics %s', msg)
        return ''

    return data


if __name__ == '__main__':
    app.run(host=cfg.CONF.PROMETHEUS_EXPORTER.metric_server_ip,
            port=cfg.CONF.PROMETHEUS_EXPORTER.metric_server_port)
