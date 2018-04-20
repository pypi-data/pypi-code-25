from pubcontrol.config import Config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy import create_engine

from sqlalchemy.pool import StaticPool
import abc

# Changed 15.04.2018
# This is just to bring them into the namespace so that they are known, when a plugin uses the import *
# statement on this module
from sqlalchemy.dialects import sqlite, mysql
from sqlalchemy import Column, ForeignKey, DateTime, String, Text, Integer, Table, and_, or_, UnicodeText
from sqlalchemy.orm import relationship


BigInt = mysql.BIGINT()
BigInt = BigInt.with_variant(sqlite.INTEGER(), 'sqlite')

LongBlob = mysql.LONGBLOB()
LongBlob = LongBlob.with_variant(sqlite.BLOB(), 'sqlite')


class SQLDatabase:

    @property
    @abc.abstractmethod
    def engine(self):
        pass

    @property
    @abc.abstractmethod
    def session_maker(self):
        pass

    @property
    @abc.abstractmethod
    def session(self):
        return None

    @property
    @abc.abstractmethod
    def query_property(self):
        pass

    @abc.abstractmethod
    def create_all(self, base):
        pass

    @abc.abstractmethod
    def drop_all(self, base):
        pass


class TempSQLiteDatabase:

    class _TempSQLiteDatabase(SQLDatabase):

        def __init__(self):
            # Creating the engine as a sqlite database in the RAM
            engine_string = 'sqlite://'
            self._engine = create_engine(engine_string)

            self._session_maker = scoped_session(sessionmaker(bind=self._engine))

            self._current_session = self._session_maker()

        @property
        def session_maker(self):
            return self._session_maker

        @property
        def query_property(self):
            return self._session_maker.query_property()

        @property
        def engine(self):
            return self._engine

        @property
        def session(self):
            #self._current_session.close()
            #self._current_session = self._session_maker()
            return self._current_session

        def create_all(self, base):
            base.metadata.create_all(self._engine)

        def drop_all(self, base):
            base.metadata.drop_all(self._engine)

    _instance = None

    def __init__(self):
        if self._instance is None:
            setattr(TempSQLiteDatabase, '_instance', TempSQLiteDatabase._TempSQLiteDatabase())

    def __setattr__(self, key, value):
        if self._instance is not None:
            setattr(self._instance, key, value)

    def __getattr__(self, item):
        return getattr(self._instance, item)


class MySQLDatabase:

    CONFIG = Config()
    USERNAME = CONFIG['MYSQL']['username']
    PASSWORD = CONFIG['MYSQL']['password']
    HOST = CONFIG['MYSQL']['host']
    DATABASE = 'pubcontrol'

    class _MySQLDatabase:

        def __init__(self, username, password, host, database):
            engine_string = 'mysql+mysqldb://{}:{}@{}/{}?charset=utf8'.format(
                username,
                password,
                host,
                database
            )

            self.engine = create_engine(
                engine_string,
                connect_args={'connect_timeout': 10},
                poolclass=StaticPool
            )

            self.session_maker = scoped_session(sessionmaker(bind=self.engine))

            self._current_session = self.session_maker()

        @property
        def session(self):
            """
            CHANGELOG

            Changed 13.04.2018
            Removed the functionality, that with every property call the session would be closed and a new would be
            opened. For example this would also account for the case, that a add and commit call to the property would
            be in two different session, so that the add would never be commited and the commit would be for a empty
            session

            :return:
            """
            #self._current_session.close()
            #self._current_session = self.session_maker()
            return self._current_session

    _instance = None

    def __init__(self):
        if self._instance is None:
            mysql_database = MySQLDatabase._MySQLDatabase(
                self.USERNAME,
                self.PASSWORD,
                self.HOST,
                self.DATABASE
            )
            setattr(MySQLDatabase, '_instance', mysql_database)

    def create_all(self, base):
        base.metadata.create_all(self.engine)

    def drop_all(self, base):
        base.metadata.drop_all(self.engine)

    def __setattr__(self, key, value):
        if self._instance is not None:
            setattr(self._instance, key, value)

    def __getattr__(self, item):
        return getattr(self._instance, item)


# The base class for all models in the register database
BASE = declarative_base()
BASE.query = MySQLDatabase().session_maker.query_property()