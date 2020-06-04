# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Dolphin base exception handling.

Includes decorator for re-raising Dolphin-type exceptions.

SHOULD include dedicated exception logging.

"""

import six
import webob.exc

from oslo_log import log

from dolphin.i18n import _

LOG = log.getLogger(__name__)


class ConvertedException(webob.exc.WSGIHTTPException):
    def __init__(self, exception):
        self.code = exception.code
        self.title = ''
        self.explanation = exception.msg
        self.error_code = exception.error_code
        self.error_args = exception.error_args
        super(ConvertedException, self).__init__()


class DolphinException(Exception):
    """Base Dolphin Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the tuple arguments provided to the constructor.

    """
    msg_fmt = _("An unknown exception occurred.")
    code = 500

    def __init__(self, *args, **kwargs):
        self.error_args = args
        message = kwargs.get('message')
        try:
            if not message:
                message = self.msg_fmt.format(*args)
            else:
                message = six.text_type(message)
        except Exception:
            LOG.error("Failed to format message: {0}".format(args))
            message = self.msg_fmt
        self.msg = message
        super(DolphinException, self).__init__(message)

    @property
    def error_code(self):
        return self.__class__.__name__


class NotAuthorized(DolphinException):
    msg_fmt = _("Not authorized.")
    code = 403


class Invalid(DolphinException):
    msg_fmt = _("Unacceptable parameters.")
    code = 400


class BadRequest(Invalid):
    msg_fmt = _('The server could not comply with the request since\r\n'
                'it is either malformed or otherwise incorrect.\r\n')
    code = 400


class MalformedRequestBody(Invalid):
    msg_fmt = _("Malformed request body: {0}.")


class MalformedRequestUrl(Invalid):
    msg_fmt = _("Malformed request url.")


class InvalidCredential(Invalid):
    msg_fmt = _("The credentials are invalid.")


class InvalidRequest(Invalid):
    msg_fmt = _("The request is invalid.")


class InvalidResults(Invalid):
    msg_fmt = _("The results are invalid. {0}")


class InvalidInput(Invalid):
    msg_fmt = _("Invalid input received. {0}")


class InvalidName(Invalid):
    msg_fmt = _("An invalid 'name' value was provided. {0}")


class InvalidContentType(Invalid):
    msg_fmt = _("Invalid content type: {0}.")


class StorageSerialNumberMismatch(Invalid):
    msg_fmt = _("Storage serial number mismatch. {0}")


class StorageAlreadyExists(Invalid):
    msg_fmt = _("Storage already exists.")


class InvalidSNMPConfig(Invalid):
    msg_fmt = _("Invalid SNMP configuration: {0}")


class NotFound(DolphinException):
    msg_fmt = _("Resource could not be found.")
    code = 404


class NoSuchAction(NotFound):
    msg_fmt = _("There is no such action: {0}")


class AccessInfoNotFound(NotFound):
    msg_fmt = _("Access information for storage {0} could not be found.")


class AlertSourceNotFound(NotFound):
    msg_fmt = _("Alert source for storage {0} could not be found.")


class AlertSourceNotFoundWithHost(NotFound):
    msg_fmt = _("Alert source could not be found with host {0}.")


class StorageNotFound(NotFound):
    msg_fmt = _("Storage {0} could not be found.")


class StorageBackendNotFound(NotFound):
    msg_fmt = _("Storage backend could not be found.")


class StoragePoolNotFound(NotFound):
    msg_fmt = _("Storage pool {0} could not be found.")


class VolumeNotFound(NotFound):
    msg_fmt = _("Volume {0} could not be found.")


class StorageDriverNotFound(NotFound):
    msg_fmt = _("Storage driver '{0}'could not be found.")


class ConfigNotFound(NotFound):
    msg_fmt = _("Could not find config at {0}.")


class PasteAppNotFound(NotFound):
    msg_fmt = _("Could not load paste app '{0}' from {1}.")


class StorageBackendException(DolphinException):
    msg_fmt = _("Exception from Storage Backend: {0}.")


class SSHException(DolphinException):
    msg_fmt = _("Exception in SSH protocol negotiation or logic. {0}")


class SSHInjectionThreat(DolphinException):
    msg_fmt = _("SSH command injection detected: {0}.")


# Tooz locking
class LockCreationFailed(DolphinException):
    msg_fmt = _('Unable to create lock. Coordination backend not started.')


class LockAcquisitionFailed(DolphinException):
    msg_fmt = _('Lock acquisition failed.')


class DuplicateExtension(DolphinException):
    msg_fmt = _('Found duplicate extension: {0}.')


class ImproperIPVersion(DolphinException):
    msg_fmt = _("Provided improper IP version {0}.")
