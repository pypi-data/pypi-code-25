from db.db_credentials import config
from db.connectors import connection_factory

DB_TYPE = 'mysql'
connector = connection_factory(DB_TYPE, **config)
