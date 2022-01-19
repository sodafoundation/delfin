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


def parse_performance_data(metrics):
    """Parse metrics response to a map
    :param metrics: metrics from unispshere REST API
    :returns: map with key as metric name and value as dictionary
        containing {timestamp: value} for a the timestamps available
    """
    metrics_map = {}
    timestamp = metrics["timestamp"]
    for key, value in metrics.items():
        metrics_map[key] = metrics_map.get(key, {})
        metrics_map[key][timestamp] = value
    return metrics_map


def construct_metrics(storage_id, resource_metrics, unit_map, perf_list):
    metrics_list = []
    for perf in perf_list:
        metrics_values = {}
        collected_metrics_list = perf.get('metrics')
        for collected_metrics in collected_metrics_list:
            metrics_map = parse_performance_data(collected_metrics)

            for key, value in resource_metrics.items():
                metrics_map_value = metrics_map.get(value)
                if metrics_map_value:
                    metrics_values[key] = metrics_values.get(key, {})
                    for k, v in metrics_map_value.items():
                        metrics_values[key][k] = v

        for resource_key, resource_value in metrics_values.items():
            labels = {
                'storage_id': storage_id,
                'resource_type': perf.get('resource_type'),
                'resource_id': perf.get('resource_id'),
                'resource_name': perf.get('resource_name'),
                'type': 'RAW',
                'unit': unit_map[resource_key]['unit']
            }
            metrics_res = constants.metric_struct(name=resource_key,
                                                  labels=labels,
                                                  values=resource_value)
            metrics_list.append(metrics_res)
    return metrics_list
