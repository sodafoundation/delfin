# Copyright 2022 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

SYSTEM_INFO = [
    {
        "systemVersionName": "DellEMC ScaleIO Version: R2_5.0.254",
        "capacityAlertHighThresholdPercent": 80,
        "capacityAlertCriticalThresholdPercent": 90,
        "remoteReadOnlyLimitState": False,
        "upgradeState": "NoUpgrade",
        "mdmManagementPort": 6611,
        "sdcMdmNetworkDisconnectionsCounterParameters": {
            "shortWindow": {
                "threshold": 300,
                "windowSizeInSec": 60
            },
            "mediumWindow": {
                "threshold": 500,
                "windowSizeInSec": 3600
            },
            "longWindow": {
                "threshold": 700,
                "windowSizeInSec": 86400
            }
        },
        "sdcSdsNetworkDisconnectionsCounterParameters": {
            "shortWindow": {
                "threshold": 800,
                "windowSizeInSec": 60
            },
            "mediumWindow": {
                "threshold": 4000,
                "windowSizeInSec": 3600
            },
            "longWindow": {
                "threshold": 20000,
                "windowSizeInSec": 86400
            }
        },
        "sdcMemoryAllocationFailuresCounterParameters": {
            "shortWindow": {
                "threshold": 300,
                "windowSizeInSec": 60
            },
            "mediumWindow": {
                "threshold": 500,
                "windowSizeInSec": 3600
            },
            "longWindow": {
                "threshold": 700,
                "windowSizeInSec": 86400
            }
        },
        "sdcSocketAllocationFailuresCounterParameters": {
            "shortWindow": {
                "threshold": 300,
                "windowSizeInSec": 60
            },
            "mediumWindow": {
                "threshold": 500,
                "windowSizeInSec": 3600
            },
            "longWindow": {
                "threshold": 700,
                "windowSizeInSec": 86400
            }
        },
        "sdcLongOperationsCounterParameters": {
            "shortWindow": {
                "threshold": 10000,
                "windowSizeInSec": 60
            },
            "mediumWindow": {
                "threshold": 100000,
                "windowSizeInSec": 3600
            },
            "longWindow": {
                "threshold": 1000000,
                "windowSizeInSec": 86400
            }
        },
        "cliPasswordAllowed": True,
        "managementClientSecureCommunicationEnabled": True,
        "tlsVersion": "TLSv1.2",
        "showGuid": True,
        "authenticationMethod": "Native",
        "mdmToSdsPolicy": "Authentication",
        "mdmCluster": {
            "clusterState": "ClusteredNormal",
            "clusterMode": "ThreeNodes",
            "goodNodesNum": 3,
            "goodReplicasNum": 2,
            "id": "8049148500852184920"
        },
        "perfProfile": "Default",
        "installId": "7b940dfb71191770",
        "daysInstalled": 6,
        "maxCapacityInGb": "Unlimited",
        "capacityTimeLeftInDays": "Unlimited",
        "isInitialLicense": True,
        "defaultIsVolumeObfuscated": False,
        "restrictedSdcModeEnabled": False,
        "restrictedSdcMode": "None",
        "enterpriseFeaturesEnabled": True,
        "id": "6fb451ea51a99758",
        "links": [
            {
                "rel": "/api/System/relationship/Statistics",
                "href": "/api/instances/System::6fb451ea51a99758/"
                        "relationships/Statistics"
            }
        ]
    }
]

SYSTEM_DETAIL = {
    "pendingMovingOutBckRebuildJobs": 0,
    "rfcachePoolWritePending": 0,
    "degradedHealthyCapacityInKb": 0,
    "activeMovingOutFwdRebuildJobs": 0,
    "rfcachePoolWritePendingG1Sec": 0,
    "bckRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "primaryReadFromDevBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "BackgroundScannedInMB": 0,
    "rfcacheReadsSkippedAlignedSizeTooLarge": 0,
    "rfcachePoolSize": 0,
    "pendingMovingInRebalanceJobs": 0,
    "rfcacheWritesSkippedHeavyLoad": 0,
    "rfcachePoolPagesInuse": 0,
    "unusedCapacityInKb": 14107527168,
    "rmcacheEntryEvictionCount": 0,
    "rfcacheFdAvgWriteTime": 0,
    "totalReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "totalWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rmPendingAllocatedInKb": 0,
    "numOfVolumes": 19,
    "rfcacheIosOutstanding": 0,
    "rmcacheBigBlockEvictionSizeCountInKb": 0,
    "capacityAvailableForVolumeAllocationInKb": 7038042112,
    "numOfMappedToAllVolumes": 0,
    "numOfScsiInitiators": 0,
    "rebuildPerReceiveJobNetThrottlingInKbps": 0,
    "rmcache32kbEntryCount": 0,
    "rfcachePoolEvictions": 0,
    "rfcachePoolNumCacheDevs": 0,
    "activeMovingInNormRebuildJobs": 0,
    "rfcacheFdWriteTimeGreater500Millis": 0,
    "rmcacheSkipCountCacheAllBusy": 0,
    "fixedReadErrorCount": 0,
    "rfcachePoolNumSrcDevs": 0,
    "numOfSdc": 3,
    "rfcacheFdMonitorErrorStuckIo": 0,
    "rfcacheReadsSkippedInternalError": 0,
    "pendingMovingInBckRebuildJobs": 0,
    "rfcachePoolWritePendingG500Micro": 0,
    "activeBckRebuildCapacityInKb": 0,
    "rebalanceCapacityInKb": 0,
    "rfcachePoolInLowMemoryCondition": 0,
    "rfcacheReadsSkippedLowResources": 0,
    "thinCapacityInUseInKb": 4096,
    "rfcachePoolLowResourcesInitiatedPassthroughMode": 0,
    "rfcachePoolWritePendingG10Millis": 0,
    "rfcacheWritesSkippedInternalError": 0,
    "rfcachePoolWriteHit": 0,
    "rmcache128kbEntryCount": 0,
    "rfcacheWritesSkippedCacheMiss": 0,
    "rfcacheFdReadTimeGreater5Sec": 0,
    "numOfFaultSets": 0,
    "degradedFailedCapacityInKb": 0,
    "BackgroundScanCompareCount": 0,
    "activeNormRebuildCapacityInKb": 0,
    "snapCapacityInUseInKb": 20967424,
    "rfcacheWriteMiss": 0,
    "rfcacheFdIoErrors": 0,
    "primaryReadFromRmcacheBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfVtrees": 19,
    "rfacheReadHit": 0,
    "rfcachePooIosOutstanding": 0,
    "pendingMovingCapacityInKb": 0,
    "numOfSnapshots": 0,
    "sdcIds": [
        "7bec302f00000000",
        "7bec303000000001",
        "7bec303100000002"
    ],
    "pendingFwdRebuildCapacityInKb": 0,
    "rmcacheBigBlockEvictionCount": 0,
    "rmcacheNoEvictionCount": 0,
    "rmcacheCurrNumOf128kbEntries": 0,
    "normRebuildCapacityInKb": 0,
    "rfcachePoolReadPendingG1Millis": 0,
    "primaryWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfThickBaseVolumes": 14,
    "rmcacheSizeInUseInKb": 0,
    "rfcachePoolReadPendingG10Millis": 0,
    "activeRebalanceCapacityInKb": 0,
    "rfcacheReadsSkippedLockIos": 0,
    "unreachableUnusedCapacityInKb": 0,
    "rfcachePoolReadPendingG500Micro": 0,
    "rmcache8kbEntryCount": 0,
    "numOfVolumesInDeletion": 0,
    "maxCapacityInKb": 17932736512,
    "pendingMovingOutFwdRebuildJobs": 0,
    "rmcacheSkipCountLargeIo": 0,
    "protectedCapacityInKb": 3825209343,
    "secondaryWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "normRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "thinCapacityAllocatedInKb": 2097152000,
    "thinCapacityAllocatedInKm": 2097152000,
    "rebalanceWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rmcacheCurrNumOf8kbEntries": 0,
    "primaryVacInKb": 2961178624,
    "secondaryVacInKb": 2961178624,
    "numOfDevices": 10,
    "rfcachePoolWriteMiss": 0,
    "rfcachePoolReadPendingG1Sec": 0,
    "failedCapacityInKb": 0,
    "rebalanceWaitSendQLength": 0,
    "rfcacheFdReadTimeGreater1Min": 0,
    "rmcache4kbEntryCount": 0,
    "rfcachePoolWritePendingG1Millis": 0,
    "rebalancePerReceiveJobNetThrottlingInKbps": 0,
    "rfcacheReadsFromCache": 0,
    "activeMovingOutBckRebuildJobs": 0,
    "rfcacheFdReadTimeGreater1Sec": 0,
    "rmcache64kbEntryCount": 0,
    "pendingMovingInNormRebuildJobs": 0,
    "primaryReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "failedVacInKb": 0,
    "pendingRebalanceCapacityInKb": 0,
    "rfcacheAvgReadTime": 0,
    "semiProtectedCapacityInKb": 0,
    "rfcachePoolSourceIdMismatch": 0,
    "rfcacheFdAvgReadTime": 0,
    "fwdRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritesReceived": 0,
    "rfcachePoolSuspendedIos": 0,
    "protectedVacInKb": 5922357248,
    "activeMovingRebalanceJobs": 0,
    "bckRebuildCapacityInKb": 0,
    "activeMovingInFwdRebuildJobs": 0,
    "pendingMovingRebalanceJobs": 0,
    "degradedHealthyVacInKb": 0,
    "rfcachePoolLockTimeGreater1Sec": 0,
    "semiProtectedVacInKb": 0,
    "userDataReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "pendingBckRebuildCapacityInKb": 0,
    "rmcacheCurrNumOf4kbEntries": 0,
    "capacityLimitInKb": 17932736512,
    "numOfProtectionDomains": 1,
    "activeMovingCapacityInKb": 0,
    "rfcacheIosSkipped": 0,
    "scsiInitiatorIds": [],
    "rfcacheFdWriteTimeGreater5Sec": 0,
    "userDataWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "inMaintenanceVacInKb": 0,
    "rfcacheReadsSkipped": 0,
    "rfcachePoolReadHit": 0,
    "rebuildWaitSendQLength": 0,
    "numOfUnmappedVolumes": 17,
    "rmcacheCurrNumOf64kbEntries": 0,
    "rfcacheWritesSkippedMaxIoSize": 0,
    "rfacheWriteHit": 0,
    "atRestCapacityInKb": 3825209344,
    "bckRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheSourceDeviceWrites": 0,
    "spareCapacityInKb": 0,
    "rfcacheFdInlightReads": 0,
    "normRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfSds": 3,
    "rfcacheIoErrors": 0,
    "capacityInUseInKb": 3825209344,
    "rebalanceReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rmcacheSkipCountUnaligned4kbIo": 0,
    "rfcacheReadsSkippedMaxIoSize": 0,
    "secondaryReadFromDevBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcachePoolSuspendedPequestsRedundantSearchs": 0,
    "secondaryReadFromRmcacheBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritesSkippedStuckIo": 0,
    "secondaryReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfStoragePools": 2,
    "rfcachePoolCachePages": 0,
    "inMaintenanceCapacityInKb": 0,
    "protectionDomainIds": [
        "4389836100000000"
    ],
    "inUseVacInKb": 5922357248,
    "fwdRebuildCapacityInKb": 0,
    "thickCapacityInUseInKb": 3825205248,
    "activeMovingInRebalanceJobs": 0,
    "rmcacheCurrNumOf32kbEntries": 0,
    "rfcacheWritesSkippedLowResources": 0,
    "rfcacheFdCacheOverloaded": 0,
    "rmcache16kbEntryCount": 0,
    "rmcacheEntryEvictionSizeCountInKb": 0,
    "rfcacheSkippedUnlinedWrite": 0,
    "rfcacheAvgWriteTime": 0,
    "pendingNormRebuildCapacityInKb": 0,
    "rfcacheFdReadTimeGreater500Millis": 0,
    "pendingMovingOutNormrebuildJobs": 0,
    "rfcacheSourceDeviceReads": 0,
    "rmcacheCurrNumOf16kbEntries": 0,
    "rfcacheReadsPending": 0,
    "fwdRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheReadsSkippedHeavyLoad": 0,
    "rfcacheFdInlightWrites": 0,
    "rfcacheReadMiss": 0,
    "rfcacheFdReadsReceived": 0,
    "activeMovingInBckRebuildJobs": 0,
    "movingCapacityInKb": 0,
    "pendingMovingInFwdRebuildJobs": 0,
    "rfcacheReadsReceived": 0,
    "rfcachePoolReadsPending": 0,
    "snapCapacityInUseOccupiedInKb": 0,
    "activeFwdRebuildCapacityInKb": 0,
    "rfcacheReadsSkippedStuckIo": 0,
    "activeMovingOutNormRebuildJobs": 0,
    "rfcacheFdWritesReceived": 0,
    "rmcacheSizeInKb": 393216,
    "rfcacheFdWriteTimeGreater1Min": 0,
    "rfcacheWritePending": 0,
    "rfcacheFdWriteTimeGreater1Sec": 0,
    "numOfThinBaseVolumes": 5,
    "numOfRfcacheDevices": 0,
    "degradedFailedVacInKb": 0,
    "rfcachePoolIoTimeGreater1Min": 0,
    "rfcachePoolReadMiss": 0
}
SYSTEM_STORAGE_POOL_INFO = [
    {
        "protectionDomainId": "4389836100000000",
        "sparePercentage": 0,
        "rmcacheWriteHandlingMode": "Cached",
        "checksumEnabled": False,
        "useRfcache": False,
        "rebuildEnabled": True,
        "rebalanceEnabled": True,
        "numOfParallelRebuildRebalanceJobsPerDevice": 2,
        "capacityAlertHighThreshold": 80,
        "capacityAlertCriticalThreshold": 90,
        "rebalanceIoPriorityPolicy": "favorAppIos",
        "rebuildIoPriorityNumOfConcurrentIosPerDevice": 1,
        "rebuildIoPriorityPolicy": "limitNumOfConcurrentIos",
        "rebalanceIoPriorityNumOfConcurrentIosPerDevice": 1,
        "rebuildIoPriorityBwLimitPerDeviceInKbps": 10240,
        "rebalanceIoPriorityBwLimitPerDeviceInKbps": 10240,
        "rebuildIoPriorityAppIopsPerDeviceThreshold": None,
        "rebalanceIoPriorityAppIopsPerDeviceThreshold": None,
        "rebuildIoPriorityAppBwPerDeviceThresholdInKbps": None,
        "rebalanceIoPriorityAppBwPerDeviceThresholdInKbps": None,
        "rebuildIoPriorityQuietPeriodInMsec": None,
        "rebalanceIoPriorityQuietPeriodInMsec": None,
        "zeroPaddingEnabled": False,
        "useRmcache": False,
        "backgroundScannerMode": "Disabled",
        "backgroundScannerBWLimitKBps": 0,
        "name": "StoragePool",
        "id": "b1566d0f00000000",
        "links": [
            {
                "rel": "/api/StoragePool/relationship/Statistics",
                "href": "/api/instances/StoragePool::b1566d0f00000000/"
                        "relationships/Statistics"
            }
        ]
    }
]

SYSTEM_POOL_DETAIL = {
    "pendingMovingOutBckRebuildJobs": 0,
    "deviceIds": [
        "6afe148700000000",
        "6afe3b9c00000001",
        "6afe3b9d00000002",
        "6afe148500010000",
        "6afe3b9900010001",
        "6afe3b9a00010002",
        "6afe3b9b00010003",
        "bbfe3b9600020000",
        "bbfe3b9e00020001",
        "bbfe3b9f00020002"
    ],
    "secondaryVacInKb": 2961178624,
    "numOfDevices": 10,
    "degradedHealthyCapacityInKb": 0,
    "activeMovingOutFwdRebuildJobs": 0,
    "bckRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "failedCapacityInKb": 0,
    "primaryReadFromDevBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "BackgroundScannedInMB": 0,
    "volumeIds": [
        "851005a700000000",
        "851005a800000001",
        "851005a900000002",
        "851005aa00000003",
        "851005ab00000004",
        "851005ac00000005",
        "851005ad00000006",
        "851005ae00000007",
        "851005af00000008",
        "851005b000000009",
        "851005b10000000a",
        "851005b20000000b",
        "851005b30000000c",
        "851005b40000000d",
        "851005b50000000e",
        "851005b60000000f",
        "85102cb300000010",
        "85102cb400000011",
        "85102cb500000012"
    ],
    "activeMovingOutBckRebuildJobs": 0,
    "rfcacheReadsFromCache": 0,
    "pendingMovingInNormRebuildJobs": 0,
    "rfcacheReadsSkippedAlignedSizeTooLarge": 0,
    "primaryReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "failedVacInKb": 0,
    "pendingMovingInRebalanceJobs": 0,
    "pendingRebalanceCapacityInKb": 0,
    "rfcacheWritesSkippedHeavyLoad": 0,
    "unusedCapacityInKb": 14107527168,
    "rfcacheAvgReadTime": 0,
    "semiProtectedCapacityInKb": 0,
    "totalReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "fwdRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "totalWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritesReceived": 0,
    "rmPendingAllocatedInKb": 0,
    "numOfVolumes": 19,
    "rfcacheIosOutstanding": 0,
    "protectedVacInKb": 5922357248,
    "capacityAvailableForVolumeAllocationInKb": 7038042112,
    "numOfMappedToAllVolumes": 0,
    "bckRebuildCapacityInKb": 0,
    "activeMovingInFwdRebuildJobs": 0,
    "activeMovingRebalanceJobs": 0,
    "pendingMovingRebalanceJobs": 0,
    "degradedHealthyVacInKb": 0,
    "semiProtectedVacInKb": 0,
    "userDataReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "pendingBckRebuildCapacityInKb": 0,
    "capacityLimitInKb": 17932736512,
    "vtreeIds": [
        "d39b454d00000000",
        "d39b454e00000001",
        "d39b454f00000002",
        "d39b455000000003",
        "d39b455100000004",
        "d39b455200000005",
        "d39b455300000006",
        "d39b455400000007",
        "d39b455500000008",
        "d39b455600000009",
        "d39b45570000000a",
        "d39b45580000000b",
        "d39b45590000000c",
        "d39b455a0000000d",
        "d39b455b0000000e",
        "d39b455c0000000f",
        "d39b6c5700000010",
        "d39b6c5800000011",
        "d39b6c5900000012"
    ],
    "activeMovingInNormRebuildJobs": 0,
    "activeMovingCapacityInKb": 0,
    "rfcacheIosSkipped": 0,
    "userDataWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "inMaintenanceVacInKb": 0,
    "rfcacheReadsSkipped": 0,
    "numOfUnmappedVolumes": 17,
    "rfcacheWritesSkippedMaxIoSize": 0,
    "fixedReadErrorCount": 0,
    "rfacheWriteHit": 0,
    "atRestCapacityInKb": 3825209344,
    "bckRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "pendingMovingInBckRebuildJobs": 0,
    "rfcacheReadsSkippedInternalError": 0,
    "activeBckRebuildCapacityInKb": 0,
    "rfcacheSourceDeviceWrites": 0,
    "spareCapacityInKb": 0,
    "rebalanceCapacityInKb": 0,
    "normRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheIoErrors": 0,
    "capacityInUseInKb": 3825209344,
    "rfcacheReadsSkippedLowResources": 0,
    "rebalanceReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "thinCapacityInUseInKb": 4096,
    "rfcacheReadsSkippedMaxIoSize": 0,
    "secondaryReadFromDevBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "secondaryReadFromRmcacheBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "secondaryReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritesSkippedStuckIo": 0,
    "rfcacheWritesSkippedInternalError": 0,
    "inMaintenanceCapacityInKb": 0,
    "inUseVacInKb": 5922357248,
    "fwdRebuildCapacityInKb": 0,
    "rfcacheWritesSkippedCacheMiss": 0,
    "thickCapacityInUseInKb": 3825205248,
    "activeMovingInRebalanceJobs": 0,
    "degradedFailedCapacityInKb": 0,
    "BackgroundScanCompareCount": 0,
    "activeNormRebuildCapacityInKb": 0,
    "snapCapacityInUseInKb": 26210304,
    "rfcacheWriteMiss": 0,
    "rfcacheWritesSkippedLowResources": 0,
    "primaryReadFromRmcacheBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfVtrees": 19,
    "rfacheReadHit": 0,
    "rfcacheSkippedUnlinedWrite": 0,
    "rfcacheAvgWriteTime": 0,
    "pendingMovingCapacityInKb": 0,
    "numOfSnapshots": 0,
    "pendingNormRebuildCapacityInKb": 0,
    "pendingFwdRebuildCapacityInKb": 0,
    "pendingMovingOutNormrebuildJobs": 0,
    "normRebuildCapacityInKb": 0,
    "rfcacheSourceDeviceReads": 0,
    "primaryWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfThickBaseVolumes": 14,
    "rfcacheReadsPending": 0,
    "rfcacheReadsSkippedHeavyLoad": 0,
    "fwdRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheReadMiss": 0,
    "activeRebalanceCapacityInKb": 0,
    "activeMovingInBckRebuildJobs": 0,
    "movingCapacityInKb": 0,
    "rfcacheReadsSkippedLockIos": 0,
    "unreachableUnusedCapacityInKb": 0,
    "pendingMovingInFwdRebuildJobs": 0,
    "rfcacheReadsReceived": 0,
    "numOfVolumesInDeletion": 0,
    "maxCapacityInKb": 17932736512,
    "snapCapacityInUseOccupiedInKb": 0,
    "pendingMovingOutFwdRebuildJobs": 0,
    "activeFwdRebuildCapacityInKb": 0,
    "rfcacheReadsSkippedStuckIo": 0,
    "activeMovingOutNormRebuildJobs": 0,
    "protectedCapacityInKb": 3825209343,
    "secondaryWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritePending": 0,
    "normRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfThinBaseVolumes": 5,
    "thinCapacityAllocatedInKb": 2097152000,
    "degradedFailedVacInKb": 0,
    "thinCapacityAllocatedInKm": 2097152000,
    "rebalanceWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "primaryVacInKb": 2961178624
}

SYSTEM_STORAGE_VOLUME_INFO = [
    {
        "mappedSdcInfo": [
            {
                "sdcId": "7bec302f00000000",
                "sdcIp": "192.168.3.240",
                "limitIops": 0,
                "limitBwInMbps": 0
            },
            {
                "sdcId": "7bec303100000002",
                "sdcIp": "192.168.3.239",
                "limitIops": 0,
                "limitBwInMbps": 0
            },
            {
                "sdcId": "7bec303000000001",
                "sdcIp": "192.168.3.241",
                "limitIops": 0,
                "limitBwInMbps": 0
            }
        ],
        "mappingToAllSdcsEnabled": False,
        "isVvol": False,
        "sizeInKb": 209715200,
        "vtreeId": "d39b455100000004",
        "isObfuscated": False,
        "volumeType": "ThinProvisioned",
        "consistencyGroupId": None,
        "ancestorVolumeId": None,
        "useRmcache": False,
        "storagePoolId": "b1566d0f00000000",
        "creationTime": 1653359703,
        "name": "volume023",
        "id": "851005ab00000004",
        "links": [
            {
                "rel": "/api/Volume/relationship/Statistics",
                "href": "/api/instances/Volume::851005ab00000004/"
                        "relationships/Statistics"
            }
        ]
    }
]
SYSTEM_VOLUME_DETAIL = {
    "descendantVolumeIds": [],
    "numOfMappedScsiInitiators": 0,
    "numOfChildVolumes": 0,
    "numOfMappedSdcs": 3,
    "userDataReadBwc": {
        "numSeconds": 1,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "userDataWriteBwc": {
        "numSeconds": 1,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "numOfDescendantVolumes": 0,
    "childVolumeIds": [],
    "mappedSdcIds": [
        "7bec302f00000000",
        "7bec303100000002",
        "7bec303000000001"
    ]
}

SYSTEM_STORAGE_DISK_INFO = [
    {
        "sdsId": "29ab6a0a00000000",
        "deviceState": "Normal",
        "capacityLimitInKb": 942668800,
        "maxCapacityInKb": 942668800,
        "ledSetting": "Off",
        "storagePoolId": "b1566d0f00000000",
        "errorState": "None",
        "name": "sd09",
        "id": "6afe3b9d00000002"
    }
]

SYSTEM_DISK_DETAIL = {
    "rfcacheReadsSkippedInternalError": 0,
    "pendingMovingInBckRebuildJobs": 0,
    "avgReadLatencyInMicrosec": 618,
    "rfcacheSourceDeviceWrites": 0,
    "pendingMovingOutBckRebuildJobs": 0,
    "secondaryVacInKb": 150192128,
    "normRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheIoErrors": 0,
    "capacityInUseInKb": 222265344,
    "rfcacheReadsSkippedLowResources": 0,
    "rebalanceReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "thinCapacityInUseInKb": 0,
    "activeMovingOutFwdRebuildJobs": 0,
    "rfcacheReadsSkippedMaxIoSize": 0,
    "secondaryReadFromDevBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "bckRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "avgWriteLatencyInMicrosec": 0,
    "secondaryReadFromRmcacheBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "secondaryReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritesSkippedInternalError": 0,
    "rfcacheWritesSkippedStuckIo": 0,
    "primaryReadFromDevBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "BackgroundScannedInMB": 0,
    "rfcacheReadsFromCache": 0,
    "activeMovingOutBckRebuildJobs": 0,
    "pendingMovingInNormRebuildJobs": 0,
    "inUseVacInKb": 310329344,
    "rfcacheWritesSkippedCacheMiss": 0,
    "rfcacheReadsSkippedAlignedSizeTooLarge": 0,
    "primaryReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "failedVacInKb": 0,
    "pendingMovingInRebalanceJobs": 0,
    "rfcacheWritesSkippedHeavyLoad": 0,
    "thickCapacityInUseInKb": 222265344,
    "unusedCapacityInKb": 719354880,
    "rfcacheAvgReadTime": 0,
    "activeMovingInRebalanceJobs": 0,
    "BackgroundScanCompareCount": 0,
    "totalReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "snapCapacityInUseInKb": 1048576,
    "rfcacheWriteMiss": 0,
    "rfcacheWritesSkippedLowResources": 0,
    "primaryReadFromRmcacheBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "fwdRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "totalWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritesReceived": 0,
    "rmPendingAllocatedInKb": 0,
    "rfacheReadHit": 0,
    "rfcacheIosOutstanding": 0,
    "rfcacheSkippedUnlinedWrite": 0,
    "protectedVacInKb": 310329344,
    "activeMovingInFwdRebuildJobs": 0,
    "activeMovingRebalanceJobs": 0,
    "rfcacheAvgWriteTime": 0,
    "pendingMovingRebalanceJobs": 0,
    "pendingMovingOutNormrebuildJobs": 0,
    "degradedHealthyVacInKb": 0,
    "rfcacheSourceDeviceReads": 0,
    "avgWriteSizeInBytes": 0,
    "primaryWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheReadsPending": 0,
    "rfcacheReadsSkippedHeavyLoad": 0,
    "semiProtectedVacInKb": 0,
    "fwdRebuildWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheReadMiss": 0,
    "avgReadSizeInBytes": 1024,
    "activeMovingInBckRebuildJobs": 0,
    "capacityLimitInKb": 942668800,
    "rfcacheReadsSkippedLockIos": 0,
    "unreachableUnusedCapacityInKb": 0,
    "pendingMovingInFwdRebuildJobs": 0,
    "rfcacheReadsReceived": 0,
    "activeMovingInNormRebuildJobs": 0,
    "rfcacheIosSkipped": 0,
    "inMaintenanceVacInKb": 0,
    "rfcacheReadsSkipped": 0,
    "snapCapacityInUseOccupiedInKb": 0,
    "maxCapacityInKb": 942668800,
    "pendingMovingOutFwdRebuildJobs": 0,
    "rfcacheReadsSkippedStuckIo": 0,
    "activeMovingOutNormRebuildJobs": 0,
    "secondaryWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "normRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "rfcacheWritePending": 0,
    "rfcacheWritesSkippedMaxIoSize": 0,
    "fixedReadErrorCount": 0,
    "thinCapacityAllocatedInKb": 88064000,
    "degradedFailedVacInKb": 0,
    "thinCapacityAllocatedInKm": 88064000,
    "rfacheWriteHit": 0,
    "rebalanceWriteBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "bckRebuildReadBwc": {
        "numSeconds": 0,
        "totalWeightInKb": 0,
        "numOccured": 0
    },
    "primaryVacInKb": 160137216
}

SYSTEM_HOST_INFO = [
    {
        "sdcApproved": True,
        "osType": "Linux",
        "mdmConnectionState": "Connected",
        "memoryAllocationFailure": None,
        "socketAllocationFailure": None,
        "softwareVersionInfo": "R2_5.0.0",
        "sdcGuid": "ADEF3BC8-693F-4FCF-A423-6890508731C8",
        "installedSoftwareVersionInfo": "R2_5.0.0",
        "kernelVersion": "3.10.0",
        "kernelBuildNumber": None,
        "sdcIp": "192.168.3.240",
        "sdcApprovedIps": None,
        "versionInfo": "R2_5.0.0",
        "perfProfile": "Default",
        "systemId": "6fb451ea51a99758",
        "name": None,
        "id": "7bec302f00000000",
    },
    {
        "sdcApproved": True,
        "osType": "Linux",
        "mdmConnectionState": "Connected",
        "memoryAllocationFailure": None,
        "socketAllocationFailure": None,
        "softwareVersionInfo": "R2_5.0.0",
        "sdcGuid": "FBAD6944-6F2D-442C-9AA1-9FF0403B7235",
        "installedSoftwareVersionInfo": "R2_5.0.0",
        "kernelVersion": "3.10.0",
        "kernelBuildNumber": None,
        "sdcIp": "192.168.3.241",
        "sdcApprovedIps": None,
        "versionInfo": "R2_5.0.0",
        "perfProfile": "Default",
        "systemId": "6fb451ea51a99758",
        "name": None,
        "id": "7bec303000000001",
    },
    {
        "sdcApproved": True,
        "osType": "Linux",
        "mdmConnectionState": "Connected",
        "memoryAllocationFailure": None,
        "socketAllocationFailure": None,
        "softwareVersionInfo": "R2_5.0.0",
        "sdcGuid": "FFA0F6C3-E2CD-45F5-AF7E-0C1DDF570303",
        "installedSoftwareVersionInfo": "R2_5.0.0",
        "kernelVersion": "3.10.0",
        "kernelBuildNumber": None,
        "sdcIp": "192.168.3.239",
        "sdcApprovedIps": None,
        "versionInfo": "R2_5.0.0",
        "perfProfile": "Default",
        "systemId": "6fb451ea51a99758",
        "name": None,
        "id": "7bec303100000002",
    }
]

SYSTEM_INITIATORS_INFO = [
    {
        "protectionDomainId": "4389836100000000",
        "faultSetId": None,
        "sdsState": "Normal",
        "membershipState": "Joined",
        "mdmConnectionState": "Connected",
        "drlMode": "Volatile",
        "rmcacheEnabled": True,
        "rmcacheSizeInKb": 131072,
        "rmcacheFrozen": False,
        "rmcacheMemoryAllocationState": "AllocationPending",
        "rfcacheEnabled": True,
        "maintenanceState": "NoMaintenance",
        "sdsDecoupled": None,
        "sdsConfigurationFailure": None,
        "sdsReceiveBufferAllocationFailures": None,
        "rfcacheErrorLowResources": False,
        "rfcacheErrorApiVersionMismatch": False,
        "rfcacheErrorInconsistentCacheConfiguration": False,
        "rfcacheErrorInconsistentSourceConfiguration": False,
        "rfcacheErrorInvalidDriverPath": False,
        "authenticationError": "None",
        "softwareVersionInfo": "R2_5.0.0",
        "rfcacheErrorDeviceDoesNotExist": False,
        "numOfIoBuffers": None,
        "perfProfile": "Default",
        "ipList": [
            {
                "ip": "192.168.3.241",
                "role": "all"
            }
        ],
        "onVmWare": True,
        "name": "SDS_192.168.3.241",
        "port": 7072,
        "id": "29ab911800000002",
    },
    {
        "protectionDomainId": "4389836100000000",
        "faultSetId": None,
        "sdsState": "Normal",
        "membershipState": "Joined",
        "mdmConnectionState": "Connected",
        "drlMode": "Volatile",
        "rmcacheEnabled": True,
        "rmcacheSizeInKb": 131072,
        "rmcacheFrozen": False,
        "rmcacheMemoryAllocationState": "AllocationPending",
        "rfcacheEnabled": True,
        "maintenanceState": "NoMaintenance",
        "sdsDecoupled": None,
        "sdsConfigurationFailure": None,
        "sdsReceiveBufferAllocationFailures": None,
        "rfcacheErrorLowResources": False,
        "rfcacheErrorApiVersionMismatch": False,
        "rfcacheErrorInconsistentCacheConfiguration": False,
        "rfcacheErrorInconsistentSourceConfiguration": False,
        "rfcacheErrorInvalidDriverPath": False,
        "authenticationError": "None",
        "softwareVersionInfo": "R2_5.0.0",
        "rfcacheErrorDeviceDoesNotExist": False,
        "numOfIoBuffers": None,
        "perfProfile": "Default",
        "ipList": [
            {
                "ip": "192.168.3.239",
                "role": "all"
            }
        ],
        "onVmWare": True,
        "name": "SDS_192.168.3.239",
        "port": 7072,
        "id": "29ab6a0a00000000",
    },
    {
        "protectionDomainId": "4389836100000000",
        "faultSetId": None,
        "sdsState": "Normal",
        "membershipState": "Joined",
        "mdmConnectionState": "Connected",
        "drlMode": "Volatile",
        "rmcacheEnabled": True,
        "rmcacheSizeInKb": 131072,
        "rmcacheFrozen": False,
        "rmcacheMemoryAllocationState": "AllocationPending",
        "rfcacheEnabled": True,
        "maintenanceState": "NoMaintenance",
        "sdsDecoupled": None,
        "sdsConfigurationFailure": None,
        "sdsReceiveBufferAllocationFailures": None,
        "rfcacheErrorLowResources": False,
        "rfcacheErrorApiVersionMismatch": False,
        "rfcacheErrorInconsistentCacheConfiguration": False,
        "rfcacheErrorInconsistentSourceConfiguration": False,
        "rfcacheErrorInvalidDriverPath": False,
        "authenticationError": "None",
        "softwareVersionInfo": "R2_5.0.0",
        "rfcacheErrorDeviceDoesNotExist": False,
        "numOfIoBuffers": None,
        "perfProfile": "Default",
        "ipList": [
            {
                "ip": "192.168.3.240",
                "role": "all"
            }
        ],
        "onVmWare": True,
        "name": "SDS_192.168.3.240",
        "port": 7072,
        "id": "29ab6a0800000001",
    }
]
SYSTEM_STORAGE = {
    "name": "ScaleIO",
    "vendor": "DELL EMC",
    "model": "DellEMC ScaleIO",
    "status": "normal",
    "serial_number": "6fb451ea51a99758",
    "firmware_version": "R2_5.0.254",
    "raw_capacity": 965292851200,
    "total_capacity": 18363122188288,
    "used_capacity": 3917014368256,
    "free_capacity": 14446107820032
}

SYSTEM_ALERT_INFO = [
    {
        "alertType": "TRIAL_LICENSE_USED",
        "severity": "ALERT_LOW",
        "affectedObject": {
            "type": "com.emc.ecs.api.model.gen.System",
            "id": "6fb451ea51a99758",
            "objectId": "6fb451ea51a99758"
        },
        "alertValues": {},
        "lastObserved": "2022-05-27T03:10:52.552Z",
        "uuid": "31d682d5-e696-466e-990a-57d0f9616b21",
        "startTime": "2022-05-26T18:00:13.336Z",
        "name": "31d682d5-e696-466e-990a-57d0f9616b21",
        "id": "31d682d5-e696-466e-990a-57d0f9616b21",
    }
]

SYSTEM_TRAP_ALERT = 'system.sysUpTime.0=6132004 S:1.1.4.1.0=E:1139.101.1 ' \
                    'E:1139.101.1.1=5 ' \
                    'E:1139.101.1.2="MDM.MDM_Cluster.MDM_CONNECTION_LOST" ' \
                    'E:1139.101.1.3="hjfadsfa42524533" ' \
                    'E:1139.101.1.4="SIO02.01.0000008"'

SYSTEM_STORAGE_POOL = [
    {
        "name": "StoragePool",
        "storage_id": "12345",
        "native_storage_pool_id": "b1566d0f00000000",
        "status": "normal",
        "storage_type": "block",
        "total_capacity": 18363122188288,
        "used_capacity": 3917014368256,
        "free_capacity": 14446107820032
    }
]

SYSTEM_STORAGE_VOLUME = [
    {
        "name": "volume023",
        "storage_id": "12345",
        "description": "volume023",
        "status": "normal",
        "native_volume_id": "851005ab00000004",
        "native_storage_pool_id": "b1566d0f00000000",
        "wwn": "851005ab00000004",
        "type": "thin",
        "total_capacity": 214748364800,
        "free_capacit": 0,
        "used_capacity": 0,
        "compressed": True,
        "deduplicated": True
    }
]

SYSTEM_STORAGE_DISK = [
    {
        'native_disk_id': '6afe3b9d00000002',
        'name': 'sd09',
        'status': 'normal',
        'storage_id': '12345',
        'native_disk_group_id': '29ab6a0a00000000',
        'serial_number': '6afe3b9d00000002',
        'capacity': 965292851200,
        'health_score': 'normal'
    }
]


SYSTEM_ALERT = [
    {
        'alert_id': '31d682d5-e696-466e-990a-57d0f9616b21',
        'alert_name': 'TRIAL_LICENSE_USED31d682d5-e696-466e-990a-57d0f9616b21',
        'severity': 'Minor',
        'category': 'Fault',
        'type': 'TRIAL_LICENSE_USED',
        'sequence_number': '31d682d5-e696-466e-990a-57d0f9616b21',
        'description': 'trial license used',
        'occur_time': 1653588013336,
        'match_key': '10648e5e11b1d6daf4f5cf989349967d'
    }
]

SYSTEM_HOST = [
    {
        "name": "ADEF3BC8-693F-4FCF-A423-6890508731C8",
        "description": "192.168.3.240R2_5.0.0",
        "storage_id": "12345",
        "native_storage_host_id": "7bec302f00000000",
        "os_type": "Linux",
        "status": "normal",
        "ip_address": "192.168.3.240"
    }, {
        "name": "FBAD6944-6F2D-442C-9AA1-9FF0403B7235",
        "description": "192.168.3.241R2_5.0.0",
        "storage_id": "12345",
        "native_storage_host_id": "7bec303000000001",
        "os_type": "Linux",
        "status": "normal",
        "ip_address": "192.168.3.241"
    }, {
        "name": "FFA0F6C3-E2CD-45F5-AF7E-0C1DDF570303",
        "description": "192.168.3.239R2_5.0.0",
        "storage_id": "12345",
        "native_storage_host_id": "7bec303100000002",
        "os_type": "Linux",
        "status": "normal",
        "ip_address": "192.168.3.239"
    }
]

SYSTEM_VIEW_MAPPING = [
    {'name': 'volume0237bec302f00000000851005ab00000004',
     'description': 'volume023',
     'storage_id': '12345',
     'native_masking_view_id': 'volume0237bec302f00000000851005ab00000004',
     'native_volume_id': '851005ab00000004',
     'native_storage_host_id': '7bec302f00000000'
     }, {
        'name': 'volume0237bec303100000002851005ab00000004',
        'description': 'volume023',
        'storage_id': '12345',
        'native_masking_view_id': 'volume0237bec303100000002851005ab00000004',
        'native_volume_id': '851005ab00000004',
        'native_storage_host_id': '7bec303100000002'
    }, {
        'name': 'volume0237bec303000000001851005ab00000004',
        'description': 'volume023',
        'storage_id': '12345',
        'native_masking_view_id': 'volume0237bec303000000001851005ab00000004',
        'native_volume_id': '851005ab00000004',
        'native_storage_host_id': '7bec303000000001'
    }
]


SYSTEM_INITIATORS = [
    {"name": "SDS_192.168.3.241",
     "storage_id": "12345",
     "native_storage_host_initiator_id": "29ab911800000002",
     "wwn": "29ab911800000002",
     "type": "unknown",
     "status": "online",
     "native_storage_host_id": "7bec303000000001"
     }, {
        "name": "SDS_192.168.3.239",
        "storage_id": "12345",
        "native_storage_host_initiator_id": "29ab6a0a00000000",
        "wwn": "29ab6a0a00000000",
        "type": "unknown",
        "status": "online",
        "native_storage_host_id": "7bec303100000002"
    }, {
        "name": "SDS_192.168.3.240",
        "storage_id": "12345",
        "native_storage_host_initiator_id": "29ab6a0800000001",
        "wwn": "29ab6a0800000001",
        "type": "unknown",
        "status": "online",
        "native_storage_host_id": "7bec302f00000000"
    }
]

SYSTEM_TRAP = {
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1655171867749,
    'severity': 'Critical',
    'description': 'mdm connection lost"',
    'location': 'mdm connection lost"',
    'alert_id': 'hjfadsfa42524533',
    'alert_name': 'SIO02.01.0000008'
}
