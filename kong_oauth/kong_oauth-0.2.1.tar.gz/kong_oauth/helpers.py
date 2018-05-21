import requests
from django.conf import settings
from django.contrib.auth import get_user_model

def get_auth_data(data):
    possible_fields = ['username', 'phone_number', 'otp', 'password']
    parsed_data = {}
    for field in possible_fields:
        val = data.get(field, None)
        if val is not None: parsed_data[field] = val
    return parsed_data

def get_user(token):
    path = '/api/users/me/'
    url = '{}{}'.format(settings.APPGURU_URL, path)
    headers = {"Authorization": "token {}".format(token)}
    return requests.get(url, headers=headers)

def user_from_result(result):
    user = get_user_model()()
    user.id = result.json().get('id')
    user.username = result.json().get('id')
    user.data = result.json()
    return user

def ag_authenticate(path, data):
    url = '{}{}'.format(settings.APPGURU_URL, path)
    result = requests.post(url, data)
    if result.status_code == 200:
        token = result.json().get('token')
        user_data = get_user(token)
        return user_from_result(user_data)
    return None


def kong_login(user, client_id, client_secret):

    base_url = getattr(settings, 'KONG_GATEWAY_URL')
    data = {
        "client_id": client_id,
        "client_secret": client_secret, # testtest
        "grant_type": "password",
        "provision_key": settings.KONG_PROVISION_KEY,
        "authenticated_userid": user.id,
    }
    url = "{}/oauth2/token".format(base_url)
    url = settings.KONG_OAUTH_ENDPOINT
    result = requests.post(url, data, verify=False)
    status = result.status_code
    result = result.json()
    return (result, status)