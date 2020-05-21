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
import uuid

import redis
from oslo_config import cfg
from oslo_log import log

from dolphin import cryptor
from dolphin import utils
from dolphin.common import constants

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class RedisClient(metaclass=utils.Singleton):
    def __init__(self):
        password = cryptor.decode(CONF.redis.password)
        self.pool = redis.ConnectionPool(host=CONF.redis.redis_ip,
                                         port=CONF.redis.redis_port,
                                         password=password,
                                         socket_connect_timeout=constants.SOCKET_CONNECT_TIMEOUT,
                                         socket_timeout=constants.SOCKET_TIMEOUT)
        self.redis_client = self.get_redis()

    def get_redis(self):
        """Get redis client

        :return: The redis client
        """
        try:
            redis_client = redis.StrictRedis(connection_pool=self.pool)
            return redis_client
        except Exception as err:
            if isinstance(err, TimeoutError) \
                    or isinstance(err, ConnectionError):
                LOG.error("connect to redis failed")
                raise err

    def acquire_lock(self, lock_name):
        """
        Acquire lock from redis

        :param lock_name: Lock name
        :return identifier: Identifier of this lock
        """
        identifier = str(uuid.uuid4())
        if self.redis_client.set(lock_name, identifier, nx=True, ex=constants.REDIS_TASK_TIMEOUT):
            return identifier
        elif not self.redis_client.ttl(lock_name):
            self.redis_client.expire(lock_name, constants.REDIS_TASK_TIMEOUT)
        time.sleep(constants.REDIS_SLEEP_TIME)
        return None

    def release_lock(self, lock_name, identifier):
        """
        Release lock from redis

        :param lock_name: Lock name
        :param identifier: Identifier of this lock
        :return bool: Whether release the lock successfully
        """
        pipeline = self.redis_client.pipeline(True)
        while True:
            try:
                pipeline.watch(lock_name)
                lock_value = self.redis_client.get(lock_name)
                if not lock_value:
                    return True
                if lock_value.decode() == identifier:
                    pipeline.multi()
                    pipeline.delete(lock_name)
                    pipeline.execute()
                    return True
                pipeline.unwatch()
                break
            except redis.exceptions.WatchError:
                LOG.error("redis pipeline watch failed.")
        return False

    def is_locked(self, lock_name):
        """
        Check whether a lock is locked

        :param lock_name: Lock name
        :return bool: Whether the lock is locked
        """
        if self.redis_client.get(lock_name) is not None:
            return True
        else:
            return False
