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

DATA_HEAD_PATTERN = re.compile('[-]{3,}')
ALERT_HEAD_PATTERN = re.compile('[*]{3,}')
STORAGE_VENDOR = 'Hitachi'
TIME_TYPE = '%Y-%m-%d %H:%M:%S'

OID_TRAP_DATA = '1.3.6.1.4.1.11096.6.1.1'

STORAGE_INFO_COMMAND = "cluster-show"
STORAGE_MODEL_COMMAND = "ver"
LOCATION_COMMAND = 'system-information-get'

DISK_INFO_COMMAND = "sd-list --scsi"

POOL_INFO_COMMAND = "span-list"
POOL_SIZE_COMMAND = "span-space-distribution"

CONTROLLER_INFO_COMMAND = "cluster-show -y"

ALERT_INFO_COMMAND = "event-log-show -w -s -x"
ALERT_TIME = " --from '%s'"
ALERT_FORMAT_TIME = "%Y-%m-%d %H:%M:%S"

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
    'Degraded': constants.StorageStatus.DEGRADED,
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

FS_INDEX = {
    'status_len': 6,
    'id_index': 1,
    'pool_index': 2,
    'status_index': 3,
    'detail_len': 8,
    'total_index': 3,
    'used_index': 4,
    'free_index': 7,
    'type_index': 8,
}

ETH_INDEX = {
    'name_len': 1,
    'name_index': 0,
    'status_len': 2,
    'status_index': 0,
    'ip_len': 2,
    'ip_index': 1,
    'mask_index': 3
}

ALERT_INDEX = {
    'alert_len': 4,
    'table_head': 0,
    'severity_index': 1,
    'year_index': 2,
    'time_index': 3,
    'id_index': 0
}

NODE_INDEX = {
    'node_len': 7,
    'status_index': 2,
    'name_index': 1,
    'id_index': 0
}

POOL_INDEX = {
    'pool_len': 6,
    'total_index': 3,
    'free_index': 0,
    'status_index': 1,
    'name_index': 0,
}

DISK_INDEX = {
    'type_len': 2,
    'model_index': 1,
    'vendor_index': 0,
    'version_index': 2
}
