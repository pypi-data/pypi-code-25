from unittest import TestCase
from afrigis import authentication


class TestAuthentication(TestCase):

    def setUp(self):
        pass

    def test_get_auth_digest_returns_correct_hash_code(self):
        auth_code = authentication.get_auth_code_digest(
            afrigis_key='fake-key',
            afrigis_secret='fake-secret',
            service_name='some-service',
            query_params={'fake_ils_parameter': 'fake_ils_value'}
        )
        # Pre-generated hash for asserting correct behaviour
        correct_hash_code = 'Mx7IWtT4yfyq17x_rhnEP9UuTWQ'
        self.assertEqual(auth_code, correct_hash_code)
