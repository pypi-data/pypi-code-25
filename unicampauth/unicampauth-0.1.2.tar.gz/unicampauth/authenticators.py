from django.urls import reverse_lazy
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials

from .conf import settings


class BaseAuthentication():
    auth_uri = ''
    token_uri = ''
    client_id = ''
    client_secret = ''
    scopes = ['']

    @property
    def redirect_uri(self):
        return '{}{}'.format(settings.SITE_URL, reverse_lazy('unicampauth:callback'))

    def get_authorization_url(self, state=''):
        raise NotImplementedError

    def response_code_or_false(self, request):
        raise NotImplementedError

    def exchange_auth_code(self, code):
        return NotImplementedError

    def get_credentials(self, token, refresh_token):
        raise NotImplementedError

    def get_data(self):
        return NotImplementedError


class GooglePeopleAuthentication(BaseAuthentication):
    auth_uri = 'https://accounts.google.com/o/oauth2/auth'
    token_uri = 'https://accounts.google.com/o/oauth2/token'
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_SECRET
    scope = settings.GOOGLE_SCOPE

    def __init__(self):
        self.get_flow()

    def get_client_config(self):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'include_granted_scopes': 'true',
            'access_type': 'offline',
        }

    def get_flow(self):

        self._flow = OAuth2WebServerFlow(**self.get_client_config())
        return self._flow

    def get_authorization_url(self, state=''):
        authorization_url = self._flow.step1_get_authorize_url(state=state)
        return authorization_url

    def response_code_or_false(self, request):
        return request.GET.get('code', False)

    def exchange_auth_code(self, code):
        self.credentials = self._flow.step2_exchange(code=code)

    def get_credentials(self, token, refresh_token):
        self._credentials = {
            'token': token,
            'refresh_token': refresh_token,
            'token_uri': self.token_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scopes': self.scopes
        }
        self.credentials = Credentials(**self._credentials)
        return self.credentials

    def get_data(self):
        info = None
        email = None
        self.people = build('people', 'v1', credentials=self.credentials)
        raw = self.people.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()
        if raw.get('names', False):
            info = list(filter(lambda x: x['metadata']['source']['type'] == 'DOMAIN_PROFILE', raw['names']))
        if raw.get('emailAddresses', False):
            email = list(filter(lambda x: x['metadata']['source']['type'] == 'DOMAIN_PROFILE', raw['emailAddresses']))
        if not info or not email:
            data = {
                'first_name': '',
                'last_name': '',
                'resource_id': raw['resourceName'],
                'email': 'invalid@email.com'
            }
        else:
            data = {
                'first_name': info[0]['givenName'],
                'last_name': info[0]['familyName'],
                'resource_id': raw['resourceName'],
                'email': email[0]['value']
            }
        return data
