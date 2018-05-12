from django.conf import settings

from prometheus.template_backends.jinja2 import jinjaglobal


@jinjaglobal
def site_name():
    return settings.SITE_NAME


@jinjaglobal
def site_url():
    return settings.SITE_URL
