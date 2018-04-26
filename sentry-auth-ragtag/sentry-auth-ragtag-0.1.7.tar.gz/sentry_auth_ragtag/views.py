from __future__ import absolute_import, print_function

from django import forms
from sentry.auth.view import AuthView, ConfigureView
from sentry.models import AuthIdentity

from .client import RagtagClient


def _get_name_from_email(email):
    """
    Given an email return a capitalized name. Ex. john.smith@example.com would return John Smith.
    """
    name = email.rsplit('@', 1)[0]
    name = ' '.join([n_part.capitalize() for n_part in name.split('.')])
    return name


class FetchUser(AuthView):
    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.client = RagtagClient(client_id, client_secret)
        super(FetchUser, self).__init__(*args, **kwargs)

    def handle(self, request, helper):
        access_token = helper.fetch_state('data')['access_token']

        user = self.client.get_user(access_token)

        # A user hasn't set their name in their Ragtag profile so it isn't
        # populated in the response
        if not user.get('full_name'):
            user['name'] = _get_name_from_email(user['email'])

        helper.bind_state('user', user)

        return helper.next_step()


class RagtagConfigureView(ConfigureView):
    def dispatch(self, request, organization, auth_provider):
        return self.render('sentry_auth_ragtag/configure.html')
