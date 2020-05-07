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
import stevedore
import threading

from oslo_log import log
from dolphin import exception
from dolphin.i18n import _
from dolphin import utils
from dolphin.drivers import helper

LOG = log.getLogger(__name__)


class DriverManager(metaclass=utils.Singleton):
    _instance_lock = threading.Lock()
    NAMESPACE = 'dolphin.storage.drivers'

    def __init__(self):
        # The driver_factory will keep the driver instance for
        # each of storage systems so that the session between driver
        # and storage system is effectively used.
        self.driver_factory = dict()

    def _create_driver(self, context, **kwargs):
        vendor = kwargs.get('vendor', None)
        model = kwargs.get('model', None)

        try:
            if not vendor or not model:
                access_info = helper.get_access_info(context, kwargs['storage_id'])
                kwargs = copy.deepcopy(access_info)

            driver = stevedore.driver.DriverManager(
                namespace=self.NAMESPACE,
                name='%s %s' % (kwargs['vendor'], kwargs['model']),
                invoke_on_load=True,
                invoke_kwds=kwargs
            ).driver
        except Exception as e:
            msg = (_("Storage driver '%s %s' could not be found.") % (kwargs['vendor'],
                                                                      kwargs['model']))
            LOG.error(e)
            raise exception.StorageDriverNotFound(message=msg)

        return driver

    def get_driver(self, context, **kwargs):
        """
        Caller can get driver with storage_id or vendor&model
        :param context:
        :param kwargs: A dictionary, only storage_id is necessary, for the first
            time to register storage, storage_id is newly created, nothing can be found
            from database with this storage_id, so other access information should be
            included in access_info, otherwise, storage_id can be used to get access
            information from database.
        :return: A driver object.
        """
        storage_id = kwargs.get('storage_id', None)
        if not storage_id:
            raise exception.StorageDriverNotFound(message="storage_id is missed")

        driver = self.driver_factory.get(storage_id, None)
        if not driver:
            with self._instance_lock:
                driver = self.driver_factory.get(storage_id, None)
                if not driver:
                    driver = self._create_driver(context, **kwargs)

        self.driver_factory[storage_id] = driver
        return driver

    def remove_driver(self, context, storage_id):
        """Clear driver instance from driver factory."""
        self.driver_factory.pop(storage_id, None)

    @staticmethod
    def get_storage_registry():
        """Show register parameters which the driver needs."""
        pass
