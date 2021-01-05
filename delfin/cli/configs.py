# Copyright 2021 The OpenSDS Authors.
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

# This class contains the constants required by different modules

import json

# Input parameters
DefaultStorage = {
  "vendor": "fake_storage",
  "model": "fake_driver",
  "rest": {
    "host": "127.0.0.1",
    "port": 22,
    "username": "admin",
    "password": "password"
  }
}

# Delfin URL:
#               DefaultDelfinProto + '://' +
#               DefaultDelfinIP + ':' +
#               DefaultDelfinPort + '/' +
#               DefaultDelfinAPIVer
# ( Eg. http://127.0.0.1:8190/v1/ )

DefaultDelfinIP = '127.0.0.1'
DefaultDelfinPort = '8190'
DefaultDelfinAPIVer = 'v1'
DefaultDelfinProto = 'http'

DelfinURL = DefaultDelfinProto + '://' + DefaultDelfinIP + ':' + DefaultDelfinPort + '/' + DefaultDelfinAPIVer


def update_config_vars(args):
    if args.data is None:
        args.data = json.dumps(DefaultStorage)
