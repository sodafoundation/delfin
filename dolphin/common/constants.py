# Copyright 2013 OpenStack Foundation
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

# SHARE AND GENERAL STATUSES
STATUS_CREATING = 'creating'
STATUS_DELETING = 'deleting'
STATUS_DELETED = 'deleted'
STATUS_ERROR = 'error'
STATUS_ERROR_DELETING = 'error_deleting'
STATUS_AVAILABLE = 'available'
STATUS_INACTIVE = 'inactive'
STATUS_MANAGING = 'manage_starting'
STATUS_MANAGE_ERROR = 'manage_error'
STATUS_UNMANAGING = 'unmanage_starting'
STATUS_UNMANAGE_ERROR = 'unmanage_error'
STATUS_UNMANAGED = 'unmanaged'
STATUS_EXTENDING = 'extending'
STATUS_EXTENDING_ERROR = 'extending_error'
STATUS_SHRINKING = 'shrinking'
STATUS_SHRINKING_ERROR = 'shrinking_error'
STATUS_MIGRATING = 'migrating'
STATUS_MIGRATING_TO = 'migrating_to'
STATUS_SHRINKING_POSSIBLE_DATA_LOSS_ERROR = (
    'shrinking_possible_data_loss_error'
)
STATUS_REPLICATION_CHANGE = 'replication_change'
STATUS_RESTORING = 'restoring'
STATUS_REVERTING = 'reverting'
STATUS_REVERTING_ERROR = 'reverting_error'

# Access rule states
ACCESS_STATE_QUEUED_TO_APPLY = 'queued_to_apply'
ACCESS_STATE_QUEUED_TO_DENY = 'queued_to_deny'
ACCESS_STATE_APPLYING = 'applying'
ACCESS_STATE_DENYING = 'denying'
ACCESS_STATE_ACTIVE = 'active'
ACCESS_STATE_ERROR = 'error'
ACCESS_STATE_DELETED = 'deleted'

# Share instance "access_rules_status" field values
SHARE_INSTANCE_RULES_SYNCING = 'syncing'
SHARE_INSTANCE_RULES_ERROR = 'error'

# States/statuses for multiple resources
STATUS_NEW = 'new'
STATUS_OUT_OF_SYNC = 'out_of_sync'
STATUS_ACTIVE = 'active'

ACCESS_RULES_STATES = (
    ACCESS_STATE_QUEUED_TO_APPLY,
    ACCESS_STATE_QUEUED_TO_DENY,
    ACCESS_STATE_APPLYING,
    ACCESS_STATE_DENYING,
    ACCESS_STATE_ACTIVE,
    ACCESS_STATE_ERROR,
    ACCESS_STATE_DELETED,
)

TASK_STATE_MIGRATION_STARTING = 'migration_starting'
TASK_STATE_MIGRATION_IN_PROGRESS = 'migration_in_progress'
TASK_STATE_MIGRATION_COMPLETING = 'migration_completing'
TASK_STATE_MIGRATION_SUCCESS = 'migration_success'
TASK_STATE_MIGRATION_ERROR = 'migration_error'
TASK_STATE_MIGRATION_CANCELLED = 'migration_cancelled'
TASK_STATE_MIGRATION_DRIVER_STARTING = 'migration_driver_starting'
TASK_STATE_MIGRATION_DRIVER_IN_PROGRESS = 'migration_driver_in_progress'
TASK_STATE_MIGRATION_DRIVER_PHASE1_DONE = 'migration_driver_phase1_done'
TASK_STATE_DATA_COPYING_STARTING = 'data_copying_starting'
TASK_STATE_DATA_COPYING_IN_PROGRESS = 'data_copying_in_progress'
TASK_STATE_DATA_COPYING_COMPLETING = 'data_copying_completing'
TASK_STATE_DATA_COPYING_COMPLETED = 'data_copying_completed'
TASK_STATE_DATA_COPYING_CANCELLED = 'data_copying_cancelled'
TASK_STATE_DATA_COPYING_ERROR = 'data_copying_error'

BUSY_TASK_STATES = (
    TASK_STATE_MIGRATION_STARTING,
    TASK_STATE_MIGRATION_IN_PROGRESS,
    TASK_STATE_MIGRATION_COMPLETING,
    TASK_STATE_MIGRATION_DRIVER_STARTING,
    TASK_STATE_MIGRATION_DRIVER_IN_PROGRESS,
    TASK_STATE_MIGRATION_DRIVER_PHASE1_DONE,
    TASK_STATE_DATA_COPYING_STARTING,
    TASK_STATE_DATA_COPYING_IN_PROGRESS,
    TASK_STATE_DATA_COPYING_COMPLETING,
    TASK_STATE_DATA_COPYING_COMPLETED,
)

BUSY_COPYING_STATES = (
    TASK_STATE_DATA_COPYING_STARTING,
    TASK_STATE_DATA_COPYING_IN_PROGRESS,
    TASK_STATE_DATA_COPYING_COMPLETING,
)

TRANSITIONAL_STATUSES = (
    STATUS_CREATING, STATUS_DELETING,
    STATUS_MANAGING, STATUS_UNMANAGING,
    STATUS_EXTENDING, STATUS_SHRINKING,
    STATUS_MIGRATING, STATUS_MIGRATING_TO,
    STATUS_RESTORING, STATUS_REVERTING,
)

INVALID_SHARE_INSTANCE_STATUSES_FOR_ACCESS_RULE_UPDATES = (
    TRANSITIONAL_STATUSES + (STATUS_ERROR,)
)

SUPPORTED_SHARE_PROTOCOLS = (
    'NFS', 'CIFS', 'GLUSTERFS', 'HDFS', 'CEPHFS', 'MAPRFS')

SECURITY_SERVICES_ALLOWED_TYPES = ['active_directory', 'ldap', 'kerberos']

LIKE_FILTER = ['name~', 'description~']

NFS_EXPORTS_FILE = '/etc/exports'
NFS_EXPORTS_FILE_TEMP = '/var/lib/nfs/etab'

MOUNT_FILE = '/etc/fstab'
MOUNT_FILE_TEMP = '/etc/mtab'

# Below represented ports are ranges (from, to)
CIFS_PORTS = (
    ("tcp", (445, 445)),
    ("tcp", (137, 139)),
    ("udp", (137, 139)),
    ("udp", (445, 445)),
)
NFS_PORTS = (
    ("tcp", (2049, 2049)),
    ("udp", (2049, 2049)),
)
SSH_PORTS = (
    ("tcp", (22, 22)),
)
PING_PORTS = (
    ("icmp", (-1, -1)),
)
WINRM_PORTS = (
    ("tcp", (5985, 5986)),
)

SERVICE_INSTANCE_SECGROUP_DATA = (
    CIFS_PORTS + NFS_PORTS + PING_PORTS + WINRM_PORTS)

ACCESS_LEVEL_RW = 'rw'
ACCESS_LEVEL_RO = 'ro'

ACCESS_LEVELS = (
    ACCESS_LEVEL_RW,
    ACCESS_LEVEL_RO,
)

TASK_STATE_STATUSES = (
    TASK_STATE_MIGRATION_STARTING,
    TASK_STATE_MIGRATION_IN_PROGRESS,
    TASK_STATE_MIGRATION_COMPLETING,
    TASK_STATE_MIGRATION_SUCCESS,
    TASK_STATE_MIGRATION_ERROR,
    TASK_STATE_MIGRATION_CANCELLED,
    TASK_STATE_MIGRATION_DRIVER_IN_PROGRESS,
    TASK_STATE_MIGRATION_DRIVER_PHASE1_DONE,
    TASK_STATE_DATA_COPYING_STARTING,
    TASK_STATE_DATA_COPYING_IN_PROGRESS,
    TASK_STATE_DATA_COPYING_COMPLETING,
    TASK_STATE_DATA_COPYING_COMPLETED,
    TASK_STATE_DATA_COPYING_CANCELLED,
    TASK_STATE_DATA_COPYING_ERROR,
    None,
)

REPLICA_STATE_ACTIVE = 'active'
REPLICA_STATE_IN_SYNC = 'in_sync'
REPLICA_STATE_OUT_OF_SYNC = 'out_of_sync'

REPLICATION_TYPE_READABLE = 'readable'
REPLICATION_TYPE_WRITABLE = 'writable'
REPLICATION_TYPE_DR = 'dr'


class ExtraSpecs(object):

    # Extra specs key names
    DRIVER_HANDLES_SHARE_SERVERS = "driver_handles_share_servers"
    SNAPSHOT_SUPPORT = "snapshot_support"
    REPLICATION_TYPE_SPEC = "replication_type"
    CREATE_SHARE_FROM_SNAPSHOT_SUPPORT = "create_share_from_snapshot_support"
    REVERT_TO_SNAPSHOT_SUPPORT = "revert_to_snapshot_support"
    MOUNT_SNAPSHOT_SUPPORT = "mount_snapshot_support"
    AVAILABILITY_ZONES = "availability_zones"

    # Extra specs containers
    REQUIRED = (
        DRIVER_HANDLES_SHARE_SERVERS,
    )

    OPTIONAL = (
        SNAPSHOT_SUPPORT,
        CREATE_SHARE_FROM_SNAPSHOT_SUPPORT,
        REVERT_TO_SNAPSHOT_SUPPORT,
        REPLICATION_TYPE_SPEC,
        MOUNT_SNAPSHOT_SUPPORT,
        AVAILABILITY_ZONES,
    )

    # NOTE(cknight): Some extra specs are necessary parts of the Manila API and
    # should be visible to non-admin users. REQUIRED specs are user-visible, as
    # are a handful of community-agreed standardized OPTIONAL ones.
    TENANT_VISIBLE = REQUIRED + OPTIONAL

    BOOLEAN = (
        DRIVER_HANDLES_SHARE_SERVERS,
        SNAPSHOT_SUPPORT,
        CREATE_SHARE_FROM_SNAPSHOT_SUPPORT,
        REVERT_TO_SNAPSHOT_SUPPORT,
        MOUNT_SNAPSHOT_SUPPORT,
    )

    # NOTE(cknight): Some extra specs are optional, but a nominal (typically
    # False, but may be non-boolean) default value for each is still needed
    # when creating shares.
    INFERRED_OPTIONAL_MAP = {
        SNAPSHOT_SUPPORT: False,
        CREATE_SHARE_FROM_SNAPSHOT_SUPPORT: False,
        REVERT_TO_SNAPSHOT_SUPPORT: False,
        MOUNT_SNAPSHOT_SUPPORT: False,
    }

    REPLICATION_TYPES = ('writable', 'readable', 'dr')
