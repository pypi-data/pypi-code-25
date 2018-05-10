import unittest
import yaml
import binascii
from recordskeeper_python_lib import *
from recordskeeper_python_lib.blockchain import Blockchain

import sys

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


class BlockchainTest(unittest.TestCase):

    def test_getchaininfo(self):
        
        chainname = Blockchain.getChainInfo()[7]
        self.assertEqual(chainname, "recordskeeper-test")

        rootstream = Blockchain.getChainInfo()[2]
        self.assertEqual(rootstream, "root")

        rpcport = Blockchain.getChainInfo()[5]
        self.assertEqual(rpcport, 8378)

        networkport = Blockchain.getChainInfo()[4]
        self.assertEqual(networkport, 8379)

    def test_getnodeinfo(self):

        info = Blockchain.getNodeInfo()[1]
        self.assertGreater(info, 60)

        balance = Blockchain.getNodeInfo()[0]
        self.assertIsNotNone(balance)

        difficulty = Blockchain.getNodeInfo()[3]
        self.assertLess(difficulty, 1)


    def test_permissions(self):

        permissions = Blockchain.permissions()
        self.assertListEqual(permissions, ['mine', 'admin', 'activate', 'connect', 'send', 'receive', 'issue', 'create'])


    def test_getpendingtransactions(self):

        pendingtx = Blockchain.getpendingTransactions()[1]
        self.assertListEqual(pendingtx, [])

        pendingtxcount = Blockchain.getpendingTransactions()[0]
        self.assertGreaterEqual(pendingtxcount, 0)

    def test_checknodebalance(self):

        balance = Blockchain.checkNodeBalance()
        self.assertGreater(balance, 0)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BlockchainTest)
    unittest.TextTestRunner(verbosity=2).run(suite)