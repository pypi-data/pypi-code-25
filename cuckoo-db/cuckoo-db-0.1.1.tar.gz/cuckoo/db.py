from playhouse.postgres_ext import PostgresqlExtDatabase

import json
import os


class Database(object):
    __DB__ = None
    
    @classmethod
    def get_instance(cls, cfg_path):
        if Database.__DB__ is None:
            Database.set_db(cfg_path)
        
        return Database.__DB__
        
    @classmethod
    def set_db(cls, cfg_path):
        with open(cfg_path, 'r') as infile:
            config = json.load(infile)

        Database.__DB__ = PostgresqlExtDatabase(
            database=config['db_name'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            register_hstore=False
        )