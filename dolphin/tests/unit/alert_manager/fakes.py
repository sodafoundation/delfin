# Copyright 2020 The SODA Authors.
# Copyright 2010 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from dolphin import exception


def fake_storage_info():
    return {
        'id': 'abcd-1234-56789',
        'name': 'Dell EMC',
        'vendor': 'Dell EMC',
        'model': 'vmax'
    }


def fake_alert_model():
    return {'me_dn': 'abcd-1234-56789',
            'me_name': 'Dell EMC',
            'manufacturer': 'Dell EMC',
            'location': 'Component type: Symmetrix Disk '
                        'Group,Component name: SRP_1',
            'event_type': 'topology',
            'severity': 'warning',
            'probable_cause': 'Symmetrix 000192601409 FastSRP '
                              'SRP_1 : Remote (SRDF) diagnostic'
                              'event trace triggered.',
            'me_category': 'storage-subsystem',
            'native_me_dn': '000192601409',
            'alarm_id': '1050',
            'alarm_name':
                'SYMAPI_AEVENT2_UID_MOD_DIAG_TRACE_TRIG'
            }


def fake_v3_alert_source():
    return {'storage_id': 'abcd-1234-5678',
            'version': 'snmpv3',
            'engine_id': '800000d30300000e112245',
            'username': 'test1',
            'auth_key': 'YWJjZDEyMzQ1Njc=',
            'auth_protocol': 'md5',
            'privacy_key': 'YWJjZDEyMzQ1Njc=',
            'privacy_protocol': 'des'
            }


def fake_v3_alert_source_list_with_one():
    return [
        {'storage_id': 'abcd-1234-5678',
         'version': 'snmpv3',
         'engine_id': '800000d30300000e112245',
         'username': 'test1',
         'auth_key': 'YWJjZDEyMzQ1Njc=',
         'auth_protocol': 'md5',
         'privacy_key': 'YWJjZDEyMzQ1Njc=',
         'privacy_protocol': 'des'
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
         'auth_protocol': 'md5',
         'privacy_key': 'YWJjZDEyMzQ1Njc=',
         'privacy_protocol': 'des'
         },
        {'storage_id': 'abcd-1234-5677',
         'version': 'snmpv3',
         'engine_id': '800000d30300000e112246',
         'username': 'test2',
         'auth_key': 'YWJjZDEyMzQ1Njc=',
         'auth_protocol': 'md5',
         'privacy_key': 'YWJjZDEyMzQ1Njc=',
         'privacy_protocol': 'des'
         }
    ]


def parse_alert_exception():
    raise exception.InvalidResults("parse alert failed.")


def load_config_exception():
    raise exception.InvalidResults("load config failed.")
