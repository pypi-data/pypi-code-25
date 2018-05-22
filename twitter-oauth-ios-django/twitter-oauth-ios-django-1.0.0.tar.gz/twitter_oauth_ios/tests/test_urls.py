from django.test import TestCase
from django.urls import resolve, reverse
from twitter_oauth_ios.views import AuthView


class TestUrlResolveTests(TestCase):

    def setUp(self):
        self.auth_view = AuthView.as_view()

    def tearDown(self):
        self.auth_view = None

    def test_url_resolves_to_auth_view(self):
        found = resolve(reverse('twitter_oauth_ios:auth_view'))

        self.assertEqual(found.func.view_class, AuthView)
