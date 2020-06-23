# Copyright 2020 The SODA Authors.
# Copyright 2014 Mirantis Inc.
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

"""Test of Base Manager for Manila."""

import ddt
from oslo_utils import importutils

from delfin import manager
from delfin import test


@ddt.ddt
class ManagerTestCase(test.TestCase):

    def setUp(self):
        super(ManagerTestCase, self).setUp()
        self.host = 'host'
        self.db_driver = 'fake_driver'
        self.mock_object(importutils, 'import_module')

    def test_verify_manager_instance(self):
        fake_manager = manager.Manager(self.host, self.db_driver)
        self.assertTrue(hasattr(fake_manager, '_periodic_tasks'))
        self.assertTrue(hasattr(fake_manager, 'additional_endpoints'))
        self.assertTrue(hasattr(fake_manager, 'host'))
        self.assertTrue(hasattr(fake_manager, 'periodic_tasks'))
        self.assertTrue(hasattr(fake_manager, 'init_host'))
        self.assertTrue(hasattr(fake_manager, 'service_version'))
        self.assertTrue(hasattr(fake_manager, 'service_config'))
        self.assertEqual(self.host, fake_manager.host)
        importutils.import_module.assert_called_once_with(self.db_driver)

    @ddt.data(True, False)
    def test_periodic_tasks(self, raise_on_error):
        fake_manager = manager.Manager(self.host, self.db_driver)
        fake_context = 'fake_context'
        self.mock_object(fake_manager, 'run_periodic_tasks')

        fake_manager.periodic_tasks(fake_context, raise_on_error)

        fake_manager.run_periodic_tasks.assert_called_once_with(
            fake_context, raise_on_error=raise_on_error)
