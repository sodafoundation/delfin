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

import abc
from oslo_log import log

from dolphin import exception
from dolphin import db

LOG = log.getLogger(__name__)


def get_access_info(context, storage_id):
    if not storage_id:
        msg = "No storage_id provided."
        LOG.error(msg)
        raise exception.AccessInfoNotFound(message=msg)

    access_info = db.access_info_get(context, storage_id)
    if not access_info:
        msg = (_("Access information of storage '%s' could not be found.") % storage_id)
        LOG.error(msg)
        raise exception.AccessInfoNotFound(message=msg)

    return access_info.to_dict()
