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

# CPG's status
STATUS_POOL_NORMAL = 1  # CPG STATUS Normal operation
STATUS_POOL_DEGRADED = 2  # CPG STATUS Degraded state
STATUS_POOL_FAILED = 3  # CPG STATUS Abnormal operation
STATUS_POOL_UNKNOWN = 99  # CPG STATUS Unknown state
# VOLUME's status
STATUS_VOLUME_NORMAL = 1  # VOLUME STATUS Normal operation
STATUS_VOLUME_DEGRADED = 2  # VOLUME STATUS Degraded state
STATUS_VOLUME_FAILED = 3  # VOLUME STATUS Abnormal operation
STATUS_VOLUME_UNKNOWN = 99  # VOLUME STATUS Unknown state
# VOLUME's type
THIN_LUNTYPE = 2  # TPVV 2	• TPVV,
# VOLUME's Compression status
STATUS_COMPRESSION_YES = 1  # Compression is enabled on the volume
# VOLUME's deduplication status
STATUS_DEDUPLICATIONSTATE_YES = 1  # Enables deduplication on the volume
# MIB to Bytes
MiB_TO_Bytes = 1024 * 1024
# Page size per page at default paging
QUERY_PAGE_SIZE = 150
# Connection timeout
LOGIN_SOCKET_TIMEOUT = 4
SOCKET_TIMEOUT = 30
# 403  The client request has an invalid session key.
# The request came from a different IP address
ERROR_SESSION_INVALID_CODE = 403
# 409  Session key is being used.
ERROR_SESSION_IS_BEING_USED_CODE = 409
# http SUCCESS's status
SUCCESS_STATUS_CODES = 200
# session SUCCESS's status
LOGIN_SUCCESS_STATUS_CODES = 201

# alert state enumeration
ALERT_STATE_NEW = 1  # New.
ALERT_STATE_ACKED = 2  # Acknowledged state.
ALERT_STATE_FIXED = 3  # Alert issue fixed.
ALERT_STATE_UNKNOWN = 99  # Unknown state

# alert severity enumeration
ALERT_SEVERITY_CRITICAL = 2
ALERT_SEVERITY_MAJOR = 3
ALERT_SEVERITY_MINOR = 4
ALERT_SEVERITY_DEGRADED = 5
