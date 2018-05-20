"""Query class"""
from keytar.where import FilterClause

class Query:
    __table = False
    __where_clauses = []

    def __init__(self, table):
        self.__table = table

    def add_where(self, key, value, operator):
        self.__where_clauses.append(FilterClause(key, value, operator))
        return self

    def get_table(self):
        return self.__table

    def get_where_clauses(self):
        return self.__where_clauses
