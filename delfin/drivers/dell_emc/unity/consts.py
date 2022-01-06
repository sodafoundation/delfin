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

DEFAULT_TIMEOUT = 10
ALERT_TIMEOUT = 20
TRAP_DESC = {
    "1:127486a": ["WARNING", "ALRT_LCC_FW_UPGRADE_FAILED",
                  "The link control card (LCC) will continue to function with "
                  "older versions of the software. The next time the affected "
                  "Storage Processor (SP) reboots, the firmware will attempt "
                  "the upgrade again."],
    "1:127486b": ["WARNING", "ALRT_LCC_FW_UPGRADE_FAILED",
                  "The link control card (LCC) will continue to function with "
                  "older versions of the software. The next time the affected "
                  "Storage Processor (SP) reboots, the firmware will attempt "
                  "the upgrade again."],
    "1:1278982": ["ERROR", "ALRT_DAE_INVALID_DRIVE",
                  "There is an invalid disk in the Disk Array Enclosure (DAE)."
                  " Replace the disk with the correct type."],
    "1:12dc501": ["CRITICAL", "ALRT_SYS_POOL_OFFLINE",
                  "An internal system service is offline. Some system "
                  "capabilities may not be available. Contact your service "
                  "provider"],
    "1:12dcd00": ["CRITICAL", "ALRT_SYS_LUN_OFFLINE",
                  "An internal system service required for metrics is offline."
                  "System metrics are not available. Contact your service "
                  "provider."],
    "1:1670071": ["INFO", "ALRT_PBL_ENV_CLEARED",
                  "The environmental interface failure has been resolved. "
                  "No action is required."],
    "1:1678007": ["ERROR", "ALRT_PBL_ESP_ERROR_FUP_FAILED",
                  "Firmware upgrade has failed. Contact "
                  "your service provider."],
    "1:167800e": ["ERROR", "ALRT_PBL_ESP_ERROR_RESUME_PROM_READ_FAILED",
                  "The Resume Prom Read operation has failed. Contact "
                  "your service provider"],
    "1:167803d": ["CRITICAL", "ALRT_SSD_PECYCLE_EXPIRE",
                  "%2 is predicted to exceed drive specified write endurance "
                  "in %3 days. It is recommended to replace the drive"],
    "1:1678049": ["ERROR", "ALRT_PBL_ENV_FAILURE",
                  "An environmental interface failure has been detected. Gath"
                  "er diagnostic materials and contact your service "
                  "provider."],
    "1:1678052": ["ERROR", "ALRT_PBL_ESP_ERROR_LCC_COMPONENT_FAULTED",
                  "Link Control Card (LCC) has faulted. This failure may be "
                  "caused by a component other than the LCC. Replace the "
                  "faulted disks first. If the problem persists, contact "
                  "your service provider."],
    "1:167805f": ["ERROR", "ALRT_DRIVE_AFA_FAILED",
                  "One of the system drives failed All-Flash check. Replace "
                  "the non-Flash drive with a Flash drive."],
    "1:167c00a": ["ERROR", "ALRT_PBL_ESP_PEERSP_POST_FAIL",
                  "The Storage Processor (SP) has faulted. Contact your "
                  "service provider."],
    "1:1688028": ["ERROR", "ALRT_DISK_USER_DISK_IN_SYSTEM_SLOT",
                  "A bind user disk has been inserted in a system disk slot. "
                  "remove the disk and insert it in a user drive slot."],
    "1:1688029": ["ERROR", "ALRT_DISK_SYSTEM_DISK_IN_USER_SLOT",
                  "A system disk has been inserted in a wrong slot. Remove the"
                  " disk and insert it in a system disk slot."],
    "1:16d80c4": ["INFO", "ALRT_SNAPSHOT_INVALIDATION",
                  "Snapshots have been automatically marked for deletion due "
                  "to insufficient pool space."],
    "1:16f0077": ["INFO", "ALRT_MLU_UDI_RDWT_RESTORE",
                  "The file system is now read-write, because free space in "
                  "its pool has increased more than 12.5 GB."],
    "1:16f0078": ["INFO", "ALRT_MLU_UDI_SNAPS_OK",
                  "The file system is no longer at risk of losing its "
                  "snapshots, because there is now enough free space in Its "
                  "associated pool."],
    "1:16f0079": ["INFO", "ALRT_MLU_UDI_ABOUT_NOT_NEEDING_FULL_SYNC",
                  "The file system no longer needs a full synchronization for "
                  "the associated replication session, because there is enough"
                  " free space in the associated pool."],
    "1:16f4007": ["WARNING",
                  "ALRT_FILESYSTEM_REACHED_CIFS_SHARE_COUNT_THRESHOLD",
                  "Creation of the SMB share has exceeded the 90% threshold "
                  "for the underlying file system or snapshot. Remove "
                  "unnecessary SMB shares from the file system or snapshot."],
    "1:16f4008": ["WARNING",
                  "ALRT_FILESYSTEM_REACHED_NFS_SHARE_COUNT_THRESHOLD",
                  "Creation of the NFS share has exceeded the 90% threshold "
                  "for the underlying file system or snapshot. Remove "
                  "unnecessary NFS shares from the file system or snapshot."],
    "1:16f4009": ["WARNING", "ALRT_MLU_UDI_ABOUT_SNAP_INVALIDATION",
                  "Pool containing the file system is low on free space, and "
                  "the file system will lose all of its snapshots. To retain "
                  "the snapshots, add more space to the pool, free up space "
                  "from the pool, or use the CLI to change the file system's "
                  "pool full policy to failWrites."],
    "1:16f400a": ["WARNING", "ALRT_MLU_UDI_ABOUT_NEEDING_FULL_SYNC",
                  "Pool containing the file system is low on free space, so "
                  "the associated replication session will need a full "
                  "synchronization. To resolve this issue, add more space to "
                  "the pool, free up space from the pool, or use the CLI to "
                  "change the file system's pool full policy to failWrites."],
    "1:16f400b": ["WARNING", "ALRT_POOL_SPACE_LOW",
                  "The pool space is low and the associated  file system is "
                  "configured with a Fail Writes pool full  policy. When the "
                  "pool reaches full capacity, any write operations to this "
                  "file system  may fail. Change the pool full policy for the "
                  "file system using the CLI or add more space to the pool."],
    "1:16f8319": ["ERROR", "ALRT_MLU_UDI_RD_ONLY_SNAP_INVALIDATION",
                  "The file system is now read-only, because the pool's free "
                  "space dropped below 4 GB, and its poolFullPolicy is set to "
                  "failWrites. To make the file system read-write with this "
                  "policy, add space to the pool or free up space until there "
                  "is at least 12.5 GB of free space. Alternatively, use the "
                  "CLI to change the file system's pool full policy to "
                  "deleteAllSnaps."],
    "1:16fc000": ["ERROR", "ALRT_SYS_VDM_OFFLINE",
                  "An internal system service is offline. Some system "
                  "capabilities may not be available. Contact your service "
                  "provider."],
    "1:1744002": ["WARNING", "ALRT_VVNX_VDISK_EXCEED_MAX_COUNT",
                  "The maximum number of virtual disks is exceeded. One or "
                  "more virtual disks will not be available unless you remove"
                  " some existing virtual disks. Check the system "
                  "log for details."],
    "1:174c001": ["CRITICAL", "ALRT_LXF_UNSUPPORTED_SCSI_CONTROLLER",
                  "An unsupported virtual SCSI controller was added to the "
                  "system. You should remove this controller, because it can "
                  "cause problems on the next reboot."],
    "1:1760114": ["INFO", "ALRT_CBE_KEYSTORE_BACKUP_REQUIRED",
                  "The Data at Rest Encryption keystore has been modified due "
                  "to configuration changes on the array. It is very important"
                  " to retrieve and save a copy of the keystore in order to "
                  "secure your data on the array."],
    "1:1768001": ["ERROR", "ALRT_KMIP_SERVER_UNAVAILABLE",
                  "A configured KMIP Server is either unavailable "
                  "or misconfigured."],
    "1:1768002": ["ERROR", "ALRT_KMIP_SERVER_NO_ENCRYPTION_KEY",
                  "ALRT_KMIP_SERVER_NO_ENCRYPTION_KEY",
                  "A configured KMIP Server does not have the encryption "
                  "key for this array"],
    "10:10000": ["WARNING", "ALRT_FILESYSTEM_REACHED_CIFS_SHARE_MAX_COUNT",
                 "A file system has reached a limit of maximum allowed number "
                 "of SMB shares."],
    "10:10001": ["WARNING", "ALRT_FILESYSTEM_REACHED_NFS_SHARE_MAX_COUNT",
                 "A file system has reached a limit of maximum allowed number"
                 " of NFS shares"],
    "12:104e0017": ["CRITICAL", "ALRT_LDAP_NO_CONNECT",
                    "The system could not connect to the LDAP server. This "
                    "impacts your ability to log into the system but does not"
                    " impact data access."],
    "12:104f0003": ["ERROR", "ALRT_TIME_NOT_SYNCED",
                    "There is a significant difference between the clock time"
                    " of the Storage Processor (SP) and the Windows domain "
                    "controller. To resolve time synchronization problems, "
                    "you can set up a network time protocol (NTP) server or "
                    "contact your Windows domain administrator."],
    "12:1074002f": ["CRITICAL", "ALRT_MS_DC_NO_CONNECT",
                    "The system could not connect to the Microsoft Windows "
                    "Domain Controller."],
    "12:10760024": ["CRITICAL", "ALRT_DNS_FAIL_PING",
                    "The DNS server is not available on the network and the "
                    "NX3e system could Not connect."],
    "12:10760025": ["CRITICAL", "ALRT_DNS_INVALID_CONFIG",
                    "The system cannot connect to the DNS server. The DNS "
                    "server may be configured Incorrectly."],
    "13:102b0001": ["ERROR", "ALRT_DUPLICATE_ADDRESS_FOUND",
                    "A duplicate address was detected on the network. The "
                    "address being configured cannot be used, because it is "
                    "being used by another Node."],
    "13:102b0002": ["ERROR", "ALRT_DUPLICATE_ADDRESS_FOUND",
                    "A duplicate address was detected on the network. The "
                    "address being configured cannot be used, because it is "
                    "being used by another node."],
    "13:10360005": ["WARNING", "ALRT_NAS_CA_CERT_EXPIRES_TODAY",
                    "The CA certificate installed on the NAS server will "
                    "expire today. This certificate is required to keep "
                    "SSL-enabled services (such as LDAP with enabled SSL "
                    "security and CA certificate validation) functioning. "
                    "Upon certificate expiration, users may lose access to "
                    "shares on the NAS server, especially when multiprotocol "
                    "sharing is enabled. Contact the system administrator to "
                    "renew the CA certificate, and then upload it to the "
                    "NAS server."],
    "13:10360007": ["WARNING", "ALRT_NAS_CA_CERT_EXPIRES_IN_ONE_WEEK",
                    "The CA certificate installed on the NAS server will "
                    "expire in one week. This certificate is required to keep "
                    "SSL-enabled services (such as LDAP with enabled SSL "
                    "security and CA certificate validation) functioning. "
                    "Once it expires, users may lose access to shares on the"
                    " NAS server, especially when multiprotocol sharing is "
                    "enabled. Contact the system administrator to renew the "
                    "CA certificate, and then upload it to the NAS server."],
    "13:10360008": ["ERROR", "ALRT_NAS_CA_CERT_HAS_EXPIRED",
                    "The CA certificate installed on the NAS server has "
                    "expired. Services that use this certificate to "
                    "validate remote hosts (such as LDAP with enabled SSL "
                    "security and CA certificate validation) will not "
                    "function properly, and corresponding SSL connections "
                    "will be rejected. Users may lose access to shares on "
                    "the NAS server, especially when multiprotocol sharing "
                    "is enabled. Contact the system administrator to renew "
                    "the CA certificate, and then upload it to the "
                    "NAS server."],
    "13:10360009": ["INFO", "ALRT_NAS_CA_CERT_EXPIRES_IN_30_DAYS",
                    "The CA certificate installed on the NAS server will "
                    "expire in 30 days. This certificate is required to "
                    "keep SSL-enabled services (such as LDAP with enabled "
                    "SSL security and CA certificate validation) functioning."
                    " Upon certificate expiration, users may lose access to "
                    "shares on the NAS server, especially when multiprotocol"
                    " sharing is enabled. Contact the system administrator to"
                    " renew the CA certificate, and then upload it to the "
                    "NAS server."],
    "13:1040003c": ["WARNING", "ALRT_BLOCK_USER_SOFTQUOTA",
                    "You have used too much space in the specified file system"
                    " and should delete unwanted files and directories from it"
                    ". Alternatively, the administrator can increase your soft"
                    " quota limit for the file system."],
    "13:1040003d": ["ERROR", "ALRT_BLOCK_USER_SOFTQUOTA_EXPIRED",
                    "You have used too much space in the specified file system"
                    " and will no longer be able to write to the file sysetem"
                    " unless you delete unwanted files and directories from it"
                    ". Alternatively, the administrator can increase your soft"
                    " quota limit for the file system."],
    "13:1040003e": ["ERROR", "ALRT_BLOCK_USER_HARDQUOTA",
                    "You have used too much space in the specified file system"
                    " and will no longer be able to write to it unless you"
                    " delete unwanted files and directories to reduce the"
                    " percentage of used space. Alternatively, the "
                    "administrator can increase your hard quota limit for"
                    " the file system."],
    "13:1040003f": ["WARNING", "ALRT_BLOCK_USER_SOFTQUOTA_CROSSEDWITHINTREE",
                    "You have used too much space in the specified quota tree"
                    " and should delete unwanted files and directories from"
                    " the tree. Alternatively, the administrator can increase"
                    " your soft quota limit for the quota tree."],
    "13:10400040": ["ERROR",
                    "ALRT_BLOCK_USER_SOFTQUOTACROSSED_GRACEEXPIREDWITHINTREE",
                    "You have used too much space in the specified quota tree"
                    " and will no longer be able to write to it unless you"
                    " delete unwanted files and directories to reduce the "
                    "percentage of used space. Alternatively, the "
                    "administrator can increase your soft quota limit for"
                    " that quota tree."],
    "13:10400041": ["ERROR", "ALRT_BLOCK_USER_HARDQUOTAEXCEEDEDWITHINTREE",
                    "You have used too much space in the specified quota tree"
                    " and will no longer be able to write to it unless you"
                    " delete unwanted files and directories to reduce the"
                    " percentage of used space. Alternatively, the "
                    "administrator can increase your hard quota limit for "
                    "the quota tree."],
    "13:10400042": ["WARNING", "ALRT_BLOCK_TREESOFTQUOTACROSSED",
                    "Too much space has been consumed on the specified quota"
                    " tree. You should delete unwanted files and directories"
                    " from the quota tree. Alternatively, the administrator"
                    " can increase the soft quota limit for the quota tree."],
    "13:10400043": ["ERROR", "ALRT_BLOCK_TREESOFTQUOTACROSSED_GRACEEXPIRED",
                    "Too much space has been consumed on the specified quota"
                    " tree. Users will no longer be able to write to the quota"
                    " tree unless they delete unwanted files and directories "
                    "from it. Alternatively, the administrator can increase "
                    "the soft quota limit for the quota tree."],
    "13:10400044": ["ERROR", "ALRT_BLOCK_TREEHARDQUOTAEXCEEDED",
                    "Too much space has been consumed on the specified quota"
                    " tree. Users will no longer be able to write to the quota"
                    " tree unless they delete unwanted files and directories"
                    " from it. Alternatively, the administrator can increase"
                    " the hard quota limit for the quota tree."],
    "13:10400045": ["WARNING", "ALRT_BLOCK_TREESOFTQUOTA_AGGREGATION",
                    "Too much space has been consumed on the specified quota"
                    " tree. You should delete unwanted files and directories"
                    " from the quota tree. Alternatively, the administrator"
                    " can increase the soft quota limit for the quota tree."],
    "13:10400046": ["ERROR", "ALRT_BLOCK_TREEHARDQUOTA_AGGREGATION",
                    "Too much space has been consumed on the specified quota"
                    " tree. Users will no longer be able to write to the"
                    " quota tree unless they delete unwanted files and "
                    "directories from it. Alternatively, the administrator "
                    "can increase the hard quota limit for the quota tree."],
    "13:10400047": ["WARNING", "ALRT_BLOCK_USERSOFTQUOTA_AGGREGATION",
                    "You have used too much space in the specified file"
                    " system and should delete unwanted files and directories"
                    " from it. Alternatively, the administrator can increase"
                    " your soft quota limit for the file system."],
    "13:10400048": ["ERROR", "ALRT_BLOCK_USERHARDQUOTA_AGGREGATION",
                    "You have used too much space in the specified file system"
                    " and will no longer be able to write to the file system"
                    " unless you delete unwanted files and directories from it"
                    ". Alternatively, the administrator can increase your "
                    "quota limits for the file system."],
    "13:10400049": ["WARNING",
                    "ALRT_BLOCK_USERSOFTQUOTAWITHINTREE_AGGREGATION",
                    "You have used too much space in the specified quota tree"
                    " and should delete unwanted files and directories from it"
                    ". Alternatively, the administrator can increase your soft"
                    " quota limit for the quota tree."],
    "13:1040004a": ["ERROR", "ALRT_BLOCK_USERHARDQUOTAWITHINTREE_AGGREGATION",
                    "You have used too much space in the specified quota tree"
                    " and will no longer be able to write to the quota tree"
                    " unless you delete unwanted files and directories from it"
                    ". Alternatively, the administrator can increase your"
                    " quota limits for the quota tree."],
    "13:10490005": ["ERROR", "ALRT_NAS_NIS_UNREACHABLE",
                    "The Network Information Service (NIS) configured for the"
                    " NAS server was unable to provide user mapping "
                    "information and is not responding. Check the availability"
                    " of the NIS server, and ensure that the domain name and "
                    "addresses used for the server are accurate."],
    "13:104e0005": ["ERROR", "ALRT_NAS_LDAP_ALL_UNREACHABLE",
                    "The LDAP service configured for the NAS server was unable"
                    " to provide user mapping information and is no longer "
                    "responding. At least one configured LDAP server needs to "
                    "be operational. Check the availability of the LDAP "
                    "servers, and look for connectivity Issues."],
    "13:104e0007": ["WARNING", "ALRT_NAS_LDAP_BAD_CONFIGURATION",
                    "The LDAP client settings on the NAS server are not "
                    "configured correctly for the domain. You may encounter"
                    " unexpected issues or mapping errors when using LDAP as a"
                    " Unix directory service. Verify account settings. Check "
                    "the binding and access permissions for the "
                    "configured LDAP servers."],
    "13:104f0001": ["ERROR", "ALRT_NAS_CIFSSERVER_TIMENOTSYNC",
                    "The current system time is not synchronized with the "
                    "Active Directory controller of the domain. Check the "
                    "system NTP (Network Time Protocol) settings to ensure the"
                    " your system's time is synchronized with the time of "
                    "the Active Directory controller."],
    "13:10510004": ["CRITICAL", "ALRT_VIRUS_CHECKER_NO_CONNECT",
                    "The system could not connect to your virus Checker"
                    " server."],
    "13:10510005": ["ERROR", "ALRT_VC_ERROR_STOPCIFS",
                    "No virus checker server is available. SMB has stopped and"
                    " cannot resume until a virus checker server becomes "
                    "available. Check the status of the network and the virus"
                    " checker servers."],
    "13:10510006": ["ERROR", "ALRT_VC_ERROR_STOPVC",
                    "The virus checker server is not available. Virus checking"
                    " is paused and cannot resume until a virus checker server"
                    " becomes available. Check the status of the network and"
                    " the virus checker servers."],
    "13:1051000b": ["CRITICAL", "ALRT_VIRUS_SCAN_CMPLTE",
                    "The antivirus scan has completed successfully."],
    "13:1051000c": ["CRITICAL", "ALRT_VIRUS_SCAN_FAIL",
                    "Antivirus scanning has aborted.        ."],
    "13:1051000d": ["CRITICAL", "ALRT_VC_FILE_DELETE",
                    "An infected file was detected and deleted by your "
                    "antivirus application"],
    "13:1051000e": ["CRITICAL", "ALRT_VC_FILE_RENAMED",
                    "An infected file was detected and renamed by your"
                    " antivirus application."],
    "13:1051000f": ["CRITICAL", "ALRT_VC_FILE_MOD",
                    "An infected file was detected and modified by your "
                    "antivirus application."],
    "13:1051001e": ["ERROR", "ALRT_VC_ERROR_SERVER_OFFLINE_MSRPC",
                    "The system could not connect to your virus checker server"
                    ". Check the status of the network and the virus checker"
                    " server."],
    "13:10510021": ["ERROR", "ALRT_VC_ERROR_SERVER_OFFLINE_MSRPC_WIN",
                    "The system could not connect to your virus checker server"
                    ". Check the status of the network and the virus checker"
                    " server."],
    "13:10510022": ["ERROR", "ALRT_VC_ERROR_SERVER_OFFLINE_HTTP",
                    "The system could not connect to the virus checker server."
                    " Check the status of the network and the virus checker"
                    " server."],
    "13:10600002": ["WARNING", "DHSM_CONNECTION_DOWN",
                    "A Distributed Hierarchical Storage Management (DHSM) "
                    "connection to a secondary storage is down. Make sure that"
                    ": 1) The secondary storage is up and running on the "
                    "correct port. 2) The DHSM settings (URL, remote port, "
                    "credentials) are Correct."],
    "13:10600003": ["INFO", "DHSM_CONNECTION_RESUMED",
                    "A Distributed Hierarchical Storage Management (DHSM) "
                    "connection to a secondary storage has resumed. It is now"
                    " operational."],
    "13:106c004b": ["ERROR", "ALRT_REP_FAILED_FOR_ATTACHED_SNAPSHOT",
                    "The system cannot replicate an attached snapshot. Detach"
                    " the snapshot. When the detach operation completes, try"
                    " to replicate the snapshot again."],
    "13:106c004c": ["ERROR",
                    "ALRT_REP_FAILED_FOR_SNAPSHOT_WITH_SHARES_OR_EXPORTS",
                    "The system cannot replicate a snapshot that has shares or"
                    " exports. Delete the shares and exports, and try to "
                    "replicate the snapshot again."],
    "13:10760001": ["CRITICAL", "ALRT_DNS_NO_CONNECT",
                    "The system could not connect to the DNS server. This may"
                    " be the result of the DNS settings being Incorrect."],
    "13:1092000f": ["NOTICE", "CEPP_STARTED",
                    "The events publishing service is running on the specified"
                    " NAS server."],
    "13:10920010": ["NOTICE", "CEPP_STOPPED",
                    "The events publishing service is no longer running on the"
                    " specified NAS server. Events are no longer being sent to"
                    " the CEPA servers."],
    "13:10920011": ["INFO", "CEPP_SERVER_ONLINE",
                    "The specified CEPA server is operational."],
    "13:10920012": ["ERROR", "CEPP_SERVER_OFFLINE0",
                    "The specified CEPA server is not operational. Verify: 1)"
                    " Network availability and the CEPA facility is running on"
                    " the CEPA server. 2) That a pool has at least one event "
                    "assigned. 3) That the Events Publishing service is "
                    "running. 4) Network integrity between the SMB server "
                    "and the CEPA server."],
    "13:10920013": ["ERROR", "CEPP_SERVER_OFFLINENT",
                    "The specified CEPA server is not operational. Verify: 1)"
                    " Network availability and the CEPA facility is running on"
                    " the CEPA server. 2) That a pool has at least one event "
                    "assigned. 3) That the Events Publishing service is "
                    "running. 4) Network integrity between the SMB server and"
                    " the CEPA server."],
    "13:10920014": ["ERROR", "CEPP_SERVER_OFFLINEHTTP",
                    "The specified CEPA server is not operational. Verify: 1)"
                    " Network availability and the CEPA facility is running on"
                    " the CEPA server. 2) That a pool has at least one event "
                    "assigned. 3) That the Events Publishing service is "
                    "running. 4) Network integrity between the SMB server and "
                    "the CEPA server."],
    "13:10920015": ["ERROR", "CEPP_CIFS_SUSPENDED",
                    "The SMB service was suspended by the events publishing "
                    "service. The specified pool does not contain at least one"
                    " online CEPA server, and an events policy is in effect. "
                    "Make sure at least one CEPA server is online for this "
                    "pool, or set the events policy to 'Ignore'."],
    "13:10920016": ["NOTICE", "CEPP_CIFS_RESUME",
                    "The SMB service is no longer suspended by the events "
                    "publishing service. There is either at least one online "
                    "CEPA server in the pool, or the events policy was set to "
                    "'Ignore'."],
    "13:10940002": ["WARNING", "ALRT_DEDUP_NO_SPACE",
                    "There is insufficient space available to complete "
                    "deduplication. You need to allocate additional space."],
    "13:10940066": ["WARNING", "ALRT_DEDUP_NO_PROT_SPACE",
                    "There is insufficient space available to complete "
                    "deduplication. You need to allocate additional "
                    "protection space."],
    "13:10940068": ["INFO", "ALRT_DEDUP_FS_FAILED",
                    "The deduplication process on the specified file system "
                    "failed. This may have occurred because of insufficient "
                    "disk space or other system resource issues. Check any "
                    "related alerts and fix the underlying problems. If the "
                    "problem persists, contact your service provider."],
    "13:10ad0001": ["WARNING", "ALRT_NO_DEFAULT_UNIX_ACCOUNT",
                    "A Windows user was unable to access a multiprotocol file"
                    " system that has a Unix access policy. Create a valid "
                    "default Unix user for the associated NAS server, or map "
                    "the Windows user to a valid Unix user."],
    "13:10ad0002": ["WARNING", "ALRT_NO_DEFAULT_WIN_ACCOUNT",
                    "A Unix user was unable to access a multiprotocol file "
                    "system that has a Windows access policy. Create a valid "
                    "default Windows user for the associated NAS server, or "
                    "map the Unix user to a valid Windows user."],
    "13:10ad0003": ["WARNING", "ALRT_INVALID_DEFAULT_WINDOWS_ACCOUNT",
                    "A Unix user mapped to a default Windows user was unable "
                    "to access a multiprotocol file system with a Windows "
                    "access policy."],
    "13:10ad0004": ["WARNING", "ALRT_INVALID_DEFAULT_UNIX_ACCOUNT",
                    "A Windows user was unable to access a multiprotocol file "
                    "system because the default Unix user for the associated "
                    "NAS server is invalid. Change the default Unix user to a "
                    "valid user from the Unix directory service, or map the "
                    "Windows user to a valid Unix user."],
    "13:10ad0005": ["ERROR", "ALRT_NAS_UNIX_USER_MAPPING_ERR",
                    "User mapping failed. The Unix username cannot be mapped "
                    "to a Windows username. Specify a valid Windows username "
                    "to allow the Unix users to access the Windows- based "
                    "file systems."],
    "13:10ad0007": ["ERROR", "ALRT_NAS_WIN_USER_MAPPING_ERR",
                    "An SMB session cannot be established because the Windows "
                    "username in the domain cannot be mapped to a Unix "
                    "username. Check the Unix Directory Service settings, "
                    "and optionally specify a default Unix username for the "
                    "NAS server."],
    "14:100001": ["INFO", "DESC_TEST_SNMP_ALERT",
                  "This is a test message to be sent in an SNMP trap."],
    "14:110001": ["INFO", "DESC_TEST_EMAIL_ALERT",
                  "This is a test email alert message."],
    "14:160074": ["WARNING", "ALRT_AUTO_REMOVE_FILE_INTERFACE",
                  "The system automatically removed the overridden "
                  "file interface associated with a replication destination "
                  "NAS server, because the corresponding file interface was "
                  "removed on the source NAS server."],
    "14:160092": ["WARNING", "ALRT_AUTO_DISABLE_DNS_CLIENT",
                  "The system automatically disabled an overridden DNS client "
                  "of a replication destination NAS server, because the "
                  "corresponding DNS client was disabled on the source "
                  "NAS server."],
    "14:16009c": ["WARNING", "ALRT_AUTO_DISABLE_NIS_CLIENT",
                  "The system automatically disabled the overridden NIS client"
                  " of a replication destination NAS server, because the "
                  "corresponding NIS client was disabled on the source "
                  "NAS server"],
    "14:1600c4": ["WARNING", "ALRT_AUTO_DISABLE_LDAP_CLIENT",
                  "The system automatically disabled an overridden LDAP client"
                  " of a replication destination NAS server, because the "
                  "corresponding LDAP client was disabled on the source NAS "
                  "server"],
    "14:170001": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire soon"
                  ". Obtain and install the license files to ensure continued "
                  "access to the relevant feature."],
    "14:170002": ["CRITICAL", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire soon"
                  ". Obtain and install the license files to ensure continued"
                  " access to the relevant feature."],
    "14:170003": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170004": ["CRITICAL", "ALRT_ANTI_VIRUS_LICENSE_EXPIRED",
                  "The Antivirus Server Integration license has expired, and "
                  "the storage system no longer has antivirus protection. "
                  "Obtain and install a new license file to ensure access to "
                  "antivirus protection."],
    "14:170005": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170006": ["CRITICAL", "ALRT_LICENSE_EXPIRED",
                  "The EMC Unity Operating Environment V4.0 license has "
                  "expired, and your access to Unity functionality has been "
                  "disabled. Obtain and install the license file to ensure "
                  "continued access to Unity functionality."],
    "14:170007": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170008": ["CRITICAL", "ALRT_CIFS_LICENSE_EXPIRED",
                  "The CIFS/SMB Support license has expired, and the storage "
                  "system no longer has support for the CIFS/SMB protocol. "
                  "Obtain and install a new license file to ensure support "
                  "for CIFS/SMB."],
    "14:170009": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17000a": ["CRITICAL", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17000b": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17000c": ["CRITICAL", "ALRT_EMCSUPPORT_LICENSE_EXPIRED",
                  "The EMC Support license has expired, and the storage "
                  "system's access to EMC support has been disabled. Obtain "
                  "and install a new license file to ensure access to EMC "
                  "support."],
    "14:17000d": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17000e": ["CRITICAL", "ALRT_ESA_LICENSE_EXPIRED",
                  "The EMC Storage Analytics (ESA) license has expired, and "
                  "the storage system no longer has access to ESA. Obtain and"
                  " install a new license file to ensure access to ESA."],
    "14:17000f": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170010": ["CRITICAL", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170011": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170012": ["CRITICAL", "ALRT_FASTVP_LICENSE_EXPIRED",
                  "The FAST VP license has expired, and the storage system no "
                  "longer has support for FAST VP. Obtain and install a new "
                  "license file to ensure support for FAST VP."],
    "14:170013": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170014": ["CRITICAL", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170015": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170016": ["CRITICAL", "ALRT_ISCSI_LICENSE_WILL_EXPIRE",
                  "The Internet Small Computer System Interface (iSCSI) "
                  "license has expired, and the storage system no longer has"
                  " support for iSCSI. Obtain and install a new license file"
                  " to ensure iSCSI support."],
    "14:170017": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170018": ["CRITICAL", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170019": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17001a": ["CRITICAL", "ALRT_LOCAL_COPIES_LICENSE_EXPIRED",
                  "The Local Copies license has expired, and the storage "
                  "system no longer has support for local copies (including "
                  "the ability to create snapshots). Obtain and install a new "
                  "license file to ensure support for local copies."],
    "14:17001b": ["WARNING", "ALRT_CIFS_LICENSE_EXPIRING",
                  "The NFS license will expire soon, and the storage system's"
                  " support for NFS will be disabled. Obtain and install a new"
                  " license file to ensure continued support for NFS."],
    "14:17001c": ["CRITICAL", "ALRT_NFS_LICENSE_EXPIRED",
                  "The NFS license has expired, and the storage system no "
                  "longer has support for the NFS protocol. Obtain and install"
                  " a new license file to ensure support for NFS."],
    "14:17001d": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17001e": ["CRITICAL", "ALRT_QOS_LICENSE_EXPIRED",
                  "The Quality of Service (QOS) license has expired, and the "
                  "storage system no longer has support for the QOS feature."
                  " Obtain and install a new license file to ensure support "
                  "for the QOS feature."],
    "14:17001f": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170020": ["CRITICAL", "ALRT_REPLICATION_LICENSE_EXPIRED",
                  "The Replication license has expired, and the storage system"
                  " no longer has support for replication. Obtain and install"
                  " a new license file to ensure support for replication."],
    "14:170021": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170022": ["CRITICAL", "ALRT_SCE_LICENSE_EXPIRED",
                  "The Storage Capacity Expansion license has expired, and "
                  "your ability to manage extended storage capacity has been"
                  " disabled. Obtain and install a new license file to ensure"
                  " access to extended storage capacity."],
    "14:170023": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170024": ["CRITICAL", "ALRT_THIN_PROVISIONING_LICENSE_EXPIRED",
                  "The Thin Provisioning license has expired, and the storage"
                  " system no longer has suppport for thin provisioning. "
                  "Obtain and install the license file to ensure support for"
                  " thin provisioning."],
    "14:170025": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170026": ["CRITICAL", "ALRT_UNISPHERE_LICENSE_EXPIRED",
                  "The Unisphere license has expired, and the storage system's"
                  " access to Unisphere functionality has been disabled. "
                  "Obtain and install a new license file to ensure access to"
                  " Unisphere functionality."],
    "14:170027": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170028": ["CRITICAL", "ALRT_UC_LICENSE_EXPIRED",
                  "The Unisphere Central license has expired, and the storage"
                  " system's support for Unisphere Central has been disabled."
                  " Obtain and install a new license file to ensure support"
                  " for Unisphere Central."],
    "14:170029": ["WARNING", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:17002a": ["CRITICAL", "ALRT_VMWARE_LICENSE_EXPIRED",
                  "The VMware VASA/VVols license has expired, and the storage "
                  "system no longer has support for VVols. Obtain and install"
                  " a new license file to ensure support for VVols."],
    "14:17002b": ["CRITICAL", "ALRT_LICENSE_EXPIRING",
                  "One of your system licenses has expired or will expire "
                  "soon. Obtain and install the license files to ensure "
                  "continued access to the relevant feature."],
    "14:170032": ["WARNING", "ALRT_INLINE_COMPRESSION_LICENSE_WILL_EXPIRE",
                  "The inline compression license will expire soon. Obtain and"
                  " install a new license file to ensure continued support "
                  "for inline compression."],
    "14:170033": ["CRITICAL", "ALRT_INLINE_COMPRESSION_LICENSE_EXPIRED",
                  "The Inline Compression license has expired, and the storage"
                  " system no longer has support for inline compression. "
                  "Obtain and install a new license file to ensure support for"
                  " inline compression."],
    "14:170034": ["NOTICE", "ALRT_MAX_CAPACITY_LIMIT_INCREASE",
                  "The maximum storage capacity limit has been increased."],
    "14:170051": ["CRITICAL", "ALRT_ANTI_VIRUS_LICENSE_WILL_EXPIRE",
                  "The Antivirus Server Integration license has expired, and "
                  "the storage system's access to antivirus protection will be"
                  " disabled soon. Obtain and install a new license file to "
                  "ensure continued access to antivirus protection."],
    "14:170052": ["CRITICAL", "ALRT_LICENSE_WILL_EXPIRE",
                  "The EMC Unity Operating Environment, V4.0 license has "
                  "expired, and your access to Unity functionality will be "
                  "disabled soon. Obtain and install a new license file to "
                  "ensure continued access to Unity functionality."],
    "14:170053": ["CRITICAL", "ALRT_CIFS_SMB_LICENSE_WILL_EXPIRE",
                  "The CIFS/SMB Support license has expired, and the storage"
                  " system's support for the CIFS/SMB protocol will be "
                  "disabled soon. Obtain and install a new license file to "
                  "ensure continued support for CIFS/SMB."],
    "14:170055": ["CRITICAL", "ALRT_EMCSUPPORT_LICENSE_WILL_EXPIRE",
                  "The EMC Support license has expired, and the storage "
                  "system's access to EMC support will be disabled soon. "
                  "Obtain and install a new license file to ensure continued"
                  " access to EMC support."],
    "14:170056": ["CRITICAL", "ALRT_ESA_LICENSE_WILL_EXPIRE",
                  "The EMC Storage Analytics (ESA) license has expired, and "
                  "the storage system's access to ESA will be disabled soon. "
                  "Obtain and install a new license file to ensure continued "
                  "access to ESA."],
    "14:170058": ["CRITICAL", "ALRT_FASTVP_LICENSE_EXPIRED_PERIOD",
                  "The FAST VP license has expired, and the storage system's"
                  " support for FAST VP will be disabled soon. Obtain and "
                  "install a new license file to ensure continued support "
                  "for FAST VP."],
    "14:17005a": ["CRITICAL", "ALRT_ISCSI_LICENSE_EXPIRING",
                  "The Internet Small Computer System Interface (iSCSI) "
                  "license has expired, and the storage system's support for "
                  "iSCSI will be disabled soon. Obtain and install a new "
                  "license file to ensure continued support for iSCSI."],
    "14:17005c": ["CRITICAL", "ALRT_LOCAL_COPIES_LICENSE_EXPIRING",
                  "The Local Copies license has expired, and the storage "
                  "system's support for local copies (including the ability "
                  "to create snapshots) will be disabled soon. Obtain and "
                  "install a new license file to ensure continued support "
                  "for local copies."],
    "14:17005d": ["CRITICAL", "ALRT_NFS_LICENSE_EXPIRING",
                  "The NFS license has expired, and the storage system's "
                  "support for the NFS protocol will be disabled soon. "
                  "Obtain and install a new license file to ensure continued "
                  "support for NFS."],
    "14:17005e": ["CRITICAL", "ALRT_QOS_LICENSE_EXPIRING",
                  "The Quality of Service (QOS) license has expired, and the"
                  " storage system's support for the QOS feature will be "
                  "disabled soon. Obtain and install a new license file to "
                  "ensure continued support for the QOS feature."],
    "14:17005f": ["CRITICAL", "ALRT_REPLICATION_LICENSE_EXPIRING",
                  "The Replication license has expired, and the storage "
                  "system's support for replication will be disabled soon. "
                  "Obtain and install a new license file to ensure continued "
                  "support for replication."],
    "14:170060": ["CRITICAL", "ALRT_SCE_LICENSE_EXPIRING",
                  "The Storage Capacity Expansion license has expired, and "
                  "your ability to manage extended storage capacity will be "
                  "disabled soon. Obtain and install a new license file to "
                  "ensure continued access to extended storage capacity."],
    "14:170061": ["CRITICAL", "ALRT_THIN_PROVISIONING_LICENSE_EXPIRING",
                  "The Thin Provisioning license has expired, and the storage"
                  " system's support for thin provisioning will be disabled "
                  "soon. Obtain and install the license file to ensure "
                  "continued support for thin provisioning."],
    "14:170062": ["CRITICAL", "ALRT_UNISPHERE_LICENSE_EXPIRING",
                  "The Unisphere license has expired, and the storage system's"
                  " access to Unisphere functionality will be disabled soon. "
                  "Obtain and install a new license file to ensure continued "
                  "access to Unisphere functionality."],
    "14:170063": ["CRITICAL", "ALRT_UC_LICENSE_EXPIRING",
                  "The Unisphere Central license has expired, and the storage"
                  " system's support for Unisphere Central will be disabled "
                  "soon. Obtain and install a new license file to ensure "
                  "continued support for Unisphere Central."],
    "14:170064": ["CRITICAL", "ALRT_VMWARE_LICENSE_EXPIRING",
                  "The VMware VASA/VVols license has expired, and the storage"
                  " system's support for VVols will be disabled soon. obtain "
                  "and install a new license file to ensure continued support"
                  " for VVols."],
    "14:170065": ["CRITICAL", "ALRT_INLINE_COMPRESSION_LICENSE_EXPIRING",
                  "The Inline Compression license has expired, and the storage"
                  " system's support for inline compression will be disabled "
                  "soon. Obtain and install a new license file to ensure "
                  "continued support for inline compression."],
    "14:180002": ["ERROR", "ALRT_HEALTH_CHECK_NOT_START",
                  "The pre-upgrade health check has failed to start."],
    "14:180004": ["ERROR", "ALRT_HEALTH_CHECK_FAILED",
                  "The pre-upgrade health check has failed. Check the error "
                  "messages in the Health Check dialog box."],
    "14:180005": ["ERROR", "ALRT_HEALTH_CHECK_TERMINATED",
                  "The pre-upgrade health check was unexpectedly terminated. "
                  "Try running the health Check again."],
    "14:180007": ["ERROR", "ALRT_UPGRADE_NOT_START",
                  "The software upgrade process failed to start. Check the "
                  "system logs and other alerts to identify the issue. Once "
                  "the issue is fixed, try running the upgrade again."],
    "14:180008": ["NOTICE", "ALRT_UPGRADE_OK",
                  "The upgrade completed successfully. To access the latest "
                  "management software, you must reload Unisphere. Close any"
                  " browsers opened prior to the upgrade and start a new "
                  "Unisphere login session."],
    "14:180009": ["ERROR", "ALRT_UPGRADE_FAILED",
                  "The upgrade has failed. Review information about the failed"
                  " upgrade on the Settings screen."],
    "14:18000a": ["ERROR", "ALRT_UPGRADE_TERMINATED",
                  "The upgrade terminated unexpectedly. Please try running the"
                  " upgrade again."],
    "14:18000c": ["ERROR", "ALRT_UPGRADE_FAILED",
                  "The upgrade has failed. From Unisphere, click Settings "
                  "More Configuration  Update Software and review information"
                  " about the failed upgrade."],
    "14:18000d": ["NOTICE", "ALRT_UPGRADE_SUCCESS",
                  "The upgrade has completed successfully."],
    "14:18000e": ["NOTICE", "ALRT_UPGRADE_SUCCESS",
                  "The upgrade has completed successfully."],
    "14:18000f": ["ERROR", "ALRT_UPGRADE_FAILED",
                  "The upgrade has failed. Review information about the failed"
                  " upgrade on the Settings screen."],
    "14:180010": ["ERROR", "ALRT_UPGRADE_FAILED",
                  "The upgrade has failed. Review information about the "
                  "failed upgrade on the Settings screen."],
    "14:180011": ["ERROR", "ALRT_UPGRADE_TERMINATED",
                  "The upgrade terminated unexpectedly. Please try running the"
                  " upgrade again."],
    "14:180012": ["ERROR", "ALRT_UPGRADE_TERMINATED",
                  "The upgrade terminated unexpectedly. Please try running the"
                  " upgrade again."],
    "14:22001d": ["CRITICAL", "ALRT_STATICPOOL_TRANSACTION_LOG_FAILURE",
                  "System was unable to automatically recover after the "
                  "provisioning operation failed. Contact your service "
                  "provider for assistance with system cleanup."],
    "14:300007": ["WARNING", "ALRT_DART_FS_OVER_THRESHOLD",
                  "The total number of storage resources has exceeded the "
                  "maximum allowed threshold limit. Delete unneeded snapshots"
                  " or storage resources to free up some space."],
    "14:30014": ["ERROR", "ALRT_UPGRADE_ECOM_FAILED",
                 "LDAP users and groups may have been lost during the upgrade."
                 " Review the list of LDAP users and groups to determine "
                 "whether any have been deleted. Add missing LDAP users/groups"
                 " again, if necessary."],
    "14:330009": ["CRITICAL", "ALRT_CONFIG_PSM_RW_FAILED",
                  "The system encountered an error while accessing "
                  "configuration information. Reboot the storage processors "
                  "(SPs) from the Service System page."],
    "14:380001": ["WARNING", "ALRT_CONTRACT_WILL_EXPIRE",
                  "The <a contract will expire in <b days. Go to the EMC "
                  "Online Support portal to view and manage support "
                  "contracts."],
    "14:380002": ["CRITICAL", "ALRT_CONTRACT_EXPIRED",
                  "The <a contract has expired. You should renew this support"
                  " contact immediately. Go to the EMC Online Support portal"
                  " to view and manage Contracts."],
    "14:380004": ["WARNING", "ALRT_CONTRACT_REFRESH_BAD_CREDS",
                  "Contract data failed to refresh because the credentials "
                  "that you provided are invalid. Verify the credentials and "
                  "try again."],
    "14:380005": ["WARNING", "ALRT_CONTRACT_REFRESH_SERV_UNAVAIL",
                  "The service contract data failed to automatically "
                  "refresh."],
    "14:380006": ["WARNING", "ALRT_CONTRACT_REFRESH_ERR",
                  "The service contract data failed to automatically refresh."
                  " This error is undetermined, but it is possible that this "
                  "problem may be temporary. Please wait to see if the problem"
                  " resolves itself."],
    "14:380009": ["INFO", "ALRT_DF_UPGRADE_AVAILABLE",
                  "A disk firmware upgrade is now available for download. From"
                  " Unisphere, click Support  Downloads. This link takes you "
                  "to the EMC Online Support Downloads page from where you can"
                  " download an upgrade for your storage system."],
    "14:38000a": ["INFO", "ALRT_LN_UPGRADE_AVAILABLE",
                  "A language pack upgrade is now available for download. From"
                  " Unisphere, click Support  Downloads. This link takes you "
                  "to the EMC Online Support Downloads page from where you can"
                  " download an upgrade for your storage system."],
    "14:38000b": ["WARNING", "ALRT_CONTRACT_CANT_VERIFY_CREDS",
                  "The EMC Support account credentials that you provided "
                  "cannot be verified because there is a network communication"
                  " problem. Ensure that ports 80 (HTTP) and 443 (HTTPS) are "
                  "open to internet traffic."],
    "14:38000c": ["NOTICE", "ALRT_ADVISORIES_AVAIL",
                  "There are one or more new technical advisories available "
                  "for viewing on the Technical Advisories page."],
    "14:380010": ["WARNING", "ALRT_CONTRACT_INVALID_CONTENT",
                  "The service contract data failed to automatically refresh."
                  " The contract context is not in the proper format, but it "
                  "is possible that this problem may be temporary and resolves"
                  " itself. If it does not resolve itself, contact EMC service"
                  " to check the service contract information in the backend "
                  "servers. If the backend information is wrong, it is "
                  "possible that a proxy server altered the context before "
                  "transimitting it to the SP."],
    "14:380011": ["WARNING", "ALRT_NONE_CONTRACT_THROUGH_PROXY",
                  "Unable to retrieve service contract information through the"
                  " configured proxy server. Check whether the configured "
                  "proxy server information is correct and the server is "
                  "online and functioning properly."],
    "14:380012": ["ERROR", "ALR_NON_TECHNICAL_ADVISORY_THROUGH_PROXY",
                  "Unable to get the latest technical advisory for the current"
                  " storage system. Check whether the configured proxy server"
                  " information is correct and the server is online and "
                  "functioning properly."],
    "14:380013": ["ERROR", "ALRT_NON_UPGRADE_NOTIFICATION_THROUGH_PROXY",
                  "Unable to know the latest available storage software, drive"
                  " firmware or language pack updates through the configured"
                  " support proxy server. Check whether the configured proxy"
                  " server information is correct and the server is online and"
                  " functioning properly."],
    "14:380017": ["WARNING", "ALRT_FIRMWARE_UPGRADE_AVAILABLE_WARNING",
                  "A recommended disk firmware upgrade is now available for"
                  " download. The disk firmware version currently installed"
                  " is more than 180 days old. To ensure optimal performance,"
                  " upgrade the disk firmware."],
    "14:380018": ["WARNING", "ALRT_LN_UPGRADE_AVAILABLE_WARNING",
                  "A recommended language pack upgrade is now available for "
                  "download. The language pack version currently installed is"
                  " more than 180 days old. To ensure optimal experience, "
                  "upgrade the language pack."],
    "14:38001d": ["INFO", "ALRT_CONTACT_INFO_REMINDER",
                  "Please verify your system contact information. This will "
                  "help your service provider to contact you and quickly "
                  "respond to any critical issues."],
    "14:38001e": ["INFO", "ALRT_SW_UPGRADE_AVAILABLE",
                  "A recommended system software is now available for "
                  "download. To ensure optimal system performance, EMC "
                  "recommends upgrading to this version. Run a health check "
                  "about a week before installing the upgrade to identify and"
                  " resolve any underlying issues that may prevent a"
                  " successful update."],
    "14:38001f": ["WARNING", "ALRT_SW_UPGRADE_AVAILABLE_WARNING",
                  "System is running a system software version that is more "
                  "than 180 days old. A recommended system software is now "
                  "available for download. To ensure optimal system "
                  "performance, EMC recommends upgrading to this version."
                  " Run a health check about a week before installing the "
                  "upgrade to identify and resolve any underlying issues that"
                  " may prevent a successful update."],
    "14:380020": ["ERROR", "ALRT_SW_UPGRADE_AVAILABLE_ERROR",
                  "System is running a deprecated version of the system "
                  "software. A recommended system software is now available "
                  "for download. To ensure optimal system performance, EMC "
                  "recommends upgrading to this version. Run a health check "
                  "about a week before installing the upgrade to identify and"
                  " resolve any underlying issues that may prevent a "
                  "successful update."],
    "14:380021": ["ERROR", "ALRT_SW_UPGRADE_AVAILABLE_GENERAL_ERROR",
                  "System is running a deprecated version of the system "
                  "software. A recommended system software is now available "
                  "for download. To ensure optimal system performance, "
                  "EMC recommends upgrading to this version. Run a health "
                  "check about a week before installing the upgrade to "
                  "identify and resolve any underlying issues that may "
                  "prevent a successful update."],
    "14:380022": ["INFO", "ALRT_SW_UPGRADE_AVAILABLE_PUHC",
                  "A recommended update to Health Check is available for"
                  " download."],
    "14:380027": ["CRITICAL", "ALRT_DISK_USAGE_CRITICAL",
                  "There is little disk space left in the system disk of "
                  "current system. Please contact your service provider to"
                  " do the cleaning up as soon as possible."],
    "14:380028": ["WARNING", "ALRT_DISK_USAGE_WARNING",
                  "There is not much disk space left in the system disk of "
                  "current system. Please pay attention to any new critical"
                  " alert about system disk usage."],
    "14:380029": ["INFO", "ALRT_DISK_USAGE_INFO",
                  "The system disk of current system has enough disk "
                  "space now"],
    "14:39000a": ["WARNING", "ALRT_SITE_INFO_UPDATE_REQUEST",
                  "A dial home alert has been generated requesting an update"
                  " to the site Information."],
    "14:390014": ["ERROR", "ALRT_EVE_FAIL_ENABLE_FOR_UPGRADE",
                  "Integrated ESRS could not be automatically re-enabled after"
                  " the upgrade. Contact your service provider to re-enable"
                  " it."],
    "14:390015": ["ERROR", "ALRT_PROXY_PASS_FAIL_RESTORE_FOR_UPGRADE",
                  "The proxy credentials that were provided before the upgrade"
                  " could not be transferred. Please configure the proxy "
                  "server information again."],
    "14:440001": ["INFO", "DESC_TEST_MOZZO_ALERT",
                  "This is a test mozzo alert message."],
    "14:450001": ["ERROR", "ALRT_SED_KEY_BACKUP_FAILED",
                  "A request to back up the self-encrypting drive key has "
                  "failed. If the problem persists, please go to Support"
                  " Chat to chat with EMC support personnel. If this option"
                  " is not available, contact your service provider."],
    "14:46000d": ["ERROR", "ALRT_ESRS_CANT_CONNECT",
                  "ESRS is unable to make a connection to EMC. This usually "
                  "indicates a network problem, though it may resolve on "
                  "its own."],
    "14:46000e": ["ERROR", "ALRT_ESRS_CANT_START",
                  "An error has occurred that is preventing the ESRS service "
                  "from starting up."],
    "14:46000f": ["INFO", "ALRT_ESRS_OK",
                  "All issues with ESRS have been resolved."],
    "14:460010": ["NOTICE", "ALRT_ESRS_DISABLED",
                  "Remote support options are not available while ESRS is"
                  " Disabled."],
    "14:460011": ["NOTICE", "ALRT_ESRS_ENABLED",
                  "Remote support options are available while ESRS is "
                  "enabled."],
    "14:460012": ["ERROR", "ALRT_ESRS_NO_PROXY",
                  "The connection to the ESRS proxy server has been lost. "
                  "ESRS will not function correctly until the connection is "
                  "restored. Verify that there are no network problems between"
                  " the storage system and the proxy server, and that the "
                  "proxy server itself has not been shut down."],
    "14:460013": ["INFO", "ALRT_ESRS_PROXY_RESTORED",
                  "All connection issues with the ESRS proxy server have been"
                  " resolved."],
    "14:460014": ["ERROR", "ALRT_ESRS_POL_MAN_LOST",
                  "The connection to the ESRS Policy Manager has been lost."
                  " remote connectivity will not be possible if it is "
                  "configured with an Ask for approval policy. Additionally,"
                  " any configuration changes you make to the Policy Manager"
                  " will not take effect until connectivity is restored."],
    "14:460015": ["INFO", "ALRT_ESRS_POL_MAN_RESTORED",
                  "All connection issues with the ESRS Policy Manager have"
                  " been resolved."],
    "14:5000a": ["INFO", "ALRT_HOST_IQN_DUPLICATE",
                 "The iSCSI Qualified Name (IQN) is present in two or more "
                 "hosts. Modifying host access for these hosts, deleting any"
                 " of these hosts, or deleting the IQN can interrupt I/O "
                 "through the IQN."],
    "14:5010001": ["ERROR", "ALRT_MOZZO_CANT_REACH_SVR",
                   "The Unisphere Central server may be temporarily "
                   "unavailable or unreachable. Verify network connectivity."],
    "14:5010002": ["INFO", "ALRT_MOZZO_CAN_REACH_SVR",
                   "The service is operating normally. No action is "
                   "required."],
    "14:5010003": ["ERROR", "ALRT_MOZZO_INVL_VNXE_VER",
                   "Unisphere Central server is not compatible with your "
                   "storage system software. Contact the Unisphere Central "
                   "administrator to upgrade the server to a compatible "
                   "version."],
    "14:5010004": ["INFO", "ALRT_MOZZO_VALID_VNXE_VE",
                   "The service is now operating normally. No action is "
                   "required."],
    "14:5010005": ["ERROR", "ALRT_MOZZO_INVL_SVR_CERT",
                   "The certificate could not be validated. The Unisphere "
                   "Central server hash specified did not match the hash value"
                   " provided by the server. Please contact your Unisphere "
                   "Central server administrator to verify certificate hash"
                   " value."],
    "14:5010006": ["INFO", "ALRT_MOZZO_VALID_SVR_CERT",
                   "The service is operating normally. No action is required"],
    "14:5010007": ["ERROR", "ALRT_MOZZO_INVL_VNXE_CERT",
                   "The Unisphere Central challenge phrase specified did not "
                   "match the same value provided by the server. Verify this"
                   " value with your Unisphere Central server administrator."],
    "14:5010008": ["INFO", "ALRT_MOZZO_VALID_VNXE_CERT",
                   "The service is operating normally. No action is "
                   "required."],
    "14:501000a": ["ERROR", "ALRT_MOZZO_INVL_SVR_CERT_NAME",
                   "The Unisphere Central server is responding with the wrong"
                   " certificate name. Please verify your Unisphere Central "
                   "configuration."],
    "14:501000b": ["INFO", "ALRT_MOZZO_VALID_SVR_CERT",
                   "The service is operating normally. No action is required"],
    "14:52008e": ["ERROR", "ALRT_POOL_LIMITS_EXCEEDED",
                  "The system was unable to create a new pool or extend an "
                  "existing pool because the maximum number of pools or"
                  " maximum space of all pools has been reached. Delete "
                  "unneeded snapshots or storage resources to free up some "
                  "space"],
    "14:52008f": ["ERROR", "ALRT_SV_LIMITS_EXCEEDED",
                  "The system was unable to create a new LUN because the "
                  "maximum number of LUNs or maximum number of LUNs and LUN "
                  "snapshots has been reached. Delete unneeded snapshots or"
                  " storage resources to free up some space."],
    "14:520090": ["ERROR", "ALRT_FS_LIMITS_EXCEEDED",
                  "The system was unable to create a new file system because "
                  "the maximum number of file systems and file system "
                  "snapshots has been reached. Delete one or more file "
                  "systems or file system snapshots to maintain system "
                  "performance."],
    "14:520091": ["WARNING", "ALRT_POOL_THRESHOLDS_EXCEEDED",
                  "The threshold of the total number of pools in the system "
                  "or the total space of all the pools in the system has been "
                  "exceeded. Delete one or more pools to maintain system "
                  "performance."],
    "14:520092": ["WARNING", "ALRT_SV_THRESHOLDS_EXCEEDED",
                  "The threshold of the total number of the LUNs or the total "
                  "number of the LUNs and LUN snapshots has been exceeded. "
                  "Delete one or more LUNs to maintain system performance."],
    "14:520093": ["WARNING", "ALRT_FS_THRESHOLDS_EXCEEDED",
                  "The threshold of the total number of file systems and file"
                  " system snapshots has been exceeded. Delete one or more "
                  "file systems to maintain system performance."],
    "14:520096": ["ERROR", "ALRT_POOL_SIZE_LIMITS_EXCEEDED",
                  "The system was unable to create a new pool or extend an "
                  "existing pool because the specified pool size exceeds the"
                  " system limit. Consider deleting any existing pools that "
                  "may no longer be used, and then try creating the new pool"
                  " with a size within system limits."],
    "14:520097": ["ERROR", "ALRT_POOL_NUMBER_LIMITS_EXCEEDED",
                  "The system was unable to create a new pool because the"
                  " maximum number of pools has been reached. Consider "
                  "deleting any existing pools that may no longer be used, "
                  "and then try creating the new pool with a size within "
                  "system limits."],
    "14:520098": ["ERROR", "ALRT_LUN_SIZE_LIMITS_EXCEEDED",
                  "The system was unable to create a new LUN or extend an "
                  "existing LUN because the specified LUN size exceeds system"
                  " limit. Try creating a LUN again with a size that is within"
                  " the system limits."],
    "14:520099": ["ERROR", "ALRT_LUN_NUMBER_LIMITS_EXCEEDED",
                  "The system was unable to create a new LUN because the "
                  "maximum number of LUNs has been reached. Consider deleting"
                  " any existing LUNs that may no longer be used, and then try"
                  " creating the new LUN with a size within system limits."],
    "14:52009a": ["ERROR", "ALRT_LUN_AND_SNAPSHOT_NUMBER_LIMITS_EXCEEDED",
                  "The system was unable to create a new LUN because the "
                  "maximum number of LUNs and LUN snapshots has been reached."
                  " Consider deleting any existing LUNs and LUN snapshots that"
                  " may no longer be used, and then try creating the new LUN "
                  "with a size within system limits."],
    "14:52009b": ["ERROR", "ALRT_FS_SIZE_LIMITS_EXCEEDED",
                  "The system could not create a new file system or extend an"
                  " existing one, because the specified file system size "
                  "exceeds the system limit. Try specifying a file system size"
                  " that is within the system limits."],
    "14:60001f": ["ERROR", "ALRT_SNAPSHOT_CREATE_FAILED",
                  "The system could not create a snapshot because the storage"
                  " resource does not have enough protection space. Add more"
                  " protection space."],
    "14:600020": ["ERROR", "ALRT_SNAPSHOT_CREATE_HIT_APP_LIMIT",
                  "The system could not create the snapshot because the"
                  " maximum number of snapshots allowed for the application "
                  "has been reached. Delete one or more snapshots and try"
                  " again"],
    "14:600026": ["ERROR", "ALRT_SNAPSHOT_STILL_CREATING_LAST",
                  "The system is unable to create a snapshot because another "
                  "snapshot creation for this same application is in progress."
                  " Reduce the frequency of scheduled snapshots."],
    "14:600027": ["ERROR", "ALRT_SNAPSHOT_CREATE_HIT_FS_LIMIT",
                  "The system could not create the snapshot because the"
                  " maximum number of allowed file-based snapshots has been"
                  " reached. Delete one or more snapshots and try again."],
    "14:600028": ["ERROR", "ALRT_SNAPSHOT_CREATE_HIT_VOL_LIMIT",
                  "The system could not create the snapshot because the"
                  " maximum number of allowed LUN snapshots has been reached."
                  " Delete one or more snapshots and try again."],
    "14:60002e": ["ERROR", "ALRT_SNAPSHOT_CREATE_FAILED_LUN",
                  "An attempt to create a scheduled snapshot failed, because"
                  " the system could not find any LUNs associated with the "
                  "storage resource. If the storage resource has no LUNs, "
                  "ignore this message. If the storage resource has LUNs, "
                  "contact your service provider."],
    "14:600036": ["WARNING", "ALRT_SNAPSHOT_WILL_EXCEED_VDISK_CAPACITY",
                  "The number of LUN snapshots is approaching the limit for "
                  "the maximum snapshots allowed. Delete snapshots and/or "
                  "reduce the frequency of scheduled snapshots to stay within"
                  " snapshot capacity limits."],
    "14:600037": ["NOTICE", "ALRT_SNAPSHOT_WILL_NOT_EXCEED_VDISK_CAPACITY",
                  "The predicted number of LUN snapshots is no longer expected"
                  " to reach the maximum."],
    "14:600038": ["WARNING", "ALRT_SNAPSHOT_WILL_EXCEED_FS_CAPACITY",
                  "The number of file- based snapshots is approaching the "
                  "limit for the maximum snapshots allowed. Delete snapshots"
                  " and/or reduce the frequency of scheduled snapshots to stay"
                  " within snapshot capacity limits."],
    "14:600039": ["NOTICE", "ALRT_SNAPSHOT_WILL_NOT_EXCEED_FS_CAPACITY",
                  "The predicted number of file-based snapshots is no longer "
                  "expected to reach the maximum."],
    "14:60003a": ["ERROR", "ALRT_SNAPSHOT_CREATE_HIT_FS_NAS_SERVER_LIMIT",
                  "The system cannot create the snapshot because the "
                  "associated NAS server has reached the number of maximum "
                  "combined limit of file systems and file system snapshots."
                  " Delete one or more snapshots and try again."],
    "14:600c8": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:600cc": ["WARNING", "ALRT_APP_DEGRADE",
                 "The NAS server used by this file system is either "
                 "restarting, is degraded, or is not accessing an external"
                 " server. Check the NAS server health status and logs. If"
                 " needed, check the external server status and login "
                 "information."],
    "14:600cd": ["ERROR", "ALRT_APP_FAILED",
                 "The NAS server used by this file system is either "
                 "restarting, is degraded, or is not accessing an external"
                 " server. Check the NAS server health status and logs. If"
                 " needed, check the external server status and login"
                 " information."],
    "14:600ce": ["CRITICAL", "ALRT_APP_SERVER_UNAVAILABLE",
                 "The NAS server used by this storage resource is being "
                 "restarted. No action required."],
    "14:600cf": ["WARNING", "ALRT_APP_REPL_MINOR",
                 "The replication session for this application is degraded."],
    "14:600d0": ["WARNING", "ALRT_APP_REPL_CRIT",
                 "The replication session for this storage resource has "
                 "faulted. You need to delete this replication session and "
                 "create a new replication session."],
    "14:600d1": ["INFO", "ALRT_APP_FS_OK",
                 "This storage resource is operating normally. No action "
                 "is required."],
    "14:600d2": ["WARNING", "ALRT_APP_FS_FILLING",
                 "The file system is running out of space. Allocate more "
                 "storage space to the storage resource."],
    "14:600d3": ["ERROR", "ALRT_APP_FS_FULL",
                 "The file system has run out of space. Allocate more storage"
                 "space to the storage resource."],
    "14:600d6": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this"
                 " time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:600d9": ["INFO", "ALRT_VOL_OK",
                 "The LUN is operating Normally. No action is required."],
    "14:600de": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:600e2": ["WARNING", "ALRT_APP_TEMP_UNMOUNT",
                 "The storage associated with the storage resource is "
                 "temporarily unavailable. This can be related to normal"
                 " system activity, and your storage will be available "
                 "shortly. If the storage remains unavailable, try fixing "
                 "any underlying problems to restore access to the storage."
                 " If the problem persists, contact your service provider."],
    "14:600e4": ["CRITICAL", "ALRT_APP_PERM_UNMOUNT",
                 "The storage associated with the storage resource is "
                 "unavailable. This can be related to normal system activity, "
                 "and your storage will be available shortly. If the storage "
                 "remains unavailable, try fixing any underlying problems to "
                 "restore access to the storage. If the problem persists, "
                 "contact your service provider."],
    "14:600e7": ["CRITICAL", "ALRT_VOL_NEED_RECOVER",
                 "The LUN is offline and requires recovery. this may be caused"
                 " by the pool being offline. Please fix the issue on the "
                 "pool first. If the problem still exists, contact your "
                 "service provider."],
    "14:600e8": ["CRITICAL", "ALRT_VOL_OFFLINE",
                 "The LUN is offline. This may be caused by the pool being "
                 "offline. Please fix the issue on the pool first. If the "
                 "problem still exists, contact your service provider."],
    "14:600e9": ["CRITICAL", "ALRT_VOL_BAD",
                 "The LUN is unavailable or may have a data inconsistency. "
                 "Try rebooting the storage system. If the problem persists, "
                 "contact your service provider."],
    "14:600ea": ["WARNING", "ALRT_VOL_FAULT",
                 "There are some issues detected on the LUN and it is "
                 "degraded. please contact your service provider."],
    "14:600eb": ["WARNING", "ALRT_VOL_BAD",
                 "The LUN is unavailable or may have a data inconsistency. "
                 "Try rebooting the storage system. If the problem persists,"
                 " contact your service provider."],
    "14:600ec": ["WARNING", "ALRT_APP_FAULT",
                 "There are some issues detected on the storage resource and "
                 "it is degraded. Contact your service provider."],
    "14:600ed": ["CRITICAL", "ALRT_APP_OFFLINE",
                 "The storage resource is offline. This may be caused by its"
                 " storage elements being offline. Please contact your service"
                 " provider."],
    "14:600ee": ["ERROR", "ALRT_APP_UNAVAILABLE",
                 "The NAS server used by this file system is restarting, is"
                 " degraded, or is not accessing an external server. Check the"
                 " NAS server health status and logs. If needed, check the"
                 " external server status and login information."],
    "14:600ef": ["WARNING", "ALRT_APP_UNAVAILABLE",
                 "The NAS server used by this file system is restarting, is"
                 " degraded, or is not accessing an external server. Check the"
                 " NAS server health status and logs. If needed, check the "
                 "external server status and login information."],
    "14:600f0": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:600f2": ["CRITICAL", "ALRT_APP_BAD_FS",
                 "The file system is unavailable or may have a data "
                 "inconsistency. Try rebooting the storage system. If the "
                 "problem persists, contact your service provider."],
    "14:600f3": ["CRITICAL", "ALRT_APP_FS_NEED_RECOVER",
                 "The file system is offline and requires recovery. This may "
                 "be caused by the pool being offline. Please fix the issue "
                 "on the pool first. If the problem still exists, contact your"
                 " service provider."],
    "14:600f4": ["CRITICAL", "ALRT_APP_FS_OFFLINE",
                 "The file system is offline. This may be caused by the pool"
                 " being offline. Please fix the issue on the pool first. If "
                 "the problem still exists, contact your service provider."],
    "14:600f5": ["WARNING", "ALRT_APP_FS_FAULT",
                 "There are some issues detected on the file system and it is"
                 " degraded. Please contact your service provider."],
    "14:600f6": ["WARNING", "ALRT_APP_BAD_FS",
                 "The file system is unavailable or may have a data "
                 "inconsistency. Try rebooting the storage system. If the "
                 "problem persists, contact your service provider."],
    "14:600f7": ["WARNING", "ALRT_APP_FS_IO_SIZE_TOO_SMALL",
                 "The majority of the recent write I/O operations to the "
                 "VMware NFS datastore were not aligned with the configured"
                 " Host I/O size."],
    "14:600f8": ["WARNING", "ALRT_APP_FS_IO_SIZE_UNALIGNED",
                 "The majority of the recent write I/O operations to the "
                 "VMware NFS datastore were not aligned with 8K."],
    "14:6012c": ["INFO", "ALRT_BBU_CHARGE",
                 "The battery backup unit (BBU) in your Storage Processor is"
                 " Currently charging."],
    "14:6012d": ["CRITICAL", "ALRT_BBU_FAULT",
                 "A battery backup unit (BBU) in your Storage Processor has "
                 "faulted and needs to be replaced."],
    "14:6012e": ["ERROR", "ALRT_BBU_MISSING",
                 "The battery backup unit (BBU) has been removed from your "
                 "Storage Processor and needs to be reinstalled."],
    "14:6012f": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60130": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60131": ["CRITICAL", "ALRT_BBU_LOW",
                 "The battery level in the Storage Processor (SP) is low. "
                 "Please wait for the battery to charge. If the battery cannot"
                 " be charged, pay attention to the alert for the battery and"
                 " power supply."],
    "14:60132": ["CRITICAL", "ALRT_BBU_AC_FAULT",
                 "Power supply to the battery backup unit has faulted. Check"
                 " the power supply to the Storage Processor (SP)."],
    "14:60133": ["CRITICAL", "ALRT_BBU_REPLACE",
                 "The battery has faulted and needs to be replaced."],
    "14:60193": ["CRITICAL", "ALRT_DAE_FAULT",
                 "A Disk Array Enclosure (DAE) has faulted. This may have "
                 "occurred because of a faulted subcomponent. Identify and fix"
                 " the issue with the subcomponent. If the problem persists,"
                 " contact your service provider."],
    "14:60194": ["CRITICAL", "ALRT_LCC_FAULT",
                 "A link control card (LCC) in your Disk Array Enclosure has"
                 " faulted and needs to be replaced."],
    "14:60195": ["ERROR", "ALRT_DAE_MISCABLED",
                 "A Disk Array Enclosure (DAE) has not been connected "
                 "correctly. This may be a temporary issue because the DAE is"
                 " getting connected or a Link Control Card (LCC) is getting "
                 "inserted in the DAE. If the issue persists, contact your "
                 "service provider."],
    "14:60196": ["CRITICAL", "ALRT_DAE_MISCONFIGURED",
                 "Either the cables or the ID of a Disk Array Enclosure (DAE)"
                 " have been misconfigured."],
    "14:60197": ["CRITICAL", "ALRT_DAE_MISSING",
                 "A Disk Array Enclosure (DAE) has been removed and needs to "
                 "be reinstalled."],
    "14:60198": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:6019c": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:6019e": ["CRITICAL", "ALRT_DAE_TOO_MANY",
                 "The number of Disk Array Enclosures (DAEs) added has "
                 "exceeded the maximum allowed. Remove the newly attached"
                 " DAE."],
    "14:6019f": ["CRITICAL", "ALRT_DAE_UNSUPPORTED",
                 "An unsupported Disk Array Enclosure (DAE) has been detected."
                 " Replace the DAE with one that the system supports."],
    "14:601a0": ["CRITICAL", "ALRT_DAE_CROSSCABLED",
                 "The Disk Array Enclosure (DAE) has been cabled incorrectly."
                 " Ensure that the DAE is cabled correctly."],
    "14:601a1": ["WARNING", "ALRT_DAE_TEMPERATURE_WARNING",
                 "The Disk Array Enclosure (DAE) temperature has reached the "
                 "warning threshold. This may lead to the DAE shutting down."
                 " Check the hardware, environmental temperature, system logs,"
                 " and other alerts to identify and fix the issue. If the "
                 "problem persists, contact your service provider."],
    "14:601a2": ["ERROR", "ALRT_DAE_TEMPERATURE_FAULT",
                 "The Disk Array Enclosure (DAE) temperature has reached the"
                 " failure threshold. The DAE will shut down shortly. Check "
                 "the hardware, environmental temperature, system logs, and "
                 "other alerts to identify and fix the issue. If the problem "
                 "persists, contact your service provider."],
    "14:601a3": ["ERROR", "ALRT_DAE_FAULT_DRIVE_FAULT",
                 "A Disk Array Enclosure (DAE) has faulted. This may have "
                 "occurred because of a faulted disk. Identify and fix the"
                 " issue with the disk. If the problem persists, contact your"
                 " service provider."],
    "14:601a4": ["ERROR", "ALRT_DAE_FAULT_POWERSUPPLY_FAULT",
                 "A Disk Array Enclosure (DAE) has faulted. This may have "
                 "occurred because of a faulted power supply. Identify and fix"
                 " the issue with the power supply. If the problem persists, "
                 "contact your service provider."],
    "14:601a5": ["ERROR", "ALRT_DAE_FAULT_LCC_FAULT",
                 "A Disk Array Enclosure (DAE) has faulted. This may have "
                 "occurred because of a faulted Link Control Card. Identify"
                 " and fix the issue with the Link Control Card. If the "
                 "problem persists, contact your service provider."],
    "14:601a6": ["ERROR", "ALRT_DAE_FAN_FAULT",
                 "The disk array enclosure (DAE) has faulted. This may have "
                 "occurred because of a faulted cooling module. Identify and "
                 "fix the issue with the cooling module. If the problem "
                 "persists, contact your service provider."],
    "14:601a7": ["ERROR", "ALRT_DAE_NO_REASON_FAILURE",
                 "This DAE fault led is on but no specific fault is detected,"
                 " this could be a transient state. Please contact your "
                 "service provider if the issue persists."],
    "14:601a8": ["CRITICAL", "ALRT_DAE_FAULT_LCC_FAULT",
                 "The fault LED on the disk array enclosure (DAE) is on. This"
                 " may have occurred because of an issue with the Link Control"
                 " Card (LCC) cables connecting to the DAE. Replace LCC cables"
                 " to the enclousre first. If it does not solve the problem, "
                 "replace the LCC(s) in the enclosure."],
    "14:601a9": ["CRITICAL", "ALRT_DAE_FAULT",
                 "The Disk Array Enclosure (DAE) has faulted. This may have "
                 "occurred because of a faulted internal component. Power "
                 "cycle the enclosure first. If it does not solve the problem,"
                 " replace the enclosure."],
    "14:601f4": ["ERROR", "ALRT_PWR_SUPPLY_NO_POWER",
                 "A power supply in the enclosure is not receiving power. "
                 "Check the power cables to be sure that each power cable "
                 "is plugged in to its power supply."],
    "14:601f5": ["CRITICAL", "ALRT_PWR_SUPPLY_FAULT",
                 "A power supply in your system has faulted and needs to "
                 "be replaced."],
    "14:601f6": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is"
                 " required."],
    "14:601f7": ["ERROR", "ALRT_PWR_SUPPLY_GONE",
                 "A power supply in your system has been removed and needs "
                 "to be reinstalled."],
    "14:601f8": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this"
                 " time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:601f9": ["CRITICAL", "ALRT_PWR_UNSUPPORTED",
                 "A power supply on your system is not supported. Replace it "
                 "with a supported one."],
    "14:601fa": ["CRITICAL", "ALRT_PWR_SHUTDOWM",
                 "A power supply on your system has shut down. Check the power"
                 " supply cable Connections."],
    "14:601fb": ["CRITICAL", "ALRT_PWR_SMBUS_ACCESS_FAULT",
                 "A power supply on your system cannot be accessed. Try "
                 "reseating the power supply. If the problem persists, you may"
                 " need to replace your power supply."],
    "14:601fc": ["WARNING", "ALRT_PWR_THERMAL_FAULT",
                 "A power supply is operating at a high temperature. The power"
                 " supply may not be the source of the problem. Gather "
                 "diagnostic materials and contact your service provider."],
    "14:601fd": ["CRITICAL", "ALRT_PWR_FW_UPG_FAIL",
                 "Firmware upgrade for the power supply has failed. Contact "
                 "your service provider."],
    "14:60258": ["CRITICAL", "ALRT_DISK_FAULT",
                 "A disk in your system has faulted. Check that the disk is "
                 "seated properly. If the problem persists, replace "
                 "the disk."],
    "14:6025b": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:6025c": ["WARNING", "ALRT_DISK_REBUILD",
                 "A disk is resynchronizing with the system, because  it has"
                 " been replaced. System performance may be affected during "
                 "resynchronization. Caution: Do not do anything with the disk"
                 " until it has finished synchronizing."],
    "14:6025d": ["ERROR", "ALRT_DISK_REMOVED",
                 "A disk in your system has been removed and needs to be "
                 "reinstalled."],
    "14:6025e": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:6025f": ["CRITICAL", "ALRT_DISK_UNUSABLE",
                 "A disk in your system is unusable and needs to be "
                 "replaced."],
    "14:60261": ["ERROR", "ALRT_DISK_WRONG_SLOT",
                 "A disk has been moved and inserted in the wrong slot. "
                 "Reposition disk in the Correct slot."],
    "14:60262": ["WARNING", "ALRT_DISK_EXCEEDS_LIMIT",
                 "The disk is unusable because the total number of disks "
                 "configured has reached the system limit."],
    "14:60263": ["CRITICAL", "ALRT_DISK_NOT_SYMMETRIC",
                 "A disk is unusable because a system Storage Processor (SP) "
                 "cannot communicate with the disk. There are several "
                 "possible causes for this problem. In Unisphere, go to the"
                 " System Health page to locate the SPs. Verify that there is"
                 " not an SP in service mode. Check to be sure a link control"
                 " card (LCC) has not faulted. Then check to be sure the SAS"
                 " cable is connected securely and is not damaged. Lastly, "
                 "reseat the disk by removing and reinserting it. If the "
                 "problem persists, you need to shut down and restart the "
                 "system Click."],
    "14:60264": ["ERROR", "ALRT_DISK_SED_DISK",
                 "Inserting a Self- Encrypting Drive (SED) into a system that"
                 " does not support SED functionality is not allowed. Remove"
                 " the drive and replace it with a non-self- encrypting"
                 " drive."],
    "14:60265": ["ERROR", "ALRT_DISK_SED_ARRAY",
                 "Inserting a drive that does not have self- encrypting "
                 "functionality into a Self-Encrypting Drive (SED) system is"
                 " not allowed. Remove the drive and replace it with an SED"
                 " drive."],
    "14:60266": ["ERROR", "ALRT_DISK_LOCKED_FOREIGN_DISK",
                 "The self-encrypting drive is locked and might have been "
                 "inserted in the wrong array. Insert it in the correct "
                 "array, or revert the drive to its factory default by "
                 "running the svc_key_restore service script. For "
                 "information, go to the EMC Online Support website, "
                 "access the VNXe Product page, and search for VNXe "
                 "Service Commands Technical Notes."],
    "14:60267": ["ERROR", "ALRT_DISK_LOCKED_CORRUPTED_KEY",
                 "The authentication key is corrupted and the disk is "
                 "locked. Please put the system in Service Mode, and run the"
                 " svc_key_restore service script to restore the"
                 " authentication key."],
    "14:60268": ["INFO", "ALRT_DISK_SLOT_EMPTY",
                 "A disk in your system has been removed. the slot is empty."],
    "14:60276": ["ERROR", "ALRT_VVNX_VDISK_OFFLINE",
                 "The virtual disk is not currently attached to the storage"
                 " system. Resolve any connectivity or VMware configuration "
                 "issues, and then try attaching the disk to the VM."],
    "14:60277": ["ERROR", "ALRT_VVNX_VDISK_ERROR",
                 "This virtual disk failed due to a system or I/O error. Check"
                 " the system logs and other alerts to identify the issue. "
                 "Check the VM configuration and virtual environment."],
    "14:60278": ["INFO", "ALRT_VVNX_VDISK_WRONG_SYSTEM",
                 "This virtual disk is accessible, but was originally "
                 "configured for a different storage system. You can choose to"
                 " reconfigure the disk or continue using it. Using the disk "
                 "will overwrite the existing disk configuration and data."],
    "14:60279": ["INFO", "ALRT_VVNX_VDISK_WRONG_POOL",
                 "This virtual disk is working and accessible, but an existing"
                 " pool configuration has been detected on it. Adding the "
                 "virtual  disk to a new pool will delete all data from the "
                 "previous Configuration."],
    "14:6027a": ["ERROR", "ALRT_VVNX_VDISK_TOO_SMALL",
                 "The virtual disk is too small. Detach it from the VM running"
                 " UnityVSA, and attach a larger virtual disk. See the Alerts"
                 " page for the minimum virtual disk size allowed."],
    "14:6027b": ["ERROR", "ALRT_VVNX_VDISK_TOO_LARGE",
                 "The virtual disk is too large. Detach it from the VM running"
                 " UnityVSA, and attach a smaller virtual disk."],
    "14:6027c": ["WARNING", "ALRT_DISK_EOL",
                 "This disk is reaching the end of its service life and needs"
                 " to be replaced"],
    "14:6027d": ["WARNING", "ALRT_VVNX_SPA_VDISK_NOT_REACHABLE",
                 "The Storage Processor SP A cannot reach one of the virtual"
                 " disks. The virtual disk is degraded. Check the VM "
                 "configuration and virtual environment."],
    "14:6027e": ["WARNING", "ALRT_VVNX_SPB_VDISK_NOT_REACHABLE",
                 "The Storage Processor SP B cannot reach one of the virtual "
                 "disks. The virtual disk is degraded. Check the VM "
                 "configuration and virtual environment."],
    "14:6027f": ["ERROR", "ALRT_VDISK_CLONED",
                 "The virtual disk was cloned from another virtual disk. The "
                 "system prevents the use of cloned disks to avoid corrupting"
                 " potentially usable data."],
    "14:60280": ["INFO", "ALRT_DISK_EOL_IN_180_DAYS",
                 "Drive is predicted to wear out in less than 180 days. If the"
                 " drive is a provisioned drive and there is a spare drive"
                 " available, the storage system will automatically replace"
                 " it with no data loss when it reaches end- of-life."],
    "14:60281": ["INFO", "ALRT_DISK_EOL_IN_90_DAYS",
                 "Drive is predicted to wear out in less than 90 days. If the"
                 " drive is a provisioned drive and there is a spare drive "
                 "available, the storage system will automatically replace it"
                 " with no data loss when it reaches end- of-life."],
    "14:60282": ["WARNING", "ALRT_DISK_EOL_IN_30_DAYS",
                 "Drive is predicted to wear out in less than 30 days. If the"
                 " drive is provisioned and there is a spare drive available,"
                 " the storage system will automatically replace the drive "
                 "with no data loss when it reaches end-of-life. If the drive"
                 " is unprovisioned, you should replace it."],
    "14:602bc": ["CRITICAL", "ALRT_LCC_FAULT",
                 "A link control card (LCC) in your Disk Array Enclosure has "
                 "faulted and needs to be replaced."],
    "14:602bd": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:602be": ["CRITICAL", "ALRT_LCC_REMOVED",
                 "A link control card (LCC) in your Disk Array Enclosure has"
                 " been removed and needs to be reinstalled."],
    "14:602bf": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:602c0": ["CRITICAL", "ALRT_LCC_SHUNTED",
                 "The port in the Link Control Card (LCC) within the Disk"
                 " Array Enclosure (DAE) is disabled. Verify the cabling "
                 "exists. If the problem persists, you may need to replace"
                 " the LCC."],
    "14:602c3": ["CRITICAL", "ALRT_LCC_UPG_FAIL",
                 "Firmware upgrade for the link control card (LCC) has failed."
                 " Contact your service provider."],
    "14:602c4": ["ERROR", "ALRT_LCC_CONNECTION_FAULT",
                 "The Link Control Card (LCC) has a connection fault. It may"
                 " have occurred because of a faulted drive, cable, or the "
                 "LCC itself. Replace any faulted disks to see whether the "
                 "fault clears. If the problem persists, contact your service"
                 " provider."],
    "14:60326": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is"
                 " required."],
    "14:60327": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60328": ["WARNING", "ALRT_POOL_USER_THRESH",
                 "This storage pool has exceeded the capacity threshold you "
                 "specified. To allocate more storage space, add additional "
                 "disks to your system."],
    "14:60329": ["CRITICAL", "ALRT_POOL_SYS_DISKS_FAILED",
                 "Depending on the type of disks your system uses, the loss"
                 " of more two or more disks may result in data loss. If "
                 "multiple faulted disk drives are in Disk Processor Enclosure"
                 " (DPE) slots 0-3, contact your service provider for "
                 "assistance with replacement of these system disks."],
    "14:6032a": ["CRITICAL", "ALRT_POOL_NEED_RECOVER",
                 "The pool is offline and requires recovery. Contact your "
                 "service provider."],
    "14:6032b": ["CRITICAL", "ALRT_POOL_OFFLINE",
                 "The pool is offline. Contact your service provider."],
    "14:6032c": ["ERROR", "ALRT_POOL_BAD_VOL",
                 "The pool is unavailable or may have a data inconsistency. "
                 "Try rebooting the storage system. If the problem persists, "
                 "contact your service provider."],
    "14:6032d": ["WARNING", "ALRT_POOL_FAULT",
                 "The pool performance is degraded. Check the storage system "
                 "for hardware faults. Contact your service provider."],
    "14:6032e": ["WARNING", "ALRT_POOL_BAD_VOL",
                 "The pool is unavailable or may have a data inconsistency. "
                 "Try rebooting the storage system. If the problem persists, "
                 "contact your service provider."],
    "14:6032f": ["WARNING", "ALRT_POOL_SPACE_HARVEST_FAIL",
                 "Auto-delete ran into an internal error. The system will make"
                 " another attempt later. If the problem persists, contact "
                 "your service provider."],
    "14:60330": ["WARNING", "ALRT_POOL_SPACE_HARVEST_LWM",
                 "Storage pool could not reach the pool- used-space low "
                 "threshold. To address this issue, follow the suggestions in"
                 " the associated help topic."],
    "14:60331": ["WARNING", "ALRT_POOL_SPACE_HARVEST_HWM",
                 "Automatic snapshot deletion paused, because the storage pool"
                 " could not reach the pool-used-space high threshold. To "
                 "address this issue, follow the suggestions in the"
                 " associated help topic."],
    "14:60332": ["WARNING", "ALRT_POOL_SNAP_HARVEST_FAIL",
                 "Auto-delete ran into an internal error. The system will make"
                 " another attempt later. If the problem persists, contact"
                 " your service provider."],
    "14:60333": ["WARNING", "ALRT_POOL_SNAP_HARVEST_LWM",
                 "Storage pool could not reach the snapshot-used-space low "
                 "threshold. To address this issue, follow the suggestions in"
                 " the associated help topic."],
    "14:60334": ["WARNING", "ALRT_POOL_SNAP_HARVEST_HWM",
                 "Automatic snapshot deletion paused, because the storage pool"
                 " could not reach the snapshot-used- space high threshold. To"
                 " address this issue, follow the suggestions in the"
                 " associated help topic."],
    "14:60335": ["WARNING", "ALRT_POOL_SYSTEM_THRESH",
                 "This storage pool has exceeded the system capacity"
                 " threshold. To allocate more storage space, add additional "
                 "disks to your system."],
    "14:60336": ["ERROR", "ALRT_POOL_CRITICAL_THRESH",
                 "This storage pool exceeds the critical capacity threshold. "
                 "Thin-provisioned resources may suffer data loss or become "
                 "unavailable when the pool reaches full capacity. Snapshots"
                 " may become invalid and replication sessions may stop "
                 "synchronizing for storage resources provisioned in this "
                 "pool. To allocate more storage space, add more disks to "
                 "your system."],
    "14:60337": ["INFO", "ALRT_POOL_SPACE_HARVEST_RUNNING",
                 "Auto-delete of snapshots has been initiated because the "
                 "pool space consumption exceeded the high threshold. If"
                 " automatic snapshot deletion was not expected, you can "
                 "modify the pool properties to disable the feature. Add more"
                 " disks to the pool or increase the automatic deletion "
                 "threshold."],
    "14:60338": ["INFO", "ALRT_POOL_SNAP_HARVEST_RUNNING",
                 "Auto-delete initiated as the snap consumption exceeded the"
                 " high threshold. If automatic snapshot deletion was not "
                 "expected, you can modify the pool properties to disable the "
                 "feature. Add more disks to the pool or increase the"
                 " automatic deletion threshold."],
    "14:60339": ["WARNING", "ALRT_POOL_NEED_RECOVER_LATER",
                 "The storage pool is degraded and requires recovery. This is"
                 " not an urgent issue. Contact your service provider and "
                 "schedule downtime to perform the pool recovery procedure."],
    "14:6033a": ["WARNING", "ALRT_POOL_INSUFFICIENT_FLASH_FOR_STORAGE",
                 "The pool is not performing optimally, because it does not"
                 " have Flash storage. Add Flash drives to the pool. See the"
                 " Best Practices for Peformance and Availability document, "
                 "available at http://bit.ly/unityinfo hub, for "
                 "recommendations on configuring pools."],
    "14:6033b": ["WARNING", "ALRT_POOL_ADDITIONAL_FLASH_NEEDED_FOR_STORAGE",
                 "The pool is not performing optimally due to insufficient "
                 "Flash storage. Add Flash drives to the pool. See the Best"
                 " Practices for Peformance and Availability document, "
                 "available at http://bit.ly/unityinfo hub, for "
                 "recommendations on configuring pools."],
    "14:6033c": ["INFO", "ALRT_POOL_DISK_EOL_WARNING",
                 "Pool has one or more drives predicted to wear out in less "
                 "than 180 days. The storage system will automatically replace"
                 " the affected drives with no data loss when they reach "
                 "end- of-life."],
    "14:6033d": ["INFO", "ALRT_POOL_DISK_EOL_WARNING_RANGE",
                 "Pool has one or more drives predicted to wear out in less"
                 " than 180 days. The storage system will automatically "
                 "replace the affected drives with no data loss when they"
                 " reach end- of-life."],
    "14:6033e": ["INFO", "ALRT_POOL_DISK_EOL_SEVERE",
                 "Pool has one or more drives predicted to wear out in less"
                 " than 90 days. The storage system will automatically replace"
                 " the affected drives with no data loss when they reach"
                 " end- of-life."],
    "14:6033f": ["INFO", "ALRT_POOL_DISK_EOL_SEVERE_RANGE",
                 "Pool has one or more drives predicted to wear out in less"
                 " than 90 days. The storage system will automatically replace"
                 " the affected drives with no data loss when they reach"
                 " end- of-life."],
    "14:60340": ["WARNING", "ALRT_POOL_DISK_EOL_CRITICAL",
                 "Pool has one or more drives predicted to wear out in less "
                 "than 30 days. If there are spare drives available, the"
                 " storage system will automatically replace the affected"
                 " drives with no data loss when they reach end-of-life."],
    "14:60341": ["WARNING", "ALRT_POOL_DISK_EOL_CRITICAL_RANGE",
                 "Pool has one or more drives predicted to wear out in less "
                 "than 30 days. If there are spare drives available, the "
                 "storage system will automatically replace the affected "
                 "drives with no data loss when they reach end-of-life."],
    "14:60342": ["CRITICAL", "ALRT_POOL_DISK_PACO_START_FAIL",
                 "The system could not start an automatic copy of data from "
                 "one or more drives in the pool to replace a  drive that is"
                 " wearing out, because spare drives are not available. Add"
                 " drives to the pool."],
    "14:60343": ["WARNING", "ALRT_POOL_REBUILD",
                 "A storage pool is rebuilding, because it lost a drive. "
                 "System performance may be affected during the rebuilding."
                 " Caution: Do not access the pool until it has finished"
                 " rebuilding."],
    "14:60344": ["INFO", "ALRT_POOL_FINISH_REBUILD",
                 "A storage pool has finished rebuilding and is operating"
                 " normally. No action is required."],
    "14:60345": ["INFO", "ALRT_LOW_SPARE_CAPACITY_STORAGE_POOL",
                 "A storage pool does not have enough spare space. Caution: "
                 "Suggest replacing the failed drive."],
    "14:60346": ["WARNING", "ALRT_INSUFFICIENT_SPARE_CAPACITY_STORAGE_POOL",
                 "A storage pool does not have enough spare space and becomes"
                 " degraded. Caution: Suggest replacing the failed drive."],
    "14:60347": ["INFO", "ALRT_OK_SPARE_CAPACITY_STORAGE_POOL",
                 "The required amount of spare storage space for the pool has"
                 " been restored. No action is required."],
    "14:60348": ["CRITICAL", "ALRT_POOL_DRIVE_EOL_AUTO_PACO_FAILED",
                 "The pool has one or more drives that have reached "
                 "end-of-life threshold and the system failed to automatically"
                 " start procative copying of these drives, even though there"
                 " were spare drives available. Please contact your service "
                 "provider."],
    "14:60349": ["WARNING", "ALRT_POOL_DRIVE_EOL_IN_60_DAYS",
                 "The pool has Flash drives of a specific type that are "
                 "predicted to exceed end-of-life thresholds within 60 days. "
                 "The storage system does not have enough free drives of the "
                 "same type to replace them. Add the required drives to the"
                 " pool."],
    "14:60388": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60389": ["ERROR", "ALRT_NAS_FILESERVER_OFFLINE",
                 "The NAS server is not accessible and its services are not "
                 "available. The file system may be temporarily offline. "
                 "Please contact your service provider."],
    "14:6038b": ["ERROR", "ALRT_NAS_FILESERVER_FAULTED",
                 "The NAS server is faulted, possibly due to an internal "
                 "error. Please contact your service provider."],
    "14:6038c": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:6038d": ["ERROR", "ALRT_NAS_CIFSSERVER_UNJOINED",
                 "The SMB server is no longer joined to the domain. Check "
                 "the network interface and domain settings of the NAS "
                 "server and try to add the SMB server into the domain "
                 "again."],
    "14:6038e": ["ERROR", "ALRT_NAS_CIFSSERVER_TIMENOTSYNC",
                 "The current system time is not synchronized with the Active"
                 " Directory controller of the domain. Check the system NTP "
                 "(Network Time Protocol) settings to ensure the your system's"
                 " time is synchronized with the time of the Active Directory "
                 "controller."],
    "14:6038f": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60390": ["WARNING", "ALRT_NAS_FILEINTERFACE_GATEWAY_UNREACHABLE",
                 "The network interface gateway of the NAS server is"
                 " unreachable. Review the NAS server network interface "
                 "settings. If the problem persists and the NAS server "
                 "network interface settings are correct, review your network"
                 " environment."],
    "14:60391": ["ERROR", "ALRT_NAS_FILEINTERFACE_DUPLICATED_ADDRESS",
                 "The network interface IP address of the NAS server conflicts"
                 " with another host on the same subnet. Review the NAS server"
                 " network interface settings for potential conflicts. If the "
                 "problem persists and the NAS server network interface "
                 "settings are correct, review your network environment."],
    "14:60392": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:60393": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this"
                 " time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:60394": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60396": ["ERROR", "ALRT_NAS_FILELDAPSERVER_OFFLINE",
                 "The LDAP client configured for the NAS server is offline. "
                 "Try resetting the settings of the LDAP client."],
    "14:60398": ["WARNING", "ALRT_NAS_FILELDAPSERVER_FAULTED",
                 "The LDAP client configured for the NAS server has faulted."
                 " Contact your service provider."],
    "14:6039b": ["WARNING", "ALRT_NAS_CIFSSERVER_FAULTED",
                 "The SMB server configured for the NAS server has faulted."
                 " Contact your service provider."],
    "14:603a0": ["ERROR", "ALRT_NAS_CIFSSERVER_OFFLINE",
                 "The SMB server configured for the NAS server is offline. "
                 "Try deleting and recreating it."],
    "14:603a2": ["ERROR", "ALRT_NAS_FILENISSERVER_OFFLINE",
                 "The NIS client configured for the NAS server is offline."
                 " Try to reset settings of the NIS client."],
    "14:603a4": ["WARNING", "ALRT_NAS_FILENISSERVER_FAULTED",
                 "The NIS client configured for the NAS server has faulted. "
                 "Contact your service provider."],
    "14:603a7": ["ERROR", "ALRT_NAS_NFSSERVER_OFFLINE",
                 "The NFS server configured for the NAS server is offline. "
                 "Try disabling the NFS server, and enabling it again."],
    "14:603a9": ["WARNING", "ALRT_NAS_NFSSERVER_FAULTED",
                 "The NFS server configured for the NAS server has faulted. "
                 "Contact your service provider."],
    "14:603ab": ["WARNING", "ALRT_NAS_CIFSSERVER_ALL_DC_DOWN",
                 "Domain controller servers configured for the SMB server are"
                 " not reachable. Check network connectivity. Ensure that at "
                 "least one domain controller is running and the storage "
                 "system can access it."],
    "14:603ac": ["INFO", "ALRT_NAS_CIFSSERVER_SOME_DC_DOWN",
                 "Some domain controller servers configured for the SMB server"
                 " are not reachable."],
    "14:603ad": ["WARNING", "ALRT_NAS_FILELDAPSERVER_NOT_CONNECTED",
                 "None of the LDAP servers configured for LDAP client of the"
                 " NAS server are reachable. Check network connectivity. "
                 "Ensure at least one LDAP server is available and the storage"
                 " system can access it."],
    "14:603ae": ["INFO", "ALRT_NAS_FILELDAPSERVER_SOME_SERVERS_DOWN",
                 "One or more LDAP servers configured for the LDAP client of "
                 "the NAS server are not reachable."],
    "14:603af": ["WARNING", "ALRT_NAS_FILENISSERVER_WRONG_DOMAIN",
                 "The domain configured for the NIS client of the NAS server "
                 "is not valid. Please modify the domain name for the NIS"
                 " client of the NAS server."],
    "14:603b0": ["INFO", "ALRT_NAS_FILENISSERVER_SOME_SERVERS_DOWN",
                 "One or more NIS servers configured for the NIS client of the"
                 " NAS server are not reachable."],
    "14:603b1": ["WARNING", "ALRT_NAS_FILENISSERVER_NOT_CONNECTED",
                 "None of the NIS servers configured for the NIS client of the"
                 " NAS server are reachable. Check network connectivity. "
                 "Ensure that at least one NIS server is running and the "
                 "storage system can access it."],
    "14:603b3": ["ERROR", "ALRT_NAS_FILEDNSSERVER_OFFLINE",
                 "The DNS client configured for the NAS server is offline. "
                 "Try removing the DNS settings, and then configure the DNS "
                 "client settings on the NAS server again."],
    "14:603b4": ["INFO", "ALRT_NAS_FILEDNSSERVER_UNDER_CONSTRUCTION",
                 "The DNS client is initializing."],
    "14:603b5": ["WARNING", "ALRT_NAS_FILEDNSSERVER_FAULTED",
                 "The DNS client configured for the NAS server has faulted. "
                 "Contact your service provider."],
    "14:603b7": ["INFO", "ALRT_NAS_FILEDNSSERVER_SOME_SERVERS_DOWN",
                 "Some DNS servers configured for the DNS client of the NAS "
                 "server are not reachable."],
    "14:603b8": ["WARNING", "ALRT_NAS_FILEDNSSERVER_NOT_CONNECTED",
                 "DNS servers configured for the NIS client of the NAS server "
                 "are not reachable. Check network connectivity. Ensure that "
                 "at least one DNS server is running and the storage system "
                 "can access it."],
    "14:603b9": ["WARNING", "ALRT_NAS_FILEINTERFACE_NO_SOURCE",
                 "The file interface was deleted from the replication source"
                 " NAS server, but it still exists on the replication "
                 "destination NAS server. Manually remove the file interface "
                 "from the destination NAS server. If this does not help, "
                 "restart management services on the destination storage "
                 "system."],
    "14:603ba": ["WARNING", "ALRT_NAS_FILELDAPSERVER_NO_SOURCE",
                 "LDAP settings were deleted from the replication source NAS "
                 "server, but they still exist on the replication destination"
                 " NAS server. Manually remove LDAP settings from the "
                 "destination NAS server. If this does not help, restart "
                 "management services on the destination storage system."],
    "14:603bb": ["WARNING", "ALRT_NAS_FILENISSERVER_NO_SOURCE",
                 "NIS settings were deleted from the replication source NAS "
                 "server, but they still exist on the replication destination"
                 " NAS server. Manually remove NIS settings from the "
                 "destination NAS server. If this does not help, restart"
                 " management services on the destination storage system."],
    "14:603bc": ["WARNING", "ALRT_NAS_FILEDNSSERVER_NO_SOURCE",
                 "DNS settings were deleted from the replication source NAS "
                 "server, but they still exist on the replication destination"
                 " NAS server. Manually remove DNS settings from the "
                 "destination NAS server. If this does not help, restart "
                 "management services on the destination storage system."],
    "14:603bd": ["WARNING", "ALRT_NAS_FILEINTERFACE_OFFLINE",
                 "The NAS server file interface is offline. Contact your "
                 "service provider."],
    "14:603be": ["WARNING", "ALRT_NAS_FILELDAPSERVER_BADLY_CONFIGURED",
                 "LDAP client on the NAS server is configured incorrectly. "
                 "Verify the provided LDAP schema, LDAP client account "
                 "settings, Bind Distinguished Name, and password. Check the "
                 "access permissions of the LDAP client account for the "
                 "configured LDAP servers."],
    "14:603bf": ["WARNING",
                 "ALRT_NAS_FILELDAPSERVER_INAPPROPRIATE_AUTHENTICATION",
                 "The LDAP client attempted to perform a type of "
                 "authentication that is not allowed for the target user. "
                 "This may also indicate that the client attempted to perform "
                 "anonymous authentication when that is not allowed. Verify "
                 "the authorization settings for the LDAP client account."],
    "14:603c0": ["WARNING", "ALRT_NAS_FILELDAPSERVER_INVALID_CREDENTIALS",
                 "The LDAP client attempted to bind as a user that either does"
                 " not exist, not allowed to bind, or the credentials are "
                 "invalid. Verify LDAP client Bind Distinguished Name and "
                 "Password, and permissions for this account."],
    "14:603c1": ["WARNING", "ALRT_NAS_FILELDAPSERVER_INSUFFICIENT_PERMISSIONS",
                 "The LDAP client does not have permission to perform the "
                 "requested operation. Verify authorization settings for the "
                 "LDAP client account."],
    "14:603c2": ["WARNING", "ALRT_NAS_FILEINTERFACE_NO_DEVICE",
                 "The system is unable to detect an Ethernet port or link "
                 "aggregation on which the NAS server network interface was "
                 "configured. Switch the interface to use another Ethernet "
                 "port or link aggregation. If this does not help, restart the"
                 " management software. If the problem persists, contact your"
                 " service provider."],
    "14:603ca": ["ERROR", "ALRT_NAS_CEPP_FAULTED",
                 "The CEPA server configured for the specified NAS server is"
                 " not functional. Verify that the CEPA settings are valid."],
    "14:603cc": ["ERROR", "ALRT_NAS_CEPP_NOT_CONNECTED",
                 "All servers configured for the CEPA server of the specified"
                 " NAS server cannot be reached. Verify: 1) That the network"
                 " addresses of the CEPA servers are valid. 2) That the "
                 "network is available and that the CEPA facility is running "
                 "on the CEPA server. 3) The network integrity between the "
                 "storage system and the CEPA server."],
    "14:603cd": ["WARNING", "ALRT_NAS_CEPP_SOME_SERVERS_DOWN",
                 "Some servers configured for the CEPA server of the "
                 "specified NAS server cannot be reached. Verify: 1) That the"
                 " network addresses of the CEPA servers are valid. 2) That "
                 "the network is available and that the CEPA facility is "
                 "running on the CEPA server. 3) The network integrity between"
                 " the storage system and the CEPA server."],
    "14:603d3": ["WARNING", "ALRT_NAS_FILESERVER_KEYTAB_IS_NOT_UPLOADED",
                 "Secure NFS is not working. Upload a keytab file to the "
                 "specified NAS server."],
    "14:603e8": ["CRITICAL", "ALRT_SLIC_FAULT",
                 "An I/O module in your Disk Processor Enclosure has faulted"
                 " and needs to be replaced."],
    "14:603ea": ["ERROR", "ALRT_SLIC_MISMATCH",
                 "The I/O modules in the Storage Processors (SP) are "
                 "configured incorrectly. I/O modules must be configured "
                 "symmetrically."],
    "14:603eb": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:603ed": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:603ee": ["CRITICAL", "ALRT_SLIC_UNSUPPORT",
                 "An I/O module in your Disk Processor Enclosure is the wrong"
                 " model type. Replace it with a supported model."],
    "14:603ef": ["WARNING", "ALRT_SLIC_UNCONFIG",
                 "This I/O module has been inserted into one of your Storage"
                 " Processors (SP) but has not yet been configured. Commit"
                 " the I/O module."],
    "14:603f3": ["WARNING", "ALRT_SLIC_MISSING",
                 "A previously configured I/O module is missing. Reboot the"
                 " Storage Processors (SP) and then reseat the I/O module."],
    "14:603f4": ["CRITICAL", "ALRT_SLIC_UNINITIALIZED",
                 "The inserted I/O module has not been initialized and cannot"
                 " be used. Wait for the system to load drivers that "
                 "initialize the I/O module."],
    "14:603f5": ["INFO", "ALRT_SLIC_EMPTY",
                 "The Disk Processor Enclosure (DPE) contains a vacant I/O"
                 " module slot."],
    "14:603f6": ["ERROR", "ALRT_SLIC_INCORRECT",
                 "An incorrect type of I/O module has been inserted. The ports"
                 " in this slot have been configured for a different type of"
                 " I/O module. Replace it with a supported I/O module."],
    "14:603f7": ["CRITICAL", "ALRT_SLIC_POWEROFF",
                 "The I/O module is powered off. Try rebooting the Storage"
                 " Processor (SP). If the I/O module remains powered off after"
                 " a reboot, you may need to replace the I/O module."],
    "14:603f8": ["CRITICAL", "ALRT_SLIC_POWERUPFAILED",
                 "The system was unable to power on this I/O module. Replace"
                 " the I/O module."],
    "14:603f9": ["CRITICAL", "ALRT_SLIC_NOTCOMMITTED",
                 "This I/O module will remain unsupported until the current"
                 " software version is committed. Reboot the system to commit"
                 " the software version."],
    "14:6044c": ["CRITICAL", "ALRT_SP_FAULT",
                 "The Storage Processor (SP) has faulted. Try rebooting the"
                 " SP. If the fault persists or occurs repeatedly, the SP"
                 " needs to be replaced."],
    "14:6044d": ["CRITICAL", "ALRT_SP_MISSING",
                 "A Storage Processor is missing and needs to be reinstalled"],
    "14:6044e": ["WARNING", "ALRT_SP_CACHE",
                 "The write cache on the Storage Processor (SP) is "
                 "temporarily disabled. An SP may be in service mode or "
                 "there may be problem with a hardware component. Check "
                 "related alerts and fix the underlying problems. When the"
                 " problem is fixed, the write cache is automatically re-"
                 "enabled."],
    "14:6044f": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is"
                 " required."],
    "14:60450": ["CRITICAL", "ALRT_SP_PROBLEM",
                 "An issue has occurred with the system software on this"
                 " Storage Processor (SP). Before you proceed, collect service"
                 " information. Ensure that the cables are connected securely"
                 " and not damaged, and then reboot the SP. If rebooting the "
                 "SP does not resolve the issue, reimage the SP. If the"
                 "problem still persists, contact your service provider."],
    "14:60451": ["CRITICAL", "ALRT_RESCUE_MODE",
                 "You may have manually put the Storage Processor (SP) in "
                 "Service Mode or the SP entered Service Mode due to some"
                 " problem with the SP."],
    "14:60452": ["CRITICAL", "ALRT_SP_FAULT_BLADE",
                 "The Storage Processor (SP) has faulted and needs to be "
                 "replaced."],
    "14:60453": ["CRITICAL", "ALRT_SP_CABLE_WRONG_SAS",
                 "The SAS port on this Storage Processor (SP) is cabled"
                 " incorrectly. Ensure the SAS port is cabled correctly."],
    "14:60454": ["CRITICAL", "ALRT_SP_FAULT_CPU_DIMMS",
                 "The CPU module and memory modules have faulted in this "
                 "Storage Processor (SP). Power cycle the system."],
    "14:60455": ["CRITICAL", "ALRT_SP_FAULT_CPU",
                 "The CPU module in this Storage Processor (SP) has faulted. "
                 "You need to replace the SP."],
    "14:60456": ["CRITICAL", "ALRT_SP_FAULT_CPU_SLIC0",
                 "The CPU module and I/O module 0 in this Storage Processor "
                 "(SP) have faulted. Power cycle the system."],
    "14:60457": ["CRITICAL", "ALRT_SP_FAULT_CPU_SLIC1",
                 "The CPU module and the I/O module 1 in this Storage "
                 "Processor (SP) have faulted. Power cycle the system."],
    "14:6045a": ["CRITICAL", "ALRT_SP_FAULT_DIMM0_1",
                 "Memory modules 0 and 1 in this Storage Processor (SP) have"
                 " faulted and need to be replaced."],
    "14:6045b": ["CRITICAL", "ALRT_SP_FAULT_DIMM0",
                 "Memory module 0 in this Storage Processor (SP) has faulted "
                 "and needs to be replaced."],
    "14:6045c": ["CRITICAL", "ALRT_SP_FAULT_DIMM1",
                 "Memory module 1 in this Storage Processor (SP) has faulted"
                 " and needs to be replaced."],
    "14:6045d": ["CRITICAL", "ALRT_SP_FAULT_DIMM2",
                 "Memory module 2 in this Storage Processor (SP) has faulted "
                 "and needs to be replaced."],
    "14:6045e": ["CRITICAL", "ALRT_SP_FAULT_DIMMS",
                 "Memory modules in this Storage Processor (SP) have faulted "
                 "and need to be replaced."],
    "14:6045f": ["CRITICAL", "ALRT_SP_FAULT_ENCLOSURE",
                 "A fault in the Disk Processor Enclosure (DPE) has placed "
                 "the Storage Processor (SP) in Service Mode. Power cycle "
                 "the system."],
    "14:60461": ["CRITICAL", "ALRT_SP_FLAREDB_DISK_FAULT",
                 "A disk on this Storage Processor (SP) has faulted and needs "
                 "to be replaced."],
    "14:60462": ["CRITICAL", "ALRT_SP_INVALID_DISK_CONFIG",
                 "The disk configuration on this Storage Processor (SP) is"
                 " unsupported."],
    "14:60465": ["CRITICAL", "ALRT_SP_NO_IO_WITH_LCC",
                 "The Storage Processor (SP) is unable to communicate with the"
                 " link control card (LCC) and has been put into Service Mode."
                 " You need to shut down the system. From Unisphere, click"
                 " Settings  Service System, enter your service password and"
                 " click Shut Down System."],
    "14:60466": ["CRITICAL", "ALRT_SP_NO_SAS_PORT",
                 "Unable to detect the SAS port on this Storage Processor"
                 " (SP)."],
    "14:60467": ["CRITICAL", "ALRT_SP_FAULT_POST",
                 "The Power-On Self Test (POST) failed to run on this Storage"
                 " Processor (SP). You need to replace this SP."],
    "14:60469": ["CRITICAL", "ALRT_SP_FAULT_SLIC0",
                 "I/O module 0 in this Storage Processor (SP) has faulted and"
                 " needs to be replaced."],
    "14:6046a": ["CRITICAL", "ALRT_SP_FAULT_SLIC1",
                 "I/O module 1 in the Storage Processor (SP) has faulted and "
                 "needs to be replaced."],
    "14:6046b": ["CRITICAL", "ALRT_SP_FAULT_SSD",
                 "A solid state disk (SSD) in this Storage Processor (SP) has"
                 " faulted and needs to be replaced."],
    "14:6046c": ["CRITICAL", "ALRT_SP_UNEXPECTED",
                 "An unexpected error has occurred with the Storage Processor"
                 " (SP). Try rebooting the SP."],
    "14:6046f": ["WARNING", "ALRT_SP_START",
                 "The Storage Processor (SP) is currently rebooting. Please"
                 " wait for the SP to reboot."],
    "14:60470": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60471": ["WARNING", "ALRT_SP_USER_SERVICE_MODE",
                 "The Storage Processor (SP) has been manually put in to"
                 " Service Mode."],
    "14:60472": ["CRITICAL", "ALRT_SP_IO_MISCONFIGURED",
                 "This I/O module has been inserted into one of your Storage "
                 "Processors (SPs) but is not yet configured. Reboot the SP "
                 "and commit the I/O module."],
    "14:60473": ["ERROR", "ALRT_SP_HUNG",
                 "The Storage Processor (SP) did not restart successfully."
                 " Wait 5 minutes to see if the problem resolves itself. If "
                 "the problem persists, you will need to restart the SP."],
    "14:60474": ["CRITICAL", "ALRT_SP_SYS_DISK_TYPE",
                 "A replacement disk should be the same type (SAS, SATA, "
                 "FLASH) as the disk it is replacing."],
    "14:60475": ["CRITICAL", "ALRT_SP_SYS_DISK_BLK",
                 "A replacement disk should be the same type (SAS, SATA, "
                 "FLASH) and have the same capacity (size and speed) as the "
                 "disk it is replacing."],
    "14:60476": ["CRITICAL", "ALRT_SP_SYS_DISK_SIZE",
                 "A replacement disk should have the same capacity (size and "
                 "speed) as the disk it is replacing."],
    "14:60477": ["CRITICAL", "ALRT_SP_DPE_SN",
                 "The Product ID / SN cannot be read from the Disk Processor"
                 " Enclosure (DPE) and will need to be reprogrammed. Contact"
                 " your service provider for assistance."],
    "14:60479": ["CRITICAL", "ALRT_SP_FAULT_DIMM0_2",
                 "Memory modules 0 and 2 in this Storage Processor (SP) have"
                 " faulted and need to be replaced."],
    "14:6047a": ["CRITICAL", "ALRT_SP_FAULT_DIMM1_3",
                 "Memory modules 1 and 3 in this Storage Processor (SP) have "
                 "faulted and need to be replaced."],
    "14:6047b": ["CRITICAL", "ALRT_SP_FAULT_DIMM2_3",
                 "Memory modules 2 and 3 in this Storage Processor (SP) have"
                 " faulted and need to be replaced."],
    "14:6047c": ["CRITICAL", "ALRT_SP_FAULT_DIMM3",
                 "Memory module 3 in this Storage Processor (SP) has faulted "
                 "and needs to be replaced."],
    "14:6047d": ["WARNING", "ALRT_SP_UNSAFE_REMOVE",
                 "The Storage Processor (SP) is unsafe to remove. Wait for the"
                 " Unsafe to Remove LED to turn off."],
    "14:6047e": ["WARNING", "ALRT_SP_DEGRADED",
                 "The Storage  Processor (SP) is operating in a degraded "
                 "state. Check the system logs or other alerts to identify and"
                 " fix the issue. If the problem persists, you may need to "
                 "replace the SP."],
    "14:60482": ["WARNING", "ALRT_SP_READ_CACHE_DISABLED",
                 "The read cache on the Storage Processor (SP) is temporarily"
                 " disabled. An SP may be in service mode or there may be"
                 " problem with a hardware component. Check related alerts and"
                 " fix the underlying problems. When the problem is fixed, the"
                 " read cache is automatically re- enabled. If one SP is in"
                 " service mode, rebooting the active SP will re-enable the"
                 " read cache."],
    "14:60483": ["CRITICAL", "ALRT_SP_SHUTDOWN",
                 "There was a problem shutting down a Storage Processor (SP)."
                 " Power-cycle the SP manually."],
    "14:60485": ["CRITICAL", "ALRT_SP_SASEXPANDER_FAULT",
                 "SAS expander in the Storage Processor (SP) has faulted."
                 " Check the system logs and try rebooting the SP. If the "
                 "problem persists, you may need to replace the SP."],
    "14:60486": ["WARNING", "ALRT_SP_SASEXPANDER_DEGRADED",
                 "The SAS expander in the Storage Processor (SP) is operating"
                 " in a degraded mode. Check system logs and try rebooting the"
                 " SP. If the problem persists, you may need to replace the"
                 " SP."],
    "14:60487": ["CRITICAL", "ALRT_SP_RESCUE_DISK_UNKNOWN",
                 "The system is unable to run the disk check. Disks status "
                 "cannot be determined."],
    "14:60488": ["ERROR", "ALRT_SP_SHUTDOWN_WARNING",
                 "The Storage Processor (SP) is shutting down. The temperature"
                 " of the storage system may be too high to support safe "
                 "operation. Check the system logs and other alerts to "
                 "identify the issue. If the problem persists, contact your"
                 " service provider."],
    "14:60489": ["ERROR", "ALRT_SP_AMBIENT_TEMPERATURE_FAULT",
                 "The ambient temperature of Storage Processor (SP) is high."
                 " Ensure that the fan modules are operating normally and the"
                 " environment temperature is OK."],
    "14:6048a": ["CRITICAL", "ALRT_VVNX_SP_FAULT",
                 "The Storage Processor (SP) has faulted. Reboot or re- image"
                 " the SP using service actions, or reboot the SP using "
                 "vSphere. If the problem persists, contact your service"
                 " provider."],
    "14:6048b": ["WARNING", "ALRT_VVNX_SP_DEGRADED",
                 "The Storage Processor is operating in a degraded state. "
                 "Check the system logs and other alerts to identify the "
                 "issue."],
    "14:6048c": ["WARNING", "ALRT_VVNX_SP_READ_CACHE_DISABLED",
                 "The read cache on the Storage Processor is temporarily "
                 "disabled. Check related alerts and fix the underlying "
                 "problems. When the problems are fixed, the read cache is "
                 "automatically re- enabled."],
    "14:6048d": ["ERROR", "ALRT_VVNX_SP_SHUTDOWN_WARNING",
                 "The Storage Processor is shutting down. Check the system "
                 "logs and other alerts to identify the issue."],
    "14:6048e": ["CRITICAL", "ALRT_VVNX_SP_SHUTDOWN",
                 "There was a problem shutting down a Storage Processor (SP)."
                 " Reboot the SP using the hypervisor."],
    "14:6048f": ["CRITICAL", "ALRT_VVNX_SP_PROBLEM",
                 "An issue has occurred with the system software on this "
                 "Storage Processor (SP). Before you proceed, collect service"
                 " information. Reboot the SP using service actions or the "
                 "hypervisor. If the issue persists, contact your service "
                 "provider or refer to the EMC community forums."],
    "14:60490": ["CRITICAL", "ALRT_VVNX_HARDWARE_CONFIG_UNSUPPORTED",
                 "Virtual hardware configuration does not match the supported"
                 " profiles. Try fixing the configuration from the hypervisor"
                 " hosting the virtual machine. Run the svc_diag -b command "
                 "on the SP for more information."],
    "14:60491": ["CRITICAL", "ALRT_SP_SAS_EXP_FW_UPG_FAIL",
                 "Firmware upgrade for the SAS Expander on the storage "
                 "processor has failed. Contact your service provider."],
    "14:60492": ["WARNING", "ALRT_SP_HELD_IN_RESET",
                 "The storage processor has been placed in a held in reset "
                 "state, a special service state for performing certain"
                 " hardware services. Reboot the SP when the hardware service"
                 " is completed."],
    "14:60493": ["CRITICAL", "ALRT_BAD_DIMM_CONFIG",
                 "Incorrect amount or configuration of memory has placed the"
                 " storage processor (SP) in service mode. Fix the memory "
                 "configuration and then reboot the SP. For more information,"
                 " refer to the Customer Replacement Procedure Replacing  a"
                 " faulted memory module located at EMC Online Support "
                 "(https://support.emc. com)."],
    "14:604b0": ["CRITICAL", "ALRT_SSD_FAULT",
                 "A solid state disk (SSD) in a Storage Processor (SP) has"
                 " faulted and needs to be replaced."],
    "14:604b1": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:604b2": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:604b3": ["CRITICAL", "ALRT_SSD_REMOVED",
                 "A solid state disk (SSD) in a Storage Processor (SP) has "
                 "been removed and needs to be reinstalled."],
    "14:604b4": ["WARNING", "ALRT_SSD_FAILING",
                 "This solid state drive (SSD) is reaching the end of its"
                 " service life expectancy and needs to be replaced."],
    "14:60514": ["ERROR", "ALRT_SYSTEM_CRITICAL",
                 "The system has experienced one or more failures, which may"
                 " result in data loss. You need to take immediate action."
                 " Check related alerts and fix the underlying problems."],
    "14:60515": ["WARNING", "ALRT_SYSTEM_DEGRADED",
                 "The system has experienced one or more failures resulting "
                 "in degraded system performance. Check related alerts and "
                 "fix the underlying problems."],
    "14:60516": ["ERROR", "ALRT_SYSTEM_MAJOR_FAILURE",
                 "The system has experienced one or more major failures, "
                 "which have significant impact on the system. You need to "
                 "take immediate action. Check related alerts and fix the "
                 "underlying problems."],
    "14:60517": ["ERROR", "ALRT_SYSTEM_MINOR_FAILURE",
                 "The system has experienced one or more minor failures. Check"
                 " related alerts and fix the underlying problems."],
    "14:60518": ["CRITICAL", "ALRT_SYSTEM_NON_RECOVERABLE",
                 "The system has experienced one or more nonrecoverable "
                 "failures, which may have resulted in data loss. Use the "
                 "System Health page to see the health state of hardware "
                 "and system components."],
    "14:60519": ["INFO", "ALRT_SYSTEM_OK",
                 "The system is operating normally."],
    "14:6051a": ["INFO", "ALRT_SYSTEM_UNKNOWN",
                 "The system health cannot be determined. Check related alerts"
                 " and fix the underlying problems."],
    "14:60579": ["ERROR", "ALRT_SAS_PORT_LINK_DOWN",
                 "The SAS cable connected to the SAS port may not be connected"
                 " securely, or may be damaged or missing."],
    "14:6057a": ["INFO", "ALRT_PORT_LINK_DOWN_NOT_IN_USE",
                 "The port link is down, but not in use. No action is "
                 "required."],
    "14:6057b": ["ERROR", "ALRT_PORT_MGT_NOT_CONNECTED",
                 "The network connection to the management port has been lost."
                 " Check the cable and network configuration."],
    "14:6057c": ["INFO", "ALRT_PORT_LINK_UP",
                 "The port is operating normally."],
    "14:6057d": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60580": ["ERROR", "ALRT_PORT_LINK_DOWN",
                 "The port has lost communication with the network."],
    "14:60581": ["ERROR", "ALRT_DAE_TOO_MANY",
                 "The number of Disk Array Enclosures (DAEs) added has "
                 "exceeded the maximum allowed. Remove the newly "
                 "attached DAE."],
    "14:60582": ["WARNING", "ALRT_SASPORT_DEGRADED",
                 "The SAS port on the Storage Processor (SP) is operating in "
                 "a degraded mode. You may need to replace the SP that "
                 "contains the degraded component."],
    "14:60583": ["CRITICAL", "ALRT_SASPORT_UNINITIALIZED",
                 "A SAS port on your system is not initialized. Identify the "
                 "SAS port, check the system log for hardware errors or "
                 "warnings. If the problem persists, you may need to replace"
                 " the Storage Processor (SP)."],
    "14:60584": ["INFO", "ALRT_SASPORT_EMPTY",
                 "The Disk Processor Enclosure (DPE) contains a vacant "
                 "SAS port."],
    "14:60585": ["WARNING", "ALRT_SASPORT_MISSING",
                 "The Storage Processor (SP) cannot detect a previously "
                 "configured SAS port. Check system logs and reboot the SP. "
                 "If the problem persists, you may need to replace the SP."],
    "14:60586": ["CRITICAL", "ALRT_SASPORT_FAULT",
                 "A SAS port has faulted. Replace the Storage Processor (SP) "
                 "containing the faulted port."],
    "14:60587": ["CRITICAL", "ALRT_SASPORT_UNAVAILABLE",
                 "A SAS port is not available. Check system logs and reboot"
                 " the Storage Processor (SP). If the problem persists, you"
                 " may need to replace the SP."],
    "14:60589": ["CRITICAL", "ALRT_SASPORT_SFP_REMOVED",
                 "A Small Form-factor Pluggable (SFP) module in one of the "
                 "SAS ports on your Storage Processor (SP) has been removed."
                 " Reinsert a supported SFP module."],
    "14:6058a": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:6058d": ["WARNING", "ALRT_ETHERNETPORT_DEGRADED",
                 "Performance of an Ethernet port has degraded. Identify  "
                 "the Ethernet port, check the cabling, and network "
                 "configuration. If the problem persists, you may need to "
                 "replace the Storage Processor (SP)."],
    "14:6058e": ["CRITICAL", "ALRT_ETHERNETPORT_UNINITIALIZED",
                 "An Ethernet port on your system is not initialized. Identify"
                 "  the Ethernet port, check the cabling, and network "
                 "configuration. If the problem persists, you may need to "
                 "replace the Storage Processors (SPs)."],
    "14:6058f": ["INFO", "ALRT_ETHERNETPORT_EMPTY",
                 "The Disk Processor Enclosure (DPE) contains a vacant "
                 "Ethernet port."],
    "14:60590": ["WARNING", "ALRT_ETHERNETPORT_MISSING",
                 "The system is unable to detect an Ethernet port on the "
                 "Storage Processor (SP). Check system logs and reboot the "
                 "SP. If the problem persists, you may need to replace the "
                 "SP."],
    "14:60591": ["CRITICAL", "ALRT_ETHERNETPORT_FAULTED",
                 "An Ethernet port has faulted. Check system log for hardware"
                 " errors or warnings and try rebooting the Storage Processor "
                 "(SP). If the problem persists, you may need to replace the "
                 "I/O module or the SP containing the faulted port."],
    "14:60592": ["CRITICAL", "ALRT_ETHERNETPORT_UNAVAILABLE",
                 "An Ethernet port on the Storage Processor (SP) is not "
                 "available. Please check the cable and network configuration,"
                 " and then restart the SP. If the problem persists, you may"
                 " need to replace the SP."],
    "14:60593": ["CRITICAL", "ALRT_ETHERNETPORT_DISABLED",
                 "An Ethernet port on your Storage Processor (SP) is disabled."
                 " Please check system logs, cabling, and network "
                 "configuration, and then restart the SP. If the problem "
                 "persists, you may need to replace the SP."],
    "14:60594": ["ERROR", "ALRT_PORT_LINK_DOWN",
                 "The port has lost communication with the network."],
    "14:60595": ["CRITICAL", "ALRT_ETHERNETPORT_SFP_UNSUPPORT",
                 "The Small Form-factor Pluggable (SFP) module inserted in "
                 "this Ethernet port is not supported. Replace it with a"
                 " supported SFP module."],
    "14:60596": ["ERROR", "ALRT_ETHERNETPORT_SFP_FAULT",
                 "The Small Form-factor Pluggable (SFP) module in this"
                 " Ethernet port has faulted and needs to be replaced."],
    "14:60597": ["ERROR", "ALRT_ETHERNETPORT_OVERLIMIT",
                 "This Ethernet port cannot be used because it exceeds "
                 "the number of supported ports. Remove the I/O module that"
                 " contains this port."],
    "14:60598": ["CRITICAL", "ALRT_ETHERNETPORT_INCORRECTSLIC",
                 "An incorrect type of I/O module has been inserted. The"
                 " system does not support the Ethernet port configuration for"
                 " this port. Replace the I/O module."],
    "14:60599": ["CRITICAL", "ALRT_SASPORT_SFP_UNSUPPORT",
                 "The Small Form-factor Pluggable (SFP) module inserted in "
                 "this SAS port is not supported. Replace it with a supported"
                 " SFP module."],
    "14:6059a": ["CRITICAL", "ALRT_SASPORT_SFP_FAULT",
                 "The Small Form-factor Pluggable (SFP) module in this SAS "
                 "port has faulted and needs to be replaced."],
    "14:6059b": ["ERROR", "ALRT_SASPORT_OVERLIMIT",
                 "This SAS port cannot be used because it exceeds the number"
                 " of supported ports. Remove the I/O module that contains"
                 " this port."],
    "14:6059c": ["CRITICAL", "ALRT_SASPORT_INCORRECTSLIC",
                 "An incorrect type of I/O module has been inserted. The"
                 " system does not support the SAS port configuration for this"
                 " port. Replace the I/O module."],
    "14:6059d": ["WARNING", "ALRT_ETHERNETPORT_SFP_REMOVED",
                 "The Small Form-factor Pluggable (SFP) module in this"
                 " Ethernet port has been removed. Since the port is in use,"
                 " reinsert a supported SFP module."],
    "14:6059e": ["WARNING", "ALRT_VVNX_ETHERNETPORT_DEGRADED",
                 "Performance of an Ethernet port has degraded. Identify the "
                 "Ethernet port on the System View page, and then check the "
                 "network configuration."],
    "14:6059f": ["CRITICAL", "ALRT_VVNX_ETHERNETPORT_UNINITIALIZED",
                 "An Ethernet port on your system is not initialized. Identify"
                 " the Ethernet port using the System View page, and then"
                 " check the network configuration."],
    "14:605a0": ["CRITICAL", "ALRT_VVNX_ETHERNETPORT_FAULTED",
                 "An Ethernet port on your system has faulted. Check the "
                 "system log for errors or warnings, and then reboot the "
                 "Storage Processor."],
    "14:605a1": ["CRITICAL", "ALRT_VVNX_ETHERNETPORT_UNAVAILABLE",
                 "An Ethernet port on your system is not available. Identify"
                 " the Ethernet port using the System Health page, check the "
                 "network configuration, and then restart the SP."],
    "14:605a2": ["CRITICAL", "ALRT_VVNX_ETHERNETPORT_DISABLED",
                 "An Ethernet port on your system is disabled. Check the "
                 "system logs and network configuration, and then reboot the"
                 " Storage Processor."],
    "14:605a3": ["INFO", "ALRT_ETHERNETPORT_SFP_REMOVED_NOT_IN_USE",
                 "The Small Form-factor Pluggable (SFP) module in this "
                 "Ethernet port has been removed. Since the port is not in"
                 " use, no action is required."],
    "14:605a4": ["ERROR", "ALRT_VVNX_PORT_MGT_NOT_CONNECTED",
                 "The network connection to the management port has been lost."
                 " Check the virtual environment and network configuration."],
    "14:605a5": ["INFO", "ALRT_ETHERNETPORT_SFP_ASYMMETRIC",
                 "The SFPs in the Storage Processor(SP) are configured"
                 " incorrectly. Its supported speeds is asymmetric with "
                 "its peer's."],
    "14:605dc": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:605dd": ["CRITICAL", "ALRT_CM_REMOVED",
                 "The cooling module has been removed. Insert the cooling"
                 " module again."],
    "14:605de": ["WARNING", "ALRT_CM_SINGLE_FAULT",
                 "One of the fans in the cooling module has faulted. Replace"
                 " the cooling module."],
    "14:605df": ["CRITICAL", "ALRT_CM_MULTI_FAULT",
                 "More than one of the fans in the cooling module have"
                 " faulted. Replace the cooling module."],
    "14:605e0": ["CRITICAL", "ALRT_CM_SMBUS_ACCESS_FAULT",
                 "The cooling module has an access issue. Reinsert the "
                 "cooling module again. If the fault persists or occurs "
                 "repeatedly, you may need to replace the cooling module."],
    "14:605e1": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:605e2": ["CRITICAL", "ALRT_CM_UPG_FAIL",
                 "Firmware upgrade for the cooling module has failed. Contact"
                 " your service provider."],
    "14:605e3": ["CRITICAL", "ALRT_CM_FAULT",
                 "A cooling module has faulted. Replace the cooling module."],
    "14:60641": ["WARNING", "ALRT_DPE_FAILED_COMPONENT",
                 "The Disk Processor Enclosure (DPE) has one or more faulted"
                 " components."],
    "14:60642": ["CRITICAL", "ALRT_DPE_INVALID_DRIVE",
                 "There is an invalid disk in the Disk Processor Enclosure "
                 "(DPE). Replace the disk with the correct disk type."],
    "14:60643": ["CRITICAL", "ALRT_DPE_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may "
                 "have occurred because of a faulted subcomponent. Identify "
                 "and fix the issue with the subcomponent. If the problem "
                 "persists, contact your service provider."],
    "14:60645": ["CRITICAL", "ALRT_DPE_MISCONFIGURED",
                 "The Disk Processor Enclosure (DPE) has been cabled or "
                 "configured incorrectly. Refer to the Installation Guide for"
                 " installation and cabling instructions. Go to the support"
                 " website to access the latest product documentation."],
    "14:60646": ["CRITICAL", "ALRT_DPE_MISCONFIGURED",
                 "The Disk Processor Enclosure (DPE) has been cabled or "
                 "configured incorrectly. Refer to the Installation Guide for"
                 " installation and cabling instructions. Go to the support"
                 " website to access the latest product documentation."],
    "14:60648": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60649": ["CRITICAL", "ALRT_PWR_SUPPLY_FAULT",
                 "A power supply in your system has faulted and needs to be"
                 " replaced."],
    "14:6064a": ["CRITICAL", "ALRT_SLIC_FAULT",
                 "An I/O module in your Disk Processor Enclosure has faulted"
                 " and needs to be replaced."],
    "14:6064b": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:6064e": ["CRITICAL", "ALRT_DPE_CROSSCABLED",
                 "The cabling from Disk Processor Enclosure (DPE) to Disk "
                 "Array Enclosure (DAE) is incorrect."],
    "14:6064f": ["WARNING", "ALRT_DPE_TEMPERATURE_WARNING",
                 "The Disk Processor Enclosure (DPE) temperature has reached"
                 " the warning threshold. This may lead to the DPE shutting "
                 "down. Check the hardware, environmental temperature, system"
                 " logs, and other alerts to identify and fix the issue. If "
                 "the problem persists, contact your service provider."],
    "14:60650": ["ERROR", "ALRT_DPE_TEMPERATURE_FAULT",
                 "The Disk Processor Enclosure (DPE) temperature has reached "
                 "the failure threshold. The DPE will shut down shortly. "
                 "Check the hardware, environmental temperature, system logs,"
                 " and other alerts to identify and fix the issue. If the "
                 "problem persists, contact your service provider."],
    "14:60651": ["ERROR", "ALRT_DPE_FAULT_DRIVE_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may"
                 " have occurred because of a faulted disk. Identify and fix "
                 "the issue with the disk. If the problem persists, contact "
                 "your service provider."],
    "14:60652": ["ERROR", "ALRT_DPE_FAULT_POWERSUPPLY_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may"
                 " have occurred because of a faulted power supply. Identify"
                 " and fix the issue with the power supply. If the problem "
                 "persists, contact your service provider."],
    "14:60653": ["ERROR", "ALRT_DPE_FAULT_FAN_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may "
                 "have occurred because of a faulted cooling module. Identify"
                 " and fix the issue with the cooling module. If the problem"
                 " persists, contact your service provider."],
    "14:60654": ["ERROR", "ALRT_DPE_FAULT_SP_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may"
                 " have occurred because of a faulted SP. Identify and fix "
                 "the issue with the SP. If the problem persists, contact "
                 "your service provider."],
    "14:60655": ["ERROR", "ALRT_DPE_FAULT_IOPORT_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may"
                 " have occurred because of a faulted port. Identify and fix "
                 "the issue with the port. If the problem persists, contact"
                 " your service provider."],
    "14:60656": ["ERROR", "ALRT_DPE_FAULT_IOMODULE_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may"
                 " have occurred because of a faulted I/O module. Identify "
                 "and fix the issue with the I/O module. If the problem "
                 "persists, contact your service provider."],
    "14:60658": ["ERROR", "ALRT_DPE_FAULT_DIMM_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may "
                 "have occurred because of a faulted memory module. Identify"
                 " and fix the issue with the memory module. If the problem"
                 " persists, contact your service provider."],
    "14:60659": ["ERROR", "ALRT_DPE_NO_REASON_FAILURE",
                 "The DPE fault led is on but no specific fault is detected,"
                 " this could be a transient state. Please contact your "
                 "service provider if the issue persists."],
    "14:6065a": ["CRITICAL", "ALRT_DPE_FAULT_LCC_FAULT",
                 "The fault LED on the disk processor enclosure (DPE) is on."
                 " This may have occurred because of an issue with the Link "
                 "Control Card (LCC) cables connecting to the DPE. Replace "
                 "LCC cables to the enclosure first. If it does not solve the"
                 " problem, replace the LCC(s) in the enclosure."],
    "14:6065b": ["CRITICAL", "ALRT_DPE_FAULT",
                 "The Disk Processor Enclosure (DPE) has faulted. This may"
                 " have occurred because of a faulted internal component."
                 " Power cycle the enclosure first. If it does not solve the "
                 "problem, replace the enclosure."],
    "14:606a4": ["CRITICAL", "ALRT_MEMORY_FAULT",
                 "This memory module has faulted and needs to be replaced."],
    "14:606a5": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:606a6": ["ERROR", "ALRT_MEMORY_REMOVED",
                 "This memory module has been removed and needs to be "
                 "reinstalled."],
    "14:606a7": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:606a8": ["ERROR", "ALRT_MEMORY_INCORRECT_SPEED",
                 "This memory module speed is not correct for your storage "
                 "processor model and needs to be replaced."],
    "14:60708": ["WARNING", "ALRT_CACHE_DEGRADED",
                 "The cache protection module is operating in a degraded mode."
                 " Replace the failing component."],
    "14:60709": ["CRITICAL", "ALRT_CACHE_FAULT",
                 "The cache protection module has faulted and needs to be "
                 "replaced."],
    "14:6070a": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is"
                 " required."],
    "14:6070b": ["CRITICAL", "ALRT_CACHE_MISSING",
                 "The cache protection module has been removed and needs to"
                 " be reinstalled."],
    "14:6070c": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:6076c": ["ERROR", "ALRT_REPL_CONN_FAULT",
                 "The connection with this remote replication host has been "
                 "lost. On the Replication Connections page, click the Verify "
                 "and Update Connection button."],
    "14:6076d": ["INFO", "ALRT_REPL_CONN_OK",
                 "Communication with the replication host is established. "
                 "No action is required."],
    "14:6076e": ["WARNING", "ALRT_REPL_FAIL_OVR",
                 "This replication session has failed over."],
    "14:6076f": ["CRITICAL", "REPL_RECREATE",
                 "This replication session has encountered an error. Try"
                 " pausing, and then resuming the replication session. If"
                 " the problem persists, delete, and then create the "
                 "replication session again."],
    "14:60770": ["ERROR", "ALRT_REPL_CONN_FAULT",
                 "The connection with this remote replication host has been "
                 "lost. On the Replication Connections page, click the Verify"
                 " and Update Connection button."],
    "14:60771": ["INFO", "ALRT_REPL_OK",
                 "This replication session is operating normally. No action is"
                 " required."],
    "14:60772": ["WARNING", "ALRT_REPL_PAUSED",
                 "This replication session has been paused. Try resuming the "
                 "replication session. If the problem persists, delete, and "
                 "then create the replication session again."],
    "14:60773": ["WARNING", "ALRT_REPL_SWITCHED",
                 "This replication session has been switched over to the"
                 " destination site."],
    "14:60774": ["INFO", "ALRT_REPL_CONN_UPDATE",
                 "This replication connection is currently being updated."
                 " Please wait a few minutes for the connection to become "
                 "available again."],
    "14:60775": ["WARNING", "ALRT_REPL_UPDATE_NEEDED",
                 "The destination storage resource associated with this "
                 "replication session has multiple source storage resources"
                 " replicating to it. This may cause inconsistencies when "
                 "setting up replication for new LUNs. Delete replication "
                 "sessions from all but one of the source storage resources "
                 "to this destination."],
    "14:60777": ["CRITICAL", "ALRT_REPL_GP_INCONSISTENT_MAP",
                 "Member file systems of the source NAS server are replicating"
                 " to file systems outside the destination NAS server."],
    "14:60778": ["CRITICAL", "ALRT_REPL_PARENT_NOT_REPL",
                 "The member file system is replicating, but the parent NAS"
                 " server cannot replicate."],
    "14:60779": ["INFO", "ALRT_REPL_REMOTESYS_UP_TO_DATE",
                 "Update the remote system connection to pick up the latest"
                 " interface changes on the local and remote systems."],
    "14:6077a": ["CRITICAL", "ALRT_REPL_MEM_STATE_MISMATCH",
                 "The replication sessions for member file systems of a parent"
                 " NAS server are not in same state."],
    "14:6077b": ["CRITICAL", "ALRT_REPL_PARENT_STATE_MISMATCH",
                 "The parent NAS server replication session is not in the same"
                 " state as the member file system replication session."],
    "14:6077c": ["ERROR", "ALRT_REPL_NTWKCONN",
                 "One or more replication interface pairs are experiencing "
                 "network connectivity issues between the local and remote "
                 "systems."],
    "14:6077f": ["WARNING", "ALRT_REPL_DEST_POOL_FULL",
                 "The replication session is operating in a degraded state "
                 "because the storage pool on the destination system has run "
                 "out of space. Expand the pool to restore normal operation."],
    "14:60780": ["ERROR", "ALRT_REPL_NO_IO_CONN",
                 "An Import connection between the local system and the remote"
                 " VNX system has not been created. Create an Import"
                 " connection between the remote VNX system and the local"
                 " system."],
    "14:60781": ["CRITICAL", "ALRT_NOT_ALL_REP_SESSION_FAILOVER",
                 "At least one member of a consistency group is not in the "
                 "Failed Over state. Check the Audit log for the replication"
                 " failure reason, and reattempt a Failover."],
    "14:60782": ["CRITICAL", "ALRT_NOT_ALL_REP_SESSION_FAILOVER_SYNC",
                 "At least one member of a consistency group is not in the"
                 " Failed Over with Sync state. Check the Audit log for the"
                 " replication failure reason, and reattempt a Failover with"
                 " Sync."],
    "14:607d0": ["INFO", "ALRT_SED_KEY_GEN",
                 "An authentication key has been generated and is valid for"
                 " the self-encrypting drive system. Please back up the key "
                 "immediately to an external device in case the key becomes "
                 "corrupted or lost."],
    "14:607d1": ["ERROR", "ALRT_SED_KEY_RESTORE",
                 "The authentication key is invalid and is not available for"
                 " backup to an external device. This may prevent access to "
                 "stored data. Please put the system in Service Mode, and run"
                 " the svc_key_restore service script to restore the"
                 " authentication key."],
    "14:607d2": ["INFO", "ALRT_SED_KEY_NO_KEY",
                 "The authentication key is not present and is not available"
                 " for backup to an external device. The key will be generated"
                 " and available for backup after the first storage pool has"
                 " been created."],
    "14:60898": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60899": ["CRITICAL", "ALRT_HOST_CONTAINER_ERROR",
                 "The system cannot connect to the virtual service because of"
                 " an internal error. Retry the operation. If the problem "
                 "persists, contact your service provider."],
    "14:6089a": ["CRITICAL", "ALRT_HOST_CONTAINER_CONNECTION_FAILURE",
                 "The system failed to connect to the virtual service. Retry"
                 " the operation. If the problem persists, contact your"
                 " service provider."],
    "14:6089b": ["CRITICAL", "ALRT_HOST_CONTAINER_LOGIN_FAILURE",
                 "The system cannot connect to the virtual service. Check the"
                 " credentials used to access the virtual service."],
    "14:6089c": ["CRITICAL", "ALRT_HOST_CONTAINTER_CERTIFICATE_FAILURE",
                 "The certificate to access virtual service is invalid. Check"
                 " and update the certificate used to access the virtual"
                 " service."],
    "14:6089d": ["INFO", "ALRT_HOST_CONTAINER_UNKNOWN",
                 "The system is unable to refresh the host container because "
                 "of an unknown issue. Wait to see if the problem resolves "
                 "itself. If the problem persists, contact your service"
                 " provider."],
    "14:608fc": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:608fd": ["WARNING", "ALRT_HOST_INITIATORS_NO_HA",
                 "The host only has one path to the storage system. Add"
                 " multiple paths between host and storage systems to "
                 "establish redundancy."],
    "14:608fe": ["WARNING", "ALRT_HOST_NO_LOGGED_IN_INITIATORS",
                 "The host does not have any initiators logged into the"
                 " storage system. Register one or more initiators on the "
                 "host to the storage system. This may also require zoning "
                 "changes on the switches."],
    "14:608ff": ["CRITICAL", "ALRT_HOST_CONFLICTING_IP",
                 "Host has one or more IP addresses that are associated with "
                 "other hosts. Resolve the conflicts by assigning the IP "
                 "address to only one host."],
    "14:60900": ["CRITICAL", "ALRT_HOST_CONFLICTING_INITIATOR",
                 "Host has one or more initiators that are associated with "
                 "other hosts. Resolve the conflicts by assigning the "
                 "initiators to only one host."],
    "14:60901": ["CRITICAL", "ALRT_HOST_ERROR",
                 "An internal issue has occurred. Retry the operation. If the"
                 " problem persists, contact your service provider."],
    "14:60902": ["CRITICAL", "ALRT_HOST_CONNECTION_FAILURE",
                 "Failed to connect to host. Please check your network "
                 "connection."],
    "14:60903": ["CRITICAL", "ALRT_HOST_LOGIN_FAILURE",
                 "The system cannot log on to the host. Check the credentials"
                 " used to access the host."],
    "14:60904": ["CRITICAL", "ALRT_HOST_CERTIFICATE_FAILURE",
                 "The certificate to access the host is invalid. Check the"
                 " certificate used to access host."],
    "14:60905": ["CRITICAL", "ALRT_HOST_DUPLICATE_UUID",
                 "Multiple hosts are using the same UUID. Change or remove"
                 " the duplicate host UUID that is in conflict with "
                 "this host."],
    "14:60906": ["INFO", "ALRT_HOST_UNKNOWN",
                 "The system is unable to refresh a managed server because"
                 " of an unknown issue."],
    "14:60960": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is"
                 " required."],
    "14:60961": ["WARNING", "ALRT_INITIATOR_NO_LOGGED_IN_PATH",
                 "The initiator does not have any logged in initiator paths."
                 " Check the connection between the initiator and the storage"
                 " system."],
    "14:60962": ["WARNING", "ALRT_INITIATOR_NOT_ASSOC_WITH_HOST",
                 "The initiator is not associated with any host. Register the"
                 " initiator with a known storage system."],
    "14:60963": ["CRITICAL", "ALRT_INITIATOR_CONFLICTING_HOST_UUID",
                 "The initiator is registered with more than one host. Resolve"
                 " the conflicts by assigning the initiators to only "
                 "one host."],
    "14:609c4": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:609c5": ["INFO", "ALRT_PORT_LINK_UP",
                 "The port is operating normally."],
    "14:609c6": ["WARNING", "ALRT_FCPORT_DEGRADED",
                 "Performance of a Fibre Channel (FC) port on one of the I/O"
                 " modules has degraded. Identify the port, check the cabling,"
                 " and network configuration. If the problem persists, you"
                 " may need to replace the I/O module."],
    "14:609c7": ["CRITICAL", "ALRT_FCPORT_UNINITIALIZED",
                 "A Fibre Channel (FC) port on one of the I/O modules not"
                 " initialized. Identify the port, check the cabling, and"
                 " network configuration. If the problem persists, you may "
                 "need to replace the I/O module."],
    "14:609c8": ["INFO", "ALRT_FCPORT_EMPTY",
                 "The Disk Processor Enclosure (DPE) contains a vacant Fibre"
                 " Channel (FC) port."],
    "14:609c9": ["WARNING", "ALRT_FCPORT_MISSING",
                 "The system is unable to detect a Fibre Channel (FC) port on"
                 " one of the I/O modules. Check system logs and reboot the "
                 "I/O module. If the problem persists, you may need to replace"
                 " the I/O module."],
    "14:609ca": ["CRITICAL", "ALRT_FCPORT_FAULT",
                 "A Fibre Channel (FC) port has faulted. Check system log for"
                 " hardware errors or warnings. If the problem persists, you "
                 "may need to replace the I/O module."],
    "14:609cc": ["WARNING", "ALRT_FCPORT_SFP_REMOVED",
                 "The Small Form-factor Pluggable (SFP) module in this Fibre"
                 " Channel (FC) port has been removed. Since the port is in "
                 "use, reinsert a supported SFP module."],
    "14:609cd": ["INFO", "ALRT_FCPORT_SFP_REMOVED_NOT_IN_USE",
                 "The Small Form-factor Pluggable (SFP) module in this Fibre"
                 " Channel (FC) port has been removed. Since the port is not"
                 " in use, no action is required."],
    "14:609cf": ["ERROR", "ALRT_FCPORT_LINKDOWN",
                 "The Fibre Channel (FC) port has lost communication with the"
                 " network."],
    "14:609d0": ["INFO", "ALRT_PORT_LINK_DOWN_NOT_IN_USE",
                 "The port link is down, but not in use. No action is "
                 "required."],
    "14:609d1": ["CRITICAL", "ALRT_FCPORT_SFP_UNSUPPORT",
                 "The Small Form-factor Pluggable (SFP) module inserted in "
                 "this Fibre Channel (FC) port is not supported. Replace it "
                 "with a supported SFP module."],
    "14:609d2": ["CRITICAL", "ALRT_FCPORT_SFP_FAULT",
                 "The Small Form-factor Pluggable (SFP) module in this Fibre"
                 " Channel (FC) port has faulted and needs to be replaced."],
    "14:609d3": ["ERROR", "ALRT_FCPORT_OVERLIMIT",
                 "This Fibre Channel (FC) port cannot be used because it "
                 "exceeds the number of supported ports. Remove the I/O "
                 "module that contains this port."],
    "14:609d4": ["CRITICAL", "ALRT_FCPORT_INCORRECTSLIC",
                 "An incorrect type of I/O module has been inserted. The "
                 "system cannot support the Fibre Channel (FC) port "
                 "configuration for this port. Replace the I/O module."],
    "14:609d5": ["INFO", "ALRT_FCPORT_SFP_ASYMMETRIC",
                 "The SFPs in the Storage Processor(SP) are configured "
                 "incorrectly. Its supported speeds is asymmetric with its "
                 "peer's."],
    "14:60a28": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60a29": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this"
                 " time. This may be an intermittent problem. Please wait to"
                 " see if the problem resolves itself."],
    "14:60a2d": ["WARNING", "ALRT_FASTCACHE_DEGRADED",
                 "FAST Cache performance is degraded because it has one or"
                 " more disks with problems. Replace the faulted disks."],
    "14:60a2e": ["CRITICAL", "ALRT_FASTCACHE_FAULT",
                 "FAST Cache is offline because it has two or more disks "
                 "with problems. Contact your service provider."],
    "14:60a33": ["INFO", "ALRT_FASTCACHE_DISK_EOL_WARNING",
                 "FAST Cache has one or more drives predicted to wear out in"
                 " less than 180 days. The storage system will automatically "
                 "replace the affected drives with no data loss when they "
                 "reach end-of-life."],
    "14:60a34": ["INFO", "ALRT_FASTCACHE_DISK_EOL_WARNING_RANGE",
                 "FAST Cache has one or more drives predicted to wear out in"
                 " less than 180 days. The storage system will automatically "
                 "replace the affected drives with no data loss when they "
                 "reach end-of-life."],
    "14:60a35": ["INFO", "ALRT_FASTCACHE_DISK_EOL_SEVERE",
                 "FAST Cache has one or more drives predicted to wear out in "
                 "less than 90 days. The storage system will automatically"
                 " replace the affected drives with no data loss when they "
                 "reach end-of-life."],
    "14:60a36": ["INFO", "ALRT_FASTCACHE_DISK_EOL_SEVERE_RANGE",
                 "FAST Cache has one or more drives predicted to wear out in "
                 "less than 90 days. The storage system will automatically "
                 "replace the affected drives with no data loss when they "
                 "reach end-of-life."],
    "14:60a37": ["WARNING", "ALRT_FASTCACHE_DISK_EOL_CRITICAL",
                 "FAST Cache has drives predicted to wear out in less than "
                 "30 days. If there are spare drives available, the storage"
                 " system will automatically replace the affected drives with "
                 "no data loss when they reach end- of-life."],
    "14:60a38": ["WARNING", "ALRT_FASTCACHE_DISK_EOL_CRITICAL_RANGE",
                 "FAST Cache has drives predicted to wear out in less than 30"
                 " days. If there are spare drives available, the storage "
                 "system will automatically replace the affected drives with "
                 "no data loss when they reach end- of-life."],
    "14:60a39": ["CRITICAL", "ALRT_FASTCACHE_DISK_PACO_START_FAIL_NO_SPARE",
                 "The system could not start an automatic copy of data from "
                 "one or more drives in FAST Cache to replace a drive that is"
                 " wearing out, because spare drives are not available. Add"
                 " drives to the FAST Cache."],
    "14:60a3a": ["CRITICAL", "ALRT_FASTCACHE_DRIVE_EOL_AUTO_PACO_FAILED",
                 "The system could not start an automatic copy of data from"
                 " one or more drives in FAST Cache to replace drives that"
                 " are wearing out, even though there are spare drives"
                 " available. Please contact your service provider."],
    "14:60a3b": ["WARNING", "ALRT_FASTCACHE_DRIVE_EOL_IN_60_DAYS",
                 "The FAST Cache has Flash drives of a specific type that are"
                 " predicted to exceed end-of-life thresholds within 60 days."
                 " The storage system does not have enough free drives of the"
                 " same type to replace them. Add drives to the FAST Cache."],
    "14:60bb8": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60bb9": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60bba": ["WARNING", "ALRT_POOL_ALLOC_SYSTEM_THRESHOLD",
                 "Storage resource allocation from one of the pools has "
                 "exceed the 85% threshold. Allocate more storage space "
                 "from the pool to the storage resource."],
    "14:60bbb": ["WARNING", "ALRT_POOL_ALLOC_CRITICAL_THRESHOLD",
                 "Storage resource allocation from one of the pools has exceed"
                 " the 95% threshold. Allocate more storage space from the "
                 "pool to the storage resource."],
    "14:60bbc": ["ERROR", "ALRT_POOL_ALLOC_CRITICAL_THRESHOLD_OVERSUBSCRIBE",
                 "Storage resource allocation from one of the pools has"
                 " exceed the 95% threshold, and the storage resource is "
                 "oversubscribed. Allocate more storage space from the pool "
                 "to the storage resource."],
    "14:60c1c": ["INFO", "ALRT_COMPONENT_OK",
                 "The component is operating normally. No action is "
                 "required."],
    "14:60c1d": ["INFO", "ALRT_UNKNOWN",
                 "The health of the component cannot be determined at this "
                 "time. This may be an intermittent problem. Please wait to "
                 "see if the problem resolves itself."],
    "14:60c1e": ["ERROR", "ALRT_SSC_REMOVED",
                 "The system status card (SSC) has been removed and needs to"
                 " be installed again. Removing the SSC may result in faults "
                 "or removal of other components in this enclosure."],
    "14:60c1f": ["CRITICAL", "ALRT_SSC_FAULT",
                 "The system status card has faulted and needs to be "
                 "replaced."],
    "14:60c80": ["INFO", "ALRT_UNCOMMITTEDPORT_UNINITIALIZED",
                 "The uncommitted port has not been initialized. It needs to"
                 " be committed before it can be used."],
    "14:60c81": ["INFO", "ALRT_UNCOMMITTEDPORT_SFP_REMOVED",
                 "The Small Form-factor Pluggable (SFP) module in this "
                 "uncommitted port has been removed. Since the port is not"
                 " in use, no action is required."],
    "14:60c82": ["WARNING", "ALRT_UNCOMMITTEDPORT_SFP_UNSUPPORT",
                 "The Small Form-factor Pluggable (SFP) module inserted in"
                 " this uncommitted port is not supported. Replace it with a"
                 " supported SFP module."],
    "14:60c83": ["ERROR", "ALRT_UNCOMMITTEDPORT_SFP_FAULT",
                 "The Small Form-factor Pluggable (SFP) module in this "
                 "uncommitted port has faulted and needs to be replaced."],
    "14:60ce4": ["WARNING", "ALRT_BACKINGSTORE_ONE_CONNECTION",
                 "Only one SP of backing store is connected."],
    "14:60ce5": ["CRITICAL", "ALRT_BACKINGSTORE_CONNECTION_LOST",
                 "The system has lost connection to the backing store. "
                 "Contact your service provider."],
    "14:60ce6": ["INFO", "ALRT_BACKINGSTORE_BAD_CONNECTION",
                 "The backing store has faulty connections. Contact your "
                 "service provider."],
    "14:60ce7": ["INFO", "ALRT_BACKINGSTORE_OK",
                 "The backing store is operating normally."],
    "14:60ce8": ["INFO", "ALRT_BACKINGSTORE_UNKNOWN",
                 "The health of the backing store cannot be determined. "
                 "Contact your service provider."],
    "14:60d48": ["INFO", "ALRT_VMWARE_PE_OK",
                 "The protocol endpoint is operating normally. No action is"
                 " required."],
    "14:60d49": ["INFO", "ALRT_VMWARE_PE_UNKNOWN",
                 "The health of the protocol endpoint cannot be determined "
                 "at this time."],
    "14:60d4a": ["WARNING", "ALRT_VMWARE_PE_DEGRADED",
                 "There are issues detected on the protocol endpoint for the"
                 " virtual volume and it is degraded."],
    "14:60d4b": ["CRITICAL", "ALRT_VMWARE_PE_OFFLINE",
                 "The NAS protocol endpoint is offline. This may be caused by "
                 "the NAS server being offline."],
    "14:60d4c": ["CRITICAL", "ALRT_VMWARE_PE_FAILURE",
                 "The VMware Protocol Endpoint is offline. This can be caused "
                 "by host access configuration failure."],
    "14:60dac": ["INFO", "ALRT_MIGRATION_SESSION_OK",
                 "The import session is operating normally."],
    "14:60dad": ["CRITICAL",
                 "ALRT_MIGRATION_SESSION_FAILED_CONNECTION_FAILURE",
                 "The import session failed to import data in initial/"
                 "incremental copy due to connection failure. Check the import"
                 " connection between source and destination manually. After "
                 "connection recovery, import will restart automatically. If "
                 "the error persists, cancel the import session."],
    "14:60dae": ["ERROR", "ALART_MIGRATION_SESSION_COMMIT_FAILED",
                 "The import session failed to commit. Commit the import "
                 "session again."],
    "14:60daf": ["ERROR", "ALRT_MIGRATION_SESSION_START_FAILED",
                 "The import session failed to provision the target resource. "
                 "It may have failed during one of these steps: 'Validate "
                 "before starting import', 'Create target NAS server','Create"
                 " target file system(s)','Dump source file system quota(s)'"
                 " or 'Add source export entries'. Check job and task status "
                 "to get error details. After the error is fixed, resume the "
                 "import session. If the error persists, cancel the import"
                 " session."],
    "14:60db0": ["CRITICAL",
                 "ALRT_MIGRATION_SESSION_FAILED_PAUSED_TARGET_IO_FAILURE",
                 "The import session failed and paused importing data during "
                 "initial/incremental copy due to target IO failure."],
    "14:60db1": ["CRITICAL", "ALRT_MIGRATION_SESSION_FAILED_UNRECOVERABLE",
                 "The import session failed due to unrecoverable failure. "
                 "Cancel the import for data integrity consideration."],
    "14:60db2": ["CRITICAL",
                 "ALRT_MIGRATION_SESSION_FAILED_PAUSED_SOURCE_IO_FAILURE",
                 "The import session failed and paused importing data during "
                 "initial/incremental copy due to source IO failure."],
    "14:60db3": ["ERROR", "ALRT_MIGRATION_SESSION_CONFIGURATION_FAILED",
                 "The import session has configuration failure. Resume the "
                 "import session. If the error persists, cancel the import"
                 " session."],
    "14:60db4": ["CRITICAL", "ALRT_MIGRATION_SESSION_CUTOVER_FAILED",
                 "The import session failed to cutover. Check and fix the "
                 "error reported in related job; otherwise, cancel the "
                 "import."],
    "14:60db5": ["CRITICAL", "ALRT_MIGRATION_SESSION_FAILED_SOURCE_IO_FAILURE",
                 "The import session failed importing data during initial/"
                 "incremental copy due to source IO failure."],
    "14:60db6": ["CRITICAL", "ALRT_MIGRATION_SESSION_FAILED_TARGET_IO_FAILURE",
                 "The import session failed importing data during initial/"
                 "incremental copy due to target IO failure"],
    "14:60db7": ["CRITICAL",
                 "ALRT_MIGRATION_SESSION_FAILED_PAUSED_CONNECTION_FAILURE",
                 "The import session failed and paused importing data during"
                 " initial/incremental copy due to connection failure. Check "
                 "the import connection between source and destination "
                 "manually. After connection recovery, import will restart "
                 "automatically. If the error persists, cancel the import "
                 "session."],
    "14:60db8": ["CRITICAL", "ALRT_MIGRATION_SESSION_CANCELLING_FAILED",
                 "The import session failed to cancel. Cancel the import for "
                 "data integrity consideration."],
    "14:60dba": ["NOTICE", "ALRT_MIGRATION_SESSION_PAUSED",
                 "The import session is paused. Resume the import session."],
    "14:60dbb": ["ERROR", "ALRT_MIGRATION_SESSION_FAULTED",
                 "The import session is faulted. Cancel the import session."],
    "14:60dbc": ["ERROR", "ALRT_MIGRATION_SESSION_OFFLINE",
                 "The import session is offline. Cancel the import session."],
    "14:60dbd": ["CRITICAL", "ALRT_MIGRATION_SESSION_FAILED_NON_RECOVERABLE",
                 "The import session failed due to a non- recoverable error."
                 " Go to session properties dialog to check health details"
                 " and resolution steps in GUI or use UECMCLI command ¡°"
                 "import/session/elem ent show -detail¡± to check session "
                 "health details and resolution steps."],
    "14:60e10": ["INFO", "ALRT_MOVE_SESSION_OK",
                 "The specified storage resource move session is operating"
                 " normally."],
    "14:60e11": ["INFO", "ALRT_MOVE_SESSION_UNKNOWN",
                 "The health of storage resource move session cannot be"
                 " determined."],
    "14:60e12": ["ERROR", "ALRT_MOVE_SESSION_FAILED",
                 "The specified storage resource move session has failed. "
                 "Contact your service provider."],
    "14:60e13": ["ERROR", "ALRT_MOVE_SESSION_STOP_POOL_OFFLINE",
                 "The pool went offline and the specified storage resource "
                 "move session cannot continue. Contact your service "
                 "provider."],
    "14:60e14": ["ERROR", "ALRT_MOVE_SESSION_STOP_NO_SPACE",
                 "The pool exhausted the space available and the specified "
                 "storage resource move session cannot continue. Remove the"
                 " move session, free up space on the destination pool, and "
                 "restart the move session."],
    "14:60e15": ["ERROR", "ALRT_MOVE_SESSION_INTERNAL_ERR",
                 "The specified storage resource move session encountered an "
                 "internal error. Contact your service provider."],
    "14:60e74": ["INFO", "ALRT_ELEMENT_IMPORT_SESSION_OK",
                 "The element import session is operating normally."],
    "14:60e75": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_NONRECOVERABLE",
                 "The import session failed due to a non- recoverable failure."
                 " Cancel the import session and determine the integrity of "
                 "the data."],
    "14:60e76": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_UNABLE_TO_LOCATE_DEVICE",
                 "Element import session related to a Sancopy session ran into"
                 " error, 0x712AC007, Unable to locate the device. Check that "
                 "the device with this WWN exists. (WWN). This can be due to"
                 " FC zoning or iSCSI connection configuration between the VNX"
                 " and Unity systems. Follow documentation to configure "
                 "connectivity between all SP pairs between the VNX and Unity "
                 "systems. Once the FC/iSCSI connection configuration is "
                 "validated, run the Verify and Update operation for the "
                 "remote system connection to VNX. This will discover/update"
                 " all."],
    "14:60e77": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_"
                 "BAD_BLOCK_ON_SOURCE_DEVICE",
                 "Element import session related to a Sancopy session ran "
                 "into error: 0x712AC015: A bad block was encountered on the"
                 " source device. (WWN). This is a non- recoverable error."
                 " Cancel the session. The resource cannot be imported."],
    "14:60e78": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_UNABLE_TO_ACCESS_DEVICE",
                 "Unable to access the device. (WWN). Check cables and FC"
                 " zoning or iSCSI connection configuration between the VNX "
                 "and Unity systems. Ensure connectivity between all SP pairs"
                 " between the VNX and Unity systems. Once the FC/iSCSI "
                 "connection configuration is validated, run the Verify and "
                 "Update operation for the remote system connection to the "
                 "VNX, which will discover/update all configuration changes."
                 " Run the Resume operation on the import session to recover "
                 "the session from the error state."],
    "14:60e79": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LU_TRESPASSED",
                 "This LUN will need to be manually trespassed over to the SP"
                 " that started the session. (WWN). This is due to LUN "
                 "trespassed state. To resolve this issue, tresspass over the "
                 "LUN to the same SP on which the SAN Copy session was "
                 "created . Once resolved, log in to the Unity system and run"
                 " the Resume operation for this import session to recover"
                 " from the error."],
    "14:60e7a": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_SOURCE_DEVICE_"
                 "INACCESSIBLE",
                 "Transfer failed because the source device is inaccessible"
                 " from the peer SP. This is probably due to incorrect "
                 "FC zoning on the switch or the device is not configured "
                 "in the correct storage group. (WWN). Configure connectivity"
                 " between all SP pairs between the VNX and Unity systems."
                 " Once the FC or iSCSI connection configuration is validated,"
                 " run Verify and Update operation for the Remote System"
                 " connection to the VNX to discover/update all configuration"
                 " changes; then, run Resume operation on the import "
                 "session."],
    "14:60e7b": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LOW_USER_LINK_BANDWIDTH",
                 "The User Link Bandwidth must be >= 16 kilobits. The error "
                 "occurred due to bandwidth setting changes made through the "
                 "VNX UI. Reset the link bandwidth to the default value."],
    "14:60e7c": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_CONCURRENT_SANCOPY_"
                 "SESSION_DESTINATIONS",
                 "The command failed because one or more failed destinations"
                 " exist on this SAN Copy Session due to concurrent sancopy"
                 " sync to different targets. Do not add any new targets to"
                 " the SAN Copy session created by the Unity system. Remove"
                 " any non-Unity targets added to the SAN Copy session to "
                 "recover from the error."],
    "14:60e7d": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_COMMUNICATING_WITH"
                 "_SNAPVIEW",
                 "A non-recoverable error occurred: An error occured "
                 "communicating with SnapView."],
    "14:60e7e": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_INCONSISTENT_STATE",
                 "The session has completed successfully but is in an "
                 "inconsistent state."],
    "14:60e7f": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_DESTINATION_IN_"
                 "INCONSISTENT_STATE",
                 "A non-recoverable error occurred: The session has completed"
                 " successfully but is in an inconsistent state."],
    "14:60e80": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_RESUME_ON_AUTO_RECOVERY",
                 "A non-recoverable error occurred: Resume of copy session %2"
                 " failed on auto-recovery."],
    "14:60e81": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_DUE_TO_ALL_PATHS_FAILURE",
                 "A non-recoverable error occurred: Copy session %2 failed due"
                 " to all paths failure on device with WWN %3."],
    "14:60e82": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_ACCESS_DENIED_TO_DEVICE",
                 "A non-recoverable error occurred: Access denied to the "
                 "device. (WWN)."],
    "14:60e83": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_NOT_ENOUGH_MEMORY",
                 "A non-recoverable error occurred: Not enough memory "
                 "resources exist to complete the request."],
    "14:60e84": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_SOURCE_DEVICE_FAILED",
                 "The source device specified in the session failed. (WWN). "
                 "This can be due to either a Raidgroup or Storage Pool being"
                 " offline or corruption on source LUN on VNX. Verify that the"
                 " source LUN is in a good state. Once the resource is in a"
                 " good state, run Resume of session from Unity UI."],
    "14:60e85": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_DESTINATION_DEVICE"
                 "_FAILED",
                 "The following target device specified in the session failed."
                 " (WWN). This can be due to the storage pool being offline or"
                 " corruption of the target LUN. Verify that the target LUN is"
                 " in a good state. Once the resource is in a good state, run"
                 " Resume operation of session from Unity UI."],
    "14:60e86": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_DESTINATION_DEVICE_NOT_"
                 "FOUND",
                 "The destination device could not be found due to either"
                 " incorrect zoning on the switch or the device is not in the "
                 "correct storage group. (WWN). This can be due to FC Zoning "
                 "or iSCSI Connection configuration between VNX and Unity "
                 "arrays. Configure connectivity between all SP pairs between"
                 " the VNX and Unity systems. Once the FC or iSCSI connection"
                 " configuration is validated, run the Verify and Update "
                 "operation for the Remote System connection to the VNX to "
                 "discover/update all."],
    "14:60e87": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_TARGET_LU_NOT_"
                 "INITIALIZED",
                 "A non-recoverable error occurred: Target LUN list has not"
                 " been initialized yet."],
    "14:60e88": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_COMMAND_TIMED_OUT",
                 "A non-recoverable error occurred: The command timed out "
                 "waiting on another SAN Copy operation to complete."],
    "14:60e89": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_VERIFYING_FRONT_END_"
                 "DEVICE_TIMEDOUT",
                 "A non-recoverable error occurred: Verifying front end devic"
                 "e timed out."],
    "14:60e8a": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_VERIFYING_FRONT_END_"
                 "DEVICE_TIMEDOUT_ANOTHER_OPERATION",
                 "A non-recoverable error occurred: Verifying front end device"
                 " timed out waiting for another front end operation to "
                 "complete."],
    "14:60e8b": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_VERIFYING_SOURCE_"
                 "CONNECTIVITY_TIMEDOUT",
                 "A non-recoverable error occurred: Operation timed out "
                 "trying to verify the connectivity to the source device."],
    "14:60e8c": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_VERIFYING_DESTINATION"
                 "_CONNECTIVITY_TIMEDOUT",
                 "A non-recoverable error occurred: Operation timed out "
                 "trying to verify the connectivity to the target device."],
    "14:60e8d": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_RLP_LUN_IO_FAILURE",
                 "A non-recoverable error occurred: Operation failed due to "
                 "an unrecoverable I/O failure of a reserved LUN."],
    "14:60e8e": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LIMIT_OF_TOTAL_"
                 "SESSIONS_FOR_SANCOPYE_REACHED",
                 "A non-recoverable error occurred: This copy session could "
                 "not be created because the limit of total sessions for "
                 "SAN Copy/E has been reached."],
    "14:60e8f": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LIMIT_OF_INCREMENTAL"
                 "_SESSIONS_FOR_SANCOPYE_REACHED",
                 "This copy session could not be created because the limit "
                 "of incremental sessions for SAN Copy/E has been reached. "
                 "Resolve the limit issue by deleting an existing incremental "
                 "session related to systems other than the Unity system or "
                 "remove some MirrorView/A sessions from the system. Once the"
                 " limit issue is resolved, run the resume operation on teh "
                 "import session from the Unity system."],
    "14:60e90": ["INFO",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_COPY_COMMAND_QUEUED",
                 "Copy command is queued due to SAN Copy concurrent sync "
                 "limits interference from a VNX admininstrator scheduled"
                 " start and the Unity scheduled start. Stop or abort any SAN"
                 " Copy starts issued on VNX systems on imports happening to"
                 " non- Unity systems."],
    "14:60e91": ["INFO",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_ON_SOURCE_OR"
                 "_DESTINATIONS",
                 "The session failed because either the source or all targets"
                 " have failed due to failure status on the source or target"
                 " device of the SAN Copy session. Log in to the VNX system "
                 "and resolve the SAN Copy error reported for this element "
                 "session and resume the SAN Copy session from the VNX UI."],
    "14:60e92": ["INFO",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_DEVICE_CANNOT_BE_LOCATED",
                 "Element import session related Sancopy session ran into "
                 "error: 0x712A0030: Unable to locate the device. Check that "
                 "the device with this WWN exists Session ran into an non- "
                 "recoverable error. Please collect support materials from "
                 "both VNX and Unity system. Report an issue with EMC Support"
                 " for resolution. Please cancel the session."],
    "14:60e93": ["WARNING",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_NO_UNUSED_RLP_LUNS",
                 "There are no unused LUNs available in the reserved LUN pool"
                 " (RPL) for session create or start. Add LUNs to the RLP"
                 " pool, then resume the import session operation."],
    "14:60e94": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_RLP_LUN_NOT_SUPPORT_"
                 "INCREMENTAL_SESSIONS",
                 "A non-recoverable error occurred: Existing reserved LUN does"
                 " not support incremental sessions"],
    "14:60e95": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_SNAPVIEW_RESERVED_"
                 "LUN_NOT_ENOUGH_SPACE",
                 "A non-recoverable error occurred: A SnapView reserved LUN "
                 "did not have sufficient space for the minimum map regions."],
    "14:60e96": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_TOO_MANY_SNAPSHOTS_ON_"
                 "SINGLE_LU",
                 "A non-recoverable error occurred: Too many snapshots have"
                 " been created on a single source LUN."],
    "14:60e97": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_CANNOT_OPEN_RESERVED_LUN",
                 "A non-recoverable error occurred: The reserved LUN cannot"
                 " be opened."],
    "14:60e98": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_CANNOT_GET_RESERVED_"
                 "LUN_INFO",
                 "A non-recoverable error has occurred: Unable to get the "
                 "geometry information for reserved LUN."],
    "14:60e99": ["ERROR", "ALRT_ELEMENT_IMPORT_SESSION_FAILED_NO_SPACE_ON_RLP",
                 "No more room exists in the reserved LUN pool (RLP). An RLP"
                 " LUN or space is unavailable to create or start a session."
                 " Add LUNs to the RLP pool, then resume the operation."],
    "14:60e9a": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_TOTAL_NUMBER_SUPPORTED_"
                 "INCREMENTAL_SESSIONS_REACHED",
                 "This incremental copy session could not be created because "
                 "the maximum incremental SAN Copy sessions limit on the VNX"
                 " has been reached. The limit is shared with the MirrorView "
                 "Async feature. Resolve the limit issue by removing an"
                 " unwanted or unused SAN Copy session related to systems "
                 "other than the Unity system or remove some MirrorView/A "
                 "sessions from the system. Once the limit issue is resolved,"
                 " run the Resume operation on the import session from the "
                 "Unity system."],
    "14:60e9b": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LIMIT_OF_TOTAL_SANCOPY"
                 "_SESSIONS_REACHED",
                 "This incremental copy session could not be created because"
                 " the maximum incremental SAN Copy sessions limit on the"
                 " VNX has been reached. The limit is shared with the "
                 "MirrorView Async feature. Resolve the limit issue by"
                 " removing an unwanted or unused SAN Copy session related "
                 "to systems other than the Unity system or remove some "
                 "MirrorView/A sessions from the system. Once the limit "
                 "issue is resolved, run the Resume operation on the import "
                 "session from the Unity system."],
    "14:60e9c": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LIMIT_OF_TOTAL_I"
                 "NCREMENTAL_SANCOPY_SESSIONS_REACHED",
                 "This incremental copy session could not be created "
                 "because the maximum incremental SAN Copy sessions limit "
                 "on the VNX has been reached. The limit is shared with the "
                 "MirrorView Async feature. Resolve the limit issue by "
                 "removing an unwanted or unused SAN Copy session related to "
                 "systems other than the Unity system or remove some"
                 " MirrorView/A sessions from the system. Once the limit "
                 "issue is resolved, run the Resume operation on the import"
                 " session from the Unity system."],
    "14:60e9d": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_LOST_COMMUNICATION",
                 "Communication with the source array has been lost. On the "
                 "Remote System Connection page, click Verify and Update"
                 " Connection. If that does not correct the issue, verify "
                 "that the physical network is operational."],
    "14:60e9e": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_RLP_MAXIMUM_DEVICES",
                 "The reserved LUN pool (RLP) has its maximum number of "
                 "devices. An RLP LUN or space is unavailable to create or"
                 " start a session. Add LUNs to the RLP pool, then resume "
                 "the operation."],
    "14:60e9f": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_NO_CACHE_DEVICES",
                 "The user attempted to start a session without cache devices."
                 " A reserved LUN pool (RLP) LUN or space is unavailable to "
                 "create or start a session. Add LUNs to the RLP pool, then "
                 "resume the operation."],
    "14:60ea0": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_TARGET_"
                 "INSUFFICIENT_SPACE",
                 "Failed to write to target device due to insufficient "
                 "storage space, which can be caused by a pool out of space or"
                 " target device error state on the Unity system. Verify the "
                 "condition of the target device, or pool, or both. Add or"
                 " free storage space in the pool, or correct the resource "
                 "state, or both and then resume the operation."],
    "14:60ea1": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_DEVICE_NOT_READY",
                 "Element import session related to a SAN Copy session failed"
                 " because the device is not ready. One cause can be a reboot"
                 " of the VNX system, which would cause the SAN Copy session"
                 " to go to the paused state. Resolve the VNX reboot issue "
                 "and verify that the source LUN or LUNs are completly "
                 "recovered. Then from the Unity console, run the Resume "
                 "operation on the import session to recover."],
    "14:60ea2": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_COMMUNICATING_WITH_"
                 "SNAPVIEW_1",
                 "A non-recoverable error occurred: An error occured "
                 "communicating with SnapView."],
    "14:60ea3": ["CRITICAL",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_SOURCE_DEVICE"
                 "_UNAVAILABLE",
                 "Element import session related Sancopy session failed "
                 "because the source device is unavailable for IO operations."
                 " Ensure that the device is not a MirrorView secondary image,"
                 " a SnapView Clone, an inactive Snapshot, or a detached or"
                 " offline VNX Snapshot Mount Point. If the session still"
                 " fails, gather SPcollects and contact your service "
                 "provider."],
    "14:60ea4": ["WARNING", "ALRT_IMPORT_REMOTE_SYSTEM_DEGRADED",
                 "Connection to one of the remote VNX system management "
                 "IP addresses cannot be made. Check and restore connectivity "
                 "to both management IP addresses on the VNX system."],
    "14:60ea5": ["ERROR",
                 "ALRT_ELEMENT_IMPORT_SESSION_FAILED_SOURCE_IN_IMPORT_SESSION",
                 "The import session could not be created because the source"
                 " resource is already in import session. Resolve the issue"
                 " by removing the SAN Copy session for this resource on the"
                 " VNX. Once the issue is resolved, wait for few minutes and"
                 " run the Resume operation on the import session from the"
                 " Unity system."],
    "14:60f00": ["INFO", "ALRT_ROUTE_OK",
                 "The component is operating normally."],
    "14:60f01": ["ERROR", "ALRT_ROUTE_INVALID_IP_VERSION",
                 "There is an IPv4/IPv6 mismatch between the network route's"
                 " destination and/or gateway, and the source IP interface."
                 " Edit the destination and/or gateway attributes of the"
                 " route."],
    "14:60f02": ["ERROR", "ALRT_ROUTE_SRC_IP_NOT_FOUND",
                 "The source IP interface of the network route does not "
                 "exist."],
    "14:60f03": ["ERROR", "ALRT_ROUTE_DIFF_SUBNET",
                 "The gateway of the network route is inaccessible, because it"
                 " is not on the same subnet as the source interface. Modify"
                 " the attributes of the network route or source Interface to "
                 "associate them with the same subnet."],
    "14:60f04": ["ERROR", "ALRT_ROUTE_NOT_OPERATIONAL",
                 "The network route is not operational. Delete the route and"
                 " create a new one, if necessary."],
    "14:61008c": ["NOTICE",
                  "ALRT_MIGRATION_SESSION_CUTOVER_THRESHOLD_PERCENTAGE"
                  "_REMAINING",
                  "Import session reached cutover threshold and is cutover "
                  "ready."],
    "14:62001f": ["WARNING", "ALRT_QOS_MAX_PERF_CLASSES",
                  "Maximum number of I/O limit resources has been reached."],
    "14:640001": ["CRITICAL", "ALRT_UDOCTOR_FAIL_TO_START",
                  "An error has occurred that is preventing the UDoctor "
                  "service from starting up. Contact your service provider."],
    "14:640002": ["ERROR", "ALRT_UDOCTOR_GENERAL_ALERT",
                  "The UDoctor service has detected an error and generated"
                  " this alert. For more information, refer to the relevant"
                  " knowledgebase article on the support website or contact "
                  "your service provider."],
    "14:640003": ["CRITICAL", "ALRT_UDOCTOR_CRITICAL_ALERT",
                  "The UDoctor service has detected an error and generated "
                  "this alert. For more information, refer to the relevant "
                  "knowledgebase article on the support website or contact "
                  "your service provider."],
    "14:70001": ["ERROR", "ALRT_SEND_FAILED",
                 "The storage system failed to communicate an event message "
                 "via the Email server, SNMP servers, or ESRS gateway or "
                 "servers. Resolve the problem with the Email, ESRS, or "
                 "SNMP servers."],
    "14:70003": ["ERROR", "ALRT_BAD_PRVCY",
                 "Set the SNMP privacy protocol to one of the valid values: "
                 "DES or AES."],
    "14:70004": ["ERROR", "ALRT_BAD_AUTH",
                 "Set the SNMP authentication protocol to one of the valid "
                 "values: MD5 or SHA."],
    "14:80001": ["INFO", "DESC_TEST_UI_ALERT",
                 "This is a test message to be shown in a UI pop-up."],
    "14:90001": ["INFO", "DESC_TEST_PHONE_HOME_ALERT",
                 "This is a test message to be sent via ConnectHome."],
    "201:20000": ["INFO", "ALRT_NTP_OK",
                  "The system can now reach the NTP server."],
    "201:20001": ["WARNING", "ALRT_NTP_PART_NO_CONNECT",
                  "The system has a partial connection to the NTP server."],
    "201:20002": ["ERROR", "ALRT_NTP_NO_CONNECT",
                  "The system could not connect to the Time Server (NTP)."
                  " Check your NTP settings."],
    "301:24001": ["WARNING", "ALRT_STORAGE_SERVER_RESTART",
                  "The NAS servers that are configured to run on this Storage"
                  " Processor (SP) have stopped and will be automatically "
                  "restarted. ? This may affect host connections, which may"
                  " need to be reconnected to your storage resources. If the "
                  "problem persists, contact your service provider."],
    "301:30000": ["INFO", "ALRT_CONTROLLED_REBOOT_START",
                  "This Storage Processor (SP) is currently rebooting. No "
                  "action is required."],
    "301:30001": ["INFO", "ALRT_CONTROLLED_REBOOT_FINISHED",
                  "The Storage Processor (SP) has finished rebooting. No "
                  "action is required."],
    "301:30002": ["INFO", "ALRT_CONTROLLED_SERVICE_START",
                  "This Storage Processor (SP) is currently rebooting into "
                  "Service Mode. No action is required."],
    "301:3000e": ["INFO", "ALRT_CONTROLLED_SYSTEMSHUTDOWN_START",
                  "The Storage Processor (SP) is shutting down. The shut down "
                  "and power up procedure must be performed in a particular"
                  " order. If you have not already printed the power up"
                  " instructions, go to the EMC Support website to locate "
                  "product documentation."],
    "301:30010": ["NOTICE", "PLATFORM_HARDWARE_PERSIST_STARTED",
                  "A hardware commit operation has started. The system may "
                  "reboot multiple  times. Please do not interrupt this"
                  " process."],
    "301:30011": ["NOTICE", "PLATFORM_HARDWARE_COMMIT_COMPLETE",
                  "Your new hardware configuration has been committed and is "
                  "now ready for use."],
    "301:3001a": ["INFO", "ALRT_VVNX_CONTROLLED_SYSTEMSHUTDOWN_START",
                  "The Storage Processor (SP) is shutting down."],
    "301:31004": ["ERROR", "ALRT_DEBUG_PROCESS_CRASH",
                  "A process crashed, and it might impact the whole system."
                  " Please check the core dump by svc_dc -lcd after data "
                  "collection is complete (it usually needs several"
                  " minutes)."],
    "301:32001": ["ERROR", "PLATFORM_HARDWARE_COMMIT_FAILED",
                  "The hardware configuration could not be committed. Please"
                  " try again."],
    "301:40001": ["INFO", "ALRT_METRICS_DB_RECOVERED",
                  "Performance metrics are available now. No action is "
                  "required."],
    "301:48000": ["ERROR", "ALRT_METRICS_DB_FAIL",
                  "Performance metrics are unavailable due to a system error."
                  " Contact your service provider."]
}
IOPS_DESCRIPTION = {
    "unit": "IOPS",
    "description": "Input/output operations per second"
}
READ_IOPS_DESCRIPTION = {
    "unit": "IOPS",
    "description": "Read input/output operations per second"
}
WRITE_IOPS_DESCRIPTION = {
    "unit": "IOPS",
    "description": "Write input/output operations per second"
}
THROUGHPUT_DESCRIPTION = {
    "unit": "MB/s",
    "description": "Represents how much data is "
                   "successfully transferred in MB/s"
}
READ_THROUGHPUT_DESCRIPTION = {
    "unit": "MB/s",
    "description": "Represents how much data read is "
                   "successfully transferred in MB/s"
}
WRITE_THROUGHPUT_DESCRIPTION = {
    "unit": "MB/s",
    "description": "Represents how much data write is "
                   "successfully transferred in MB/s"
}
RESPONSE_TIME_DESCRIPTION = {
    "unit": "ms",
    "description": "Average time taken for an IO "
                   "operation in ms"
}
CACHE_HIT_RATIO_DESCRIPTION = {
    "unit": "%",
    "description": "Percentage of io that are cache hits"
}
READ_CACHE_HIT_RATIO_DESCRIPTION = {
    "unit": "%",
    "description": "Percentage of read ops that are cache hits"
}
WRITE_CACHE_HIT_RATIO_DESCRIPTION = {
    "unit": "%",
    "description": "Percentage of write ops that are cache hits"
}
IO_SIZE_DESCRIPTION = {
    "unit": "KB",
    "description": "The average size of IO requests in KB"
}
READ_IO_SIZE_DESCRIPTION = {
    "unit": "KB",
    "description": "The average size of read IO requests in KB"
}
WRITE_IO_SIZE_DESCRIPTION = {
    "unit": "KB",
    "description": "The average size of write IO requests in KB"
}
CPU_USAGE_DESCRIPTION = {
    "unit": "%",
    "description": "Percentage of CPU usage"
}
MEMORY_USAGE_DESCRIPTION = {
    "unit": "%",
    "description": "Percentage of DISK memory usage in percentage"
}
SERVICE_TIME = {
    "unit": 'ms',
    "description": "Service time of the resource in ms"
}
VOLUME_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION,
    "ioSize": IO_SIZE_DESCRIPTION,
    "readIoSize": READ_IO_SIZE_DESCRIPTION,
    "writeIoSize": WRITE_IO_SIZE_DESCRIPTION
}
PORT_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION
}
DISK_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION
}
FILESYSTEM_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "ioSize": IO_SIZE_DESCRIPTION,
    "readIoSize": READ_IO_SIZE_DESCRIPTION,
    "writeIoSize": WRITE_IO_SIZE_DESCRIPTION
}
