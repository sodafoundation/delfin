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

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

from dolphin.cryptor import basecryptor


class Aes(basecryptor.ICryptor):
    key = b'3B#98B%F3D$482D!'

    @staticmethod
    def encode(data):
        length = 16
        count = len(data)
        if count % length != 0:
            add = length - (count % length)
        else:
            add = 0
        data = data + ('\0' * add)
        cryptor = AES.new(Aes.key, AES.MODE_ECB)
        cipher_text = cryptor.encrypt(data)
        return b2a_hex(cipher_text)

    @staticmethod
    def decode(data):
        cryptor = AES.new(Aes.key, AES.MODE_ECB)
        plain_text = cryptor.decrypt(a2b_hex(data))
        return plain_text.rstrip(b'\0')
