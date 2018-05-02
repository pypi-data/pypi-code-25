"""
The byte_array module provides the ability to convert byte arrays to
Strings, Base-64 and hexadecimal and vice-versa.

Cryptography is mainly about manipulating byte arrays, so this class provides
the different translations you need:

- Plain-text strings need to be converted to a byte array for encryption
  and, after decryption, need to be converted from a byte array back to a
  String.
- Encrypted byte arrays look like random bytes, which means they can't be
  reliably represented as a String. The simplest way to represent arbitrary bytes
  as a String is using Base-64. This class lets you convert a byte array of
  encrypted data to Base-64 so it can be easily stored and back again so it can
  be decrypted.
- Finally, this class also allows you to transform a byte array to a
  hexadecimal String and back again. This is most useful in development when
  you need to print out values to see what's going on. Conversion from
  hexadecimal to byte array is occasionally useful, but chances are you'll use
  byte[] to hex most of the time.

The naming convention for functions is set up from the point of view of
a byte array. For example, a byte array can go:

``to_hex``

and back:

``from_hex``

The same pattern is used for each pair of methods (to/from hex, base64 and string).
"""

import binascii
import base64

__author__ = "David Carboni"


def to_hex(byte_array):
    """
    Renders the given byte array as a hex String.

    This is a convenience method useful for testing values during development.

    :param byte_array: The byte array to be represented in hex.
    :return: A hex string representation of the byte array.
    """
    result = None
    if byte_array is not None:
        result = binascii.hexlify(byte_array).decode("utf-8")
    return result


def from_hex(hex_string):
    """
    Converts the given hex string to a byte array.

    This is a convenience method useful for testing values during development.

    :param hex_string: The hex String to parse to bytes.
    :return: A byte array, as parsed from the given String
    """
    result = None
    if hex_string is not None:
        result = bytearray.fromhex(hex_string)
    return result


def to_base64(byte_array):
    """
    Encodes the given byte array as a base-64 String.

    :param byte_array: The byte array to be encoded.
    :return: The byte array encoded using base-64.
    """
    result = None
    if byte_array is not None:
        result = base64.b64encode(byte_array).decode("utf-8")
    return result


def from_base64(base64_string):
    """
    Decodes the given base-64 string to a byte array.

    :param base64_string: A base-64 encoded string.
    :return: The decoded byte array.
    """
    result = None
    if base64_string is not None:
        result = bytearray(base64.b64decode(base64_string))
    return result


def to_string(byte_array):
    """
    Converts the given byte array to a String.

    :param byte_array: The byte array to be converted to a String.
    :return: The String represented by the given bytes.
    """
    result = None
    if byte_array is not None:
        result = byte_array.decode("utf-8")
    return result


def from_string(unicode_string):
    """
    Converts the given String to a byte array.

    :param unicode_string: The String to be converted to a byte array.
    :return: A byte array representing the String.
    """
    result = None
    if unicode_string is not None:
        result = bytearray(unicode_string.encode("utf-8"))
    return result
