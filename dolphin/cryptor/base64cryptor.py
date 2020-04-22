import base64
from cryptor import basecryptor


class Base64(basecryptor.ICryptor):

    @staticmethod
    def encode(data):
        return base64.b64encode(data.encode())

    @staticmethod
    def decode(data):
        return base64.b64decode(data)
