# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class OidMapper(object):
    """Functions/attributes for oid to alert info mapper"""

    # Map to translate trap oid strings to oid names
    OID_MAP = {"1.3.6.1.3.94.1.11.1.3": "connUnitEventId",
               "1.3.6.1.3.94.1.11.1.6": "connUnitEventSeverity",
               "1.3.6.1.3.94.1.11.1.7": "connUnitEventType",
               "1.3.6.1.3.94.1.11.1.8": "connUnitEventObject",
               "1.3.6.1.3.94.1.11.1.9": "connUnitEventDescr",
               "1.3.6.1.3.94.1.6.1.20": "connUnitName",
               "1.3.6.1.3.94.1.6.1.3": "connUnitType",
               "1.3.6.1.4.1.1139.3.8888.1.0": "emcAsyncEventSource",
               "1.3.6.1.4.1.1139.3.8888.2.0": "emcAsyncEventCode",
               "1.3.6.1.4.1.1139.3.8888.3.0": "emcAsyncEventComponentType",
               "1.3.6.1.4.1.1139.3.8888.4.0": "emcAsyncEventComponentName"}

    def __init__(self):
        pass

    def map_oids(self, alert):
        """Translate oids using static map."""
        alert_model = dict()

        for attr in alert:
            # Remove the instance number at the end of oid before mapping
            oid_str = attr.rsplit('.', 1)[0]
            key = self.OID_MAP.get(oid_str, None)
            alert_model[key] = alert[attr]

        return alert_model
