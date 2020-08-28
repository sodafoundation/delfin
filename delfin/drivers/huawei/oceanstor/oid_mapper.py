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
    OID_MAP = {
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.1": "hwIsmReportingAlarmNodeCode",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.2": "hwIsmReportingAlarmLocationInfo",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.3": "hwIsmReportingAlarmRestoreAdvice",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.4": "hwIsmReportingAlarmFaultTitle",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.5": "hwIsmReportingAlarmFaultType",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.6": "hwIsmReportingAlarmFaultLevel",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.7": "hwIsmReportingAlarmAlarmID",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.8": "hwIsmReportingAlarmFaultTime",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.9": "hwIsmReportingAlarmSerialNo",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.10": "hwIsmReportingAlarmAdditionInfo",
        "1.3.6.1.4.1.2011.2.91.10.3.1.1.11": "hwIsmReportingAlarmFaultCategory"
    }

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
