from django.utils.translation import ugettext_lazy as _
from .models import Tag
from django.conf import settings


def tags(request):
    """
    Context processor that provides list of tags.
    :return: list of tags
    """
    _tags = Tag.objects.all()
    return {'tags': _tags}


def blog_settings(request):
    """
    Context processor for blog settings defined in settings.py.
    :return: dict of settings
    """
    return {'blog_settings': {
        'description': getattr(settings, 'BLOG_DESCRIPTION', _("Simple Blog Application for Django")),
        'keywords': getattr(settings, 'BLOG_KEYWORDS', _("blog, demo, django")),
        'author': getattr(settings, 'BLOG_AUTHOR', _("pyninjas"))
    }}
