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

from delfin.common import constants


class ViewBuilder(object):

    def show(self, access_info):
        access_info_dict = access_info.to_dict()
        for access in constants.ACCESS_TYPE:
            if access_info.get(access):
                access_info[access].pop('password', None)
        return access_info_dict
