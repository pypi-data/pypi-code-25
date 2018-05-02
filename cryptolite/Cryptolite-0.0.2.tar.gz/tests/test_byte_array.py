# coding=utf-8
import unittest
from unittest import TestCase
from cryptolite import byte_array, generate


class TestByteArray(TestCase):
    """
    Tests for byte array conversions.
    """

    def test_hex(self):
        """
        Verifies a byte array can be correctly converted to a hex String and back again.
        """

        # Given
        data = generate.byte_array(100)

        # When
        # We convert to hex and back again
        hex = byte_array.to_hex(data)
        back_again = byte_array.from_hex(hex)

        # Then
        # The end result should match the input
        self.assertEqual(data, back_again)
        self.assertIsInstance(hex, str)
        self.assertIsInstance(back_again, bytearray)

    def test_hex_none(self):
        """
        Verifies that None is gracefully handled.
        """

        # When
        # We attempt conversion
        b = byte_array.to_hex(None)
        s = byte_array.from_hex(None)

        # Then
        # No error should occur and we should have None results
        self.assertEqual(None, b)
        self.assertEqual(None, s)

    def test_base64(self):
        """
        Verifies a byte array can be correctly converted to base64 and back again.
        """

        # Given
        data = generate.byte_array(100)

        # When
        # We convert to hex and back again
        base64 = byte_array.to_base64(data)
        back_again = byte_array.from_base64(base64)

        # Then
        # The end result should match the input
        self.assertEqual(data, back_again)
        self.assertIsInstance(base64, str)
        self.assertIsInstance(back_again, bytearray)

    def test_base64_none(self):
        """
        Verifies that None is gracefully handled.
        """

        # When
        # We attempt conversion
        b = byte_array.to_base64(None)
        s = byte_array.from_base64(None)

        # Then
        # No error should occur and we should have None results
        self.assertEqual(None, b)
        self.assertEqual(None, s)

    def test_string(self):
        """
        Verifies a byte array can be correctly converted to a string and back again.
        """

        # Given
        data = bytearray("Mary had a little Café".encode("UTF8"))

        # When
        # We convert to string and back again
        string = byte_array.to_string(data)
        back_again = byte_array.from_string(string)

        # Then
        # The end result should match the input
        self.assertEqual(data, back_again)
        self.assertIsInstance(string, str)
        self.assertIsInstance(back_again, bytearray)

    def test_string_none(self):
        """
        Verifies that None is gracefully handled.
        """

        # When
        # We attempt conversion
        b = byte_array.to_string(None)
        s = byte_array.from_string(None)

        # Then
        # No error should occur and we should have None results
        self.assertEqual(None, b)
        self.assertEqual(None, s)


if __name__ == '__main__':
    unittest.main()
