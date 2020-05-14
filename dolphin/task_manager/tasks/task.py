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
from dolphin.drivers import manager as driver_manager
from dolphin.db.sqlalchemy import api as db
from dolphin.i18n import _
from dolphin.task_manager import rpcapi as task_rpcapi

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
        LOG.info('Remove storage device for storage id:{0}'.format(self.storage_id))
        try:
            db.storage_delete(self.context, self.storage_id)
        except Exception as e:
            LOG.error('Failed to update storage entry in DB: {0}'.format(e))
        else:
            for subclass in StorageResourceInMemoryTask.__subclasses__():
                task_rpcapi.TaskAPI().remove_storage_resource(
                    self.context,
                    self.storage_id,
                    subclass.__module__ + '.' + subclass.__name__
                )


class StoragePoolTask(StorageResourceTask):
    def sync(self):
        pass

    def remove(self):
        LOG.info('Remove pools for storage id:{0}'.format(self.storage_id))
        db.pool_delete(self.context, self.storage_id)


class StorageVolumeTask(StorageResourceTask):
    def sync(self):
        pass

    def remove(self):
        LOG.info('Remove volumes for storage id:{0}'.format(self.storage_id))
        db.volume_delete(self.context, self.storage_id)


class StorageResourceInMemoryTask(object):

    def __init__(self, context, storage_id):
        self.storage_id = storage_id
        self.context = context


class StorageDeviceInMemoryTask(StorageResourceInMemoryTask):
    def sync(self):
        pass

    def remove(self):
        LOG.info('Remove storage device in memory for storage id:{0}'.format(self.storage_id))
        drivers = driver_manager.DriverManager()
        drivers.remove_driver(self.context, self.storage_id)
