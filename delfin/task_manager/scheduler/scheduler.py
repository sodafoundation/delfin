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

from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:
    __instance = None

    @staticmethod
    def get_instance():
        """ Get instance of scheduler class """
        if Scheduler.__instance is None:
            Scheduler.__instance = BackgroundScheduler()
        return Scheduler.__instance

    def __init__(self):
        if Scheduler.__instance is not None:
            raise Exception("The instance of scheduler class is already"
                            "running.")
        else:
            Scheduler.__instance = self
