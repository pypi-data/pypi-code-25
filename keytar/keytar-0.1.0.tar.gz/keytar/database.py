"""Wrapper around databases"""

from keytar.dynamo import Dynamo              # aws
from keytar.cloud_data_store import Datastore # gcp
from keytar.redis import Redis                # Redis
from keytar.mongo import Mongo                # Mongo
from keytar.db_types import AWS_DYNAMO, GCP_DATASTORE, REDIS, MONGO

class Database:
    """Interface for all databases"""
    __client = False
    __type = False

    def __init__(self, db, db_type):
        """Provide an initialized client and its type"""
        if db_type == AWS_DYNAMO:
            self.__client = Dynamo(db)
        elif db_type == GCP_DATASTORE:
            self.__client = Datastore(db)
        elif db_type == REDIS:
            self.__client = Redis(db)
        elif db_type == MONGO:
            self.__client = Mongo(db)
        else:
            raise "Invalid type"

        self.__type = db_type

    def get(self, table, key):
        """Get data for key object"""
        return self.__client.get(table, key)

    def set(self, table, key, item):
        """Set data for key"""
        return self.__client.set(table, key, item)

    def query(self, query):
        """Execute custom query"""
        if self.__type != GCP_DATASTORE:
            raise "Error, the query interface is not yet supported for aws DynamoDb"

        return self.__client.query(query)
