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
from delfin.exporter import base_exporter

LOG = log.getLogger(__name__)


class AlertExporterExample(base_exporter.BaseExporter):
    def dispatch(self, ctxt, data):
        LOG.info("AlertExporterExample, report data: %s" % data)


class PerformanceExporterExample(base_exporter.BaseExporter):
    def dispatch(self, ctxt, data):
        LOG.info("PerformanceExporterExample, report data: %s" % data)
