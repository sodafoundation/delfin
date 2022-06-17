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

from delfin.common.constants import ResourceType, StorageMetric, \
    StoragePoolMetric, VolumeMetric, ControllerMetric, PortMetric, \
    DiskMetric, FileSystemMetric

STORAGE_CAPABILITIES_SCHEMA = {
    'type': 'object',
    'properties': {
        'is_historic': {'type': 'boolean'},
        'performance_metric_retention_window': {'type': 'integer'},
        'resource_metrics': {
            'type': 'object',
            'properties': {
                ResourceType.STORAGE: {
                    'type': 'object',
                    'properties': {
                        StorageMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric.THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric.RESPONSE_TIME
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.READ_RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric
                                                  .READ_RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.WRITE_RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric
                                                  .WRITE_RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric
                                                  .READ_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric
                                                  .WRITE_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric.READ_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StorageMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StorageMetric.WRITE_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },

                    },
                    'additionalProperties': False
                },
                ResourceType.STORAGE_POOL: {
                    'type': 'object',
                    'properties': {
                        StoragePoolMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric
                                                  .THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StoragePoolMetric.RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric
                                                  .RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StoragePoolMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StoragePoolMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric
                                                  .READ_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StoragePoolMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric
                                                  .WRITE_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StoragePoolMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric.READ_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        StoragePoolMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [StoragePoolMetric.WRITE_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                ResourceType.VOLUME: {
                    'type': 'object',
                    'properties': {
                        VolumeMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.RESPONSE_TIME
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.READ_RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric
                                                  .READ_RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.WRITE_RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric
                                                  .WRITE_RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.READ_THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric
                                                  .WRITE_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.READ_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.WRITE_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.CACHE_HIT_RATIO.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.CACHE_HIT_RATIO
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.READ_CACHE_HIT_RATIO.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric
                                                  .READ_CACHE_HIT_RATIO.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.WRITE_CACHE_HIT_RATIO.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric
                                                  .WRITE_CACHE_HIT_RATIO.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.IO_SIZE.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.IO_SIZE.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.READ_IO_SIZE.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.READ_IO_SIZE
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        VolumeMetric.WRITE_IO_SIZE.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [VolumeMetric.WRITE_IO_SIZE
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },

                    },
                    'additionalProperties': False
                },
                ResourceType.CONTROLLER: {
                    'type': 'object',
                    'properties': {
                        ControllerMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric.THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        ControllerMetric.RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric
                                                  .RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        ControllerMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        ControllerMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric
                                                  .READ_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        ControllerMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric
                                                  .WRITE_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        ControllerMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric.READ_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        ControllerMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [ControllerMetric.WRITE_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                ResourceType.PORT: {
                    'type': 'object',
                    'properties': {
                        PortMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        PortMetric.RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.RESPONSE_TIME
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        PortMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        PortMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.READ_THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        PortMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.WRITE_THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        PortMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.READ_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        PortMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [PortMetric.WRITE_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                ResourceType.DISK: {
                    'type': 'object',
                    'properties': {
                        DiskMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        DiskMetric.RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.RESPONSE_TIME
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        DiskMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        DiskMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.READ_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        DiskMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.WRITE_IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        DiskMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.READ_THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        DiskMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [DiskMetric.WRITE_THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                    },
                    'additionalProperties': False
                },
                ResourceType.FILESYSTEM: {
                    'type': 'object',
                    'properties': {
                        FileSystemMetric.THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric.THROUGHPUT
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric.IOPS.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.READ_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric
                                                  .READ_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.WRITE_THROUGHPUT.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric
                                                  .WRITE_THROUGHPUT.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.READ_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric.READ_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.WRITE_IOPS.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric.WRITE_IOPS
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.READ_RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric
                                                  .READ_RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.WRITE_RESPONSE_TIME.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric
                                                  .WRITE_RESPONSE_TIME.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.IO_SIZE.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric.IO_SIZE
                                                  .unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.READ_IO_SIZE.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric
                                                  .READ_IO_SIZE.unit]
                                         },
                                'description': {'type': 'string',
                                                'minLength': 1,
                                                'maxLength': 255}
                            },
                        },
                        FileSystemMetric.WRITE_IO_SIZE.name: {
                            'type': 'object',
                            'properties': {
                                'unit': {'type': 'string',
                                         'enum': [FileSystemMetric
                                                  .WRITE_IO_SIZE.unit]
                                         },
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
