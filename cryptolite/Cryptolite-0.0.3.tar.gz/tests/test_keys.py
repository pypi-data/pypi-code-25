# coding=utf-8
import unittest
from unittest import TestCase
from cryptolite import byte_array, keys


class TestByteArray(TestCase):
    """
    Tests for key generation.
    """

    def test_generate_secret_key(self):
        """
        Verifies the same key can be reliably generated given the same password and salt values.
        """

        # Given
        # A known password/salt -> key vector
        password = "Mary had a little Café"
        salt = "EvwdaavC8dRvR4RPaI9Gkg=="
        key_hex = "e73d452399476f0488b32b0bea2b8c0da35c33b122cd52c6ed35188e4117f448"

        # When
        # We generate the key
        key = keys.generate_secret_key(password, salt)

        # Then
        # We should get the expected key
        self.assertEqual(key_hex, byte_array.to_hex(key))


if __name__ == '__main__':
    unittest.main()
