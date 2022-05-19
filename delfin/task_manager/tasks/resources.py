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

import inspect

import decorator
from oslo_log import log

from delfin import coordination
from delfin import db
from delfin import exception
from delfin.common import constants
from delfin.drivers import api as driverapi
from delfin.i18n import _

LOG = log.getLogger(__name__)


def set_synced_after():
    @decorator.decorator
    def _set_synced_after(func, *args, **kwargs):
        call_args = inspect.getcallargs(func, *args, **kwargs)
        self = call_args['self']
        sync_result = constants.ResourceSync.SUCCEED
        ret = None
        try:
            ret = func(*args, **kwargs)
        except Exception:
            sync_result = constants.ResourceSync.FAILED
        lock = coordination.Lock(self.storage_id)
        with lock:
            try:
                storage = db.storage_get(self.context, self.storage_id)
            except exception.StorageNotFound:
                LOG.warn('Storage %s not found when set synced'
                         % self.storage_id)
            else:
                # One sync task done, sync status minus 1
                # When sync status get to 0
                # means all the sync tasks are completed
                if storage['sync_status'] != constants.SyncStatus.SYNCED:
                    storage['sync_status'] -= sync_result
                    db.storage_update(self.context, self.storage_id,
                                      {'sync_status': storage['sync_status']})

        return ret

    return _set_synced_after


def check_deleted():
    @decorator.decorator
    def _check_deleted(func, *args, **kwargs):
        call_args = inspect.getcallargs(func, *args, **kwargs)
        self = call_args['self']
        ret = func(*args, **kwargs)
        # When context.read_deleted is 'yes', db.storage_get would
        # only get the storage whose 'deleted' tag is not default value
        self.context.read_deleted = 'yes'
        try:
            db.storage_get(self.context, self.storage_id)
        except exception.StorageNotFound:
            LOG.debug('Storage %s not found when checking deleted'
                      % self.storage_id)
        else:
            self.remove()
        self.context.read_deleted = 'no'
        return ret

    return _check_deleted


class StorageResourceTask(object):
    NATIVE_RESOURCE_ID = None

    def __init__(self, context, storage_id):
        self.storage_id = storage_id
        self.context = context
        self.driver_api = driverapi.API()

    def _classify_resources(self, storage_resources, db_resources, key):
        """
        :param storage_resources:
        :param db_resources:
        :return: it will return three list add_list: the items present in
        storage but not in current_db. update_list:the items present in
        storage and in current_db. delete_id_list:the items present not in
        storage but present in current_db.
        """
        original_ids_in_db = [resource[key]
                              for resource in db_resources]
        delete_id_list = [resource['id'] for resource in db_resources]
        add_list = []
        update_list = []

        for resource in storage_resources:
            if resource[key] in original_ids_in_db:
                resource['id'] = db_resources[original_ids_in_db.index(
                    resource[key])]['id']
                delete_id_list.remove(resource['id'])
                update_list.append(resource)
            else:
                add_list.append(resource)

        return add_list, update_list, delete_id_list

    @check_deleted()
    @set_synced_after()
    def sync(self):
        """
        Synchronizing device resources data to database.
        """
        LOG.info('{} sync for storage(id={}) start'.format(
            self.__class__.__name__, self.storage_id))
        try:
            # list the storage resources from driver and database
            storage_resources = self.driver_list_resources()
            db_resources = self.db_resource_get_all(
                {'storage_id': self.storage_id})

            add_list, update_list, delete_id_list = self._classify_resources(
                storage_resources, db_resources, self.NATIVE_RESOURCE_ID)

            if delete_id_list:
                self.db_resources_delete(delete_id_list)

            if update_list:
                self.db_resources_update(update_list)

            if add_list:
                self.db_resources_create(add_list)
        except NotImplementedError:
            # Ignore this exception because driver may not support it.
            pass
        except Exception as e:
            msg = _('{} sync for storage(id={}) failed: {}'.format(
                self.__class__.__name__, self.storage_id, e))
            LOG.error(msg)
            raise
        else:
            LOG.info('{} sync for storage(id={}) successful'.format(
                self.__class__.__name__, self.storage_id))

    def remove(self):
        LOG.info('{} remove for storage(id={})'.format(
            self.__class__.__name__, self.storage_id))
        self.db_resource_delete_by_storage()

    def driver_list_resources(self):
        raise NotImplementedError(
            'Resource task API driver_list_resources() is not implemented')

    def db_resource_get_all(self, filters):
        raise NotImplementedError(
            'Resource task API db_resource_get_all() is not implemented')

    def db_resources_delete(self, delete_id_list):
        raise NotImplementedError(
            'Resource task API db_resources_delete() is not implemented')

    def db_resources_update(self, update_list):
        raise NotImplementedError(
            'Resource task API db_resources_update() is not implemented')

    def db_resources_create(self, add_list):
        raise NotImplementedError(
            'Resource task API db_resources_create() is not implemented')

    def db_resource_delete_by_storage(self):
        raise NotImplementedError(
            'Resource task API db_resource_delete_by_storage() '
            'is not implemented')


class StorageDeviceTask(StorageResourceTask):
    def __init__(self, context, storage_id):
        super(StorageDeviceTask, self).__init__(context, storage_id)

    @check_deleted()
    @set_synced_after()
    def sync(self):
        """
        :return:
        """
        LOG.info('Syncing storage device for storage id:{0}'.format(
            self.storage_id))
        try:
            storage = self.driver_api.get_storage(self.context,
                                                  self.storage_id)

            db.storage_update(self.context, self.storage_id, storage)
        except Exception as e:
            msg = _('Failed to update storage entry in DB: {0}'
                    .format(e))
            LOG.error(msg)
            raise
        else:
            LOG.info("Syncing storage successful!!!")

    def remove(self):
        LOG.info('Remove storage device for storage id:{0}'
                 .format(self.storage_id))
        try:
            db.storage_delete(self.context, self.storage_id)
            db.access_info_delete(self.context, self.storage_id)
            db.alert_source_delete(self.context, self.storage_id)
        except Exception as e:
            LOG.error('Failed to update storage entry in DB: {0}'.format(e))


class StoragePoolTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_storage_pool_id'

    def driver_list_resources(self):
        return self.driver_api.list_storage_pools(
            self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.storage_pool_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.storage_pools_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.storage_pools_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.storage_pools_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.storage_pool_delete_by_storage(self.context, self.storage_id)


class StorageVolumeTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_volume_id'

    def driver_list_resources(self):
        return self.driver_api.list_volumes(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.volume_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.volumes_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.volumes_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.volumes_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.volume_delete_by_storage(self.context, self.storage_id)


class StorageControllerTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_controller_id'

    def driver_list_resources(self):
        return self.driver_api.list_controllers(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.controller_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.controllers_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.controllers_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.controllers_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.controller_delete_by_storage(self.context, self.storage_id)


class StoragePortTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_port_id'

    def driver_list_resources(self):
        return self.driver_api.list_ports(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.port_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.ports_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.ports_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.ports_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.port_delete_by_storage(self.context, self.storage_id)


class StorageDiskTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_disk_id'

    def driver_list_resources(self):
        return self.driver_api.list_disks(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.disk_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.disks_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.disks_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.disks_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.disk_delete_by_storage(self.context, self.storage_id)


class StorageQuotaTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_quota_id'

    def driver_list_resources(self):
        return self.driver_api.list_quotas(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.quota_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.quotas_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.quotas_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.quotas_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.quota_delete_by_storage(self.context, self.storage_id)


class StorageFilesystemTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_filesystem_id'

    def driver_list_resources(self):
        return self.driver_api.list_filesystems(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.filesystem_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.filesystems_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.filesystems_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.filesystems_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.filesystem_delete_by_storage(self.context, self.storage_id)


class StorageQtreeTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_qtree_id'

    def driver_list_resources(self):
        return self.driver_api.list_qtrees(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.qtree_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.qtrees_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.qtrees_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.qtrees_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.qtree_delete_by_storage(self.context, self.storage_id)


class StorageShareTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_share_id'

    def driver_list_resources(self):
        return self.driver_api.list_shares(self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.share_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.shares_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.shares_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.shares_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.share_delete_by_storage(self.context, self.storage_id)


class StorageHostInitiatorTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_storage_host_initiator_id'

    def driver_list_resources(self):
        return self.driver_api.list_storage_host_initiators(
            self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.storage_host_initiators_get_all(
            self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.storage_host_initiators_delete(
            self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.storage_host_initiators_update(
            self.context, update_list)

    def db_resources_create(self, add_list):
        return db.storage_host_initiators_create(
            self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.storage_host_initiators_delete_by_storage(
            self.context, self.storage_id)


class StorageHostTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_storage_host_id'

    def driver_list_resources(self):
        return self.driver_api.list_storage_hosts(
            self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.storage_hosts_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.storage_hosts_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.storage_hosts_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.storage_hosts_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.storage_hosts_delete_by_storage(
            self.context, self.storage_id)


class StorageHostGroupTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_storage_host_group_id'

    def driver_list_resources(self):
        hg_obj = self.driver_api.list_storage_host_groups(
            self.context, self.storage_id)
        storage_host_groups = hg_obj['storage_host_groups']
        storage_host_rels = hg_obj['storage_host_grp_host_rels']
        if storage_host_groups:
            db.storage_host_grp_host_rels_delete_by_storage(
                self.context, self.storage_id)
            db.storage_host_grp_host_rels_create(
                self.context, storage_host_rels)
            LOG.info('Building host group relations successful for '
                     'storage id:{0}'.format(self.storage_id))
        return storage_host_groups

    def db_resource_get_all(self, filters):
        return db.storage_host_groups_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.storage_host_groups_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.storage_host_groups_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.storage_host_groups_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        db.storage_host_grp_host_rels_delete_by_storage(
            self.context, self.storage_id)
        return db.storage_host_groups_delete_by_storage(
            self.context, self.storage_id)


class PortGroupTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_port_group_id'

    def driver_list_resources(self):
        pg_obj = self.driver_api.list_port_groups(
            self.context, self.storage_id)
        port_groups = pg_obj['port_groups']
        port_group_relation_list = pg_obj['port_grp_port_rels']
        if port_groups:
            db.port_grp_port_rels_delete_by_storage(
                self.context, self.storage_id)
            db.port_grp_port_rels_create(
                self.context, port_group_relation_list)
            LOG.info('Building port group relations successful for '
                     'storage id:{0}'.format(self.storage_id))
        return port_groups

    def db_resource_get_all(self, filters):
        return db.port_groups_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.port_groups_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.port_groups_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.port_groups_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        db.port_grp_port_rels_delete_by_storage(
            self.context, self.storage_id)
        return db.port_groups_delete_by_storage(
            self.context, self.storage_id)


class VolumeGroupTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_volume_group_id'

    def driver_list_resources(self):
        vg_obj = self.driver_api.list_volume_groups(
            self.context, self.storage_id)
        volume_groups = vg_obj['volume_groups']
        volume_groups_rels = vg_obj['vol_grp_vol_rels']
        if volume_groups:
            db.vol_grp_vol_rels_delete_by_storage(
                self.context, self.storage_id)
            db.vol_grp_vol_rels_create(self.context, volume_groups_rels)
            LOG.info('Building volume group relations successful for '
                     'storage id:{0}'.format(self.storage_id))
        return volume_groups

    def db_resource_get_all(self, filters):
        return db.volume_groups_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.volume_groups_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.volume_groups_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.volume_groups_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        db.vol_grp_vol_rels_delete_by_storage(
            self.context, self.storage_id)
        return db.volume_groups_delete_by_storage(
            self.context, self.storage_id)


class MaskingViewTask(StorageResourceTask):
    NATIVE_RESOURCE_ID = 'native_masking_view_id'

    def driver_list_resources(self):
        return self.driver_api.list_masking_views(
            self.context, self.storage_id)

    def db_resource_get_all(self, filters):
        return db.masking_views_get_all(self.context, filters=filters)

    def db_resources_delete(self, delete_id_list):
        return db.masking_views_delete(self.context, delete_id_list)

    def db_resources_update(self, update_list):
        return db.masking_views_update(self.context, update_list)

    def db_resources_create(self, add_list):
        return db.masking_views_create(self.context, add_list)

    def db_resource_delete_by_storage(self):
        return db.masking_views_delete_by_storage(
            self.context, self.storage_id)
