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
get_all_controllers = """id controller_name
16 controller13
"""
get_single_controller = """id 16
controller_name controller13
WWNN 2100340006260912
mdisk_link_count 5
max_mdisk_link_count 10
degraded no
vendor_id HUAWEI
product_id_low XSG1
product_id_high
product_revision 4301
ctrl_s/n
allow_quorum yes
fabric_type fc
site_id
site_name
"""
controller_result = [
    {
        'name': 'controller13',
        'storage_id': '12345',
        'native_controller_id': '16',
        'status': 'normal',
        'soft_version': 'XSG1',
        'location': 'controller13'
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
        'location': 'NBEPOC_target_Dorado5000V6'
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
port_result = [
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
        'wwn': '500507680140EF3E'
    }, {
        'name': '1',
        'storage_id': '12345',
        'native_port_id': '1',
        'location': 'node1_1',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'iscsi',
        'max_speed': 1073741824,
        'native_parent_id': 'node1',
        'mac_address': '34:40:b5:d7:5a:94',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': '',
        'ipv6_mask': ''
    }, {
        'name': '1',
        'storage_id': '12345',
        'native_port_id': '1',
        'location': 'node_165084_1',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'iscsi',
        'max_speed': 1073741824,
        'native_parent_id': 'node_165084',
        'mac_address': '34:40:b5:d4:0c:f0',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': '',
        'ipv6_mask': ''
    }, {
        'name': '2',
        'storage_id': '12345',
        'native_port_id': '2',
        'location': 'node1_2',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'iscsi',
        'max_speed': 1073741824,
        'native_parent_id': 'node1',
        'mac_address': '34:40:b5:d7:5a:94',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': '',
        'ipv6_mask': ''
    }, {
        'name': '2',
        'storage_id': '12345',
        'native_port_id': '2',
        'location': 'node_165084_2',
        'connection_status': 'connected',
        'health_status': 'abnormal',
        'type': 'iscsi',
        'max_speed': 1073741824,
        'native_parent_id': 'node_165084',
        'mac_address': '34:40:b5:d4:0c:f0',
        'ipv4': '',
        'ipv4_mask': '',
        'ipv6': '',
        'ipv6_mask': ''
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
        mock_control.side_effect = [get_all_controllers, get_single_controller]
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
