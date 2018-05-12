import random

from django.contrib.humanize.templatetags.humanize import intcomma as int_comma
from django.template.defaultfilters import floatformat as float_format

from prometheus.template_backends.jinja2 import jinjafilter, jinjaglobal


@jinjafilter
def floatformat(value, digits):
    """Порт floatformat"""
    return float_format(value, digits)


@jinjafilter
def intcomma(value, use_l10n=True):
    return int_comma(value, use_l10n=use_l10n)


@jinjaglobal
def random_int(from_number=1, to_number=9999999):
    return random.randint(from_number, to_number)
