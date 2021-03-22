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
