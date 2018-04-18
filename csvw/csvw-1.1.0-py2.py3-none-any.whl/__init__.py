# csvw - https://w3c.github.io/csvw/primer/

from .metadata import (TableGroup, Table, Column, ForeignKey,
    Link, NaturalLanguage, Datatype)

from .dsv import (UnicodeWriter,
    UnicodeReader, UnicodeReaderWithLineNumber, UnicodeDictReader, NamedTupleReader,
    iterrows, rewrite)

__all__ = [
    'TableGroup',
    'Table', 'Column', 'ForeignKey',
    'Link', 'NaturalLanguage',
    'Datatype',
    'UnicodeWriter',
    'UnicodeReader', 'UnicodeReaderWithLineNumber', 'UnicodeDictReader', 'NamedTupleReader',
    'iterrows', 'rewrite',
]

__title__ = 'csvw'
__version__ = '1.1.0'
__author__ = 'Robert Forkel'
__license__ = 'Apache 2.0, see LICENSE'
__copyright__ = 'Copyright (c) 2018 Robert Forkel'
