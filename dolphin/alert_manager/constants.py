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


# Default values for trap receiver ip address and port
DEF_TRAP_RECV_ADDR = "0.0.0.0"
DEF_TRAP_RECV_PORT = 162
TRAP_RECEIVER_CLASS = "dolphin.alert_manager.trap_receiver.TrapReceiver"

# Temporary snmp community and user configurations
SNMP_COMMUNITY_STR="public"
SNMP_USM_USER="test1"
SNMP_V3_AUTHKEY="abcd123456"
SNMP_V3_PRIVKEY="abcd123456"
SNMP_V3_AUTH_PROTOCOL="usmHMACMD5AuthProtocol"
SNMP_V3_PRIV_PROTOCOL="usmDESPrivProtocol"
SNMP_ENGINE_ID="800000d30300000e112245"

# Temporary mib lod dir. This mechanism to be changed later
SNMP_MIB_PATH = '/usr/local/lib/python3.6/dist-packages/pysnmp/smi/mibs'

# SNMP dispatcher job id (static identifier)
SNMP_DISPATCHER_JOB_ID = 1
