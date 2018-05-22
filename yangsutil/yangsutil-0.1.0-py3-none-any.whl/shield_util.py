from Crypto.Cipher import AES
from Crypto import Random
import base64
import hashlib


class ShieldUtil:
    SHA224 = 0
    SHA256 = 1
    SHA384 = 2
    SHA512 = 3

    # AES
    @staticmethod
    def encrypt_aes(iv, key, item, is_random=False):
        cipher = AES.new(key, AES.MODE_CFB, iv)

        encrypt_text = cipher.encrypt(str(item))
        if is_random is True:
            encrypt_text = iv + encrypt_text

        encrypted = base64.b64encode(encrypt_text)
        return encrypted.decode('utf-8')

    @staticmethod
    def random_encrypt_aes(key, item):
        iv = Random.new().read(AES.block_size)
        return ShieldUtil.encrypt_aes(
            iv=iv,
            key=key,
            item=item,
            is_random=True
        )

    @staticmethod
    def decrypt_aes(iv, key, item, is_random=False):
        cipher = AES.new(key, AES.MODE_CFB, iv)

        enc = item
        if is_random is False:
            enc = base64.b64decode(item)

        decrypted = cipher.decrypt(enc)
        return decrypted.decode('utf-8')

    @staticmethod
    def random_decrypt_aes(key, item):
        enc = base64.b64decode(item)

        return ShieldUtil.decrypt_aes(
            iv=enc[:16],
            key=key,
            item=enc[16:],
            is_random=True
        )

    # SHA
    @staticmethod
    def hash(item, hash_type=1):

        if hash_type == 0:
            hash_obj = hashlib.sha3_224
        elif hash_type == 1:
            hash_obj = hashlib.sha3_256
        elif hash_type == 2:
            hash_obj = hashlib.sha3_384
        elif hash_type == 3:
            hash_obj = hashlib.sha3_512
        else:
            return None

        return hash_obj(bytes(item, 'utf-8')).hexdigest()
