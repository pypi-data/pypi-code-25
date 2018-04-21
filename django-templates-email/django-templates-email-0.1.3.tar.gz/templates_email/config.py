from django.conf import settings

_templates_email_settings = getattr(settings, 'TEMPLATES_EMAIL', None)

default_fallback_language = _templates_email_settings['FALLBACK_LANGUAGE'] if _templates_email_settings else None
