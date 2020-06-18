# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Base classes for our unit tests.

Allows overriding of flags for use of fakes, and some black magic for
inline callbacks.

"""

import fixtures
from unittest import mock
from oslo_concurrency import lockutils
from oslo_config import cfg
from oslo_config import fixture as config_fixture
import oslo_messaging
from oslo_messaging import conffixture as messaging_conffixture
from oslo_utils import uuidutils
import oslotest.base as base_test

from delfin.common import config  # noqa
from delfin import coordination
from delfin.db.sqlalchemy import api as db_api
from delfin.db.sqlalchemy import models as db_models
from delfin import rpc
from delfin import service
from delfin.tests.unit import conf_fixture, fake_notifier

test_opts = [
    cfg.StrOpt('sqlite_db',
               default='delfin.sqlite',
               help='The filename to use with sqlite.'),
]

CONF = cfg.CONF
CONF.register_opts(test_opts)

_DB_CACHE = None


class Database(fixtures.Fixture):

    def __init__(self, db_session, sql_connection):
        self.sql_connection = sql_connection
        self.engine = db_session.get_engine()
        self.engine.dispose()
        conn = self.engine.connect()
        db_models.BASE.metadata.create_all(self.engine)
        self._DB = "".join(line for line in conn.connection.iterdump())
        self.engine.dispose()

    def setUp(self):
        super(Database, self).setUp()
        conn = self.engine.connect()
        conn.connection.executescript(self._DB)
        self.addCleanup(self.engine.dispose)


class TestCase(base_test.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(TestCase, self).setUp()

        conf_fixture.set_defaults(CONF)
        CONF([], default_config_files=[])

        global _DB_CACHE
        if not _DB_CACHE:
            _DB_CACHE = Database(
                db_api,
                sql_connection=CONF.database.connection)
        self.useFixture(_DB_CACHE)

        self.injected = []
        self._services = []
        # This will be cleaned up by the NestedTempfile fixture
        lock_path = self.useFixture(fixtures.TempDir()).path
        self.fixture = self.useFixture(config_fixture.Config(lockutils.CONF))
        self.fixture.config(lock_path=lock_path, group='oslo_concurrency')
        self.fixture.config(
            disable_process_locking=True, group='oslo_concurrency')

        rpc.add_extra_exmods('delfin.tests')
        self.addCleanup(rpc.clear_extra_exmods)
        self.addCleanup(rpc.cleanup)

        self.messaging_conf = messaging_conffixture.ConfFixture(CONF)
        self.messaging_conf.transport_url = 'fake:/'
        self.messaging_conf.response_timeout = 15
        self.useFixture(self.messaging_conf)

        oslo_messaging.get_notification_transport(CONF)
        self.override_config('driver', ['test'],
                             group='oslo_messaging_notifications')

        rpc.init(CONF)

        fake_notifier.stub_notifier(self)

        # Locks must be cleaned up after tests
        CONF.set_override('backend_type', 'file',
                          group='coordination')
        CONF.set_override('backend_server', lock_path,
                          group='coordination')
        coordination.LOCK_COORDINATOR.start()
        self.addCleanup(coordination.LOCK_COORDINATOR.stop)

    def tearDown(self):
        """Runs after each test method to tear down test environment."""
        super(TestCase, self).tearDown()
        # Reset any overridden flags
        CONF.reset()

        # Stop any timers
        for x in self.injected:
            try:
                x.stop()
            except AssertionError:
                pass

        # Kill any services
        for x in self._services:
            try:
                x.kill()
            except Exception:
                pass

        # Delete attributes that don't start with _ so they don't pin
        # memory around unnecessarily for the duration of the test
        # suite
        for key in [k for k in self.__dict__.keys() if k[0] != '_']:
            del self.__dict__[key]

    def flags(self, **kw):
        """Override flag variables for a test."""
        for k, v in kw.items():
            CONF.set_override(k, v)

    def start_service(self, name, host=None, **kwargs):
        host = host and host or uuidutils.generate_uuid()
        kwargs.setdefault('host', host)
        kwargs.setdefault('binary', 'delfin-%s' % name)
        svc = service.Service.create(**kwargs)
        svc.start()
        self._services.append(svc)
        return svc

    def mock_object(self, obj, attr_name, new_attr=None, **kwargs):
        """Use python mock to mock an object attribute

        Mocks the specified objects attribute with the given value.
        Automatically performs 'addCleanup' for the mock.

        """
        if not new_attr:
            new_attr = mock.Mock()
        patcher = mock.patch.object(obj, attr_name, new_attr, **kwargs)
        patcher.start()
        self.addCleanup(patcher.stop)
        return new_attr

    def mock_class(self, class_name, new_val=None, **kwargs):
        """Use python mock to mock a class

        Mocks the specified objects attribute with the given value.
        Automatically performs 'addCleanup' for the mock.

        """
        if not new_val:
            new_val = mock.Mock()
        patcher = mock.patch(class_name, new_val, **kwargs)
        patcher.start()
        self.addCleanup(patcher.stop)
        return new_val

    # Useful assertions
    def assertDictMatch(self, d1, d2, approx_equal=False, tolerance=0.001):
        """Assert two dicts are equivalent.

        This is a 'deep' match in the sense that it handles nested
        dictionaries appropriately.

        NOTE:

            If you don't care (or don't know) a given value, you can specify
            the string DONTCARE as the value. This will cause that dict-item
            to be skipped.

        """
        def raise_assertion(msg):
            d1str = str(d1)
            d2str = str(d2)
            base_msg = ('Dictionaries do not match. %(msg)s d1: %(d1str)s '
                        'd2: %(d2str)s' %
                        {"msg": msg, "d1str": d1str, "d2str": d2str})
            raise AssertionError(base_msg)

        d1keys = set(d1.keys())
        d2keys = set(d2.keys())
        if d1keys != d2keys:
            d1only = d1keys - d2keys
            d2only = d2keys - d1keys
            raise_assertion('Keys in d1 and not d2: %(d1only)s. '
                            'Keys in d2 and not d1: %(d2only)s' %
                            {"d1only": d1only, "d2only": d2only})

        for key in d1keys:
            d1value = d1[key]
            d2value = d2[key]
            try:
                error = abs(float(d1value) - float(d2value))
                within_tolerance = error <= tolerance
            except (ValueError, TypeError):
                # If both values aren't convertible to float, just ignore
                # ValueError if arg is a str, TypeError if it's something else
                # (like None)
                within_tolerance = False

            if hasattr(d1value, 'keys') and hasattr(d2value, 'keys'):
                self.assertDictMatch(d1value, d2value)
            elif 'DONTCARE' in (d1value, d2value):
                continue
            elif approx_equal and within_tolerance:
                continue
            elif d1value != d2value:
                raise_assertion("d1['%(key)s']=%(d1value)s != "
                                "d2['%(key)s']=%(d2value)s" %
                                {
                                    "key": key,
                                    "d1value": d1value,
                                    "d2value": d2value
                                })

    def assertDictListMatch(self, L1, L2, approx_equal=False, tolerance=0.001):
        """Assert a list of dicts are equivalent."""
        def raise_assertion(msg):
            L1str = str(L1)
            L2str = str(L2)
            base_msg = ('List of dictionaries do not match: %(msg)s '
                        'L1: %(L1str)s L2: %(L2str)s' %
                        {"msg": msg, "L1str": L1str, "L2str": L2str})
            raise AssertionError(base_msg)

        L1count = len(L1)
        L2count = len(L2)
        if L1count != L2count:
            raise_assertion('Length mismatch: len(L1)=%(L1count)d != '
                            'len(L2)=%(L2count)d' %
                            {"L1count": L1count, "L2count": L2count})

        for d1, d2 in zip(L1, L2):
            self.assertDictMatch(d1, d2, approx_equal=approx_equal,
                                 tolerance=tolerance)

    def assertSubDictMatch(self, sub_dict, super_dict):
        """Assert a sub_dict is subset of super_dict."""
        self.assertTrue(set(sub_dict.keys()).issubset(set(super_dict.keys())))
        for k, sub_value in sub_dict.items():
            super_value = super_dict[k]
            if isinstance(sub_value, dict):
                self.assertSubDictMatch(sub_value, super_value)
            elif 'DONTCARE' in (sub_value, super_value):
                continue
            else:
                self.assertEqual(sub_value, super_value)

    def assertIn(self, a, b, *args, **kwargs):
        """Python < v2.7 compatibility.  Assert 'a' in 'b'."""
        try:
            f = super(TestCase, self).assertIn
        except AttributeError:
            self.assertTrue(a in b, *args, **kwargs)
        else:
            f(a, b, *args, **kwargs)

    def assertNotIn(self, a, b, *args, **kwargs):
        """Python < v2.7 compatibility.  Assert 'a' NOT in 'b'."""
        try:
            f = super(TestCase, self).assertNotIn
        except AttributeError:
            self.assertFalse(a in b, *args, **kwargs)
        else:
            f(a, b, *args, **kwargs)

    def assertIsInstance(self, a, b, *args, **kwargs):
        """Python < v2.7 compatibility."""
        try:
            f = super(TestCase, self).assertIsInstance
        except AttributeError:
            self.assertIsInstance(a, b)
        else:
            f(a, b, *args, **kwargs)

    def assertIsNone(self, a, *args, **kwargs):
        """Python < v2.7 compatibility."""
        try:
            f = super(TestCase, self).assertIsNone
        except AttributeError:
            self.assertTrue(a is None)
        else:
            f(a, *args, **kwargs)

    def _dict_from_object(self, obj, ignored_keys):
        if ignored_keys is None:
            ignored_keys = []
        return {k: v for k, v in obj.items()
                if k not in ignored_keys}

    def _assertEqualListsOfObjects(self, objs1, objs2, ignored_keys=None):
        obj_to_dict = lambda o: (  # noqa: E731
            self._dict_from_object(o, ignored_keys))
        sort_key = lambda d: [d[k] for k in sorted(d)]  # noqa: E731
        conv_and_sort = lambda obj: (  # noqa: E731
            sorted(map(obj_to_dict, obj), key=sort_key))

        self.assertEqual(conv_and_sort(objs1), conv_and_sort(objs2))

    def assert_notify_called(self, mock_notify, calls):
        for i in range(0, len(calls)):
            mock_call = mock_notify.call_args_list[i]
            call = calls[i]

            posargs = mock_call[0]

            self.assertEqual(call[0], posargs[0])
            self.assertEqual(call[1], posargs[2])

    def override_config(self, name, override, group=None):
        """Cleanly override CONF variables."""
        CONF.set_override(name, override, group)
        self.addCleanup(CONF.clear_override, name, group)
