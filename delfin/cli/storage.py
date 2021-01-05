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


import requests
import json

from configs import DelfinURL, update_config_vars


# API get storage from id
def get_storage(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storages/" + args.id
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for Storage get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get storage
def list_storage(args):
    url = DelfinURL + "/storages"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for Storage list failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API delete storage from id
def delete_storage(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storages/" + args.id
    resp = requests.delete(url=url)
    if resp.status_code != 202:
        print("Request for delete Storage failed:", args.id)
    else:
        print("Successfully deleted: ", args.id)

    print(resp)


def add_storage(args):
    update_config_vars(args)

    if args.data is None:
        raise Exception('Missing parameter, "data"')
    url = DelfinURL + '/storages'
    headers = {
        'content-type': 'application/json'
    }

    resp = requests.post(url=url, data=args.data, headers=headers)
    if resp.status_code != 201:
        print("Request for Register Storage failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))
