from __future__ import absolute_import
from __future__ import print_function

import unittest
import xtt

class TestReturnCodes(unittest.TestCase):

    def test_error_string(self):
        string = xtt.error_string(0)
        self.assertEqual(string, "XTT - SUCCESS")

class TestCrypto(unittest.TestCase):

    def test_create_ed25519_key_pair(self):
        (pub, priv) = xtt.crypto.create_ed25519_key_pair()
        self.assertEqual(len(pub.data), 32)
        self.assertEqual(len(priv.data), 64)

if __name__ == "__main__":
    unittest.main()
