from abc import ABCMeta, abstractmethod


class ICryptor(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def encode(plain_text):
        pass

    @staticmethod
    @abstractmethod
    def decode(cipher_text):
        pass
