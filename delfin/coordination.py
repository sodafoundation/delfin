# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Tooz Coordination and locking utilities."""

import inspect

import decorator

from oslo_config import cfg
from oslo_log import log
from oslo_utils import uuidutils
import six
from tooz import coordination
from tooz import locking
from tooz import partitioner

from delfin import cryptor
from delfin import exception
from delfin.i18n import _

LOG = log.getLogger(__name__)

coordination_opts = [
    cfg.StrOpt('backend_type',
               default='redis',
               help='The backend type for distributed coordination.'
                    'Backend could be redis, mysql, zookeeper and so on.'
                    'For more supported backend, please check Tooz'),
    cfg.StrOpt('backend_user',
               default='',
               help='The backend user for distributed coordination.'),
    cfg.StrOpt('backend_password',
               help='The backend password to use '
                    'for distributed coordination.'),
    cfg.StrOpt('backend_server',
               default='127.0.0.1:6379',
               help='The backend server for distributed coordination.'),
    cfg.IntOpt('expiration',
               default=100,
               help='The expiration(in second) of the lock.'),
    cfg.IntOpt('lease_timeout',
               default=15,
               help='The expiration(in second) of the lock.'),
]

CONF = cfg.CONF
CONF.register_opts(coordination_opts, group='coordination')


class Coordinator(object):
    """Tooz coordination wrapper.

    Coordination member id is created from concatenated `prefix` and
    `agent_id` parameters.

    :param str agent_id: Agent identifier
    :param str prefix: Used to provide member identifier with a
    meaningful prefix.
    """

    def __init__(self, agent_id=None, prefix=''):
        self.coordinator = None
        self.agent_id = agent_id or uuidutils.generate_uuid()
        self.started = False
        self.prefix = prefix

    def start(self):
        """Connect to coordination back end."""
        if self.started:
            return

        # NOTE(gouthamr): Tooz expects member_id as a byte string.
        member_id = (self.prefix + self.agent_id).encode('ascii')

        LOG.info('Started Coordinator (Agent ID: %(agent)s, prefix: '
                 '%(prefix)s)', {'agent': self.agent_id,
                                 'prefix': self.prefix})

        backend_url = _get_redis_backend_url()
        self.coordinator = coordination.get_coordinator(
            backend_url, member_id,
            timeout=CONF.coordination.expiration)
        self.coordinator.start(start_heart=True)
        self.started = True

    def stop(self):
        """Disconnect from coordination back end."""
        msg = 'Stopped Coordinator (Agent ID: %(agent)s, prefix: %(prefix)s)'
        msg_args = {'agent': self.agent_id, 'prefix': self.prefix}
        if self.started:
            self.coordinator.stop()
            self.coordinator = None
            self.started = False

        LOG.info(msg, msg_args)

    def get_lock(self, name):
        """Return a Tooz back end lock.

        :param str name: The lock name that is used to identify it
            across all nodes.
        """
        # NOTE(gouthamr): Tooz expects lock name as a byte string
        lock_name = (self.prefix + name).encode('ascii')
        if self.started:
            return self.coordinator.get_lock(lock_name)
        else:
            raise exception.LockCreationFailed(_('Coordinator uninitialized.'))


LOCK_COORDINATOR = Coordinator(prefix='delfin-')


class LeaderElectionCoordinator(Coordinator):

    def __init__(self, agent_id=None):
        super(LeaderElectionCoordinator, self). \
            __init__(agent_id=agent_id, prefix="leader_election")
        self.group = None

    def start(self):
        """Connect to coordination back end."""
        if self.started:
            return

        # NOTE(gouthamr): Tooz expects member_id as a byte string.
        member_id = (self.prefix + "-" + self.agent_id).encode('ascii')
        LOG.info('Started Coordinator (Agent ID: %(agent)s, '
                 'prefix: %(prefix)s)', {'agent': self.agent_id,
                                         'prefix': self.prefix})

        backend_url = _get_redis_backend_url()
        self.coordinator = coordination.get_coordinator(
            backend_url, member_id,
            timeout=CONF.coordination.lease_timeout)
        self.coordinator.start()
        self.started = True

    def ensure_group(self, group):
        req = self.coordinator.get_groups()
        groups = req.get()
        try:
            # Check if group exist
            groups.index(group)
        except Exception:
            # Create a group if not exist
            LOG.debug("Exception is expected as requested group not available "
                      "in tooz backend. Creating the group")
            request = self.coordinator.create_group(group)
            request.get()
        else:
            LOG.info("Leader group already exist")

        self.group = group

    def join_group(self):
        if self.group:
            request = self.coordinator.join_group(self.group)
            request.get()

    def register_on_start_leading_callback(self, callback):
        return self.coordinator.watch_elected_as_leader(self.group, callback)

    def send_heartbeat(self):
        return self.coordinator.heartbeat()

    def start_leader_watch(self):
        return self.coordinator.run_watchers()

    def stop(self):
        """Disconnect from coordination back end."""
        if self.started:
            self.coordinator.stop()
            self.coordinator = None
            self.started = False

        LOG.info('Stopped Coordinator (Agent ID: %(agent)s',
                 {'agent': self.agent_id})

    def is_still_leader(self):
        for acquired_lock in self.coordinator._acquired_locks:
            return acquired_lock.is_still_owner()
        return False


class Lock(locking.Lock):
    """Lock with dynamic name.

    :param str lock_name: Lock name.
    :param dict lock_data: Data for lock name formatting.
    :param coordinator: Coordinator object to use when creating lock.
        Defaults to the global coordinator.

    Using it like so::

        with Lock('mylock'):
           ...

    ensures that only one process at a time will execute code in context.
    Lock name can be formatted using Python format string syntax::

        Lock('foo-{share.id}, {'share': ...,}')

    Available field names are keys of lock_data.
    """

    def __init__(self, lock_name, lock_data=None, coordinator=None):
        super(Lock, self).__init__(six.text_type(id(self)))
        lock_data = lock_data or {}
        self.coordinator = coordinator or LOCK_COORDINATOR
        self.blocking = True
        self.lock = self._prepare_lock(lock_name, lock_data)

    def _prepare_lock(self, lock_name, lock_data):
        if not isinstance(lock_name, six.string_types):
            raise ValueError(_('Not a valid string: %s') % lock_name)
        return self.coordinator.get_lock(lock_name.format(**lock_data))

    def acquire(self, blocking=None):
        """Attempts to acquire lock.

        :param blocking: If True, blocks until the lock is acquired. If False,
            returns right away. Otherwise, the value is used as a timeout
            value and the call returns maximum after this number of seconds.
        :return: returns true if acquired (false if not)
        :rtype: bool
        """
        blocking = self.blocking if blocking is None else blocking
        return self.lock.acquire(blocking=blocking)

    def release(self):
        """Attempts to release lock.

        The behavior of releasing a lock which was not acquired in the first
        place is undefined.
        """
        self.lock.release()


def synchronized(lock_name, blocking=True, coordinator=None):
    """Synchronization decorator.

    :param str lock_name: Lock name.
    :param blocking: If True, blocks until the lock is acquired.
            If False, raises exception when not acquired. Otherwise,
            the value is used as a timeout value and if lock is not acquired
            after this number of seconds exception is raised.
    :param coordinator: Coordinator object to use when creating lock.
        Defaults to the global coordinator.
    :raises tooz.coordination.LockAcquireFailed: if lock is not acquired

    Decorating a method like so::

        @synchronized('mylock')
        def foo(self, *args):
           ...

    ensures that only one process will execute the foo method at a time.

    Different methods can share the same lock::

        @synchronized('mylock')
        def foo(self, *args):
           ...

        @synchronized('mylock')
        def bar(self, *args):
           ...

    This way only one of either foo or bar can be executing at a time.

    Lock name can be formatted using Python format string syntax::

        @synchronized('{f_name}-{shr.id}-{snap[name]}')
        def foo(self, shr, snap):
           ...

    Available field names are: decorated function parameters and
    `f_name` as a decorated function name.
    """

    @decorator.decorator
    def _synchronized(f, *a, **k):
        call_args = inspect.getcallargs(f, *a, **k)
        call_args['f_name'] = f.__name__
        lock = Lock(lock_name, call_args, coordinator)
        with lock(blocking):
            LOG.info('Lock "%(name)s" acquired by "%(function)s".',
                     {'name': lock_name, 'function': f.__name__})
            return f(*a, **k)

    return _synchronized


def _get_redis_backend_url():
    cipher_password = getattr(CONF.coordination, 'backend_password', None)
    if cipher_password is not None:
        # If password is needed, the password should be
        # set in config file with cipher text
        # And in this scenario, these are also needed for backend:
        # {backend_type}://[{user}]:{password}@{ip}:{port}.
        plaintext_password = cryptor.decode(cipher_password)
        # User could be null
        backend_url = '{backend_type}://{user}:{password}@{server}' \
            .format(backend_type=CONF.coordination.backend_type,
                    user=CONF.coordination.backend_user,
                    password=plaintext_password,
                    server=CONF.coordination.backend_server)

    else:
        backend_url = '{backend_type}://{server}' \
            .format(backend_type=CONF.coordination.backend_type,
                    server=CONF.coordination.backend_server)
    return backend_url


class ConsistentHashing(Coordinator):
    GROUP_NAME = 'partitioner_group'

    def __init__(self):
        super(ConsistentHashing, self). \
            __init__(agent_id=CONF.host, prefix="")

    def join_group(self):
        try:
            self.coordinator.join_partitioned_group(self.GROUP_NAME)
        except coordination.MemberAlreadyExist:
            LOG.info('Member %s already in partitioner_group' % CONF.host)

    def get_task_executor(self, task_id):
        part = partitioner.Partitioner(self.coordinator, self.GROUP_NAME)
        members = part.members_for_object(task_id)
        for member in members:
            LOG.info('For task id %s, host should be %s' % (task_id, member))
            return member.decode('utf-8')

    def register_watcher_func(self, on_node_join, on_node_leave):
        self.coordinator.watch_join_group(self.GROUP_NAME, on_node_join)
        self.coordinator.watch_leave_group(self.GROUP_NAME, on_node_leave)

    def watch_group_change(self):
        self.coordinator.run_watchers()


class GroupMembership(Coordinator):

    def __init__(self, agent_id):
        super(GroupMembership, self). \
            __init__(agent_id=agent_id, prefix="")

    def create_group(self, group):
        # Create the group
        try:
            self.coordinator.create_group(group.encode()).get()
        except coordination.GroupAlreadyExist:
            LOG.info("GROUP {0} already exist".format(group))

    def delete_group(self, group):
        # Create the group
        try:
            self.coordinator.delete_group(group.encode()).get()
        except coordination.GroupNotCreated:
            LOG.info("GROUP {0} Group not created".format(group))
        except coordination.GroupNotEmpty:
            LOG.info("GROUP {0} Group not Empty".format(group))
        except coordination.ToozError:
            LOG.info("GROUP {0} Internal Error while delete".format(group))

    def join_group(self, group):
        try:
            # Join the group
            self.coordinator.join_group(group.encode()).get()
        except coordination.MemberAlreadyExist:
            LOG.info('Member %s already in group' % group)

    def leave_group(self, group):
        try:
            # Join the group
            self.coordinator.leave_group(group.encode()).get()
        except coordination.GroupNotCreated:
            LOG.info('Group %s not created' % group)

    def get_members(self, group):
        try:
            # Join the group
            return self.coordinator.get_members(group.encode()).get()
        except coordination.GroupNotCreated:
            LOG.info('Group %s not created' % group)

        return None

    def register_watcher_func(self, group, on_process_join, on_process_leave):
        self.coordinator.watch_join_group(group.encode(), on_process_join)
        self.coordinator.watch_leave_group(group.encode(), on_process_leave)

    def watch_group_change(self):
        self.coordinator.run_watchers()
