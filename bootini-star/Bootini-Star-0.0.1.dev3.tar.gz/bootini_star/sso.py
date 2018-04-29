"""
Handle EVE SSO calls.
"""
__author__ = 'Ralph Seichter'

import datetime
from pprint import pprint

from requests_oauthlib import OAuth2Session

from .config import Config
from .extensions import log

scope = [
    'esi-characters.read_standings.v1',
    'esi-mail.read_mail.v1',
    'esi-skills.read_skillqueue.v1',
    'esi-wallet.read_character_wallet.v1',
]


def token_updater(x):  # pragma: no cover
    ''' Only used for debugging '''
    print('*** tu_hook:')
    pprint(x.reason)
    pprint(vars(x.request))


class EveSso(OAuth2Session):
    ''' Some code in this class is not covered by automated unit tests because it
        would require user interaction to authorize a character using EVE SSO. '''

    config = Config()
    # Required when refreshing by CCP's ESI
    refresh_kwargs = {
        'client_id': config.ESI_CLIENT_ID,
        'client_secret': config.ESI_SECRET_KEY
    }

    def __init__(self, token_dict=None):
        super().__init__(
            client_id=self.config.ESI_CLIENT_ID,
            redirect_uri=self.config.ESI_CALLBACK_URI,
            auto_refresh_url=self.config.ESI_TOKEN_URI,
            auto_refresh_kwargs=self.refresh_kwargs,
            token_updater=token_updater,
            scope=scope,
            token=token_dict
        )

    def auth_url_state(self, state=None):
        url, state = self.authorization_url(
            self.config.ESI_AUTHORIZATION_URI,
            state=state
        )
        return url, state

    def auth_token(self, code):
        self.token = self.fetch_token(
            self.config.ESI_TOKEN_URI,
            client_secret=self.config.ESI_SECRET_KEY,
            code=code
        )
        return self.token  # pragma: no cover (Not reached during tests)

    def auth_verify(self):  # pragma: no cover (Not reached during tests)
        return self.get(self.config.ESI_VERIFY_URI)

    def refresh_token(self, force_refresh=False):
        needs_refresh = False
        ea = self.token.get('expires_at')
        if ea and datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(ea - 90):  # pragma: no cover (Never true during tests)
            needs_refresh = True
            log.debug('Access token expired')
        if force_refresh or needs_refresh:
            log.debug('Attempting to refresh token')
            token = super().refresh_token(
                self.config.ESI_TOKEN_URI,
                **self.refresh_kwargs
            )
            log.debug(
                'Returning refreshed token')  # pragma: no cover (Not reached during tests)
            return token, True  # pragma: no cover (Not reached during tests)
        log.debug('Returning existing token')
        return self.token, False
