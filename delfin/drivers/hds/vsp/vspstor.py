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
from delfin.common import constants
from delfin.drivers import driver
from delfin import exception
from delfin.drivers.hds.vsp import rest_client, alert_handler
from delfin.drivers.utils.ssh_client import SSHClient
from delfin.drivers.hds.vsp import consts
from delfin import context

LOG = log.getLogger(__name__)


class HdsVspDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.restclient = rest_client.RestClient(**kwargs)
        self.restclient.login()
        self.sshclient = SSHClient(**kwargs)
        self.sshclient.login(context)

    def get_storage(self, context):

        specificjson = self.restclient.get_specific_storage()
        summaryjson = self.restclient.get_summary_storage()
        capacityjson = self.restclient.get_capacity()

        # Get status
        status = constants.StorageStatus.OFFLINE
        if specificjson is not None:
            status = consts.StorageStatus.NORMAL

        s = {
            'name': summaryjson["name"],
            'vendor': 'Hitachi',
            'description': 'Hitachi VSP Storage',
            'model': specificjson["model"],
            'status': status,
            'serial_number': specificjson["serialNumber"],
            'firmware_version': '',
            'location': '',
            'raw_capacity': capacityjson["internal"]["totalCapacity"] * consts.KB_TO_Bytes,
            'subscribed_capacity': capacityjson["internal"]["totalCapacity"] * consts.KB_TO_Bytes -
            capacityjson["internal"]["freeSpace"] * consts.KB_TO_Bytes,
            'total_capacity': capacityjson["total"]["totalCapacity"] * consts.KB_TO_Bytes,
            'used_capacity': capacityjson["total"]["totalCapacity"] * consts.KB_TO_Bytes -
            capacityjson["total"]["freeSpace"] * consts.KB_TO_Bytes,
            'free_capacity': capacityjson["total"]["freeSpace"] * consts.KB_TO_Bytes
        }
        LOG.info("get_storage(), successfully retrieved storage details")
        return s

    def list_storage_pools(self, context):
        try:
            # Get list of OceanStor pool details
            poolsinfo = self.restclient.get_all_pools()

            pool_list = []
            if poolsinfo is not None:
                pools = poolsinfo.get('data')
            else:
                return pool_list

            for pool in pools:
                # Get pool status
                status = consts.StoragePoolStatus.OFFLINE
                if pool['poolStatus'] == consts.STATUS_POOL_ONLINE:
                    status = consts.StoragePoolStatus.NORMAL

                # Get pool storage_type
                storage_type = consts.StorageType.FILE
#                if pool.get('poolType') == consts.FILE_SYSTEM_POOL_TYPE:
#                    storage_type = constants.StorageType.FILE

                total_cap = \
                    int(pool['totalPoolCapacity']) * consts.MiB_TO_Bytes
                free_cap = \
                    int(pool['availableVolumeCapacity']) * consts.MiB_TO_Bytes
                used_cap = total_cap - free_cap
                subscribed_capacity = int(pool['totalLocatedCapacity']) * consts.MiB_TO_Bytes
#                        * (int(pool['usedLocatedCapacityRate']) * 0.01)

                p = {
                    'name': pool['poolName'],
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': pool['poolId'],
                    'description': 'Hitachi VSP Pool',
                    'status': status,
                    'storage_type': storage_type,
                    'subscribed_capacity': subscribed_capacity,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                }
                pool_list.append(p)

            return pool_list

        except Exception as err:
            LOG.error(
                "Failed to get pool metrics from hdsvspttor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get pool metrics from hdsvspttor')

    def list_volumes(self, context):
        try:
            # Get all volumes
            wwn = ''
            volumesinfo = self.restclient.get_all_volumes()
            """
            portsinfo = self.restclient.get_ports()
            if portsinfo is not None:
                #volumes = volumesinfo.get('data')
                for port in portsinfo.get('data'):
                    if 'wwn' in port:
                        if wwn is None:
                            wwn = '''%s''' % (port['wwn'])
                        else:
                            wwn = '''%s,%s''' % (wwn, port['wwn'])
            """

            volume_list = []
            if volumesinfo is not None:
                volumes = volumesinfo.get('data')
            else:
                return volume_list

            for volume in volumes:
                orig_pool_id = volume['poolId']

                compressed = False
                deduplicated = False
                if volume['dataReductionMode'] == 'compression_deduplication':
                    deduplicated = True
                    compressed = True
                if volume['dataReductionMode'] == 'compression':
                    compressed = True

                status = 'offline'
                if volume['status'] == 'NML':
                    status = 'normal'

                for port in volume['ports']:
                    if 'wwn' in port:
                        if wwn is None:
                            wwn = '''%s''' % (port['wwn'])
                        else:
                            wwn = '''%s,%s''' % (wwn, port['wwn'])

                vol_type = consts.VolumeType.THICK
                for voltype in volume['attributes']:
                    if voltype == 'HTI':
                        vol_type = consts.VolumeType.THIN

                total_cap = int(volume['blockCapacity']) * consts.Block_Size
                used_cap = int(volume['numOfUsedBlock']) * consts.Block_Size
                free_cap = total_cap - used_cap

                v = {
                    'name': volume['label'],
                    'storage_id': self.storage_id,
                    'description': 'Hitachi VSP volume',
                    'status': status,
                    'native_volume_id': volume['ldevId'],
                    'native_storage_pool_id': orig_pool_id,
                    'wwn': wwn,
                    'type': vol_type,
                    'total_capacity': total_cap,
                    'used_capacity': used_cap,
                    'free_capacity': free_cap,
                    'compressed': compressed,
                    'deduplicated': deduplicated,
                }

                volume_list.append(v)

            return volume_list

        except Exception as err:
            LOG.error(
                "Failed to get list volumes from OceanStor: {}".format(err))
            raise exception.StorageBackendException(
                reason='Failed to get list volumes from hitachi')

    def list_alerts(self, context):
        alertsinfo = self.restclient.get_alerts()
        alert_list = []
        if alertsinfo is not None:
            alerts = alertsinfo.get('data')
        else:
            return alert_list

        for alert in alerts:
            if alert['errorLevel'] == 'Moderate':
                alert_level = 4
            elif alert['errorLevel'] == 'Error ':
                alert_level = 2
            elif alert['errorLevel'] == 'Acute ':
                alert_level = 1

            a = {
                'location': alert['location'],
                'alarm_id': alert['alertId'],
                'device_alert_sn': alert['alertIndex'],
                'probable_cause': alert['errorDetail'],
                'occur_time': alert['occurenceTime'],
                'severity': alert_level,
            }
            alert_list.append(a)

        return alert_list

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def parse_alert(self, context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, alert):
        return alert_handler.AlertHandler().clear_alert(context, self.sshclient, alert)
