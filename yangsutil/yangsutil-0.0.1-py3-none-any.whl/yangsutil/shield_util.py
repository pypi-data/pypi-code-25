from Crypto.Cipher import AES
from Crypto import Random
import base64


class ShieldUtil:
    @staticmethod
    def encrypt_aes(key, item):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encrypted = base64.b64encode(iv + cipher.encrypt(str(item)))
        return encrypted.decode('utf-8')

    @staticmethod
    def decrypt_aes(key, crypt_text):
        enc = base64.b64decode(crypt_text)
        cipher = AES.new(key, AES.MODE_CFB, enc[:16])
        decrypted = cipher.decrypt(enc[16:])
        return decrypted.decode('utf-8')
