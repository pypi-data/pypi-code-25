from sqlite3 import Connection

from sqlite_framework.component.factory import SqliteStorageComponentFactory
from sqlite_framework.log.logger import SqliteLogger
from sqlite_framework_test.components.test import TestSqliteComponent


class TestSqliteStorageComponentFactory(SqliteStorageComponentFactory):
    def __init__(self, connection: Connection, logger: SqliteLogger):
        super().__init__(connection, logger)

    def test(self) -> TestSqliteComponent:
        return self._initialized(TestSqliteComponent())
