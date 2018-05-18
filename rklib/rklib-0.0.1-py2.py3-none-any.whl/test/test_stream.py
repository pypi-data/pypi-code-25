import unittest
import yaml
import binascii
from pyrklib import stream
from pyrklib.stream import Stream

import sys

with open("test_config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = stream.network

class StreamTest(unittest.TestCase):


    def test_publish(self):
        
        txid = Stream.publish(net['miningaddress'], net['stream'], net['testdata'], "This is test data".encode('utf-8'). hex())
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_retrieve_with_txid(self):

        result = Stream.retrieve(net['stream'], "eef0c0c191e663409169db0972cc75ff91e577a072289ee02511b410bc304d90")
        self.assertEqual(result,"testdata")


    def test_retrieve_with_id_address(self):

        result = Stream.retrieveWithAddress(net['stream'], net['miningaddress'])
        self.assertEqual(result[1], "5468697320697320746573742064617461")
    
    def test_retrieve_with_key(self):

        result = Stream.retrieveWithKey(net['stream'], net['testdata'])
        self.assertEqual(result[1], "5468697320697320746573742064617461")

    def test_verifyData(self):

        result = Stream.verifyData(net['stream'], net['testdata'], 5)
        self.assertEqual(result, "Data is successfully verified.")

    def test_retrieveItems(self):
        
        result = Stream.retrieveItems(net['stream'], 5)[2][2]
        self.assertEqual(result, "Test data")
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StreamTest)
    unittest.TextTestRunner(verbosity=2).run(suite)