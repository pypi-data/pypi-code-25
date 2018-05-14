
from django.conf import settings
from django.contrib.auth.models import User


try: USER_MODEL = eval(getattr(settings, 'AUTH_USER_MODEL', None))
except: USER_MODEL = User

OPTIN_SETTINGS_UPDATE_MESSAGE_BOOLEAN = getattr(settings, 'OPTIN_SETTINGS_UPDATE_MESSAGE_BOOLEAN', True)
OPTIN_SETTINGS_UPDATE_MESSAGE = getattr(settings, 'OPTIN_SETTINGS_UPDATE_MESSAGE', 'Preferences Updated')