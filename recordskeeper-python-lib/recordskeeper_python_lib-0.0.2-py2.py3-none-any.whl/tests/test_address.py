import unittest
import yaml
import binascii
from recordskeeper_python_lib import *
from recordskeeper_python_lib.address import Address

import sys
# sys.path.append('C:\\Users\\Trinayan\\pythonsdk\\scripts')

#from stream import Stream

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


class AddressTest(unittest.TestCase):


    def test_getaddress(self):
        
        address = Address.getAddress()
        address_size = sys.getsizeof(address)
        self.assertEqual(address_size, 83)

    def test_checkifvalid(self):

        checkaddress = Address.checkifValid('mwp2SHRUaqA7EvfdNFzZkMf1cMZGSh5d1z')
        self.assertEqual(checkaddress, 'Address is valid')

    def test_checkifvalid(self):

        wrongaddress = Address.checkifValid('1UCjNZmSNJxKNes6SFBfMKCahAPJ7DGHCvfh6E')
        self.assertEqual(wrongaddress, 'Address is valid')

    def test_checkifmineallowed(self):

        checkaddress = Address.checkifMineAllowed('mwp2SHRUaqA7EvfdNFzZkMf1cMZGSh5d1z')
        self.assertEqual(checkaddress, 'Address has mining permission')

    def test_checkifmineallowed(self):

        wrongaddress = Address.checkifMineAllowed('mmx8H2YZDqsvhTt1YHkJpYKkcD1w8JBTgh')
        self.assertEqual(wrongaddress, 'Address has mining permission')

    def test_checkbalance(self):

        balance = Address.checkBalance('mmx8H2YZDqsvhTt1YHkJpYKkcD1w8JBTgh')
        self.assertEqual(balance, 5)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AddressTest)
    unittest.TextTestRunner(verbosity=2).run(suite)