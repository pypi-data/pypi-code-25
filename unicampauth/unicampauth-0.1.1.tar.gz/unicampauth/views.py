from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from .conf import settings
from django.apps import apps

# Get the app that contains the auth profile model
app = apps.get_app_config(settings.UNICAMP_AUTH_APP_NAME)
# Get it's model by name
AUTH_MODEL = app.get_model(settings.UNICAMP_AUTH_MODEL_NAME)
# Authenticator class used to process the login flow
AUTHENTICATOR_CLASS = settings.UNICAMP_AUTHENTICATOR_CLASS
# Validator class used to validate new users
VALIDATOR_CLASS = settings.UNICAMP_VALIDATOR_CLASS


class Authorize(RedirectView):
    auth_class = AUTHENTICATOR_CLASS
    validator = VALIDATOR_CLASS

    def get_redirect_url(self):
        redirect_url = self.auth_class().get_authorization_url()
        return redirect_url


class ExchangeCode(RedirectView):
    auth_class = AUTHENTICATOR_CLASS
    validator = VALIDATOR_CLASS
    auth_model = AUTH_MODEL

    def get_redirect_url(self):
        # Instantiate the auth class
        auth_class = self.auth_class()
        # Get authorization code from request url
        code = auth_class.response_code_or_false(self.request)
        # If no code was provided
        if not code:
            # Add error message
            messages.error(self.request, settings.UNICAMP_AUTH_FAIL_MESSAGE)
        # If successful
        else:
            # Exchange code with provider
            auth_class.exchange_auth_code(code)
            # Get the data related to the auth profile model
            data = auth_class.get_data()
            # Use the provided validator to validate the data
            if not self.validator().validate(data):
                # If the data was invalid, add error message
                messages.error(self.request, settings.UNICAMP_AUTH_FAIL_MESSAGE)
            else:
                # If it was valid, register or update the auth profile model
                profile = self.auth_model.register_or_update_user(
                    auth_class.credentials.access_token,
                    auth_class.credentials.refresh_token,
                    **data
                )
                # Login the user
                login(self.request, profile.user)
        # Finish by returning to the index
        return reverse_lazy(settings.INDEX_URL_NAME)
