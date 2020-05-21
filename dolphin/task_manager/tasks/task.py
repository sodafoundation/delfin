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

    def _classify_pools(self, storage_pools, db_pools):
        """
        :param storage_pools:
        :param db_pools:
        :return: it will return three list add_list: the items present in
        storage but not in current_db. update_list:the items present in
        storage and in current_db. delete_id_list:the items present not in
        storage but present in current_db.
        """
        original_ids_in_db = [pool['original_id'] for pool in db_pools]
        delete_id_list = [pool['id'] for pool in db_pools]
        add_list = []
        update_list = []

        for pool in storage_pools:
            if pool['original_id'] in original_ids_in_db:
                pool['id'] = db_pools[original_ids_in_db.index(
                    pool['original_id'])]['id']
                delete_id_list.remove(pool['id'])
                update_list.append(pool)
            else:
                add_list.append(pool)

        return add_list, update_list, delete_id_list

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

            add_list, update_list, delete_id_list = self._classify_pools(
                storage_pools, db_pools
            )
            db.pools_delete(self.context, delete_id_list)

            db.pools_update(self.context, update_list)

            db.pools_create(self.context, add_list)
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
