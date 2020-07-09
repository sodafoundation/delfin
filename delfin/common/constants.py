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

from enum import IntEnum

# The maximum value a signed INT type may have
DB_MAX_INT = 0x7FFFFFFF


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


class SyncStatus(IntEnum):
    SYNCED = 0


class VolumeType(object):
    THICK = 'thick'
    THIN = 'thin'

    ALL = (THICK, THIN)


class PortType(object):
    FRONT_END = 'front_end'
    BACK_END = 'back_end'
    REPLICATION = 'replication'
    OTHER = 'other'

    ALL = (FRONT_END, BACK_END, REPLICATION, OTHER)


class ControllerType(object):
    FRONT_END = 'front_end'
    BACK_END = 'back_end'
    REPLICATION = 'replication'
    OTHER = 'other'

    ALL = (FRONT_END, BACK_END, REPLICATION, OTHER)


class InterfaceType(object):
    FC = 'fc'
    FICON = 'ficon'
    ESCON = 'escon'
    ISCSI = 'iscsi'
    FCOE = 'fcoe'
    ETHERNET = 'ethernet'
    OTHER = 'other'

    ALL = (FC, FICON, ESCON, ISCSI, FCOE, ETHERNET, OTHER)


class PortStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    UNKNOWN = 'unknown'

    ALL = (NORMAL, OFFLINE, UNKNOWN)


class ControllerStatus(object):
    NORMAL = 'normal'
    OFFLINE = 'offline'
    UNKNOWN = 'unknown'

    ALL = (NORMAL, OFFLINE, UNKNOWN)
