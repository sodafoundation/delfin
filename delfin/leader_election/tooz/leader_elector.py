# Copyright 2021 The SODA Authors.
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

"""Leader elector is leased based leader election"""

import threading

from oslo_log import log
from oslo_utils import timeutils

from delfin.coordination import LeaderElectionCoordinator
from delfin.leader_election.interface import LeaderElector

LOG = log.getLogger(__name__)


class Elector(LeaderElector):

    def __init__(self, callbacks, leader_election_key):
        key = leader_election_key.encode('ascii')
        super(Elector, self).__init__(callbacks, key)

        self._coordinator = None
        self.leader = False
        self._stop = threading.Event()
        self._runner = None

    def run(self):
        if self._coordinator:
            return

        self._stop.clear()

        self._coordinator = LeaderElectionCoordinator()
        self._coordinator.start()

        self._coordinator.ensure_group(self.election_key)
        self._coordinator.join_group()

        self._coordinator. \
            register_on_start_leading_callback(self.
                                               callbacks.on_started_leading)

        # Register internal callback to notify being a leader
        self._coordinator. \
            register_on_start_leading_callback(self.set_leader_callback)

        while not self._stop.is_set():
            with timeutils.StopWatch() as w:
                LOG.debug("sending heartbeats for leader election")
                wait_until_next_beat = self._coordinator.send_heartbeat()

            ran_for = w.elapsed()
            has_to_sleep_for = wait_until_next_beat - ran_for
            if has_to_sleep_for < 0:
                LOG.warning(
                    "Heart beating took too long to execute (it ran for"
                    " %0.2f seconds which is %0.2f seconds longer than"
                    " the next heartbeat idle time). This may cause"
                    " timeouts (in locks, leadership, ...) to"
                    " happen (which will not end well).", ran_for,
                    ran_for - wait_until_next_beat)

            # Check if coordinator is still a leader
            if self.leader and not self._coordinator.is_still_leader():
                self.on_stopped_leading()
                self.leader = False
                return
            self._coordinator.start_leader_watch()

            if self.leader:
                # Adjust time for leader
                has_to_sleep_for = has_to_sleep_for / 2

            LOG.debug('resting after leader watch as leader=%(leader)s '
                      'for heartbeat timeout of %(timeout)s sec',
                      {'timeout': has_to_sleep_for, 'leader': self.leader})

            self._stop.wait(has_to_sleep_for)
        LOG.error("Returning from leader loop -----------------> ")

    def set_leader_callback(self, *args, **kwargs):
        self.leader = True

    def cleanup(self):
        self._stop.set()

        if self._coordinator:
            self._coordinator.stop()
            self._coordinator = None

        if self.leader:
            self.on_stopped_leading()
            self.leader = False

    def on_stopped_leading(self):
        self.callbacks.on_stopped_leading()
