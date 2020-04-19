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
from dolphin.api.common import wsgi
from dolphin.api.views import versions as views_versions
from dolphin.task_manager import manager
from dolphin.common import config
from dolphin import context, db
from dolphin.db.sqlalchemy import api
from dolphin.driver_manager import manager as drivermanager

from webob import exc

LOG = log.getLogger(__name__)


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
        obj = RegistrationController()
        if body.get('id'):
            obj.id = body.get('id')
        if body.get('name'):
            obj.name = body.get('name')
        if body.get('description'):
            obj.description = body.get('description')
        if body.get('vendor'):
            obj.description = body.get('vendor')
        if body.get('manufacturer'):
            obj.description = body.get('manufacturer')
        if body.get('model'):
            obj.description = body.get('model')
        if body.get('firmware_version'):
            obj.description = body.get('firmware_version')
        obj.created_at = timeutils.utcnow()
        return obj

    @wsgi.response(200)
    def create(self, req, body):

        # Create DB entry for the storage body
        api.register_db()
        api.storage_create(self.__create_body(body))

        # Call the driver for actual registration
        driver_obj = drivermanager.Driver()
        driver_obj.register(context)

        # Update the device information to this table.(Its a light weight table)
        updated_body = self.__create_body(body)
        api.registered_device_list(updated_body)

        return str(body)


def create_resource():
    return wsgi.Resource(RegistrationController())
