from django.conf import settings
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

import importlib

register = template.Library()


@register.simple_tag
def get_site_title():
    return settings.COSMICDB_SITE_TITLE or "CosmicDB"


@register.simple_tag
def get_signup_button():
    button_html = ''
    if settings.COSMICDB_ALLOW_SIGNUP:
        button_html = '<a href="'+ reverse('signup') +'" class="ui fluid large primary submit button" style="margin-top: 10px;">Sign Up</a>'
    return mark_safe(button_html)
