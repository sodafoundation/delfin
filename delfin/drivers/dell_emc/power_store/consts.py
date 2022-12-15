# Copyright 2022 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from delfin.common import constants


class StatusCode(object):
    SUCCESS = 200
    SUCCESS_CREATE_RESPONSE = 201
    SUCCESS_NO_CONTENT = 204
    PARTIAL_CONTENT = 206
    UNAUTHORIZED = 401
    FORBIDDEN = 403


class DigitalConstant(object):
    ZERO = 0
    ONE = 1
    MINUS_ONE = -1
    TWO = 2
    THREE = 3
    FIVE = 5
    SIX = 6
    SIXTY = 60


STORAGE_STATUS_MAP = {
    'Unconfigured': constants.StorageStatus.NORMAL,
    'Unconfigured_Faulted': constants.StorageStatus.ABNORMAL,
    'Configuring': constants.StorageStatus.NORMAL,
    'Core_Initialization': constants.StorageStatus.NORMAL,
    'Configured': constants.StorageStatus.NORMAL,
    'Expanding': constants.StorageStatus.NORMAL,
    'Removing': constants.StorageStatus.NORMAL,
    'Clustering_Failed': constants.StorageStatus.ABNORMAL,
    'Core_Initialization_Failed': constants.StorageStatus.ABNORMAL,
    'Removed': constants.StorageStatus.OFFLINE,
    'Post_Core_Initialization': constants.StorageStatus.NORMAL,
    'Unknown': constants.StorageStatus.UNKNOWN
}

VOLUME_STATUS_MAP = {
    'Ready': constants.StorageStatus.NORMAL,
    'Initializing': constants.StorageStatus.NORMAL,
    'Offline': constants.StorageStatus.OFFLINE,
    'Destroying': constants.StorageStatus.NORMAL
}

VIRTUAL_VOLUME_STATUS_MAP = {
    'Ready': constants.StorageStatus.NORMAL,
    'Not_Ready': constants.StorageStatus.ABNORMAL,
    'Write_Disabled': constants.StorageStatus.ABNORMAL,
    'Mixed': constants.StorageStatus.ABNORMAL,
    'Not_Applicable': constants.StorageStatus.ABNORMAL
}

VOLUME_TYPE_MAP = {
    'Primary': constants.VolumeType.THIN,
    'Clone': constants.VolumeType.THIN
}

DISK_PHYSICAL_TYPE = {
    'SAS_SSD': constants.DiskPhysicalType.SSD,
    'NVMe_SCM': constants.DiskPhysicalType.UNKNOWN,
    'NVMe_SSD': constants.DiskPhysicalType.NVME_SSD,
    'Unknown': constants.DiskPhysicalType.UNKNOWN
}

DISK_STATUS_MAP = {
    'Uninitialized': constants.DiskStatus.NORMAL,
    'Healthy': constants.DiskStatus.NORMAL,
    'Initializing': constants.DiskStatus.NORMAL,
    'Failed': constants.DiskStatus.ABNORMAL,
    'Disconnected': constants.DiskStatus.OFFLINE,
    'Prepare_Failed': constants.DiskStatus.NORMAL,
    'Trigger_Update': constants.DiskStatus.NORMAL
}

CONTROLLER_STATUS_MAP = {
    'Uninitialized': constants.ControllerStatus.NORMAL,
    'Healthy': constants.ControllerStatus.NORMAL,
    'Initializing': constants.ControllerStatus.NORMAL,
    'Failed': constants.ControllerStatus.FAULT,
    'Disconnected': constants.ControllerStatus.OFFLINE,
    'Prepare_Failed': constants.ControllerStatus.NORMAL,
    'Trigger_Update': constants.ControllerStatus.NORMAL
}

PORT_CONNECTION_STATUS_MAP = {
    'true': constants.PortConnectionStatus.CONNECTED,
    True: constants.PortConnectionStatus.CONNECTED,
    'false': constants.PortConnectionStatus.DISCONNECTED,
    False: constants.PortConnectionStatus.DISCONNECTED
}

PORT_HEALTH_STATUS_MAP = {
    'Uninitialized': constants.PortHealthStatus.NORMAL,
    'Healthy': constants.PortHealthStatus.NORMAL,
    'Initializing': constants.PortHealthStatus.NORMAL,
    'Failed': constants.PortHealthStatus.ABNORMAL,
    'Disconnected': constants.PortHealthStatus.NORMAL,
    'Prepare_Failed': constants.PortHealthStatus.NORMAL,
    'Trigger_Update': constants.PortHealthStatus.NORMAL,
    'Empty': constants.PortHealthStatus.UNKNOWN
}

ALERT_SEVERITY_MAP = {
    'Critical': constants.Severity.CRITICAL,
    'Major': constants.Severity.MAJOR,
    'Minor': constants.Severity.MINOR,
    'Info': constants.Severity.INFORMATIONAL,
    'None': constants.Severity.NOT_SPECIFIED,
}

HOST_OS_TYPES_MAP = {
    'Windows': constants.HostOSTypes.WINDOWS,
    'Linux': constants.HostOSTypes.LINUX,
    'ESXi': constants.HostOSTypes.VMWARE_ESX,
    'AIX': constants.HostOSTypes.AIX,
    'HP-UX': constants.HostOSTypes.HP_UX,
    'Solaris': constants.HostOSTypes.SOLARIS
}

INITIATOR_TYPE_MAP = {
    'iSCSI': constants.InitiatorType.ISCSI,
    'FC': constants.InitiatorType.FC,
    'NVMe': constants.InitiatorType.NVME_OVER_FABRIC,
    'NVMe_vVol': constants.InitiatorType.NVME_OVER_FABRIC
}


class DiskType(object):
    NVME_NVRAM = 'NVMe_NVRAM'
    NVME_SCM = 'NVMe_SCM'

    ALL = (NVME_SCM, NVME_NVRAM)


#  /metrics/generate
SPACE_METRICS_BY_APPLIANCE = 'space_metrics_by_appliance'
SPACE_METRICS_BY_VOLUME = 'space_metrics_by_volume'
PERFORMANCE_METRICS_BY_CLUSTER = 'performance_metrics_by_cluster'
PERFORMANCE_METRICS_BY_APPLIANCE = 'performance_metrics_by_appliance'
PERFORMANCE_METRICS_BY_VOLUME = 'performance_metrics_by_volume'
PERFORMANCE_METRICS_BY_NODE = 'performance_metrics_by_node'
PERFORMANCE_METRICS_BY_FE_FC_PORT = 'performance_metrics_by_fe_fc_port'
PERFORMANCE_METRICS_INTERVAL = 'Twenty_Sec'
PERF_INTERVAL = 20

# character
CHARACTER_DRIVE = 'Drive'
CHARACTER_NODE = 'Node'
CHARACTER_SNAPSHOT = 'Snapshot'
CHARACTER_EMPTY = 'Empty'
MGMT_NODE_COREOS = 'Mgmt_Node_CoreOS'
LIMIT_COUNT = 2000
DEFAULT_TIMEOUT = 10

UTC_FORMAT = '%Y-%m-%dT%H:%M:%S.%f+00:00'
SYSTEM_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
PERF_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

PARSE_ALERT_DESCRIPTION = '1.3.6.1.4.1.1139.205.1.1.2'
PARSE_ALERT_CODE = '1.3.6.1.4.1.1139.205.1.1.1'
PARSE_ALERT_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'
PARSE_ALERT_TIME = '1.3.6.1.2.1.1.3.0'
PARSE_ALERT_TIME_UTC = '1.3.6.1.4.1.1139.205.1.1.10'
PARSE_ALERT_UPDATE_TIME_UTC = '1.3.6.1.4.1.1139.205.1.1.9'
PARSE_ALERT_RESOURCE_TYPE = '1.3.6.1.4.1.1139.205.1.1.4'
PARSE_ALERT_RESOURCE_ID = '1.3.6.1.4.1.1139.205.1.1.5'
PARSE_ALERT_RESOURCE_NAME = '1.3.6.1.4.1.1139.205.1.1.6'
PARSE_ALERT_STATE = '1.3.6.1.4.1.1139.205.1.1.7'
PARSE_ALERT_APPLIANCE = '1.3.6.1.4.1.1139.205.1.1.8'

SNMP_SEVERITY_MAP = {
    '1.3.6.1.4.1.1139.205.1.2.1': constants.Severity.CRITICAL,
    '1.3.6.1.4.1.1139.205.1.2.2': constants.Severity.MAJOR,
    '1.3.6.1.4.1.1139.205.1.2.3': constants.Severity.MINOR,
    '1.3.6.1.4.1.1139.205.1.2.4': constants.Severity.INFORMATIONAL
}

STORAGE_CAP = {
    constants.StorageMetric.IOPS.name: {
        "unit": constants.StorageMetric.IOPS.unit,
        "description": constants.StorageMetric.IOPS.description
    },
    constants.StorageMetric.READ_IOPS.name: {
        "unit": constants.StorageMetric.READ_IOPS.unit,
        "description": constants.StorageMetric.READ_IOPS.description
    },
    constants.StorageMetric.WRITE_IOPS.name: {
        "unit": constants.StorageMetric.WRITE_IOPS.unit,
        "description": constants.StorageMetric.WRITE_IOPS.description
    },
    constants.StorageMetric.THROUGHPUT.name: {
        "unit": constants.StorageMetric.THROUGHPUT.unit,
        "description": constants.StorageMetric.THROUGHPUT.description
    },
    constants.StorageMetric.READ_THROUGHPUT.name: {
        "unit": constants.StorageMetric.READ_THROUGHPUT.unit,
        "description": constants.StorageMetric.READ_THROUGHPUT.description
    },
    constants.StorageMetric.WRITE_THROUGHPUT.name: {
        "unit": constants.StorageMetric.WRITE_THROUGHPUT.unit,
        "description": constants.StorageMetric.WRITE_THROUGHPUT.description
    },
    constants.StorageMetric.RESPONSE_TIME.name: {
        "unit": constants.StorageMetric.RESPONSE_TIME.unit,
        "description": constants.StorageMetric.RESPONSE_TIME.description
    },
    constants.StorageMetric.READ_RESPONSE_TIME.name: {
        "unit": constants.StorageMetric.READ_RESPONSE_TIME.unit,
        "description": constants.StorageMetric.READ_RESPONSE_TIME.description
    },
    constants.StorageMetric.WRITE_RESPONSE_TIME.name: {
        "unit": constants.StorageMetric.WRITE_RESPONSE_TIME.unit,
        "description": constants.StorageMetric.WRITE_RESPONSE_TIME.description
    },
    constants.StorageMetric.IO_SIZE.name: {
        "unit": constants.StorageMetric.IO_SIZE.unit,
        "description": constants.StorageMetric.IO_SIZE.description
    },
    constants.StorageMetric.READ_IO_SIZE.name: {
        "unit": constants.StorageMetric.READ_IO_SIZE.unit,
        "description": constants.StorageMetric.READ_IO_SIZE.description
    },
    constants.StorageMetric.WRITE_IO_SIZE.name: {
        "unit": constants.StorageMetric.WRITE_IO_SIZE.unit,
        "description": constants.StorageMetric.WRITE_IO_SIZE.description
    }
}

STORAGE_POOL_CAP = {
    constants.StoragePoolMetric.IOPS.name: {
        "unit": constants.StoragePoolMetric.IOPS.unit,
        "description": constants.StoragePoolMetric.IOPS.description
    },
    constants.StoragePoolMetric.READ_IOPS.name: {
        "unit": constants.StoragePoolMetric.READ_IOPS.unit,
        "description": constants.StoragePoolMetric.READ_IOPS.description
    },
    constants.StoragePoolMetric.WRITE_IOPS.name: {
        "unit": constants.StoragePoolMetric.WRITE_IOPS.unit,
        "description": constants.StoragePoolMetric.WRITE_IOPS.description
    },
    constants.StoragePoolMetric.THROUGHPUT.name: {
        "unit": constants.StoragePoolMetric.THROUGHPUT.unit,
        "description": constants.StoragePoolMetric.THROUGHPUT.description
    },
    constants.StoragePoolMetric.READ_THROUGHPUT.name: {
        "unit": constants.StoragePoolMetric.READ_THROUGHPUT.unit,
        "description": constants.StoragePoolMetric.READ_THROUGHPUT.description
    },
    constants.StoragePoolMetric.WRITE_THROUGHPUT.name: {
        "unit": constants.StoragePoolMetric.WRITE_THROUGHPUT.unit,
        "description": constants.StoragePoolMetric.WRITE_THROUGHPUT.description
    },
    constants.StoragePoolMetric.RESPONSE_TIME.name: {
        "unit": constants.StoragePoolMetric.RESPONSE_TIME.unit,
        "description": constants.StoragePoolMetric.RESPONSE_TIME.description
    },
    constants.StoragePoolMetric.READ_RESPONSE_TIME.name: {
        "unit": constants.StoragePoolMetric.READ_RESPONSE_TIME.unit,
        "description":
            constants.StoragePoolMetric.READ_RESPONSE_TIME.description
    },
    constants.StoragePoolMetric.WRITE_RESPONSE_TIME.name: {
        "unit": constants.StoragePoolMetric.WRITE_RESPONSE_TIME.unit,
        "description":
            constants.StoragePoolMetric.WRITE_RESPONSE_TIME.description
    },
    constants.StoragePoolMetric.IO_SIZE.name: {
        "unit": constants.StoragePoolMetric.IO_SIZE.unit,
        "description": constants.StoragePoolMetric.IO_SIZE.description
    },
    constants.StoragePoolMetric.READ_IO_SIZE.name: {
        "unit": constants.StoragePoolMetric.READ_IO_SIZE.unit,
        "description": constants.StoragePoolMetric.READ_IO_SIZE.description
    },
    constants.StoragePoolMetric.WRITE_IO_SIZE.name: {
        "unit": constants.StoragePoolMetric.WRITE_IO_SIZE.unit,
        "description": constants.StoragePoolMetric.WRITE_IO_SIZE.description
    }
}

VOLUME_CAP = {
    constants.VolumeMetric.IOPS.name: {
        "unit": constants.VolumeMetric.IOPS.unit,
        "description": constants.VolumeMetric.IOPS.description
    },
    constants.VolumeMetric.READ_IOPS.name: {
        "unit": constants.VolumeMetric.READ_IOPS.unit,
        "description": constants.VolumeMetric.READ_IOPS.description
    },
    constants.VolumeMetric.WRITE_IOPS.name: {
        "unit": constants.VolumeMetric.WRITE_IOPS.unit,
        "description": constants.VolumeMetric.WRITE_IOPS.description
    },
    constants.VolumeMetric.THROUGHPUT.name: {
        "unit": constants.VolumeMetric.THROUGHPUT.unit,
        "description": constants.VolumeMetric.THROUGHPUT.description
    },
    constants.VolumeMetric.READ_THROUGHPUT.name: {
        "unit": constants.VolumeMetric.READ_THROUGHPUT.unit,
        "description": constants.VolumeMetric.READ_THROUGHPUT.description
    },
    constants.VolumeMetric.WRITE_THROUGHPUT.name: {
        "unit": constants.VolumeMetric.WRITE_THROUGHPUT.unit,
        "description": constants.VolumeMetric.WRITE_THROUGHPUT.description
    },
    constants.VolumeMetric.RESPONSE_TIME.name: {
        "unit": constants.VolumeMetric.RESPONSE_TIME.unit,
        "description": constants.VolumeMetric.RESPONSE_TIME.description
    },
    constants.VolumeMetric.READ_RESPONSE_TIME.name: {
        "unit": constants.VolumeMetric.READ_RESPONSE_TIME.unit,
        "description": constants.VolumeMetric.READ_RESPONSE_TIME.description
    },
    constants.VolumeMetric.WRITE_RESPONSE_TIME.name: {
        "unit": constants.VolumeMetric.WRITE_RESPONSE_TIME.unit,
        "description": constants.VolumeMetric.WRITE_RESPONSE_TIME.description
    },
    constants.VolumeMetric.IO_SIZE.name: {
        "unit": constants.VolumeMetric.IO_SIZE.unit,
        "description": constants.VolumeMetric.IO_SIZE.description
    },
    constants.VolumeMetric.READ_IO_SIZE.name: {
        "unit": constants.VolumeMetric.READ_IO_SIZE.unit,
        "description": constants.VolumeMetric.READ_IO_SIZE.description
    },
    constants.VolumeMetric.WRITE_IO_SIZE.name: {
        "unit": constants.VolumeMetric.WRITE_IO_SIZE.unit,
        "description": constants.VolumeMetric.WRITE_IO_SIZE.description
    }
}

CONTROLLER_CAP = {
    constants.ControllerMetric.IOPS.name: {
        "unit": constants.ControllerMetric.IOPS.unit,
        "description": constants.ControllerMetric.IOPS.description
    },
    constants.ControllerMetric.READ_IOPS.name: {
        "unit": constants.ControllerMetric.READ_IOPS.unit,
        "description": constants.ControllerMetric.READ_IOPS.description
    },
    constants.ControllerMetric.WRITE_IOPS.name: {
        "unit": constants.ControllerMetric.WRITE_IOPS.unit,
        "description": constants.ControllerMetric.WRITE_IOPS.description
    },
    constants.ControllerMetric.THROUGHPUT.name: {
        "unit": constants.ControllerMetric.THROUGHPUT.unit,
        "description": constants.ControllerMetric.THROUGHPUT.description
    },
    constants.ControllerMetric.READ_THROUGHPUT.name: {
        "unit": constants.ControllerMetric.READ_THROUGHPUT.unit,
        "description": constants.ControllerMetric.READ_THROUGHPUT.description
    },
    constants.ControllerMetric.WRITE_THROUGHPUT.name: {
        "unit": constants.ControllerMetric.WRITE_THROUGHPUT.unit,
        "description": constants.ControllerMetric.WRITE_THROUGHPUT.description
    },
    constants.ControllerMetric.RESPONSE_TIME.name: {
        "unit": constants.ControllerMetric.RESPONSE_TIME.unit,
        "description": constants.ControllerMetric.RESPONSE_TIME.description
    },
    constants.ControllerMetric.READ_RESPONSE_TIME.name: {
        "unit": constants.ControllerMetric.READ_RESPONSE_TIME.unit,
        "description":
            constants.ControllerMetric.READ_RESPONSE_TIME.description
    },
    constants.ControllerMetric.WRITE_RESPONSE_TIME.name: {
        "unit": constants.ControllerMetric.WRITE_RESPONSE_TIME.unit,
        "description":
            constants.ControllerMetric.WRITE_RESPONSE_TIME.description
    },
    constants.ControllerMetric.IO_SIZE.name: {
        "unit": constants.ControllerMetric.IO_SIZE.unit,
        "description": constants.ControllerMetric.IO_SIZE.description
    },
    constants.ControllerMetric.READ_IO_SIZE.name: {
        "unit": constants.ControllerMetric.READ_IO_SIZE.unit,
        "description": constants.ControllerMetric.READ_IO_SIZE.description
    },
    constants.ControllerMetric.WRITE_IO_SIZE.name: {
        "unit": constants.ControllerMetric.WRITE_IO_SIZE.unit,
        "description": constants.ControllerMetric.WRITE_IO_SIZE.description
    },
    constants.ControllerMetric.CPU_USAGE.name: {
        "unit": constants.ControllerMetric.CPU_USAGE.unit,
        "description": constants.ControllerMetric.CPU_USAGE.description
    }
}

PORT_CAP = {
    constants.PortMetric.IOPS.name: {
        "unit": constants.PortMetric.IOPS.unit,
        "description": constants.PortMetric.IOPS.description
    },
    constants.PortMetric.READ_IOPS.name: {
        "unit": constants.PortMetric.READ_IOPS.unit,
        "description": constants.PortMetric.READ_IOPS.description
    },
    constants.PortMetric.WRITE_IOPS.name: {
        "unit": constants.PortMetric.WRITE_IOPS.unit,
        "description": constants.PortMetric.WRITE_IOPS.description
    },
    constants.PortMetric.THROUGHPUT.name: {
        "unit": constants.PortMetric.THROUGHPUT.unit,
        "description": constants.PortMetric.THROUGHPUT.description
    },
    constants.PortMetric.READ_THROUGHPUT.name: {
        "unit": constants.PortMetric.READ_THROUGHPUT.unit,
        "description": constants.PortMetric.READ_THROUGHPUT.description
    },
    constants.PortMetric.WRITE_THROUGHPUT.name: {
        "unit": constants.PortMetric.WRITE_THROUGHPUT.unit,
        "description": constants.PortMetric.WRITE_THROUGHPUT.description
    },
    constants.PortMetric.RESPONSE_TIME.name: {
        "unit": constants.PortMetric.RESPONSE_TIME.unit,
        "description": constants.PortMetric.RESPONSE_TIME.description
    },
    constants.PortMetric.READ_RESPONSE_TIME.name: {
        "unit": constants.PortMetric.READ_RESPONSE_TIME.unit,
        "description": constants.PortMetric.READ_RESPONSE_TIME.description
    },
    constants.PortMetric.WRITE_RESPONSE_TIME.name: {
        "unit": constants.PortMetric.WRITE_RESPONSE_TIME.unit,
        "description": constants.PortMetric.WRITE_RESPONSE_TIME.description
    },
    constants.PortMetric.IO_SIZE.name: {
        "unit": constants.PortMetric.IO_SIZE.unit,
        "description": constants.PortMetric.IO_SIZE.description
    },
    constants.PortMetric.READ_IO_SIZE.name: {
        "unit": constants.PortMetric.READ_IO_SIZE.unit,
        "description": constants.PortMetric.READ_IO_SIZE.description
    },
    constants.PortMetric.WRITE_IO_SIZE.name: {
        "unit": constants.PortMetric.WRITE_IO_SIZE.unit,
        "description": constants.PortMetric.WRITE_IO_SIZE.description
    }
}
