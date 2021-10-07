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

from delfin import db
from delfin import test
from delfin.api.v1.quotas import QuotaController
from delfin.tests.unit.api import fakes


class TestQuotaController(test.TestCase):

    def setUp(self):
        super(TestQuotaController, self).setUp()
        self.controller = QuotaController()

    def test_list(self):
        self.mock_object(
            db, 'quota_get_all',
            fakes.fake_quotas_get_all)
        req = fakes.HTTPRequest.blank('/v1/quotas')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "quotas": [
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "native_quota_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "type": "q_type_1",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_filesystem_id": "NF_ID_1",
                    "native_qtree_id": "NQT_ID_1",
                    "capacity_hard_limit": 1000000000000,
                    "capacity_soft_limit": 1000000000000,
                    "file_hard_limit": 1000000000000,
                    "file_soft_limit": 1000000000000,
                    "file_count": 1000000000000,
                    "used_capacity": 1000000000000,
                    "user_group_name": "UG_1",
                },
                {
                    "created_at": "2020-06-10T07:17:31.157079",
                    "updated_at": "2020-06-10T07:17:31.157079",
                    "id": "d7fe425b-fddc-4ba4-accb-4343c142dc47",
                    "native_quota_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "type": "q_type_1",
                    "storage_id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                    "native_filesystem_id": "NF_ID_2",
                    "native_qtree_id": "NQT_ID_2",
                    "capacity_hard_limit": 2000000000000,
                    "capacity_soft_limit": 2000000000000,
                    "file_hard_limit": 2000000000000,
                    "file_soft_limit": 2000000000000,
                    "file_count": 2000000000000,
                    "used_capacity": 2000000000000,
                    "user_group_name": "UG_2",
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)
