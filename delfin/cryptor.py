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

import base64
from abc import ABCMeta, abstractmethod

from oslo_config import cfg
from oslo_utils import importutils

CONF = cfg.CONF


class ICryptor(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def encode(plain_text):
        pass

    @staticmethod
    @abstractmethod
    def decode(cipher_text):
        pass


class _Base64(ICryptor):

    @staticmethod
    def encode(data):
        """Base64 encode

        :param data: The plain text that need to be encode
        :type str:
        :return cipher data: The encoded cipher text
        :type str:
        """
        return base64.b64encode(data.encode()).decode('utf-8')

    @staticmethod
    def decode(data):
        """Base64 decode

        :param data: The cipher text that need to be decode
        :type str:
        :return plain data: The decoded plain text
        :type str:
        """
        return base64.b64decode(data).decode('utf-8')


_cryptor = importutils.import_class(CONF.delfin_cryptor)


def encode(plain_text):
    return _cryptor.encode(plain_text)


def decode(cipher_text):
    return _cryptor.decode(cipher_text)
