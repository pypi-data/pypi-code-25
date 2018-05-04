from functools import partial

import pytest
import requests_mock

from url_checker.engine import get_status_code, format_url


def test_format_url_returns_with_schema():
    assert format_url('http://google.com').startswith('http://')
    assert format_url('https://google.com').startswith('https://')
    assert format_url('www.google.com').startswith('http://')
    assert format_url('google.com').startswith('http://')


def test_format_url_force_https_schema():
    https_format_url = partial(format_url, force_https=True)
    assert https_format_url('http://google.com').startswith('https://')
    assert https_format_url('https://google.com').startswith('https://')
    assert https_format_url('www.google.com').startswith('https://')
    assert https_format_url('google.com').startswith('https://')


def test_get_status_code_invalid_urls_return_0():
    assert get_status_code('https://www.nothing.rm') == 0
    assert get_status_code('nothing.rm') == 0
    assert get_status_code('www.google.com') == 0
    assert get_status_code('google.com') == 0


def test_get_status_code_with_format_adds_schema():
    get_status_code_with_format = partial(get_status_code, should_format=True)
    assert get_status_code_with_format('www.google.com') != 0
    assert get_status_code_with_format('google.com') != 0


def test_get_status_code_returns_initial_status_code():
    with requests_mock.Mocker() as mock_session:
        mock_session.get('https://httpbin.org/status/200', status_code=200)
        mock_session.get('https://httpbin.org/status/404', status_code=404)
        mock_session.get('https://httpbin.org/status/302', status_code=302)
        assert get_status_code('https://httpbin.org/status/200') == 200
        assert get_status_code('https://httpbin.org/status/404') == 404
        assert get_status_code('https://httpbin.org/status/302') == 302


if __name__ == '__main__':
    pytest.main('-v')
