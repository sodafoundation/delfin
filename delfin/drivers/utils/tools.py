# Copyright 2020 The SODA Authors.
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
import time

from oslo_log import log as logging
from oslo_utils import units

LOG = logging.getLogger(__name__)


class Tools(object):

    def __init__(self):
        pass

    def get_time_stamp(self, time_str, time_pattern):
        """ Time stamp to time conversion
        """
        time_stamp = ''
        try:
            if time_str is not None:
                # Convert to time array first
                time_array = time.strptime(time_str, time_pattern)
                # Convert to timestamps to milliseconds
                time_stamp = int(time.mktime(time_array) * units.k)
        except Exception as e:
            LOG.error(e)

        return time_stamp

    def get_time_str(self, time_stamp, time_pattern):
        """ Time str to time stamp conversion
        """
        time_str = ''
        try:
            if time_stamp is not None:
                time_stamp = time_stamp / units.k
                timeArray = time.localtime(time_stamp)
                time_str = time.strftime(time_pattern, timeArray)
        except Exception as e:
            LOG.error(e)

        return time_str
