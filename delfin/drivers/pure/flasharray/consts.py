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

# The default volume
DEFAULT_CAPACITY = 0

# The default speed
DEFAULT_SPEED = 0

# The default list_alerts time conversion
DEFAULT_LIST_ALERTS_TIME_CONVERSION = 1000

# The default count for the get_volumes_info function
DEFAULT_COUNT_GET_VOLUMES_INFO = 0

# Number of re-logins
RE_LOGIN_TIMES = 3

# Constant one
CONSTANT_ONE = 1
# Constant zero
CONSTANT_ZERO = 0

# Success status code
SUCCESS_STATUS_CODE = 200

# Status code of no permission
PERMISSION_DENIED_STATUS_CODE = 401

# Custom token of Pure
CUSTOM_TOKEN = 'x-next-token'

# The default get_storage model
CONTROLLER_PRIMARY = 'primary'

# Normal value of the controller status
NORMAL_CONTROLLER_STATUS = 'ready'

# disk type
DISK_TYPE_NVRAM = 'NVRAM'

# The account password is incorrect during login.
LOGIN_PASSWORD_ERR = 'invalid credentials'

# list_port: Add ":" to the WWN every 2 sequences.
SPLICE_WWN_SERIAL = 2
SPLICE_WWN_COLON = ':'

SEVERITY_MAP = {'fatal': constants.Severity.FATAL,
                'critical': constants.Severity.CRITICAL,
                'major': constants.Severity.MAJOR,
                'minor': constants.Severity.MINOR,
                'warning': constants.Severity.WARNING,
                'informational': constants.Severity.INFORMATIONAL,
                'NotSpecified': constants.Severity.NOT_SPECIFIED}
CATEGORY_MAP = {'fault': constants.Category.FAULT,
                'event': constants.Category.EVENT,
                'recovery': constants.Category.RECOVERY,
                'notSpecified': constants.Category.NOT_SPECIFIED}
CONTROLLER_STATUS_MAP = {'normal': constants.ControllerStatus.NORMAL,
                         'ok': constants.ControllerStatus.NORMAL,
                         'offline': constants.ControllerStatus.OFFLINE,
                         'not_installed': constants.ControllerStatus.OFFLINE,
                         'fault': constants.ControllerStatus.FAULT,
                         'degraded': constants.ControllerStatus.DEGRADED,
                         'unready': constants.ControllerStatus.UNKNOWN}
DISK_STATUS_MAP = {'normal': constants.DiskStatus.NORMAL,
                   'healthy': constants.DiskStatus.NORMAL,
                   'abnormal': constants.DiskStatus.ABNORMAL,
                   'unhealthy': constants.DiskStatus.ABNORMAL,
                   'offline': constants.DiskStatus.OFFLINE}
PORT_STATUS_MAP = {'ok': constants.PortHealthStatus.NORMAL,
                   'not_installed': constants.PortHealthStatus.ABNORMAL
                   }

PARSE_ALERT_ALERT_ID = '1.3.6.1.2.1.1.3.0'
PARSE_ALERT_STORAGE_NAME = '1.3.6.1.4.1.40482.3.1'
PARSE_ALERT_CONTROLLER_NAME = '1.3.6.1.4.1.40482.3.3'
PARSE_ALERT_ALERT_NAME = '1.3.6.1.4.1.40482.3.5'
PARSE_ALERT_DESCRIPTION = '1.3.6.1.4.1.40482.3.6'
PARSE_ALERT_SEVERITY = '1.3.6.1.4.1.40482.3.7'

PARSE_ALERT_SEVERITY_MAP = {'1': constants.Severity.WARNING,
                            '2': constants.Severity.INFORMATIONAL}

# collect_perf_metrics method
ONE_YEAR_DIFFERENCE = 1000 * 60 * 60 * 24 * 365
NINETY_DAY_DIFFERENCE = 1000 * 60 * 60 * 24 * 90
THIRTY_DAY_DIFFERENCE = 1000 * 60 * 60 * 24 * 30
SEVEN_DAY_DIFFERENCE = 1000 * 60 * 60 * 24 * 7
ONE_DAY_DIFFERENCE = 1000 * 60 * 60 * 24
THREE_HOUR_DIFFERENCE = 1000 * 60 * 60 * 3
ONE_HOUR_DIFFERENCE = 1000 * 60 * 60

ONE_HOUR = '1h'
THREE_HOUR = '3h'
ONE_DAY = '24h'
SEVEN_DAY = '7d'
THIRTY_DAY = '30d'
NINETY_DAY = '90d'
ONE_YEAR = '1y'
AVERAGE_TWO = 2
LIST_METRICS = -1

IOPS_DESCRIPTION = {
    "unit": "IOPS",
    "description": "Input/output operations per second"
}
READ_IOPS_DESCRIPTION = {
    "unit": "IOPS",
    "description": "Read input/output operations per second"
}
WRITE_IOPS_DESCRIPTION = {
    "unit": "IOPS",
    "description": "Write input/output operations per second"
}
THROUGHPUT_DESCRIPTION = {
    "unit": "MB/s",
    "description": "Represents how much data is "
                   "successfully transferred in MB/s"
}
READ_THROUGHPUT_DESCRIPTION = {
    "unit": "MB/s",
    "description": "Represents how much data read is "
                   "successfully transferred in MB/s"
}
WRITE_THROUGHPUT_DESCRIPTION = {
    "unit": "MB/s",
    "description": "Represents how much data write is "
                   "successfully transferred in MB/s"
}
RESPONSE_TIME_DESCRIPTION = {
    "unit": "ms",
    "description": "Average time taken for an IO "
                   "operation in ms"
}
STORAGE_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION,
}
VOLUME_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION,
}

HOST_OS_TYPES_MAP = {
    'linux': constants.HostOSTypes.LINUX,
    'windows': constants.HostOSTypes.WINDOWS,
    'solaris': constants.HostOSTypes.SOLARIS,
    'hp-ux': constants.HostOSTypes.HP_UX,
    'hpux': constants.HostOSTypes.HP_UX,
    'aix': constants.HostOSTypes.AIX,
    'xenserver': constants.HostOSTypes.XEN_SERVER,
    'vmware esx': constants.HostOSTypes.VMWARE_ESX,
    'esxi': constants.HostOSTypes.VMWARE_ESX,
    'linux_vis': constants.HostOSTypes.LINUX_VIS,
    'windows server 2012': constants.HostOSTypes.WINDOWS_SERVER_2012,
    'oracle vm': constants.HostOSTypes.ORACLE_VM,
    'oracle-vm-server': constants.HostOSTypes.ORACLE_VM,
    'open vms': constants.HostOSTypes.OPEN_VMS,
    'vms': constants.HostOSTypes.OPEN_VMS,
    'unknown': constants.HostOSTypes.UNKNOWN
}
