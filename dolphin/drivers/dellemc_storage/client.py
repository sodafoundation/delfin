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

import json
import PyU4V
from PyU4V import U4VConn

from dolphin import exception
from oslo_log import log

LOG = log.getLogger(__name__)

SUPPORTED_VERSION='90'

def get_connection(access_info):
    array_id = access_info.get('extra_attributes', {}).\
                            get('array_id', None)
    if not array_id:
        raise exception.InvalidInput(reason='Input array_id is missing')

    try:
        # Initialise PyU4V connection to Unisphere
        return PyU4V.U4VConn(
            u4v_version=SUPPORTED_VERSION,
            server_ip=access_info['host'],
            port=access_info['port'],
            verify=False,
            array_id=array_id,
            username=access_info['username'],
            password=access_info['password'])

    except Exception as err:
        LOG.error("Failed to connect to Unisphere: {}".format(err))
        raise exception.InvalidInput(reason='Invalid credentials for VMAX storage')

def get_version(conn):
    try:
        # Get the Unisphere version
        return conn.common.get_uni_version()

    except Exception as err:
        LOG.error("Failed to get version from vmax: {}".format(err))
        raise exception.StorageBackendException(
            reason='Failed to get version from VMAX')

def get_model(conn, symmetrix_id):
    try:
        # Get the Unisphere model
        uri = "/system/symmetrix/" + symmetrix_id
        model = conn.common.get_request(uri, "")
        return model['symmetrix'][0]['model']
    except Exception as err:
        LOG.error("Failed to get model from vmax: {}".format(err))
        raise exception.StorageBackendException(
            reason='Failed to get model from VMAX')

def get_storage_capacity(conn, symmetrix_id):
    try:
        uri = "/" + SUPPORTED_VERSION + "/sloprovisioning/symmetrix/" + symmetrix_id
        storage_info = conn.common.get_request(uri, "")
        return storage_info['system_capacity']
    except Exception as err:
        LOG.error("Failed to get model from vmax: {}".format(err))
        raise exception.StorageBackendException(
            reason='Failed to get capacity from VMAX')

def get_pool_metrics(conn, symmetrix_id, start, end, pool):
    # Get pool metrics
    uri = "/performance/ThinPool/metrics"
    payload = {
        "startDate": start,
        "endDate": end,
        "symmetrixId": symmetrix_id,
        "poolId": pool,
        "dataFormat": "Average",
        "metrics": [
            "TotalPoolCapacity",
            "UsedPoolCapacity"
        ]
    }
    try:
        pools = conn.request(uri, "POST", request_object=payload)
        return pools[0]['resultList']['result'][0]
    except Exception as err:
        LOG.error("Failed to get pool metrics from vmax: {}".format(err))
        raise exception.StorageBackendException(
            reason='Failed to get pool metrics from VMAX')

def list_pools(conn, symmetrix_id):
    # Get list of pool names
    payload = {
        "symmetrixId": symmetrix_id
    }
    uri = "/performance/ThinPool/keys"
    try:
        pools_info = conn.request(uri, "POST", request_object=payload)

        pool_list = []
        pools = pools_info[0].get('poolInfo')
        for pool in pools:
            capacity = get_pool_metrics(
                conn,
                symmetrix_id,
                pool["lastAvailableDate"],
                pool["lastAvailableDate"],
                pool["poolId"]
            )
            # Capacity from GB to Bytes
            total_capacity = capacity['TotalPoolCapacity'] * 1000 * 1000 * 1000
            used_capacity = capacity['UsedPoolCapacity'] * 1000 * 1000 * 1000
            p = {
                "id":"",
                "name": pool["poolId"],
                "storage_id": symmetrix_id,
                "original_id": "",
                "description":"",
                "status": "",
                "storage_type": "",
                "total_capacity": total_capacity,
                "used_capacity": used_capacity,
                "free_capacity": total_capacity - used_capacity,
            }
            pool_list.append(p)

        return pool_list

    except Exception as err:
        LOG.error("Failed to get pool metrics from vmax: {}".format(err))
        raise exception.StorageBackendException(
            reason='Failed to get pool metrics from VMAX')
