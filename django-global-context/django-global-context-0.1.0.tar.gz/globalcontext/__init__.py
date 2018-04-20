from django.conf import settings


def ga_processor(request):
    return {
        'SENTRY_DSN': getattr(settings, 'SENTRY_DSN', None),
    }
