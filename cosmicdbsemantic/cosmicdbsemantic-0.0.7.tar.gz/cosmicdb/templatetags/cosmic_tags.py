from django.conf import settings
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

import importlib

register = template.Library()


@register.simple_tag
def get_site_title():
    return settings.COSMICDB_SITE_TITLE or "CosmicDB"
