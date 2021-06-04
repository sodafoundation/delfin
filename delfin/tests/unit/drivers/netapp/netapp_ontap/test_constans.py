# Copyright 2021 The SODA Authors.
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
        "host": "192.168.159.130",
        "port": 22,
        "username": "admin",
        "password": "aq114477",
    }
}

SYSTEM_INFO = """Cluster UUID: 47096983-8018-11eb-bd5b-000c293284bd\r
          Cluster Name: cl\r
 Cluster Serial Number: -\r
      Cluster Location:\r
       Cluster Contact: \r"""

AGGREGATE_INFO = """\r
Aggregate     Size Available Used% State   #Vols  Nodes   RAID Status\r
--------- -------- --------- ----- ------- ------ --------------------\r
aggr0        855MB   42.14MB   95% online       1 cl-01   raid_dp,\r
                                normal\r
aggr1       8.79GB    3.98GB   55% online       3 cl-01   raid_dp,\r
                                normal\r
aggr2       8.79GB    4.98GB   43% online       3 cl-01   raid_dp,\r
                                normal\r"""

VERSION = """NetApp Release 9.0: Fri Aug 19 06:39:33 UTC 2016"""

SYSTEM_STATUS = """Status\r
---------------\r
ok"""

DISK_INFO = """
                     Usable           Disk    Container   Container\r
Disk                   Size Shelf Bay Type    Type        Name      Owner\r
---------------- ---------- ----- --- ------- ----------- --------- -----\r
NET-1.1              1020254     -  16 FCAL    aggregate   aggr0     cl-01\r
NET-1.2              1020MB     -  17 FCAL    aggregate   aggr1     cl-01\r
NET-1.3              1020MB     -  18 FCAL    aggregate   aggr1     cl-01\r
NET-1.4              1020MB     -  19 FCAL    aggregate   aggr1     cl-01\r
NET-1.5              1020MB     -  20 FCAL    aggregate   aggr1     cl-01\r
NET-1.6              1020MB     -  21 FCAL    aggregate   aggr1     cl-01\r
NET-1.7              1020MB     -  22 FCAL    aggregate   aggr1     cl-01\r
NET-1.8              1020MB     -  24 FCAL    aggregate   aggr2     cl-01\r
NET-1.9              1020MB     -  16 FCAL    aggregate   aggr0     cl-01\r
NET-1.10             1020MB     -  17 FCAL    aggregate   aggr0     cl-01\r
NET-1.11             1020MB     -  18 FCAL    aggregate   aggr1     cl-01\r
NET-1.12             1020MB     -  19 FCAL    aggregate   aggr1     cl-01\r
NET-1.13             1020MB     -  20 FCAL    aggregate   aggr1     cl-01\r
NET-1.14             1020MB     -  25 FCAL    aggregate   aggr2     cl-01\r
NET-1.15             1020MB     -  26 FCAL    aggregate   aggr2     cl-01\r
NET-1.16             1020MB     -  27 FCAL    aggregate   aggr2     cl-01\r
NET-1.17             1020MB     -  28 FCAL    aggregate   aggr2     cl-01\r
NET-1.18             1020MB     -  21 FCAL    aggregate   aggr1     cl-01\r
NET-1.19             1020MB     -  22 FCAL    aggregate   aggr1     cl-01\r
NET-1.20             1020MB     -  24 FCAL    aggregate   aggr1     cl-01\r
NET-1.21             1020MB     -  25 FCAL    aggregate   aggr2     cl-01\r
NET-1.22             1020MB     -  26 FCAL    aggregate   aggr2     cl-01\r
NET-1.23             1020MB     -  27 FCAL    aggregate   aggr2     cl-01\r
NET-1.24             1020MB     -  28 FCAL    aggregate   aggr2     cl-01\r
NET-1.25             1020MB     -  29 FCAL    aggregate   aggr2     cl-01\r
NET-1.26             1020MB     -  32 FCAL    aggregate   aggr2     cl-01\r
NET-1.27             1020MB     -  29 FCAL    aggregate   aggr2     cl-01\r
NET-1.28             1020MB     -  32 FCAL    spare       Pool0     cl-01\r
28 entries were displayed."""

POOLS_INFO = """
\r
                        Storage Pool Name: Pool1\r
                     UUID of Storage Pool: 60f2f1b9-e60f-11e3\r
           Nodes Sharing the Storage Pool: node-a, node-b\r
          Number of Disks in Storage Pool: 2\r
                     Allocation Unit Size: 372.5GB\r
                             Storage Type: SSD\r
                 Storage Pool Usable Size: 1.09TB\r
                  Storage Pool Total Size: 1.45TB\r
                         Is Pool Healthy?: true\r
                State of the Storage Pool: normal\r
  Reason for storage pool being unhealthy: -\r
Job ID of the Currently Running Operation: - \r
\r
                        Storage Pool Name: Pool2\r
                     UUID of Storage Pool: 60f2f1b9-e60f-11e3\r
           Nodes Sharing the Storage Pool: node-a, node-b\r
          Number of Disks in Storage Pool: 2\r
                     Allocation Unit Size: 372.5GB\r
                             Storage Type: SSD\r
                 Storage Pool Usable Size: 1.09TB\r
                  Storage Pool Total Size: 1.45TB\r
                         Is Pool Healthy?: true\r
                State of the Storage Pool: normal\r
  Reason for storage pool being unhealthy: -\r
Job ID of the Currently Running Operation: - \r"""

AGGREGATE_DETAIL_INFO = """\r
\r
                                         Aggregate: aggr0\r
                                      Storage Type: hdd\r
                                    Checksum Style: block\r
                                   Number Of Disks: 3\r
                                            Mirror: false\r
                              Disks for First Plex: NET-1.9, NET-1.1\r
                           Disks for Mirrored Plex: -\r
                         Partitions for First Plex: -\r
                      Partitions for Mirrored Plex: -\r
                                              Node: cl-01\r
                           Free Space Reallocation: off\r
                                         HA Policy: cfo\r
                               Ignore Inconsistent: off\r
                Space Reserved for Snapshot Copies: 5%\r
           Aggregate Nearly Full Threshold Percent: 97%\r
                  Aggregate Full Threshold Percent: 98%\r
                             Checksum Verification: on\r
                                   RAID Lost Write: on\r
                             Enable Thorough Scrub: off\r
                                    Hybrid Enabled: false\r
                                    Available Size: 30.34MB\r
                                  Checksum Enabled: true\r
                                   Checksum Status: active\r
                                           Cluster: cl\r
                                   Home Cluster ID: 47096983-8018-11eb-bd5b\r
                                        DR Home ID: -\r
                                      DR Home Name: -\r
                                   Inofile Version: 4\r
                                  Has Mroot Volume: true\r
                     Has Partner Node Mroot Volume: false\r
                                           Home ID: 4082368507\r
                                         Home Name: cl-01\r
                           Total Hybrid Cache Size: 0B\r
                                            Hybrid: false\r
                                      Inconsistent: false\r
                                 Is Aggregate Home: true\r
                                     Max RAID Size: 16\r
       Flash Pool SSD Tier Maximum RAID Group Size: -\r
                                          Owner ID: 4082368507\r
                                        Owner Name: cl-01\r
                                   Used Percentage: 96%\r
                                            Plexes: /aggr0/plex0\r
                                       RAID Groups: /aggr0/plex0/rg0 (block)\r
                             RAID Lost Write State: on\r
                                       RAID Status: raid_dp, normal\r
                                         RAID Type: raid_dp\r
   SyncMirror Resync Snapshot Frequency in Minutes: 5\r
                                           Is Root: true\r
      Space Used by Metadata for Volume Efficiency: 0B\r
                                              Size: 855MB\r
                                             State: online\r
                        Maximum Write Alloc Blocks: 0\r
                                         Used Size: 824.7MB\r
                                 Uses Shared Disks: false\r
                                       UUID String: a71b1e4e-d151-abebf8\r
                                 Number Of Volumes: 1
                             Is Flash Pool Caching: -\r
            Is Eligible for Auto Balance Aggregate: false\r
             State of the aggregate being balanced: ineligible\r
                          Total Physical Used Size: 712.3MB\r
                          Physical Used Percentage: 79%\r
            State Change Counter for Auto Balancer: 0\r
                                      Is Encrypted: false\r
                                     SnapLock Type: non-snaplock\r
                                 Encryption Key ID: -\r
 Is in the precommit phase of Copy-Free Transition: false\r
                Is a 7-Mode transitioning aggregat: false\r
Threshold When Aggregate Is Considered Unbalanced (%): 70\r
Threshold When Aggregate Is Considered Balanced (%): 40\r
                        Resynchronization Priority: -\r
                    Space Saved by Data Compaction: 0B\r
               Percentage Saved by Data Compaction: 0%\r
                          Amount of compacted data: 0B\r
\r
                                         Aggregate: aggr1\r
                                      Storage Type: hdd\r
                                    Checksum Style: block\r
                                   Number Of Disks: 12\r
                                            Mirror: false\r
                              Disks for First Plex: NET-1.2, NET-1.11,\r
                                                    NET-1.12, NET-1.4,\r
                                                    NET-1.13, NET-1.5,\r
                                                    NET-1.18, NET-1.6,\r
                                                    NET-1.19, NET-1.7\r
                           Disks for Mirrored Plex: -\r
                         Partitions for First Plex: -\r
                      Partitions for Mirrored Plex: -\r
                                              Node: cl-01\r
                           Free Space Reallocation: off\r
                                         HA Policy: sfo\r
                               Ignore Inconsistent: off\r
                Space Reserved for Snapshot Copies: -\r
           Aggregate Nearly Full Threshold Percent: 95%\r
                  Aggregate Full Threshold Percent: 98%\r
                             Checksum Verification: on\r
                                   RAID Lost Write: on\r
                             Enable Thorough Scrub: off\r
                                    Hybrid Enabled: false\r
                                    Available Size: 5.97GB\r
                                  Checksum Enabled: true\r
                                   Checksum Status: active\r
                                           Cluster: cl\r
                                   Home Cluster ID: 47096983-8018-bd\r
                                        DR Home ID: -\r
                                      DR Home Name: -\r
                                   Inofile Version: 4\r
                                  Has Mroot Volume: false\r
                     Has Partner Node Mroot Volume: false\r
                                           Home ID: 4082368507\r
                                         Home Name: cl-01\r
                           Total Hybrid Cache Size: 0B\r
                                            Hybrid: false\r
                                      Inconsistent: false\r
                                 Is Aggregate Home: true\r
                                     Max RAID Size: 16\r
       Flash Pool SSD Tier Maximum RAID Group Size: -\r
                                          Owner ID: 4082368507\r
                                        Owner Name: cl-01\r
                                   Used Percentage: 32%\r
                                            Plexes: /aggr1/plex0\r
                                       RAID Groups: /aggr1/plex0/rg0 (block)\r
                             RAID Lost Write State: on\r
                                       RAID Status: raid_dp, normal\r
                                         RAID Type: raid_dp\r
   SyncMirror Resync Snapshot Frequency in Minutes: 5\r
                                           Is Root: false\r
      Space Used by Metadata for Volume Efficiency: 0B\r
                                              Size: 8.79GB\r
                                             State: online\r
                        Maximum Write Alloc Blocks: 0\r
                                         Used Size: 2.82GB\r
                                 Uses Shared Disks: false\r
                                       UUID String: 68ffbbca-eb735\r
                                 Number Of Volumes: 3\r
                             Is Flash Pool Caching: -\r
            Is Eligible for Auto Balance Aggregate: false\r
             State of the aggregate being balanced: ineligible\r
                          Total Physical Used Size: 154.7MB\r
                          Physical Used Percentage: 2%\r
            State Change Counter for Auto Balancer: 0\r
                                      Is Encrypted: false\r
                                     SnapLock Type: non-snaplock\r
                                 Encryption Key ID: -\r
 Is in the precommit phase of Copy-Free Transition: false\r
                 Is a 7-Mode transitioning aggrega: false\r
Threshold When Aggregate Is Considered Unbalanced (%): 70
Threshold When Aggregate Is Considered Balanced (%): 40\r
                        Resynchronization Priority: -\r
                    Space Saved by Data Compaction: 0B\r
               Percentage Saved by Data Compaction: 0%\r
                          Amount of compacted data: 0B\r
\r
                                         Aggregate: aggr2\r
                                      Storage Type: hdd\r
                                    Checksum Style: block\r
                                   Number Of Disks: 12\r
                                            Mirror: false\r
                              Disks for First Plex: NET-1.8, NET-1.21,\r
                                                    NET-1.14, NET-1.22,\r
                                                    NET-1.15, NET-1.23,\r
                                                    NET-1.16, NET-1.24,\r
                                                    NET-1.17, NET-1.25,\r
                                                    NET-1.27, NET-1.26\r
                           Disks for Mirrored Plex: -\r
                         Partitions for First Plex: -\r
                      Partitions for Mirrored Plex: -\r
                                              Node: cl-01\r
                           Free Space Reallocation: off\r
                                         HA Policy: sfo\r
                               Ignore Inconsistent: off\r
                Space Reserved for Snapshot Copies: -\r
           Aggregate Nearly Full Threshold Percent: 95%\r
                  Aggregate Full Threshold Percent: 98%\r
                             Checksum Verification: on\r
                                   RAID Lost Write: on\r
                             Enable Thorough Scrub: off\r
                                    Hybrid Enabled: false\r
                                    Available Size: 2.93GB\r
                                  Checksum Enabled: true\r
                                   Checksum Status: active\r
                                           Cluster: cl\r
                                   Home Cluster ID: 47096983-8018-\r
                                        DR Home ID: -\r
                                      DR Home Name: -\r
                                   Inofile Version: 4\r
                                  Has Mroot Volume: false\r
                     Has Partner Node Mroot Volume: false\r
                                           Home ID: 4082368507\r
                                         Home Name: cl-01\r
                           Total Hybrid Cache Size: 0B\r
                                            Hybrid: false\r
                                      Inconsistent: false\r
                                 Is Aggregate Home: true\r
                                     Max RAID Size: 16\r
       Flash Pool SSD Tier Maximum RAID Group Size: -\r
                                          Owner ID: 4082368507\r
                                        Owner Name: cl-01\r
                                   Used Percentage: 67%\r
                                            Plexes: /aggr2/plex0\r
                                       RAID Groups: /aggr2/plex0/rg0 (block)\r
                             RAID Lost Write State: on\r
                                       RAID Status: raid_dp, normal\r
                                         RAID Type: raid_dp\r
   SyncMirror Resync Snapshot Frequency in Minutes: 5\r
                                           Is Root: false\r
      Space Used by Metadata for Volume Efficiency: 0B\r
                                              Size: 8.79GB\r
                                             State: online\r
                        Maximum Write Alloc Blocks: 0\r
                                         Used Size: 5.85GB\r
                                 Uses Shared Disks: false\r
                                       UUID String: b5cfe36e-ea\r
                                 Number Of Volumes: 6
                             Is Flash Pool Caching: -\r
            Is Eligible for Auto Balance Aggregate: false\r
             State of the aggregate being balanced: ineligible\r
                          Total Physical Used Size: 68.84MB\r
                          Physical Used Percentage: 1%\r
            State Change Counter for Auto Balancer: 0\r
                                      Is Encrypted: false\r
                                     SnapLock Type: non-snaplock\r
                                 Encryption Key ID: -\r
 Is in the precommit phase of Copy-Free Transition: false\r
                              Is a 7-Mode of space: false\r
Threshold When Aggregate Is Considered Unbalanced (%): 70\r
Threshold When Aggregate Is Considered Balanced (%): 40\r
                        Resynchronization Priority: -\r
                    Space Saved by Data Compaction: 0B\r
               Percentage Saved by Data Compaction: 0%\r
                          Amount of compacted data: 0B\r
3 entries were displayed.\r
"""

LUN_INFO = """              Vserver Name: svm5\r
                  LUN Path: /vol/lun_0_vol/lun_0\r
               Volume Name: lun_0_vol\r
                Qtree Name: ""\r
                  LUN Name: lun_0\r
                  LUN Size: 512MB\r
                   OS Type: linux\r
         Space Reservation: enabled\r
             Serial Number: wpEzy]QpkWFm\r
       Serial Number (Hex): 7770457a795d51706b57466d\r
                   Comment:\r
Space Reservations Honored: true\r
          Space Allocation: disabled\r
                     State: online\r
                  LUN UUID: d4d1c11a-fa21-4ef8-9536-776017748474\r
                    Mapped: unmapped
                Block Size: 512\r
          Device Legacy ID: -\r
          Device Binary ID: -\r
            Device Text ID: -\r
                 Read Only: false\r
     Fenced Due to Restore: false\r
                 Used Size: 0\r
       Maximum Resize Size: 64.00GB\r
             Creation Time: 5/7/2021 18:34:52\r
                     Class: regular\r
      Node Hosting the LUN: cl-01\r
          QoS Policy Group: -\r
       Caching Policy Name: -\r
                     Clone: false\r
  Clone Autodelete Enabled: false\r
       Inconsistent Import: false\r
       """

FS_INFO = """\r
                                   Vserver Name: cl-01\r
                                    Volume Name: vol0\r
                                 Aggregate Name: aggr0\r
  List of Aggregates for FlexGroup Constituents: -\r
                                    Volume Size: 807.3MB\r
                             Volume Data Set ID: -\r
                      Volume Master Data Set ID: -\r
                                   Volume State: online\r
                                   Volume Style: flex\r
                          Extended Volume Style: flexvol\r
                         Is Cluster-Mode Volume: false\r
                          Is Constituent Volume: false\r
                                  Export Policy: -\r
                                        User ID: -\r
                                       Group ID: -\r
                                 Security Style: -\r
                               UNIX Permissions: ------------\r
                                  Junction Path: -\r
                           Junction Path Source: -\r
                                Junction Active: -\r
                         Junction Parent Volume: -\r
                                        Comment: -\r
                                 Available Size: 135.4MB\r
                                Filesystem Size: 807.3MB\r
                        Total User-Visible Size: 766.9MB\r
                                      Used Size: 631.5MB\r
                                Used Percentage: 83%\r
           Volume Nearly Full Threshold Percent: 95%\r
                  Volume Full Threshold Percent: 98%\r
           Maximum Autosize (for flexvols only): 968.7MB\r
                               Minimum Autosize: 807.3MB\r
             Autosize Grow Threshold Percentage: 85%\r
           Autosize Shrink Threshold Percentage: 50%\r
                                  Autosize Mode: off\r
            Total Files (for user-visible data): 24539\r
             Files Used (for user-visible data): 16715\r
                      Space Guarantee in Effect: true\r
                            Space SLO in Effect: true\r
                                      Space SLO: none\r
                          Space Guarantee Style: volume\r
                             Fractional Reserve: 100%\r
                                    Volume Type: RW\r
              Snapshot Directory Access Enabled: true\r
             Space Reserved for Snapshot Copies: 5%\r
                          Snapshot Reserve Used: 604%\r
                                Snapshot Policy: -\r
                                  Creation Time: Mon Mar 08 14:09:37 2021\r
                                       Language: -\r
                                   Clone Volume: -\r
                                      Node name: cl-01\r
                      Clone Parent Vserver Name: -\r
                        FlexClone Parent Volume: -\r
                                  NVFAIL Option: on\r
                          Volume's NVFAIL State: false\r
        Force NVFAIL on MetroCluster Switchover: off\r
                      Is File System Size Fixed: false\r
                     (DEPRECATED)-Extent Option: off\r
                  Reserved Space for Overwrites: 0B\r
              Primary Space Management Strategy: volume_grow\r
                       Read Reallocation Option: off\r
    Naming Scheme for Automatic Snapshot Copies: ordinal\r
               Inconsistency in the File System: false\r
                   Is Volume Quiesced (On-Disk): false\r
                 Is Volume Quiesced (In-Memory): false\r
      Volume Contains Shared or Compressed Data: false\r
              Space Saved by Storage Efficiency: 0B\r
         Percentage Saved by Storage Efficiency: 0%\r
                   Space Saved by Deduplication: 0B\r
              Percentage Saved by Deduplication: 0%\r
                  Space Shared by Deduplication: 0B\r
                     Space Saved by Compression: 0B\r
          Percentage Space Saved by Compression: 0%\r
            Volume Size Used by Snapshot Copies: 243.7MB\r
                                     Block Type: 64-bit\r
                               Is Volume Moving: -\r
                 Flash Pool Caching Eligibility: read-write\r
  Flash Pool Write Caching Ineligibility Reason: -\r
                     Managed By Storage Service: -\r
Create Namespace Mirror Constituents For SnapDiff Use: -\r
                        Constituent Volume Role: -\r
                          QoS Policy Group Name: -\r
                            Caching Policy Name: -\r
                Is Volume Move in Cutover Phase: -\r
        Number of Snapshot Copies in the Volume: 8\r
VBN_BAD may be present in the active filesystem: false\r
                Is Volume on a hybrid aggregate: false\r
                       Total Physical Used Size: 671.8MB\r
                       Physical Used Percentage: 83%\r
                                  List of Nodes: -\r
                          Is Volume a FlexGroup: false\r
                                  SnapLock Type: non-snaplock\r
                          Vserver DR Protection: -\r
\r
                                   Vserver Name: svm1\r
                                    Volume Name: svm1_root\r
                                 Aggregate Name: aggr1\r
  List of Aggregates for FlexGroup Constituents: -\r
                                    Volume Size: 800MB\r
                             Volume Data Set ID: 1025\r
                      Volume Master Data Set ID: 2155388521\r
                                   Volume State: online\r
                                   Volume Style: flex\r
                          Extended Volume Style: flexvol\r
                         Is Cluster-Mode Volume: true\r
                          Is Constituent Volume: false\r
                                  Export Policy: default\r
                                        User ID: -\r
                                       Group ID: -\r
                                 Security Style: ntfs\r
                               UNIX Permissions: ------------\r
                                  Junction Path: /\r
                           Junction Path Source: -\r
                                Junction Active: true\r
                         Junction Parent Volume: -\r
                                        Comment:\r
                                 Available Size: 759.8MB\r
                                Filesystem Size: 800MB\r
                        Total User-Visible Size: 760MB\r
                                      Used Size: 244KB\r
                                Used Percentage: 5%\r
           Volume Nearly Full Threshold Percent: 95%\r
                  Volume Full Threshold Percent: 98%\r
           Maximum Autosize (for flexvols only): 960MB\r
                               Minimum Autosize: 800MB\r
             Autosize Grow Threshold Percentage: 85%\r
           Autosize Shrink Threshold Percentage: 50%\r
                                  Autosize Mode: off\r
            Total Files (for user-visible data): 24313\r
             Files Used (for user-visible data): 103\r
                      Space Guarantee in Effect: true\r
                            Space SLO in Effect: true\r
                                      Space SLO: none\r
                          Space Guarantee Style: volume\r
                             Fractional Reserve: 100%\r
                                    Volume Type: RW\r
              Snapshot Directory Access Enabled: false\r
             Space Reserved for Snapshot Copies: 5%\r
                          Snapshot Reserve Used: 0%\r
                                Snapshot Policy: none\r
                                  Creation Time: Mon Mar 08 14:31:03 2021\r
                                       Language: C.UTF-8\r
                                   Clone Volume: false\r
                                      Node name: cl-01\r
                      Clone Parent Vserver Name: -\r
                        FlexClone Parent Volume: -\r
                                  NVFAIL Option: off\r
                          Volume's NVFAIL State: false\r
        Force NVFAIL on MetroCluster Switchover: off\r
                      Is File System Size Fixed: false\r
                     (DEPRECATED)-Extent Option: off\r
                  Reserved Space for Overwrites: 0B\r
              Primary Space Management Strategy: volume_grow\r
                       Read Reallocation Option: off\r
    Naming Scheme for Automatic Snapshot Copies: create_time\r
               Inconsistency in the File System: false\r
                   Is Volume Quiesced (On-Disk): false\r
                 Is Volume Quiesced (In-Memory): false\r
      Volume Contains Shared or Compressed Data: false\r
              Space Saved by Storage Efficiency: 0B\r
         Percentage Saved by Storage Efficiency: 0%\r
                   Space Saved by Deduplication: 0B\r
              Percentage Saved by Deduplication: 0%\r
                  Space Shared by Deduplication: 0B\r
                     Space Saved by Compression: 0B\r
          Percentage Space Saved by Compression: 0%\r
            Volume Size Used by Snapshot Copies: 0B\r
                                     Block Type: 64-bit\r
                               Is Volume Moving: false\r
                 Flash Pool Caching Eligibility: read-write\r
  Flash Pool Write Caching Ineligibility Reason: -\r
                     Managed By Storage Service: -\r
Create Namespace Mirror Constituents For SnapDiff Use: -\r
                        Constituent Volume Role: -\r
                          QoS Policy Group Name: -\r
                            Caching Policy Name: -\r
                Is Volume Move in Cutover Phase: false\r
        Number of Snapshot Copies in the Volume: 0\r
VBN_BAD may be present in the active filesystem: false\r
                Is Volume on a hybrid aggregate: false\r
                       Total Physical Used Size: 244KB\r
                       Physical Used Percentage: 0%\r
                                  List of Nodes: -\r
                          Is Volume a FlexGroup: false\r
                                  SnapLock Type: non-snaplock\r
                          Vserver DR Protection: -\r
\r
                                   Vserver Name: svm1\r
                                    Volume Name: vol_svm1_1\r
                                 Aggregate Name: aggr1\r
  List of Aggregates for FlexGroup Constituents: -\r
                                    Volume Size: 2GB\r
                             Volume Data Set ID: 1027\r
                      Volume Master Data Set ID: 2155388523\r
                                   Volume State: online\r
                                   Volume Style: flex\r
                          Extended Volume Style: flexvol\r
                         Is Cluster-Mode Volume: true\r
                          Is Constituent Volume: false\r
                                  Export Policy: default\r
                                        User ID: -\r
                                       Group ID: -\r
                                 Security Style: ntfs\r
                               UNIX Permissions: ------------\r
                                  Junction Path: -\r
                           Junction Path Source: -\r
                                Junction Active: -\r
                         Junction Parent Volume: -\r
                                        Comment:\r
                                 Available Size: 2.00GB\r
                                Filesystem Size: 2GB\r
                        Total User-Visible Size: 2GB\r
                                      Used Size: 3.84MB\r
                                Used Percentage: 0%\r
           Volume Nearly Full Threshold Percent: 95%\r
                  Volume Full Threshold Percent: 98%\r
           Maximum Autosize (for flexvols only): 2.40GB\r
                               Minimum Autosize: 2GB\r
             Autosize Grow Threshold Percentage: 85%\r
           Autosize Shrink Threshold Percentage: 50%\r
                                  Autosize Mode: off\r
            Total Files (for user-visible data): 62258\r
             Files Used (for user-visible data): 97\r
                      Space Guarantee in Effect: true\r
                            Space SLO in Effect: true\r
                                      Space SLO: none\r
                          Space Guarantee Style: volume\r
                             Fractional Reserve: 100%\r
                                    Volume Type: RW\r
              Snapshot Directory Access Enabled: true\r
             Space Reserved for Snapshot Copies: 0%\r
                          Snapshot Reserve Used: 0%\r
                                Snapshot Policy: default\r
                                  Creation Time: Mon Mar 08 14:32:54 2021\r
                                       Language: C.UTF-8\r
                                   Clone Volume: false\r
                                      Node name: cl-01\r
                      Clone Parent Vserver Name: -\r
                        FlexClone Parent Volume: -\r
                                  NVFAIL Option: off\r
                          Volume's NVFAIL State: false\r
        Force NVFAIL on MetroCluster Switchover: off\r
                      Is File System Size Fixed: false\r
                     (DEPRECATED)-Extent Option: off\r
                  Reserved Space for Overwrites: 0B\r
              Primary Space Management Strategy: volume_grow\r
                       Read Reallocation Option: off\r
    Naming Scheme for Automatic Snapshot Copies: create_time\r
               Inconsistency in the File System: false\r
                   Is Volume Quiesced (On-Disk): false\r
                 Is Volume Quiesced (In-Memory): false\r
      Volume Contains Shared or Compressed Data: false\r
              Space Saved by Storage Efficiency: 0B\r
         Percentage Saved by Storage Efficiency: 0%\r
                   Space Saved by Deduplication: 0B\r
              Percentage Saved by Deduplication: 0%\r
                  Space Shared by Deduplication: 0B\r
                     Space Saved by Compression: 0B\r
          Percentage Space Saved by Compression: 0%\r
            Volume Size Used by Snapshot Copies: 2.98MB\r
                                     Block Type: 64-bit\r
                               Is Volume Moving: false\r
                 Flash Pool Caching Eligibility: read-write\r
  Flash Pool Write Caching Ineligibility Reason: -\r
                     Managed By Storage Service: -\r
Create Namespace Mirror Constituents For SnapDiff Use: -\r
                        Constituent Volume Role: -\r
                          QoS Policy Group Name: -\r
                            Caching Policy Name: -\r
                Is Volume Move in Cutover Phase: false\r
        Number of Snapshot Copies in the Volume: 8\r
VBN_BAD may be present in the active filesystem: false\r
                Is Volume on a hybrid aggregate: false\r
                       Total Physical Used Size: 3.84MB\r
                       Physical Used Percentage: 0%\r
                                  List of Nodes: -\r
                          Is Volume a FlexGroup: false\r
                                  SnapLock Type: non-snaplock\r
                          Vserver DR Protection: -\r
7 entries were displayed."""

EVENT_INFO = """\r
                  Node: cl-01\r
             Sequence#: 9102\r
                  Time: 3/10/2021 18:19:14\r
              Severity: ERROR\r
                Source: mgwd\r
          Message Name: mgmtgwd.configbr.noSNCBackup\r
                 Event: mgmtgwd.confiigured.\r
     Corrective Action: Configutination <destin man pagestion.\r
           Description: This message occurURL is configured.\r
\r
                  Node: cl-01\r
             Sequence#: 7855\r
                  Time: 3/10/2021 10:18:36\r
              Severity: ERROR\r
                Source: mgwd\r
          Message Name: mgmtgwd.configbr.noSNCBackup\r
                 Event: mgmtgwd.configbr.noSNCBackup: \r
     Corrective Action: Configure an o modify -desinformation.\r
           Description: This mes."""

ALERT_INFO = """\r
                  Node: node1\r
               Monitor: node-connect\r
              Alert ID: DualPathToDiskShelf_Alert\r
     Alerting Resource: 50:05:0c:c1:02:00:0f:02\r
             Subsystem: SAS-connect\r
       Indication Time: Mon Mar 10 10:26:38 2021\r
    Perceived Severity: Major\r
        Probable Cause: Connection_establishment_error\r
           Description: Disk shelf 2 does not \r
    Corrective Actions: 1. Halt controller node1 and \r
                        2. Connect disk shelf 2 t\r
                        3. Reboot the halted controllers.\r
                        4. Contact support per.\r
       Possible Effect: Access to disk shelf\r
           Acknowledge: false\r
              Suppress: false\r
                Policy: DualPathToDiskShelf_Policy\r
          Acknowledger: -\r
            Suppressor: -   \r
Additional Information: Shelf uuid: 50:05:0c:c1:02:00:0f:02\r
                        Shelf id: 2\r
                        Shelf Name: 4d.shelf2\r
                        Number of Paths: 1\r
                        Number of Disks: 6\r
                        Adapter connected to IOMA:\r
                        Adapter connected to IOMB: 4d\r
Alerting Resource Name: Shelf ID 2\r
 Additional Alert Tags: quality-of-service, nondisruptive-upgrade\r"""

CONTROLLER_INFO = """\r
                                              Node: cl-01\r
                                             Owner: \r
                                          Location: \r
                                             Model: SIMBOX\r
                                     Serial Number: 4082368-50-7\r
                                         Asset Tag: -\r
                                            Uptime: 1 days 06:17\r
                                   NVRAM System ID: 4082368507\r
                                         System ID: 4082368507\r
                                            Vendor: NetApp\r
                                            Health: true\r
                                       Eligibility: true\r
                           Differentiated Services: false\r
                               All-Flash Optimized: false\r
                               """

PORTS_INFO = """\r
                                        Node: cl-01\r
                                        Port: e0a\r
                                        Link: up\r
                                         MTU: 1500\r
             Auto-Negotiation Administrative: true\r
                Auto-Negotiation Operational: true\r
                  Duplex Mode Administrative: auto\r
                     Duplex Mode Operational: full\r
                        Speed Administrative: auto\r
                           Speed Operational: 1000\r
                 Flow Control Administrative: full\r
                    Flow Control Operational: none\r
                                 MAC Address: 00:0c:29:32:84:bd\r
                                   Port Type: physical\r
                 Interface Group Parent Node: -\r
                 Interface Group Parent Port: -\r
                       Distribution Function: -\r
                               Create Policy: -\r
                            Parent VLAN Node: -\r
                            Parent VLAN Port: -\r
                                    VLAN Tag: -\r
                            Remote Device ID: -\r
                                IPspace Name: Default\r
                            Broadcast Domain: Default\r
                          MTU Administrative: 1500\r
                          Port Health Status: healthy\r
                   Ignore Port Health Status: false\r
                Port Health Degraded Reasons: -\r
\r
                                        Node: cl-01\r
                                        Port: e0b\r
                                        Link: up\r
                                         MTU: 1500\r
             Auto-Negotiation Administrative: true\r
                Auto-Negotiation Operational: true\r
                  Duplex Mode Administrative: auto\r
                     Duplex Mode Operational: full\r
                        Speed Administrative: auto\r
                           Speed Operational: 1000\r
                 Flow Control Administrative: full\r
                    Flow Control Operational: none\r
                                 MAC Address: 00:0c:29:32:84:c7\r
                                   Port Type: physical\r
                 Interface Group Parent Node: -\r
                 Interface Group Parent Port: -\r
                       Distribution Function: -\r
                               Create Policy: -\r
                            Parent VLAN Node: -\r
                            Parent VLAN Port: -\r
                                    VLAN Tag: -\r
                            Remote Device ID: -\r
                                IPspace Name: Default\r
                            Broadcast Domain: Default\r
                          MTU Administrative: 1500\r
                          Port Health Status: healthy\r
                   Ignore Port Health Status: false\r
                Port Health Degraded Reasons: -\r"""

INTERFACE_INFO = """\r
                    Vserver Name: cl\r
          Logical Interface Name: cl-01_mgmt1\r
                            Role: node-mgmt\r
                   Data Protocol: none\r
                       Home Node: cl-01\r
                       Home Port: e0c\r
                    Current Node: cl-01\r
                    Current Port: e0c\r
              Operational Status: up\r
                 Extended Status: -\r
                         Is Home: true\r
                 Network Address: 192.168.159.130\r
                         Netmask: 255.255.255.0\r
             Bits in the Netmask: 24\r
                     Subnet Name: -\r
           Administrative Status: up\r
                 Failover Policy: local-only\r
                 Firewall Policy: mgmt\r
                     Auto Revert: true\r
   Fully Qualified DNS Zone Name: none\r
         DNS Query Listen Enable: false\r
             Failover Group Name: Default\r
                        FCP WWPN: -\r
                  Address family: ipv4\r
                         Comment: -\r
                  IPspace of LIF: Default\r
  Is Dynamic DNS Update Enabled?: -\r
\r
                    Vserver Name: cl\r
          Logical Interface Name: cluster_mgmt\r
                            Role: cluster-mgmt\r
                   Data Protocol: none\r
                       Home Node: cl-01\r
                       Home Port: e0d\r
                    Current Node: cl-01\r
                    Current Port: e0a\r
              Operational Status: up\r
                 Extended Status: -\r
                         Is Home: false\r
                 Network Address: 192.168.159.131\r
                         Netmask: 255.255.255.0\r
             Bits in the Netmask: 24\r
                     Subnet Name: -\r
           Administrative Status: up\r
                 Failover Policy: broadcast-domain-wide\r
                 Firewall Policy: mgmt\r
                     Auto Revert: false\r
   Fully Qualified DNS Zone Name: none\r
         DNS Query Listen Enable: false\r
             Failover Group Name: Default\r
                        FCP WWPN: -\r
                  Address family: ipv6\r
                         Comment: -\r
                  IPspace of LIF: Default\r
  Is Dynamic DNS Update Enabled?: -\r
2 entries were displayed.\r"""

FC_PORT_INFO = """
\r
                          Node: cl-01\r
                       Adapter: 0a\r
                   Description: Fibre Channel Target Adap\r
             Physical Protocol: fibre-channel\r
                 Maximum Speed: 8\r
         Administrative Status: up\r
            Operational Status: online\r
               Extended Status: ADAPTER UP\r
             Host Port Address: 3e8\r
             Firmware Revision: 1.0.0\r
         Data Link Rate (Gbit): 8\r
            Fabric Established: true\r
                   Fabric Name: -\r
        Connection Established: ptp\r
                     Mediatype: ptp\r
              Configured Speed: auto\r
                  Adapter WWNN: 50:0a:09:80:06:32:84:bd\r
                  Adapter WWPN: 50:0a:09:81:06:32:84:bd\r
                   Switch Port: ACME Switch:1\r
    Form Factor Of Transceiver: ACM\r
    Vendor Name Of Transceiver: SFP Vendor\r
    Part Number Of Transceiver: 0000\r
       Revision Of Transceiver: 1.0\r
  Serial Number Of Transceiver: 0000\r
FC Capabilities Of Transceiver: 8 (Gbit/sec)\r
     Vendor OUI Of Transceiver: 0:5:2\r
      Wavelength In Nanometers: 0\r
      Date Code Of Transceiver: 11:04:02\r
       Validity Of Transceiver: true\r
                Connector Used: ACME Connector\r
                 Encoding Used: 0\r
      Is Internally Calibrated: true\r
        Received Optical Power: 10.0 (uWatts)\r
    Is Received Power In Range: true\r
 SPF Transmitted Optical Power: 10.0 (uWatts)\r
        Is Xmit Power In Range: true\r
\r
                          Node: cl-01\r
                       Adapter: 0b\r
                   Description: Fibre Channel Target \r
             Physical Protocol: fibre-channel\r
                 Maximum Speed: 8\r
         Administrative Status: up\r
            Operational Status: online\r
               Extended Status: ADAPTER UP\r
             Host Port Address: 3e9\r
             Firmware Revision: 1.0.0\r
         Data Link Rate (Gbit): 8\r
            Fabric Established: true\r
                   Fabric Name: -\r
        Connection Established: ptp\r
                     Mediatype: ptp\r
              Configured Speed: auto\r
                  Adapter WWNN: 50:0a:09:80:06:32:84:bd\r
                  Adapter WWPN: 50:0a:09:82:06:32:84:bd\r
                   Switch Port: ACME Switch:1\r
    Form Factor Of Transceiver: ACM\r
    Vendor Name Of Transceiver: SFP Vendor\r
    Part Number Of Transceiver: 0000\r
       Revision Of Transceiver: 1.0\r
  Serial Number Of Transceiver: 0000\r
FC Capabilities Of Transceiver: 8 (Gbit/sec)\r
     Vendor OUI Of Transceiver: 0:5:2\r
      Wavelength In Nanometers: 0\r
      Date Code Of Transceiver: 11:04:02\r
       Validity Of Transceiver: true\r
                Connector Used: ACME Connector\r
                 Encoding Used: 0\r
      Is Internally Calibrated: true\r
        Received Optical Power: 10.0 (uWatts)\r
    Is Received Power In Range: true\r
 SPF Transmitted Optical Power: 10.0 (uWatts)\r
        Is Xmit Power In Range: true\r
\r
                          Node: cl-01\r
                       Adapter: 0c\r
                   Description: Fibre Channel Target Adapter)\r
             Physical Protocol: ethernet\r
                 Maximum Speed: 10\r
         Administrative Status: up\r
            Operational Status: online\r
               Extended Status: ADAPTER UP\r
             Host Port Address: 3ea\r
             Firmware Revision: 1.0.0\r
         Data Link Rate (Gbit): 10\r
            Fabric Established: true\r
                   Fabric Name: -\r
        Connection Established: ptp\r
                     Mediatype: ptp\r
              Configured Speed: auto\r
                  Adapter WWNN: 50:0a:09:80:06:32:84:bd\r
                  Adapter WWPN: 50:0a:09:83:06:32:84:bd\r
                   Switch Port: ACME Switch:1\r
    Form Factor Of Transceiver: ACM\r
    Vendor Name Of Transceiver: SFP Vendor\r
    Part Number Of Transceiver: 0000\r
       Revision Of Transceiver: 1.0\r
  Serial Number Of Transceiver: 0000\r
FC Capabilities Of Transceiver: 2,8 (Gbit/sec)\r
     Vendor OUI Of Transceiver: 0:5:2\r
      Wavelength In Nanometers: 0\r
      Date Code Of Transceiver: 11:04:02\r
       Validity Of Transceiver: true\r
                Connector Used: ACME Connector\r
                 Encoding Used: 0\r
      Is Internally Calibrated: true\r
        Received Optical Power: 10.0 (uWatts)\r
    Is Received Power In Range: true\r
 SPF Transmitted Optical Power: 10.0 (uWatts)\r
        Is Xmit Power In Range: true\r
\r
                          Node: cl-01\r
                       Adapter: 0d\r
                   Description: Fibre Channel Target Adapt)\r
             Physical Protocol: ethernet\r
                 Maximum Speed: 10\r
         Administrative Status: up\r
            Operational Status: online\r
               Extended Status: ADAPTER UP\r
             Host Port Address: 3eb\r
             Firmware Revision: 1.0.0\r
         Data Link Rate (Gbit): 10\r
            Fabric Established: true\r
                   Fabric Name: -\r
        Connection Established: ptp\r
                     Mediatype: ptp\r
              Configured Speed: auto\r
                  Adapter WWNN: 50:0a:09:80:06:32:84:bd\r
                  Adapter WWPN: 50:0a:09:84:06:32:84:bd\r
                   Switch Port: ACME Switch:1\r
    Form Factor Of Transceiver: ACM\r
    Vendor Name Of Transceiver: SFP Vendor\r
    Part Number Of Transceiver: 0000\r
       Revision Of Transceiver: 1.0\r
  Serial Number Of Transceiver: 0000\r
FC Capabilities Of Transceiver: 2,8 (Gbit/sec)\r
     Vendor OUI Of Transceiver: 0:5:2\r
      Wavelength In Nanometers: 0\r
      Date Code Of Transceiver: 11:04:02\r
       Validity Of Transceiver: true\r
                Connector Used: ACME Connector\r
                 Encoding Used: 0\r
      Is Internally Calibrated: true\r
        Received Optical Power: 10.0 (uWatts)\r
    Is Received Power In Range: true\r
 SPF Transmitted Optical Power: 10.0 (uWatts)\r
        Is Xmit Power In Range: true\r
\r
                          Node: cl-01\r
                       Adapter: 0e\r
                   Description: Fibre Channel Target Adap)\r
             Physical Protocol: fibre-channel\r
                 Maximum Speed: 16\r
         Administrative Status: up\r
            Operational Status: online\r
               Extended Status: ADAPTER UP\r
             Host Port Address: 3ec\r
             Firmware Revision: 1.0.0\r
         Data Link Rate (Gbit): 16\r
            Fabric Established: true\r
                   Fabric Name: -\r
        Connection Established: ptp\r
                     Mediatype: ptp\r
              Configured Speed: auto\r
                  Adapter WWNN: 50:0a:09:80:06:32:84:bd\r
                  Adapter WWPN: 50:0a:09:85:06:32:84:bd\r
                   Switch Port: ACME Switch:1\r
    Form Factor Of Transceiver: ACM\r
    Vendor Name Of Transceiver: SFP Vendor\r
    Part Number Of Transceiver: 0000\r
       Revision Of Transceiver: 1.0\r
  Serial Number Of Transceiver: 0000\r
FC Capabilities Of Transceiver: 10 (Gbit/sec)\r
     Vendor OUI Of Transceiver: 0:5:2\r
      Wavelength In Nanometers: 0\r
      Date Code Of Transceiver: 11:04:02\r
       Validity Of Transceiver: true\r
                Connector Used: ACME Connector\r
                 Encoding Used: 0\r
      Is Internally Calibrated: true\r
        Received Optical Power: 10.0 (uWatts)\r
    Is Received Power In Range: true\r
 SPF Transmitted Optical Power: 10.0 (uWatts)\r
        Is Xmit Power In Range: true\r
5 entries were displayed.\r"""

DISKS_INFO = """\r
                  Disk: NET-1.1\r
        Container Type: aggregate\r
            Owner/Home: cl-01 / cl-01\r
               DR Home: -\r
    Stack ID/Shelf/Bay: -  / -  / 16\r
                   LUN: 0\r
                 Array: NETAPP_VD_1\r
                Vendor: NETAPP\r
                 Model: VD-1000MB-FZ-520\r
         Serial Number: 07294300
                   UID: 4E455441:50502020:56442D31:\r
                   BPS: 520\r
         Physical Size: 1.00GB\r
              Position: parity\r
Checksum Compatibility: block\r
             Aggregate: aggr0\r
                  Plex: plex0\r
Paths:\r
                LUN Initiatr Side Target Side      Link\r
Controller IniD SwitcSwitch Port Acc Use  Target Port     TPGN  Speed/s IOPS\r
--------------- -------------------- ---  -------------------- -------- ----\r
cl-01      v1 0 N/A  N/A         AO  INU  0000000000000000   0 0 Gb/S 0    0\r
cl-01      v5 0 N/A  N/A         AO  RDY  0000000000000000   0 0 Gb/S 0    0\r
\r
Errors:\r
-
                  Disk: NET-1.2\r
        Container Type: aggregate\r
            Owner/Home: cl-01 / cl-01\r
               DR Home: -\r
    Stack ID/Shelf/Bay: -  / -  / 17\r
                   LUN: 0\r
                 Array: NETAPP_VD_1\r
                Vendor: NETAPP\r
                 Model: VD-1000MB-FZ-520\r
         Serial Number: 07294301\r
                   UID: 4E455441:50502\r
                   BPS: 520\r
         Physical Size: 1.00GB\r
              Position: dparity\r
Checksum Compatibility: block\r
             Aggregate: aggr1\r
                  Plex: plex0\r
Paths:\r
                LUN Initiatr Side Target Side      Link\r
Controller IniD SwitcSwitch Port Acc Use  Target Port     TPGN  Speed/s IOPS\r
--------------- -------------------- ---  -------------------- -------- ----\r
cl-01      v1 0 N/A  N/A         AO  INU  0000000000000000   0 0 Gb/S 0    0\r
cl-01      v5 0 N/A  N/A         AO  RDY  0000000000000000   0 0 Gb/S 0    0\r
\r
Errors:\r
-\r
"""

PHYSICAL_INFO = """
Disk             Type    Vendor   Model                Revision     RPM  BPS\r
---------------- ------- -------- -------------------- -------- ------- ----\r
NET-1.1          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294300\r
NET-1.2          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294301\r
NET-1.3          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294302\r
NET-1.4          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294303\r
NET-1.5          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294304\r
NET-1.6          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294305\r
NET-1.7          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294306\r
NET-1.8          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294307\r
NET-1.9          FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904200\r
NET-1.10         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904201\r
NET-1.11         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904202\r
NET-1.12         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904203\r
NET-1.13         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904204\r
NET-1.14         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294308\r
NET-1.15         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294309\r
NET-1.16         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294310\r
NET-1.17         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294311\r
NET-1.18         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904205\r
NET-1.19         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904206\r
NET-1.20         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904207\r
NET-1.21         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904208\r
NET-1.22         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904209\r
NET-1.23         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904210\r
NET-1.24         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904311\r
NET-1.25         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904312\r
NET-1.26         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07904313\r
NET-1.27         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294312\r
NET-1.28         FCAL    NETAPP   VD-1000MB-FZ-520     0042       15000  520\r
                 SerialNumber: 07294313\r
28 entries were displayed.\r"""

ERROR_DISK_INFO = """Disk             Error Type        Error Text\r
---------------- ----------------- ----------------------------------\r
NET-1.25         diskfail          ."""

QTREES_INFO = """
\r
                      Vserver Name: svm1\r
                       Volume Name: svm1_root\r
                        Qtree Name: ""\r
  Actual (Non-Junction) Qtree Path: /vol/svm1_root\r
                    Security Style: ntfs\r
                       Oplock Mode: enable\r
                  Unix Permissions: -\r
                          Qtree Id: 0\r
                      Qtree Status: normal\r
                     Export Policy: default\r
        Is Export Policy Inherited: true\r
\r
                      Vserver Name: svm1\r
                       Volume Name: vol_svm1_1\r
                        Qtree Name: ""\r
  Actual (Non-Junction) Qtree Path: /vol/vol_svm1_1\r
                    Security Style: ntfs\r
                       Oplock Mode: enable\r
                  Unix Permissions: -\r
                          Qtree Id: 0\r
                      Qtree Status: normal\r
                     Export Policy: default\r
        Is Export Policy Inherited: true\r
\r
                      Vserver Name: svm1\r
                       Volume Name: vol_svm1_1\r
                        Qtree Name: qtree_svm1_1\r
  Actual (Non-Junction) Qtree Path: /vol/vol_svm1_1/qtree_svm1_1\r
                    Security Style: unix\r
                       Oplock Mode: enable\r
                  Unix Permissions: ---rwxrwxrwx\r
                          Qtree Id: 1\r
                      Qtree Status: normal\r
                     Export Policy: default\r
        Is Export Policy Inherited: true\r
\r
                      Vserver Name: svm1\r
                       Volume Name: vol_svm1_2\r
                        Qtree Name: ""\r
  Actual (Non-Junction) Qtree Path: /vol/vol_svm1_2\r
                    Security Style: ntfs\r
                       Oplock Mode: enable\r
                  Unix Permissions: -\r
                          Qtree Id: 0\r
                      Qtree Status: normal\r
                     Export Policy: default\r
        Is Export Policy Inherited: true"""

SHARE_VSERVER_INFO = """
                               Admin      Operational Root\r
Vserver     Type    Subtype    State      State       Volume     Aggregate\r
----------- ------- ---------- ---------- ----------- ---------- ----------\r
svm4.example.com      data    default    running    running  SVC_FC_ NETAPP"""

SHARES_INFO = """
\r
                                      Vserver: svm4.example.com\r
                                        Share: admin$\r
                     CIFS Server NetBIOS Name: NETAPP-NODE01\r
                                         Path: /\r
                             Share Properties: browsable\r
                           Symlink Properties: -\r
                      File Mode Creation Mask: -\r
                 Directory Mode Creation Mask: -\r
                                Share Comment: -\r
                                    Share ACL: -\r
                File Attribute Cache Lifetime: -\r
                                  Volume Name: svm4examplecom_root\r
                                Offline Files: -\r
                Vscan File-Operations Profile: standard\r
            Maximum Tree Connections on Share: 4294967295\r
                   UNIX Group for File Create: -\r
\r
                                      Vserver: svm4.example.com\r
                                        Share: c$\r
                     CIFS Server NetBIOS Name: NETAPP-NODE01\r
                                         Path: /\r
                             Share Properties: oplocks\r
                                               browsable\r
                                               changenotify\r
                                               show-previous-versions\r
                           Symlink Properties: symlinks\r
                      File Mode Creation Mask: -\r
                 Directory Mode Creation Mask: -\r
                                Share Comment: -\r
                                    Share ACL: BUILTIN\r
                File Attribute Cache Lifetime: -\r
                                  Volume Name: svm4examplecom_root\r
                                Offline Files: -\r
                Vscan File-Operations Profile: standard\r
            Maximum Tree Connections on Share: 4294967295\r
                   UNIX Group for File Create: -\r
\r
                                      Vserver: svm4.example.com\r
                                        Share: etc\r
                     CIFS Server NetBIOS Name: NETAPP-NODE01\r
                                         Path: /.vsadmin/config/etc\r
                             Share Properties: browsable\r
                                               changenotify\r
                                               oplocks\r
                                               show-previous-versions\r
                           Symlink Properties: enable\r
                      File Mode Creation Mask: -\r
                 Directory Mode Creation Mask: -\r
                                Share Comment: -\r
                                    Share ACL: Everyone / Full Control\r
                File Attribute Cache Lifetime: -\r
                                  Volume Name: svm4examplecom_root\r
                                Offline Files: manual\r
                Vscan File-Operations Profile: standard\r
            Maximum Tree Connections on Share: 4294967295\r
                   UNIX Group for File Create: -\r
\r
                                      Vserver: svm4.example.com\r
                                        Share: ipc$\r
                     CIFS Server NetBIOS Name: NETAPP-NODE01\r
                                         Path: /\r
                             Share Properties: browsable\r
                           Symlink Properties: -\r
                      File Mode Creation Mask: -\r
                 Directory Mode Creation Mask: -\r
                                Share Comment: -\r
                                    Share ACL: -\r
                File Attribute Cache Lifetime: -\r
                                  Volume Name: svm4examplecom_root\r
                                Offline Files: -\r
                Vscan File-Operations Profile: standard\r
            Maximum Tree Connections on Share: 4294967295\r
                   UNIX Group for File Create: -\r
\r
                                      Vserver: svm4.example.com\r
                                        Share: vol_svm4_1\r
                     CIFS Server NetBIOS Name: NETAPP-NODE01\r
                                         Path: /vol_svm4_1\r
                             Share Properties: oplocks\r
                                               browsable\r
                                               changenotify\r
                                               show-previous-versions\r
                           Symlink Properties: symlinks\r
                      File Mode Creation Mask: -\r
                 Directory Mode Creation Mask: -\r
                                Share Comment: -\r
                                    Share ACL: Everyone / Full Control\r
                File Attribute Cache Lifetime: -\r
                                  Volume Name: vol_svm4_1\r
                                Offline Files: manual\r
                Vscan File-Operations Profile: standard\r
            Maximum Tree Connections on Share: 4294967295\r
                   UNIX Group for File Create: -"""

SHARES_AGREEMENT_INFO = """
vserver allowed-protocols\r
------- -----------------\r
svm4.example.com 
nfs,cifs,fcp,iscsi\r
7 entries were displayed.\r
"""

THIN_FS_INFO = """
Vserver Volume Aggregate State Type Size Available Used%\r
--------- ------------ ------------ ---------- ---- -\r
svm1 vol_svm1_2 aggr1 online RW 2GB 2.00GB 0%\r"""

TRAP_MAP = {
    '1.3.6.1.4.1.789.1.1.12.0':
        'LUN.inconsistent.filesystem:The on-disk structure of the LUN at path '
        'test in volume 0 (DSID 0) is inconsistent in the WAFL file system.',
    '1.3.6.1.4.1.789.1.1.9.0': '1-80-000008'
}


QUOTAS_INFO = """\r
                 Vserver: svm5\r
             Policy Name: default\r
             Volume Name: svm5_vol1\r
                    Type: tree\r
                  Target: qtree_21052021_110317_94\r
              Qtree Name: ""\r
            User Mapping: -\r
              Disk Limit: 4.88MB\r
             Files Limit: 1000\r
Threshold for Disk Limit: 4.88MB\r
         Soft Disk Limit: 4.88MB\r
        Soft Files Limit: 1000\r
\r
                 Vserver: svm5\r
             Policy Name: default\r
             Volume Name: svm5_vol1\r
                    Type: user\r
                  Target: ""\r
              Qtree Name: ""\r
            User Mapping: off\r
              Disk Limit: 4.88MB\r
             Files Limit: 1000\r
Threshold for Disk Limit: 4.88MB\r
         Soft Disk Limit: 4.88MB\r
        Soft Files Limit: 1000\r
\r
                 Vserver: svm5\r
             Policy Name: default\r
             Volume Name: svm5_vol1\r
                    Type: group\r
                  Target: ""\r
              Qtree Name: ""\r
            User Mapping: -\r
              Disk Limit: 4.88MB\r
             Files Limit: 1000\r
Threshold for Disk Limit: 4.88MB\r
         Soft Disk Limit: 4.88MB\r
        Soft Files Limit: 1000\r
\r
                 Vserver: svm5\r
             Policy Name: default\r
             Volume Name: svm5_vol1\r
                    Type: group\r
                  Target: ""\r
              Qtree Name: qtree_08052021_152034_44\r
            User Mapping: -\r
              Disk Limit: 4.88MB\r
             Files Limit: 100\r
Threshold for Disk Limit: 4.88MB\r
         Soft Disk Limit: 4.88MB\r
        Soft Files Limit: 100\r
\r
                 Vserver: svm5\r
             Policy Name: default\r
             Volume Name: svm5_vol1\r
                    Type: group\r
                  Target: pcuser\r
              Qtree Name: ""\r
            User Mapping: -\r
              Disk Limit: 4.88MB\r
             Files Limit: 1000\r
Threshold for Disk Limit: 4.88MB\r
         Soft Disk Limit: 4.88MB\r
        Soft Files Limit: 1000\r
5 entries were displayed."""
