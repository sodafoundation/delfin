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


from oslo_config import cfg
from oslo_log import log
import six
from stevedore import extension

from delfin import exception
from delfin.i18n import _

LOG = log.getLogger(__name__)

exporter_opts = [
    cfg.ListOpt('alert_exporters',
                default=['AlertExporterExample'],
                help="Which exporters for alert push."),
    cfg.ListOpt('performance_exporters',
                default=['PerformanceExporterExample'],
                help="Which exporters for performance push."),
]

CONF = cfg.CONF
CONF.register_opts(exporter_opts)


class BaseExporter(object):
    """Base class for data exporter."""

    def dispatch(self, ctxt, data):
        """Dispatch data to the third platforms.
            :param ctxt: delfin.RequestContext
            :param data: The data to be pushed, it's a list with dict item.
            :type data: list
        """
        raise NotImplementedError()


class BaseManager(BaseExporter):
    def __init__(self, namespace):
        self.extension_manager = extension.ExtensionManager(namespace)
        self.exporters = self._get_exporters()

    def dispatch(self, ctxt, data):
        if not isinstance(data, (list, tuple)):
            data = [data]
        for exporter in self.exporters:
            try:
                exporter.dispatch(ctxt, data)
            except exception.DelfinException as e:
                err_msg = _("Failed to export data (%s).") % e.msg
                LOG.exception(err_msg)
            except Exception as e:
                err_msg = six.text_type(e)
                LOG.exception(err_msg)

    def _get_exporters(self):
        """Get exporters from configuration file which
        shall be supported in entry points.
        """
        supported_exporters = self._get_supported_exporters()
        configured_exporters = self._get_configured_exporters()
        return [cls() for cls in supported_exporters
                if cls.__name__ in configured_exporters]

    def _get_supported_exporters(self):
        """Get all supported exporters from entry points file."""
        return [ext.plugin for ext in self.extension_manager]

    def _get_configured_exporters(self):
        """Get exporters from configuration file."""
        raise NotImplementedError()


class AlertExporterManager(BaseManager):
    NAMESPACE = 'delfin.alert.exporters'

    def __init__(self):
        super(AlertExporterManager, self).__init__(self.NAMESPACE)

    def _get_configured_exporters(self):
        return CONF.alert_exporters


class PerformanceExporterManager(BaseManager):
    NAMESPACE = 'delfin.performance.exporters'

    def __init__(self):
        super(PerformanceExporterManager, self).__init__(self.NAMESPACE)

    def _get_configured_exporters(self):
        return CONF.performance_exporters
