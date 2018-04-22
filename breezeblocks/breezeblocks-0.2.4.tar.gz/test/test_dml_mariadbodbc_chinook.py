import os
import pyodbc
import unittest
from breezeblocks import Database

from base_dml_chinook_tests import BaseDMLChinookTests

CONNECTION_STRING = "Driver={MariaDB};User Id=quinn;Password=bbMaria;Data Source=127.0.0.1;Database=chinook"

class MariaDBODBCTests(BaseDMLChinookTests, unittest.TestCase):
    """Tests using MariaDB through an ODBC adapter."""
    
    def setUp(self):
        self.db = Database(dsn=CONNECTION_STRING, dbapi_module=pyodbc)
