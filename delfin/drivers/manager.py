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
import six
import stevedore
import threading

from oslo_log import log

from delfin import db
from delfin import exception
from delfin import utils
from delfin import ssl_utils
from delfin.common import constants

LOG = log.getLogger(__name__)


@six.add_metaclass(utils.Singleton)
class DriverManager(stevedore.ExtensionManager):
    _instance_lock = threading.Lock()
    NAMESPACE = 'delfin.storage.drivers'

    def __init__(self):
        super(DriverManager, self).__init__(self.NAMESPACE)
        # The driver_factory will keep the driver instance for
        # each of storage systems so that the session between driver
        # and storage system is effectively used.
        self.driver_factory = dict()

    def get_driver(self, context, invoke_on_load=True,
                   cache_on_load=True, **kwargs):
        """Get a driver from manager.

        :param context: The context of delfin.
        :type context: delfin.context.RequestContext
        :param invoke_on_load: Boolean to decide whether to return the
            driver object.
        :type invoke_on_load: bool
        :param cache_on_load: Boolean to decide whether save driver object
            in driver_factory when generating a new driver object.
            It takes effect when invoke_on_load is True.
        :type cache_on_load: bool
        :param kwargs: Parameters from access_info.
        """
        context.storage_id = kwargs.get('storage_id')
        kwargs = copy.deepcopy(kwargs)
        kwargs['verify'] = False
        ca_path = ssl_utils.get_storage_ca_path()
        if ca_path:
            ssl_utils.verify_ca_path(ca_path)
            kwargs['verify'] = ca_path

        if not invoke_on_load:
            return self._get_driver_cls(**kwargs)
        else:
            return self._get_driver_obj(context, cache_on_load, **kwargs)

    def update_driver(self, storage_id, driver):
        self.driver_factory[storage_id] = driver

    def remove_driver(self, storage_id):
        """Clear driver instance from driver factory."""
        self.driver_factory.pop(storage_id, None)

    def _get_driver_obj(self, context, cache_on_load=True, **kwargs):
        if not cache_on_load or not kwargs.get('storage_id'):
            if kwargs['verify']:
                ssl_utils.reload_certificate(kwargs['verify'])
            cls = self._get_driver_cls(**kwargs)
            return cls(**kwargs)

        if kwargs['storage_id'] in self.driver_factory:
            return self.driver_factory[kwargs['storage_id']]

        with self._instance_lock:
            if kwargs['storage_id'] in self.driver_factory:
                return self.driver_factory[kwargs['storage_id']]

            if kwargs['verify']:
                ssl_utils.reload_certificate(kwargs['verify'])

            access_info = copy.deepcopy(kwargs)
            storage_id = access_info.pop('storage_id')
            access_info.pop('verify')
            if access_info:
                cls = self._get_driver_cls(**kwargs)
                driver = cls(**kwargs)
            else:
                access_info = db.access_info_get(
                    context, storage_id).to_dict()

                access_info_dict = copy.deepcopy(access_info)
                remove_fields = ['created_at', 'updated_at',
                                 'storage_id', 'storage_name',
                                 'extra_attributes']
                # Remove unrelated query fields
                for field in remove_fields:
                    if access_info_dict.get(field):
                        access_info_dict.pop(field)
                for access in constants.ACCESS_TYPE:
                    if access_info_dict.get(access):
                        access_info_dict.pop(access)

                access_info_list = db.access_info_get_all(
                    context, filters=access_info_dict)
                for _access_info in access_info_list:
                    if _access_info['storage_id'] in self.driver_factory:
                        driver = self.driver_factory[
                            _access_info['storage_id']]
                        driver.add_storage(access_info)
                        self.driver_factory[storage_id] = driver
                        return driver
                access_info['verify'] = kwargs.get('verify')
                cls = self._get_driver_cls(**access_info)
                driver = cls(**access_info)

            self.driver_factory[storage_id] = driver
            return driver

    def _get_driver_cls(self, **kwargs):
        """Get driver class from entry points."""
        name = '%s %s' % (kwargs.get('vendor'), kwargs.get('model'))
        if name in self.names():
            return self[name].plugin

        msg = "Storage driver '%s' could not be found." % name
        LOG.error(msg)
        raise exception.StorageDriverNotFound(name)
