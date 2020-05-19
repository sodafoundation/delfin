#    Copyright 2015 IBM Corp.
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

"""Custom fields for Dolphin objects."""


class StorageStatus(object):
    AVAILABLE = 'available'
    ERROR = 'error'
    IN_USE = 'in-use'

    ALL = (AVAILABLE, ERROR, IN_USE)


class PoolStatus(object):
    AVAILABLE = 'available'
    ERROR = 'error'
    IN_USE = 'in-use'

    ALL = (AVAILABLE, ERROR, IN_USE)


class VolumeStatus(object):
    CREATING = 'creating'
    AVAILABLE = 'available'
    DELETING = 'deleting'
    ERROR = 'error'
    ERROR_DELETING = 'error_deleting'
    IN_USE = 'in-use'
    EXTENDING = 'extending'

    ALL = (CREATING, AVAILABLE, DELETING, ERROR, ERROR_DELETING,
           IN_USE, EXTENDING)


class StorageType(object):
    BLOCK = 'block'
    FILE = 'file'

    ALL = (BLOCK, FILE)
