from datetime import datetime
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from social_django.models import UserSocialAuth
from twitter_oauth_ios.views import AuthView

import json


class TestAuthView(TestCase):

    endpoint = reverse('twitter_oauth_ios:auth_view')
    user_model = get_user_model()

    def setUp(self):
        self.auth_view = AuthView.as_view()
        self.factory = RequestFactory()
        self.parameter = {
            "user_id": 1111111111,
            "oauth_token": "1111111111-this_is_test_oauth_token",
            "oauth_token_secret": "this_is_test_oauth_token_secret",
            "screen_name": "test_screen_name",
            "display_name": "test_display_name"
        }

    def tearDown(self):
        self.factory = None
        self.parameter = None
        call_command('flush', interactive=False)

    def test_not_allow_method(self):
        request = self.factory.post(self.endpoint, self.parameter)
        request.content_type = 'application/json'
        response = self.auth_view(request)

        self.assertEqual(response.status_code, 405)

    def test_failure_put(self):
        request = self.factory.put(self.endpoint, {})
        request.content_type = 'application/json'
        response = self.auth_view(request)

        self.assertEqual(json.loads(response.content.decode('utf-8')), {'result': 'error'})
        self.assertEqual(response.status_code, 400)

    def test_success_create_put(self):
        request = self.factory.put(self.endpoint, json.dumps(self.parameter))
        request.content_type = 'application/json'
        response = self.auth_view(request)

        self.assertEqual(json.loads(response.content.decode('utf-8')), {'result': 'success'})
        self.assertEqual(response.status_code, 200)

    def test_success_update_put(self):
        user = self.user_model.objects.create_user(
            username=self.parameter['screen_name'],
            first_name=self.parameter['display_name'],
            is_active=True
        )
        user.save()

        extra_data = {
            'auth_time': int(datetime.now().strftime('%s')),
            'id': self.parameter['user_id'],
            'access_token': {
                'oauth_token': self.parameter['oauth_token'],
                'oauth_token_secret': self.parameter['oauth_token_secret'],
                'user_id': self.parameter['user_id'],
                'screen_name': self.parameter['screen_name']
            }
        }
        user_social_auth = UserSocialAuth(
            user=user,
            provider='twitter',
            uid=self.parameter['user_id'],
            extra_data=extra_data
        )
        user_social_auth.save()

        request = self.factory.put(self.endpoint, json.dumps(self.parameter))
        request.content_type = 'application/json'
        response = self.auth_view(request)

        self.assertEqual(json.loads(response.content.decode('utf-8')), {'result': 'success'})
        self.assertEqual(response.status_code, 200)
