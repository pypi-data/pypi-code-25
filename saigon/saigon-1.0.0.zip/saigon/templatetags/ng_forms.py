# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.safestring import mark_safe
import json
from copy import copy
import re

register = Library()

@register.simple_tag
def ng_form(form):
    """
    Tag renderuje dyrektywe 'sg-dj-form', ktora na formularzu django inicjuje dane i pokazje bledy.
    
    Usage:
        <form name="myForm" action="." method="post" {% ng_form form=form %} novalidate>
    
    Requirements:
        saigon.forms.js
    """

    form_data = {}
    form_errors = {}

    # jesli jest form.initial zwracamy go
    if form.initial:
        form_data = json.dumps(form.initial)

    # natomiast jesli pojawi sie form.data nadpisujemy form.initial
    if form.data:
        # nie chcemy przekazywać haseł...
        _data = copy(form.data)
        sensitive_data = re.compile('api|token|key|secret|password|signature', re.I)
        for key in _data:
            if sensitive_data.search(key):
                _data[key] = None

        form_data = json.dumps(_data)

    if form.errors:
        # parusjemy dj messages dla formatu saigon'a
        for key, value  in json.loads(form.errors.as_json()).items():
            try:
                message = value[0].get('message')
                # change ' & " -> '
                message = message.replace('"', "&#39;").replace("'", "&#39;")
                form_errors[key] = [message]
            except IndexError:
                pass

        form_errors = json.dumps(form_errors)

    # zamienieamy ' -> ", poniewaz rozbijaja tagi htmlowe i jest kwas....
    html_context = {
        'form_data': form_data.replace("'", "&#39;") if form_data else form_data,
        'form_errors': form_errors
    }

    # renderujemy html'a dyrektywy
    html = """ sg-dj-form='[%(form_data)s, %(form_errors)s]' """ % html_context

    return mark_safe(html)

@register.simple_tag
def ng_messages(form, field, messages = None):
    """
    Tag renderuje ng-messages dla wskazanego pola we wskazanym formularzu.
    Domyslnie zawsze required i rejected. Opcjonalnie mozna dostarczyc wlasna liste messages.
    
    Usage:
        {% ng_messages form="myForm" field="test" messages="rejected:[[ personChangeForm.first_name.$message ]], wrong : [[ personChangeForm.first_name.$message ]]," %}

    Requirements:
        saigon.forms.js    
    """

    # message list
    message_list = [
        ("required", "To pole jest wymagane"),
        ("rejected", "[[ %(form)s.%(field)s.$message ]]" % {'form': form, 'field': field, })
    ]

    # parse messages
    if messages:
        for s in messages.split(','):
            splited = s.split(':')
            if not len(splited) is 2:
                continue

            # add message
            key = splited[0].strip()
            value = splited[1].strip()
            message_list.append((key, value))

    html = """<div ng-messages="%(form)s.%(field)s.$error">""" % {'form': form, 'field': field, }

    for m in message_list:
        html += """<div ng-message="%(key)s">%(value)s</div>""" % {'key': m[0], 'value': m[1]}

    html += """</div>"""

    return mark_safe(html)
