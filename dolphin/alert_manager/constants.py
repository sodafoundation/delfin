# Copyright 2020 The SODA Authors.
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


# SNMP dispatcher job id (static identifier)
SNMP_DISPATCHER_JOB_ID = 1

# Valid SNMP versions.
SNMP_V1_INT = 1
SNMP_V2_INT = 2
SNMP_V3_INT = 3
VALID_SNMP_VERSIONS = {"snmpv1": SNMP_V1_INT, "snmpv2c": SNMP_V2_INT,
                       "snmpv3": SNMP_V3_INT}

# Default limitation for batch query.
DEFAULT_LIMIT = 1000
