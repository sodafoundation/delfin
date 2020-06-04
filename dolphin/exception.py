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
import re

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log
import six
import webob.exc

from dolphin.i18n import _

LOG = log.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='Whether to make exception message format errors fatal.'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)

ProcessExecutionError = processutils.ProcessExecutionError


class ConvertedException(webob.exc.WSGIHTTPException):
    def __init__(self, code=400, title="", explanation=""):
        self.code = code
        self.title = title
        self.explanation = explanation
        super(ConvertedException, self).__init__()


class Error(Exception):
    pass


class DolphinException(Exception):
    """Base Dolphin Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, detail_data={}, **kwargs):
        self.kwargs = kwargs
        self.detail_data = detail_data

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass
        for k, v in self.kwargs.items():
            if isinstance(v, Exception):
                self.kwargs[k] = six.text_type(v)

        if not message:
            try:
                message = self.message % kwargs

            except Exception:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation.')
                for name, value in kwargs.items():
                    LOG.error("%(name)s: %(value)s", {
                        'name': name, 'value': value})
                if CONF.fatal_exception_format_errors:
                    raise
                else:
                    # at least get the core message out if something happened
                    message = self.message
        elif isinstance(message, Exception):
            message = six.text_type(message)

        if re.match(r'.*[^\.]\.\.$', message):
            message = message[:-1]
        self.msg = message
        super(DolphinException, self).__init__(message)


class NetworkException(DolphinException):
    message = _("Exception due to network failure.")


class NetworkBindException(DolphinException):
    message = _("Exception due to failed port status in binding.")


class NetworkBadConfigurationException(NetworkException):
    message = _("Bad network configuration: %(reason)s.")


class BadConfigurationException(DolphinException):
    message = _("Bad configuration: %(reason)s.")


class NotAuthorized(DolphinException):
    message = _("Not authorized.")
    code = 403


class AdminRequired(NotAuthorized):
    message = _("User does not have admin privileges.")


class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")


class Conflict(DolphinException):
    message = _("%(err)s")
    code = 409


class Invalid(DolphinException):
    message = _("Unacceptable parameters.")
    code = 400


class InvalidCredential(Invalid):
    message = _("The credentials are invalid.")


class InvalidRequest(Invalid):
    message = _("The request is invalid.")


class InvalidResults(Invalid):
    message = _("The results are invalid.")


class InvalidInput(Invalid):
    message = _("Invalid input received: %(reason)s.")


class InvalidName(Invalid):
    message = _("An invalid 'name' value was provided. %(reason)s")


class ValidationError(Invalid):
    message = "%(detail)s"


class InvalidContentType(Invalid):
    message = _("Invalid content type %(content_type)s.")


class InvalidHost(Invalid):
    message = _("Invalid host: %(reason)s")


# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    message = _("%(err)s")


class InvalidUUID(Invalid):
    message = _("Expected a uuid but received %(uuid)s.")


class InvalidDriverMode(Invalid):
    message = _("Invalid driver mode: %(driver_mode)s.")


class InvalidAPIVersionString(Invalid):
    message = _("API Version String %(version)s is of invalid format. Must "
                "be of format MajorNum.MinorNum.")


class VersionNotFoundForAPIMethod(Invalid):
    message = _("API version %(version)s is not supported on this method.")


class InvalidGlobalAPIVersion(Invalid):
    message = _("Version %(req_ver)s is not supported by the API. Minimum "
                "is %(min_ver)s and maximum is %(max_ver)s.")


class InvalidCapacity(Invalid):
    message = _("Invalid capacity: %(name)s = %(value)s.")


class NotFound(DolphinException):
    message = _("Resource could not be found.")
    code = 404
    safe = True


class MessageNotFound(NotFound):
    message = _("Message %(message_id)s could not be found.")


class Found(DolphinException):
    message = _("Resource was found.")
    code = 302
    safe = True


class InUse(DolphinException):
    message = _("Resource is in use.")


class AvailabilityZoneNotFound(NotFound):
    message = _("Availability zone %(id)s could not be found.")


class ServiceNotFound(NotFound):
    message = _("Service %(service_id)s could not be found.")


class ResourceNotFound(NotFound):
    message = _("Resource %(storage_id)s could not be found.")


class AccessInfoNotFound(NotFound):
    message = _("Storage access info %(storage_id)s could not be found.")


class StorageNotFound(NotFound):
    message = _("Storage %(id)s could not be found.")


class StoragePoolNotFound(NotFound):
    message = _("Pool %(id)s could not be found.")


class VolumeNotFound(NotFound):
    message = _("Volume %(id)s could not be found.")


class StorageDriverNotFound(NotFound):
    message = _("Storage driver could not be found.")


class StorageBackendException(DolphinException):
    message = _("Exception from Storage Backend: %(reason)s.")


class StorageSerialNumberMismatch(Invalid):
    message = _("Storage serial number mismatch: "
                "%(reason)s")


class ServiceIsDown(Invalid):
    message = _("Service %(service)s is down.")


class HostNotFound(NotFound):
    message = _("Host %(host)s could not be found.")


class FileNotFound(NotFound):
    message = _("File %(file_path)s could not be found.")


class MalformedRequestBody(DolphinException):
    message = _("Malformed message body: %(reason)s.")


class ConfigNotFound(NotFound):
    message = _("Could not find config at %(path)s.")


class PasteAppNotFound(NotFound):
    message = _("Could not load paste app '%(name)s' from %(path)s.")


class NoValidHost(DolphinException):
    message = _("No valid host was found. %(reason)s.")


class InvalidSqliteDB(Invalid):
    message = _("Invalid Sqlite database.")


class SSHException(DolphinException):
    message = _("Exception in SSH protocol negotiation or logic.")


class SSHInjectionThreat(DolphinException):
    message = _("SSH command injection detected: %(command)s")


class AlertSourceNotFound(NotFound):
    message = _("Alert source for storage %(storage_id)s could not be found.")


# Tooz locking
class LockCreationFailed(DolphinException):
    message = _('Unable to create lock. Coordination backend not started.')


class LockingFailed(DolphinException):
    message = _('Lock acquisition failed.')


class InvalidSNMPConfig(Invalid):
    message = _("SNMP configuration is invalid: %(detail)s.")
