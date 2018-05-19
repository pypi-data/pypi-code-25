import pytest

from nhs_dos.users import User
from nhs_dos.soap_api import SoapApiClient


def test_new_soapapiclient_returns_valid_object():
    u = User('username', 'password')
    url = 'http://fake.url'
    s = SoapApiClient(u, url=url)
    assert type(s) is SoapApiClient


def test_new_soapapiclient_without_user_throws_exception():
    with pytest.raises(TypeError):
        SoapApiClient(url='http://fake.url')


def test_new_soapapiclient_without_none_user_throws_exception():
    with pytest.raises(TypeError):
        u = None
        SoapApiClient(u, url='http://fake.url')
