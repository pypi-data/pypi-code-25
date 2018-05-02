# coding=utf-8
import unittest
from unittest import TestCase
import re
from cryptolite import generate, byte_array


class TestRandom(TestCase):
    """
    Test for random
    """

    def test_byte_array(self):
        """
        Checks that generating a random byte array returns the expected number of bytes.
        """

        # Given
        length = 20

        # When
        # Some random bytes
        random_bytes = generate.byte_array(length)

        # Then
        # Check we got what we expected
        self.assertEqual(length, len(random_bytes), "Unexpected random byte lenth.")
        self.assertIsInstance(random_bytes, bytearray)

    def test_token_length(self):
        """
        Checks that the number of bits in the returned ID is the same as specified by TOKEN_BITS.
        """

        # When
        # We generate a token
        token = generate.token()

        # Then
        # It should be of the expected length
        token_bytes = byte_array.from_hex(token)
        self.assertEqual(generate.TOKEN_BITS, len(token_bytes) * 8, "Unexpected token bit-length")

    def test_salt_length(self):
        """
        Checks that the number of bytes in a returned salt value matches the length specified in SALT_BYTES.
        """

        # When
        # We generate a salt
        salt = generate.salt()

        # Then
        # It should be of the expected length
        salt_bytes = byte_array.from_base64(salt)
        self.assertEqual(generate.SALT_BYTES, len(salt_bytes), "Unexpected salt byte-length")

    def test_password(self):
        """
        Checks the number of characters and the content of the returned password matches the expected content.
        """

        # Given
        max_length = 100

        for length in range(1, max_length):
            # When
            password = generate.password(length)

            # Then
            self.assertEqual(length, len(password), "Unexpected password length")
            p = re.compile("[A-Za-z0-9]+")
            self.assertTrue(p.match(password), "Unexpected password content")

    def test_randomness_of_tokens(self):
        """
        Test the general randomness of token generation.

        If this test fails, consider yourself astoundingly lucky.. or check the code is really producing random numbers.
        """

        iterations = 1000
        for i in range(1, iterations):
            # When
            token1 = generate.token()
            token2 = generate.token()

            # Then
            self.assertNotEqual(token1, token2, "Got identical tokens.")

    def test_randomness_of_salt(self):
        """
        Test the general randomness of salt generation.

        If this test fails, consider yourself astoundingly lucky.. or check the code is really producing random numbers.
        """

        iterations = 1000
        for i in range(1, iterations):
            # When
            salt1 = generate.salt()
            salt2 = generate.salt()

            # Then
            self.assertNotEqual(salt1, salt2, "Got identical salts.")

    def test_randomness_of_passwords(self):
        """
        Test the general randomness of password generation.

        If this test fails, consider yourself astoundingly lucky.. or check the code is really producing random numbers.
        """

        iterations = 1000
        pasword_size = 8
        for i in range(1, iterations):
            # When
            password1 = generate.password(pasword_size)
            password2 = generate.password(pasword_size)

            # Then
            self.assertNotEqual(password1, password2, "Got identical passwords.")


if __name__ == '__main__':
    unittest.main()
