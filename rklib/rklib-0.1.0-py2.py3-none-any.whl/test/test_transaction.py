import unittest
import yaml
import binascii
from pyrklib import transaction
from pyrklib.transaction import Transaction

import sys

with open("test_config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = transaction.network

class TransactionTest(unittest.TestCase):


    def test_sendtransaction(self):
        
        txid = Transaction.sendTransaction(net['miningaddress'], net['validaddress'], "hello", 0.2)
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_sendrawtransaction(self):

        txid = Transaction.sendRawTransaction(net['dumpsignedtxhex'])
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_signrawtransaction(self):

    	txhex = Transaction.signRawTransaction(net['dumptxhex'], net['privatekey'])				#call to function signRawTransaction
    	tx_size = sys.getsizeof(txhex)
    	self.assertEqual(tx_size, 501)

    def test_createrawtransaction(self):

    	txhex = Transaction.createRawTransaction(net['miningaddress'], net['validaddress'], net['amount'], net['testdata'])
    	tx_size = sys.getsizeof(txhex)
    	self.assertEqual(tx_size, 317)

    def test_sendsignedtransaction(self):

    	txid = Transaction.sendSignedTransaction(net['miningaddress'], net['validaddress'] , net['amount'], net['privatekey'],net['testdata'])
    	tx_size = sys.getsizeof(txid)
    	self.assertEqual(tx_size, 113)


    def test_retrievetransaction(self):

    	sentdata = Transaction.retrieveTransaction(net['dumptxid'])[0]
    	self.assertEqual(sentdata, "hellodata")

    	sentamount = Transaction.retrieveTransaction(net['dumptxid'])[1]
    	self.assertGreaterEqual(sentamount, 0)

    
    def test_getfee(self):

    	fees = Transaction.getFee(net['miningaddress'], "4b1fbf9fb1e5c93cfee2d37ddc5fef444da0a05cc9354a834dc7155ff861a5e0")
    	self.assertEqual(fees, 0.0269)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TransactionTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
