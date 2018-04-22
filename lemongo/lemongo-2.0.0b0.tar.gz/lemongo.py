"""Provides a unified PyMongo interface for LeMaster plugins."""


from argparse import ArgumentParser as _ArgumentParser
from logging import getLogger as _getLogger

from pymongo import MongoClient as _MongoClient


_DEFAULT_CLIENT_VALUE = None
_client = _DEFAULT_CLIENT_VALUE

_parser = _ArgumentParser(fromfile_prefix_chars='@', add_help=False)

_parser.add_argument(
    '-u', '--mongodb-uri', help='MongoDB connection URI')

_logger = _getLogger(__name__)


def _reset_module_state():
    global _client

    _client = _DEFAULT_CLIENT_VALUE


def get_client():
    """Return a MongoClient instance."""
    global _client

    if not _client:
        args, _ = _parser.parse_known_args()
        _client = _MongoClient(args.mongodb_uri)
        _logger.debug('A new client was created: %s', _client)

    return _client
