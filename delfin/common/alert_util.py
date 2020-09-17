# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2010-2011 OpenStack Foundation
# Copyright 2012 Justin Santa Barbara
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def fill_storage_attributes(alert_model, storage):
    """ Fills storage attributes for alert model """
    alert_model['storage_id'] = storage['id']
    alert_model['storage_name'] = storage['name']
    alert_model['vendor'] = storage['vendor']
    alert_model['model'] = storage['model']
    alert_model['serial_number'] = storage['serial_number']


def is_alert_in_time_range(query_para, occur_time):
    # query_para contains optional begin_time and end_time
    # This function checks for their existence and validates if occur_time
    # falls in begin_time and end_time range
    if not query_para:
        return True
    begin_time = None
    end_time = None
    try:
        if query_para.get('begin_time'):
            begin_time = int(query_para.get('begin_time'))

        if query_para.get('end_time'):
            end_time = int(query_para.get('end_time'))
    except Exception:
        LOG.warning("Invalid query parameters received, ignoring them")
        return True

    if begin_time is not None and end_time is not None:
        if begin_time <= occur_time <= end_time:
            return True
    elif begin_time is not None and begin_time <= occur_time:
        return True
    elif end_time is not None and end_time >= occur_time:
        return True

    return False
