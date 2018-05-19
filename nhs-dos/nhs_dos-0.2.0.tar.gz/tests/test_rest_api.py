import pytest
import mock
import requests

from nhs_dos import RestApiClient, User, rest_api


def test_new_restapiclient_sets_up_session():
    u = User('test-username', 'test-password')
    c = RestApiClient(u)
    assert isinstance(c.s, requests.Session)


def test_url_defaults_to_uat_when_not_passed_in():
    u = User('test-username', 'test-password')
    c = RestApiClient(u)
    assert c.url == 'https://uat.pathwaysdos.nhs.uk/app/controllers/api/v1.0'


def test_passing_url_parameter_sets_attribute():
    u = User('test-username', 'test-password')
    url = 'https://a.different.url'
    c = RestApiClient(u, url)
    assert c.url == url


def test_single_service_found():
    u = User('test-username', 'test-password')
    client = RestApiClient(u)
    identifier = '12345'
    data = {
        'success':
            {
                'serviceCount': 1,
                'services':
                    [
                        {'id': '12345', 'name': 'Test Service', 'endpoints': []}
                    ]
            }
    }

    url = 'https://uat.pathwaysdos.nhs.uk/app/controllers/api/v1.0/services/byServiceId/12345'

    with mock.patch.object(client.s, 'get') as get:
        mock_response = get.return_value
        mock_response.json.return_value = data
        response = client.get_single_service(identifier, 'dos')

        get.assert_called_with(url)
        assert response[0].id == '12345'
        assert response[0].name == 'Test Service'
        assert response[0].endpoints == []
        assert len(response) == 1


def test_no_service_found():
    u = User('test-username', 'test-password')
    client = RestApiClient(u)
    id = '12345'
    data = {
        'success':
            {
                'serviceCount': 0,
                'services':
                    []
            }
    }

    url = 'https://uat.pathwaysdos.nhs.uk/app/controllers/api/v1.0/services/byServiceId/12345'

    with mock.patch.object(client.s, 'get') as get:
        mock_response = get.return_value
        mock_response.json.return_value = data
        response = client.get_single_service(id, 'dos')

        get.assert_called_with(url)
        assert response == []


def test_log_line_written():
    u = User('test-username', 'test-password')
    client = RestApiClient(u)
    identifier = '12345'
    data = {
        'success':
            {
                'serviceCount': 1,
                'services':
                    [
                        {'id': '12345', 'name': 'Test Service', 'endpoints': []}
                    ]
            }
    }

    with mock.patch.object(client.s, 'get') as get:
        mock_response = get.return_value
        mock_response.json.return_value = data

        with mock.patch.object(rest_api.logger, 'debug') as log:
            client.get_single_service(identifier, 'dos')
            log.assert_any_call(f'get_single_service response id = {identifier}')


def test_multiple_services_found():
    pass


def test_i_dont_catch_requests_error():
    u = User('test-username', 'test-password')
    client = RestApiClient(u)
    identifier = '12345'

    with mock.patch.object(client.s, 'get') as get:
        get.side_effect = requests.ConnectionError
        with pytest.raises(requests.ConnectionError):
            client.get_single_service(identifier, 'dos')


def test_get_service_by_id_passes_dos_id_type():
    u = User('test-username', 'test-password')
    client = RestApiClient(u)
    identifier = '12345'

    with mock.patch.object(client, 'get_single_service') as gss:
        client.get_service_by_id(identifier)
        gss.assert_called_with(identifier, 'dos')

