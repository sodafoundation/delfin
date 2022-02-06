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

from delfin.leader_election.tooz.callback import ToozLeaderElectionCallback
from delfin.leader_election.tooz.leader_elector import Elector
from delfin.task_manager.scheduler.schedule_manager import SchedulerManager

LEADER_ELECTION_KEY = "delfin-performance-metric-collection"


class LeaderElectionFactory:

    @staticmethod
    def construct_elector(plugin, leader_key=None):
        """
        Construct leader election elector based on specified plugin

        :param string plugin: required plugin for leader election
        """
        # Maintain a unique key for metric collection leader election
        leader_election_key = LEADER_ELECTION_KEY
        if leader_key:
            leader_election_key = leader_key

        scheduler_mgr = SchedulerManager()

        if plugin == "tooz":
            scheduler_mgr.start()
            # Create callback object
            callback = ToozLeaderElectionCallback.register(
                on_leading_callback=scheduler_mgr.schedule_boot_jobs,
                on_stop_callback=scheduler_mgr.stop)

            return Elector(callback, leader_election_key)
        else:
            raise ValueError(plugin)
