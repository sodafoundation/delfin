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

import json
from delfin.common import constants
from kafka import KafkaProducer

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

# metrics and its unit we do support
unit_of_metric = {'response_time': 'ms', 'throughput': 'IOPS',
                  'read_throughput': 'IOPS', 'write_throughput': 'IOPS',
                  'bandwidth': 'MBps', 'read_bandwidth': 'MBps',
                  'write_bandwidth': 'MBps'
                  }
"""


class KafkaExporter(object):

    def push_to_kafka(self, data):
        bootstrap_server = constants.KAFKA_IP + ':' + constants.KAFKA_PORT
        producer = KafkaProducer(
            bootstrap_servers=[bootstrap_server],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'))

        producer.send(constants.KAFKA_TOPIC_NAME, value=data)
