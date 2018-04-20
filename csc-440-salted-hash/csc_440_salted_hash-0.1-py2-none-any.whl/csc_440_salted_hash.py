import os
import binascii
import hashlib


def make_salted_hash(password, salt=None):
    """
    Create a salted hash password

    :param password
    :param salt

    """
    if not salt:
        salt = os.urandom(64)
    d = hashlib.sha512()
    d.update(salt[:32])
    d.update(password)
    d.update(salt[32:])
    return binascii.hexlify(salt) + d.hexdigest()


def check_hashed_password(password, salted_hash):
    """
    Check a salted hash password

    :param password
    :param salted_hash

        """
    salt = binascii.unhexlify(salted_hash[:128])
    return make_salted_hash(password, salt) == salted_hash