# Copyright 2022 The SODA Authors.
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

StorageVendor = 'DELL EMC'
DEFAULT_TIMEOUT = 10
REST_AUTH_LOGIN = '/api/login'
REST_AUTH_LOGOUT = '/api/logout'
REST_SCALEIO_SYSTEM = '/api/types/System/instances'
REST_SCALEIO_STORAGE_POOL = '/api/types/StoragePool/instances'
REST_SCALEIO_VOLUMES = '/api/types/Volume/instances'
REST_SCALEIO_DISKS = '/api/types/Device/instances'
REST_SCALIO_HOSTS = '/api/types/Sdc/instances'
REST_SCALIO_INITIIATORS = '/api/types/Sds/instances'
REST_SCALEIO_ALERT = '/api/types/Alert/instances'
DEFAULT_ALERTS_TIME_CONVERSION = 1000
DEFAULT_VOLUME_USERD_CAPACITY = 0
DATETIME_UTC_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
OID_SEVERITY = '1139.101.1.1'
OID_EVENT_TYPE = '1139.101.1.2'
OID_ERR_ID = '1139.101.1.3'
OID_EVENT_ID = '1139.101.1.4'

TRAP_ALERT_MAP = {
    '5': constants.Severity.CRITICAL,
    '2': constants.Severity.WARNING,
}
