"""Interface for Mongodb"""

class Mongo:
    __database = False

    def __init__(self, db):
        self.__database = db

    def get(self, table, key):
        """Get item for key"""
        cursor = self.__database[table].find(make_key(key))
        return cursor

    def set(self, table, key, item):
        item = {**item, **make_key(key)}
        self.__database[table].insertOne(item)
        return

def make_key(key):
    return {key.get_primary_key_name(): key.get_primary_key_value()}
