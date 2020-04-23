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

"""The shares api."""

import copy

from oslo_db import exception
from oslo_log import log
from webob import exc

from dolphin import db, context
from dolphin.db.sqlalchemy import api as db
from dolphin.drivers import manager as drivermanager

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
    This function for registering the new storage device
    :param req:
    :param body: "It contains the all input parameters"
    :return:
    """
    # validate the body has all required parameters
    required_parameters = ('hostname', 'manufacturer', 'model', 'username', 'password')

    storage = body['storages']

    for parameter in required_parameters:
        if parameter not in storage:
            msg = "Required parameter %s not found" % parameter
            raise exc.HTTPUnprocessableEntity(explanation=msg)
        if not storage.get(parameter):
            msg = "Required parameter %s is empty" % parameter
            raise exc.HTTPUnprocessableEntity(explanation=msg)

    driver = drivermanager.DriverManager()
    device_info = driver.register_storage(context, storage)
    if device_info.get('status') == 'available':
        try:
            storage['storage_id'] = device_info.get('id')
            db.registry_context_create(storage)
        except Exception:
            msg = 'Exception during registry context creation'
            LOG.exception(msg)
            raise exception.DBError(msg)

        try:
            db.storage_create(device_info)
        except Exception:
            msg = 'Exception during storage creation'
            LOG.exception(msg)
            raise exception.DBError(msg)
    else:
        LOG.error('Device registration failed')

    return storage
