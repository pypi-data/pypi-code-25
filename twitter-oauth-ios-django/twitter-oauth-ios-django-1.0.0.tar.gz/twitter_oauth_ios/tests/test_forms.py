from django.test import TestCase
from twitter_oauth_ios.forms import TwitterAuthForm


class TestTwitterAuthForm(TestCase):

    form_class = TwitterAuthForm

    def setUp(self):
        self.parameter = {
            "auth_time": 1526996947,
            "user_id": 1111111111,
            "oauth_token": "1111111111-this_is_test_oauth_token",
            "oauth_token_secret": "this_is_test_oauth_token_secret",
            "screen_name": "test_screen_name",
            "display_name": "test_display_name"
        }

    def tearDown(self):
        self.parameter = None

    def test_is_valid_form(self):
        form = self.form_class(self.parameter)

        self.assertTrue(form.is_valid())

    def test_is_invalid_form(self):
        form = self.form_class({})

        self.assertFalse(form.is_valid())
