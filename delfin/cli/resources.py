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

from configs import DelfinURL


# API get storage-pools from id
def get_storage_pool(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storage-pools/" + args.id
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for storage pools get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get storage pool
def list_storage_pools(args):
    url = DelfinURL + "/storage-pools"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for storage pools list failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get volumes from id
def get_volume(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storage-pools/" + args.id
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for storage pools get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API list volumes
def list_volumes(args):
    url = DelfinURL + "/volumes"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for volumes list failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get controllers from id
def get_controller(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/controllers/" + args.id
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for controllers get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API list controllers
def list_controllers(args):
    url = DelfinURL + "/controllers"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for controllers list failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get ports from id
def get_port(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/ports/" + args.id
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for storage ports get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API list ports
def list_ports(args):
    url = DelfinURL + "/ports"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for storage ports list failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get disk from id
def get_disk(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/disks/" + args.id
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for disks get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API list disks
def list_disks(args):
    url = DelfinURL + "/disks"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for disks list failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API sync
def sync_all(args):
    if args.id is None:
        url = DelfinURL + "/storages/sync"
        api = 'sync_all'
    else:
        url = DelfinURL + "/storages/" + args.id + "/sync"
        api = 'sync' + args.id
    resp = requests.post(url=url)
    if resp.status_code != 202:
        print("Request for sync storages failed", resp.status_code)
    else:
        print("Successfully send sync request: ", api)


# API get access info from storage id
def get_access_info(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storages/" + args.id + "/access-info"
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for storage access-info get failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API update access info for a storage
def update_access_info(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    if args.data is None:
        raise Exception('Missing parameter, "data"')

    url = DelfinURL + "/storages/" + args.id + "/access-info"
    resp = requests.put(url=url, data=args.data)
    if resp.status_code != 201:
        print("Request for Update access info of Storage failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API delete alert from storage id
def delete_alert(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    if args.seq is None:
        raise Exception('Missing parameter, "seq"')
    url = DelfinURL + "/storages/" + args.id + "/alerts" + args.seq
    resp = requests.delete(url=url)
    if resp.status_code != 200:
        print("Request for storage alerts delete failed", resp.status_code,  args.id,  args.weq)
    else:
        print("Alert successfully deleted:", resp)


# API sync alerts for a storage
def sync_alert(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    if args.data is None:
        raise Exception('Missing parameter, "data"')

    url = DelfinURL + "/storages/" + args.id + "/alerts/sync"
    headers = {
        'content-type': 'application/json'
    }

    resp = requests.post(url=url, data=args.data, headers=headers)
    if resp.status_code != 201:
        print("Request for sync alerts of Storage failed", resp.status_code, args.id)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API get alert-source information from storage id
def get_alert_source(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storages/" + args.id + '/alert-source'
    resp = requests.get(url=url)
    if resp.status_code != 200:
        print("Request for alert-source failed", resp.status_code)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API update alert-source for storage id
def update_alert_source(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storages/" + args.id + '/alert-source'
    resp = requests.put(url=url, data=args.data)
    if resp.status_code != 200:
        print("Request for update alert-source failed", resp.status_code, args.id)
    else:
        print(json.dumps(resp.json(), indent=2, sort_keys=True))


# API delete alert-source for storage id
def delete_alert_source(args):
    if args.id is None:
        raise Exception('Missing parameter, "id"')
    url = DelfinURL + "/storages/" + args.id + '/alert-source'
    resp = requests.delete(url=url)
    if resp.status_code != 200:
        print("Request for delete alert-source failed:", args.id)
    else:
        print("Successfully deleted alert-source: ", args.id)
    print(resp)
