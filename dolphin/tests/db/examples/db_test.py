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

"""An Example to shw How DB interfaces are called"""
import copy
import sys

from dolphin import  db
from oslo_config import cfg


CONF = cfg.CONF
storage_id='123456789'
register_info = {'storage_id':storage_id, 'username':'admin', 'password':'my_password', 'hostname':"host1", 'extra_attributes':{'key1': 'value1', 'key2': 'value2"'}}
storage = {'name':'Array1','id':storage_id,'vendor':'EMC','model':'VMAX','description':'EMC VMax Array'}

def main():
    # Initialize DB Connection
    CONF(sys.argv[1:], project='dolphin',
         version='v1')
    db.register_db()
    # Create a Storage backend object in DB
    db.registry_context_create(register_info)
    db.storage_create(storage)
    # Get a Storage backend object by providing ID
    strorage=db.storage_get(storage_id)
    print(strorage)
    registry_context = db.registry_context_get(storage_id)
    print(registry_context)
    registry_contexts = db.registry_context_get_all()
    storages_all = db.storage_get_all()


if __name__ == '__main__':
    main()
