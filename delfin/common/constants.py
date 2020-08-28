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
from pysnmp.entity import config

# The maximum value a signed INT type may have
DB_MAX_INT = 0x7FFFFFFF

# Valid access type supported currently.
ACCESS_TYPE = ['rest', 'ssh']


# Custom fields for Delfin objects
class StorageStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    ABNORMAL = 'abnormal'

    ALL = (NORMAL, OFFLINE, ABNORMAL)


class StoragePoolStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    ABNORMAL = 'abnormal'

    ALL = (NORMAL, OFFLINE, ABNORMAL)


class VolumeStatus(object):
    AVAILABLE = 'available'
    ERROR = 'error'

    ALL = (AVAILABLE, ERROR)


class StorageType(object):
    BLOCK = 'block'
    FILE = 'file'

    ALL = (BLOCK, FILE)


class SyncStatus(object):
    SYNCED = 0


class VolumeType(object):
    THICK = 'thick'
    THIN = 'thin'

    ALL = (THICK, THIN)


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
