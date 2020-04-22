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

"""This is sample driver manager code just to run the framework. Need not review"""

import shlex
import subprocess
from oslo_log import log
from oslo_service import time
from oslo_utils import uuidutils

LOG = log.getLogger(__name__)

DEVICE_INFO = {
    'id': uuidutils.generate_uuid(),
    'name': 'string',
    'description': 'string',
    'vendor': 'string',
    'status': 'available',
    'total_capacity': 'double',
    'used_capacity': 'double',
    'free_capacity': 'double',
    'manufacturer': 'string',
    'model': 'string',
    'firmwareVersion': 'string',
    'serial_number': 'string',
    'location': 'string',
    'created_at': 'string',
    'updated_at': 'string'
}


class Driver:
    def __init__(self):
        self.stderr = None
        self.stdout = None

    def run_command(self, command):
        args = shlex.split(command)
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr != '':
            raise Exception(stderr)
        else:
            LOG.info("Stdout: {0}".format(stdout))
        return stdout, stderr

    def list_volumes(self, context, device_name):
        LOG.info("Listing Volumes for {0}".format(device_name))
        self.run_command("osdsctl volume list")

    def list_pools(self, context, device_name):
        LOG.info("Listing Pools for {0}".format(device_name))
        self.run_command("osdsctl pool list")

    def register(self):

        # the real implementation
        time.sleep(1)
        return DEVICE_INFO
