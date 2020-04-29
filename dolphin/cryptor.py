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
        return base64.b64encode(data.encode())

    @staticmethod
    def decode(data):
        return base64.b64decode(data)


_cryptor = importutils.import_class(CONF.dolphin_cryptor)


def encode(plain_text):
    return _cryptor.encode(plain_text)


def decode(cipher_text):
    return _cryptor.decode(cipher_text)
