"""GCP Datastore

https://cloud.google.com/datastore/docs/reference/libraries
"""

import random
from google.cloud import datastore
from keytar.key import Key

class Datastore:
    """Wrapper around GCP Datastore"""
    __database = False

    def __init__(self, db):
        self.__database = db

    def get(self, table, key):
        """Get item for key"""
        key = self.__make_key(table, key)
        return self.__database.get(key)

    def query(self, query):
        """Execute a custom query"""
        query = self.__make_query(query)
        return list(query.fetch())

    def set(self, table, key, item):
        """Set an item in a table"""
        key = self.__make_key(table, key)
        return self.__database.put(make_entity(key, item))

    def random_keys(self, table, limit=10):
        """Get random keys for kind, fairly inefficient"""
        keys = [i.id() for i in self.__get_keys(table)]
        return [Key(random.choice(keys)) for i in range(0, limit)]

    def __get_keys(self, kind):
        query = self.__database.query(kind=kind).keys_only()
        return list(query.fetch())

    def __make_key(self, kind, key):
        return self.__database.key(kind, key.get_primary_key_value())

    def __make_query(self, qry):
        query = self.__database.query(kind=qry.get_table())

        where_clauses = qry.get_where_clauses()

        for i in where_clauses:
            query.add_filter(i.get_key(), i.get_operator(), i.get_value())

        return query

def make_entity(key, value):
    """Wrapper around the client's thing"""
    entity = datastore.Entity(key=key)

    # Map values
    for dict_key, dict_value in value.items():
        entity[dict_key] = dict_value

    return entity
