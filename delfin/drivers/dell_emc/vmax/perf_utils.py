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

import time

# minimum interval supported by VMAX
VMAX_PERF_MIN_INTERVAL = 5

ARRAY_METRICS = ["HostIOs",
                 "HostMBWritten",
                 "ReadResponseTime",
                 "HostMBReads",
                 "HostReads",
                 "HostWrites",
                 "WriteResponseTime"
                 ]

VMAX_REST_TARGET_URI_ARRAY_PERF = '/performance/Array/metrics'


def epoch_time_ms_now():
    """Get current time in epoch ms.
    :returns: epoch time in milli seconds
     """
    ms = int(time.time() * 1000)
    return ms


def epoch_time_interval_ago(interval_seconds=VMAX_PERF_MIN_INTERVAL):
    """Get epoch time in milliseconds  before an interval
    :param interval_seconds: interval in seconds
    :returns: epoch time in milliseconds
    """
    return int(epoch_time_ms_now() - (interval_seconds * 1000))


def generate_performance_payload(array, interval, metrics):
    """Generate request payload for VMAX performance POST request
    :param array: symmetrixID
    :param interval: interval in seconds
    :returns: payload dictionary
    """
    return {'symmetrixId': str(array),
            "endDate": epoch_time_ms_now(),
            "startDate": epoch_time_interval_ago(interval),
            "metrics": metrics,
            "dataFormat": "Average"}


def parse_performance_data(response):
    """Parse metrics response to a map
    :param response: response from unispshere REST API
    :returns: map with key as metric name and value as dictionary
        containing {timestamp: value} for a the timestamps available
    """
    metrics_map = {}
    for metrics in response["resultList"]["result"]:
        timestamp = metrics["timestamp"]
        for key, value in metrics.items():
            metrics_map[key] = metrics_map.get(key, {})
            metrics_map[key][timestamp] = value
    return metrics_map


def map_array_perf_metrics_to_delfin_metrics(metrics_value_map):
    """map vmax array performance metrics values  to delfin metrics values
        :param metrics_value_map: metric to values map of vmax metrics
        :returns: map with key as delfin metric name and value as dictionary
            containing {timestamp: value} for a the timestamps available
        """
    # read and write response_time
    read_response_values_dict = metrics_value_map['ReadResponseTime']
    write_response_values_dict = metrics_value_map['WriteResponseTime']
    # response_time_values is sum of read and write response
    response_time_values_dict = {
        x: read_response_values_dict.get(x, 0)
        + write_response_values_dict.get(x, 0) for x in
        set(read_response_values_dict).union(write_response_values_dict)}
    # bandwidth metrics
    read_bandwidth_values_dict = metrics_value_map['HostMBReads']
    write_bandwidth_values_dict = metrics_value_map['HostMBWritten']
    bandwidth_values_dict = {
        x: read_bandwidth_values_dict.get(x, 0)
        + write_bandwidth_values_dict.get(x, 0) for x in
        set(read_bandwidth_values_dict).union(write_bandwidth_values_dict)}
    throughput_values_dict = metrics_value_map['HostIOs']
    read_throughput_values_dict = metrics_value_map['HostReads']
    write_throughput_values_dict = metrics_value_map['HostWrites']
    # map values to delfin metrics spec
    delfin_metrics = {'response_time': response_time_values_dict,
                      'read_bandwidth': read_bandwidth_values_dict,
                      'write_bandwidth': write_bandwidth_values_dict,
                      'throughput': throughput_values_dict,
                      'read_throughput': read_throughput_values_dict,
                      'write_throughput': write_throughput_values_dict,
                      'bandwidth': bandwidth_values_dict}
    return delfin_metrics
