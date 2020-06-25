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


class Example1Exporter(base_exporter.BaseExampleExporter):
    def __init__(self):
        """Do some initialization"""
        LOG.info("Init Example1Exporter ...")

    def dispatch_data(self, data):
        LOG.info("Example1: report data ...")
        for name, value in sorted(data.items()):
            LOG.info("example1: %s = %s" % (name, value))

    def dispatch_alert_model(self, alert_model):
        LOG.info("\nExample1Exporter: Exported Alert model..")
        for name, value in sorted(alert_model.items()):
            LOG.info("%s = %s" % (name, value))


class Example2Exporter(base_exporter.BaseExampleExporter):
    def __init__(self):
        """Do some initialization"""
        LOG.info("Init Example2Exporter ...")

    def dispatch_data(self, data):
        LOG.info("Example2: report data ...")
        for name, value in sorted(data.items()):
            LOG.info("example2: %s = %s" % (name, value))

    def dispatch_alert_model(self, alert_model):
        LOG.info("\nExample2Exporter: Exported Alert model..")
        for name, value in sorted(alert_model.items()):
            LOG.info("%s = %s" % (name, value))
