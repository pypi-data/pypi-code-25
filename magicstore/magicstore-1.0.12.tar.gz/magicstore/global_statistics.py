import logging

from magicstore.repository.mongo_client import MongoClient

logger = logging.getLogger(__name__)


class GlobalStatistics(MongoClient):
    collection_name = 'global_statistics'

    def all(self):
        return self.collection().find()
