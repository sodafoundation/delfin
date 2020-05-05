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

import redis
from oslo_log import log
from oslo_config import cfg

from dolphin import cryptor
from dolphin.common import constants
from dolphin import utils

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

    def has_key(self, key_name):
        """Check whether the key is in redis

        :param key_name: Key name
        :return: Whether the key is in redis
        """
        if self.redis_client.get(key_name) is None:
            return False
        else:
            return True

    def add_key(self, key_name, value="", expire=None):
        """Add a key-value pair to redis

        :param key_name: Key name
        :param value: The value of the key
        :param expire: The time to expire in seconds
        """
        self.redis_client.set(key_name, value, ex=expire)

    def remove_key(self, key_name):
        """Remove a key-value pair from redis

        :param key_name: Key name
        """
        self.redis_client.delete(key_name)
