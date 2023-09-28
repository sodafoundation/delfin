# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime
import os
import re
import time

import six

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from scp import SCPClient

from oslo_log import log as logging
from oslo_utils import units

LOG = logging.getLogger(__name__)


class Tools(object):

    def time_str_to_timestamp(self, time_str, time_pattern):
        """ Time str to time stamp conversion
        """
        time_stamp = ''
        if time_str:
            time_array = time.strptime(time_str, time_pattern)
            time_stamp = int(time.mktime(time_array) * units.k)
        return time_stamp

    def timestamp_to_time_str(self, time_stamp, time_pattern):
        """ Time stamp to time str conversion
        """
        time_str = ''
        if time_stamp:
            time_stamp = time_stamp / units.k
            time_array = time.localtime(time_stamp)
            time_str = time.strftime(time_pattern, time_array)
        return time_str

    @staticmethod
    def timestamp_to_utc_time_str(time_stamp, time_pattern):
        """ Time stamp to time str conversion
        """
        time_str = ''
        if time_stamp:
            time_stamp = time_stamp / units.k
            dateArray = datetime.datetime.utcfromtimestamp(time_stamp)
            time_str = dateArray.strftime(time_pattern)
        return time_str

    @staticmethod
    def change_capacity_to_bytes(unit):
        unit = unit.upper()
        if unit == 'TB':
            res = units.Ti
        elif unit == 'GB':
            res = units.Gi
        elif unit == 'MB':
            res = units.Mi
        elif unit == 'KB':
            res = units.Ki
        else:
            res = 1
        return int(res)

    @staticmethod
    def get_capacity_size(value):
        capacity = 0
        if value and value != '' and value != '-' and value != '0B':
            if value.isdigit():
                capacity = float(value)
            else:
                unit = value[-2:]
                capacity = float(value[:-2]) * int(
                    Tools.change_capacity_to_bytes(unit))
        return capacity

    @staticmethod
    def split_value_map_list(value_info, map_list, is_mapping=False,
                             is_alert=False, split=":"):
        detail_array = value_info.split('\r\n')
        value_map = {}
        temp_key = ''
        for detail in detail_array:
            if detail:
                string_info = detail.split(split + " ")
                key = string_info[0].replace(' ', '').strip()
                value = ''
                if len(string_info) > 1 or is_mapping:
                    for string in string_info[1:]:
                        value = string.replace('""', '')
                    value_map[key] = value
                if is_alert and key and len(string_info) > 1:
                    temp_key = key
                    continue
                if is_alert and temp_key and 'entries' not in detail:
                    if len(string_info) > 1:
                        value_map[temp_key] += string_info[1]
                    elif len(string_info) == 1:
                        value_map[temp_key] += string_info[0]
            else:
                if value_map != {}:
                    map_list.append(value_map)
                value_map = {}
        if value_map != {}:
            map_list.append(value_map)
        return map_list

    @staticmethod
    def get_numbers_in_brackets(source_info, pattern_str):
        """Get the contents in brackets through regular expressions.
           source_info：Source data, example: "collect time (1583012100)"
           pattern_str: regular expression. example："\\(\\d+\\)"
        """
        object_info = ''
        object_infos = re.findall(pattern_str, source_info)
        if object_infos:
            object_info = object_infos[0].replace('(', '').replace(')', '')
        return object_info

    @staticmethod
    def remove_file_with_same_type(file_name, file_path):
        file_type = '%s_%s_%s' % (file_name.split('_')[0],
                                  file_name.split('_')[1],
                                  file_name.split('_')[2])
        path_dir = os.listdir(file_path)
        for file in path_dir:
            if file_type in file:
                local_file = '%s%s' % (file_path, file)
                os.remove(local_file)

    @staticmethod
    def get_remote_file_to_xml(ssh, file, local_path, remote_path):
        root_node = None
        local_file = '%s%s' % (local_path, file)
        try:
            scp_client = SCPClient(ssh.get_transport(),
                                   socket_timeout=15.0)
            remote_file = '%s%s' % (remote_path, file)
            scp_client.get(remote_file, local_path)
            root_node = open(local_file).read()
            root_node = ET.fromstring(root_node)
        except Exception as e:
            err_msg = "Failed to copy statics file: %s" % \
                      (six.text_type(e))
            LOG.error(err_msg)
        finally:
            if os.path.exists(local_file):
                Tools.remove_file_with_same_type(file, local_path)
        return root_node
