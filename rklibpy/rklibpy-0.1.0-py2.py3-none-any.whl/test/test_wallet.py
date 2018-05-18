import unittest
import yaml
import binascii
from pyrklib import wallet
from pyrklib.wallet import Wallet

import sys


with open("test_config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = wallet.network

class WalletTest(unittest.TestCase):

    def test_createwallet(self):
        
        address = Wallet.createWallet()[0]
        address_size = sys.getsizeof(address)
        self.assertEqual(address_size, 83)

    def test_getprivkey(self):

        checkprivkey = Wallet.getPrivateKey(net['miningaddress'])
        self.assertEqual(checkprivkey, net['privatekey'])

    def test_retrievewalletinfo(self):

        wallet_balance = Wallet.retrieveWalletinfo()[0]
        self.assertGreaterEqual(wallet_balance, 0)

    def test_signmessage(self):

        signedMessage = Wallet.signMessage(net['miningaddress'], net['testdata'])
        self.assertEqual(signedMessage, net['signedtestdata'])

    def test_verifymessage(self):

        validity = Wallet.verifyMessage(net['miningaddress'], net['signedtestdata'], net['testdata'])
        self.assertEqual(validity, 'Yes, message is verified')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WalletTest)
    unittest.TextTestRunner(verbosity=2).run(suite)