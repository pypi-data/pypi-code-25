"""Encrypt stirng

This module supply the encryption of the string.
"""

import hashlib

WORDS = ("abcdefghijkmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
         "_$@#!%^*&:?;=_")


def encrypt(string, encry_type="sha224"):
    """Encrypt password.

    >>> encrypt('hogehoge') == encrypt('hogehoge')
    True
    """
    _encrypt = eval("hashlib.%s()" % encry_type)
    try:
        encry = _encrypt
    except ImportError:
        encry = hashlib.sha224()
    encry.update(string)
    return encry.hexdigest()
