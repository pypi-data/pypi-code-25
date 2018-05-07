# -*- coding: utf-8 -*-

from django.utils.crypto import salted_hmac

from django_restful import RestfulApiError

from django_sae.models.user import UserModel


class UserWrapper(object):

    def __init__(self, user):
        if not isinstance(user, dict):
            user = user.__dict__

        for k, v in user.iteritems():
            setattr(self, k.lower(), v)

        self.pk = self.id
        self.password = self.login_password
        self.is_authenticated = self.authenticated

    def save(self, **field):
        pass

    def authenticated(self):
        return True

    def get_session_auth_hash(self):
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()


class ModelBackend(object):
    """
    Authenticates against django.contrib.auth.models.User.
    """
    supports_inactive_user = True

    # TODO: Model, login attribute name and password attribute name should be
    # configurable.
    def authenticate(self, username=None, password=None):
        try:
            _service = UserModel()
            user = _service.authenticate(username, password)
            return UserWrapper(user)
        except RestfulApiError:
            return None

    def get_user(self, user_id):
        try:
            _service = UserModel()
            user = _service.get_user(user_id)
            return UserWrapper(user)
        except RestfulApiError:
            return None
