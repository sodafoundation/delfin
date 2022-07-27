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
SYSTEM_QUERY = 'system mgt query'
SYSTEM_VERSION = 'system mgt getversion'
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
VOLUME_GROUP_N = 'client lungroup getlunlist –n {}'
SHARE_LUN_LIST = 'client mgt getsharelunlist -n {}'
MAPVIEW = 'client mapview getlist'
TARGET_QUERY_PORT_LIST = 'client target queryportlist'
SAS_PORT_LIST = 'system sas getportlist -c {}:{}'
EVENT_GETLIST = 'alarm event getlist'

# character
SUCCESSFUL_TAG = 'Command completed successfully.'
FAILED_TAG = 'Command failed.Failed to query ha state!'
UNKNOWN_COMMAND_TAG = 'Unknown command.'
PORT_SUCCESSFUL_TAG = 'Commandcompletedsuccessfully.'
COLON = ':'
LEFT_HALF_BRACKET = '['
AFTER_HALF_BRACKET = 'Version]'
SP_KEY = 'SP1'
SP = 'SP'
ODSP_MSC_VERSION_KEY = 'ODSP_MSCVersion'
STORAGE_VENDOR = 'MacroSAN'
FIELDS_NAME = 'Name:'
FIELDS_EVENT_NAME = 'Event Name:'
FIELDS_INITIATOR_ALIAS = 'InitiatorAlias:'
FIELDS_HOST_NAME = 'Host Name:'
FIELDS_HOST_NAME_TWO = 'HostName:'
FIELDS_HOST_GROUP_NAME = 'Host Group Name:'
FIELDS_VOLUME_GROUP_NAME = 'LUN Group Name:'
FIELDS_LUN_NAME = 'LUNName:'
FIELDS_MAPVIEW_NAME = 'Mapview Name:'
FIELDS_LINK_STATUS = 'Link Status'
DSU = 'DSU-'
DISK = 'Disk-'
SYS = 'SYS-{}'
HA_RUNNING_STATUS = 'HARunningStatus'
PORT = 'port'
GBPS = 'Gbps'
MBPS = 'Mbps'
KBPS = 'KBPS'
TIME_PATTERN = '%Y-%m-%d %H:%M:%S'

# regular expression
SYSTEM_VERSION_SP_REGULAR = '\\[SP\\d Version\\]'
POOL_LIST_NAME_REGULAR = '^Name\\:'
HA_STATUS_SP_REGULAR = '^SP\\d'
TARGET_PORT_REGULAR = 'port\\-\\d\\:\\d\\:\\d$'

# The time limit
TIME_LIMIT = 3


class digital_constant(object):
    ZERO_INT = 0
    ONE_INT = 1
    MINUS_ONE_INT = -1
    TWO_INT = 2
    THREE_INT = 3
    FIVE_INT = 5
    SIX_INT = 6
    THIRTY_SIX = 36


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
    'offline': constants.ControllerStatus.OFFLINE,
    'absent--poweroff': constants.ControllerStatus.FAULT,
    'fault': constants.ControllerStatus.FAULT,
    'error': constants.ControllerStatus.FAULT,
    'abnormal': constants.ControllerStatus.FAULT,
    'degraded': constants.ControllerStatus.DEGRADED,
    'double-idle': constants.ControllerStatus.DEGRADED,
    'unknown': constants.ControllerStatus.UNKNOWN
}

PORT_CONNECTION_STATUS_MAP = {
    '1': constants.PortConnectionStatus.CONNECTED,
    '2': constants.PortConnectionStatus.DISCONNECTED,
    'Full-Linkup': constants.PortConnectionStatus.CONNECTED
}

INITIATOR_TYPE_MAP = {
    'fc': constants.InitiatorType.FC,
    'iscsi': constants.InitiatorType.ISCSI,
    'roce': constants.InitiatorType.NVME_OVER_ROCE,
    'sas': constants.InitiatorType.SAS,
    'nvme-of': constants.InitiatorType.NVME_OVER_FABRIC,
    'unknown': constants.InitiatorType.UNKNOWN
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
    'FC_link_error': constants.Severity.MAJOR,
    'HA_heartbeat_lost': constants.Severity.FATAL,
    'HA_recover_failed': constants.Severity.FATAL,
    'HA_self_detect_failure': constants.Severity.FATAL,
    'HA_takeover_failed': constants.Severity.FATAL,
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
    'RAID_degraded': constants.Severity.FATAL,
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
}

PARSE_ALERT_ALERT_ID = '1.3.6.1.2.1.1.3.0'
PARSE_ALERT_TIME = '1.3.6.1.2.1.25.1.2'
PARSE_ALERT_STORAGE = '1.3.6.1.4.1.35904.1.2.1.1'
PARSE_ALERT_NAME = '1.3.6.1.4.1.35904.1.2.1.4.1'
PARSE_ALERT_LOCATION = '1.3.6.1.4.1.35904.1.2.1.4.2'
PARSE_ALERT_DESCRIPTION = '1.3.6.1.4.1.35904.1.2.1.4.3'
