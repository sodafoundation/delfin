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
    """ This enum class  describes the types of port
            based on the purpose it serves
         FRONT_END -  port which is masked to an initiator
         BACK_END -  port which is used to connect  disk enclosures.
         REPLICATION - port which is used to connect  controllers for
            replication purpose.
         OTHER - any port which is not belongs to above categories
            or serves multiple purpose .
    """
    FRONT_END = 'front_end'
    BACK_END = 'back_end'
    REPLICATION = 'replication'
    OTHER = 'other'

    ALL = (FRONT_END, BACK_END, REPLICATION, OTHER)


class ControllerType(object):
    """This enum class  describes the types of controller
            based on the purpose it serves
             FRONT_END -  controller  which has only FRONT_END ports
             BACK_END -  controller  which has only BACK_END ports
             REPLICATION - controller which is used only for
                replication purpose.
             OTHER - any controller  which is not belongs to above categories
                or serves multiple purpose .
        """
    FRONT_END = 'front_end'
    BACK_END = 'back_end'
    REPLICATION = 'replication'
    OTHER = 'other'

    ALL = (FRONT_END, BACK_END, REPLICATION, OTHER)


class InterfaceType(object):
    """This is enum class  describes the types of interface/module
     FC - Fibre Channel Protocol
     FICON -  is the IBM proprietary
        name Fibre Channel protocol
     ESCON - is a data connection created by IBM,
        and is commonly used to connect their mainframe computers.
     ISCSI - an Internet Protocol-based storage
        networking standard for linking data storage facilities.
     FCOE - is a computer network
        technology that encapsulates Fibre Channel
        frames over Ethernet networks.
     ETHERNET - local area network (LAN) using
        Ethernet as the transmission mechanism.
    """
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
