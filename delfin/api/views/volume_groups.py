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
import copy


def build_volume_groups(volume_groups):
    # Build list of volume groups
    views = [build_volume_group(volume_group)
             for volume_group in volume_groups]
    return dict(volume_groups=views)


def build_volume_group(volume_group):
    view = copy.deepcopy(volume_group)
    volumes = view['volumes']
    view['volumes'] = []
    if volumes:
        view['volumes'] = volumes.split(',')
    return dict(view)
