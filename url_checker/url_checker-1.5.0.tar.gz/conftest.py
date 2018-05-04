import pytest
import requests
import requests_mock


@pytest.fixture()
def mock_request_session():
    adapter = requests_mock.Adapter()
    session = requests.Session()

    adapter.register_uri(
        'GET', 'https://httpbin.org/status/200', status_code=200
    )
    adapter.register_uri(
        'GET', 'https://httpbin.org/status/302', [
            {'status_code': 302},
            {'status_code': 200}
        ]
    )
    adapter.register_uri(
        'GET', 'https://httpbin.org/status/404', status_code=404
    )

    session.mount(prefix='', adapter=adapter)
    return session


@pytest.fixture(autouse=False)
def no_requests(monkeypatch):
    monkeypatch.delattr('requests.sessions.Session.request')
