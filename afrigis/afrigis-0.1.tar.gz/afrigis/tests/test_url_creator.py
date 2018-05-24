from unittest import TestCase
from afrigis.url_creator import create_full_url


class TestUrlCreator(TestCase):

    def setUp(self):
        pass

    def test_url_creator_returns_correct_url(self):

        # Pre-generated url for testing purposes
        correct_url = 'http://example.rest/api/service.stub/key.stub/Y4COBwOqmksoSS22XMjDyUb1x4Q'

        url = create_full_url(
            afrigis_key='key.stub',
            afrigis_secret='secret.stub',
            afrigis_base_uri='http://example.rest/api/',
            service_name='service.stub',
            query_parameters={
                'ils_parameter.stub': 'ils_parameter_value.stub'
            }
        )

        self.assertEqual(url, correct_url)

    def test_url_creator_returns_correct_url_without_params(self):

        # Pre-generated url for testing purposes
        correct_url = 'http://example.rest/api/service.stub/key.stub/CFCWk-x7utrDDUjbDnd0m_Haw1Y'

        url = create_full_url(
            afrigis_key='key.stub',
            afrigis_secret='secret.stub',
            afrigis_base_uri='http://example.rest/api/',
            service_name='service.stub'
        )

        self.assertEqual(url, correct_url)


