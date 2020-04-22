from cryptor import descryptor, base64cryptor, aescryptor


class CryptorFactory(object):
    cryptors = {'base64': base64cryptor.Base64, 'aes': aescryptor.Aes, 'des': descryptor.Des}

    @staticmethod
    def get(cryptor_type='base64'):
        if cryptor_type in CryptorFactory.cryptors.keys():
            return CryptorFactory.cryptors[cryptor_type.lower()]
        else:
            return None
