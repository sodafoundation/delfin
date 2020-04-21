# Copyright 2013 NetApp
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

"""The shares api."""

import copy

from os_service_types import exc
from oslo_log import log
from oslo_utils import uuidutils, timeutils

from dolphin import db
from dolphin.db.sqlalchemy import api as db
from dolphin.driver_manager import manager as drivermanager

LOG = log.getLogger(__name__)


def device_model(body):
    device = DeviceModel()
    device.id = uuidutils.generate_uuid()
    device.created_at = timeutils.utcnow()
    if body.get('name'):
        device.name = body.get('name')
    if body.get('description'):
        device.description = body.get('description')
    if body.get('vendor'):
        device.vendor = body.get('vendor')
    if body.get('status'):
        device.status = body.get('status')
    if body.get('total_capacity'):
        device.total_capacity = body.get('total_capacity')
    if body.get('manufacturer'):
        device.manufacturer = body.get('manufacturer')
    if body.get('model'):
        device.model = body.get('model')
    if body.get('firmware_version'):
        device.firmware_version = body.get('firmware_version')
    return device


class DeviceModel:
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.vendor = None
        self.status = None
        self.total_capacity = None
        self.used_capacity = None
        self.free_capacity = None
        self.manufacturer = None
        self.model = None
        self.firmware_version = None
        self.serial_number = None
        self.location = None
        self.created_at = None
        self.updated_at = None


def register_context(device_info):
    registerctx = RegisterContext()
    if device_info.get('storage_id'):
        registerctx.storage_id = device_info.get('storage_id')
    if device_info.get('hostname'):
        registerctx.hostname = device_info.get('hostname')
    if device_info.get('username'):
        registerctx.username = device_info.get('username')
    if device_info.get('password'):
        registerctx.password = device_info.get('password')
    if device_info.get('vendor'):
        registerctx.vendor = device_info.get('vendor')
    if device_info.get('model'):
        registerctx.model = device_info.get('model')
    if device_info.get('extra_attributes'):
        registerctx.extra_attributes = device_info.get('extra_attributes')
    return registerctx


class RegisterContext:
    def __init__(self):
        self.storage_id = None
        self.hostname = None
        self.username = None
        self.password = None
        self.vendor = None
        self.model = None
        self.extra_attributes = None


def build_storages(storages):
    views = [build_storage(storage)
             for storage in storages]
    return dict(storage=views)


def build_storage(storage):
    view = copy.deepcopy(storage)
    return view


def get_all():
    storage_all = db.storage_get_all()
    return build_storages(storage_all)


def register(self, req, body):
    """
            This is create function for registering the new storage device
            :param req:
            :param body: "It contains the all input parameters"
            :return:
            """
    # Check if body is valid
    if not self.is_valid_body(body, 'storages'):
        LOG.error("Not a valid body")
        raise exc.HTTPUnprocessableEntity()

    storage = body['storages']

    driver = drivermanager.Driver()
    device_info = driver.register()
    if device_info.get('status') == 'available':
        try:
            db.registry_context_create(register_context(storage))
        except:
            LOG.error('device context registration failed!!')
            raise

        try:
            db.storage_create(device_model(device_info))
        except:
            LOG.error('storage DB entry creation failed')
            raise
    else:
        raise Exception('device registration failed!!')

    return storage