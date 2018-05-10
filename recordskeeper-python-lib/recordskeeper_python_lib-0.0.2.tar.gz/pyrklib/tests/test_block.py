import unittest
import yaml
import recordskeeper_python_lib
from recordskeeper_python_lib.block import Block

import sys


with open("config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)


class BlockTest(unittest.TestCase):


    def test_block_info(self):

        miner = Block.blockinfo("100")[2]  
        self.assertEqual(miner,'n2gNFB8oz4qfmUKCsfwqLo8ineWfocpNMk')
        
        size = Block.blockinfo("100")[3]
        self.assertEqual(size, 300)

        nonce = Block.blockinfo("100")[4]
        self.assertEqual(nonce, 260863)

        merkleroot = Block.blockinfo("100")[8]
        self.assertEqual(merkleroot, 'c6d339bf75cb969baa4c65e1ffd7fade562a191fa90aac9dd495b764f2c1b429')


    def test_retrieveBlocks(self):

        miner = Block.retrieveBlocks("10-20")[1][1]
        self.assertEqual(miner, "n2gNFB8oz4qfmUKCsfwqLo8ineWfocpNMk")

        blocktime = Block.retrieveBlocks("10-20")[2][2]
        self.assertEqual(blocktime,1522831624)

        blockhash = Block.retrieveBlocks("10-20")[0][4]
        self.assertEqual(blockhash, "000002d184165e5c18facde8a5678acd975ba9d315eb440752d83dcd70d4abd5")

        txcount = Block.retrieveBlocks("10-20")[3][1]
        self.assertEqual(txcount, 1)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BlockTest)
    unittest.TextTestRunner(verbosity=2).run(suite)