# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_log import log

from delfin import context
from delfin import manager
from delfin.drivers import manager as driver_manager

LOG = log.getLogger(__name__)


class APIManager(manager.Manager):
    """API listening and processing functions"""

    RPC_API_VERSION = '1.0'

    def __init__(self, service_name=None, *args, **kwargs):
        self.driver_mgr = driver_manager.DriverManager()
        super(APIManager, self).__init__(*args, **kwargs)

    def remove_storage(self, ctxt, storage_id):
        LOG.info('Remove storage device in memory for storage id:{0}'
                 .format(storage_id))
        self.driver_mgr.remove_driver(context, storage_id)
