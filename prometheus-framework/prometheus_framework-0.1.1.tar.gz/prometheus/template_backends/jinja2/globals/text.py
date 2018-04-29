import re

from prometheus.template_backends.jinja2 import jinjafilter


phone_re = re.compile(r'(\.|\s|-|\)|\()+')
whitespace_re = re.compile(r'(\s|-|\)|\()+', re.MULTILINE)


@jinjafilter
def phone_url(val):
    val = strip_whitescapes(val, phone_re)

    # если не 8 800
    if not val.startswith('8'):
        if not val.startswith('+'):
            val = '+7' + val

    return val


@jinjafilter
def strip_whitescapes(val, re_obj=whitespace_re):
    return re_obj.sub('', val)


@jinjafilter
def rjust(value, width, fillchar):
    return str(value).rjust(width, fillchar)
