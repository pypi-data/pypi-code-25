import re
import hashlib
import base64
from struct import unpack

from Cryptodome.Cipher import AES

#: default jenkins magic
MAGIC = b'::::MAGIC::::'
#: by default
BLOCK_SIZE = 16
#: appears to be a random seed, but jenkins knows a drill
IV = '\x00' * BLOCK_SIZE


def pad(text: bytes, block_size=BLOCK_SIZE):
    size = (block_size - len(text) % block_size)
    return text + b'\x0c' * size


class JenkinsCipher(object):
    def __init__(self, master_key: bytes, hudson_secret_key: bytes):
        """
        Initiate jenkins cipher object with master and hudson secret keys
        for further encryption / decryption procedures

        :param master_key: jenkins master key
        :param hudson_secret_key: hudson secret key
        :raises AssertionError:
            - if MAGIC was not found in processed data
        """
        hashed_master_key = hashlib.sha256(master_key).digest()[:BLOCK_SIZE]
        cipher = AES.new(hashed_master_key, AES.MODE_ECB)
        result = cipher.decrypt(hudson_secret_key)
        assert MAGIC in result

        key = result[:-16]
        self.cipher_key = key[:16]

    @staticmethod
    def _is_new(raw) -> bool:
        """
        Detects if data has been encrypted with new approach

        :param bytes raw: encrypted string
        :return: True if data was encrypted with new approach
        """
        return base64.decodebytes(raw)[0] == 1

    def decrypt(self, encrypted_text: bytes) -> str:
        """
        Decrypts jenkins ``password_hash`` given in base64 encoded string to
        plain password

        :param encrypted_text: base64 encoded password hash
            .. note::

                password hash should be in bytes form not in base64 encoded
                string format.

        :return: plain password
        :raises AssertionError:
            - if MAGIC was not found in decrypted data taken from
              ``encrypted_text``
        """
        if self._is_new(encrypted_text):
            block = base64.decodebytes(encrypted_text)[1:]
            iv_length, *_ = unpack('>I', block[:4])

            #: strip iv length int block
            block = block[4:]
            #: using big-endian
            data_length, *_ = unpack('>I', block[:4])

            #: strip data length int block
            block = block[4:]
            iv = block[:iv_length]
            block = block[iv_length:]
            o = AES.new(self.cipher_key, AES.MODE_CBC, iv)
            decrypted_p = o.decrypt(block)
            padding = decrypted_p[-1]
            if padding > 0x10:
                raise ValueError("Input is not padded or padding is corrupt")
            return decrypted_p[:len(decrypted_p) - padding].decode('utf-8')
        else:
            cipher = AES.new(self.cipher_key, AES.MODE_ECB)
            raw = cipher.decrypt(encrypted_text)
            assert MAGIC in raw

        return re.split(MAGIC.decode('utf-8'), raw.decode('utf-8'), 1)[0]

    def encrypt(self, plain_text: str) -> bytes:
        """
        Encrypt ``plain`` string with jenkins hudson secret key

        :param plain_text: plain text to encrypt
        :return: encrypted text

        .. note::

            encrypted text are not encoded to base64, so please pack it after
        """
        cipher = AES.new(self.cipher_key, AES.MODE_ECB)
        message = pad(plain_text.encode('utf-8') + MAGIC)
        return cipher.encrypt(message)
