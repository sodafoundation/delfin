# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
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

# CPG's status
from delfin.common import constants

STATUS_POOL_NORMAL = 1  # CPG STATUS Normal operation
STATUS_POOL_DEGRADED = 2  # CPG STATUS Degraded state
STATUS_POOL_FAILED = 3  # CPG STATUS Abnormal operation
STATUS_POOL_UNKNOWN = 99  # CPG STATUS Unknown state
# VOLUME's status
STATUS_VOLUME_NORMAL = 1  # VOLUME STATUS Normal operation
STATUS_VOLUME_DEGRADED = 2  # VOLUME STATUS Degraded state
STATUS_VOLUME_FAILED = 3  # VOLUME STATUS Abnormal operation
STATUS_VOLUME_UNKNOWN = 99  # VOLUME STATUS Unknown state
# VOLUME's type
THIN_LUNTYPE = 2  # TPVV 2	• TPVV,
# VOLUME's Compression status
STATUS_COMPRESSION_YES = 1  # Compression is enabled on the volume
# VOLUME's deduplication status
STATUS_DEDUPLICATIONSTATE_YES = 1  # Enables deduplication on the volume
# Page size per page at default paging
QUERY_PAGE_SIZE = 150
# Connection timeout
LOGIN_SOCKET_TIMEOUT = 10
SOCKET_TIMEOUT = 10
# 403  The client request has an invalid session key.
# The request came from a different IP address
ERROR_SESSION_INVALID_CODE = 403
# 409  Session key is being used.
ERROR_SESSION_IS_BEING_USED_CODE = 409
# http SUCCESS's status
SUCCESS_STATUS_CODES = 200
# session SUCCESS's status
LOGIN_SUCCESS_STATUS_CODES = 201

SERVICE_UNAVAILABLE_CODES = 503
BAD_REQUEST_CODES = 400
NOT_IMPLEMENTED_CODES = 501

# alert state enumeration
ALERT_STATE_NEW = 1  # New.
ALERT_STATE_ACKED = 2  # Acknowledged state.
ALERT_STATE_FIXED = 3  # Alert issue fixed.
ALERT_STATE_UNKNOWN = 99  # Unknown state

# alert severity enumeration
ALERT_SEVERITY_CRITICAL = 2
ALERT_SEVERITY_MAJOR = 3
ALERT_SEVERITY_MINOR = 4
ALERT_SEVERITY_DEGRADED = 5

# alert code
HPE3PAR_ALERT_CODE = {
    '0x0000000': 'Node CPU Thermal Status',
    '0x0010001': 'Serial link event',
    '0x0010002': 'Serial link fail FIFO full',
    '0x0010003': 'Serial link fail full loss',
    '0x0010004': 'Serial link fail rate loss',
    '0x0020001': 'Active VLUN Limit Exceeded',
    '0x0020002': 'System Reporter VLUN performance (major alert)',
    '0x0020003': 'System Reporter VLUN performance (critical alert)',
    '0x0020004': 'System Reporter VLUN performance (minor alert)',
    '0x0020005': 'System Reporter VLUN performance (info alert)',
    '0x0030001': 'Firmware coredump event',
    '0x0030002': 'Too many WWNs on an RCFC port',
    '0x0030003': 'Host [[sw_port]] experienced over 50 CRC '
                 'errors (<count>) in 24 hours',
    '0x0030005': 'FC Port Error',
    '0x0030006': 'FC Port Loop Connection Type Not Supported',
    '0x0030007': 'RCFC port sees non-3PAR WWNs',
    '0x0030009': 'Excessive retransmits on RCFC port',
    '0x0030010': 'Port Device Count Exceeded',
    '0x0030011': 'CRC error on RCIP port',
    '0x0030012': 'Unsupported SATA Drive',
    '0x0030013': 'Unsupported SAS Device',
    '0x0030014': 'Multiple SAS Initiators',
    '0x0030015': 'System Reporter port performance (major alert)',
    '0x0030016': 'Disk Port has exceeded IO error threshold',
    '0x0030017': 'System Reporter port performance (critical alert)',
    '0x0030018': 'System Reporter port performance (minor alert)',
    '0x0030019': 'System Reporter port performance (info alert)',
    '0x00300de': 'Component state change',
    '0x00300fa': 'Component state change',
    '0x0040001': 'Metadata inconsistency in a VV',
    '0x0040003': 'Admin Volume I/O timeout',
    '0x0040004': 'VV availability',
    '0x0040005': 'Pinned DCOWs',
    '0x0040006': 'Aborted DCOWs',
    '0x0040007': 'Recovery scan found corrupt log',
    '0x0040008': 'vlmap count exceeds threshold',
    '0x0040009': 'FlashCache performance degradation',
    '0x004000a': 'VV unrecovered DIF error',
    '0x004000b': 'Metadata inconsistency in a Deduplication Group',
    '0x004000c': 'VV unrecovered DIF error',
    '0x004000d': 'System Reporter VV space major alert',
    '0x004000e': 'System Reporter VV space critical alert',
    '0x004000f': 'System Reporter VV space minor alert',
    '0x0040010': 'System Reporter VV space info alert',
    '0x0040011': 'Flash Cache Creation Failure',
    '0x0040012': 'SD Metadata inconsistency in a VV',
    '0x0040013': 'Compression is not enabled for Volumes less than 16GB',
    '0x0040014': 'System VV detected',
    '0x00400de': 'Component state change',
    '0x00400fa': 'Component state change',
    '0x0050002': 'Ldsk has failed set',
    '0x0050003': 'LD check summary message',
    '0x0050004': 'LD availability has reduced',
    '0x0050005': 'Log LD raid set failure.',
    '0x0050006': 'System Reporter LD performance (major alert)',
    '0x0050007': 'LD check inconsistent',
    '0x0050008': 'LD check failed LD not consistent',
    '0x0050009': 'LD check consistent',
    '0x005000a': 'LD check changed logical disk',
    '0x005000b': 'System Reporter LD performance (critical alert)',
    '0x005000c': 'System Reporter LD performance (minor alert)',
    '0x005000d': 'System Reporter LD performance (info alert)',
    '0x005000f': 'System Reporter LD space critical alert',
    '0x0050010': 'System Reporter LD space minor alert',
    '0x0050011': 'System Reporter LD space info alert',
    '0x0050012': 'System Reporter LD space major alert',
    '0x0060001': 'Disk fail alert',
    '0x0060002': 'Disk monitor stopped',
    '0x0060003': 'Invalid PD configuration',
    '0x0060007': '42 Alerts',
    '0x0060008': 'Disk overtemp warning',
    '0x0060009': 'Disk overtemp alert',
    '0x006000a': 'Chunklet relocation failure',
    '0x006000b': 'System Reporter PD performance (major alert)',
    '0x006000c': 'System overtemp',
    '0x006000d': 'Disk overtemp warning',
    '0x006000e': 'Disk overtemp alert',
    '0x0060011': 'Disk overtemp but not spundown',
    '0x0060012': 'Disk overtemp and spundown',
    '0x0060013': 'Disk overtemp but not spundown no DSK',
    '0x0060014': 'Disk overtemp and spundown no DSK',
    '0x0060015': 'System Reporter PD space major alert',
    '0x0060016': 'System Reporter PD space critical alert',
    '0x0060017': 'System Reporter PD space minor alert',
    '0x0060018': 'System Reporter PD space info alert',
    '0x0060019': 'System Reporter PD performance critical alert',
    '0x006001a': 'System Reporter PD performance minor alert',
    '0x006001b': 'System Reporter PD performance info alert',
    '0x00600de': 'Component state change',
    '0x00600fa': 'Component state change',
    '0x0070001': 'No free chunklet found for relocation',
    '0x0070002': 'No spare chunklet found for relocation',
    '0x0080001': 'Could not process SCSI DB',
    '0x0090001': 'Host Path Status Change',
    '0x00900de': 'Component state change',
    '0x00a0005': 'Snap Admin Volume low on space, degraded',
    '0x00a0006': 'Snap Data Volume low on space, degraded',
    '0x00a0007': 'Second snap Data Volume low on space, degraded',
    '0x00b0001': 'Kernel crashdump event',
    '0x00b0002': 'Kernel crashdump with error',
    '0x00c0001': 'Process has exited',
    '0x00c0002': 'Process cannot be started',
    '0x00c0003': 'Process coredump event',
    '0x00c0004': 'Attempt to run grub failed',
    '0x00c0005': 'Attempt to run grub failed, PM not starting',
    '0x00c0006': 'Attempt to run grub failed, retval',
    '0x00c0007': 'Process coredump with error',
    '0x00d0001': 'Corrupt PR table found',
    '0x00d0002': 'PR transition',
    '0x00d0003': 'PR transition, degraded.',
    '0x00e0001': 'Double node failure',
    '0x00e0002': 'System manager cannot startup',
    '0x00e0003': 'Node recovery powerfail event',
    '0x00e0004': '<success> use of golden license',
    '0x00e0005': 'License key usage, license expired',
    '0x00e0006': 'System recovery notification about bad volume',
    '0x00e0007': 'Pfail partition needs to be wiped',
    '0x00e0008': 'Power fail saved version mismatch',
    '0x00e0009': 'Failed to save task data',
    '0x00e000a': 'Task failed',
    '0x00e000b': 'Pfail recovery continued with failed previous NM1 recovery',
    '0x00e000d': 'System recovery stalled due to unknown replicant state',
    '0x00e000e': 'System recovery stalled due to sole owner of ld missing',
    '0x00e0011': '"servicemag start" operation has completed',
    '0x00e0012': '"servicemag resume" operation has completed',
    '0x00e0014': 'Battery States',
    '0x00e0015': 'Node not integrated',
    '0x00e0016': 'System recovery stalled due to unstarted vvs',
    '0x00e0017': 'TOC corruption detected',
    '0x00e0018': 'Pfail Recovery with a missing VV',
    '0x00e0019': 'Pfail Recovery with VV in bad state',
    '0x00e001a': 'Pfail Recovery skipped due to multiple NM1 nodes',
    '0x00e001b': 'NM1 pfail recovery proceeding with missing replicant',
    '0x00e001c': 'Configuration lock hold time',
    '0x00e001d': 'Inconsistent TOC object removed',
    '0x00e001e': 'Invalid VVMEMB(s) resolved',
    '0x00e001f': '"servicemag resume" operation has passed '
                 'with dismissed disks',
    '0x00e0020': '"servicemag resume" operation has passed '
                 'without dismissing any disks',
    '0x00e0021': '"servicemag resume" operation has failed '
                 'with no error message',
    '0x00e0022': '"servicemag resume" operation has failed to admit disk',
    '0x00e0023': '"servicemag resume" operation has failed '
                 'unrecoverable disk',
    '0x00e0024': '"servicemag resume" operation has failed to '
                 'relocate_chunklets',
    '0x00e0025': 'System manager cannot start up, TOC not found',
    '0x00e0026': 'System manager cannot start up, waiting on nodes',
    '0x00e0027': 'System manager cannot start up, manual start up set',
    '0x00e0028': 'System manager cannot start up, TOC quorum not met',
    '0x00e0029': 'System manager cannot start up, waiting for '
                 'nodes to recover',
    '0x00e002a': 'Pfail partition needs to be wiped',
    '0x00e002b': 'Pfail partition needs to be wiped',
    '0x00e002c': 'System manager cannot start up, incomplete powerfail',
    '0x00e002d': 'System manager cannot start up, TOC quorum found, '
                 'incomplete powerfail',
    '0x00e002e': 'System manager cannot start up, TOC quorum found, '
                 'waiting for nodes to recover',
    '0x00e002f': 'System manager cannot start up, waiting for nodes '
                 'to recover',
    '0x00e0030': 'Unexpected encryption state on node drive',
    '0x00e0031': '"servicemag start" failed',
    '0x00e0032': 'Single node WBC is active',
    '0x00e0033': 'Single node WBC is expired',
    '0x0100001': 'Online upgrade',
    '0x0100002': 'Unresponsive IOCTL',
    '0x0100003': 'Update available',
    '0x0100004': 'Update status',
    '0x0100005': 'Update install status',
    '0x0100006': 'Unresponsive IOCTL Verbose',
    '0x0110001': 'Errors accessing the IDE disk',
    '0x0110002': 'IDE disk error handling',
    '0x0110004': 'Version mismatch event',
    '0x0110005': 'Serial comm init failed',
    '0x0110006': 'IDE disk error node shutdown',
    '0x0110007': 'IDE disk error node not shutdown',
    '0x0110008': 'IDE disk error node not shutdown LDs cannot be served',
    '0x0110009': 'IDE disk error node reboot',
    '0x011000a': 'Version mismatch event for svcalert',
    '0x011000b': 'Version mismatch event',
    '0x011000c': 'Version mismatch event',
    '0x0130001': 'Too many alerts in the system',
    '0x0140001': 'Notification',
    '0x0140003': 'fork(2) call failed',
    '0x0140004': 'System Reporter QoS performance (major alert)',
    '0x0140005': 'SFP Unqualified Notification',
    '0x0140007': 'System upgrade cancelled',
    '0x0140008': 'System upgrade Cancellation Failed',
    '0x0140009': 'System serial number could not be determined',
    '0x014000a': 'DC3 I2C Lockup Reset Succeeded',
    '0x014000b': 'DC3 I2C Lockup Reset Failed',
    '0x014000c': 'admitpd not allowed on Emulex generated wwn',
    '0x014000d': 'admitpd not allowed on toto-sata generated wwn',
    '0x014000e': 'RAID 0 LD failed due to stale chunklet',
    '0x014000f': 'Mismatch of failed chunklet information',
    '0x0140010': 'System Reporter QoS performance (critical alert)',
    '0x0140011': 'System Reporter QoS performance (minor alert)',
    '0x0140012': 'System Reporter QoS performance (info alert)',
    '0x0150004': 'CLI server cannot communicate with system manager',
    '0x0150005': 'CLI internal error using authentication library',
    '0x0150006': 'Authentication failure',
    '0x0150007': 'CLI internal error',
    '0x015000c': 'CPG free space limit',
    '0x015000d': 'CLI client process event',
    '0x015000f': 'Relocatepd request',
    '0x0150010': 'Control Recovery Auth Ciphertext Export',
    '0x0150011': 'CLI server process event, max tpdtcl exceeded',
    '0x0150012': 'CLI server process event, twice max tpdtcl exceeded',
    '0x0150013': 'CLI server process event, max CLI server exceeded',
    '0x0150014': 'CLI server process event, max local exceeded',
    '0x0150015': 'CLI server process event, max server exceeded brief',
    '0x0150016': 'CLI server process event, max server exceeded local',
    '0x0150017': 'CLI server process event, error in track',
    '0x0150018': 'CLI server process event, error in store user name',
    '0x0150019': 'CLI server process event, svcalert brief',
    '0x015001a': 'CLI server process event, svcalert',
    '0x015001b': 'CLI internal error Failed sanity check',
    '0x015001c': 'CLI internal error sqlite database',
    '0x015001d': 'CLI internal error SQLite DB',
    '0x015001f': 'CLI client process event disk high temp',
    '0x0150020': 'Unable to send an event to the security syslog server.',
    '0x0150021': 'Connection has been reestablished to the '
                 'security syslog server.',
    '0x0150022': 'Slow Disk temperature unavailable',
    '0x0170001': 'TOC update',
    '0x0170004': 'TOC update, not above error threshold and decreased.',
    '0x0170005': 'TOC update, not above warn threshold and decreased.',
    '0x0190001': 'ea msg timeout',
    '0x0190002': 'Pre Integration Link Test Error',
    '0x01a0001': 'CPU Memory Correctable ECC',
    '0x01a0002': 'Node is offline',
    '0x01a0003': 'Node Time of Day Battery',
    '0x01a0005': 'HW: CPU Memory Correctable ECC',
    '0x01a0006': 'CPU Configuration',
    '0x01a0007': 'BIOS IDE log entry',
    '0x01a0008': 'Node Environmental Check Pass',
    '0x01a0009': 'IDE file integrity check results',
    '0x01a000b': 'Eagle memory uerr',
    '0x01a000c': 'Eagle memory muerr',
    '0x01a000d': 'Eagle memory cerr',
    '0x01a000e': 'Eagle internal system error',
    '0x01a000f': 'Eagle hardware watchdog error',
    '0x01a0010': 'Eagle PCI error',
    '0x01a0011': 'Eagle driver software error',
    '0x01a0012': 'Memory usage information',
    '0x01a0014': 'Too many TCP segment retransmits',
    '0x01a0015': 'Node PCIe Correctable Error Status',
    '0x01a0016': 'Node PCIe Link Status',
    '0x01a0017': 'Too many TCP segment errors',
    '0x01a0019': 'Cluster thermal shutdown',
    '0x01a001a': 'Link Configuration Mismatch',
    '0x01a001b': 'Unexpected Cable Event',
    '0x01a001c': 'Link establish alert',
    '0x01a001d': 'Core File Received From Remote/Local MCU',
    '0x01a001f': 'Node Needs to Shutdown',
    '0x01a0021': 'Node Rescue',
    '0x01a0022': 'Node-Failure-Analysis File Received From Remote/Local MCU',
    '0x01a0024': 'Slab usage information',
    '0x01a0025': 'System Reporter cmp performance (major alert)',
    '0x01a0026': 'System Reporter CPU performance (major alert)',
    '0x01a0027': 'System Reporter link performance (major alert)',
    '0x01a0028': 'Node ID Mismatch',
    '0x01a0029': 'Remote Node ID Mismatch',
    '0x01a002a': 'System Model Mismatch',
    '0x01a002b': 'Remote System Model Mismatch',
    '0x01a002c': 'Node Type Mismatch',
    '0x01a002d': 'Remote Node Type Mismatch',
    '0x01a002e': 'SSN Mismatch',
    '0x01a002f': 'Remote SSN Mismatch',
    '0x01a0031': 'Node Rescue User Abort',
    '0x01a0032': 'Node Rescue Invalid',
    '0x01a0033': 'Node Rescue Internal Communication Error',
    '0x01a0034': 'Node Rescue No Rejoin',
    '0x01a0035': 'Node Rescue Port 80 Blocked',
    '0x01a0036': 'Node Rescue Port 69 Blocked',
    '0x01a0037': 'Node Rescue Port 873 Blocked',
    '0x01a0038': 'Node Rescue No Backplane Connection',
    '0x01a0039': 'CMP Threshold',
    '0x01a003a': 'DIF error',
    '0x01a003b': 'IDE file integrity check bad run',
    '0x01a003c': 'IDE file integrity check bad',
    '0x01a003d': 'IDE file integrity check very bad',
    '0x01a003e': 'System Reporter cache performance alert',
    '0x01a003f': 'Legacy System Model Mismatch',
    '0x01a0040': 'Remote System Model Mismatch',
    '0x01a0041': 'Node Rescue Detected Dual Boot Node Drive Size Mismatch',
    '0x01a0042': 'Node Environmental Check Fail',
    '0x01a0043': 'Node Thermal Status svc alert',
    '0x01a0044': 'Node Needs to Shutdown svc alert',
    '0x01a0045': 'Node Thermal Status Alert',
    '0x01a0046': 'Node Thermal Status Warning',
    '0x01a0047': 'System Reporter cmp performance (critical alert)',
    '0x01a0048': 'System Reporter cmp performance (minor alert)',
    '0x01a0049': 'System Reporter cmp performance (info alert)',
    '0x01a004a': 'System Reporter CPU performance (critical alert)',
    '0x01a004b': 'System Reporter CPU performance (minor alert)',
    '0x01a004c': 'System Reporter CPU performance (info alert)',
    '0x01a004d': 'System Reporter link performance (critical alert)',
    '0x01a004e': 'System Reporter link performance (minor alert)',
    '0x01a004f': 'System Reporter link performance (info alert)',
    '0x01a0050': 'System Reporter cache performance (critical alert)',
    '0x01a0051': 'System Reporter cache performance (minor alert)',
    '0x01a0052': 'System Reporter cache performance (info alert)',
    '0x01a0053': 'Eagle link error',
    '0x01a0054': 'System Series Mismatch',
    '0x01a0055': 'Remote System Series Mismatch',
    '0x01a0056': 'Node temporary filesystem in use',
    '0x01a0057': 'Node rescue detected that rescuee node has an '
                 'incompatible board series',
    '0x01a00de': 'Component state change',
    '0x01a00fa': 'Component state change',
    '0x01b0001': 'Power Supply',
    '0x01b0002': 'Power Supply DC Status',
    '0x01b0003': 'Power Supply AC Status',
    '0x01b0004': 'Power Supply Fan Status',
    '0x01b0005': 'Power Supply Charger Status',
    '0x01b0009': 'Power Supply Type Mismatch',
    '0x01b0015': 'VSC 055 Interrupt Error',
    '0x01b00de': 'Component state change',
    '0x01b00fa': 'Component state change',
    '0x01d0001': 'Bios eeprom log events',
    '0x01e0001': 'Cage log event',
    '0x01e0005': 'Cage coredump event',
    '0x01e0006': 'servicemag failed to dismiss PD: '
                 'cage <cageid>, mag <magid>, '
                 'taskid <taskid>, pd <pdid>: error<smag_err> - <text>',
    '0x01e0007': 'Critical ESI port count, down to one',
    '0x01e0008': 'Critical ESI port count, one valid',
    '0x01e0009': 'Critical ESI port count, lost',
    '0x01e000a': 'Invalid cage isolated configuration',
    '0x01e000b': 'Invalid cage isolated configuration',
    '0x01e000c': 'Invalid cage mixed configuration',
    '0x01e000d': 'Invalid cage unknown configuration',
    '0x01e000e': 'Invalid cage partners configuration',
    '0x01e000f': 'Invalid cage maxcage configuration',
    '0x01e0010': 'Invalid cage twice configuration',
    '0x01e0011': 'Unknown cage configuration',
    '0x01e0012': 'Cage coredump event - detailed - 0',
    '0x01e0013': 'Cage coredump event - detailed - 1',
    '0x01e0014': 'Cage coredump event - detailed - 2',
    '0x01e0015': 'Cage coredump event - detailed - 3',
    '0x01e0016': 'Cage coredump event - very detailed - 0',
    '0x01e0017': 'Cage coredump event - very detailed - 1',
    '0x01e0018': 'Cage log event, firmware panic',
    '0x01e0019': 'Cage log event, midplane esi',
    '0x01e001a': 'Cage log event, midplane',
    '0x01e001b': 'Cage log event, post',
    '0x01e001c': 'Cage log event, midplane lm87',
    '0x01e001d': 'Cage log event, midplane pmc',
    '0x01e00de': 'Component state change',
    '0x01e00fa': 'Component state change',
    '0x01f0001': 'Mixing SSDs with different RPMs not supported',
    '0x01f00de': 'Component state change',
    '0x01f00fa': 'Component state change',
    '0x0200006': 'GUI server can not communicate with the system manager',
    '0x0200009': 'Internal error in authentication library',
    '0x0210001': 'InForm GUI has lost connection to the event filter',
    '0x0220001': 'Battery expiring soon',
    '0x0220010': 'Assert Battery FAIL',
    '0x0220014': 'Battery Type Mismatch',
    '0x0220017': 'Battery expiration soon',
    '0x02200de': 'Component state change',
    '0x02200fa': 'Component state change',
    '0x0230003': 'Port shutdown on fatal error',
    '0x0230004': 'Host port is down',
    '0x0230005': 'All ports in the same FC card must be configured for RCFC',
    '0x0230006': 'HBA fw file status',
    '0x0230007': 'HBA FW error opening file',
    '0x0230008': 'HBA FW error reading file',
    '0x0230009': 'HBA FW unsupported file',
    '0x0240002': 'Internodal Serial Port Receiver Timeout Error',
    '0x0240003': 'Internodal Serial Port Default Error',
    '0x0250002': 'Remote Copy link status',
    '0x0250007': 'System Reporter RC Target performance (major alert)',
    '0x0250008': 'System Reporter RC VV performance (major alert)',
    '0x0250009': 'Remote Copy group in failsafe state',
    '0x025000a': 'Replication resource usage exceeded - Group "Logging".',
    '0x025000b': 'Replication resource usage exceeded - Group "Stopped".',
    '0x025000c': 'Replication resources restored - Group transition '
                 'from Logging failure',
    '0x025000d': 'System Reporter RC VV performance (critical alert)',
    '0x025000e': 'System Reporter RC VV performance (minor alert)',
    '0x025000f': 'System Reporter RC VV performance (info alert)',
    '0x0250011': 'System Reporter RC Target performance (critical alert)',
    '0x0250012': 'System Reporter RC Target performance (minor alert)',
    '0x0250013': 'System Reporter RC Target performance (info alert)',
    '0x0250014': 'Remote Copy group status alert',
    '0x0250015': 'Remote Copy group status fail',
    '0x0250016': 'Quorum is not in Started state',
    '0x0260001': 'Ethernet Monitor Event',
    '0x0260002': 'No admin network interface discovered',
    '0x0270001': 'TP VV allocation size warning',
    '0x0270002': 'TP VV allocation size limit',
    '0x0270003': 'Snapshot space allocation size warning',
    '0x0270004': 'Snapshot space allocation size limit',
    '0x0270005': 'CPG growth warning',
    '0x0270006': 'CPG growth limit',
    '0x0270007': 'TP VV allocation failure',
    '0x0270008': 'Snapshot space allocation failure',
    '0x0270009': 'CPG growth failure',
    '0x027000e': 'FC raw space allocation 50% alert',
    '0x027000f': 'FC raw space allocation 75% alert',
    '0x0270010': 'FC raw space allocation 85% alert',
    '0x0270011': 'FC raw space allocation 95% alert',
    '0x0270012': 'CPG space used status',
    '0x0270013': 'Raw space allocation user configured alert',
    '0x0270014': 'NL raw space allocation 50% alert',
    '0x0270015': 'NL raw space allocation 75% alert',
    '0x0270016': 'NL raw space allocation 85% alert',
    '0x0270017': 'NL raw space allocation 95% alert',
    '0x0270018': 'CPG was grown with degraded parameters',
    '0x0270019': 'SSD raw space allocation 50% alert',
    '0x027001a': 'SSD raw space allocation 75% alert',
    '0x027001b': 'SSD raw space allocation 85% alert',
    '0x027001c': 'SSD raw space allocation 95% alert',
    '0x027001d': 'CPG growth failure non-admin',
    '0x027001e': 'CPG growth non admin limit',
    '0x027001f': 'CPG growth non admin warning',
    '0x0270020': 'Overprovisioning CPG warning alert',
    '0x0270021': 'Overprovisioning CPG limit alert',
    '0x0270022': 'Overprovisioning warning alert',
    '0x0270023': 'Overprovisioning limit alert',
    '0x0270024': 'System Reporter CPG space critical alert',
    '0x0270025': 'System Reporter CPG space minor alert',
    '0x0270026': 'System Reporter CPG space info alert',
    '0x0270027': 'System Reporter CPG space major alert',
    '0x0280001': 'Preserved data LDs configuration',
    '0x0280002': 'Preserved data LDs unavailable',
    '0x0280003': 'Preserved data LDs are filling up',
    '0x0280004': 'Preserved data LDs are full',
    '0x0280005': 'LD availability',
    '0x0280006': 'Preserved data LDs status, mangler class',
    '0x0280007': 'Preserved data LDs configuration, Not configured',
    '0x0280008': 'Preserved data LDs configuration, Not started',
    '0x02900de': 'Component state change',
    '0x02a00de': 'Component state change',
    '0x02a00fa': 'Component state change',
    '0x02b00de': 'Component state change',
    '0x02b00fa': 'Component state change',
    '0x02d00de': 'Component state change',
    '0x02d00fa': 'Component state change',
    '0x03500de': 'Component state change',
    '0x03500fa': 'Component state change',
    '0x0360002': 'Write Cache Availability',
    '0x0360003': 'System Reporter system space critical alert',
    '0x0360004': 'System Reporter system space major alert',
    '0x0360005': 'System Reporter system space info alert',
    '0x0360006': 'System Reporter system space minor alert',
    '0x03700de': 'Component state change',
    '0x03700fa': 'Component state change',
    '0x03800de': 'Component state change',
    '0x03900fa': 'Component state change',
    '0x03a00de': 'Component state change',
    '0x03a00fa': 'Component state change',
    '0x03b0002': 'Free node disk space low',
    '0x03b0004': 'Node drive is encrypted but encryption is '
                 'not enabled on the system',
    '0x03b0005': 'Encryption is enabled on the system but the '
                 'node drive is not encrypted',
    '0x03b0006': 'Unable to do I/O to the node drive',
    '0x03b0007': 'Free node disk space low, /common not mounted',
    '0x03b0008': 'Free node disk space low, /altroot not mounted',
    '0x03b0009': 'Free node disk space low, /common and /altroot not mounted',
    '0x03b000a': 'Syslog Node Drive Failure Message Monitoring',
    '0x03b000b': 'Periodic /proc/mdstat Monitoring '
                 'Detected Degraded Node Drive Raid',
    '0x03b000c': 'Lost interrupt',
    '0x03b000d': 'IDE SMART failed self check',
    '0x03b000e': 'IDE SMART unreadable sectors',
    '0x03b000f': 'IDE SMART uncorrectable sectors',
    '0x03b0010': 'IDE SMART failed unit ready',
    '0x03b0011': 'IDE SMART failed usage attribute',
    '0x03b0012': 'IDE SMART failure',
    '0x03b0013': 'IDE SMART execute test failed',
    '0x03b0014': 'IDE SMART new self test log error',
    '0x03b0015': 'IDE SMART repeat self test log error',
    '0x03b0016': 'IDE SMART ATA error increase',
    '0x03b0017': 'IDE SMART attribute data read fail',
    '0x03b0019': 'IDE SMART error log read fail',
    '0x03b0020': 'DUAL IDE SMART failed self check',
    '0x03b0021': 'DUAL IDE SMART unreadable sectors',
    '0x03b0022': 'DUAL IDE SMART uncorrectable sectors',
    '0x03b0023': 'DUAL IDE SMART failed unit ready',
    '0x03b0024': 'DUAL IDE SMART failed usage attribute',
    '0x03b0025': 'DUAL IDE SMART failure',
    '0x03b0026': 'DUAL IDE SMART execute test failed',
    '0x03b0027': 'DUAL IDE SMART new self test log error',
    '0x03b0028': 'DUAL IDE SMART repeat self test log error',
    '0x03b0029': 'DUAL IDE SMART ATA error increase',
    '0x03b002a': 'DUAL IDE SMART attribute data read fail',
    '0x03b002b': 'DUAL IDE SMART error log read fail',
    '0x03f0001': 'Process appears unresponsive',
    '0x03f0002': 'Process name appears unresponsive',
    '0x03f0003': 'Process event handling appears unresponsive',
    '0x0450001': 'Data Cache DIMM CECC Monitoring',
    '0x0450002': 'Patrol Data Cache DIMM UERR',
    '0x0460001': 'Control Cache DIMM Temperature',
    '0x0460002': 'Control Cache DIMM Temperature',
    '0x0460003': 'Node FB-DIMM AMB Correctable Error Status',
    '0x04a0001': 'Slot PCIe Correctable Error Status',
    '0x04a0002': 'Slot PCIe Link Status',
    '0x04e0001': 'Rejecting SSH Connection',
    '0x04e0002': 'Rejecting SSH Connection from IP',
    '0x0500001': 'A system task failed',
    '0x05d00de': 'Component state change',
    '0x05d00fa': 'Component state change',
    '0x0600005': 'WSAPI internal error using authentication library',
    '0x06200fa': 'Component state change',
    '0x0640001': 'PD Scrub',
    '0x0660001': 'SED is from the wrong system',
    '0x0660002': 'SED has the wrong key',
    '0x0660003': 'SED is present, but encryption is not enabled',
    '0x0660004': 'LKM is in an unknown state',
    '0x0660005': 'MMAP failed to map the segment of the memory with keys',
    '0x0660006': 'Nodesvr unresponsive during darsvr startup',
    '0x0660007': 'Nodesvr unresponsive during fipsvr startup',
    '0x0660008': 'fipsvr unable to start in FIPS mode',
    '0x0660009': 'Failed to successfully communicate with EKM at startup',
    '0x066000a': 'Controlencryption restore failed',
    '0x066000b': 'Controlencryption restore ignore failed',
    '0x066000c': 'Controlencryption restore ignore succeeded with failures',
    '0x066000d': 'Encryption operation attempted on drive with WWN 0',
    '0x066000e': 'Unsupported drive present in the system',
    '0x06700de': 'Component state change',
    '0x0680001': 'Quorum Witness',
    '0x06e0001': 'File Services state change',
    '0x0720001': 'File Provisioning Group',
    '0x0740001': 'File Store',
    '0x0750001': 'Virtual Server IP Address',
    '0x0760001': 'Node Network Bond',
    '0x0770001': 'Node Network Interface',
    '0x0780001': 'Node IP Address',
    '0x0790001': 'File Service Node Active Directory Configuration',
    '0x07e0001': 'Anti-Virus VSE Server',
    '0x0810001': 'Anti-Virus Scan',
    '0x0820001': 'Virtual Server Certificate',
    '0x0840001': 'HTTP Share',
    '0x0850001': 'NFS Share',
    '0x0860001': 'SMB Share',
    '0x0870001': 'User Quota',
    '0x08b0001': 'File Store Snapshot',
    '0x08c0001': 'File Provisioning Group Snap Reclamation Task',
    '0x08d0001': 'Overall File Services for Node',
    '0x08e0001': 'File Services Software Update',
    '0x08f0001': 'File Services Log Collection',
    '0x0900001': 'File Service Virtual Server Backup',
    '0x0960002': 'Vasa Provider migration failed due to VVol SC migration',
    '0x0960003': 'Vasa Provider migration failed due '
                 'to Certificate mode migration',
    '0x0960004': 'Vasa Provider migration failed while updating config file',
    '0x0960005': 'VASA provider could not start because of '
                 'issues with the VASA Certificate',
    '0x0990001': 'Static IP Route',
    '0x09a0001': 'SMB Global Setting State change event',
    '0x09b0001': 'Ddcscan Monitoring',
    '0x09d0001': 'NVDIMM Battery Failure',
    '0x09e0003': 'Management Module High Temperature',
    '0x09e0004': 'Management Module not responding',
    '0x09f0001': 'File Persona VM shutdown',
    '0x09f0002': 'File Persona CPG grow limit warning',
    '0x0a50001': 'File Access Auditing Alerts'
}
NODE_PATTERN = "^\\s*Node\\s+[-]*Name[-]*\\s+[-]*State[-]*\\s+Master\\s+"
CPU_PATTERN = "^\\s*Node\\s+CPU\\s+[-]*Manufacturer[-]*\\s+[-]*Serial[-]*" \
              "\\s+CPUSpeed"
DISK_PATTERN = "^\\s*Id\\s+[-]*CagePos[-]*\\s+[-]*Type[-]*\\s+RPM\\s+State\\s+"
DISK_I_PATTERN = "^\\s*Id\\s+[-]*CagePos[-]*\\s+[-]*State[-]*\\s+" \
                 "[-]*Node_WWN[-]*\\s+[-]*MFR[-]*\\s+[-]*Model[-]*\\s+" \
                 "[-]*Serial[-]*\\s+[-]*FW_Rev[-]*"
PORT_PATTERN = "^\\s*N:S:P\\s+[-]*Mode[-]*\\s+[-]*State[-]*\\s+[-]*" \
               "Node_WWN[-]*\\s+[-]*Port_WWN/HW_Addr[-]*\\s+"
PORT_I_PATTERN = "^\\s*N:S:P\\s+Brand\\s+Model\\s+Rev\\s+Firmware\\s+" \
                 "Serial\\s+HWType"
PORT_PER_PATTERN = "^\\s*N:S:P\\s+Connmode\\s+ConnType\\s+CfgRate\\s+MaxRate"
PORT_C_PATTERN = "^\\s*N:S:P\\s+Mode\\s+Device\\s+Pos\\s+Config\\s+" \
                 "Topology\\s+Rate"
PORT_ISCSI_PATTERN = "^\\s*N:S:P\\s+State\\s+IPAddr\\s+Netmask/PrefixLen\\s+" \
                     "Gateway"
PORT_RCIP_PATTERN = "^\\s*N:S:P\\s+State\\s+[-]*HwAddr[-]*\\s+IPAddr\\s+" \
                    "Netmask\\s+Gateway\\s+MTU\\s+Rate"
PORT_FCOE_PATTERN = "^\\s*N:S:P\\s+State\\s+"
PORT_FS_PATTERN = "^\\s*N:S:P\\s+State\\s+"
FPG_PATTERN = "^\\s*FPG\\s+[-]*Mountpath[-]*\\s+[-]*Size[-]*\\s+[-]*" \
              "Available[-]*\\s+[-]*ActiveStates"
CPG_PATTERN = "^\\s*Id\\s+[-]*Name[-]*\\s+Warn"
VOLUME_PATTERN = "^\\s*Id\\s+Name\\s+Prov\\s+Compr\\s+Dedup"
FSTORE_PATTERN = "^\\s*Fstore\\s+VFS\\s+FPG\\s+State\\s+Mode"
FSHARE_PATTERN = "^\\s*ShareName\\s+Protocol\\s+VFS\\s+FileStore\\s+" \
                 "ShareDir\\s+State"
VFS_PATTERN = "^\\s*VFS\\s+FPG\\s+IPAddr\\s+State"

SRSTATPORT_PATTERN = "^\\s*PORT_N\\s+PORT_S\\s+PORT_P\\s+Rd\\s+Wr\\s+" \
                     "Tot\\s+Rd\\s+Wr\\s+Tot\\s+Rd\\s+Wr\\s+Tot"
SRSTATPD_PATTERN = "^\\s*PDID\\s+Rd\\s+Wr\\s+" \
                   "Tot\\s+Rd\\s+Wr\\s+Tot\\s+Rd\\s+Wr\\s+Tot"
SRSTATVV_PATTERN = "^\\s*VVID\\s+VV_NAME\\s+Rd\\s+Wr\\s+" \
                   "Tot\\s+Rd\\s+Wr\\s+Tot\\s+Rd\\s+Wr\\s+Tot"

IPV4_PATTERN = "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$"
CONTROLLER_STATUS_MAP = {
    'OK': constants.ControllerStatus.NORMAL,
    'NORMAL': constants.ControllerStatus.NORMAL,
    'DEGRADED': constants.ControllerStatus.DEGRADED,
    'FAILED': constants.ControllerStatus.FAULT
}
DISK_PHYSICAL_TYPE_MAP = {
    'FC': constants.DiskPhysicalType.FC,
    'SSD': constants.DiskPhysicalType.SSD,
    'NL': constants.DiskPhysicalType.UNKNOWN
}
DISK_STATUS_MAP = {
    'NORMAL': constants.DiskStatus.NORMAL,
    'DEGRADED': constants.DiskStatus.ABNORMAL,
    'FAILED': constants.DiskStatus.ABNORMAL,
    'NEW': constants.DiskStatus.ABNORMAL
}
PORT_CONNECTION_STATUS_MAP = {
    'CONFIG_WAIT': constants.PortConnectionStatus.DISCONNECTED,
    'ALPA_WAIT': constants.PortConnectionStatus.DISCONNECTED,
    'LOGIN_WAIT': constants.PortConnectionStatus.DISCONNECTED,
    'READY': constants.PortConnectionStatus.CONNECTED,
    'LOSS_SYNC': constants.PortConnectionStatus.DISCONNECTED,
    'ERROR_STATE': constants.PortConnectionStatus.DISCONNECTED,
    'XXX': constants.PortConnectionStatus.DISCONNECTED,
    'NONPARTICIPATE': constants.PortConnectionStatus.DISCONNECTED,
    'COREDUMP': constants.PortConnectionStatus.DISCONNECTED,
    'OFFLINE': constants.PortConnectionStatus.DISCONNECTED,
    'FWDEAD': constants.PortConnectionStatus.DISCONNECTED,
    'IDLE_FOR_RESET': constants.PortConnectionStatus.DISCONNECTED,
    'DHCP_IN_PROGRESS': constants.PortConnectionStatus.DISCONNECTED,
    'PENDING_RESET': constants.PortConnectionStatus.DISCONNECTED
}
PORT_TYPE_MAP = {
    'FC': constants.PortType.FC,
    'ISCSI': constants.PortType.ISCSI,
    'ETH': constants.PortType.ETH,
    'CNA': constants.PortType.CNA,
    'SAS': constants.PortType.SAS,
    'COMBO': constants.PortType.COMBO,
    'NVMe': constants.PortType.OTHER,
    'UNKNOWN': constants.PortType.OTHER,
    'RCIP': constants.PortType.RCIP,
    'RCFC': constants.PortType.OTHER
}
SSH_METRIC_TYPE = {
    1: "io",
    2: "kbytes",
    3: "svct",
    4: "iosz"
}
SSH_COLLECT_TIME_PATTERN = "\\(\\d+\\)"
COLLECT_INTERVAL_HIRES = 60000
SIXTY_SECONDS = 60
REST_COLLEC_TTIME_PATTERN = '%Y-%m-%dT%H:%M:%SZ'
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
POOL_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION
}
VOLUME_CAP = {
    "iops": IOPS_DESCRIPTION,
    "readIops": READ_IOPS_DESCRIPTION,
    "writeIops": WRITE_IOPS_DESCRIPTION,
    "throughput": THROUGHPUT_DESCRIPTION,
    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION,
    "cacheHitRatio": CACHE_HIT_RATIO_DESCRIPTION,
    "readCacheHitRatio": READ_CACHE_HIT_RATIO_DESCRIPTION,
    "writeCacheHitRatio": WRITE_CACHE_HIT_RATIO_DESCRIPTION,
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
    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
    "responseTime": RESPONSE_TIME_DESCRIPTION
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
SECONDS_PER_HOUR = 3600
