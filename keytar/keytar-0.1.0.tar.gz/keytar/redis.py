"""Redis wrapper"""

import json

class Redis:
    """Redis wrapper"""
    __database = False

    def __init__(self, db):
        self.__database = db

    def get(self, _, key):
        """Get item for key"""
        res = self.__database.get(key.get_primary_value())

        if res:
            return json.loads(res)

        return res

    def set(self, _, key, item):
        """Set item """
        self.__database.set(key.get_primary_value(), json.dumps(item))
