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
    "vendor": "hitachi",
    "model": "hnas",
    "ssh": {
        "host": "192.168.3.211",
        "port": 22,
        "username": "manager",
        "password": "manager",
    }
}

STORAGE_INFO = """\r
cluster-show\r

HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ cluster-show\r
Overall Status = Online\r
Cluster Health = Robust\r
Cluster Mode = Not clustered\r
Cluster Name = pba-hnas-1\r
Cluster UUID = a39f815a-e582-11d6-9000-b76f3098a657\r
Cluster Size = 1\r
   Node Name = pba-hnas-1-1\r
     Node ID = 1\r
Cluster GenId = 1\r
Cluster Master = No\r
\r
pba-hnas-1-1:$ """

VERSION_INFO = """\r
ver\r

HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ ver\r
\r
Model: HNAS 4060\r
\r
Software: 12.7.4221.12 (built 2016-10-28 21:51:37+01:00)\r
\r
Hardware: NAS Platform (M4SJKW1423160)\r
\r
board        MMB1\r
mmb          12.7.4221.12 release (2016-10-28 21:51:37+01:00)\r
\r
board        MFB2\r
mfb2hw       MB v0132 WL v0132 TD v0132 FD v0132 TC v00C6 RY v00C6 \r
TY v00C6 IC v00C6 WF v007C FS v007C OS v007C WD v007C D0 v0077 \r
Serial no    B1423125 (Tue Jun 17 13:38:33 2014)\r
\r
board        MCP\r
Serial no    B1423160 (Wed Jun 18 20:39:53 2014)\r
\r
pba-hnas-1-1:$ """

LOCATION_INFO = """\r
system-information-get\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ system-information-get\r
\r
      Name: pba-hnas-1\r
  Location: chengdu\r
   Contact: \r
\r
pba-hnas-1-1:$ """

DISK_INFO = """\r
sd-list --scsi\r

HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ sd-list --scsi\r
Device ID:      0\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span1' (capacity 200GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:00\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            0\r
Serial number:  212902\r
Site ID:        0\r
Tier:           1\r
HDS ctrlr port: 0000\r
HDS dev name:   1000\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      1\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span1' (capacity 200GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:01\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            1\r
Serial number:  212902\r
Site ID:        0\r
Tier:           1\r
HDS ctrlr port: 0400\r
HDS dev name:   1001\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      2\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span1' (capacity 200GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:02\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            2\r
Serial number:  212902\r
Site ID:        0\r
Tier:           1\r
HDS ctrlr port: 0000\r
HDS dev name:   1002\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      3\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span1' (capacity 200GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:03\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            3\r
Serial number:  212902\r
Site ID:        0\r
Tier:           1\r
HDS ctrlr port: 0400\r
HDS dev name:   1003\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      4\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:04\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            4\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0000\r
HDS dev name:   1004\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      5\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:05\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            5\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0400\r
HDS dev name:   1005\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      6\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:06\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            6\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0000\r
HDS dev name:   1006\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      7\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:07\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            7\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0400\r
HDS dev name:   1007\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      8\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:08\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            8\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0400\r
HDS dev name:   1008\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      9\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:09\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            9\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0000\r
HDS dev name:   1009\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      10\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:0A\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            10\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0400\r
HDS dev name:   100A\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
Device ID:      11\r
Comment:        \r
Capacity:       50GiB (53687746560 bytes)\r
Status:         OK\r
Role:           Primary\r
Access:         Allowed\r
Used in span:   'span2' (capacity 400GiB)\r
Type:           Make: HITACHI; Model: OPEN-V; Revision: 7303\r
Submodel:       HM70\r
Luid:           [03:01:00]60:06:0E:80:13:32:66:00:50:20:32:66:00:00:10:0B\r
Blocksize:      512\r
Superflush:     Default\r
Lun:            11\r
Serial number:  212902\r
Site ID:        0\r
Tier:           None\r
HDS ctrlr port: 0000\r
HDS dev name:   100B\r
HDP pool no:    0\r
GAD:            No\r
Queue depth:    min 16, default 32, max 512, configured [default],
 effective 32\r
\r
pba-hnas-1-1:$ """

POOL_INFO = """\r
span-list\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ span-list\r
Span instance name     OK?  Free  Cap/GiB  System drives              Con\r
---------------------  ---  ----  -------  -------------------------  ---\r
span1                  Yes  100%      200  0,1,2,3                    90%\r
   Tier 0: empty: file systems can't be created or mounted\r
   Tier 1: capacity     200GiB; free: 200GiB (100%); HDP pool free 996GiB\r
span2                  Yes   86%      400  4,5,6,7;8,9,10,11          90%\r
pba-hnas-1-1:$ """

POOL_DETAIL_INFO = """\r
\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ span-space-distribution\r
Span span2:\r
\r
  How each stripeset is used:\r
    Stripeset 0:\r
              18GiB     9.09%   fs1\r
              18GiB     9.09%   fs2\r
              18GiB     9.09%   fs3\r
             145GiB    72.74%   [Free space]\r
    Stripeset 1:\r
             200GiB   100.00%   [Free space]\r
\r
  Where each filesystem resides:\r
    Filesystem fs1:\r
      Stripeset  0            18GiB   100.00%\r
    Filesystem fs2:\r
      Stripeset  0            18GiB   100.00%\r
    Filesystem fs3:\r
      Stripeset  0            18GiB   100.00%\r
\r
Span span1:\r
\r
  How each stripeset is used:\r
    Stripeset 0:\r
             200GiB   100.00%   [Free space]\r
\r
  Where each filesystem resides:\r
\r
pba-hnas-1-1:$"""

ALERT_INFO = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ event-log-show -w -s\r
****** Current time : 2021-10-25 11:12:35+08:00 ******\r
8208 Information 2021-11-02 08:26:01+08:00 Chassis device 'md0'
is running background media scan.\r
    CAUSE:      Chassis drive volume is running a media check.\r
    RESOLUTION: No Action required.\r
\r
8462 Warning     2021-11-02 08:00:10+08:00 [ pba-hnas-1 ] The
SMU does not have an email
alert profile relating to a managed server.\r
    CAUSE:      An email alert profile relating to a managed
    server must be applied to the SMU so that alert and diagnostic
    emails can be sent to the required recipients.\r
    RESOLUTION: Go to an SMTP Email Profile page and apply a
    profile to the SMU.\r
\r
8208 Information 2021-11-02 04:04:01+08:00 Chassis device 'md2'
is running background media scan.\r
    CAUSE:      Chassis drive volume is running a media check.\r
    RESOLUTION: No Action required.\r
\r
8209 Information 2021-11-02 04:04:00+08:00 Chassis device 'md3'
has completed background media scan.\r
    CAUSE:      Chassis drive volume media check has completed.\r
    RESOLUTION: No Action required.\r
\r
9995 Information 2021-11-01 20:50:36+08:00 wq test snmp.\r
    CAUSE:      A test event was requested.\r
    RESOLUTION: No action required.\r
\r\
3303 Information 2021-11-01 19:27:22+08:00 Exceeded socket backlog:
dropping additional connection request from 127.0.0.1:34008->127.0.0.1:206:
this event, Id 3303, happened once in the last 6.25 d on the MMB1.\r
    CAUSE:      Socket backlogged: could not allow a new connection.\r
    RESOLUTION: This is expected behavior on receiving a flurry of
    connection requests.  If it happens in other circumstances,
    run the Performance Info Report, then report this and send the
    PIR results to your support provider.\r
\r
8208 Information 2021-11-01 16:44:01+08:00 Chassis device 'md3' is
running background media scan.\r
    CAUSE:      Chassis drive volume is running a media check.\r
    RESOLUTION: No Action required.\r
\r
8462 Warning     2021-11-01 08:00:10+08:00 [ pba-hnas-1 ] The SMU
does not have an email alert profile relating to a managed server.\r
    CAUSE:      An email alert profile relating to a managed server
    must be applied to the SMU so that alert and diagnostic emails
    can be sent to the required recipients.\r
    RESOLUTION: Go to an SMTP Email Profile page and apply a profile
    to the SMU.\r
****** Current time : 2021-10-25 11:12:35+08:00 ******\r
pba-hnas-1-1:$ """

TRAP_INFO = {
    '1.3.6.1.4.1.11096.6.1.1':
        "8462 Warning: [ pba-hnas-1 ] The SMU does not have an email alert "
        "profile relating to a managed server."
}

NODE_INFO = """Linux pba-hnas-1 2.6.32-5-amd64 #1 SMP Sun Dec 21 18:
01:12 UTC 2014 x86_64\r
\r
\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ cluster-show -y\r
                                           Ethernet    Mgmnt\r
ID  Node Name        Status    FS Access   Aggs        Netwrk  FC   EVS IDs\r
--  ---------------  --------  ----------  ----------  ------  ---  -------\r
1   pba-hnas-1-1     ONLINE    OK          Degraded    OK      OK   [0,1,2]\r
\r
Cluster Communications Status:\r
\r
Cluster Interconnect\r
From  To=> Node 1  Node 2  \r
Node 1       --      OK   \r
Node 2       OK      --   \r
\r
Management Network\r
From  To=> Node 1  Node 2  \r
Node 1       --      OK   \r
Node 2       OK      --   \r
pba-hnas-1-1:$ """

FC_PORT_INFO = """\r
fc-hports\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ fc-hports\r
\r
Host Port 1\r
Addrs: 0x1\r
Port name: 50:03:01:70:00:06:8B:01\r
Node name: 50:03:01:70:00:06:8B:00 \r
FC Link is up\r
Status : Good \r
\r
Host Port 2\r
Addrs: not assigned\r
Port name: 50:03:01:70:00:06:8B:02\r
Node name: 50:03:01:70:00:06:8B:00 \r
FC Link is down\r
\r
Host Port 3\r
Addrs: 0x1\r
Port name: 50:03:01:70:00:06:8B:03\r
Node name: 50:03:01:70:00:06:8B:00 \r
FC Link is up\r
Status : Good \r
\r
Host Port 4\r
Addrs: not assigned\r
Port name: 50:03:01:70:00:06:8B:04\r
Node name: 50:03:01:70:00:06:8B:00 \r
FC Link is down\r
\r
pba-hnas-1-1:$ """

FC_PORT_STATUS = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ fc-link-speed\r
FC 1:      8 Gbps\r
FC 2:      4 Gbps\r
FC 3:      8 Gbps\r
FC 4:      8 Gbps\r
pba-hnas-1-1:$ """

ETH_PORT_INFO = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ ifconfig\r
ag1       Link encap:1         HWaddr 00-30-17-09-fc-08\r
          inet addr:192.168.0.1  Bcast:192.168.0.255  mask:255.255.255.0\r
          inet addr:192.168.0.2  Bcast:192.168.0.255  mask:255.255.255.0\r
          Link:DOWN Admin:UP   MTU:1500  Metric:1  txqueuelen:64\r
\r
ag2       Link encap:1         HWaddr 00-30-17-09-fc-09\r
          Link:DOWN Admin:DOWN MTU:1500  Metric:1  txqueuelen:64\r
\r
c1        Link encap:1         HWaddr 00-30-17-09-fc-10\r
          inet addr:240.152.166.87  Bcast:240.255.255.255  mask:255.0.0.0\r
          Link:DOWN Admin:UP   MTU:1488  Metric:2  txqueuelen:64\r
\r
c2        Link encap:1         HWaddr 00-30-17-09-fc-11\r
          Link:DOWN Admin:DOWN MTU:1488  Metric:2  txqueuelen:64\r
\r
eth0      Link encap:1         HWaddr 0c-c4-7a-05-9e-a0\r
          inet addr:192.168.3.211  Bcast:192.168.3.255  mask:255.255.255.0\r
          inet6 addr: fe80::ec4:7aff:fe05:9ea0/64 Scope:Link\r
          Link:UP   Admin:UP   MTU:1500  Metric:4  txqueuelen:64\r
\r
eth1      Link encap:1         HWaddr 0c-c4-7a-05-9e-a1\r
          inet addr:192.0.2.2  Bcast:192.0.255.255  mask:255.255.0.0\r
          inet addr:192.0.2.200  Bcast:192.0.255.255  mask:255.255.0.0\r
          Link:DOWN Admin:UP   MTU:1500  Metric:4  txqueuelen:64\r
\r
lo        Link encap:1         \r
          inet addr:127.0.0.1  Bcast:127.255.255.255  mask:255.0.0.0\r
          inet6 addr: ::1/128 Scope:Global\r
          inet6 addr: fe80::200:ff:fe00:0/64 Scope:Link\r
          Link:UP   Admin:UP   MTU:1500  Metric:4  txqueuelen:64\r
\r
pba-hnas-1-1:$ """

FS_INFO = """\r
filesystem-list\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ filesystem-list\r
Instance name      Dev   On span      State  EVS  Cap/GiB  Confined Flag\r
-----------------  ----  -----------  -----  ---  -------  -------- ----\r
fs1                1024  span2        Mount   1        18       20      \r
pba-hnas-1-1:$ """

QTREE_INFO = """\r
evs-select 1\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ evs-select 1\r
pba-hnas-1-1[EVS1]:$ virtual-volume list --verbose fs1\r
tree1\r
  email        : \r
  root         : /12323\r
  tag          : 2\r
  usage  bytes : 0 B  files: 1\r
  last modified: 2021-09-23 07:18:14.714807865+00:00\r
vol2\r
  email        : \r
  root         : /123\r
  tag          : 1\r
  usage  bytes : 0 B  files: 1\r
  last modified: 2021-09-15 07:17:02.790323869+00:00\r
pba-hnas-1-1[EVS1]:$ """

CIFS_SHARE_INFO = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ evs-select 1\r
pba-hnas-1-1[EVS1]:$ cifs-share list\r
\r
           Share name: tree1\r
           Share path: \12323\r
          Share users: 0\r
         Share online: Yes\r
        Share comment: Share associated with Virtual Volume tree1\r
        Cache options: Manual local caching for documents\r
            ABE enabled: No\r
Continuous Availability: No\r
       Access snapshots: Yes\r
      Display snapshots: Yes\r
     ShadowCopy enabled: Yes\r
   Lower case on create: No\r
        Follow symlinks: Yes\r
 Follow global symlinks: No\r
       Scan for viruses: Yes\r
     File system label: fs1\r
      File system size: 18 GB\r
File system free space: 15.6 GB\r
     File system state: \r
                formatted = Yes\r
                  mounted = Yes\r
                   failed = No\r
         thin provisioned = No\r
Disaster recovery setting:\r
Recovered = No\r
Transfer setting = Use file system default\r
     Home directories: Off\r
  Mount point options:\r
\r
           Share name: C$\r
           Share path: \\r
          Share users: 0\r
         Share online: Yes\r
        Share comment: Default share\r
        Cache options: Manual local caching for documents\r
            ABE enabled: No\r
Continuous Availability: No\r
       Access snapshots: Yes\r
      Display snapshots: No\r
     ShadowCopy enabled: Yes\r
   Lower case on create: No\r
        Follow symlinks: Yes\r
 Follow global symlinks: No\r
       Scan for viruses: Yes\r
      File system info: *** not available ***\r
Disaster recovery setting:\r
Recovered = No\r
Transfer setting = Use file system default\r
Home directories: Off\r
  Mount point options:\r
\r
\r
           Share name: vol6\r
           Share path: \666\r
          Share users: 0\r
         Share online: No\r
        Share comment: Share associated with Virtual Volume vol6\r
        Cache options: Manual local caching for documents\r
            ABE enabled: No\r
Continuous Availability: No\r
       Access snapshots: Yes\r
      Display snapshots: Yes\r
     ShadowCopy enabled: Yes\r
   Lower case on create: No\r
        Follow symlinks: Yes\r
 Follow global symlinks: No\r
       Scan for viruses: Yes\r
      File system info: *** not available ***\r
Disaster recovery setting:\r
Recovered = No\r
Transfer setting = Use file system default\r
Home directories: Off\r
  Mount point options:\r
  \r
pba-hnas-1-1[EVS1]:$ """

NFS_SHARE_INFO = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ evs-select 1\r
pba-hnas-1-1[EVS1]:$ nfs-export list\r
\r
            Export name: /nfs1\r
            Export path: /\r
      File system label: fs1\r
       File system size: 18 GB\r
 File system free space: 15.6 GB\r
      File system state: \r
               formatted = Yes\r
                 mounted = Yes\r
                  failed = No\r
        thin provisioned = No\r
       Access snapshots: Yes\r
      Display snapshots: Yes\r
           Read Caching: Disabled\r
Disaster recovery setting:\r
Recovered = No\r
Transfer setting = Use file system default\r
\r
Export configuration:\r
192.168.3.163\r
\r
\r
            Export name: /vol6\r
            Export path: /666\r
       File system info: *** not available *** \r
       Access snapshots: Yes\r
      Display snapshots: Yes\r
           Read Caching: Disabled\r
Disaster recovery setting:\r
Recovered = No\r
Transfer setting = Use file system default\r
\r
Export configuration:\r
\r
\r
\r
            Export name: /vol2\r
            Export path: /123\r
      File system label: fs1\r
       File system size: 18 GB\r
 File system free space: 15.6 GB\r
      File system state: \r
               formatted = Yes\r
                 mounted = Yes\r
                  failed = No\r
        thin provisioned = No\r
       Access snapshots: Yes\r
      Display snapshots: Yes\r
           Read Caching: Disabled\r
Disaster recovery setting:\r
Recovered = No\r
Transfer setting = Use file system default\r
\r
Export configuration:\r
\r
\r
pba-hnas-1-1[EVS1]:$ """

FS_DETAIL_INFO = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ df -k\r
\r
  ID  Label  EVS         Size              Used  Snapshots """\
                 + """ Deduped              Avail  Thin     FS Type  \r
----  -----  ---  -----------  ----------------  --------- """\
                 + """   -------  -----------------  ----  -----  \r
1024    fs1    1  18874368 KB  2520544 KB (13%)  0 KB (0%)     """\
                 + """    NA  16353824 KB (87%)    No  32 KB,WFS-2,128 DSBs \r
\r
pba-hnas-1-1:$ """

QUOTA_INFO = """\r
\r
HDS NAS OS Console\r
MAC ID : B7-6F-30-98-A6-57\r
\r
pba-hnas-1-1:$ evs-select 1\r
pba-hnas-1-1[EVS1]:$ quota list fs1\r
Type            : Explicit\r
Target          : Group: root\r
Usage           : 10 GB\r
  Limit         : 1 GB (Soft)\r
  Warning       : 75% (768 MB)\r
  Critical      : 85% (870.4 MB)\r
  Reset         : 5% (51.2 MB)\r
File Count      : 7\r
  Limit         : 213 (Soft)\r
  Warning       : 75% (159)\r
  Critical      : 85% (181)\r
  Reset         : 5% (10)\r
Generate Events : Disabled\r
\r
Type            : Explicit\r
Target          : User: root\r
Usage           : 10 GB\r
  Limit         : 1 GB (Soft)\r
  Warning       : 75% (768 MB)\r
  Critical      : 85% (870.4 MB)\r
  Reset         : 5% (51.2 MB)\r
File Count      : 7\r
  Limit         : 213 (Soft)\r
  Warning       : 75% (159)\r
  Critical      : 85% (181)\r
  Reset         : 5% (10)\r
Generate Events : Disabled\r
\r
Type            : Explicit\r
Target          : ViVol: vol2\r
Usage           : 0 B\r
  Limit         : 1 GB (Soft)\r
  Warning       : 75% (768 MB)\r
  Critical      : 85% (870.4 MB)\r
  Reset         : 5% (51.2 MB)\r
File Count      : 1\r
  Limit         : 213 (Soft)\r
  Warning       : 75% (159)\r
  Critical      : 85% (181)\r
  Reset         : 5% (10)\r
Generate Events : Disabled\r
\r
pba-hnas-1-1[EVS1]:$"""
