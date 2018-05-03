import logging
import pymongo
import os

from magicstore.foundation.utils.exceptions_utils import error_message

logger = logging.getLogger(__name__)


class MongoClient(object):
    client = None
    collection_name = ''

    def __init__(self):
        try:
            self.mongo_uri = os.environ['MONGO_URI']
            self.mongo_db = os.environ['MONGO_DB']

            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            logger.info("MongoDB client created.")
        except KeyError as e:
            logger.error(f'MONGO_URI or MONGO_DB is not config in the os env: {error_message(e)}')

        except Exception as e:
            logger.error(f'MongoDB client create failed: {error_message(e)}')

    def collection(self):
        return self.db[self.collection_name]

    def close(self):
        logger.info("MongoDB connection is closed.")
        self.client.close()
