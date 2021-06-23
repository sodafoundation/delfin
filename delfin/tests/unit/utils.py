# Copyright 2021 The SODA Authors.
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

import unittest
from delfin.db.sqlalchemy import models

case = unittest.TestCase()


def check_isinstance(obj, cls):
    if isinstance(obj, cls):
        return True
    else:
        assert isinstance(models.StoragePool, object)


def get_db_schema_attributes_list(schema):
    db_attrib_lst = []
    for i in schema.__dict__.keys():
        if not i.startswith('_'):
            db_attrib_lst.append(i)
    return sorted(db_attrib_lst)


def validate_db_schema_model(got, model):
    try:
        res = check_isinstance(got, model)
        if res:
            attributes = get_db_schema_attributes_list(model)
            lst = sorted(list(got.keys()))
            case.assertListEqual(attributes, lst)
            case.assertCountEqual(attributes, lst)
    except AssertionError:
        raise
