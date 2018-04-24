"""
To make sure we do not save passphrases unencrypted, use this function
"""

from simplecrypt import encrypt, decrypt

class Crypt:

    def encrypt(self, string, password):
        return encrypt(password, string)

    def decrypt(self, crypt, password):
        return decrypt(password, crypt).decode("utf-8")