from __future__ import absolute_import
from __future__ import print_function

import six
import sys

def to_bytes(s, encoding="utf-8"):
    """
    Converts the string to a bytes type, if not already.

    :s: the string to convert to bytes
    :returns: `str` on Python2 and `bytes` on Python3.
    """
    if isinstance(s, six.binary_type):
        return s
    else:
        return six.text_type(s).encode(encoding)

def to_text(s, encoding="utf-8"):
    """
    Converts the bytes to a text type, if not already.

    :s: the bytes to convert to text
    :returns: `unicode` on Python2 and `str` on Python3.
    """
    if isinstance(s, six.text_type):
        return s
    else:
        return six.binary_type(s).decode(encoding)

def _check_len(a, b):
    """
    Raises an exception if the two values do not have the same
    length. This is useful for validating preconditions.

    :a: the first value
    :b: the second value
    :raises ValueError: if the sizes do not match
    """
    if len(a) != len(b):
        msg = "Length must be {}. Got {}".format(len(a), len(b))
        raise ValueError(msg)
