__author__ = 'Bohdan Mushkevych'

from typing import Union
from enum import Enum, unique
from yaml import YAMLObject

VARCHAR_DEFAULT_LENGTH = 256
MIN_VERSION_NUMBER = 1


# `https://pig.apache.org/docs/r0.16.0/basic.html#Data+Types+and+More`
@unique
class FieldType(Enum):
    INTEGER = 1
    LONG = 2
    FLOAT = 3
    CHARARRAY = 4  # STRING
    BYTEARRAY = 5  # BLOB
    BOOLEAN = 6
    DATETIME = 7
    ARRAY = 8
    MAP = 9
    UNSUPPORTED = 999


class Field(YAMLObject):
    """ module represents a single versioned field in the schema.
        for instance: `name chararray max_length 64 NOT NULL`
        if the field version is higher than the data repository (database) version,
        the field should be excluded from processing
    """
    yaml_tag = '!Field'

    def __init__(self, name: str, field_type: FieldType, is_nullable: bool = None, is_unique: bool = None,
                 is_primary_key: bool = None, max_length: int = None, default=None, version=MIN_VERSION_NUMBER,
                 **kwargs):
        assert version >= MIN_VERSION_NUMBER, 'Version number for field {0} must be a positive integer'.format(name)

        self.name = name
        self.field_type = field_type.name
        self.is_nullable = is_nullable
        self.is_unique = is_unique
        self.is_primary_key = is_primary_key
        self.max_length = max_length
        self.default = default
        self.version = version
        self.kwargs = kwargs

    def __eq__(self, other):
        """ compares two fields.
            NOTICE: `version` field is not considered """
        return self.name == other.name \
               and self.field_type == other.field_type \
               and self.is_nullable == other.is_nullable \
               and self.is_unique == other.is_unique \
               and self.is_primary_key == other.is_primary_key \
               and self.max_length == other.max_length \
               and self.default == other.default

    def __hash__(self):
        """ NOTICE: `version` field is not considered """
        return hash(self.name) ^ hash(self.field_type) ^ hash(self.is_nullable) ^ hash(self.is_unique) ^ \
               hash(self.is_primary_key) ^ hash(self.max_length) ^ hash(self.default)


class ArrayField(Field):
    yaml_tag = '!ArrayField'

    def __init__(self, name: str, value_type: FieldType, **kwargs):
        if 'field_type' not in kwargs:
            kwargs['field_type'] = FieldType.ARRAY
        super(ArrayField, self).__init__(name, **kwargs)
        self.value_type = value_type.name


class MapField(Field):
    yaml_tag = '!MapField'

    def __init__(self, name: str, key_type: FieldType, value_type: FieldType, **kwargs):
        if 'field_type' not in kwargs:
            kwargs['field_type'] = FieldType.MAP
        super(MapField, self).__init__(name, **kwargs)
        self.key_type = key_type.name
        self.value_type = value_type.name


class Schema(YAMLObject):
    """ module represents collection of schema fields """
    yaml_tag = '!Schema'

    def __init__(self):
        self.fields = list()

    def __eq__(self, other):
        if not isinstance(other, Schema):
            return False
        return set(self.fields) == set(other.fields)

    def __hash__(self):
        return hash(self.fields)

    def __getitem__(self, item):
        for f in self.fields:
            if f.name == item:
                return f
        raise KeyError('{0} does not match any field in the schema'.format(item))

    def __contains__(self, item):
        field_name = item.name if isinstance(item, Field) else item
        for f in self.fields:
            if f.name == field_name:
                return True
        return False

    @property
    def version(self):
        """ returns maximum field version value """
        return max([f.version for f in self.fields])


@unique
class DataType(Enum):
    CSV = 1  # comma-separated values
    TSV = 2  # tab-separated values
    BIN = 3  # binary data
    ORC = 4  # hive file format
    JSON = 5


@unique
class RepositoryType(Enum):
    FILE = 1
    DATABASE = 2


@unique
class Compression(Enum):
    NONE = 1
    GZIP = 2
    SNAPPY = 3


class DataRepository(YAMLObject):
    """ module specifies access to the data repository
        this can be: local fs, dfs, s3, rdbms database, etc
    """
    yaml_tag = '!DataRepository'

    def __init__(self, host: str, port: Union[int, str], db: str,
                 user: str, password: str, description: str,
                 data_type: DataType = DataType.CSV,
                 repo_type: RepositoryType = RepositoryType.FILE,
                 compression: Compression = Compression.NONE,
                 **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.description = description
        self.data_type = data_type.name
        self.repo_type = repo_type.name
        self.compression = compression.name
        self.kwargs = kwargs

    def __eq__(self, other):
        return self.host == other.host \
               and self.port == other.port \
               and self.db == other.db \
               and self.user == other.user \
               and self.password == other.password \
               and self.data_type == other.data_type \
               and self.repo_type == other.repo_type \
               and self.compression == other.compression \
               and self.kwargs == other.kwargs

    @property
    def is_file_type(self) -> bool:
        return self.repo_type == RepositoryType.FILE.name
