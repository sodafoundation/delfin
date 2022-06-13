# Copyright 2022 The SODA Authors.
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
ALERT_MAP = {
    'DEVICE_FAILED': 'Device failed',
    'SDC_DISCONNECTED': 'SDC disconnected',
    'MDM_NOT_CLUSTERED': 'MDM is not clustered',
    'SDS_DISCONNECTED ': 'SDS is disconnected',
    'SDS_DISCONNECTS_FREQUENTLY ': 'SDS disconnects frequently ',
    'SDS_RMCACHE_MEMORY_ALLOCATION_FAILED':
        'Memory allocation for RAM ReadCache failed on SDS',
    'STORAGE_POOL_HAS_CAPACITY_ERRORS': 'Storage Pool has capacity errors',
    'STORAGE_POOL_HAS_FAILED_CAPACITY': 'Storage Pool has failed capacity',
    'STORAGE_POOL_HAS_DEGRADED_CAPACITY': 'Storage Pool has degraded capacity',
    'STORAGE_POOL_HAS_UNREACHABLE_CAPACITY':
        'Storage Pool has decreased capacity',
    'STORAGE_POOL_HAS_UNAVAILABLE_UNUSED_CAPACITY':
        'Storage Pool has unavailable-unused capacity',
    'STORAGE_POOL_UNBALANCED': 'Storage Pool is unbalanced ',
    'CAPACITY_UTILIZATION_ABOVE_CRITICAL_THRESHOLD':
        'Capacity utilization above critical threshold',
    'CAPACITY_UTILIZATION_ABOVE_HIGH_THRESHOLD':
        'Capacity utilization above high threshold',
    'CONFIGURED_SPARE_CAPACITY_SMALLER_THAN_LARGEST_FAULT_UNIT':
    'Configured spare capacity is smaller than largest fault unit',
    'SPARE_CAPACITY_AND_FREE_CAPACITY_SMALLER_THAN_LARGEST_FAULT_UNIT':
        'Spare capacity and free capacity are smaller '
        'than the largest fault unit',
    'SPARE_CAPACITY_BELOW_THRESHOLD ': 'Spare capacity is below threshold',
    'LICENSE_EXPIRED': 'License expired',
    'LICENSE_ABOUT_TO_EXPIRE ': 'License will expire in %d days',
    'FWD_REBUILD_STUCK ': 'Forward rebuild cannot proceed ',
    'BKWD_REBUILD_STUCK': 'Backward rebuild cannot proceed',
    'REBALANCE_STUCK ': 'Rebalance cannot proceed ',
    'MDM_FAILS_OVER_FREQUENTLY': 'MDM fails over frequently',
    'FAILURE_RECOVERY_CAPACITY_BELOW_THRESHOLD':
        'Failure recovery capacity is below the threshold',
    'DEVICE_PENDING_ACTIVATION':
        'Device test is done and device is pending activation',
    'PD_INACTIVE ': 'Inactive Protection Domain',
    'DRL_MODE_NON_VOLATILE': 'DRL mode: Hardened ',
    'NOT_ENOUGH_FAULT_UNITS_IN_SP ':
        'Storage Pool does not meet the minimum requirement of 3 fault units',
    'SDC_MAX_COUNT': 'No more SDCs can be defined on this system; '
                     'the maximum has been reached',
    'FIXED_READ_ERROR_COUNT_ABOVE_THRESHOLD': 'Device has fixed read errors ',
    'SCANNER_COMPARE_ERROR':
        'Background device scanning has found data conflicts',
    'STORAGE_POOL_EXTREMELY_UNBALANCED':
        'The Storage Pool relies too heavily(over 50%)on capacity from a '
        'single SDS or Fault SetBalance capacity over other SDSs or Fault Sets'

}
