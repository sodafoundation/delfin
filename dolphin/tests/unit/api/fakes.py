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
from dolphin.api.common import wsgi as os_wsgi
from dolphin.common import config  # noqa


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


def fake_volume_get_all(context, marker=None,
                        limit=None, sort_keys=None,
                        sort_dirs=None, filters=None, offset=None):
    return [
        {
            "created_at": "2020-06-10T07:17:31.157079",
            "updated_at": "2020-06-10T07:17:31.157079",
            "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
            "name": "004DF",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "fake_storage 'thin device' volume",
            "status": "available",
            "original_id": "004DF",
            "wwn": "60000970000297801855533030344446",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        },
        {
            "created_at": "2020-06-10T07:17:31.157079",
            "updated_at": "2020-06-10T07:17:31.157079",
            "id": "dad84a1f-db8d-49ab-af40-048fc3544c12",
            "name": "004E0",
            "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
            "original_pool_id": "SRP_1",
            "description": "fake_storage 'thin device' volume",
            "status": "available",
            "original_id": "004E0",
            "wwn": "60000970000297801855533030344530",
            "provisioning_policy": 'thin',
            "total_capacity": 1075838976,
            "used_capacity": 0,
            "free_capacity": 1075838976,
            "compressed": True,
            "deduplicated": False
        }
    ]


def fake_volume_show(context, volume_id):
    return {
        "created_at": "2020-06-10T07:17:31.157079",
        "updated_at": "2020-06-10T07:17:31.157079",
        "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
        "name": "004DF",
        "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
        "original_pool_id": "SRP_1",
        "description": "fake_storage 'thin device' volume",
        "status": "available",
        "original_id": "004DF",
        "wwn": "60000970000297801855533030344446",
        "provisioning_policy": 'thin',
        "total_capacity": 1075838976,
        "used_capacity": 0,
        "free_capacity": 1075838976,
        "compressed": True,
        "deduplicated": False
    }
