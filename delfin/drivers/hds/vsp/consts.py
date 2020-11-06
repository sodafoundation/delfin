STATUS_HEALTH = '1'
STATUS_ACTIVE = '43'
STATUS_RUNNING = '10'
STATUS_VOLUME_READY = '27'
STATUS_LUNCOPY_READY = '40'
STATUS_QOS_ACTIVE = '2'
QOS_INACTIVATED = '45'
LUN_TYPE = '11'
SNAPSHOT_TYPE = '27'
STATUS_POOL_ONLINE = 'POLN'
STATUS_STORAGE_NORMAL = '1'

ERROR_CONNECT_TO_SERVER = -403
ERROR_UNAUTHORIZED_TO_SERVER = -401

SOCKET_TIMEOUT = 52
LOGIN_SOCKET_TIMEOUT = 4

# 403  The client request has an invalid session key.
# The request came from a different IP address
ERROR_SESSION_INVALID_CODE = 403
# 409  Session key is being used.
ERROR_SESSION_IS_BEING_USED_CODE = 409
# http SUCCESS's status
SUCCESS_STATUS_CODES = 200
# session SUCCESS's status
LOGIN_SUCCESS_STATUS_CODES = 201

ERROR_VOLUME_NOT_EXIST = 1077939726
RELOGIN_ERROR_PASS = [ERROR_VOLUME_NOT_EXIST]
PWD_EXPIRED = 3
PWD_RESET = 4

BLOCK_STORAGE_POOL_TYPE = '1'
FILE_SYSTEM_POOL_TYPE = '2'

SECTORS_SIZE = 512
QUERY_PAGE_SIZE = 150

THICK_LUNTYPE = '0'
THIN_LUNTYPE = '1'

LOGIN_SOCKET_TIMEOUT = 4
SOCKET_TIMEOUT = 30

# KB to Bytes
KB_TO_Bytes = 1024
# MIB to Bytes
MiB_TO_Bytes = 1024 * 1024
# block size
Block_Size = 512

VSP_MODEL_NOT_USE_SVPIP = 'VSP G350, VSP G370, VSP G700, VSP G900, ' \
                          'VSP F350, VSP F370, VSP F700, VSP F900'


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


class StorageType(object):
    BLOCK = 'block'
    FILE = 'file'

    ALL = (BLOCK, FILE)


class VolumeType(object):
    THICK = 'thick'
    THIN = 'thin'

    ALL = (THICK, THIN)
