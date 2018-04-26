from __future__ import absolute_import, print_function

from django.conf import settings

CLIENT_ID = getattr(settings, 'RAGTAG_APP_ID', None)

CLIENT_SECRET = getattr(settings, 'RAGTAG_API_SECRET', None)

SCOPE = 'identity email name'

BASE_DOMAIN = 'id.ragtag.org'
API_DOMAIN = '{}/api'.format(BASE_DOMAIN)

ACCESS_TOKEN_URL = 'https://{0}/oauth/token/'.format(BASE_DOMAIN)
AUTHORIZE_URL = 'https://{0}/oauth/authorize/'.format(BASE_DOMAIN)
