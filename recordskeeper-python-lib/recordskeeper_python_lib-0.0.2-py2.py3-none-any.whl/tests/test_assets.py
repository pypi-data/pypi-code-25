import unittest
import yaml
import binascii
from recordskeeper_python_lib import *
from recordskeeper_python_lib.assets import Assets

import sys

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


class AssetsTest(unittest.TestCase):


    def test_createasset(self):
        
        txid = Assets.createAsset("mmLF3nuSPpPDiJgUw1gBqNhvoPjZLPMdFu", "xyz", 100)
        self.assertEqual(txid, None)

    def test_retrieveassets(self):

        name = Assets.retrieveAssets()[0]
        self.assertListEqual(name, [])

    def test_retrieveassets(self):

        txid = Assets.retrieveAssets()[1]
        self.assertListEqual(txid, [])


    def test_retrieveassets(self):

        qty = Assets.retrieveAssets()[2]
        self.assertListEqual(qty, [])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssetsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)