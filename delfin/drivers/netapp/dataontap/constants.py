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

SOCKET_TIMEOUT = 15
AUTH_KEY = 'Authorization'

RETURN_SUCCESS_CODE = 200
CREATED_SUCCESS_CODE = 201
ACCEPTED_RETURN_CODE = 202
BAD_REQUEST_RETURN_CODE = 400
UNAUTHORIZED_RETURN_CODE = 401
FORBIDDEN_RETURN_CODE = 403
NOT_FOUND_RETURN_CODE = 404
METHOD_NOT_ALLOWED_CODE = 405
CONFLICT_RETURN_CODE = 409
INTERNAL_ERROR_CODE = 500

HOUR_STAMP = '1h'
DAY_STAMP = '1d'
MONTH_STAMP = '1m'
WEEK_STAMP = '1w'
YEAR_STAMP = '1y'

CLUSTER_PER_URL = '/api/cluster/metrics?interval=1h&fields=iops,throughput,' \
                  'latency'
POOL_PER_URL = '/api/storage/aggregates/%s/metrics?interval=1h&fields=iops,' \
               'throughput,latency'
VOLUME_PER_URL = '/api/storage/luns/%s/metrics?interval=1h&fields=iops,' \
                 'throughput,latency'
FS_PER_URL = '/api/storage/volumes/%s/metrics?interval=1h&fields=iops,' \
             'throughput,latency'
FC_PER_URL = '/api/network/fc/ports/%s/metrics?interval=1h&fields=iops,' \
             'throughput,latency'
ETH_PER_URL = '/api/network/ethernet/ports/%s/metrics?interval=1h&' \
              'fields=throughput'

FS_INFO_URL = '/api/storage/volumes?fields=svm'
FC_INFO_URL = '/api/network/fc/ports'
ETH_INFO_URL = '/api/network/ethernet/ports?fields=node'
PER_MAP = {
    'iops': ['iops', 'total'],
    'readIops': ['iops', 'read'],
    'writeIops': ['iops', 'write'],
    'throughput': ['throughput', 'total'],
    'readThroughput': ['throughput', 'read'],
    'writeThroughput': ['throughput', 'write'],
    'responseTime': ['latency', 'total']
}

PATTERN = re.compile('^[-]{3,}')
CLUSTER_SHOW_COMMAND = "cluster identity show"
VERSION_SHOW_COMMAND = "version"
STORAGE_STATUS_COMMAND = "system health status show"

POOLS_SHOW_DETAIL_COMMAND = "storage pool show -instance"
AGGREGATE_SHOW_DETAIL_COMMAND = "storage aggregate show -instance"

FS_SHOW_DETAIL_COMMAND = "vol show -instance"
THIN_FS_SHOW_COMMAND = "vol show -space-guarantee none"

ALTER_SHOW_DETAIL_COMMAND = "system health alert show -instance"
EVENT_SHOW_DETAIL_COMMAND = "event show -instance -severity EMERGENCY"
EVENT_TIME_TYPE = '%m/%d/%Y %H:%M:%S'

ALTER_TIME_TYPE = '%a %b %d %H:%M:%S %Y'

CLEAR_ALERT_COMMAND = \
    "system health alert delete -alerting-resource * -alert-id"

DISK_SHOW_DETAIL_COMMAND = "disk show -instance"
DISK_SHOW_PHYSICAL_COMMAND = "disk show -physical"
DISK_ERROR_COMMAND = "disk error show"

LUN_SHOW_DETAIL_COMMAND = "lun show -instance"

CONTROLLER_SHOW_DETAIL_COMMAND = "node show -instance"

PORT_SHOW_DETAIL_COMMAND = "network port show -instance"
INTERFACE_SHOW_DETAIL_COMMAND = "network interface show -instance"
FC_PORT_SHOW_DETAIL_COMMAND = "fcp adapter show -instance"

QTREE_SHOW_DETAIL_COMMAND = "qtree show -instance"

CIFS_SHARE_SHOW_DETAIL_COMMAND = "vserver cifs share show -instance" \
                                 " -vserver %(vserver_name)s"
SHARE_AGREEMENT_SHOW_COMMAND = "vserver show -fields Allowed-protocols"
VSERVER_SHOW_COMMAND = "vserver show -type data"
NFS_SHARE_SHOW_COMMAND = "volume show -junction-active true -instance"

STORAGE_VENDOR = "NetApp"
STORAGE_MODEL = "cmodel"

QUOTA_SHOW_DETAIL_COMMAND = "volume quota policy rule show -instance"

MGT_IP_COMMAND = "network interface show -fields address -role cluster-mgmt"
NODE_IP_COMMAND = "network interface show -fields address -role node-mgmt"

CONTROLLER_IP_COMMAND = \
    "network interface show -fields address,curr-node  -role cluster-mgmt"

SECURITY_STYLE = {
    'mixed': constants.NASSecurityMode.MIXED,
    'ntfs': constants.NASSecurityMode.NTFS,
    'unix': constants.NASSecurityMode.UNIX
}

STORAGE_STATUS = {
    'ok': constants.StorageStatus.NORMAL,
    'ok-with-suppressed': constants.StorageStatus.NORMAL,
    'degraded': constants.StorageStatus.ABNORMAL,
    'unreachable': constants.StorageStatus.ABNORMAL,
    'unknown': constants.StorageStatus.ABNORMAL
}

AGGREGATE_STATUS = {
    'online': constants.StoragePoolStatus.NORMAL,
    'creating': constants.StoragePoolStatus.NORMAL,
    'mounting': constants.StoragePoolStatus.NORMAL,
    'relocating': constants.StoragePoolStatus.NORMAL,
    'quiesced': constants.StoragePoolStatus.NORMAL,
    'quiescing': constants.StoragePoolStatus.NORMAL,
    'unmounted': constants.StoragePoolStatus.OFFLINE,
    'unmounting': constants.StoragePoolStatus.OFFLINE,
    'destroying': constants.StoragePoolStatus.ABNORMAL,
    'partial': constants.StoragePoolStatus.ABNORMAL,
    'frozen': constants.StoragePoolStatus.ABNORMAL,
    'reverted': constants.StoragePoolStatus.NORMAL,
    'restricted': constants.StoragePoolStatus.NORMAL,
    'inconsistent': constants.StoragePoolStatus.ABNORMAL,
    'iron_restricted': constants.StoragePoolStatus.ABNORMAL,
    'unknown': constants.StoragePoolStatus.ABNORMAL,
    'offline': constants.StoragePoolStatus.OFFLINE,
    'failed': constants.StoragePoolStatus.ABNORMAL,
    'remote_cluster': constants.StoragePoolStatus.NORMAL,
}

VOLUME_STATUS = {
    'online': constants.VolumeStatus.AVAILABLE,
    'offline': constants.VolumeStatus.ERROR,
    'nvfail': constants.VolumeStatus.ERROR,
    'space-error': constants.VolumeStatus.ERROR,
    'foreign-lun-error': constants.VolumeStatus.ERROR,
}

ALERT_SEVERITY = {
    'Unknown': constants.Severity.NOT_SPECIFIED,
    'Other': constants.Severity.NOT_SPECIFIED,
    'Information': constants.Severity.INFORMATIONAL,
    'Degraded': constants.Severity.WARNING,
    'Minor': constants.Severity.MINOR,
    'Major': constants.Severity.MAJOR,
    'Critical': constants.Severity.CRITICAL,
    'Fatal': constants.Severity.FATAL,
}

DISK_TYPE = {
    'ATA': constants.DiskPhysicalType.ATA,
    'BSAS': constants.DiskPhysicalType.SATA,
    'FCAL': constants.DiskPhysicalType.FC,
    'FSAS': constants.DiskPhysicalType.NL_SAS,
    'LUN ': constants.DiskPhysicalType.LUN,
    'SAS': constants.DiskPhysicalType.SAS,
    'MSATA': constants.DiskPhysicalType.SATA,
    'SSD': constants.DiskPhysicalType.SSD,
    'VMDISK': constants.DiskPhysicalType.VMDISK,
    'unknown': constants.DiskPhysicalType.UNKNOWN,
}

DISK_LOGICAL = {
    'aggregate': constants.DiskLogicalType.AGGREGATE,
    'spare': constants.DiskLogicalType.SPARE,
    'unknown': constants.DiskLogicalType.UNKNOWN,
    'free': constants.DiskLogicalType.FREE,
    'broken': constants.DiskLogicalType.BROKEN,
    'foreign': constants.DiskLogicalType.FOREIGN,
    'labelmaint': constants.DiskLogicalType.LABELMAINT,
    'maintenance': constants.DiskLogicalType.MAINTENANCE,
    'shared': constants.DiskLogicalType.SHARED,
    'unassigned': constants.DiskLogicalType.UNASSIGNED,
    'unsupported': constants.DiskLogicalType.UNSUPPORTED,
    'remote': constants.DiskLogicalType.REMOTE,
    'mediator': constants.DiskLogicalType.MEDIATOR,
}

FS_STATUS = {
    'online': constants.FilesystemStatus.NORMAL,
    'restricted': constants.FilesystemStatus.FAULTY,
    'offline': constants.FilesystemStatus.NORMAL,
    'force-online': constants.FilesystemStatus.FAULTY,
    'force-offline': constants.FilesystemStatus.FAULTY,
}

NETWORK_LOGICAL_TYPE = {
    'data': constants.PortLogicalType.DATA,
    'cluster': constants.PortLogicalType.CLUSTER,
    'node-mgmt': constants.PortLogicalType.NODE_MGMT,
    'cluster-mgmt': constants.PortLogicalType.CLUSTER_MGMT,
    'intercluster': constants.PortLogicalType.INTERCLUSTER,
}

ETH_LOGICAL_TYPE = {
    'physical': constants.PortLogicalType.PHYSICAL,
    'if-group': constants.PortLogicalType.IF_GROUP,
    'vlan': constants.PortLogicalType.VLAN,
    'undef': constants.PortLogicalType.OTHER
}

FC_TYPE = {
    'fibre-channel': constants.PortType.FC,
    'ethernet': constants.PortType.FCOE
}

WORM_TYPE = {
    'non-snaplock': constants.WORMType.NON_WORM,
    'compliance': constants.WORMType.COMPLIANCE,
    'enterprise': constants.WORMType.ENTERPRISE,
    '-': constants.WORMType.NON_WORM
}

QUOTA_TYPE = {
    'user': constants.QuotaType.USER,
    'tree': constants.QuotaType.TREE,
    'group': constants.QuotaType.GROUP
}

NETWORK_PORT_TYPE = {
    'nfs': constants.PortType.NFS,
    'cifs': constants.PortType.CIFS,
    'iscsi': constants.PortType.ISCSI,
    'fcp': constants.PortType.FC,
    'fcache': constants.PortType.FCACHE,
    'none': constants.PortType.OTHER,
}

SEVERITY_MAP = {
    'AccessCache.ReachedLimits': 'EMERGENCY',
    'LUN.inconsistent.filesystem': 'EMERGENCY',
    'LUN.nvfail.vol.proc.failed': 'EMERGENCY',
    'Nblade.DidNotInitialize': 'EMERGENCY',
    'Nblade.cifsNoPrivShare': 'EMERGENCY',
    'Nblade.nfsV4PoolExhaust': 'EMERGENCY',
    'Nblade.vscanNoScannerConn': 'EMERGENCY',
    'adt.dest.directory.full': 'EMERGENCY',
    'adt.dest.directory.unavail': 'EMERGENCY',
    'adt.dest.volume.offline': 'EMERGENCY',
    'adt.service.block': 'EMERGENCY',
    'adt.service.ro.filesystem': 'EMERGENCY',
    'adt.stgvol.nospace': 'EMERGENCY',
    'adt.stgvol.offline': 'EMERGENCY',
    'api.engine.killed': 'EMERGENCY',
    'app.log.emerg': 'EMERGENCY',
    'arl.aggrOnlineFailed': 'EMERGENCY',
    'bge.EepromCrc': 'EMERGENCY',
    'boot.bootmenu.issue': 'EMERGENCY',
    'boot.varfs.backup.issue': 'EMERGENCY',
    'bootfs.env.issue': 'EMERGENCY',
    'callhome.battery.failure': 'EMERGENCY',
    'callhome.ch.ps.fan.bad.xmin': 'EMERGENCY',
    'callhome.chassis.overtemp': 'EMERGENCY',
    'callhome.chassis.undertemp': 'EMERGENCY',
    'callhome.clam.node.ooq': 'EMERGENCY',
    'callhome.client.app.emerg': 'EMERGENCY',
    'callhome.fans.failed': 'EMERGENCY',
    'callhome.hba.failed': 'EMERGENCY',
    'callhome.ibretimerprog.fail': 'EMERGENCY',
    'callhome.mcc.auso.trig.fail': 'EMERGENCY',
    'callhome.mcc.switchback.failed': 'EMERGENCY',
    'callhome.mcc.switchover.failed': 'EMERGENCY',
    'callhome.mdb.recovery.unsuccessful': 'EMERGENCY',
    'callhome.netinet.dup.clustIP': 'EMERGENCY',
    'callhome.nvram.failure': 'EMERGENCY',
    'callhome.partner.down': 'EMERGENCY',
    'callhome.ps.removed': 'EMERGENCY',
    'callhome.raid.no.recover': 'EMERGENCY',
    'callhome.raidtree.assim': 'EMERGENCY',
    'callhome.rlm.replace': 'EMERGENCY',
    'callhome.rlm.replace.lan': 'EMERGENCY',
    'callhome.root.vol.recovery.reqd': 'EMERGENCY',
    'callhome.sblade.lu.resync.to': 'EMERGENCY',
    'callhome.sblade.lu.rst.hung': 'EMERGENCY',
    'callhome.sblade.prop.fail': 'EMERGENCY',
    'callhome.sfo.takeover.panic': 'EMERGENCY',
    'callhome.shlf.fan': 'EMERGENCY',
    'callhome.vol.space.crit': 'EMERGENCY',
    'cf.fm.panicInToMode': 'EMERGENCY',
    'cf.fm.reserveDisksOff': 'EMERGENCY',
    'cf.fsm.autoGivebackAttemptsExceeded': 'EMERGENCY',
    'cf.takeover.missing.ptnrDiskInventory': 'EMERGENCY',
    'cf.takeover.missing.ptnrDisks': 'EMERGENCY',
    'cft.trans.commit.failed': 'EMERGENCY',
    'clam.node.ooq': 'EMERGENCY',
    'config.localswitch': 'EMERGENCY',
    'config.noBconnect': 'EMERGENCY',
    'config.noPartnerLUNs': 'EMERGENCY',
    'coredump.dump.failed': 'EMERGENCY',
    'ctran.group.reset.failed': 'EMERGENCY',
    'ctran.jpc.multiple.nodes': 'EMERGENCY',
    'ctran.jpc.split.brain': 'EMERGENCY',
    'ctran.jpc.valid.failed': 'EMERGENCY',
    'disk.dynamicqual.failure.shutdown': 'EMERGENCY',
    'ds.sas.xfer.unknown.error': 'EMERGENCY',
    'ems.eut.prilo0_log_emerg': 'EMERGENCY',
    'ems.eut.privar0_log_emerg_var': 'EMERGENCY',
    'fci.adapter.firmware.update.failed': 'EMERGENCY',
    'ha.takeoverImpHotShelf': 'EMERGENCY',
    'haosc.invalid.config': 'EMERGENCY',
    'license.capac.eval.shutdown': 'EMERGENCY',
    'license.capac.shutdown': 'EMERGENCY',
    'license.capac.unl.shutdown': 'EMERGENCY',
    'license.subscription.enforcement': 'EMERGENCY',
    'lmgr.aggr.CA.locks.dropped': 'EMERGENCY',
    'lun.metafile.OOVC.corrupt': 'EMERGENCY',
    'lun.metafile.VTOC.corrupt': 'EMERGENCY',
    'mcc.auso.trigFailed': 'EMERGENCY',
    'mcc.auso.triggerFailed': 'EMERGENCY',
    'mgmtgwd.rootvol.recovery.changed': 'EMERGENCY',
    'mgmtgwd.rootvol.recovery.different': 'EMERGENCY',
    'mgmtgwd.rootvol.recovery.low.space': 'EMERGENCY',
    'mgmtgwd.rootvol.recovery.new': 'EMERGENCY',
    'mgmtgwd.rootvol.recovery.takeover.changed': 'EMERGENCY',
    'mgr.boot.floppy_media': 'EMERGENCY',
    'mgr.boot.reason_abnormal': 'EMERGENCY',
    'mlm.array.portMixedAddress': 'EMERGENCY',
    'monitor.chassisFanFail.xMinShutdown': 'EMERGENCY',
    'monitor.fan.critical': 'EMERGENCY',
    'monitor.globalStatus.critical': 'EMERGENCY',
    'monitor.globalStatus.nonRecoverable': 'EMERGENCY',
    'monitor.ioexpansionTemperature.cool': 'EMERGENCY',
    'monitor.mismatch.shutdown': 'EMERGENCY',
    'monitor.nvramLowBatteries': 'EMERGENCY',
    'monitor.power.degraded': 'EMERGENCY',
    'monitor.shelf.accessError': 'EMERGENCY',
    'monitor.shutdown.brokenDisk': 'EMERGENCY',
    'monitor.shutdown.chassisOverTemp': 'EMERGENCY',
    'monitor.shutdown.emergency': 'EMERGENCY',
    'monitor.shutdown.ioexpansionOverTemp': 'EMERGENCY',
    'monitor.shutdown.ioexpansionUnderTemp': 'EMERGENCY',
    'monitor.shutdown.nvramLowBatteries': 'EMERGENCY',
    'monitor.shutdown.nvramLowBattery': 'EMERGENCY',
    'netif.badEeprom': 'EMERGENCY',
    'netif.overTempError': 'EMERGENCY',
    'netif.uncorEccError': 'EMERGENCY',
    'netinet.ethr.dup.clustIP': 'EMERGENCY',
    'nodewatchdog.node.failure': 'EMERGENCY',
    'nodewatchdog.node.longreboot': 'EMERGENCY',
    'nodewatchdog.node.panic': 'EMERGENCY',
    'nonha.resvConflictHalt': 'EMERGENCY',
    'nv.fio.write.err': 'EMERGENCY',
    'nv.none': 'EMERGENCY',
    'nv2flash.copy2NVMEM.failure': 'EMERGENCY',
    'nv2flash.copy2flash.failure': 'EMERGENCY',
    'nv2flash.hw.failure': 'EMERGENCY',
    'nv2flash.initfail': 'EMERGENCY',
    'nvmem.battery.capLowCrit': 'EMERGENCY',
    'nvmem.battery.capacity.low': 'EMERGENCY',
    'nvmem.battery.current.high': 'EMERGENCY',
    'nvmem.battery.currentHigh': 'EMERGENCY',
    'nvmem.battery.currentLow': 'EMERGENCY',
    'nvmem.battery.discFET.off': 'EMERGENCY',
    'nvmem.battery.fccLowCrit': 'EMERGENCY',
    'nvmem.battery.packInvalid': 'EMERGENCY',
    'nvmem.battery.powerFault': 'EMERGENCY',
    'nvmem.battery.temp.high': 'EMERGENCY',
    'nvmem.battery.tempHigh': 'EMERGENCY',
    'nvmem.battery.unread': 'EMERGENCY',
    'nvmem.battery.voltage.high': 'EMERGENCY',
    'nvmem.battery.voltageHigh': 'EMERGENCY',
    'nvmem.battery.voltageLow': 'EMERGENCY',
    'nvmem.voltage.high': 'EMERGENCY',
    'nvram.battery.capacity.low.critical': 'EMERGENCY',
    'nvram.battery.charging.nocharge': 'EMERGENCY',
    'nvram.battery.current.high': 'EMERGENCY',
    'nvram.battery.current.low': 'EMERGENCY',
    'nvram.battery.dischargeFET.off': 'EMERGENCY',
    'nvram.battery.fault': 'EMERGENCY',
    'nvram.battery.fcc.low.critical': 'EMERGENCY',
    'nvram.battery.not.present': 'EMERGENCY',
    'nvram.battery.power.fault': 'EMERGENCY',
    'nvram.battery.sensor.unreadable': 'EMERGENCY',
    'nvram.battery.temp.high': 'EMERGENCY',
    'nvram.battery.voltage.high': 'EMERGENCY',
    'nvram.battery.voltage.low': 'EMERGENCY',
    'nvram.decryptionKey.unavail': 'EMERGENCY',
    'nvram.encryptionKey.initfail': 'EMERGENCY',
    'nvram.hw.initFail': 'EMERGENCY',
    'platform.insufficientMemory': 'EMERGENCY',
    'pvif.allLinksDown': 'EMERGENCY',
    'pvif.initMemFail': 'EMERGENCY',
    'pvif.initMesgFail': 'EMERGENCY',
    'raid.assim.disk.nolabels': 'EMERGENCY',
    'raid.assim.fatal': 'EMERGENCY',
    'raid.assim.fatal.upgrade': 'EMERGENCY',
    'raid.assim.rg.missingChild': 'EMERGENCY',
    'raid.assim.tree.degradedDirty': 'EMERGENCY',
    'raid.assim.tree.multipleRootVols': 'EMERGENCY',
    'raid.assim.upgrade.aggr.fail': 'EMERGENCY',
    'raid.config.online.req.unsup': 'EMERGENCY',
    'raid.disk.owner.change.fail': 'EMERGENCY',
    'raid.mirror.bigio.restrict.failed': 'EMERGENCY',
    'raid.mirror.bigio.wafliron.nostart': 'EMERGENCY',
    'raid.multierr.unverified.block': 'EMERGENCY',
    'raid.mv.defVol.online.fail': 'EMERGENCY',
    'raid.rg.readerr.bad.file.block': 'EMERGENCY',
    'raid.rg.readerr.wc.blkErr': 'EMERGENCY',
    'raid.vol.volinfo.mismatch': 'EMERGENCY',
    'rdb.recovery.failed': 'EMERGENCY',
    'repl.checker.block.missing': 'EMERGENCY',
    'repl.physdiff.invalid.hole': 'EMERGENCY',
    'sas.adapter.firmware.update.failed': 'EMERGENCY',
    'sas.cable.unqualified': 'EMERGENCY',
    'sas.cpr.failed': 'EMERGENCY',
    'sas.cpr.recoveryThreshold': 'EMERGENCY',
    'scsiblade.kernel.volume.limbo.group': 'EMERGENCY',
    'scsiblade.kernel.vserver.limbo.group': 'EMERGENCY',
    'scsiblade.mgmt.wedged': 'EMERGENCY',
    'scsiblade.prop.done.error': 'EMERGENCY',
    'scsiblade.unavailable': 'EMERGENCY',
    'scsiblade.vol.init.failed': 'EMERGENCY',
    'scsiblade.volume.event.lost': 'EMERGENCY',
    'scsiblade.vs.purge.fail': 'EMERGENCY',
    'scsiblade.vserver.op.timeout': 'EMERGENCY',
    'scsitarget.fct.postFailed': 'EMERGENCY',
    'scsitarget.slifct.rebootRequired': 'EMERGENCY',
    'secd.ldap.noServers': 'EMERGENCY',
    'secd.lsa.noServers': 'EMERGENCY',
    'secd.netlogon.noServers': 'EMERGENCY',
    'secd.nis.noServers': 'EMERGENCY',
    'ses.badShareStorageConfigErr': 'EMERGENCY',
    'ses.config.IllegalEsh270': 'EMERGENCY',
    'ses.config.shelfMixError': 'EMERGENCY',
    'ses.psu.powerReqError': 'EMERGENCY',
    'ses.shelf.em.ctrlFailErr': 'EMERGENCY',
    'ses.status.enclError': 'EMERGENCY',
    'ses.status.fanError': 'EMERGENCY',
    'ses.status.volError': 'EMERGENCY',
    'ses.system.em.mmErr': 'EMERGENCY',
    'ses.unsupported.shelf.psu': 'EMERGENCY',
    'ses.unsupported.shelves.psus': 'EMERGENCY',
    'sfo.reassignFailed': 'EMERGENCY',
    'snapmirror.replay.failed': 'EMERGENCY',
    'sp.ipmi.lost.shutdown': 'EMERGENCY',
    'spm.mgwd.process.exit': 'EMERGENCY',
    'spm.secd.process.exit': 'EMERGENCY',
    'spm.vifmgr.process.exit': 'EMERGENCY',
    'spm.vldb.process.exit': 'EMERGENCY',
    'ups.battery.critical.goodlinepower': 'EMERGENCY',
    'ups.battery.warning': 'EMERGENCY',
    'ups.battery.warning.goodlinepower': 'EMERGENCY',
    'ups.inputpower.failed': 'EMERGENCY',
    'ups.systemshutdown': 'EMERGENCY',
    'vifmgr.clus.linkdown': 'EMERGENCY',
    'vifmgr.cluscheck.l2ping': 'EMERGENCY',
    'vifmgr.ipspace.tooMany': 'EMERGENCY',
    'vldb.update.duringsofail': 'EMERGENCY',
    'vol.phys.overalloc': 'EMERGENCY',
    'vsa.inadequateVM': 'EMERGENCY',
    'vsa.unlicensed': 'EMERGENCY',
    'wafl.aggr.rsv.low.nomount': 'EMERGENCY',
    'wafl.aggrtrans.outofspace.offline': 'EMERGENCY',
    'wafl.bad.aggr.buftree.type': 'EMERGENCY',
    'wafl.bad.vol.buftree.type': 'EMERGENCY',
    'wafl.buf.badHeader': 'EMERGENCY',
    'wafl.buf.freeingFreeBlock': 'EMERGENCY',
    'wafl.failed.mount': 'EMERGENCY',
    'wafl.failed.mount.bad.fsid': 'EMERGENCY',
    'wafl.inconsistent.dirent': 'EMERGENCY',
    'wafl.inconsistent.threshold.reached': 'EMERGENCY',
    'wafl.iron.abort.offlineFail': 'EMERGENCY',
    'wafl.iron.badfsid': 'EMERGENCY',
    'wafl.iron.oc.abort.bad_blk': 'EMERGENCY',
    'wafl.iron.oc.abort.clog_full': 'EMERGENCY',
    'wafl.iron.oc.deletedChangeLog': 'EMERGENCY',
    'wafl.iron.oc.errorCommitLog': 'EMERGENCY',
    'wafl.iron.oc.root.lowMemory': 'EMERGENCY',
    'wafl.mcc.so.nvram.warn': 'EMERGENCY',
    'wafl.nvlog.checkFail': 'EMERGENCY',
    'wafl.nvsave.replaying.fail': 'EMERGENCY',
    'wafl.nvsave.saving.fail': 'EMERGENCY',
    'wafl.offline.versionMismatch': 'EMERGENCY',
    'wafl.online.fail.vmalign': 'EMERGENCY',
    'wafl.online.notCompatibleVer': 'EMERGENCY',
    'wafl.online.vbnMismatch': 'EMERGENCY',
    'wafl.raid.incons.xidata': 'EMERGENCY',
    'wafl.scan.typebits.diffFail': 'EMERGENCY',
    'wafl.takeover.root.fail': 'EMERGENCY',
    'wafl.takeover.vol.fail': 'EMERGENCY',
    'wafl.vol.nvfail.offline': 'EMERGENCY',
    'wafl.vol.walloc.rsv.failmount': 'EMERGENCY'}

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

CAP_MAP = {
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
    "writeIoSize": WRITE_IO_SIZE_DESCRIPTION,
}

PERF_CAPABILITIES = {
            'is_historic': True,
            'resource_metrics': {
                "storage": {
                    "throughput": THROUGHPUT_DESCRIPTION,
                    "responseTime": RESPONSE_TIME_DESCRIPTION,
                    "iops": IOPS_DESCRIPTION,
                    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
                    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
                    "readIops": READ_IOPS_DESCRIPTION,
                    "writeIops": WRITE_IOPS_DESCRIPTION,
                },
                "storagePool": {
                    "throughput": THROUGHPUT_DESCRIPTION,
                    "responseTime": RESPONSE_TIME_DESCRIPTION,
                    "iops": IOPS_DESCRIPTION,
                    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
                    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
                    "readIops": READ_IOPS_DESCRIPTION,
                    "writeIops": WRITE_IOPS_DESCRIPTION,
                },
                "volume": {
                    "throughput": THROUGHPUT_DESCRIPTION,
                    "responseTime": RESPONSE_TIME_DESCRIPTION,
                    "iops": IOPS_DESCRIPTION,
                    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
                    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
                    "readIops": READ_IOPS_DESCRIPTION,
                    "writeIops": WRITE_IOPS_DESCRIPTION,
                },
                "port": {
                    "throughput": THROUGHPUT_DESCRIPTION,
                    "responseTime": RESPONSE_TIME_DESCRIPTION,
                    "iops": IOPS_DESCRIPTION,
                    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
                    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
                    "readIops": READ_IOPS_DESCRIPTION,
                    "writeIops": WRITE_IOPS_DESCRIPTION,
                },
                "filesystem": {
                    "throughput": THROUGHPUT_DESCRIPTION,
                    "responseTime": RESPONSE_TIME_DESCRIPTION,
                    "iops": IOPS_DESCRIPTION,
                    "readThroughput": READ_THROUGHPUT_DESCRIPTION,
                    "writeThroughput": WRITE_THROUGHPUT_DESCRIPTION,
                    "readIops": READ_IOPS_DESCRIPTION,
                    "writeIops": WRITE_IOPS_DESCRIPTION,
                },
            }
        }
