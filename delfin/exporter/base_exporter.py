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

import threading

from stevedore import extension
from oslo_log import log

LOG = log.getLogger(__name__)


class ExportManager(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __init_manager(self):
        self.export_manager = extension.ExtensionManager(
            namespace='resource.exporter',
            invoke_on_load=True,
        )

    def __new__(cls, *args, **kwargs):
        if not hasattr(ExportManager, "_instance"):
            with ExportManager._instance_lock:
                if not hasattr(ExportManager, "_instance"):
                    ExportManager._instance = object.__new__(cls)
                    ExportManager._instance.__init_manager()
        return ExportManager._instance


def _dispatch_example(ext, data):
    ext.obj.dispatch_data(data)


# Task can call this function to report example data.
def dispatch_example_data(data):
    """
        :param data: Resource data.
        :type data: dict
        Redefine this in child classes.
    """
    export_manager = ExportManager().export_manager
    export_manager.map(_dispatch_example, data)


class BaseExampleExporter(object):
    """Base class for example exporter."""

    def dispatch_data(self, data):
        """Dispatch data to north bound platforms.
            :param data: Resource data.
            :type data: dict
            Redefine this in child classes.
        """
        raise NotImplementedError
