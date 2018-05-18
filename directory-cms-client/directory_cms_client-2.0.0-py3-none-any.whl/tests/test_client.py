import requests_mock

from directory_cms_client import DirectoryCMSClient


def test_cms_client_lookup_by_page_type_language():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/thing/')
        client.lookup_by_page_type('thing', language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_cms_client_lookup_by_page_type_draft():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-type/thing/')
        client.lookup_by_page_type('thing', draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }


def test_cms_client_list_by_page_type_language():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/')
        client.list_by_page_type('thing', language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
            'type': ['thing'],
        }


def test_cms_client_list_by_page_type_draft():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/')
        client.list_by_page_type('thing', draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
            'type': ['thing'],
        }


def test_cms_client_lookup_by_slug_language():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-slug/thing/')
        client.lookup_by_slug('thing', language_code='de')
        request = mock.request_history[0]

        assert request.qs == {
            'lang': ['de'],
            'fields': ['*'],
        }


def test_cms_client_lookup_by_slug_draft():
    client = DirectoryCMSClient(
        base_url='http://example.com',
        api_key='debug',
    )
    with requests_mock.mock(case_sensitive=True) as mock:
        mock.get('http://example.com/api/pages/lookup-by-slug/thing/')
        client.lookup_by_slug('thing', draft_token='draft-token')
        request = mock.request_history[0]

        assert request.qs == {
            'draft_token': ['draft-token'],
            'fields': ['*'],
        }
