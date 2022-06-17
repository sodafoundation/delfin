# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
from unittest import TestCase, mock

import paramiko

from delfin.common import constants

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from delfin.drivers.utils.tools import Tools

sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
from delfin.drivers.ibm.storwize_svc.ssh_handler import SSHHandler
from delfin.drivers.ibm.storwize_svc.storwize_svc import StorwizeSVCDriver
from delfin.drivers.utils.ssh_client import SSHPool


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


UNSECURE_ALGORITHMS = {
    "ciphers": [
        "aes128-cbc",
        "aes192-cbc",
        "aes256-cbc",
        "blowfish-cbc",
        "3des-cbc"
    ],
    "macs": [
        "hmac-sha1-96",
        "hmac-md5",
        "hmac-md5-96"
    ],
    "keys": [
        "ecdsa-sha2-nistp256",
        "ecdsa-sha2-nistp384",
        "ecdsa-sha2-nistp521",
        "ssh-dss"
    ],
    "kex": [
        "diffie-hellman-group14-sha256",
        "diffie-hellman-group-exchange-sha1",
        "diffie-hellman-group14-sha1",
        "diffie-hellman-group1-sha1"
    ]}


ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "hpe",
    "model": "3par",
    "rest": {
        "host": "10.0.0.1",
        "port": 8443,
        "username": "user",
        "password": "pass"
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "pass",
        "pub_key": "ddddddddddddddddddddddddd"
    }
}

system_info = """id 00000200A1207E1F
name Cluster_192.168.70.125
location local
partnership
total_mdisk_capacity 8.1TB
space_in_mdisk_grps 8.1TB
space_allocated_to_vdisks 5.06TB
total_free_space 3.1TB
total_vdiskcopy_capacity 5.51TB
total_used_capacity 5.05TB
total_overallocation 67
total_vdisk_capacity 5.51TB
total_allocated_extent_capacity 5.07TB
statistics_status on
statistics_frequency 5
cluster_locale en_US
time_zone 246 Asia/Shanghai
code_level 7.4.0.11 (build 103.29.1609070000)
console_IP 51.10.58.200:443
id_alias 00000200A1007E1F
gm_link_tolerance 300
gm_inter_cluster_delay_simulation 0
gm_intra_cluster_delay_simulation 0
gm_max_host_delay 5
email_reply
email_contact
email_contact_primary
email_contact_alternate
email_contact_location
email_contact2
email_contact2_primary
email_contact2_alternate
email_state stopped
inventory_mail_interval 0
cluster_ntp_IP_address
cluster_isns_IP_address
iscsi_auth_method none
iscsi_chap_secret
auth_service_configured no
auth_service_enabled no
auth_service_url
auth_service_user_name
auth_service_pwd_set no
auth_service_cert_set no
auth_service_type tip
relationship_bandwidth_limit 25
tier ssd
tier_capacity 0.00MB
tier_free_capacity 0.00MB
tier enterprise
tier_capacity 0.00MB
tier_free_capacity 0.00MB
tier nearline
tier_capacity 8.13TB
tier_free_capacity 3.06TB
has_nas_key no
layer storage
rc_buffer_size 48
compression_active no
compression_virtual_capacity 0.00MB
compression_compressed_capacity 0.00MB
compression_uncompressed_capacity 0.00MB
cache_prefetch on
email_organization
email_machine_address
email_machine_city
email_machine_state XX
email_machine_zip
email_machine_country
total_drive_raw_capacity 10.92TB
compression_destage_mode off
local_fc_port_mask 1111111111111111111111111111111
partner_fc_port_mask 11111111111111111111111111111
high_temp_mode off
topology standard
topology_status
rc_auth_method none
vdisk_protection_time 15
vdisk_protection_enabled no
product_name IBM Storwize V7000
max_replication_delay 0
partnership_exclusion_threshold 315
"""

enclosure_info = """id:status:type:managed:IO_id:IO_group_name:product_MTM
1:online:control:yes:0:io_grp0:2076-124:78N16G4:2:2:2:2:24:0:0
"""

pools_info = """id name      status mdisk_count vdisk_count capacity
1  mdiskgrp0 online 1           101         8.13TB   1024        3.06TB
"""

pool_info = """id 1
name mdiskgrp0
status online
mdisk_count 1
vdisk_count 101
capacity 8.13TB
extent_size 1024
free_capacity 3.06TB
virtual_capacity 5.51TB
used_capacity 5.05TB
real_capacity 5.06TB
overallocation 67
warning 80
easy_tier auto
easy_tier_status balanced
tier ssd
tier_mdisk_count 0
tier_capacity 0.00MB
tier_free_capacity 0.00MB
tier enterprise
tier_mdisk_count 0
tier_capacity 0.00MB
tier_free_capacity 0.00MB
tier nearline
tier_mdisk_count 1
tier_capacity 8.13TB
tier_free_capacity 3.06TB
compression_active no
compression_virtual_capacity 0.00MB
compression_compressed_capacity 0.00MB
compression_uncompressed_capacity 0.00MB
site_id
site_name
parent_mdisk_grp_id 1
parent_mdisk_grp_name mdiskgrp0
child_mdisk_grp_count 0
child_mdisk_grp_capacity 0.00MB
type parent
encrypt no
"""

volumes_info = """id  name            IO_group_id IO_group_name status
0   V7000LUN_Mig    0           io_grp0       online 1
"""

volume_info = """id:0
name:V7000LUN_Mig
IO_group_id:0
IO_group_name:io_grp0
status:online
mdisk_grp_id:1
mdisk_grp_name:mdiskgrp0
capacity:50.00GB
type:striped
formatted:no
mdisk_id:
mdisk_name:
FC_id:
FC_name:
RC_id:
RC_name:
vdisk_UID:60050768028401F87C00000000000000
throttling:0
preferred_node_id:3
fast_write_state:empty
cache:readwrite
udid:
fc_map_count:0
sync_rate:50
copy_count:1
se_copy_count:0
filesystem:
mirror_write_priority:latency
RC_change:no
compressed_copy_count:0
access_IO_group_count:1
last_access_time:190531130236
parent_mdisk_grp_id:1
parent_mdisk_grp_name:mdiskgrp0

copy_id:0
status:online
sync:yes
primary:yes
mdisk_grp_id:1
mdisk_grp_name:mdiskgrp0
type:striped
mdisk_id:
mdisk_name:
fast_write_state:empty
used_capacity:50.00GB
real_capacity:50.00GB
free_capacity:0.00MB
overallocation:100
autoexpand:
warning:
grainsize:
se_copy:no
easy_tier:on
easy_tier_status:balanced
tier:ssd
tier_capacity:0.00MB
tier:enterprise
tier_capacity:0.00MB
tier:nearline
tier_capacity:50.00GB
compressed_copy:no
uncompressed_used_capacity:50.00GB
parent_mdisk_grp_id:1
parent_mdisk_grp_name:mdiskgrp0
"""

alerts_info = """sequence_number last_timestamp object_type object_id
101             201111165750   node        3         node1
"""

alert_info = """sequence_number 101
first_timestamp 201111165750
first_timestamp_epoch 1605085070
last_timestamp 201111165750
last_timestamp_epoch 1605085070
object_type node
object_id 3
object_name node1
copy_id
reporting_node_id 3
reporting_node_name node1
root_sequence_number
event_count 1
status message
fixed no
auto_fixed no
notification_type warning
event_id 980221
event_id_text Error log cleared
error_code
error_code_text
machine_type 2076124
serial_number 78N16G4
FRU None
fixed_timestamp
fixed_timestamp_epoch
callhome_type none
sense1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense2 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense4 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense5 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense6 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense7 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
sense8 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
"""

trap_info = {
    '1.3.6.1.2.1.1.3.0': '0',
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.2.6.190.3',
    '1.3.6.1.4.1.2.6.190.4.1': '# Machine Type = 2076124',
    '1.3.6.1.4.1.2.6.190.4.2': '# Serial Number = 78N16G4',
    '1.3.6.1.4.1.2.6.190.4.3': '# Error ID = 981004 : FC discovery occurred, '
    'no configuration changes were detected',
    '1.3.6.1.4.1.2.6.190.4.4': '# Error Code = ',
    '1.3.6.1.4.1.2.6.190.4.5': '# System Version = 7.4.0.11 (build 103.29.'
    '1609070000)',
    '1.3.6.1.4.1.2.6.190.4.6': '# FRU = None ',
    '1.3.6.1.4.1.2.6.190.4.7': '# System Name = Cluster_192.168.70.125',
    '1.3.6.1.4.1.2.6.190.4.8': '# Node ID = 3',
    '1.3.6.1.4.1.2.6.190.4.9': '# Error Sequence Number = 165',
    '1.3.6.1.4.1.2.6.190.4.10': '# Timestamp = Tue Nov 10 09:08:27 2020',
    '1.3.6.1.4.1.2.6.190.4.11': '# Object Type = cluster',
    '1.3.6.1.4.1.2.6.190.4.12': '# Object ID = 0',
    '1.3.6.1.4.1.2.6.190.4.17': '# Object Name = Cluster_192.168.70.125',
    '1.3.6.1.4.1.2.6.190.4.15': '# Copy ID =  ',
    '1.3.6.1.4.1.2.6.190.4.16': '# Machine Part Number = ',
    '1.3.6.1.4.1.2.6.190.4.13': '# Additional Data (0 -> 63) = 01080000018A0',
    '1.3.6.1.4.1.2.6.190.4.14': '# Additional Data (64 -> 127) = 00000000000',
    'transport_address': '51.10.58.200',
    'storage_id': '4992d7f5-4f73-4123-a27b-6e27889f3852'
}

storage_result = {
    'name': 'Cluster_192.168.70.125',
    'vendor': 'IBM',
    'model': 'IBM Storwize V7000',
    'status': 'normal',
    'serial_number': '00000200A1207E1F',
    'firmware_version': '7.4.0.11',
    'location': 'local',
    'total_capacity': 8961019766374,
    'raw_capacity': 8906044184985,
    'subscribed_capacity': 0,
    'used_capacity': 5552533720268,
    'free_capacity': 3408486046105
}

pool_result = [
    {
        'name': 'mdiskgrp0',
        'storage_id': '12345',
        'native_storage_pool_id': '1',
        'description': '',
        'status': 'normal',
        'storage_type': 'block',
        'subscribed_capacity': 6058309069045,
        'total_capacity': 8939029533818,
        'used_capacity': 5552533720268,
        'free_capacity': 3364505580994
    }
]

volume_result = [
    {
        'description': '',
        'status': 'normal',
        'total_capacity': 53687091200,
        'used_capacity': 53687091200,
        'type': 'thick',
        'free_capacity': 0,
        'native_volume_id': '0',
        'deduplicated': True,
        'native_storage_pool_id': '1',
        'wwn': '60050768028401F87C00000000000000',
        'compressed': False,
        'name': 'V7000LUN_Mig',
        'storage_id': '12345'
    }
]

alert_result = [
    {
        'type': 'EquipmentAlarm',
        'location': 'node1',
        'category': 'Fault',
        'occur_time': 1605085070000,
        'sequence_number': '101',
        'resource_type': 'node',
        'alert_name': 'Error log cleared',
        'severity': 'warning',
        'alert_id': '980221',
        'description': 'Error log cleared'
    }
]

trap_alert_result = {
    'alert_id': '981004',
    'type': 'EquipmentAlarm',
    'severity': 'Informational',
    'sequence_number': '165',
    'description': 'FC discovery occurred, no configuration changes '
                   'were detected',
    'occur_time': 1604970507000,
    'alert_name': 'FC discovery occurred, no configuration changes '
                  'were detected',
    'resource_type': 'cluster',
    'location': 'Cluster_192.168.70.125',
    'category': 'Fault'
}
get_all_controllers = """id name
2  node_165084
"""
get_single_controller = """id 2
id 2
name node_165084
UPS_serial_number 100025I194
WWNN 500507680100EF7C
status online
IO_group_id 0
IO_group_name io_grp0
partner_node_id 4
partner_node_name node1
config_node yes
UPS_unique_id 2040000085641244
port_id 500507680140EF7C
port_status active
port_speed 8Gb
port_id 500507680130EF7C
port_status active
port_speed 8Gb
port_id 500507680110EF7C
port_status active
port_speed 8Gb
port_id 500507680120EF7C
port_status active
port_speed 8Gb
hardware CG8
iscsi_name iqn.1986-03.com.ibm:2145.cluster8.44.162.140.node165084
iscsi_alias
failover_active no
failover_name node1
failover_iscsi_name iqn.1986-03.com.ibm:2145.cluster8.44.162.140.node1
failover_iscsi_alias
panel_name 165084
enclosure_id
canister_id
enclosure_serial_number
service_IP_address 8.44.162.142
service_gateway 8.44.128.1
service_subnet_mask 255.255.192.0
service_IP_address_6
service_gateway_6
service_prefix_6
service_IP_mode static
service_IP_mode_6
site_id
site_name
identify_LED off
product_mtm 2145-CG8
code_level 7.8.1.11 (build 135.9.1912100725000)
serial_number 75PVZNA
machine_signature 0214-784E-C029-0147
"""

get_controller_cpu = """id,2
name,node_165084
status,online
IO_group_id,0
IO_group_name,io_grp0
hardware,CG8
actual_different,no
actual_valid,yes
memory_configured,24
memory_actual,24
memory_valid,yes
cpu_count,1
cpu_socket,1
cpu_configured,6 core Intel(R) Xeon(R) CPU E5645 @ 2.40GHz
cpu_actual,6 core Intel(R) Xeon(R) CPU E5645 @ 2.40GHz
cpu_valid,yes
adapter_count,3
adapter_location,1
adapter_configured,Four port 8Gb/s FC adapter
adapter_actual,Four port 8Gb/s FC adapter
adapter_valid,yes
adapter_location,0
adapter_configured,Two port 1Gb/s Ethernet adapter
adapter_actual,Two port 1Gb/s Ethernet adapter
adapter_valid,yes
adapter_location,2
adapter_configured,none
adapter_actual,none
adapter_valid,yes
ports_different,no
"""

controller_result = [
    {
        'name': 'node_165084',
        'storage_id': '12345',
        'native_controller_id': '2',
        'status': 'normal',
        'soft_version': '7.8.1.11',
        'location': 'node_165084',
        'cpu_info': '6 core Intel(R) Xeon(R) CPU E5645 @ 2.40GHz'
    }
]

get_all_disks = """id name
4 mdisk4
"""
get_single_disk = """id 4
name mdisk4
status offline
mode managed
mdisk_grp_id 1
mdisk_grp_name Pool0_NBE
capacity 2.0TB
quorum_index
block_size 512
controller_name NBEPOC_target_Dorado5000V6
ctrl_type 4
ctrl_WWNN 210030E98EE1914C
controller_id 41
path_count 0
max_path_count 0
ctrl_LUN_# 0000000000000001
UID 630e98e100e1914c1aa793ae0000001900000000000000000000000000000000
preferred_WWPN
active_WWPN
fast_write_state empty
raid_status
raid_level
redundancy
strip_size
spare_goal
spare_protection_min
balanced
tier tier0_flash
slow_write_priority
fabric_type fc
site_id
site_name
easy_tier_load medium
encrypt no
distributed no
drive_class_id
drive_count 0
stripe_width 0
rebuild_areas_total
rebuild_areas_available
rebuild_areas_goal
dedupe no
preferred_iscsi_port_id
active_iscsi_port_id
replacement_date
"""
disk_result = [
    {
        'name': 'mdisk4',
        'storage_id': '12345',
        'native_disk_id': '4',
        'capacity': 2199023255552,
        'status': 'offline',
        'physical_type': 'fc',
        'native_disk_group_id': 'Pool0_NBE',
        'location': 'NBEPOC_target_Dorado5000V6_mdisk4'
    }
]
get_all_fcports = """id fc_io_port_id
0 1
"""
get_single_fcport = """id 0
fc_io_port_id 1
port_id 1
type fc
port_speed 8Gb
node_id 1
node_name node1
WWPN 500507680140EF3E
nportid 850600
status active
switch_WWPN 200650EB1A8A59B8
fpma N/A
vlanid N/A
fcf_MAC N/A
attachment switch
cluster_use local_partner
adapter_location 1
adapter_port_id 1
fabric_WWN 100050EB1A8A59B8
 """
get_iscsiport_1 = """id 1
node_id 1
node_name node1
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d7:5a:94
duplex Full
state unconfigured
speed 1Gb/s
failover no
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6

id 1
node_id 1
node_name node1
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d7:5a:94
duplex Full
state unconfigured
speed 1Gb/s
failover yes
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6

id 1
node_id 2
node_name node_165084
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d4:0c:f0
duplex Full
state unconfigured
speed 1Gb/s
failover no
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6

id 1
node_id 2
node_name node_165084
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d4:0c:f0
duplex Full
state unconfigured
speed 1Gb/s
failover yes
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6
 """
get_iscsiport_2 = """id 2
node_id 1
node_name node1
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d7:5a:94
duplex Full
state unconfigured
speed 1Gb/s
failover no
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6

id 2
node_id 1
node_name node1
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d7:5a:94
duplex Full
state unconfigured
speed 1Gb/s
failover yes
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6

id 2
node_id 2
node_name node_165084
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d4:0c:f0
duplex Full
state unconfigured
speed 1Gb/s
failover no
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6

id 2
node_id 2
node_name node_165084
IP_address
mask
gateway
IP_address_6
prefix_6
gateway_6
MAC 34:40:b5:d4:0c:f0
duplex Full
state unconfigured
speed 1Gb/s
failover yes
mtu 1500
link_state active
host
remote_copy 0
host_6
remote_copy_6 0
remote_copy_status
remote_copy_status_6
vlan
vlan_6
adapter_location 0
adapter_port_id 1
dcbx_state
lossless_iscsi
lossless_iscsi6
iscsi_priority_tag
fcoe_priority_tag
pfc_enabled_tags
pfc_disabled_tags
priority_group_0
priority_group_1
priority_group_2
priority_group_3
priority_group_4
priority_group_5
priority_group_6
priority_group_7
bandwidth_allocation
storage
storage_6
 """
get_file_list = 'id filename\n' \
                '1 Nn_stats_78N16G4-2_211201_161110\n' \
                '2 Nn_stats_78N16G4-2_211201_161210\n' \
                '3 Nm_stats_78N16G4-2_211201_161110\n' \
                '4 Nm_stats_78N16G4-2_211201_161210\n' \
                '5 Nv_stats_78N16G4-2_211201_161110\n' \
                '6 Nv_stats_78N16G4-2_211201_161210'
file_nv_1611 = """<?xml version="1.0" encoding="utf-8" ?>
<vdsk idx="0"
ctps="0" ctrhs="0" ctrhps="0" ctds="0"
ctwfts="0" ctwwts="0" ctwfws="0" ctwhs="0"
cv="0" cm="0" ctws="0" ctrs="0"
ctr="0" ctw="0" ctp="0" ctrh="0"
ctrhp="0" ctd="0" ctwft="0" ctwwt="0"
ctwfw="0" ctwfwsh="0" ctwfwshs="0" ctwh="0"
gwot="0" gwo="0" gws="0" gwl="0"
id="powerha_fence"
ro="0" wo="0" wou="0" rb="0" wb="0"
rl="0" wl="0" rlw="0" wlw="0" xl="0">
 <ca rh="0" d="0" ft="0" wt="0" fw="0" wh="0" v="0" m="0" ri="0" wi="0" r="0"
dav="0" dcn="0" sav="0" scn="0" teav="0"
 tsav="0"  tav="0"  pp="0"/>
</vdsk>
"""
file_nv_1612 = """<?xml version="1.0" encoding="utf-8" ?>
<vdsk idx="0"
ctps="0" ctrhs="0" ctrhps="0" ctds="0"
ctwfts="0" ctwwts="0" ctwfws="0" ctwhs="0"
cv="0" cm="0" ctws="0" ctrs="0"
ctr="0" ctw="0" ctp="0" ctrh="0"
ctrhp="0" ctd="0" ctwft="0" ctwwt="0"
ctwfw="0" ctwfwsh="0" ctwfwshs="0" ctwh="0"
gwot="0" gwo="0" gws="0" gwl="0"
id="powerha_fence"
ro="0" wo="0" wou="0" rb="0" wb="0"
rl="0" wl="0" rlw="0" wlw="0" xl="0">
<ca rh="0" d="0" ft="0" wt="0" fw="0" wh="0" v="0" m="0" ri="0"
 wi="0" r="0" dav="0" dcn="0" sav="0" scn="0" teav="0"
 tsav="0"  tav="0"  pp="0"/>
</vdsk>
"""
file_nm_1611 = """<?xml version="1.0" encoding="utf-8" ?>
<mdsk idx="0"
 id="mdisk1" ro="160422028" wo="4792298" rb="65855202896" wb="5087205812"
  re="4510327873" we="324970648" rq="4510327873" wq="324970648"
  ure="4511020738035" uwe="325020569160" urq="4511020738035"
   uwq="325020569160"
 pre="14804" pwe="0" pro="14804" pwo="0">
<ca dav="0" dtav="0" dfav="0" />
</mdsk>
"""
file_nm_1612 = """<?xml version="1.0" encoding="utf-8" ?>
<mdsk idx="0"
 id="mdisk1" ro="16532168" wo="4800940" rb="807398566" wb="1268035694"
  re="336180638" we="392975230" rq="336180638" wq="392975230"
  ure="336232281210" uwe="393035597850" urq="336232281210"
  uwq="393035597850"
 pre="0" pwe="0" pro="0" pwo="0">
<ca dav="0" dtav="0" dfav="0" />
</mdsk>
"""
file_nn_1611 = """<?xml version="1.0" encoding="utf-8" ?>
<port id="1"
type="FC"
type_id="1"
wwpn="0x50050768021065cb"
fc_wwpn="0x50050768021065cb"
fcoe_wwpn=""
sas_wwn=""
iqn=""
hbt="534901200817" hbr="523369795104" het="0" her="186406977"
cbt="0" cbr="52250" cet="1324" cer="0"
lnbt="49310" lnbr="197487" lnet="2073731" lner="2070067"
rmbt="0" rmbr="0" rmet="0" rmer="0"
lf="9" lsy="21" lsi="5" pspe="0"
itw="295290111" icrc="0" bbcz="29140"
/>
"""
file_nn_1612 = """<?xml version="1.0" encoding="utf-8" ?>
<port id="1"
type="FC"
type_id="1"
wwpn="0x50050768021065cb"
fc_wwpn="0x50050768021065cb"
fcoe_wwpn=""
sas_wwn=""
iqn=""
hbt="534901200817" hbr="523369795104" het="0" her="186406977"
cbt="0" cbr="52250" cet="1324" cer="0"
lnbt="49310" lnbr="197487" lnet="2073806" lner="2070142"
rmbt="0" rmbr="0" rmet="0" rmer="0"
lf="9" lsy="21" lsi="5" pspe="0"
itw="295290111" icrc="0" bbcz="29140"
/>
"""
file_nn_node_1611 = """<?xml version="1.0" encoding="utf-8" ?>
<node id="node1" cluster="Cluster_V7000" node_id="0x0000000000000003"
 cluster_id="0x00000200a1207e1f" ro="960680162" wo="940411371"
  rb="2605358068064" wb="2619210259131" re="1193453" we="135040076"
   rq="49536391" wq="151133071"/>
"""
file_nn_node_1612 = """<?xml version="1.0" encoding="utf-8" ?>
<node id="node1" cluster="Cluster_V7000" node_id="0x0000000000000003"
 cluster_id="0x00000200a1207e1f" ro="960684525" wo="940415078"
  rb="2605359825065" wb="2619220318131" re="1193465"
   we="135040076" rq="49536391" wq="151134080"/>
"""
resource_metrics = {
    'volume': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'responseTime',
        'ioSize', 'readIoSize', 'writeIoSize',
    ],
    'port': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'responseTime'
    ],
    'disk': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'responseTime'
    ],
    'controller': [
        'iops', 'readIops', 'writeIops',
        'throughput', 'readThroughput', 'writeThroughput',
        'responseTime'
    ]
}

port_result = [
    {
        'name': 'node1_0',
        'storage_id': '12345',
        'native_port_id': '0',
        'location': 'node1_0',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'fc',
        'speed': 8000000000,
        'native_parent_id': 'node1',
        'wwn': '500507680140EF3E'
    }, {
        'name': 'node1_1',
        'storage_id': '12345',
        'native_port_id': 'node1_1',
        'location': 'node1_1',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'eth',
        'speed': 1000000000,
        'native_parent_id': 'node1',
        'mac_address': '34:40:b5:d7:5a:94',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': ''
    }, {
        'name': 'node_165084_1',
        'storage_id': '12345',
        'native_port_id': 'node_165084_1',
        'location': 'node_165084_1',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'eth',
        'speed': 1000000000,
        'native_parent_id': 'node_165084',
        'mac_address': '34:40:b5:d4:0c:f0',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': ''
    }, {
        'name': 'node1_2',
        'storage_id': '12345',
        'native_port_id': 'node1_2',
        'location': 'node1_2',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'eth',
        'speed': 1000000000,
        'native_parent_id': 'node1',
        'mac_address': '34:40:b5:d7:5a:94',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': ''
    }, {
        'name': 'node_165084_2',
        'storage_id': '12345',
        'native_port_id': 'node_165084_2',
        'location': 'node_165084_2',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'eth',
        'speed': 1000000000,
        'native_parent_id': 'node_165084',
        'mac_address': '34:40:b5:d4:0c:f0',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': ''
    }
]
perf_get_port_fc = [
    {
        'name': '0',
        'storage_id': '12345',
        'native_port_id': '0',
        'location': 'node1_0',
        'connection_status': 'connected',
        'health_status': 'normal',
        'type': 'fc',
        'max_speed': 8589934592,
        'native_parent_id': 'node1',
        'wwn': '0x50050768021065cb'
    }
]
metrics_result = [
    constants.metric_struct(
        name='iops', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readIops', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeIops', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='throughput', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readThroughput', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeThroughput', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='responseTime', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'ms'
        }, values={
            1638346330000: 0
        }), constants.metric_struct(name='ioSize', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'KB'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readIoSize', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'KB'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeIoSize', labels={
            'storage_id': '12345',
            'resource_type': 'volume',
            'resource_id': '0',
            'resource_name': 'powerha',
            'type': 'RAW',
            'unit': 'KB'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='iops', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readIops', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeIops', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='throughput', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readThroughput', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeThroughput', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='responseTime', labels={
            'storage_id': '12345',
            'resource_type': 'disk',
            'resource_id': '0',
            'resource_name': 'mdisk1',
            'type': 'RAW',
            'unit': 'ms'
        }, values={
            1638346330000: 0
        }), constants.metric_struct(name='iops', labels={
            'storage_id': '12345',
            'resource_type': 'port',
            'resource_id': '0',
            'resource_name': '0',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readIops', labels={
            'storage_id': '12345',
            'resource_type': 'port',
            'resource_id': '0',
            'resource_name': '0',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeIops', labels={
            'storage_id': '12345',
            'resource_type': 'port',
            'resource_id': '0',
            'resource_name': '0',
            'type': 'RAW',
            'unit': 'IOPS'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='throughput', labels={
            'storage_id': '12345',
            'resource_type': 'port',
            'resource_id': '0',
            'resource_name': '0',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='readThroughput', labels={
            'storage_id': '12345',
            'resource_type': 'port',
            'resource_id': '0',
            'resource_name': '0',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        }), constants.metric_struct(name='writeThroughput', labels={
            'storage_id': '12345',
            'resource_type': 'port',
            'resource_id': '0',
            'resource_name': '0',
            'type': 'RAW',
            'unit': 'MB/s'
        }, values={
            1638346330000: 0.0
        })]
get_all_hosts = """id name
1 host1
"""
get_host_summery = """id 38
name tjy_test_iscsi
port_count 3
type generic
mask 11111111111111111111111111111111111111
iogrp_count 4
status online
site_id
site_name
host_cluster_id
host_cluster_name
WWPN 21000024FF543B0C
node_logged_in_count 1
state inactive
WWPN 21000024FF438098
node_logged_in_count 1
state active
WWPN 21000024FF41C461
node_logged_in_count 1
state inactive
"""
host_result = [
    {
        'name': 'tjy_test_iscsi',
        'storage_id': '12345',
        'native_storage_host_id': '38',
        'os_type': 'Unknown',
        'status': 'normal'
    }
]
get_all_views = """id name SCSI_id vdisk_id vdisk_name
2  Solaris11.3_57         0       27       PG_1
6  hwstorage_8.44.133.80  0       24       wyktest
7  VNX-WIN8-TEST          0       31       SVC-WIN8_test
14 pd_esx6                0       65       pd_taiping0
14 pd_esx6                1       66       pd_taiping1
14 pd_esx6                2       67       pd_taiping2
"""
view_result = [
    {
        'name': '2_27',
        'native_storage_host_id': '2',
        'storage_id': '12345',
        'native_volume_id': '27',
        'native_masking_view_id': '2_27'
    }, {
        'name': '6_24',
        'native_storage_host_id': '6',
        'storage_id': '12345',
        'native_volume_id': '24',
        'native_masking_view_id': '6_24'
    }, {
        'name': '7_31',
        'native_storage_host_id': '7',
        'storage_id': '12345',
        'native_volume_id': '31',
        'native_masking_view_id': '7_31'
    }, {
        'name': '14_65',
        'native_storage_host_id': '14',
        'storage_id': '12345',
        'native_volume_id': '65',
        'native_masking_view_id': '14_65'
    }, {
        'name': '14_66',
        'native_storage_host_id': '14',
        'storage_id': '12345',
        'native_volume_id': '66',
        'native_masking_view_id': '14_66'
    }, {
        'name': '14_67',
        'native_storage_host_id': '14',
        'storage_id': '12345',
        'native_volume_id': '67',
        'native_masking_view_id': '14_67'
    }
]
init_result = [
    {
        'name': '21000024FF543B0C',
        'storage_id': '12345',
        'native_storage_host_initiator_id': '21000024FF543B0C',
        'wwn': '21000024FF543B0C',
        'status': 'online',
        'type': 'fc',
        'native_storage_host_id': '38'
    }, {
        'name': '21000024FF438098',
        'storage_id': '12345',
        'native_storage_host_initiator_id': '21000024FF438098',
        'wwn': '21000024FF438098',
        'status': 'online',
        'type': 'fc',
        'native_storage_host_id': '38'
    }, {
        'name': '21000024FF41C461',
        'storage_id': '12345',
        'native_storage_host_initiator_id': '21000024FF41C461',
        'wwn': '21000024FF41C461',
        'status': 'online',
        'type': 'fc',
        'native_storage_host_id': '38'
    }
]


def create_driver():

    SSHHandler.login = mock.Mock(
        return_value={""})

    return StorwizeSVCDriver(**ACCESS_INFO)


class TestStorwizeSvcStorageDriver(TestCase):
    driver = create_driver()

    def test_init(self):
        SSHHandler.login = mock.Mock(
            return_value={""})
        StorwizeSVCDriver(**ACCESS_INFO)

    def test_list_storage(self):
        SSHPool.get = mock.Mock(
            return_value={paramiko.SSHClient()})
        SSHHandler.do_exec = mock.Mock(
            side_effect=[system_info])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_storage_pools(self):
        SSHPool.get = mock.Mock(
            return_value={paramiko.SSHClient()})
        SSHHandler.do_exec = mock.Mock(
            side_effect=[pools_info, pool_info])
        pool = self.driver.list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])

    def test_list_volumes(self):
        SSHPool.get = mock.Mock(
            return_value={paramiko.SSHClient()})
        SSHHandler.do_exec = mock.Mock(
            side_effect=[volumes_info, volume_info])
        volume = self.driver.list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    def test_list_alerts(self):
        query_para = {
            "begin_time": 1605085070000,
            "end_time": 1605085070000
        }
        SSHPool.get = mock.Mock(
            return_value={paramiko.SSHClient()})
        SSHHandler.do_exec = mock.Mock(
            side_effect=[alerts_info, alert_info])
        alert = self.driver.list_alerts(context, query_para)
        self.assertEqual(alert[0].get('alert_id'),
                         alert_result[0].get('alert_id'))

    def test_parse_alert(self):
        alert = self.driver.parse_alert(context, trap_info)
        trap_alert_result['occur_time'] = alert['occur_time']
        self.assertEqual(alert, trap_alert_result)

    def test_clear_alert(self):
        alert_id = 101
        SSHPool.get = mock.Mock(
            return_value={paramiko.SSHClient()})
        SSHHandler.do_exec = mock.Mock(
            side_effect=['CMMVC8275E'])
        self.driver.clear_alert(context, alert_id)
        with self.assertRaises(Exception) as exc:
            SSHPool.get = mock.Mock(
                return_value={paramiko.SSHClient()})
            SSHHandler.do_exec = mock.Mock(
                side_effect=['can not find alert'])
            self.driver.clear_alert(context, alert_id)
        self.assertIn('The results are invalid. can not find alert',
                      str(exc.exception))

    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_list_controllers(self, mock_ssh_get, mock_control):
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_control.side_effect = [get_all_controllers, get_single_controller,
                                    get_controller_cpu]
        controller = self.driver.list_controllers(context)
        self.assertEqual(controller, controller_result)

    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_list_disks(self, mock_ssh_get, mock_disk):
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_disk.side_effect = [get_all_disks, get_single_disk]
        disk = self.driver.list_disks(context)
        self.assertEqual(disk, disk_result)

    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_list_ports(self, mock_ssh_get, mock_port):
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_port.side_effect = [get_all_fcports, get_single_fcport,
                                 get_iscsiport_1, get_iscsiport_2]
        port = self.driver.list_ports(context)
        self.assertEqual(port, port_result)

    @mock.patch.object(SSHHandler, 'get_fc_port')
    @mock.patch.object(Tools, 'get_remote_file_to_xml')
    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_collect_perf_metrics(self, mock_ssh_get, mock_file_list,
                                  mock_get_file, mock_fc_port):
        start_time = 1637346270000
        end_time = 1639346330000
        storage_id = '12345'
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_file_list.return_value = get_file_list
        mock_get_file.return_value = [ET.fromstring(file_nv_1611),
                                      ET.fromstring(file_nv_1612),
                                      ET.fromstring(file_nm_1611),
                                      ET.fromstring(file_nm_1612),
                                      ET.fromstring(file_nn_1611),
                                      ET.fromstring(file_nn_1612),
                                      ET.fromstring(file_nn_node_1611),
                                      ET.fromstring(file_nn_node_1612)
                                      ]
        mock_fc_port.return_value = perf_get_port_fc
        metrics = self.driver.collect_perf_metrics(context, storage_id,
                                                   resource_metrics,
                                                   start_time, end_time)
        self.assertEqual(metrics[0][1]['resource_name'], 'powerha')

    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_list_hosts(self, mock_ssh_get, mock_host):
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_host.side_effect = [get_all_hosts, get_host_summery]
        host = self.driver.list_storage_hosts(context)
        self.assertEqual(host, host_result)

    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_masking_views(self, mock_ssh_get, mock_view):
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_view.return_value = get_all_views
        view = self.driver.list_masking_views(context)
        self.assertEqual(view, view_result)

    @mock.patch.object(SSHHandler, 'do_exec')
    @mock.patch.object(SSHPool, 'get')
    def test_list_host_initiators(self, mock_ssh_get, mock_host):
        mock_ssh_get.return_value = {paramiko.SSHClient()}
        mock_host.side_effect = [get_all_hosts, get_host_summery]
        init = self.driver.list_storage_host_initiators(context)
        self.assertEqual(init, init_result)
