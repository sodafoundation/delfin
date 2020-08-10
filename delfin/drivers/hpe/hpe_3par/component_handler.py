# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_log import log

from delfin import exception
from delfin.common import constants
from delfin.drivers.hpe.hpe_3par import consts, alert_handler
# from delfin.drivers.hpe.threepar import alert_handler

import time

LOG = log.getLogger(__name__)


class ComponentHandler():
    """Hpe3par's Component handler，Superclass,
    """
    # ssh command
    HPE3PAR_COMMAND_CHECKHEALTH = 'checkhealth'  # return: System is healthy
    HPE3PAR_COMMAND_SHOWALERT = 'showalert'
    HPE3PAR_VERSION = 'Superclass'

    def __init__(self, restclient=None, sshclient=None):
        self.restclient = restclient
        self.sshclient = sshclient

    def set_storage_id(self, storage_id):
        self.storage_id = storage_id

    def get_storage(self, context):
        t = time.time()
        # get storage info
        storage = self.restclient.get_storage()
        LOG.info('Get storage=={}'.format(storage))

        # capacity = self.restclient.get_capacity()
        # LOG.info('Get capacity=={}'.format(capacity))

        # default state is offline
        status = constants.StorageStatus.OFFLINE

        if storage is not None:
            try:
                # Check the hardware and software health status of the storage system
                # return: System is healthy
                commandStr = ComponentHandler.HPE3PAR_COMMAND_CHECKHEALTH
                reStr = self.sshclient.doexec(context, commandStr)
                if 'System is healthy' in reStr:
                    status = constants.StorageStatus.NORMAL
                else:
                    status = constants.StorageStatus.ABNORMAL
            except Exception:
                status = constants.StorageStatus.ABNORMAL
                LOG.error('SSH check health Failed!')
            # "Total capacity (MiB) in the system."
            total_cap = int(
                storage.get('totalCapacityMiB')) * consts.MiB_TO_Bytes
            # Free capacity (MiB) in the system
            free_cap = int(
                storage.get('freeCapacityMiB')) * consts.MiB_TO_Bytes
            used_cap = total_cap - free_cap

            # raw_capacity
            raw_cap = int(
                storage.get('totalCapacityMiB')) * consts.MiB_TO_Bytes
            # subscribed_capacity
            subscribed_cap = int(
                storage.get('allocatedCapacityMiB')) * consts.MiB_TO_Bytes
            s = {
                'name': storage.get('name'),
                # 'vendor': storage.get('owner'),  # none in 1.2
                # 'description': storage.get('comment'),  # none in 1.2
                'model': storage.get('model'),
                'status': status,
                'serial_number': storage.get('serialNumber'),
                'firmware_version': storage.get('systemVersion'),
                'location': storage.get('location'),
                'total_capacity': total_cap,
                'raw_capacity': raw_cap,  # raw_capacity
                'subscribed_capacity': subscribed_cap,  # subscribed_capacity
                'used_capacity': used_cap,
                'free_capacity': free_cap
            }
        else:
            # If no data is returned, it indicates that there may be a problem with the network or the device.
            # Default return OFFLINE
            s = {
                'status': status
            }
        LOG.info('')
        LOG.info(
            "get_storage successfully ,use time=={}".format((t - time.time())))
        LOG.info('return storage==={}'.format(s))
        return s

    def list_storage_pools(self, context):
        try:
            t = time.time()
            # Get list of Hpe3parStor pool details
            pools = self.restclient.get_all_pools()
            LOG.info('Get list of Hpe3parStor pool details=={}'.format(pools))
            pool_list = []

            if pools is not None:
                LOG.info('Get pool list size:{}'.format(pools.get('total')))
                members = pools.get('members')
                for pool in members:
                    # Get pool status  1=normal 2,3=abnormal 99=offline
                    status = constants.StoragePoolStatus.OFFLINE
                    if pool.get('state') == consts.STATUS_POOL_NORMAL:
                        status = constants.StoragePoolStatus.NORMAL
                    elif (pool.get('state') == consts.STATUS_POOL_DEGRADED
                          or pool.get('state') == consts.STATUS_POOL_FAILED):
                        status = constants.StoragePoolStatus.ABNORMAL

                    # Get pool storage_type   default block
                    pool_type = constants.StorageType.BLOCK
                    """
                    # Total CPG space in MiB
                    total_cap = int(
                        pool.get('totalSpaceMiB')) * consts.MiB_TO_Bytes  # none in 1.2
                    free_cap = int(
                        pool.get('freeSpaceMiB')) * consts.MiB_TO_Bytes  # none in 1.2
                    used_cap = total_cap - free_cap

                    # subscribed_cap rawTotalSpaceMiB
                    subscribed_cap = int(
                        pool.get('rawTotalSpaceMiB')) * consts.MiB_TO_Bytes  # none in 1.2
                    """
                    # count in 1.2
                    usr_used = int(
                        pool['UsrUsage']['usedMiB']) * consts.MiB_TO_Bytes
                    sa_used = int(
                        pool['SAUsage']['usedMiB']) * consts.MiB_TO_Bytes
                    sd_used = int(
                        pool['SDUsage']['usedMiB']) * consts.MiB_TO_Bytes
                    usr_total = int(
                        pool['UsrUsage']['totalMiB']) * consts.MiB_TO_Bytes
                    sa_total = int(
                        pool['SAUsage']['totalMiB']) * consts.MiB_TO_Bytes
                    sd_total = int(
                        pool['SDUsage']['totalMiB']) * consts.MiB_TO_Bytes
                    total_cap = usr_total + sa_total + sd_total
                    used_cap = usr_used + sa_used + sd_used
                    free_cap = total_cap - used_cap
                    usr_subcap = int(
                        pool['UsrUsage']['rawTotalMiB']) * consts.MiB_TO_Bytes
                    sa_subcap = int(
                        pool['SAUsage']['rawTotalMiB']) * consts.MiB_TO_Bytes
                    sd_subcap = int(
                        pool['SDUsage']['rawTotalMiB']) * consts.MiB_TO_Bytes
                    subscribed_cap = usr_subcap + sa_subcap + sd_subcap

                    p = {
                        'name': pool.get('name'),
                        'storage_id': self.storage_id,
                        'native_storage_pool_id': pool.get('id'),
                        'description': 'Hpe 3parStor CPG:' + pool.get('name'),
                        'status': status,
                        'storage_type': pool_type,
                        'total_capacity': total_cap,
                        'subscribed_capacity': subscribed_cap,
                        # rawTotalSpaceMiB
                        'used_capacity': used_cap,
                        'free_capacity': free_cap
                    }
                    pool_list.append(p)

                LOG.info('')
                LOG.info(
                    "list_storage_pools successfully ,use time=={}".format(
                        (t - time.time())))
                LOG.info('return pool list==={}'.format(pool_list))
            return pool_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from Hpe3parStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from Hpe3parStor')

    def list_volumes(self, context):
        try:
            t = time.time()
            # Get all volumes in Hpe3parStor
            volumes = self.restclient.get_all_volumes()
            LOG.info(
                'Get list of Hpe3parStor volumes details=={}'.format(volumes))

            volume_list = []

            if volumes is not None:
                LOG.info(
                    'Get volumes list size:{}'.format(volumes.get('total')))
                members = volumes.get('members')
                for volume in members:
                    status = constants.StoragePoolStatus.OFFLINE
                    if volume.get('state') == consts.STATUS_VOLUME_NORMAL:
                        status = constants.StoragePoolStatus.NORMAL
                    elif (volume.get('state') == consts.STATUS_VOLUME_DEGRADED
                          or volume.get('state') == consts.STATUS_VOLUME_FAILED):
                        status = constants.StoragePoolStatus.ABNORMAL

                    # Get CPG name CPG name from which the user space is allocated.
                    # /CPG name from which the snapshot (snap and admin) space is allocated.
                    # userCPG snapCPG maybe not exist
                    orig_pool_id = ''
                    if 'userCPG' in volume and 'snapCPG' in volume:
                        orig_pool_id = volume.get('userCPG') + '/' + volume.get(
                            'snapCPG')

                    compressed = True
                    # if volume.get(
                    #         'compressionState') == consts.STATUS_COMPRESSION_YES:  # none in 1.2
                    #     compressed = True

                    deduplicated = True
                    # if volume.get(
                    #         'deduplicationState') == consts.STATUS_DEDUPLICATIONSTATE_YES:  # none in 1.2
                    #     deduplicated = True

                    vol_type = constants.VolumeType.THICK
                    if volume.get('provisioningType') == consts.THIN_LUNTYPE:
                        vol_type = constants.VolumeType.THIN

                    # Virtual size of volume in MiB (10242bytes).
                    """
                    total_cap = int(volume.get(
                        'sizeMiB')) * consts.MiB_TO_Bytes
                    # Total used space. Sum of used UserSpace and used Snapshot space
                    used_cap = int(volume.get(
                        'totalUsedMiB')) * consts.MiB_TO_Bytes  # none in 1.2
                    free_cap = total_cap - used_cap
                    """
                    # 1.2
                    usr_used = int(
                        volume['userSpace']['usedMiB']) * consts.MiB_TO_Bytes
                    admin_used = int(
                        volume['adminSpace']['usedMiB']) * consts.MiB_TO_Bytes
                    snap_used = int(
                        volume['snapshotSpace']['usedMiB']) * consts.MiB_TO_Bytes
                    usr_total = int(
                        volume['userSpace']['reservedMiB']) * consts.MiB_TO_Bytes
                    admin_total = int(
                        volume['adminSpace']['reservedMiB']) * consts.MiB_TO_Bytes
                    snap_total = int(
                        volume['snapshotSpace']['reservedMiB']) * consts.MiB_TO_Bytes
                    total_cap = usr_total + admin_total + snap_total
                    used_cap = usr_used + admin_used + snap_used
                    free_cap = total_cap - used_cap

                    v = {
                        'name': volume.get('name'),
                        'storage_id': self.storage_id,
                        'description': volume.get('comment'),  # none in 1.2
                        'status': status,
                        'native_volume_id': volume.get('id'),
                        'native_storage_pool_id': orig_pool_id,
                        'wwn': volume.get('wwn'),
                        'type': vol_type,
                        'total_capacity': total_cap,
                        'used_capacity': used_cap,
                        'free_capacity': free_cap,
                        'compressed': compressed,
                        'deduplicated': deduplicated
                    }
                    volume_list.append(v)
                LOG.info('')
                LOG.info(
                    "list_volumes() successfully,use time=={}".format(
                        (t - time.time())))
                LOG.info('return volumes list==={}'.format(volume_list))
            return volume_list

        except Exception as err:
            LOG.error(
                "Failed to get list volumes from Hpe3parStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get list volumes from Hpe3parStor')

    def list_alerts(self, context):
        try:
            t = time.time()
            # Get list of Hpe3parStor alerts

            alert_list = []
            try:
                commandStr = ComponentHandler.HPE3PAR_COMMAND_SHOWALERT
                reslist = self.sshclient.doexec(context, commandStr)
                # print (reslist)
            except Exception as e:
                LOG.error(e)
                raise exception.StorageBackendException(
                    reason='Failed to ssh Hpe3parStor')
            device_alert_sn = ''
            alarm_id = ''
            state = 1
            alarm_name = ''
            severity = 4
            event_type = ''
            occur_time = ''
            probable_cause = ''
            # print (len(reslist))
            alertlist = reslist.split('\n')
            # print(alertlist)
            for alertinfo in alertlist:
                # print(alertinfo)
                strline = alertinfo
                if strline is not None and strline != '':
                    strline = strline.replace(" ", "")
                    strinfo = strline.split(':', 1)
                    if strinfo[0] == 'Id':
                        device_alert_sn = strinfo[1]
                        alarm_id = strinfo[1]
                    elif strinfo[0] == 'State':
                        if strinfo[1] == 'New':
                            state = 1
                        elif strinfo[1] == 'ACKED':
                            state = 2
                        elif strinfo[1] == 'FIXED':
                            state = 3
                        elif strinfo[1] == 'UNKNOWN':
                            state = 99
                    elif strinfo[0] == 'MessageCode':
                        alarm_name = strinfo[1]
                    elif strinfo[0] == 'Time':
                        occur_time = strinfo[1]
                    elif strinfo[0] == 'Severity':
                        if strinfo[1] == 'Major':
                            severity = 2
                        elif strinfo[1] == 'Minor':
                            severity = 3
                        elif strinfo[1] == 'Critical':
                            severity = 1
                    elif strinfo[0] == 'Type':
                        event_type = strinfo[1]
                    elif strinfo[0] == 'Message':
                        probable_cause = strinfo[1]
                        alert_model = {
                            'category': state,
                            'event_type': event_type,
                            'severity': severity,
                            'probable_cause': probable_cause,
                            'occur_time': occur_time,
                            'alarm_id': alarm_id,
                            'alarm_name': alarm_name,
                            'device_alert_sn': device_alert_sn
                        }
                        # print (alert_model)
                        alert_list.append(alert_model)
                        device_alert_sn = ''
                        alarm_id = ''
                        state = 1
                        alarm_name = ''
                        severity = 4
                        event_type = ''
                        occur_time = ''
                        probable_cause = ''
                        # print(alert_model)
            """
            alerts = self.restclient.get_all_alerts()
            LOG.info(
                'Get list of Hpe3parStor alerts details=={}'.format(alerts))
            alert_list = []

            if alerts is not None:
                LOG.info('Get alerts list size:{}'.format(alerts.get('total')))
                members = alerts.get('members')
                for alert in members:
                    # Get pool status  1=normal 2,3=abnormal 99=offline
                    state = consts.ALERT_STATE_NEW
                    if alert.get('state') == consts.ALERT_STATE_ACKED:
                        state = 5
                    elif alert.get('state') == consts.ALERT_STATE_FIXED:
                        state = 2
                    elif alert.get('state') == consts.ALERT_STATE_UNKNOWN:
                        state = 7

                    severity = consts.ALERT_SEVERITY_DEGRADED
                    if alert.get('severity') == consts.ALERT_SEVERITY_CRITICAL:
                        severity = 1
                    elif alert.get('severity') == consts.ALERT_SEVERITY_MAJOR:
                        severity = 2
                    elif alert.get('state') == consts.ALERT_SEVERITY_MINOR:
                        severity = 3

                    alert_model = {
                        # 'me_dn': alert.get('name'),
                        # 'me_name': alert.get('name'),
                        # 'manufacturer': alert.get('name'),
                        # 'product_name': alert.get('name'),

                        'category': state,
                        # state  Table 18: alert state enumeration
                        'location': alert.get('component'),  # component
                        'event_type': alert.get('type'),  # type
                        'severity': severity,  # severity
                        'probable_cause': alert.get('description'),  # details
                        'me_category': alert_handler.AlertHandler.default_me_category,
                        # component
                        'occur_time': alert.get('timeSecs'),
                        # self.getTimeStamp(alert.get('timeOccurred'))
                        'alarm_id': alert.get('alertInfo').get('alertId'),
                        # id
                        'alarm_name': alert.get('alertInfo').get(
                            'messageCode'),  # messageCode  description
                        'device_alert_sn': alert.get('alertInfo').get(
                            'alertId'),  # id

                        # 'clear_type': alert.get('name'),
                        # 'match_key': alert.get('name'),
                        # 'native_me_dn': alert.get('name')
                    }
                    alert_list.append(alert_model)

                LOG.info('')
                LOG.info(
                    "list_storage_alerts successfully ,use time=={}".format(
                        (t - time.time())))
                LOG.info('return alert list==={}'.format(alert_list))
            """
            # print (alert_list)
            return alert_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from Hpe3parStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from Hpe3parStor')
