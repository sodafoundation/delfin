# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from delfin.common import constants

# get_storage function part
GET_STORAGE_NAME = 'show storage-system-name'
GET_STORAGE_VENDOR = 'FUJITSU'
GET_ENCLOSURE_STATUS = 'show enclosure-status'
GET_STORAGE_STATUS = 'show status'
GET_STORAGE_SERIAL_NUMBER = 'show boxid'
GET_STORAGE_FIRMWARE_VERSION = 'show firmware-version'
GET_STORAGE_TOTAL_CAPACITY = 'show storage-cluster-license'
GET_STORAGE_CONTROLLER = 'show fru-ce'
GET_STORAGE_CONTROLLER_STATUS = 'show enclosure-status -type all'
SET_CLIENV_FORCE_UNLOCK = 'set clienv-force-unlock'
FIRMWARE_VERSION_CURRENT_COUNT = 3
FIRMWARE_VERSION_LENGTH = 4
CURRENT = 'Current'
FIRMWARE_VERSION_NUMBER = 1

# list_volume  function part
GET_LIST_VOLUMES = 'show volumes'
GET_LIST_VOLUMES_MODE_UID = 'show volumes -mode uid'
GET_LIST_VOLUMES_TYPE_TPV = 'show volumes -type tpv'
GET_LIST_VOLUMES_TYPE_FTV = 'show volumes -type ftv'
CLI_STR = 'CLI>'
SPECIAL_CHARACTERS_ONE = '^'
SPECIAL_CHARACTERS_TWO = '--'
VOLUME_TYPE_OPEN = 'open'
VOLUME_ID_COUNT = 0
VOLUME_NAME_COUNT = 1
VOLUME_STATUS_COUNT = 2
VOLUME_TYPE_COUNT = 3
NATIVE_STORAGE_POOL_ID_COUNT = 5
TOTAL_CAPACITY_COUNT = 7
DEFAULT_USED_CAPACITY = 0
DEFAULT_FREE_CAPACITY = 0
VOLUMES_CYCLE = 5
VOLUMES_LENGTH = 6

# get_volumes_model function part
GET_VOLUMES_MODEL_VOLUME_ID_COUNT = 0
GET_VOLUMES_MODEL_VOLUME_NAME_COUNT = 1
GET_VOLUMES_MODEL_VOLUME_STATUS_COUNT = 2
GET_VOLUMES_MODEL_POOL_ID_COUNT = 4
GET_VOLUMES_MODEL_TOTAL_CAPACITY_COUNT = 8
GET_VOLUMES_MODEL_WWN_COUNT = 9

# list_storage_pools function part
GET_STORAGE_POOL_CSV = 'show raid-groups -csv'
GET_STORAGE_POOL = 'show raid-groups'
POOL_ID_COUNT = 0
POOL_NAME_COUNT = 1
POOL_STATUS_COUNT = 4
POOL_TOTAL_CAPACITY_COUNT = 5
POOL_FREE_CAPACITY_COUNT = 6
POOL_CYCLE = 5
POOL_LENGTH = 6

GET_DISK_COMMAND = 'show disks -disk all'

# port
GET_PORT_FC_PARAMETERS = 'show fc-parameters'
GET_PORT_FCOE_PARAMETERS = 'show fcoe-parameters'
PORT_NEWLINE_PATTERN = 'CM#\\d.*Port#\\d Information'
DATA_KEY_INDEX = 1
DATA_VALUE_INDEX = 2

CONTROLLER_NEWLINE_PATTERN = 'CM#\\d Information'
COMMON_VALUE_PATTERN = '\\[.*\\]'
SIZE_PATTERN = "\\d+(?:\\.\\d+)?"
POOL_TITLE_PATTERN = "^\\[RAID Group No\\.\\],\\[RAID Group Name"
VOLUME_TITLE_PATTERN = "^\\[Volume No\\.\\],\\[Volume Name]"
CONTROLLER_STATUS_PATTERN = 'Controller Module Status/Status Code'
CONTROLLER_STATUS_NORMAL_KEY = 'Normal'

# list_disk function part
SPECIFIC_CHARACTER_ONE = '['
SPECIFIC_CHARACTER_TWO = ']'

# list_alert function
SHOW_EVENTS_SEVERITY_WARNING = 'show events -severity warning'
SHOW_EVENTS_SEVERITY_ERROR = 'show events -severity error'
SHOW_EVENTS_LEVEL_WARNING = 'show events -level warning'
SHOW_EVENTS_LEVEL_ERROR = 'show events -level error'
OCCUR_TIME_RANGE = 19
SEVERITY_RANGE_BEGIN = 22
SEVERITY_RANGE_END = 34
CODE_RANGE_BEGIN = 38
CODE_RANGE_END = 46
DESCRIPTION_RANGE = 48
TIME_PATTERN = '%Y-%m-%d %H:%M:%S'
ALERT_EXE_TIME = 5
DEFAULT_EXE_TIME = 0.5


class DIGITAL_CONSTANT(object):
    ZERO_INT = 0
    ONE_INT = 1
    MINUS_ONE_INT = -1
    TWO_INT = 2
    THREE_INT = 3
    FIVE_INT = 5
    SIX_INT = 6
    MINUS_SIX_INT = -6
    SEVEN_INT = 7
    THOUSAND_INT = 1000


STORAGE_STATUS_MAP = {'normal': constants.StorageStatus.NORMAL,
                      'offline': constants.StorageStatus.OFFLINE,
                      'abnormal': constants.StorageStatus.ABNORMAL,
                      'degraded': constants.StorageStatus.DEGRADED,
                      'Empty': constants.StorageStatus.OFFLINE,
                      'Normal': constants.StorageStatus.NORMAL,
                      'Pinned Data': constants.StorageStatus.OFFLINE,
                      'Unused': constants.StorageStatus.OFFLINE,
                      'Warning': constants.StorageStatus.OFFLINE,
                      'Maintenance': constants.StorageStatus.ABNORMAL,
                      'Error': constants.StorageStatus.ABNORMAL,
                      'Loop Down': constants.StorageStatus.OFFLINE,
                      'Not Ready': constants.StorageStatus.ABNORMAL,
                      'Subsystem Down': constants.StorageStatus.ABNORMAL,
                      'Change Assigned CM': constants.StorageStatus.ABNORMAL}

STORAGE_POOL_STATUS_MAP = {'Available': constants.StoragePoolStatus.NORMAL,
                           'Spare in Use': constants.StoragePoolStatus.NORMAL,
                           'Readying': constants.StoragePoolStatus.NORMAL,
                           'Rebuild': constants.StoragePoolStatus.NORMAL,
                           'Copyback': constants.StoragePoolStatus.NORMAL,
                           'Redundant Copy':
                               constants.StoragePoolStatus.NORMAL,
                           'Partially Exposed Rebuild':
                               constants.StoragePoolStatus.ABNORMAL,
                           'Exposed Rebuild':
                               constants.StoragePoolStatus.ABNORMAL,
                           'Exposed': constants.StoragePoolStatus.ABNORMAL,
                           'Partially Exposed':
                               constants.StoragePoolStatus.ABNORMAL,
                           'No Disk Path':
                               constants.StoragePoolStatus.ABNORMAL,
                           'SED Locked': constants.StoragePoolStatus.ABNORMAL,
                           'Broken': constants.StoragePoolStatus.ABNORMAL,
                           'Unknown': constants.StoragePoolStatus.UNKNOWN}

LIST_VOLUMES_STATUS_MAP = {
    'normal': constants.StorageStatus.NORMAL,
    'offline': constants.StorageStatus.OFFLINE,
    'abnormal': constants.StorageStatus.ABNORMAL,
    'degraded': constants.StorageStatus.DEGRADED,
    'Available': constants.StorageStatus.NORMAL,
    'Spare in Use': constants.StorageStatus.ABNORMAL,
    'Readying': constants.StorageStatus.ABNORMAL,
    'Rebuild': constants.StorageStatus.ABNORMAL,
    'Copyback': constants.StorageStatus.ABNORMAL,
    'Redundant Copy': constants.StorageStatus.ABNORMAL,
    'Partially Exposed Rebuild': constants.StorageStatus.ABNORMAL,
    'Exposed': constants.StorageStatus.ABNORMAL,
    'Partially Exposed': constants.StorageStatus.ABNORMAL,
    'Not Ready': constants.StorageStatus.ABNORMAL,
    'Broken': constants.StorageStatus.ABNORMAL,
    'Data Lost': constants.StorageStatus.ABNORMAL,
    'Not Available': constants.StorageStatus.OFFLINE,
    'Unknown': constants.StorageStatus.UNKNOWN,
}

SEVERITY_MAP = {
    'Warning': constants.Severity.WARNING,
    'warning': constants.Severity.WARNING,
    'Error': constants.Severity.FATAL,
    'error': constants.Severity.FATAL
}

DiskPhysicalTypeMap = {
    'Nearline': constants.DiskPhysicalType.UNKNOWN,
    'Online': constants.DiskPhysicalType.UNKNOWN,
    'SSD': constants.DiskPhysicalType.SSD,
    'SAS': constants.DiskPhysicalType.SAS,
    'unknown': constants.DiskPhysicalType.UNKNOWN
}

DiskLogicalTypeMap = {
    'Data': constants.DiskLogicalType.MEMBER,
    'Spare': constants.DiskLogicalType.SPARE,
    'unknown': constants.DiskLogicalType.UNKNOWN,
}

DISK_STATUS_MAP = {
    'Available': constants.DiskStatus.NORMAL,
    'Spare': constants.DiskStatus.NORMAL,
    'Present': constants.DiskStatus.NORMAL,
    'Readying': constants.DiskStatus.NORMAL,
    'Rebuild/Copyback': constants.DiskStatus.NORMAL,
    'Copyback': constants.DiskStatus.NORMAL,
    'Rebuild': constants.DiskStatus.NORMAL,
    'Redundant': constants.DiskStatus.NORMAL,
    'Not Supported': constants.DiskStatus.ABNORMAL,
    'Not Exist': constants.DiskStatus.ABNORMAL,
    'Failed Usable': constants.DiskStatus.ABNORMAL,
    'Broken': constants.DiskStatus.NORMAL,
    'Not Available': constants.DiskStatus.ABNORMAL,
    'Formatting': constants.DiskStatus.NORMAL,
    'Not Format': constants.DiskStatus.NORMAL
}

PARSE_ALERT_ALERT_ID = '1.3.6.1.2.1.1.3.0'
PARSE_ALERT_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'
PARSE_ALERT_COMPONENT = '1.3.6.1.4.1.211.1.21.1.150.7.0'
PARSE_ALERT_LOCATION = '1.3.6.1.4.1.211.1.21.1.150.1.1.0'
PARSE_ALERT_DESCRIPTION = '1.3.6.1.4.1.211.1.21.1.150.11.0'

PARSE_ALERT_SEVERITY_MAP = {
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.5': constants.Severity.WARNING,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.2': constants.Severity.FATAL,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.3': constants.Severity.WARNING,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.9': constants.Severity.INFORMATIONAL,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.12': constants.Severity.INFORMATIONAL,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.50': constants.Severity.MINOR,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.51': constants.Severity.WARNING,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.60': constants.Severity.MINOR,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.61': constants.Severity.MINOR,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.62': constants.Severity.MINOR,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.64': constants.Severity.WARNING,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.65': constants.Severity.WARNING,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.66': constants.Severity.INFORMATIONAL,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.67': constants.Severity.MINOR,
    '1.3.6.1.4.1.211.4.1.1.126.1.150.0.68': constants.Severity.MINOR
}

# list_storage_hosts
GET_HOST_WWN_NAMES = 'show host-wwn-names'
GET_HOST_PATH_STATUS = 'show host-path-state'
GET_HOST_ISCSI_NAMES = 'show host-iscsi-names'
GET_HOST_ISCSI_NAMES_NUMBER = 'show host-iscsi-names -host-number {}'
GET_HOST_SAS_ADDRESSES = 'show host-sas-addresses'
HOST_PATH_STATUS_SPECIFIC_ONE = '----'
HOST_ID_COUNT = 0
HOST_NAME_COUNT = 1
HOST_WWN_COUNT = 2
HOST_TYPE_COUNT = 4
HOST_TOTAL = 5
HOST_FC_FIVE = 5
HOST_PATH_STATUS_NAME = 4
HOST_PATH_STATUS = 5
HOST_PATH_STATUS_TOTAL = 6
HOST_ISCSI_NAMES_ZERO = 0
HOST_ISCSI_NAMES_TWO = 2
HOST_ISCSI_NAMES_MINUS_ONE = -1
HOST_ISCSI_NAMES_SEVEN = 7
HOST_ISCSI_SPECIFIC_ONE = '*('
HOST_SAS_ZERO = 0
HOST_SAS_ONE = 1
HOST_SAS_TWO = 2
HOST_SAS_FOUR = 4
HOST_SAS_FIVE = 5
HOST_SAS_SIX = 6

# list_storage_host_groups
GET_HOST_GROUPS_ALL = 'show host-groups -all'
HOST_GROUPS_SPECIFIC_ONE = '<Host List>'
HOST_GROUPS_SPECIFIC_TWO = '----'
HOST_GROUP_ZERO = 0
HOST_GROUP_ONE = 1
HOST_GROUP_TOTAL = 2

# list_volume_groups
GET_LUN_GROUPS = 'show lun-groups'
LUN_GROUPS_SPECIFIC_TWO = '----'
GET_LUN_GROUPS_LG_NUMBER = 'show lun-groups -lg-number {}'
LUN_GROUPS_ID_COUNT = 0
LUN_GROUPS_NAME_COUNT = 1
LUN_VOLUME_ID = 1

# list_masking_views
GET_HOST_AFFINITY_NAME = 'show host-affinity -host-name {}'
GET_PORT_GROUPS = 'show port-groups -all'
GET_MAPPING = 'show mapping'
PORT_GROUP_ARR_LENGTH = 2
PORT_GROUP_ID_NUM = 0
PORT_GROUP_NAME_NUM = 1
HOST_GROUP_NAME_NUM = 3
LUN_GROUP_ID_NUM = 4
LIST_MASKING_VIEWS_VOLUME_ID = 1
PORT_GROUP_ROW_ARR_NUM = 0
PORT_LIST_ROW_ARR_NUM = 1
VIEWS_GROUP_NUM_ZERO = 0
VIEWS_GROUP_ROW_KEY_LENGTH = 4
VIEWS_HOST_ROW_KEY_LENGTH = 3
VIEWS_GROUP_ROW_VALUE_LENGTH = 7
LIST_MASKING_VIEWS_SPECIFIC_ONE = '---'
LIST_MASKING_VIEWS_SPECIFIC_TWO = '<Port List>'
LIST_MASKING_VIEWS_SPECIFIC_FOUR = '<Connection List>'
LIST_MASKING_VIEWS_SPECIFIC_FIVE = 'CM#'
LIST_MASKING_VIEWS_SPECIFIC_SIX = ' (Host'
LIST_MASKING_VIEWS_SPECIFIC_SEVEN = 'LUN  Volume'
VIEWS_REGULAR_SPECIFIC_ONE = '^Port Group'
VIEWS_REGULAR_SPECIFIC_TWO = '^Host'
LIST_MASKING_VIEWS_CONSTANT_ZERO = 0
LIST_MASKING_VIEWS_CONSTANT_TWO = 2
