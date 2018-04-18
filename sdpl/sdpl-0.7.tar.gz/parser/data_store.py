__author__ = 'Bohdan Mushkevych'

from schema.io import load
from schema.sdpl_schema import DataRepository
from parser.relation import Relation


class DataStore(object):
    """ module links relation with the data source/sink (table name and repository)
        relation is versioned - i.e. fields with higher version than provided are excluded from processing
    """

    def __init__(self, table_name:str, data_repo_path:str, relation:Relation, **kwargs):
        self.table_name = table_name.strip('\'')
        self.relation = relation
        self.kwargs = kwargs

        self.data_repo_path = None
        self._data_repo = None
        if data_repo_path:
            self.data_repo_path = data_repo_path.strip('\'')
            self._data_repo = load(self.data_repo_path)

    @property
    def data_repository(self) -> DataRepository:
        return self._data_repo
