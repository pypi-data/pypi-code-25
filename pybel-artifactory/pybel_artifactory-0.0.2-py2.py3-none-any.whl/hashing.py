# -*- coding: utf-8 -*-

"""Functions for hashing BEL resources."""

import hashlib
import json
import logging

from pybel.resources import get_bel_resource

__all__ = [
    'hash_names',
    'get_bel_resource_hash',
]

log = logging.getLogger(__name__)


def _names_to_bytes(names):
    """Reproducibly converts an iterable of strings to bytes

    :param iter[str] names: An iterable of strings
    :rtype: bytes
    """
    names = sorted(names)
    names_bytes = json.dumps(names).encode('utf8')
    return names_bytes


def hash_names(names, hash_function=None):
    """Return the hash of an iterable of strings, or a dict if multiple hash functions given.

    :param iter[str] names: An iterable of strings
    :param hash_function: A hash function or list of hash functions, like :func:`hashlib.md5` or :func:`hashlib.sha512`
    :rtype: str
    """
    hash_function = hash_function or hashlib.md5
    names_bytes = _names_to_bytes(names)
    return hash_function(names_bytes).hexdigest()


def get_bel_resource_hash(location, hash_function=None):
    """Get a BEL resource file and returns its semantic hash.

    :param str location: URL of a resource
    :param hash_function: A hash function or list of hash functions, like :func:`hashlib.md5` or :code:`hashlib.sha512`
    :return: The hexadecimal digest of the hash of the values in the resource
    :rtype: str
    :raises: pybel.resources.exc.ResourceError
    """
    resource = get_bel_resource(location)

    return hash_names(
        resource['Values'],
        hash_function=hash_function
    )
