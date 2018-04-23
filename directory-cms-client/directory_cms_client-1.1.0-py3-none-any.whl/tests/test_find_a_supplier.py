import requests_mock

from directory_cms_client.find_a_supplier import FindASupplierClient


def test_get_industries_landing_page_language():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['industries-landing-page']
        ))
        client.get_industries_landing_page(language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_get_industries_landing_page_draft():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['industries-landing-page']
        ))
        client.get_industries_landing_page(draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }


def test_get_landing_landing_page_language():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['landing-page']
        ))
        client.get_landing_page(language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_get_landing_landing_page_draft():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['landing-page']
        ))
        client.get_landing_page(draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }


def test_get_industry_contact_page_language():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['industry-contact-page']
        ))
        client.get_industry_contact_page(language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_get_industry_contact_page_draft():
    client = FindASupplierClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/{0}/'.format(
            FindASupplierClient.page_types['industry-contact-page']
        ))
        client.get_industry_contact_page(draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }
