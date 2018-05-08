import logging

from magicstore.repository.mongo_client import MongoClient

logger = logging.getLogger(__name__)


class CurrenciesHistorical(MongoClient):
    collection_name = 'currencies_historical'

    def bitcoin(self):
        return self.collection().find({"currency": "bitcoin"})
