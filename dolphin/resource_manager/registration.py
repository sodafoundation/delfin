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

import ast
import copy
from oslo_log import log
from oslo_utils import timeutils
from oslo_utils import uuidutils
from dolphin.api.common import wsgi
from dolphin.api.views import versions as views_versions
from dolphin.task_manager import manager
from dolphin.common import config
from dolphin import context, db
from dolphin.db.sqlalchemy import api as db
from dolphin.driver_manager import manager as drivermanager

from webob import exc

LOG = log.getLogger(__name__)


class RegisterContext:
    def __init__(self):
        self.storage_id = None
        self.hostname = None
        self.username = None
        self.password = None
        self.vendor = None
        self.model = None
        self.extra_attributes = None

    def register_context(self, device_info):
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


class RegistrationController(wsgi.Controller):
    def __init__(self):
        super(RegistrationController, self).__init__(None)
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

    def __create_body(self, body):
        registerctrl = RegistrationController()
        registerctrl.id = uuidutils.generate_uuid()
        if body.get('name'):
            registerctrl.name = body.get('name')
        if body.get('description'):
            registerctrl.description = body.get('description')
        if body.get('vendor'):
            registerctrl.vendor = body.get('vendor')
        if body.get('manufacturer'):
            registerctrl.manufacturer = body.get('manufacturer')
        if body.get('model'):
            registerctrl.model = body.get('model')
        if body.get('firmware_version'):
            registerctrl.firmware_version = body.get('firmware_version')
        registerctrl.created_at = timeutils.utcnow()
        return registerctrl

    @wsgi.response(200)
    def create(self, req, body):
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

        # Create DB entry for the storage body
        db.register_db()
        db.storage_create(self.__create_body(storage))

        # Call the driver for actual registration
        driver = drivermanager.Driver()
        device_info = driver.register(context)

        # Update the device information to this table.(Its a light weight table)

        registerctx = RegisterContext()
        db.registry_context_create(registerctx.register_context(device_info))

        return str(body)


def create_resource():
    return wsgi.Resource(RegistrationController())
