# -*- coding: utf-8 -*-
"""
    Tools for create a instance of a MongoDB client

"""
from pymongo import MongoClient


class Engine:
    default_config = {
        'HOST': 'localhost',
        'PORT': 27017,
        'USER': None,
        'AUTH': None,
        'DATABASE': 'general',
        'COLLECTION': 'general'
    }

    URI = 'mongodb://{}:{}'
    URI_WITH_AUTH = 'mongodb://{}:{}@{}:{}'

    def __init__(self, host=None, port=None, user=None, auth=None, database=None, collection=None):
        """
            Client for a MongoDB client instance.

            Create a object is has a connection-pooling built in.

            If an operation fails because a network error
            :class `~pymongo.errors.ConnectionFailure` is raised.
        """
        if not host:
            host = self.default_config['HOST']

        if not port:
            port = self.default_config['PORT']

        if not isinstance(port, int):
            raise TypeError("The port be an instances of int")

        if user and not auth:
            raise TypeError("The auth param is required")

        if user:
            self.instance_uri = self.URI_WITH_AUTH.format(host, port, user, auth)
        else:
            self.instance_uri = self.URI.format(host, port)

        client = MongoClient(self.instance_uri)

        if not database:
            database = self.default_config['DATABASE']

        database = client[database]

        if not collection:
            collection = self.default_config['COLLECTION']

        self.collection = database[collection]

    def insert_registry(self, document, return_id=None):
        """
           Insert a single document
           :Parameters:
            - `document`: The document to insert. Must be a mutable mapping type .
               If the document does not have an _id field onee will be added automatically.
            - `return_id': Indicates if the inserted document's _id is returned inn the function
        """
        result = self.collection.insert_one(document)

        if return_id:
            return result.inserted_id
