import os
import pyodbc
import unittest
from breezeblocks import Database

from base_query_chinook_tests import BaseQueryChinookTests

CONNECTION_STRING = "Driver=MariaDB;User ID={};Password={};Data Source=127.0.0.1;Database=chinook".format(
    os.getenv("MARIADBUSER"), os.getenv("MARIADBPASS"))

class MariaDBODBCTests(BaseQueryChinookTests, unittest.TestCase):
    """Tests using MariaDB through an ODBC adapter."""
    
    def setUp(self):
        self.db = Database(dsn=CONNECTION_STRING, dbapi_module=pyodbc)
    
    @unittest.skip("MariaDB seems to sort string case-insensitively. Python does not.")
    def test_orderByAsc(self):
        pass
    
    @unittest.skip("MariaDB seems to sort string case-insensitively. Python does not.")
    def test_orderByDesc(self):
        pass
