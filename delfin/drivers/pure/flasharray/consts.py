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
                         'ready': constants.ControllerStatus.NORMAL,
                         'offline': constants.ControllerStatus.OFFLINE,
                         'fault': constants.ControllerStatus.FAULT,
                         'degraded': constants.ControllerStatus.DEGRADED,
                         'unknown': constants.ControllerStatus.UNKNOWN,
                         'unready': constants.ControllerStatus.UNKNOWN}
DISK_STATUS_MAP = {'normal': constants.DiskStatus.NORMAL,
                   'healthy': constants.DiskStatus.NORMAL,
                   'abnormal': constants.DiskStatus.ABNORMAL,
                   'unhealthy': constants.DiskStatus.ABNORMAL,
                   'offline': constants.DiskStatus.OFFLINE}


PARSE_ALERT_ALERT_ID = '1.3.6.1.2.1.1.3.0'
PARSE_ALERT_STORAGE_NAME = '1.3.6.1.4.1.40482.3.1'
PARSE_ALERT_CONTROLLER_NAME = '1.3.6.1.4.1.40482.3.3'
PARSE_ALERT_ALERT_NAME = '1.3.6.1.4.1.40482.3.5'
PARSE_ALERT_DESCRIPTION = '1.3.6.1.4.1.40482.3.6'
PARSE_ALERT_SEVERITY = '1.3.6.1.4.1.40482.3.7'

PARSE_ALERT_SEVERITY_MAP = {'1': constants.Severity.WARNING,
                            '2': constants.Severity.INFORMATIONAL}
