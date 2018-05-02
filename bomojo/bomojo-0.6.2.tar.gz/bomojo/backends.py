from django.conf import settings
from django.utils.module_loading import import_string

from bomojo import settings as defaults


class AbstractUserBackend(object):
    """Abstract class defining required methods for any USER_BACKEND class"""
    def is_featured_contributor(self, user):
        """Indicate whether a user is allowed to make "featured" matchups"""
        raise NotImplementedError


class DefaultUserBackend(AbstractUserBackend):
    def is_featured_contributor(self, user):
        return user.is_staff


def get_user_backend():
    backend_name = getattr(settings, 'USER_BACKEND', defaults.USER_BACKEND)
    backend_class = import_string(backend_name)
    return backend_class()
