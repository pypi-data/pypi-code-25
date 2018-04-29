from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from prometheus.template_backends.jinja2 import jinjaglobal


@jinjaglobal
def get_language_href(request, lang):
    url = request.get_full_path()

    parts = url.split('/')
    parts[1] = lang
    url = '/'.join(parts)
    return url if url.endswith('/') else url + '/'


@jinjaglobal
def get_languages(request):
    return [{
        'code': x[0],
        'name': x[1],
        'href': get_language_href(request, x[0])
    } for x in settings.LANGUAGES if x[0] in settings.LANGUAGE_CODES_PUBLIC]


@jinjaglobal
def ugettext(value):
    return _(value)
