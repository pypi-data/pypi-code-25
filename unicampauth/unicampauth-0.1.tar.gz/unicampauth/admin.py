from django.contrib import admin
from .conf import settings
from django.apps import apps
# Register your models here.

app = apps.get_app_config(settings.UNICAMP_AUTH_APP_NAME)
AUTH_MODEL = app.get_model(settings.UNICAMP_AUTH_MODEL_NAME)

admin.site.register(AUTH_MODEL)
