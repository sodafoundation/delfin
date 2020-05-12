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
import copy

from oslo_log import log

from dolphin import exception
from dolphin.drivers import api as driverapi
from dolphin.db.sqlalchemy import api as db
from dolphin.i18n import _

LOG = log.getLogger(__name__)


class StorageResourceTask(object):

    def __init__(self, context, storage_id):
        self.storage_id = storage_id
        self.context = context
        self.driver_api = driverapi.API()


class StorageDeviceTask(StorageResourceTask):
    def __init__(self, context, storage_id):
        super(StorageDeviceTask, self).__init__(context, storage_id)

    def sync(self):
        """
        :return:
        """
        LOG.info('Syncing storage device for storage id:{0}'.format(self.storage_id))
        try:
            storage = self.driver_api.get_storage(self.context, self.storage_id)

            db.storage_update(self.context, self.storage_id, storage)
        except AttributeError as e:
            LOG.error(e)
        except Exception as e:
            msg = _('Failed to update storage entry in DB: {0}'
                    .format(e))
            LOG.error(msg)
        else:
            LOG.info("Syncing storage successful!!!")

    def remove(self):
        pass


class StoragePoolTask(StorageResourceTask):
    def __init__(self, context, storage_id):
        super(StoragePoolTask, self).__init__(context, storage_id)

    def _get_delete_list(self, storage_pools, db_pools):
        """
        :param storage_pools:
        :param db_pools:
        :return: prepare the delete_list. It will contain only those pool id
        which is present in db but NOT in current list of storage pools
        """
        delete_list = copy.copy(db_pools)
        [delete_list.remove(d_pool) for s_pool in storage_pools
         for d_pool in db_pools if s_pool.get('original_id') == d_pool.get(
            'original_id')]
        return delete_list

    def _get_add_list(self, storage_pools, db_pools):
        """
        :param storage_pools:
        :param db_pools:
        :return: prepare the add_list. It will contain only those pool id
        which is NOT present in db but in current list of storage pools
        """
        add_list = copy.copy(storage_pools)
        [add_list.remove(s_pool) for s_pool in storage_pools
         for d_pool in db_pools if s_pool.get('original_id') == d_pool.get(
            'original_id')]
        return add_list

    def _get_update_list(self, storage_pools, db_pools):
        """
        :param storage_pools:
        :param db_pools:
        :return: prepare the update_list. It will contain only those pool id
        which is present in db and current list of storage pools
        """
        update_list = []
        [update_list.append(s_pool) for s_pool in storage_pools
         for d_pool in db_pools if s_pool.get('original_id') == d_pool.get(
            'original_id')]
        return update_list

    def sync(self):
        """
        :return:
        """
        LOG.info('Syncing pool for storage id:{0}'.format(self.storage_id))
        try:
            # collect the pools list from driver and database
            storage_pools = self.driver_api.list_pools(self.context,
                                                       self.storage_id)
            db_pools = db.pool_get_all(self.context)

            db.pools_delete(self.context, self._get_delete_list(
                storage_pools, db_pools))

            db.pools_update(self.context, self._get_update_list(
                storage_pools, db_pools))

            db.pools_create(self.context, self._get_add_list(
                storage_pools, db_pools))
        except AttributeError as e:
            LOG.error(e)
        except Exception as e:
            msg = _('Failed to sync pools entry in DB: {0}'
                    .format(e))
            LOG.error(msg)
        else:
            LOG.info("Syncing pools successful!!!")

    def remove(self):
        pass
