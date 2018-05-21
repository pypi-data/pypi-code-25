__author__ = 'Brennon Bortz'

import pymongo

import eim.tools.document
import eim.tools.database

def connect(username, password):
    """
    Connects to the Emotion in Motion database and authenticates as the public, read-only `eim` user.

    :return: The `eim` database on the Emotion in Motion database server.
    :rtype: pymongo.Database
    """

    # Create client, connect to database, and authenticate
    client = pymongo.MongoClient('db0.musicsensorsemotion.com')
    db = client.eim
    db.authenticate(username, password)

    return db
