from unittest import TestCase

import toil.crypto.symmetric


class TestSymmetricEncryptor(TestCase):
    def test_generate_key(self):
        encryptor = toil.crypto.symmetric.SymmetricEncryptor({})

        encryptor.generate_key("/Users/aclove/testkey.dat")

        # encryptor.generate_iv()

        # self.assertRaises(Exception, s.demo, 2, 1, 2)

        # self.fail()

    def test_encrypt_and_decrypt(self):
        confidential_data = "this is an encryption data test"
        encryptor = toil.crypto.symmetric.SymmetricEncryptor({})

        key = encryptor.generate_key()

        encrypted_data = encryptor.encrypt(confidential_data, encryption_key=key)
        decrypted_data = encryptor.decrypt(encrypted_data, encryption_key=key)

        self.assertTrue(decrypted_data == confidential_data)

    # def test_generate_iv(self):
    #   self.fail()
    #
    # def test_encrypt(self):
    #   self.fail()
    #
    # def test_decrypt(self):
    #   self.fail()
