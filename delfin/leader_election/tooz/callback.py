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

from delfin.leader_election.interface import LeaderCallback


class ToozLeaderElectionCallback(LeaderCallback):

    def on_started_leading(self, *args, **kwargs):
        return self.on_started_leading_callback()

    def on_stopped_leading(self, *args, **kwargs):
        return self.on_stopped_leading_callback()
