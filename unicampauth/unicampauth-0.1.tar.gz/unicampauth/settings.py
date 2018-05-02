from django.conf import settings


def get(key, default=''):
    return getattr(settings, key, default)


def get_class(module, class_name):
    return getattr(module, class_name)


# index url name
INDEX_URL_NAME = get('INDEX_URL_NAME', 'index')

# site url
SITE_URL = get('SITE_URL', 'http://localhost:8000')

# Profile's app name
UNICAMP_AUTH_APP_NAME = get('UNICAMP_AUTH_APP_NAME', 'unicampauth')

# Profile's model name
UNICAMP_AUTH_MODEL_NAME = get('UNICAMP_AUTH_MODEL_NAME', 'GoogleAuthProfile')

# Authenticator class to be used
UNICAMP_AUTHENTICATOR_CLASS = get('UNICAMP_AUTHENTICATOR_CLASS', 'unicampauth.authenticators.GooglePeopleAuthentication')

# Validator class to be used
UNICAMP_VALIDATOR_CLASS = get('UNICAMP_VALIDATOR_CLASS', 'unicampauth.validators.GUnicampValidator')

# Error message showed when authentication fails
UNICAMP_AUTH_FAIL_MESSAGE = get('UNICAMP_AUTH_FAIL_MESSAGE', 'Não foi possível confirmar sua identidade!')

GOOGLE_CLIENT_ID = get('GOOGLE_CLIENT_ID')

GOOGLE_SECRET = get('GOOGLE_SECRET')

GOOGLE_SCOPE = get('GOOGLE_SCOPE')
