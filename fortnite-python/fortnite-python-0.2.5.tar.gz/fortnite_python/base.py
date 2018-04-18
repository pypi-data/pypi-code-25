import json

import furl
import requests

from .exceptions import UnauthorizedError, NotFoundError, UnknownPlayerError
from .domain import Platform, Player


class Fortnite:

    def __init__(self, api_key):
        self.client = Client(api_key)

    def player(self, player=None, platform=Platform.PC):
        endpoint = platform.value + '/' + player
        data = self.client.request(endpoint)
        if 'accountId' in data:
            return Player(data)
        raise UnknownPlayerError


class Client:

    BASE_URL = 'https://api.fortnitetracker.com/v1/profile/'

    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update({
            'TRN-Api-Key': api_key,
            'Accept': 'application/vnd.api+json'
        })
        self.url = furl.furl(self.BASE_URL)

    API_OK = 200
    API_ERRORS_MAPPING = {
        401: UnauthorizedError,
        400: NotFoundError,
        403: UnauthorizedError,
    }

    def request(self, endpoint):
        response = self.session.get(self.BASE_URL + endpoint)
        if response.status_code != self.API_OK:
            exception = self.API_ERRORS_MAPPING.get(
                response.status_code, Exception)
            raise exception

        return json.loads(response.text)
