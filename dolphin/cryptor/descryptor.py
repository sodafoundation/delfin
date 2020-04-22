from Crypto.Cipher import DES
from binascii import b2a_hex, a2b_hex
from cryptor import basecryptor


class Des(basecryptor.ICryptor):
    key = 'E75-B#68'

    @staticmethod
    def encode(data):
        generator = DES.new(Des.key, DES.MODE_ECB)
        length = 8
        count = len(data)
        if count % length != 0:
            add = length - (count % length)
        else:
            add = 0
        data = data + ('\0' * add)
        encrypted = generator.encrypt(data)
        return b2a_hex(encrypted)

    @staticmethod
    def decode(data):
        generator = DES.new(Des.key, DES.MODE_ECB)
        result = generator.decrypt(a2b_hex(data))
        return result.rstrip(b'\0')
