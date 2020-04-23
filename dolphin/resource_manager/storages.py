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

"""The storages api implementation"""

import copy

from oslo_log import log
from dolphin import db
from dolphin.db.sqlalchemy import api as db
from webob import exc
from dolphin.driver_manager import manager as drivermanager
from dolphin.api.common import wsgi

LOG = log.getLogger(__name__)


def build_storages(storages):
    views = [build_storage(storage)
             for storage in storages]
    return dict(storage=views)


def build_storage(storage):
    view = copy.deepcopy(storage)
    return view


def get_all(req):
    storage_all = db.storage_get_all()
    search_opts = [
        'name',
        'vendor',
        'model',
        'status',
    ]
    for search_opt in search_opts:
        if search_opt in req.GET:
            value = req.GET[search_opt]
            storage_all = [s for s in storage_all if s[search_opt] == value]
        if len(storage_all) == 0:
            break
    return build_storages(storage_all)


def register(self, req, body):
    """
    This is create function for registering the new storage device
    :param req:
    :param body: "It contains the all input parameters"
    :return:
    """
    # Check if body is valid
    if not wsgi.Controller.is_valid_body(body, 'storages'):
        msg = "Storage entity not found in request body"
        raise exc.HTTPUnprocessableEntity(explanation=msg)

    required_parameters = ('name', 'manufacturer', 'model', 'username', 'password')

    storage = body['storages']

    for parameter in required_parameters:
        if parameter not in storage:
            msg = "Required parameter %s not found" % parameter
            raise exc.HTTPUnprocessableEntity(explanation=msg)
        if not storage.get(parameter):
            msg = "Required parameter %s is empty" % parameter
            raise exc.HTTPUnprocessableEntity(explanation=msg)

    driver = drivermanager.Driver()
    device_info = driver.register()
    if device_info.get('status') == 'available':
        try:
            storage['storage_id'] = device_info.get('id')
            db.registry_context_create(storage)
        except:
            LOG.error('device context registration failed!!')
            raise

        try:
            db.storage_create(device_info)
        except:
            LOG.error('storage DB entry creation failed')
            raise
    else:
        raise Exception('device registration failed!!')

    return storage
