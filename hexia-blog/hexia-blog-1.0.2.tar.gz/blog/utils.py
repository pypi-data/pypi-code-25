from django.conf import settings
from django.contrib.auth.models import User

try: USER_MODEL = eval(getattr(settings, 'AUTH_USER_MODEL', None))
except: USER_MODEL = User

BLOG_PAGINATION = (getattr(settings, 'BLOG_PAGINATION', 20))