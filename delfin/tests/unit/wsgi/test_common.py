# Copyright 2017 Mirantis Inc.
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

from unittest import mock

from delfin import test
from delfin.wsgi import common


class FakeApp(common.Application):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class WSGICommonTestCase(test.TestCase):

    def test_application_factory(self):
        fake_global_config = mock.Mock()
        kwargs = {"k1": "v1", "k2": "v2"}

        result = FakeApp.factory(fake_global_config, **kwargs)

        fake_global_config.assert_not_called()
        self.assertIsInstance(result, FakeApp)
        for k, v in kwargs.items():
            self.assertTrue(hasattr(result, k))
            self.assertEqual(getattr(result, k), v)

    def test_application___call__(self):
        self.assertRaises(
            NotImplementedError,
            common.Application(), 'fake_environ', 'fake_start_response')
