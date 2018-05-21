import unittest

from yangsutil import ShieldUtil


class ShieldUtilTestCase(unittest.TestCase):
    def setUp(self):
        self.PLAIN_TEXT = ' i!! tem 1234## test.. T//*&^%$#'
        self.KEY = '1234567890123456'

    def test_1_encrypt_decrypt_test(self):
        encrypt_text = ShieldUtil.encrypt_aes(self.KEY, self.PLAIN_TEXT)

        self.assertEqual(
            self.PLAIN_TEXT,
            ShieldUtil.decrypt_aes(self.KEY, encrypt_text),
            msg='Encrypt Decrypt Test'
        )
