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

DRIVER_SPECIFICATION_SCHEMA = {
    'type': 'object',
    'properties': {
        'is_historic': {'type': 'boolean'},
        'resource_metrics': {
            'type': 'object',
            'properties': {
                'storage': {
                    'type': 'object',
                    'properties': {
                        'throughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'responseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'requests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'memoryUsage': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["%"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                'storagePool': {
                    'type': 'object',
                    'properties': {
                        'throughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'responseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'requests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                'volume': {
                    'type': 'object',
                    'properties': {
                        'throughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'responseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'requests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readResponseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeResponseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                'controller': {
                    'type': 'object',
                    'properties': {
                        'throughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'responseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readResponseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeResponseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'requests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'cpuUsage': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["%"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'memoryUsage': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["%"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                'port': {
                    'type': 'object',
                    'properties': {
                        'throughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'responseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readResponseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeResponseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'requests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeThroughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                'disk': {
                    'type': 'object',
                    'properties': {
                        'throughput': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["MB/s"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'responseTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'requests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'serviceTime': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["ms"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'readRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        'writeRequests': {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string', 'enum': ["IOPS"]},
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
            },
            'additionalProperties': False
        },
    },
    'additionalProperties': False,
    'required': ['is_historic']
}
