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

import webob.dec
import webob.request

from dolphin import context
from dolphin import exception
from dolphin.api.common import wsgi as os_wsgi
from dolphin.common import config, constants  # noqa
from dolphin.db.sqlalchemy import models


@webob.dec.wsgify
def fake_wsgi(self, req):
    return self.application


class HTTPRequest(os_wsgi.Request):

    @classmethod
    def blank(cls, *args, **kwargs):
        if not kwargs.get('base_url'):
            kwargs['base_url'] = 'http://localhost/v1'
        use_admin_context = kwargs.pop('use_admin_context', False)
        out = os_wsgi.Request.blank(*args, **kwargs)
        out.environ['dolphin.context'] = context.RequestContext(
            is_admin=use_admin_context)
        return out


def fake_storages_get_all(context, marker=None, limit=None, sort_keys=None,
                          sort_dirs=None, filters=None, offset=None):
    return [
        {
            "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
            "created_at": "2020-06-09T08:59:48.710890",
            "free_capacity": 1045449,
            "updated_at": "2020-06-09T08:59:48.769470",
            "name": "fake_driver",
            "location": "HK",
            "firmware_version": "1.0.0",
            "vendor": "fake_vendor",
            "status": "normal",
            "sync_status": constants.SyncStatus.SYNCED,
            "model": "fake_model",
            "description": "it is a fake driver.",
            "serial_number": "2102453JPN12KA0000113",
            "used_capacity": 3126,
            "total_capacity": 1048576
        },
        {
            "id": "277a1d8f-a36e-423e-bdd9-db154f32c289",
            "created_at": "2020-06-09T08:58:23.008821",
            "free_capacity": 1045449,
            "updated_at": "2020-06-09T08:58:23.033601",
            "name": "fake_driver",
            "location": "HK",
            "firmware_version": "1.0.0",
            "vendor": "fake_vendor",
            "status": "normal",
            "sync_status": constants.SyncStatus.SYNCED,
            "model": "fake_model",
            "description": "it is a fake driver.",
            "serial_number": "2102453JPN12KA0000112",
            "used_capacity": 3126,
            "total_capacity": 1048576
        }
    ]


def fake_storages_get_all_with_filter(
        context, marker=None, limit=None,
        sort_keys=None, sort_dirs=None, filters=None, offset=None):
    return [
        {
            "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
            "created_at": "2020-06-09T08:59:48.710890",
            "free_capacity": 1045449,
            "updated_at": "2020-06-09T08:59:48.769470",
            "name": "fake_driver",
            "location": "HK",
            "firmware_version": "1.0.0",
            "vendor": "fake_vendor",
            "status": "normal",
            "sync_status": constants.SyncStatus.SYNCED,
            "model": "fake_model",
            "description": "it is a fake driver.",
            "serial_number": "2102453JPN12KA0000113",
            "used_capacity": 3126,
            "total_capacity": 1048576
        }
    ]


def fake_storages_show(context, storage_id):
    return {
        "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
        "created_at": "2020-06-09T08:59:48.710890",
        "free_capacity": 1045449,
        "updated_at": "2020-06-09T08:59:48.769470",
        "name": "fake_driver",
        "location": "HK",
        "firmware_version": "1.0.0",
        "vendor": "fake_vendor",
        "status": "normal",
        "sync_status": constants.SyncStatus.SYNCED,
        "model": "fake_model",
        "description": "it is a fake driver.",
        "serial_number": "2102453JPN12KA0000113",
        "used_capacity": 3126,
        "total_capacity": 1048576
    }


def fake_access_info_get_all(context, marker=None, limit=None, sort_keys=None,
                             sort_dirs=None, filters=None, offset=None):
    return [
        {
            'created_at': "2020-06-09T08:59:48.710890",
            'model': 'fake_driver',
            'storage_id': '5f5c806d-2e65-473c-b612-345ef43f0642',
            'host': '10.0.0.76',
            'extra_attributes': {'array_id': '0001234567891'},
            'password': b'YWJjZA==', 'port': '1234',
            'updated_at': None,
            'username': 'admin',
            'vendor': 'fake_storage'
        }
    ]


def fake_sync(self, req, id):
    pass


def fake_v3_alert_source_config():
    return {'host': '127.0.0.1',
            'version': 'snmpv3',
            'security_level': 'AuthPriv',
            'engine_id': '800000d30300000e112245',
            'username': 'test1',
            'auth_key': 'abcd123456',
            'auth_protocol': 'md5',
            'privacy_key': 'abcd123456',
            'privacy_protocol': 'des'
            }


def fake_v2_alert_source_config():
    return {'host': '127.0.0.1',
            'version': 'snmpv2c',
            'community_string': 'public'
            }


def fake_v3_alert_source():
    alert_source = models.AlertSource()
    alert_source.host = '127.0.0.1'
    alert_source.storage_id = 'abcd-1234-5678'
    alert_source.version = 'snmpv3'
    alert_source.engine_id = '800000d30300000e112245'
    alert_source.username = 'test1'
    alert_source.auth_key = 'YWJjZDEyMzQ1Njc='
    alert_source.auth_protocol = 'md5'
    alert_source.privacy_key = 'YWJjZDEyMzQ1Njc='
    alert_source.privacy_protocol = 'des'
    return alert_source


def fake_v3_alert_source_noauth_nopriv():
    alert_source = models.AlertSource()
    alert_source.host = '127.0.0.1'
    alert_source.storage_id = 'abcd-1234-5678'
    alert_source.version = 'snmpv3'
    alert_source.security_level = 'NoAuthNoPriv'
    alert_source.engine_id = '800000d30300000e112245'
    alert_source.username = 'test1'
    return alert_source


def fake_v3_alert_source_auth_nopriv():
    alert_source = models.AlertSource()
    alert_source.host = '127.0.0.1'
    alert_source.storage_id = 'abcd-1234-5678'
    alert_source.version = 'snmpv3'
    alert_source.security_level = 'AuthNoPriv'
    alert_source.auth_protocol = 'md5'
    alert_source.engine_id = '800000d30300000e112245'
    alert_source.username = 'test1'
    return alert_source


def fake_v2_alert_source():
    alert_source = models.AlertSource()
    alert_source.host = '127.0.0.1'
    alert_source.storage_id = 'abcd-1234-5678'
    alert_source.version = 'snmpv2c'
    alert_source.community_string = 'public'
    return alert_source


def alert_source_get_exception(ctx, storage_id):
    raise exception.AlertSourceNotFound('abcd-1234-5678')
