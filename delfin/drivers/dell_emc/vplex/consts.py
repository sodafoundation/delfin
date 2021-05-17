# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from delfin.common import constants

SOCKET_TIMEOUT = 10
BASE_CONTEXT = '/vplex'
REST_AUTH_URL = '/vplex/clusters'

PORT_TYPE_MAP = {
    'fc': constants.PortType.FC,
    'iscsi': constants.PortType.ISCSI,
    'ficon': constants.PortType.FICON,
    'fcoe': constants.PortType.FCOE,
    'eth': constants.PortType.ETH,
    'sas': constants.PortType.SAS,
    'ib': constants.PortType.IB,
    'other': constants.PortType.OTHER,
}
PORT_LOGICAL_TYPE_MAP = {
    'front-end': constants.PortLogicalType.FRONTEND,
    'back-end': constants.PortLogicalType.BACKEND,
    'service': constants.PortLogicalType.SERVICE,
    'management': constants.PortLogicalType.MANAGEMENT,
    'internal': constants.PortLogicalType.INTERNAL,
    'maintenance': constants.PortLogicalType.MAINTENANCE,
    'inter-director-communication': constants.PortLogicalType.INTERCONNECT,
    'other': constants.PortLogicalType.OTHER,
    'local-com': constants.PortLogicalType.OTHER,
    'wan-com': constants.PortLogicalType.OTHER
}
PORT_CONNECT_STATUS_MAP = {
    'up': constants.PortConnectionStatus.CONNECTED,
    'down': constants.PortConnectionStatus.DISCONNECTED,
    'no-link': constants.PortConnectionStatus.UNKNOWN
}
PORT_HEALTH_STATUS_MAP = {
    'ok': constants.PortHealthStatus.NORMAL,
    'error': constants.PortHealthStatus.ABNORMAL,
    'stopped': constants.PortHealthStatus.UNKNOWN
}
CONTROLLER_STATUS_MAP = {
    "ok": constants.ControllerStatus.NORMAL,
    "busy": constants.ControllerStatus.NORMAL,
    "no contact": constants.ControllerStatus.OFFLINE,
    "lost communication": constants.ControllerStatus.OFFLINE,
    "unknown": constants.ControllerStatus.UNKNOWN
}
