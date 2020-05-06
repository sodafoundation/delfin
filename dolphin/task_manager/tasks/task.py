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

from dolphin import exception
from dolphin.drivers import manager as drivermanager
from dolphin.db.sqlalchemy import api as db
from dolphin.i18n import _

LOG = log.getLogger(__name__)


class StorageResourceTask(object):

    def __init__(self, context, storage_id):
        self.storage_id = storage_id
        self.context = context
        self.driver = drivermanager.DriverManager()


class StorageDeviceTask(StorageResourceTask):
    def __init__(self, context, storage_id):
        super(StorageDeviceTask, self).__init__(context, storage_id)

    def sync(self):
        """
        :return:
        """
        LOG.info('syncing storage device for storage id:{0}'.format(self.storage_id))
        try:
            storage = self.driver.get_storage(self.context, self.storage_id)
            # storage['id'] = self.storage_id  ## it is for fake testing
            db.storage_update(self.context, self.storage_id, storage)
        except AttributeError as e:
            LOG.error(e)
            raise exception.DolphinException(e)
        except Exception as e:
            msg = _('Failed to update storage entry in DB: {0}'
                    .format(e))
            LOG.error(msg)
            raise exception.DolphinException(msg)
        LOG.info("syncing storage successful!!!")

    def remove(self):
        pass


class StoragePoolTask(StorageResourceTask):
    def __init__(self, context, storage_id):
        super(StoragePoolTask, self).__init__(context, storage_id)

    def sync(self):
        """
        :return:
        """
        LOG.info('syncing pool for storage id:{0}'.format(self.storage_id))
        try:
            pools = self.driver.list_pools(self.context, self.storage_id)
            db.pool_update(self.context, pools)
        except AttributeError as e:
            LOG.error(e)
            raise exception.DolphinException(e)
        except Exception as e:
            msg = _('Failed to update pool entry in DB: {0}'
                    .format(e))
            LOG.error(msg)
            raise exception.DolphinException(msg)

    def remove(self):
        pass