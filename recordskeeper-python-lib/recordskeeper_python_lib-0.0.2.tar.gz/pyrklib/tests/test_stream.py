import unittest
import yaml
import binascii
from recordskeeper_python_lib import *
from recordskeeper_python_lib.stream import Stream

import sys


with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


class StreamTest(unittest.TestCase):


    def test_publish(self):
        
        txid = Stream.publish("mpC8A8Fob9ADZQA7iLrctKtwzyWTx118Q9", "root", "test", "This is test data".encode('utf-8'). hex())
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_retrieve_with_txid(self):

        result = Stream.retrieve("root", "eef0c0c191e663409169db0972cc75ff91e577a072289ee02511b410bc304d90")
        self.assertEqual(result,"testdata")


    def test_retrieve_with_id_address(self):

        result = Stream.retrieveWithAddress("root", "mpC8A8Fob9ADZQA7iLrctKtwzyWTx118Q9")
        self.assertEqual(result[1], "5468697320697320746573742064617461")
    
    def test_retrieve_with_key(self):

        result = Stream.retrieveWithKey("root", "test")
        self.assertEqual(result[1], "5468697320697320746573742064617461")

    def test_verifyData(self):

        result = Stream.verifyData("root", "test", 5)
        self.assertEqual(result, "Data is successfully verified.")

    def test_retrieveItems(self):
        
        result = Stream.retrieveItems("root", 5)[2][2]
        self.assertEqual(result, "Test data")
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StreamTest)
    unittest.TextTestRunner(verbosity=2).run(suite)