import os

from django.conf import settings

from prometheus.template_backends.jinja2 import jinjaglobal


@jinjaglobal
def static(file_path):
    filemtime = int(
        os.path.getmtime(os.path.join(settings.STATIC_ROOT, file_path))
    )
    return '%s%s?v=%s' % (settings.STATIC_URL, file_path, filemtime)
