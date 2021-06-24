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

"""Leader election interface defined"""

import six
import abc


@six.add_metaclass(abc.ABCMeta)
class LeaderCallback:

    def __init__(self):
        self.on_started_leading_callback = None
        """on_started_leading is called when elected as leader"""

        self.on_stopped_leading_callback = None
        """on_stopped_leading is called when Leader give up its leadership"""

    @abc.abstractmethod
    def on_started_leading(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def on_stopped_leading(self, *args, **kwargs):
        pass

    @classmethod
    def register(cls, on_leading_callback, on_stop_callback):
        callback = cls()
        callback.on_started_leading_callback = on_leading_callback
        callback.on_stopped_leading_callback = on_stop_callback
        return callback


@six.add_metaclass(abc.ABCMeta)
class LeaderElector:

    def __init__(self, callbacks, election_key):
        self.callbacks = callbacks
        self.election_key = election_key

    @abc.abstractmethod
    def run(self):
        """kick start leader election.
        Invoke callback.on_started_leading callback once elected as leader
        Invoke callback.on_stopped_leading callback once lose leadership

        run returns once leader losses its leadership
        """
        pass

    @abc.abstractmethod
    def cleanup(self):
        """Cleanup leader election residue
        """
        pass
