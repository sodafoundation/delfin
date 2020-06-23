#    Copyright 2017 Red Hat, Inc.
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

import ddt
from unittest import mock

from delfin import rpc
from delfin import test


@ddt.ddt
class RPCTestCase(test.TestCase):

    @ddt.data([], ['noop'], ['noop', 'noop'])
    @mock.patch('oslo_messaging.JsonPayloadSerializer', wraps=True)
    def test_init_no_notifications(self, driver, serializer_mock):
        self.override_config('driver', driver,
                             group='oslo_messaging_notifications')
        rpc.init(test.CONF)
        self.assertEqual(rpc.utils.DO_NOTHING, rpc.NOTIFIER)
        serializer_mock.assert_not_called()

    @mock.patch.object(rpc, 'messaging')
    def test_init_notifications(self, messaging_mock):
        rpc.init(test.CONF)
        self.assertTrue(messaging_mock.JsonPayloadSerializer.called)
        self.assertTrue(messaging_mock.Notifier.called)
        self.assertEqual(rpc.NOTIFIER, messaging_mock.Notifier.return_value)
