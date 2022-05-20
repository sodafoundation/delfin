from delfin.common import constants


class AlertOIDNumber(object):
    OID_ERR_ID = '1.3.6.1.3.94.1.11.1.1'
    OID_EVENT_TYPE = '1.3.6.1.3.94.1.11.1.7'
    OID_LAST_TIME = '1.3.6.1.3.94.1.11.1.4'
    OID_EVENT_DESC = '1.3.6.1.3.94.1.11.1.9'
    OID_EVENT_ID = '1.3.6.1.3.94.1.11.1.3'
    OID_SEVERITY = '1.3.6.1.3.94.1.11.1.6'


class StorageVendor(object):
    HPE_MSA_VENDOR = "HPE"


class TrapSeverity(object):
    TRAP_SEVERITY_MAP = {
        '1': 'unknown',
        '2': 'emergency',
        '3': 'alert',
        '4': constants.Severity.CRITICAL,
        '5': 'error',
        '6': constants.Severity.WARNING,
        '7': 'notify',
        '8': constants.Severity.INFORMATIONAL,
        '9': 'debug',
        '10': 'mark'
    }

    SEVERITY_MAP = {
        "warning": "Warning",
        "informational": "Informational",
        "error": "Major"
    }


class SecondsNumber(object):
    SECONDS_TO_MS = 1000


class RpmSpeed(object):
    RPM_SPEED = 1000


class DiskPhysicalType(object):
    DISK_PHYSICAL_TYPE = {
        'fc': constants.DiskPhysicalType.FC,
        'SAS': constants.DiskPhysicalType.SAS
    }


class InitiatorType(object):
    ISCSI_INITIATOR_TYPE = "9"
    FC_INITIATOR_TYPE = "6"
    ISCSI_INITIATOR_DESCRIPTION = constants.InitiatorType.ISCSI
    FC_INITIATOR_DESCRIPTION = constants.InitiatorType.FC
    UNKNOWN_INITIATOR_DESCRIPTION = constants.InitiatorType.UNKNOWN


class HostOSTypes(object):
    MSA_HOST_TYPE = {
        'HP-UX': constants.HostOSTypes.HP_UX
    }
