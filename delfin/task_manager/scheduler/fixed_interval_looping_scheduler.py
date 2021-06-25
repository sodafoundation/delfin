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

from eventlet import event
from oslo_log import log
from oslo_service import loopingcall

LOG = log.getLogger(__name__)


class FixedIntervalLoopingScheduler:

    def __init__(self):
        self._abort = event.Event()
        self.jobs = dict()
        self._running = False

    def add_job(self, func, interval, job_id, initial_delay=None):
        if not self._running:
            self._running = True

        # Ignore add job if aborted
        if self._abort.ready():
            return

        def job_runner_wrapper(func, abort):
            if abort and abort.ready():
                return
            func()

        job = loopingcall.FixedIntervalLoopingCall(
            job_runner_wrapper, func, self._abort)
        job.start(interval=interval, initial_delay=initial_delay)

        self.jobs[job_id] = job
        LOG.info("Scheduled a job [%s] with time interval [%s]" % (job_id,
                                                                   interval))

    def remove_job(self, job_id):
        job = self.jobs.get(job_id)
        if job:
            job.stop()
        self.jobs.pop(job_id, None)

    def shutdown(self):
        # Abort all jobs
        self._abort.send()
        for job in self.jobs.values():
            job.stop()

        self.jobs.clear()
        self._running = False

    @property
    def running(self):
        return self._running

    def start(self):
        pass

    def get_job(self, job_id):
        return self.jobs.get(job_id)
