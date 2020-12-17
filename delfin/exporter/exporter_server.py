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


from flask import Flask
from oslo_config import cfg
import sys

app = Flask(__name__)

grp = cfg.OptGroup('PROMETHEUS_EXPORTER')

prometheus_opts = [
    cfg.StrOpt('metric_server_ip', default='0.0.0.0',
               help='The exporter server host  ip'),
    cfg.IntOpt('metric_server_port', default=8195,
               help='The exporter server port'),
    cfg.StrOpt('metrics_cache_file', default='/var/lib/delfin/delfin_exporter'
                                             '.txt',
               help='The temp cache file used for persisting metrics'),
]
cfg.CONF.register_opts(prometheus_opts, group=grp)
cfg.CONF(sys.argv[1:])


@app.route("/metrics", methods=['GET'])
def getfile():
    with open(cfg.CONF.PROMETHEUS_EXPORTER.metrics_cache_file, "r+") as f:
        data = f.read()
        f.truncate(0)
    return data


if __name__ == '__main__':
    app.run(host=cfg.CONF.PROMETHEUS_EXPORTER.metric_server_ip, port=
    cfg.CONF.PROMETHEUS_EXPORTER.metric_server_port)
