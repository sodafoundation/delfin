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
import jsonschema

from oslo_log import log

from delfin import db
from delfin import exception
from delfin import utils
from delfin import ssl_utils
from delfin import context
from delfin.drivers.helper import empty_driver_capabilities
from delfin.drivers.driver_spec_schema import DRIVER_SPECIFICATION_SCHEMA

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
        self._validate_driver_spec()

    def _validate_driver_spec(self):
        for name in self.names():
            driver_cls = self[name].plugin
            spec = driver_cls.get_capabilities(
                context=context.RequestContext(is_admin=True))

            # in case get_capabilities not implemented
            if spec is None:
                # update list_resource_metrics to return empty
                self._add_default_capabilities(driver_cls)
                self.alert_driver_error(
                    driver_cls, "Driver's capability list is empty "
                                "for %s" % name)
            try:
                jsonschema.validate(spec, DRIVER_SPECIFICATION_SCHEMA)
            except jsonschema.ValidationError as ex:
                if isinstance(ex.cause, exception.InvalidName):
                    detail = "An invalid 'name' value was provided " \
                             "in capability list"
                elif len(ex.path) > 0:
                    detail = "Invalid input for capability list " \
                             "configured in field/attribute %(path)s." \
                             " %(message)s" % {'path': ex.path.pop(),
                                               'message': ex.message}
                else:
                    detail = ex.message
                # update list_resource_metrics to return empty
                self._add_default_capabilities(driver_cls)
                self.alert_driver_error(driver_cls, detail)
            except TypeError as ex:
                # update list_resource_metrics to return empty
                self._add_default_capabilities(driver_cls)

                # NOTE: If passing non string value to patternProperties
                # parameter, TypeError happens. Here is for catching
                # the TypeError.
                detail = six.text_type(ex)
                self.alert_driver_error(driver_cls, detail)

    def alert_driver_error(self, driver_cls, msg):
        LOG.warning(msg)
        # FIXME (Amit): Add Alert for driver's error
        #   Also enable feature flag to make Northbound API aware
        return

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

    @staticmethod
    def _add_default_capabilities(driver_cls):
        driver_cls.get_capabilities = \
            staticmethod(empty_driver_capabilities)
