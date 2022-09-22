# Copyright 2022 The SODA Authors.
# Copyright (c) 2022 Huawei Technologies Co., Ltd.
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

# Command
ODSP_SH = '/odsp/scripts/odsp_sh.sh'
SYSTEM_QUERY = 'system mgt query'
SYSTEM_VERSION = 'system mgt getversion'
SYSTEM_CPU = 'system mgt getcpuinfo'
POOL_LIST = 'pool mgt getlist'
RAID_LIST = 'raid mgt getlist -p {}'
LUN_LIST = 'lun mgt getlist -p {}'
LUN_QUERY = 'lun mgt query -n {}'
DSU_LIST = 'dsu mgt getlist'
DISK_LIST = 'disk mgt getlist -d {}'
DISK_QUERY = 'disk mgt query -d {}'
HA_STATUS = 'ha mgt getstatus'
CLIENT_INITIATOR_GETLIST = 'client initiator getlist -t all'
CLIENT_LIST = 'client mgt getclientlist'
CLIENT_HOST = 'client host gethostlist'
HOST_GROUP = 'client hostgroup gethglist'
HOST_GROUP_N = 'client hostgroup gethostlist -n {}'
VOLUME_GROUP = 'client lungroup getlglist'
VOLUME_GROUP_N = 'client lungroup getlunlist -n {}'
SHARE_LUN_LIST = 'client mgt getsharelunlist -n {}'
MAPVIEW = 'client mapview getlist'
TARGET_QUERY_PORT_LIST = 'client target queryportlist'
SAS_PORT_LIST = 'system sas getportlist -c {}:{}'

# character
SUCCESSFUL_TAG = 'Command completed successfully.'
FAILED_TAG = 'Command failed.'
UNKNOWN_COMMAND_TAG = 'Unknown command.'
PORT_SUCCESSFUL_TAG = 'Commandcompletedsuccessfully.'
COLON = ':'
LEFT_HALF_BRACKET = '['
AFTER_HALF_BRACKET = 'Version]'
CPU_INFORMATION_BRACKET = 'CPU Information]'
SP = 'SP'
ODSP_MSC_VERSION_KEY = 'ODSP_MSCVersion'
ODSP_DRIVER_VERSION_KEY = 'ODSP_DriverVersion'
PROCESSOR_VENDOR_KEY = 'Processor0Vendor_id'
PROCESSOR_FREQUENCY_KEY = 'Processor0CPUFrequency'
STORAGE_VENDOR = 'MacroSAN'
FIELDS_NAME = 'Name:'
FIELDS_ENABLE = 'enable'
FIELDS_INITIATOR_ALIAS = 'InitiatorAlias:'
FIELDS_INITIATOR_HOST = 'N/A'
FIELDS_HOST_NAME = 'Host Name:'
FIELDS_HOST_NAME_TWO = 'HostName:'
FIELDS_HOST_GROUP_NAME = 'Host Group Name:'
FIELDS_VOLUME_GROUP_NAME = 'LUN Group Name:'
FIELDS_LUN_NAME = 'LUNName:'
FIELDS_MAPVIEW_NAME = 'Mapview Name:'
FIELDS_LINK_STATUS = 'Link Status'
DSU = 'DSU-'
DISK = 'Disk-'
HA_RUNNING_STATUS = 'HARunningStatus'
PORT = 'port'
GBPS = 'Gbps'
MBPS = 'Mbps'
KBPS = 'KBPS'
TIME_PATTERN = '%Y-%m-%d %H:%M:%S'

# regular expression
SYSTEM_CPU_SP_REGULAR = '^\\[SP\\d.* CPU.*]'
SYSTEM_VERSION_SP_REGULAR = '\\[SP\\d.* Version\\]'
TARGET_PORT_REGULAR = 'port\\-\\d\\:\\d\\:\\d$'

# The time limit
TIME_LIMIT = 8

# model
MODEL_REGULAR = '^DiagInfo.*\\.gz$'
MODEL_PATH = '{}/delfin/drivers/macro_san/ms/file/{}{}'
FTP_MODEL_FILE_NAME = '/odsp/ftp/diaginfo/{}'
STORAGE_INFO_REGULAR = '^storage_info.*\\.xls$'
STORAGE_INFO_MODEL_REGULAR = '^MS'
TMP_PATH = '{}/tmp'
TMP_FILE_PATH = '{}/tmp/{}'
FTP_PATH_DIAGINFO = '/odsp/ftp/diaginfo'

# alert
MACRO_SAN_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
OS_PATH = '{}/delfin/drivers/macro_san/ms/file/alert{}'
ALERT_FILE_NAME = 'alarm_history_query.csv.sp'
FTP_ALERT_PATH = '/odsp/log/remote'
YES_FIELDS = '是'
SEVERITY_MAP = {
    'fatal': constants.Severity.FATAL,
    '紧急': constants.Severity.FATAL,
    'critical': constants.Severity.CRITICAL,
    '重要': constants.Severity.MAJOR,
    'major': constants.Severity.MAJOR,
    'minor': constants.Severity.MINOR,
    'warning': constants.Severity.WARNING,
    '警告': constants.Severity.WARNING,
    'informational': constants.Severity.INFORMATIONAL,
    'NotSpecified': constants.Severity.NOT_SPECIFIED
}


class digital_constant(object):
    ZERO_INT = 0
    ONE_INT = 1
    MINUS_ONE_INT = -1
    TWO_INT = 2
    THREE_INT = 3
    FOUR_INT = 4
    FIVE_INT = 5
    SIX_INT = 6
    SEVEN_INT = 7
    TWELVE_INT = 12
    SIXTEEN_INT = 13
    THIRTY_SIX = 36
    SIXTY = 60


STORAGE_STATUS_MAP = {
    'normal': constants.StorageStatus.NORMAL,
    'offline': constants.StorageStatus.OFFLINE,
    'abnormal': constants.StorageStatus.ABNORMAL,
    'takeover': constants.StorageStatus.NORMAL,
    'degraded': constants.StorageStatus.DEGRADED,
    'unknown': constants.StorageStatus.UNKNOWN,
}

LIST_VOLUMES_STATUS_MAP = {
    'normal': constants.StorageStatus.NORMAL,
    'offline': constants.StorageStatus.OFFLINE,
    'abnormal': constants.StorageStatus.ABNORMAL,
    'error': constants.StorageStatus.ABNORMAL,
    'fault': constants.StorageStatus.ABNORMAL,
    'faulty': constants.StorageStatus.ABNORMAL,
    'degraded': constants.StorageStatus.DEGRADED,
    'unknown': constants.StorageStatus.UNKNOWN
}
VOLUME_TYPE_MAP = {
    'disable': constants.VolumeType.THICK,
    'enable': constants.VolumeType.THIN
}


class POOL_STATUS_ABNORMAL(object):
    FAULTY = 'faulty'
    FAULT = 'fault'
    ERROR = 'error'
    ABNORMAL = 'abnormal'
    ALL = (FAULTY, FAULT, ERROR, ABNORMAL)


class POOL_STATUS_NORMAL(object):
    OFFLINE = 'offline'
    NORMAL = 'normal'
    ALL = (OFFLINE, NORMAL)


POOLS_STATUS_MAP = {
    'normal': constants.StoragePoolStatus.NORMAL,
    'offline': constants.StoragePoolStatus.OFFLINE,
    'abnormal': constants.StoragePoolStatus.ABNORMAL,
    'error': constants.StoragePoolStatus.ABNORMAL,
    'fault': constants.StoragePoolStatus.ABNORMAL,
    'faulty': constants.StoragePoolStatus.ABNORMAL,
    'unknown': constants.StoragePoolStatus.UNKNOWN,
    'degraded': constants.StoragePoolStatus.DEGRADED
}

DISK_PHYSICAL_TYPE_MAP = {
    'ssd': constants.DiskPhysicalType.SSD,
    'sata': constants.DiskPhysicalType.SATA,
    'sas': constants.DiskPhysicalType.SAS,
    'nl-ssd': constants.DiskPhysicalType.NL_SSD,
    'fc': constants.DiskPhysicalType.FC,
    'lun': constants.DiskPhysicalType.LUN,
    'ata': constants.DiskPhysicalType.ATA,
    'flash': constants.DiskPhysicalType.FLASH,
    'vmdisk': constants.DiskPhysicalType.VMDISK,
    'nl-sas': constants.DiskPhysicalType.NL_SAS,
    'ssd-card': constants.DiskPhysicalType.SSD_CARD,
    'sas-flash-vp': constants.DiskPhysicalType.SAS_FLASH_VP,
    'unknown': constants.DiskPhysicalType.UNKNOWN
}

DISK_STATUS_MAP = {
    'normal': constants.DiskStatus.NORMAL,
    'abnormal': constants.DiskStatus.ABNORMAL,
    'fault': constants.DiskStatus.ABNORMAL,
    'faulty': constants.DiskStatus.ABNORMAL,
    'degraded': constants.DiskStatus.DEGRADED,
    'offline': constants.DiskStatus.OFFLINE
}

CONTROLLERS_STATUS_MAP = {
    'normal': constants.ControllerStatus.NORMAL,
    'dual--single': constants.ControllerStatus.NORMAL,
    'single-single': constants.ControllerStatus.NORMAL,
    'single': constants.ControllerStatus.NORMAL,
    'offline': constants.ControllerStatus.OFFLINE,
    'absent--poweroff': constants.ControllerStatus.OFFLINE,
    'poweroff': constants.ControllerStatus.OFFLINE,
    'fault': constants.ControllerStatus.FAULT,
    'error': constants.ControllerStatus.FAULT,
    'abnormal': constants.ControllerStatus.FAULT,
    'degraded': constants.ControllerStatus.DEGRADED,
    'double-idle': constants.ControllerStatus.NORMAL,
    'double': constants.ControllerStatus.NORMAL,
    'triple': constants.ControllerStatus.NORMAL,
    'quadruple': constants.ControllerStatus.NORMAL,
    'unknown': constants.ControllerStatus.UNKNOWN
}

PORT_CONNECTION_STATUS_MAP = {
    '1': constants.PortConnectionStatus.CONNECTED,
    '2': constants.PortConnectionStatus.DISCONNECTED,
    'Full-Linkup': constants.PortConnectionStatus.CONNECTED,
    'Linkdown': constants.PortConnectionStatus.DISCONNECTED
}

INITIATOR_TYPE_MAP = {
    'fc': constants.InitiatorType.FC,
    'iscsi': constants.InitiatorType.ISCSI,
    'roce': constants.InitiatorType.NVME_OVER_ROCE,
    'sas': constants.InitiatorType.SAS,
    'nvme-of': constants.InitiatorType.NVME_OVER_FABRIC,
    'unknown': constants.InitiatorType.UNKNOWN
}

INITIATOR_STATUS_MAP = {
    'offline': constants.InitiatorStatus.OFFLINE,
    'online': constants.InitiatorStatus.ONLINE,
    'normal': constants.InitiatorStatus.ONLINE,
    'n/a': constants.InitiatorStatus.UNKNOWN
}

HOST_OS_TYPES_MAP = {
    'linux': constants.HostOSTypes.LINUX,
    'windows': constants.HostOSTypes.WINDOWS,
    'windows2008': constants.HostOSTypes.WINDOWS,
    'solaris': constants.HostOSTypes.SOLARIS,
    'hp-ux': constants.HostOSTypes.HP_UX,
    'hp_unix': constants.HostOSTypes.HP_UX,
    'aix': constants.HostOSTypes.AIX,
    'xenserver': constants.HostOSTypes.XEN_SERVER,
    'vmware esx': constants.HostOSTypes.VMWARE_ESX,
    'esxi': constants.HostOSTypes.VMWARE_ESX,
    'linux_vis': constants.HostOSTypes.LINUX_VIS,
    'windows server 2012': constants.HostOSTypes.WINDOWS_SERVER_2012,
    'windows2012': constants.HostOSTypes.WINDOWS_SERVER_2012,
    'oracle vm': constants.HostOSTypes.ORACLE_VM,
    'open vms': constants.HostOSTypes.OPEN_VMS,
    'vms': constants.HostOSTypes.OPEN_VMS,
    'mac os': constants.HostOSTypes.OPEN_VMS,
    'other': constants.HostOSTypes.UNKNOWN,
    'suse': constants.HostOSTypes.UNKNOWN,
    'unknown': constants.HostOSTypes.UNKNOWN
}


class NORMAL_ALERT(object):
    BATTERY_NORMAL = 'Battery_normal'
    CMOS_BATTERY_NORMAL = 'CMOS_battery_normal'
    EP_XP_ONLINE = 'EP_XP_online'
    FAN_NORMAL = 'FAN_normal'
    HA_RECOVER_SUCCESSFULLY = 'HA_recover_successfully'
    HA_TAKEOVER_SUCCESSFULLY = 'HA_takeover_successfully'
    LUN_NORMAL = 'LUN_normal'
    POWER_SUPPLY_NORMAL = 'Power_supply_normal'
    RAID_NORMAL = 'RAID_normal'
    RAID_REBUILD_START = 'RAID_rebuild_start'
    RAID_REBUILD_SUCCESSFULLY = 'RAID_rebuild_successfully'
    REPLICATION_START = 'Replication_start'
    REPLICATION_SUCCESSFULLY = 'Replication_successfully'
    SNAPSHOT_RESOURCE_EXPAND_SUCCESSFULLY = \
        'Snapshot_resource_expand_successfully'
    TEMPERATURE_NORMAL = 'Temperature_normal'
    VOLTAGE_NORMAL = 'Voltage_normal'
    WRITE_CACHE_DISABLED = 'Write_cache_disabled'
    WRITE_CACHE_FROZEN = 'Write_cache_frozen'
    VOLTAGE_CACHE_FROZEN = 'Voltage_cache_frozen'
    VOLTAGE_CACHE_DISABLED = 'Voltage_cache_disabled'
    SP_POWER_ON = 'SP_power_on'
    SP_POWER_OFF = 'SP_power_off'
    SP_ENGINE_POWER_OFF = 'SP_Engine_power_off'
    EP_XP_OFFLINE = 'EP_XP_offline'
    DISK_PULLOUT_ELECTRIFIED = 'Disk_pullout_electrified'
    ALL = (BATTERY_NORMAL, CMOS_BATTERY_NORMAL, EP_XP_ONLINE, FAN_NORMAL,
           HA_RECOVER_SUCCESSFULLY, HA_TAKEOVER_SUCCESSFULLY, LUN_NORMAL,
           POWER_SUPPLY_NORMAL, RAID_NORMAL, RAID_REBUILD_START,
           RAID_REBUILD_SUCCESSFULLY, REPLICATION_START,
           REPLICATION_SUCCESSFULLY, SNAPSHOT_RESOURCE_EXPAND_SUCCESSFULLY,
           TEMPERATURE_NORMAL, VOLTAGE_NORMAL, WRITE_CACHE_DISABLED,
           WRITE_CACHE_FROZEN, VOLTAGE_CACHE_FROZEN, VOLTAGE_CACHE_DISABLED,
           SP_POWER_ON, SP_POWER_OFF, SP_ENGINE_POWER_OFF, EP_XP_OFFLINE,
           DISK_PULLOUT_ELECTRIFIED)


NORMAL_FIELD = '_normal'
SUCCESSFULLY_FIELD = '_successfully'
START_FIELD = '_start'

ALERT_SEVERITY_MAP = {
    'Battery_absent': constants.Severity.WARNING,
    'Battery_absent_reissue': constants.Severity.WARNING,
    'Battery_expired': constants.Severity.WARNING,
    'Battery_expired_reissue': constants.Severity.WARNING,
    'Battery_failed': constants.Severity.FATAL,
    'Battery_failed_reissue': constants.Severity.FATAL,
    'Battery_will_expire': constants.Severity.WARNING,
    'CMOS_battery_low': constants.Severity.FATAL,
    'CMOS_battery_low_reissue': constants.Severity.FATAL,
    'Disk_failed': constants.Severity.FATAL,
    'Disk_single_link': constants.Severity.MAJOR,
    'Disk_warning': constants.Severity.WARNING,
    'DSU_SSU_inconsistent_link': constants.Severity.MAJOR,
    'EP_XP_disordered_link': constants.Severity.MAJOR,
    'EP_XP_install_unproperly': constants.Severity.FATAL,
    'FAN_absent': constants.Severity.FATAL,
    'FAN_absent_reissue': constants.Severity.FATAL,
    'FAN_failed': constants.Severity.FATAL,
    'FAN_failed_reissue': constants.Severity.FATAL,
    'FC_link_error': constants.Severity.FATAL,
    'HA_heartbeat_lost': constants.Severity.FATAL,
    'HA_recover_failed': constants.Severity.FATAL,
    'HA_self_detect_failure': constants.Severity.FATAL,
    'HA_takeover_failed': constants.Severity.FATAL,
    'HA_takeover': constants.Severity.MAJOR,
    'LUN_faulty': constants.Severity.FATAL,
    'Peer_SP_abnormally': constants.Severity.FATAL,
    'Pool_capacity_has_useup': constants.Severity.WARNING,
    'Pool_capacity_has_warning': constants.Severity.WARNING,
    'Pool_capacity_will_useup': constants.Severity.WARNING,
    'Power_supply_abnormal': constants.Severity.FATAL,
    'Power_supply_abnormal_reissue': constants.Severity.FATAL,
    'Power_supply_absent': constants.Severity.FATAL,
    'Power_supply_absent_reissue': constants.Severity.FATAL,
    'RAID_cannot_rebuild': constants.Severity.WARNING,
    'RAID_degraded': constants.Severity.WARNING,
    'RAID_failed': constants.Severity.FATAL,
    'RAID_faulty': constants.Severity.FATAL,
    'RAID_rebuild_paused_abnormally': constants.Severity.FATAL,
    'Replication_failed': constants.Severity.CRITICAL,
    'SAS_PHY_disabled': constants.Severity.MINOR,
    'Snapshot_point_create_failed': constants.Severity.CRITICAL,
    'Snapshot_point_delete_automatically': constants.Severity.WARNING,
    'Snapshot_resource_expand_failed': constants.Severity.CRITICAL,
    'Snapshot_resource_full': constants.Severity.WARNING,
    'Snapshot_resource_invalid': constants.Severity.WARNING,
    'SP_memory_shrink': constants.Severity.MAJOR,
    'SP_reboot_for_memory_insufficient': constants.Severity.CRITICAL,
    'SSD_life_remaining_warning': constants.Severity.WARNING,
    'SSD_time_remaining_warning': constants.Severity.WARNING,
    'SYS_LUN_Cache_capacity_insufficient': constants.Severity.WARNING,
    'Temperature_critical': constants.Severity.CRITICAL,
    'Temperature_critical_reissue': constants.Severity.CRITICAL,
    'Temperature_warning': constants.Severity.WARNING,
    'Temperature_warning_reissue': constants.Severity.WARNING,
    'ThinLUN_expand_failed': constants.Severity.WARNING,
    'ThinLUN_physical_capacity_usedup': constants.Severity.WARNING,
    'Voltage_critical': constants.Severity.CRITICAL,
    'Voltage_critical_reissue': constants.Severity.CRITICAL,
    'Voltage_warning': constants.Severity.WARNING,
    'Voltage_warning_reissue': constants.Severity.WARNING,
    'SP_power_off': constants.Severity.MAJOR,
    'EP_XP_OFFLINE': constants.Severity.MAJOR,
    'LUN_write_cache_frozen': constants.Severity.MAJOR,
    'Global_write_cache_disabled_automatically': constants.Severity.MAJOR,
}

PARSE_ALERT_ALERT_ID = '1.3.6.1.2.1.1.3.0'
PARSE_ALERT_TIME = '1.3.6.1.2.1.25.1.2'
PARSE_ALERT_STORAGE = '1.3.6.1.4.1.35904.1.2.1.1'
PARSE_ALERT_NAME = '1.3.6.1.4.1.35904.1.2.1.4.1'
PARSE_ALERT_LOCATION = '1.3.6.1.4.1.35904.1.2.1.4.2'
PARSE_ALERT_DESCRIPTION = '1.3.6.1.4.1.35904.1.2.1.4.3'

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
    constants.StorageMetric.CACHE_HIT_RATIO.name: {
        "unit": constants.StorageMetric.CACHE_HIT_RATIO.unit,
        "description": constants.StorageMetric.CACHE_HIT_RATIO.description
    },
    constants.StorageMetric.READ_CACHE_HIT_RATIO.name: {
        "unit": constants.StorageMetric.READ_CACHE_HIT_RATIO.unit,
        "description": constants.StorageMetric.READ_CACHE_HIT_RATIO.description
    },
    constants.StorageMetric.WRITE_CACHE_HIT_RATIO.name: {
        "unit": constants.StorageMetric.WRITE_CACHE_HIT_RATIO.unit,
        "description":
            constants.StorageMetric.WRITE_CACHE_HIT_RATIO.description
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
    constants.VolumeMetric.CACHE_HIT_RATIO.name: {
        "unit": constants.VolumeMetric.CACHE_HIT_RATIO.unit,
        "description": constants.VolumeMetric.CACHE_HIT_RATIO.description
    },
    constants.VolumeMetric.READ_CACHE_HIT_RATIO.name: {
        "unit": constants.VolumeMetric.READ_CACHE_HIT_RATIO.unit,
        "description": constants.VolumeMetric.READ_CACHE_HIT_RATIO.description
    },
    constants.VolumeMetric.WRITE_CACHE_HIT_RATIO.name: {
        "unit": constants.VolumeMetric.WRITE_CACHE_HIT_RATIO.unit,
        "description": constants.VolumeMetric.WRITE_CACHE_HIT_RATIO.description
    }
}

POOL_CAP = {
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
    constants.StoragePoolMetric.CACHE_HIT_RATIO.name: {
        "unit": constants.StoragePoolMetric.CACHE_HIT_RATIO.unit,
        "description": constants.StoragePoolMetric.CACHE_HIT_RATIO.description
    },
    constants.StoragePoolMetric.READ_CACHE_HIT_RATIO.name: {
        "unit": constants.StoragePoolMetric.READ_CACHE_HIT_RATIO.unit,
        "description":
            constants.StoragePoolMetric.READ_CACHE_HIT_RATIO.description
    },
    constants.StoragePoolMetric.WRITE_CACHE_HIT_RATIO.name: {
        "unit": constants.StoragePoolMetric.WRITE_CACHE_HIT_RATIO.unit,
        "description":
            constants.StoragePoolMetric.WRITE_CACHE_HIT_RATIO.description
    }
}

DISK_CAP = {
    constants.DiskMetric.IOPS.name: {
        "unit": constants.DiskMetric.IOPS.unit,
        "description": constants.DiskMetric.IOPS.description
    },
    constants.DiskMetric.READ_IOPS.name: {
        "unit": constants.DiskMetric.READ_IOPS.unit,
        "description": constants.DiskMetric.READ_IOPS.description
    },
    constants.DiskMetric.WRITE_IOPS.name: {
        "unit": constants.DiskMetric.WRITE_IOPS.unit,
        "description": constants.DiskMetric.WRITE_IOPS.description
    },
    constants.DiskMetric.THROUGHPUT.name: {
        "unit": constants.DiskMetric.THROUGHPUT.unit,
        "description": constants.DiskMetric.THROUGHPUT.description
    },
    constants.DiskMetric.READ_THROUGHPUT.name: {
        "unit": constants.DiskMetric.READ_THROUGHPUT.unit,
        "description": constants.DiskMetric.READ_THROUGHPUT.description
    },
    constants.DiskMetric.WRITE_THROUGHPUT.name: {
        "unit": constants.DiskMetric.WRITE_THROUGHPUT.unit,
        "description": constants.DiskMetric.WRITE_THROUGHPUT.description
    },
    constants.DiskMetric.RESPONSE_TIME.name: {
        "unit": constants.DiskMetric.RESPONSE_TIME.unit,
        "description": constants.DiskMetric.RESPONSE_TIME.description
    },
    constants.DiskMetric.READ_RESPONSE_TIME.name: {
        "unit": constants.DiskMetric.READ_RESPONSE_TIME.unit,
        "description": constants.DiskMetric.READ_RESPONSE_TIME.description
    },
    constants.DiskMetric.WRITE_RESPONSE_TIME.name: {
        "unit": constants.DiskMetric.WRITE_RESPONSE_TIME.unit,
        "description": constants.DiskMetric.WRITE_RESPONSE_TIME.description
    },
    constants.DiskMetric.CACHE_HIT_RATIO.name: {
        "unit": constants.DiskMetric.CACHE_HIT_RATIO.unit,
        "description": constants.DiskMetric.CACHE_HIT_RATIO.description
    },
    constants.DiskMetric.READ_CACHE_HIT_RATIO.name: {
        "unit": constants.DiskMetric.READ_CACHE_HIT_RATIO.unit,
        "description": constants.DiskMetric.READ_CACHE_HIT_RATIO.description
    },
    constants.DiskMetric.WRITE_CACHE_HIT_RATIO.name: {
        "unit": constants.DiskMetric.WRITE_CACHE_HIT_RATIO.unit,
        "description": constants.DiskMetric.WRITE_CACHE_HIT_RATIO.description
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
    constants.PortMetric.CACHE_HIT_RATIO.name: {
        "unit": constants.PortMetric.CACHE_HIT_RATIO.unit,
        "description": constants.PortMetric.CACHE_HIT_RATIO.description
    },
    constants.PortMetric.READ_CACHE_HIT_RATIO.name: {
        "unit": constants.PortMetric.READ_CACHE_HIT_RATIO.unit,
        "description": constants.PortMetric.READ_CACHE_HIT_RATIO.description
    },
    constants.PortMetric.WRITE_CACHE_HIT_RATIO.name: {
        "unit": constants.PortMetric.WRITE_CACHE_HIT_RATIO.unit,
        "description": constants.PortMetric.WRITE_CACHE_HIT_RATIO.description
    }
}
FTP_PERF_PATH = '/odsp/log/local/perf'
STRAGE_REGULAR = '^perf_device'
LUN_REGULAR = '^perf_lun'
SASPORT_REGULAR = '^perf_sasport'
ISCSIPORT_REGULAR = '^perf_iscsiport'
FCPORT_REGULAR = '^perf_fciport'
POOL_REGULAR = '^perf_raid'
DISK_REGULAR = '^perf_disk'
SYSTEM_PERFORMANCE_FILE = 'system performance getfilelist'
VERSION_SHOW = 'versionshow'
CSV = '.csv'
SIXTY = 60
ADD_FOLDER = '{}/delfin/drivers/utils/performance_file/macro_san/{}{}{}'
PERF_LUN = 'perf_lun_'
PERF_SP = '_SP'
PERF_SAS_PORT = 'perf_sasport_'
PERF_ISCSI_PORT = 'perf_iscsiport_'
GET_DATE = 'date +%s'
SPECIAL_VERSION = 'Version:'
SAS_PORT = 'sasport'
ISCSI_PORT = 'iscsiport'
FC_PORT = 'fcport'
