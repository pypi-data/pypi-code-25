from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
VERSION = '0.0.5'

class PayApiError(Exception):
    pass

def get_model(constant_name):
    constant_value = getattr(settings, constant_name)

    try:
        return django_apps.get_model(constant_value)
    except AttributeError:
        raise ImproperlyConfigured("%s needs to be defined in settings as 'app_label.model_name'" % constant_name)
    except ValueError:
        raise ImproperlyConfigured("%s must be of the form 'app_label.model_name'" % constant_name)
    except LookupError:
        raise ImproperlyConfigured("%s refers to model '%s' that has not been installed" % (constant_name, constant_value))

def get_payment_model():
    return get_model('PAY_API_PAYMENT_MODEL')

def get_config_model():
    return get_model('PAY_API_CONFIG_MODEL')

