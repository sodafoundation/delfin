# Copyright 2021 The SODA Authors.
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
from delfin import exception
from delfin.common import constants
from delfin.common.constants import ControllerMetric, DiskMetric, PortMetric, \
    VolumeMetric

SOCKET_TIMEOUT = 30
LOGIN_SOCKET_TIMEOUT = 10
CER_ERR = 'Unable to validate the identity of the server'
CALLER_ERR = 'Caller not privileged'
SECURITY_ERR = 'Security file not found'
TRYING_CONNECT_ERR = 'error occurred while trying to connect'
CONNECTION_ERR = 'connection refused'
INVALID_ERR = 'invalid username, password and/or scope'
NOT_SUPPORTED_ERR = 'CLI commands are not supported by the target storage' \
                    ' system'
EXCEPTION_MAP = {CER_ERR: exception.SSLCertificateFailed,
                 CALLER_ERR: exception.InvalidUsernameOrPassword,
                 SECURITY_ERR: exception.InvalidUsernameOrPassword,
                 TRYING_CONNECT_ERR: exception.InvalidIpOrPort,
                 CONNECTION_ERR: exception.InvalidIpOrPort,
                 INVALID_ERR: exception.InvalidUsernameOrPassword,
                 NOT_SUPPORTED_ERR: exception.StorageBackendException}
CER_STORE = '2'
CER_REJECT = '3'
DISK_ID_KEY = 'Bus 0 Enclosure 0  Disk'
LUN_ID_KEY = 'LOGICAL UNIT NUMBER'
LUN_NAME_KEY = 'Name                        '
CER_SEPARATE_KEY = '-----------------------------'
TIME_PATTERN = '%m/%d/%Y %H:%M:%S'
DATE_PATTERN = '%m/%d/%Y'
ONE_DAY_SCE = 24 * 60 * 60
LOG_FILTER_PATTERN = '\\(7[0-7]([a-f]|[0-9]){2}\\)'
NAVISECCLI_API = 'naviseccli -User %(username)s -password %(password)s' \
                 ' -scope 0 -t %(timeout)d -h %(host)s'
CER_ADD_API = 'naviseccli security -certificate -add -file'
CER_LIST_API = 'naviseccli security -certificate -list'
CER_REMOVE_API = 'naviseccli security -certificate -remove'
GET_AGENT_API = 'getagent'
GET_DOMAIN_API = 'domain -list'
GET_STORAGEPOOL_API = 'storagepool -list'
GET_RAIDGROUP_API = 'getrg'
GET_DISK_API = 'getdisk'
GET_LUN_API = 'lun -list'
GET_GETALLLUN_API = 'getall -lun'
GET_SP_API = 'getsp'
GET_PORT_API = 'port -list -sp -all'
GET_BUS_PORT_API = 'backendbus -get -all'
GET_BUS_PORT_STATE_API = 'ioportconfig -list -iomodule basemodule' \
                         ' -portstate -pportid'
GET_ISCSI_PORT_API = 'connection -getport'
GET_IO_PORT_CONFIG_API = 'ioportconfig -list -all'
GET_RESUME_API = 'getresume -all'
GET_LOG_API = 'getlog -date %(begin_time)s %(end_time)s'
EMCVNX_VENDOR = 'DELL EMC'
RAID_GROUP_ID_PREFIX = 'raid_group_'
GET_SG_LIST_HOST_API = 'storagegroup -messner -list -host'
GET_PORT_LIST_HBA_API = 'port -list -hba'
STATUS_MAP = {
    'Ready': constants.StoragePoolStatus.NORMAL,
    'Offline': constants.StoragePoolStatus.OFFLINE,
    'Valid_luns': constants.StoragePoolStatus.NORMAL,
    'Busy': constants.StoragePoolStatus.ABNORMAL,
    'Halted': constants.StoragePoolStatus.ABNORMAL,
    'Defragmenting': constants.StoragePoolStatus.NORMAL,
    'Expanding': constants.StoragePoolStatus.NORMAL,
    'Explicit Remove': constants.StoragePoolStatus.OFFLINE,
    'Invalid': constants.StoragePoolStatus.OFFLINE,
    'Bound': constants.StoragePoolStatus.NORMAL
}
VOL_TYPE_MAP = {'no': constants.VolumeType.THICK,
                'yes': constants.VolumeType.THIN}
VOL_COMPRESSED_MAP = {'no': False,
                      'yes': True}
DEFAULT_QUERY_LOG_DAYS = 9
SECS_OF_TEN_DAYS = DEFAULT_QUERY_LOG_DAYS * ONE_DAY_SCE
OID_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'
OID_MESSAGECODE = '1.3.6.1.4.1.1981.1.4.5'
OID_DETAILS = '1.3.6.1.4.1.1981.1.4.6'
SEVERITY_MAP = {"76": constants.Severity.CRITICAL,
                "75": constants.Severity.MAJOR,
                "74": constants.Severity.MINOR,
                "73": constants.Severity.WARNING,
                "72": constants.Severity.WARNING,
                "77": constants.Severity.FATAL,
                "71": constants.Severity.INFORMATIONAL,
                "70": constants.Severity.INFORMATIONAL}
TRAP_LEVEL_MAP = {'1.3.6.1.4.1.1981.0.6': constants.Severity.CRITICAL,
                  '1.3.6.1.4.1.1981.0.5': constants.Severity.MINOR,
                  '1.3.6.1.4.1.1981.0.4': constants.Severity.WARNING,
                  '1.3.6.1.4.1.1981.0.3': constants.Severity.INFORMATIONAL,
                  '1.3.6.1.4.1.1981.0.2': constants.Severity.INFORMATIONAL
                  }
DISK_STATUS_MAP = {
    'BINDING': constants.DiskStatus.ABNORMAL,
    'ENABLED': constants.DiskStatus.NORMAL,
    'EMPTY': constants.DiskStatus.ABNORMAL,
    'EXPANDING': constants.DiskStatus.ABNORMAL,
    'FORMATTING': constants.DiskStatus.ABNORMAL,
    'OFF': constants.DiskStatus.ABNORMAL,
    'POWERING UP': constants.DiskStatus.ABNORMAL,
    'REBUILDING': constants.DiskStatus.ABNORMAL,
    'REMOVED': constants.DiskStatus.ABNORMAL,
    'UNASSIGNED': constants.DiskStatus.ABNORMAL,
    'UNBOUND': constants.DiskStatus.NORMAL,
    'UNFORMATTED': constants.DiskStatus.ABNORMAL,
    'UNSUPPORTED': constants.DiskStatus.ABNORMAL
}
DISK_PHYSICAL_TYPE_MAP = {
    'SATA': constants.DiskPhysicalType.SATA,
    'SAS': constants.DiskPhysicalType.SAS,
    'SSD': constants.DiskPhysicalType.SSD,
    'NL-SAS': constants.DiskPhysicalType.NL_SAS,
    'NL-SSD': constants.DiskPhysicalType.NL_SSD,
    'FLASH': constants.DiskPhysicalType.FLASH,
    'SAS FLASH VP': constants.DiskPhysicalType.SAS_FLASH_VP,
    'FIBRE CHANNEL': constants.DiskPhysicalType.FC,
    'ATA': constants.DiskPhysicalType.ATA
}
SPPORT_KEY = "Information about each SPPORT:"
PORT_CONNECTION_STATUS_MAP = {
    'UP': constants.PortConnectionStatus.CONNECTED,
    'DOWN': constants.PortConnectionStatus.DISCONNECTED
}
PORT_HEALTH_STATUS_MAP = {
    'ONLINE': constants.PortHealthStatus.NORMAL,
    'DISABLED': constants.PortHealthStatus.ABNORMAL,
    'ENABLED': constants.PortHealthStatus.NORMAL,
    'MISSING': constants.PortHealthStatus.ABNORMAL
}
PORT_TYPE_MAP = {
    'FIBRE': constants.PortType.FC,
    'FCOE': constants.PortType.FCOE,
    'ISCSI': constants.PortType.ISCSI,
    'SAS': constants.PortType.SAS,
    'UNKNOWN': constants.PortType.OTHER
}
INITIATOR_TYPE_MAP = {
    'FC': constants.InitiatorType.FC,
    'FCOE': constants.InitiatorType.FC,
    'ISCSI': constants.InitiatorType.ISCSI,
    'SAS': constants.InitiatorType.SAS,
    'UNKNOWN': constants.InitiatorType.UNKNOWN
}
ALU_PAIRS_PATTERN = '^[0-9]+\\s+[0-9]+$'
HBA_UID_PATTERN = "^\\s*HBA UID\\s+SP Name\\s+SPPort"

CONTROLLER_CAP = {
    ControllerMetric.IOPS.name: {
        "unit": ControllerMetric.IOPS.unit,
        "description": ControllerMetric.IOPS.description
    },
    ControllerMetric.READ_IOPS.name: {
        "unit": ControllerMetric.READ_IOPS.unit,
        "description": ControllerMetric.READ_IOPS.description
    },
    ControllerMetric.WRITE_IOPS.name: {
        "unit": ControllerMetric.WRITE_IOPS.unit,
        "description": ControllerMetric.WRITE_IOPS.description
    },
    ControllerMetric.THROUGHPUT.name: {
        "unit": ControllerMetric.THROUGHPUT.unit,
        "description": ControllerMetric.THROUGHPUT.description
    },
    ControllerMetric.READ_THROUGHPUT.name: {
        "unit": ControllerMetric.READ_THROUGHPUT.unit,
        "description": ControllerMetric.READ_THROUGHPUT.description
    },
    ControllerMetric.WRITE_THROUGHPUT.name: {
        "unit": ControllerMetric.WRITE_THROUGHPUT.unit,
        "description": ControllerMetric.WRITE_THROUGHPUT.description
    },
    ControllerMetric.RESPONSE_TIME.name: {
        "unit": ControllerMetric.RESPONSE_TIME.unit,
        "description": ControllerMetric.RESPONSE_TIME.description
    }
}
VOLUME_CAP = {
    VolumeMetric.IOPS.name: {
        "unit": VolumeMetric.IOPS.unit,
        "description": VolumeMetric.IOPS.description
    },
    VolumeMetric.READ_IOPS.name: {
        "unit": VolumeMetric.READ_IOPS.unit,
        "description": VolumeMetric.READ_IOPS.description
    },
    VolumeMetric.WRITE_IOPS.name: {
        "unit": VolumeMetric.WRITE_IOPS.unit,
        "description": VolumeMetric.WRITE_IOPS.description
    },
    VolumeMetric.THROUGHPUT.name: {
        "unit": VolumeMetric.THROUGHPUT.unit,
        "description": VolumeMetric.THROUGHPUT.description
    },
    VolumeMetric.READ_THROUGHPUT.name: {
        "unit": VolumeMetric.READ_THROUGHPUT.unit,
        "description": VolumeMetric.READ_THROUGHPUT.description
    },
    VolumeMetric.WRITE_THROUGHPUT.name: {
        "unit": VolumeMetric.WRITE_THROUGHPUT.unit,
        "description": VolumeMetric.WRITE_THROUGHPUT.description
    },
    VolumeMetric.RESPONSE_TIME.name: {
        "unit": VolumeMetric.RESPONSE_TIME.unit,
        "description": VolumeMetric.RESPONSE_TIME.description
    },
    VolumeMetric.READ_CACHE_HIT_RATIO.name: {
        "unit": VolumeMetric.READ_CACHE_HIT_RATIO.unit,
        "description": VolumeMetric.READ_CACHE_HIT_RATIO.description
    },
    VolumeMetric.WRITE_CACHE_HIT_RATIO.name: {
        "unit": VolumeMetric.WRITE_CACHE_HIT_RATIO.unit,
        "description": VolumeMetric.WRITE_CACHE_HIT_RATIO.description
    },
    VolumeMetric.READ_IO_SIZE.name: {
        "unit": VolumeMetric.READ_IO_SIZE.unit,
        "description": VolumeMetric.READ_IO_SIZE.description
    },
    VolumeMetric.WRITE_IO_SIZE.name: {
        "unit": VolumeMetric.WRITE_IO_SIZE.unit,
        "description": VolumeMetric.WRITE_IO_SIZE.description
    }
}
PORT_CAP = {
    PortMetric.IOPS.name: {
        "unit": PortMetric.IOPS.unit,
        "description": PortMetric.IOPS.description
    },
    PortMetric.READ_IOPS.name: {
        "unit": PortMetric.READ_IOPS.unit,
        "description": PortMetric.READ_IOPS.description
    },
    PortMetric.WRITE_IOPS.name: {
        "unit": PortMetric.WRITE_IOPS.unit,
        "description": PortMetric.WRITE_IOPS.description
    },
    PortMetric.THROUGHPUT.name: {
        "unit": PortMetric.THROUGHPUT.unit,
        "description": PortMetric.THROUGHPUT.description
    },
    PortMetric.READ_THROUGHPUT.name: {
        "unit": PortMetric.READ_THROUGHPUT.unit,
        "description": PortMetric.READ_THROUGHPUT.description
    },
    PortMetric.WRITE_THROUGHPUT.name: {
        "unit": PortMetric.WRITE_THROUGHPUT.unit,
        "description": PortMetric.WRITE_THROUGHPUT.description
    }
}
DISK_CAP = {
    DiskMetric.IOPS.name: {
        "unit": DiskMetric.IOPS.unit,
        "description": DiskMetric.IOPS.description
    },
    DiskMetric.READ_IOPS.name: {
        "unit": DiskMetric.READ_IOPS.unit,
        "description": DiskMetric.READ_IOPS.description
    },
    DiskMetric.WRITE_IOPS.name: {
        "unit": DiskMetric.WRITE_IOPS.unit,
        "description": DiskMetric.WRITE_IOPS.description
    },
    DiskMetric.THROUGHPUT.name: {
        "unit": DiskMetric.THROUGHPUT.unit,
        "description": DiskMetric.THROUGHPUT.description
    },
    DiskMetric.READ_THROUGHPUT.name: {
        "unit": DiskMetric.READ_THROUGHPUT.unit,
        "description": DiskMetric.READ_THROUGHPUT.description
    },
    DiskMetric.WRITE_THROUGHPUT.name: {
        "unit": DiskMetric.WRITE_THROUGHPUT.unit,
        "description": DiskMetric.WRITE_THROUGHPUT.description
    },
    DiskMetric.RESPONSE_TIME.name: {
        "unit": DiskMetric.RESPONSE_TIME.unit,
        "description": DiskMetric.RESPONSE_TIME.description
    }
}
RESOURCES_TYPE_TO_METRIC_CAP = {
    constants.ResourceType.CONTROLLER: CONTROLLER_CAP,
    constants.ResourceType.PORT: PORT_CAP,
    constants.ResourceType.DISK: DISK_CAP,
    constants.ResourceType.VOLUME: VOLUME_CAP,
}
METRIC_MAP = {
    constants.ResourceType.CONTROLLER: {
        ControllerMetric.IOPS.name: 16,
        ControllerMetric.READ_IOPS.name: 25,
        ControllerMetric.WRITE_IOPS.name: 34,
        ControllerMetric.THROUGHPUT.name: 13,
        ControllerMetric.READ_THROUGHPUT.name: 19,
        ControllerMetric.WRITE_THROUGHPUT.name: 28,
        ControllerMetric.RESPONSE_TIME.name: 10
    },
    constants.ResourceType.PORT: {
        PortMetric.IOPS.name: 16,
        PortMetric.READ_IOPS.name: 25,
        PortMetric.WRITE_IOPS.name: 34,
        PortMetric.THROUGHPUT.name: 13,
        PortMetric.READ_THROUGHPUT.name: 19,
        PortMetric.WRITE_THROUGHPUT.name: 28
    },
    constants.ResourceType.DISK: {
        DiskMetric.IOPS.name: 16,
        DiskMetric.READ_IOPS.name: 25,
        DiskMetric.WRITE_IOPS.name: 34,
        DiskMetric.THROUGHPUT.name: 13,
        DiskMetric.READ_THROUGHPUT.name: 19,
        DiskMetric.WRITE_THROUGHPUT.name: 28,
        DiskMetric.RESPONSE_TIME.name: 10
    },
    constants.ResourceType.VOLUME: {
        VolumeMetric.IOPS.name: 16,
        VolumeMetric.READ_IOPS.name: 25,
        VolumeMetric.WRITE_IOPS.name: 34,
        VolumeMetric.THROUGHPUT.name: 13,
        VolumeMetric.READ_THROUGHPUT.name: 19,
        VolumeMetric.WRITE_THROUGHPUT.name: 28,
        VolumeMetric.RESPONSE_TIME.name: 10,
        VolumeMetric.READ_CACHE_HIT_RATIO.name: 42,
        VolumeMetric.WRITE_CACHE_HIT_RATIO.name: 45,
        VolumeMetric.READ_IO_SIZE.name: 22,
        VolumeMetric.WRITE_IO_SIZE.name: 31
    }
}

ARCHIVE_FILE_NAME = '%s_SPA_%s.nar'
GET_SP_TIME = 'getsptime'
GET_NAR_INTERVAL_API = 'analyzer -get -narinterval'
GET_ARCHIVE_API = 'analyzer -archive -list'
CREATE_ARCHIVE_API = 'analyzer -archiveretrieve -file %s -location %s ' \
                     '-overwrite y -retry 3'
DOWNLOAD_ARCHIVE_API = 'analyzer -archive -file %s -path %s -o'
ARCHIVEDUMP_API = 'analyzer -archivedump -data %s%s -out %s%s.csv'
ARCHIVE_FILE_DIR = "/delfin/drivers/utils/performance_file/vnx_block/"
GET_SP_TIME_PATTERN = '%m/%d/%y %H:%M:%S'
ARCHIVE_FILE_NAME_TIME_PATTERN = '%Y_%m_%d_%H_%M_%S'
# Unit: s
SLEEP_TIME_SECONDS = 60
# Unit: ms
CREATE_FILE_TIME_INTERVAL = 150000
# Unit: ms
EXEC_TIME_INTERVAL = 240000
EXEC_MAX_NUM = 50
# Unit: ms
TIME_INTERVAL_FLUCTUATION = 3000
REPLACE_PATH = "/delfin/drivers/dell_emc/vnx/vnx_block"
# Unit: s
CHECK_WAITE_TIME_SECONDS = 15
COLLECTION_TIME_PATTERN = '%m/%d/%Y %H:%M:00'
