# Copyright 2020 The SODA Authors.
# Copyright 2016 Red Hat, Inc.
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
from collections import namedtuple

from pysnmp.entity import config

# The maximum value a signed INT type may have
DB_MAX_INT = 0x7FFFFFFF

# Valid access type supported currently.
ACCESS_TYPE = ['rest', 'ssh', 'cli', 'smis']


# Custom fields for Delfin objects
class StorageStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    ABNORMAL = 'abnormal'
    DEGRADED = 'degraded'
    UNKNOWN = 'unknown'

    ALL = (NORMAL, OFFLINE, ABNORMAL, DEGRADED, UNKNOWN)


class StoragePoolStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    ABNORMAL = 'abnormal'
    UNKNOWN = 'unknown'

    ALL = (NORMAL, OFFLINE, ABNORMAL, UNKNOWN)


class VolumeStatus(object):
    AVAILABLE = 'available'
    ERROR = 'error'

    ALL = (AVAILABLE, ERROR)


class ControllerStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    FAULT = 'fault'
    DEGRADED = 'degraded'
    UNKNOWN = 'unknown'

    ALL = (NORMAL, OFFLINE, FAULT, DEGRADED, UNKNOWN)


class StorageType(object):
    BLOCK = 'block'
    FILE = 'file'
    UNIFIED = 'unified'

    ALL = (BLOCK, FILE, UNIFIED)


class SyncStatus(object):
    SYNCED = 0


class VolumeType(object):
    THICK = 'thick'
    THIN = 'thin'

    ALL = (THICK, THIN)


class PortConnectionStatus(object):
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    UNKNOWN = 'unknown'

    ALL = (CONNECTED, DISCONNECTED, UNKNOWN)


class PortHealthStatus(object):
    NORMAL = 'normal'
    ABNORMAL = 'abnormal'
    UNKNOWN = 'unknown'

    ALL = (NORMAL, ABNORMAL, UNKNOWN)


class PortType(object):
    FC = 'fc'
    ISCSI = 'iscsi'
    FICON = 'ficon'
    FCOE = 'fcoe'
    ETH = 'eth'
    SAS = 'sas'
    IB = 'ib'
    LOGIC = 'logic'
    CIFS = 'cifs'
    NFS = 'nfs'
    FCACHE = 'fcache'
    COMBO = 'combo'
    CNA = 'cna'
    RCIP = 'rcip'
    NFS_CIFS = 'nfs-cifs'
    OTHER = 'other'

    ALL = (FC, ISCSI, FICON, FCOE, ETH, SAS, IB, LOGIC,
           CIFS, NFS, FCACHE, COMBO, CNA, RCIP, NFS_CIFS, OTHER)


class PortLogicalType(object):
    FRONTEND = 'frontend'
    BACKEND = 'backend'
    SERVICE = 'service'
    MANAGEMENT = 'management'
    INTERNAL = 'internal'
    MAINTENANCE = 'maintenance'
    INTERCONNECT = 'interconnect'
    CLUSTER = 'cluster'
    DATA = 'data'
    NODE_MGMT = 'node-mgmt'
    INTERCLUSTER = 'intercluster'
    CLUSTER_MGMT = 'cluster-mgmt'
    PHYSICAL = 'physical'
    IF_GROUP = 'if-group'
    VLAN = 'vlan'
    OTHER = 'other'

    ALL = (FRONTEND, BACKEND, SERVICE, MANAGEMENT,
           INTERNAL, MAINTENANCE, INTERCONNECT, CLUSTER, DATA, NODE_MGMT,
           INTERCLUSTER, CLUSTER_MGMT, PHYSICAL, IF_GROUP, VLAN, OTHER)


class DiskStatus(object):
    NORMAL = 'normal'
    ABNORMAL = 'abnormal'
    OFFLINE = 'offline'

    ALL = (NORMAL, ABNORMAL, OFFLINE)


class DiskPhysicalType(object):
    SATA = 'sata'
    SAS = 'sas'
    SSD = 'ssd'
    NL_SSD = 'nl-ssd'
    FC = 'fc'
    LUN = 'lun'
    ATA = 'ata'
    FLASH = 'flash'
    VMDISK = 'vmdisk'
    NL_SAS = 'nl-sas'
    SSD_CARD = 'ssd-card'
    SAS_FLASH_VP = 'sas-flash-vp'
    UNKNOWN = 'unknown'

    ALL = (
        SATA, SAS, SSD, NL_SSD, FC, LUN, ATA, FLASH, VMDISK,
        NL_SAS, SSD_CARD, SAS_FLASH_VP, UNKNOWN)


class DiskLogicalType(object):
    FREE = 'free'
    MEMBER = 'member'
    HOTSPARE = 'hotspare'
    CACHE = 'cache'
    AGGREGATE = 'aggregate'
    BROKEN = 'broken'
    FOREIGN = 'foreign'
    LABELMAINT = 'labelmaint'
    MAINTENANCE = 'maintenance'
    SHARED = 'shared'
    SPARE = 'spare'
    UNASSIGNED = 'unassigned'
    UNSUPPORTED = 'unsupported'
    REMOTE = 'remote'
    MEDIATOR = 'mediator'
    UNKNOWN = 'unknown'

    ALL = (FREE, MEMBER, HOTSPARE, CACHE, AGGREGATE, BROKEN, FOREIGN,
           LABELMAINT, MAINTENANCE, SHARED, SPARE, UNASSIGNED, UNSUPPORTED,
           REMOTE, MEDIATOR, UNKNOWN)


class FilesystemStatus(object):
    NORMAL = 'normal'
    FAULTY = 'faulty'

    ALL = (NORMAL, FAULTY)


class WORMType(object):
    NON_WORM = 'non_worm'
    AUDIT_LOG = 'audit_log'
    COMPLIANCE = 'compliance'
    ENTERPRISE = 'enterprise'

    ALL = (NON_WORM, AUDIT_LOG, COMPLIANCE, ENTERPRISE)


class NASSecurityMode(object):
    MIXED = 'mixed'
    NATIVE = 'native'
    NTFS = 'ntfs'
    UNIX = 'unix'

    ALL = (MIXED, NATIVE, NTFS, UNIX)


class QuotaType(object):
    TREE = 'tree'
    USER = 'user'
    GROUP = 'group'

    ALL = (TREE, USER, GROUP)


class FSType(object):
    THICK = 'thick'
    THIN = 'thin'

    ALL = (THICK, THIN)


class ShareProtocol(object):
    CIFS = 'cifs'
    NFS = 'nfs'
    FTP = 'ftp'
    HDFS = 'hdfs'

    ALL = (CIFS, NFS, FTP, HDFS)


class HostStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    ABNORMAL = 'abnormal'
    DEGRADED = 'degraded'

    ALL = (NORMAL, OFFLINE, ABNORMAL, DEGRADED)


class HostOSTypes(object):
    LINUX = 'Linux'
    WINDOWS = 'Windows'
    SOLARIS = 'Solaris'
    HP_UX = 'HP-UX'
    AIX = 'AIX'
    XEN_SERVER = 'XenServer'
    VMWARE_ESX = 'VMware ESX'
    LINUX_VIS = 'LINUX_VIS'
    WINDOWS_SERVER_2012 = 'Windows Server 2012'
    ORACLE_VM = 'Oracle VM'
    OPEN_VMS = 'Open VMS'
    UNKNOWN = 'Unknown'

    ALL = (LINUX, WINDOWS, SOLARIS, HP_UX, AIX, XEN_SERVER, VMWARE_ESX,
           LINUX_VIS, WINDOWS_SERVER_2012, ORACLE_VM, OPEN_VMS, UNKNOWN)


class InitiatorStatus(object):
    ONLINE = 'online'
    OFFLINE = 'offline'
    UNKNOWN = 'unknown'

    ALL = (ONLINE, OFFLINE, UNKNOWN)


class InitiatorType(object):
    FC = 'fc'
    ISCSI = 'iscsi'
    NVME_OVER_ROCE = 'roce'
    SAS = 'sas'
    NVME_OVER_FABRIC = 'nvme-of'
    UNKNOWN = 'unknown'

    ALL = (FC, ISCSI, NVME_OVER_ROCE, SAS, NVME_OVER_FABRIC, UNKNOWN)


# Enumerations for alert severity
class Severity(object):
    FATAL = 'Fatal'
    CRITICAL = 'Critical'
    MAJOR = 'Major'
    MINOR = 'Minor'
    WARNING = 'Warning'
    INFORMATIONAL = 'Informational'
    NOT_SPECIFIED = 'NotSpecified'


# Enumerations for alert category
class Category(object):
    FAULT = 'Fault'
    EVENT = 'Event'
    RECOVERY = 'Recovery'
    NOT_SPECIFIED = 'NotSpecified'


# Enumerations for clear type
class ClearType(object):
    AUTOMATIC = 'Automatic'
    MANUAL = 'Manual'


# Enumerations for alert type based on X.733 Specification
class EventType(object):
    COMMUNICATIONS_ALARM = 'CommunicationsAlarm'
    EQUIPMENT_ALARM = 'EquipmentAlarm'
    PROCESSING_ERROR_ALARM = 'ProcessingErrorAlarm'
    QUALITY_OF_SERVICE_ALARM = 'QualityOfServiceAlarm'
    ENVIRONMENTAL_ALARM = 'EnvironmentalAlarm'
    INTEGRITY_VIOLATION = 'IntegrityViolation'
    OPERATIONAL_VIOLATION = 'OperationalViolation'
    PHYSICAL_VIOLATION = 'PhysicalViolation'
    SECURITY_MECHANISM_VIOLATION = 'SecurityServiceOrMechanismViolation'
    TIME_DOMAIN_VIOLATION = 'TimeDomainViolation'
    NOT_SPECIFIED = 'NotSpecified'


# Default resource type for alert
DEFAULT_RESOURCE_TYPE = 'Storage'

# Default port for connecting to alert source
DEFAULT_SNMP_CONNECT_PORT = 161

# Default retry count for connecting to alert source
DEFAULT_SNMP_RETRY_NUM = 1

# Default expiration time(in sec) for a alert source connect request
DEFAULT_SNMP_EXPIRATION_TIME = 2

# OID used for snmp query, Below oid refers to sysDescr
SNMP_QUERY_OID = '1.3.6.1.2.1.1.1.0'

# Alert id for internal alerts
SNMP_CONNECTION_FAILED_ALERT_ID = '19660818'

# Maps to convert config values to pysnmp values
AUTH_PROTOCOL_MAP = {"hmacsha": config.usmHMACSHAAuthProtocol,
                     "hmacmd5": config.usmHMACMD5AuthProtocol,
                     "hmcsha2224": config.usmHMAC128SHA224AuthProtocol,
                     "hmcsha2256": config.usmHMAC192SHA256AuthProtocol,
                     "hmcsha2384": config.usmHMAC256SHA384AuthProtocol,
                     "hmcsha2512": config.usmHMAC384SHA512AuthProtocol,
                     "none": "None"}

PRIVACY_PROTOCOL_MAP = {"aes": config.usmAesCfb128Protocol,
                        "des": config.usmDESPrivProtocol,
                        "aes192": config.usmAesCfb192Protocol,
                        "aes256": config.usmAesCfb256Protocol,
                        "3des": config.usm3DESEDEPrivProtocol,
                        "none": "None"}


# Enumerations for clear type
class SecurityLevel(object):
    AUTHPRIV = 'authPriv'
    AUTHNOPRIV = 'authNoPriv'
    NOAUTHNOPRIV = 'noAuthnoPriv'


# Performance collection constants and common models
# Metric model
metric_struct = namedtuple("Metric", "name labels values")


class ResourceType(object):
    STORAGE = 'storage'
    STORAGE_POOL = 'storagePool'
    VOLUME = 'volume'
    CONTROLLER = 'controller'
    PORT = 'port'
    DISK = 'disk'
    FILESYSTEM = 'filesystem'
    SHARE = 'share'

    ALL = (STORAGE, STORAGE_POOL, VOLUME, CONTROLLER,
           PORT, DISK, FILESYSTEM, SHARE)


# Unified Array metrics model
DELFIN_ARRAY_METRICS = [
    "responseTime",
    "throughput",
    "readThroughput",
    "writeThroughput",
    "requests",
    "readRequests",
    "writeRequests"
]

BLOCK_SIZE = 4096


class ResourceSync(object):
    START = 100
    SUCCEED = 100
    FAILED = 101


class TelemetryCollection(object):
    """Performance monitoring task name"""
    PERFORMANCE_TASK_METHOD = "delfin.task_manager.scheduler.schedulers." \
                              "telemetry.performance_collection_handler." \
                              "PerformanceCollectionHandler"
    """Failed Performance monitoring job interval"""
    FAILED_JOB_SCHEDULE_INTERVAL = 900
    """Failed Performance monitoring retry count"""
    MAX_FAILED_JOB_RETRY_COUNT = 5
    """Default performance collection interval"""
    DEF_PERFORMANCE_COLLECTION_INTERVAL = 900
    DEF_PERFORMANCE_HISTORY_ON_RESCHEDULE = 1800
    DEF_PERFORMANCE_TIMESTAMP_OVERLAP = 60
    """Maximum failed task retry window in seconds"""
    MAX_FAILED_TASK_RETRY_WINDOW = 7200


class TelemetryTaskStatus(object):
    """Telemetry task enum"""
    TASK_EXEC_STATUS_SUCCESS = True
    TASK_EXEC_STATUS_FAILURE = False


class TelemetryJobStatus(object):
    """Telemetry jobs enum"""
    FAILED_JOB_STATUS_SUCCESS = "Success"
    FAILED_JOB_STATUS_RETRYING = "Retrying"
    FAILED_JOB_STATUS_INIT = "Initialized"
