import unittest
from pydata.list import PyData


class TestList(unittest.TestCase):
    def test_scraping(self):
        self.assertTrue(PyData.scraping())
