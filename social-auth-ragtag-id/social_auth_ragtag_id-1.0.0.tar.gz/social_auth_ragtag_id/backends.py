from social_core.backends.oauth import BaseOAuth2


class RagtagOAuth2(BaseOAuth2):
    """Ragtag ID OAuth authentication backend"""
    name = 'ragtag'
    AUTHORIZATION_URL = 'https://id.ragtag.org/oauth/authorize/'
    ACCESS_TOKEN_URL = 'https://id.ragtag.org/oauth/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_URL = 'https://id.ragtag.org/oauth/revoke_token/'
    SCOPE_SEPARATOR = ' '
    ID_KEY = 'guid'

    def get_user_details(self, response):
        """Return user details from Ragtag ID account"""
        return {
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
        }

    def user_data(self, access_token, *args, **kwargs):
        """Fetches user data from id.ragtag.org"""
        return self.get_json(
            'https://id.ragtag.org/api/me/',
            headers={
                'Authorization': 'Bearer {}'.format(access_token)
            }
        )
