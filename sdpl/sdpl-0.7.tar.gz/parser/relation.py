__author__ = 'Bohdan Mushkevych'

from schema.io import load
from schema.sdpl_schema import MIN_VERSION_NUMBER, Schema


class Relation(object):
    """ module links relation name with the SDPL schema
        relation is versioned - i.e. fields with higher version than provided are excluded from processing
    """

    def __init__(self, name, schema_path, version=MIN_VERSION_NUMBER, **kwargs):
        self.name = name
        self.version = version
        self.kwargs = kwargs

        self.schema_path = None
        self._schema = None
        if schema_path:
            self.schema_path = schema_path.strip('\'')
            self._schema = load(self.schema_path)

    @property
    def schema(self) -> Schema:
        return self._schema
