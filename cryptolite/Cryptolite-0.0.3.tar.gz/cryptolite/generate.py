"""
Generates things that need to be random,
including salt, token and password values.
"""

import os
from cryptolite.byte_array import to_hex, to_base64

__author__ = "David Carboni"

"""The length for tokens."""
TOKEN_BITS = 256

"""The length for salt values."""
SALT_BYTES = 16

# Work out the right number of bytes for random tokens:
_bits_in_a_byte = 8
_token_length_bytes = TOKEN_BITS // _bits_in_a_byte

# Characters for pasword generation:
passwordCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def byte_array(length):
    """
    Instantiates and populates a byte array of the specified length.

    :param length: The length of the array.
    :return: os.urandom(length)
    """
    return bytearray(os.urandom(length))


def token():
    """
    Generates a random token.

    :return: A 256-bit (32 byte) random token as a hexadecimal string.
    """
    token_bytes = byte_array(_token_length_bytes)
    return to_hex(token_bytes)


def password(length):
    """
    Generates a random password.

    :param length: The length of the password to be returned.
    :return: A password of the specified length, selected from ``passwordCharacters``.
    """

    result = ""
    values = byte_array(length)
    # We use a modulus of an increasing index rather than of the byte values
    # to avoid certain characters coming up more often.
    index = 0

    for i in range(length):
        index += values[i]
        index = index % len(passwordCharacters)
        result += passwordCharacters[index]

    return result


def salt():
    """
    Generates a random salt value.

    If a salt value is needed by an API call,
    the documentation of that method should reference this method. Other than than,
    it should not be necessary to call this in normal usage of this library.

    :return: A random salt value of SALT_BYTES length, as a base64-encoded
    string (for easy storage).
    """
    salt_bytes = byte_array(SALT_BYTES)
    return to_base64(salt_bytes)
