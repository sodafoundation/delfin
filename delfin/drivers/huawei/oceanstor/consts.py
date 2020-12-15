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

STATUS_HEALTH = '1'
STATUS_ACTIVE = '43'
STATUS_RUNNING = '10'
STATUS_VOLUME_READY = '27'
STATUS_LUNCOPY_READY = '40'
STATUS_QOS_ACTIVE = '2'
QOS_INACTIVATED = '45'
LUN_TYPE = '11'
SNAPSHOT_TYPE = '27'
STATUS_POOL_ONLINE = '27'
STATUS_STORAGE_NORMAL = '1'
STATUS_CTRLR_OFFLINE = '28'
STATUS_CTRLR_UNKNOWN = '0'

PORT_TYPE_FC = 212
PORT_TYPE_ETH = 213
PORT_TYPE_SAS = 214
PORT_TYPE_FCOE = 252
PORT_TYPE_PCIE = 233
PORT_TYPE_BOND = 235

PORT_LOGICTYPE_HOST = '0'
PORT_HEALTH_UNKNOWN = '0'
PORT_HEALTH_NORMAL = '1'
PORT_HEALTH_FAULTY = '2'
PORT_HEALTH_ABOUTFAIL = '3'
PORT_HEALTH_PARTIALLYDAMAGED = '4'
PORT_HEALTH_INCONSISTENT = '9'

PORT_RUNNINGSTS_UNKNOWN = '0'
PORT_RUNNINGSTS_NORMAL = '1'
PORT_RUNNINGSTS_RUNNING = '2'
PORT_RUNNINGSTS_LINKUP = '10'
PORT_RUNNINGSTS_LINKDOWN = '11'
PORT_RUNNINGSTS_TOBERECOVERED = '33'

PORT_LOGICTYPE_HOST = '0'
PORT_LOGICTYPE_EXPANSION = '1'
PORT_LOGICTYPE_MANAGEMENT = '2'
PORT_LOGICTYPE_INTERNAL = '3'
PORT_LOGICTYPE_MAINTENANCE = '4'
PORT_LOGICTYPE_SERVICE = '5'
PORT_LOGICTYPE_MAINTENANCE2 = '6'
PORT_LOGICTYPE_INTERCONNECT = '11'

PortTypeMap = {
    PORT_TYPE_FC: constants.PortType.FC,
    PORT_TYPE_FCOE: constants.PortType.FCOE,
    PORT_TYPE_ETH: constants.PortType.ETH,
    PORT_TYPE_PCIE: constants.PortType.OTHER,
    PORT_TYPE_SAS: constants.PortType.SAS,
    PORT_TYPE_BOND: constants.PortType.OTHER,
}

PortLogicTypeMap = {
    PORT_LOGICTYPE_HOST:
        constants.PortLogicalType.SERVICE,
    PORT_LOGICTYPE_EXPANSION:
        constants.PortLogicalType.OTHER,
    PORT_LOGICTYPE_MANAGEMENT:
        constants.PortLogicalType.MANAGEMENT,
    PORT_LOGICTYPE_INTERNAL:
        constants.PortLogicalType.INTERNAL,
    PORT_LOGICTYPE_MAINTENANCE:
        constants.PortLogicalType.MAINTENANCE,
    PORT_LOGICTYPE_SERVICE:
        constants.PortLogicalType.SERVICE,
    PORT_LOGICTYPE_MAINTENANCE2:
        constants.PortLogicalType.MAINTENANCE,
    PORT_LOGICTYPE_INTERCONNECT:
        constants.PortLogicalType.INTERCONNECT,
}

DISK_STATUS_UNKNOWN = '0'
DISK_STATUS_NORMAL = '1'
DISK_STATUS_OFFLINE = '28'

DISK_TYPE_SAS = '1'
DISK_TYPE_SATA = '2'
DISK_TYPE_SSD = '3'

DISK_LOGICTYPE_FREE = '1'
DISK_LOGICTYPE_MEMBER = '2'
DISK_LOGICTYPE_HOTSPARE = '3'
DISK_LOGICTYPE_CACHE = '4'

DiskPhysicalTypeMap = {
    DISK_TYPE_SATA: constants.DiskPhysicalType.SATA,
    DISK_TYPE_SAS: constants.DiskPhysicalType.SAS,
    DISK_TYPE_SSD: constants.DiskPhysicalType.SSD,
}

DiskLogicalTypeMap = {
    DISK_LOGICTYPE_FREE:
        constants.DiskLogicalType.FREE,
    DISK_LOGICTYPE_MEMBER:
        constants.DiskLogicalType.MEMBER,
    DISK_LOGICTYPE_HOTSPARE:
        constants.DiskLogicalType.HOTSPARE,
    DISK_LOGICTYPE_CACHE:
        constants.DiskLogicalType.CACHE,
}

ERROR_CONNECT_TO_SERVER = -403
ERROR_UNAUTHORIZED_TO_SERVER = -401

SOCKET_TIMEOUT = 52
LOGIN_SOCKET_TIMEOUT = 4

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
