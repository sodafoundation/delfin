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
import re

from delfin.common import constants

PATTERN = re.compile('[-]{3,}')
STORAGE_VENDOR = 'HITACHI'
TIME_TYPE = '%Y-%m-%d %H:%M:%S%z'

OID_TRAP_DATA = '1.3.6.1.4.1.11096.6.1.1'

STORAGE_INFO_COMMAND = "cluster-show"
STORAGE_MODEL_COMMAND = "ver"
LOCATION_COMMAND = 'system-information-get'

DISK_INFO_COMMAND = "sd-list --scsi"

POOL_INFO_COMMAND = "span-list"
POOL_SIZE_COMMAND = "span-space-distribution"

CONTROLLER_INFO_COMMAND = "cluster-show -y"

ALERT_INFO_COMMAND = "event-log-show -w -s"

FC_PORT_COMMAND = "fc-hports"
FC_SPEED_COMMAND = "fc-link-speed"
ETH_PORT_COMMAND = "ifconfig"

FS_INFO_COMMAND = 'df -k'
FS_STATUS_COMMAND = 'filesystem-list'

CHECK_EVS = 'evs-select %s'
QUOTA_INFO_COMMAND = "quota list %s"

TREE_INFO_COMMAND = 'virtual-volume list --verbose %s'

CIFS_SHARE_COMMAND = 'cifs-share list'

NFS_SHARE_COMMAND = "nfs-export list"

CLUSTER_STATUS = {
    'Robust': constants.StorageStatus.NORMAL,
    'Degraded': constants.StorageStatus.ABNORMAL,
    'Critical': constants.StorageStatus.ABNORMAL,
    'OK': constants.StorageStatus.NORMAL,
    'Failure(s)': constants.StorageStatus.ABNORMAL
}

SEVERITY_MAP = {
    'Severe': constants.Severity.FATAL,
    'Warning': constants.Severity.WARNING,
    'Information': constants.Severity.INFORMATIONAL
}

FS_STATUS_MAP = {
    'Fail!': constants.FilesystemStatus.FAULTY,
    'OK': constants.FilesystemStatus.NORMAL,
    'NoEVS': constants.FilesystemStatus.NORMAL,
    'EVS-D': constants.FilesystemStatus.NORMAL,
    'Hiddn': constants.FilesystemStatus.NORMAL,
    'Clust': constants.FilesystemStatus.FAULTY,
    'Unavl': constants.FilesystemStatus.NORMAL,
    'Check': constants.FilesystemStatus.NORMAL,
    'Fixng': constants.FilesystemStatus.NORMAL,
    'Mount': constants.FilesystemStatus.NORMAL,
    'MntRO': constants.FilesystemStatus.NORMAL,
    'SysLk': constants.FilesystemStatus.NORMAL,
    'SysRO': constants.FilesystemStatus.NORMAL,
    'RepTg': constants.FilesystemStatus.NORMAL,
    'Rcvry': constants.FilesystemStatus.NORMAL,
    'UnMnt': constants.FilesystemStatus.FAULTY,
    'Mntg': constants.FilesystemStatus.NORMAL,
    'Formt': constants.FilesystemStatus.NORMAL,
    'Failg': constants.FilesystemStatus.FAULTY,
    None: constants.FilesystemStatus.NORMAL,
}
