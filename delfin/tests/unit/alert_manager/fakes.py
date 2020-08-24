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

from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher

from delfin import exception
from delfin.common import constants


def fake_storage_info():
    return {
        'id': 'abcd-1234-56789',
        'name': 'storage1',
        'vendor': 'fake vendor',
        'model': 'fake model',
        'serial_number': 'serial-1234',
    }


def fake_alert_model():
    return {'alert_id': '1050',
            'alert_name': 'SAMPLE_ALERT_NAME',
            'severity': constants.Severity.WARNING,
            'category': constants.Category.NOT_SPECIFIED,
            'type': constants.EventType.EQUIPMENT_ALARM,
            'sequence_number': 79,
            'description': 'Diagnostic event trace triggered.',
            'recovery_advice': 'NA',
            'resource_type': constants.DEFAULT_RESOURCE_TYPE,
            'location': 'Array id=000192601409,Component type=location1 '
                        'Group,Component name=comp1,Event source=symmetrix',
            }


def fake_v3_alert_source():
    return {'storage_id': 'abcd-1234-5678',
            'version': 'snmpv3',
            'engine_id': '800000d30300000e112245',
            'username': 'test1',
            'auth_key': 'YWJjZDEyMzQ1Njc=',
            'auth_protocol': 'HMACMD5',
            'privacy_key': 'YWJjZDEyMzQ1Njc=',
            'privacy_protocol': 'DES'
            }


def fake_v3_alert_source_list_with_one():
    return [
        {'storage_id': 'abcd-1234-5678',
         'version': 'snmpv3',
         'engine_id': '800000d30300000e112245',
         'username': 'test1',
         'auth_key': 'YWJjZDEyMzQ1Njc=',
         'auth_protocol': 'HMACMD5',
         'privacy_key': 'YWJjZDEyMzQ1Njc=',
         'privacy_protocol': 'DES'
         }
    ]


def null_alert_source_list():
    return []


def fake_v3_alert_source_list():
    return [
        {'storage_id': 'abcd-1234-5678',
         'version': 'snmpv3',
         'engine_id': '800000d30300000e112245',
         'username': 'test1',
         'auth_key': 'YWJjZDEyMzQ1Njc=',
         'auth_protocol': 'HMACMD5',
         'privacy_key': 'YWJjZDEyMzQ1Njc=',
         'privacy_protocol': 'DES'
         },
        {'storage_id': 'abcd-1234-5677',
         'version': 'snmpv3',
         'engine_id': '800000d30300000e112246',
         'username': 'test2',
         'auth_key': 'YWJjZDEyMzQ1Njc=',
         'auth_protocol': 'HMACMD5',
         'privacy_key': 'YWJjZDEyMzQ1Njc=',
         'privacy_protocol': 'DES'
         }
    ]


def parse_alert_exception():
    raise exception.InvalidResults("parse alert failed.")


def load_config_exception(para):
    raise exception.InvalidResults("load config failed.")


def mock_add_transport(snmpEngine, transportDomain, transport):
    snmpEngine.transportDispatcher = AsyncoreDispatcher()
