from unittest import TestCase
from unittest.mock import patch, Mock
from .mocks import afrigis_geocode_success_mock, \
    afrigis_geocode_unauthenticated_mock
from afrigis.services import geocode


class TestGeocode(TestCase):
    def test_geocode_raises_error_if_afrigis_key_missing(self):
        """
        Type error should be thrown if afrigis key is not passed
        """
        with self.assertRaises(
                TypeError,
                msg='geocode() should fail if `afrigis_key` is not passed'
        ):
            geocode(
                afrigis_secret='stub',
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_key_is_none_type(self):
        """
        geocode() should fail if `afrigis_key` is <NoneType>
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_key` is None'
        ):
            geocode(
                afrigis_key=None,
                afrigis_secret='stub',
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_key_is_empty(self):
        """
        geocode() should fail if `afrigis_key` is <NoneType>
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_key` is empty'
        ):
            geocode(
                afrigis_key='',
                afrigis_secret='stub',
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_key_is_non_string_edge_0(self):
        """
        geocode() should fail if `afrigis_key` is <NoneType>
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_key` is non-string'
        ):
            geocode(
                afrigis_key=123,
                afrigis_secret='stub',
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_key_is_non_string_edge_1(self):
        """
        geocode() should fail if `afrigis_key` is <NoneType>
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_key` is non-string'
        ):
            geocode(
                afrigis_key=dict(foo='bar'),
                afrigis_secret='stub',
                address_id='stub',
            )

    def test_geocode_raise_error_if_afrigis_secret_missing(self):
        """
        Type error should be thrown if afrigis secret is not passed
        """
        with self.assertRaises(
                TypeError,
                msg='geocode() should fail if `afrigis_secret` is not passed'
        ):
            geocode(
                afrigis_key='stub',
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_secret_is_nonetype(self):
        """
        geocode() should fail if `afrigis_secret` is nonetype
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_secret` is None'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret=None,
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_secret_is_empty(self):
        """
        geocode() should fail if `afrigis_secret` is empty
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_secret is empty`'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret='',
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_secret_is_non_string_edge_0(self):
        """
        geocode() should fail if `afrigis_secret` is non-string
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_secret is non-string`'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret=123,
                address_id='stub',
            )

    def test_geocode_raises_error_if_afrigis_secret_is_non_string_edge_1(self):
        """
        geocode() should fail if `afrigis_secret` is non-string
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `afrigis_secret is non-string`'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret=dict(foo='bar'),
                address_id='stub',
            )

    def test_geocode_raise_error_if_address_id_missing(self):
        """
        Type error should be thrown if afrigis secret is not passed
        """
        with self.assertRaises(
                TypeError,
                msg='geocode() should fail if `address_id` is not passed'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret='stub',
            )

    def test_geocode_raises_error_if_address_id_is_nonetype(self):
        """
        geocode() should fail if `address_id` is nonetype
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `address_id` is None'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret='stub',
                address_id=None,
            )

    def test_geocode_raises_error_if_address_id_is_empty(self):
        """
        geocode() should fail if `address_id` is empty
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `address_id` is empty'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret='stub',
                address_id='',
            )

    def test_geocode_raises_error_if_address_id_is_non_string_edge_0(self):
        """
        geocode() should fail if `address_id` is non-string
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `address_id` is non-string'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret='stub',
                address_id=123,
            )

    def test_geocode_raises_error_if_address_id_is_non_string_edge_1(self):
        """
        geocode() should fail if `address_id` is non-string
        """
        with self.assertRaises(
                ValueError,
                msg='geocode() should fail if `address_id` is non-string'
        ):
            geocode(
                afrigis_key='stub',
                afrigis_secret='stub',
                address_id=dict(foo='bar'),
            )

    @patch('urllib.request.urlopen')
    def test_geocode_raises_authentication_exception_if_call_fails_with_401(
            self,
            urlopen_mock
    ):
        mock = Mock()
        mock.read.side_effect = lambda: afrigis_geocode_unauthenticated_mock
        mock.getcode.side_effect = lambda: 200
        urlopen_mock.return_value = mock

        from afrigis.exceptions import AuthenticationFailedException

        with self.assertRaises(AuthenticationFailedException):
            geocode(
                afrigis_key='fake-key',
                afrigis_secret='fake-secret',
                address_id='some-fake-id',
            )

    @patch('urllib.request.urlopen')
    def test_geocode_returns_correct_json_response_if_afrigis_call_successful(
            self,
            urlopen_mock
    ):
        mock = Mock()
        mock.read.side_effect = lambda: afrigis_geocode_success_mock
        mock.getcode.side_effect = lambda: 200
        urlopen_mock.return_value = mock

        res = geocode(
            afrigis_key='fake-key',
            afrigis_secret='fake-secret',
            address_id='some-fake-id',
        )

        self.assertIsInstance(res, dict)

        self.assertIsInstance(res.get('result'), list)
