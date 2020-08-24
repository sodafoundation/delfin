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

# This file contains mapping of alert information to vmax specific description

# component type to descriptive info
component_type_mapping = {
    '1024': 'Symmetrix',
    '1025': 'Service Processor',
    '1026': 'Device',
    '1027': 'Physical Disk',
    '1028': 'Director',
    '1029': 'Port',
    '1030': 'SRDF sub-system',
    '1031': 'SRDF group',
    '1032': 'Snap Save Device Pool',
    '1033': 'Cache / Memory',
    '1034': 'Power or Battery subsystem',
    '1035': 'Environmental (e.g.: Temperature, Smoke)',
    '1036': 'Diagnostics',
    '1037': 'Communications sub-system',
    '1038': 'External Lock',
    '1039': 'Fan',
    '1040': 'Link Controller Card',
    '1041': 'Enclosure, Enclosure-Slot or MIBE',
    '1042': 'SRDF/A DSE Device Pool',
    '1043': 'Thin Device Data Pool',
    '1044': 'Solutions Enabler DG group',
    '1045': 'Solutions Enabler CG group',
    '1046': 'Management Module',
    '1047': 'IO Module Carrier',
    '1048': 'Director - Environmental',
    '1049': 'Storage Group',
    '1050': 'Migration Session',
    '1051': 'Symmetrix Disk Group'
}

# Alarm id to alarm name mapping
# Currently this contains limited list, to be extended
alarm_id_name_mapping = {
    '1': 'SYMAPI_AEVENT2_UID_EVT_RESTARTED',
    '2': 'SYMAPI_AEVENT2_UID_EVT_EVENTS_LOST',
    '3': 'SYMAPI_AEVENT2_UID_EVT_EVENTS_OVERFLOW',
    '1050': 'SYMAPI_AEVENT2_UID_MOD_DIAG_TRACE_TRIG',
    '1051': 'SYMAPI_AEVENT2_UID_MOD_DIAG_TRACE_TRIG_REM'
}
