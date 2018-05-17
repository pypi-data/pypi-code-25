# -*- coding: utf-8 -*-
#
#   Copyright 2016 Grigoriy Kramarenko <root@rosix.ru>
#
#   This file is part of DirectApps.
#
#   DirectApps is free software: you can redistribute it and/or
#   modify it under the terms of the GNU Affero General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   DirectApps is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with DirectApps. If not, see
#   <http://www.gnu.org/licenses/>.
#

from django.utils import six
from django.utils.encoding import force_text
from django.utils.functional import lazy

from directapps.conf import MASK_PASSWORD_FIELDS


def access(request):
    "Проверяет, является ли пользователь запроса сотрудником."
    return request.user.is_staff


def get_all_model_perms(model):
    "Возвращает итератор всех разрешений модели."
    meta = model._meta
    app_label = meta.app_label
    model_name = meta.model_name
    for p in meta.permissions:
        yield '%s.%s' % (app_label, p[0])
    for p in meta.default_permissions:
        yield '%s.%s_%s' % (app_label, p, model_name)


def get_model_perms(user, model):
    "Возвращает итератор всех разрешений, доступных пользователю."
    for p in get_all_model_perms(model):
        if user.has_perm(p):
            yield p


def has_model_perms(user, model):
    "Проверяет доступность модели для пользователя."
    for p in get_model_perms(user, model):
        return True
    return False


def is_m2m_layer(model):
    "Проверяет, является ли модель связкой для поля `ManyToManyField`."
    meta = model._meta
    fields = meta.fields
    if len(fields) == 3:
        f0, f1, f2 = fields
        if f1.rel and f2.rel:
            if f1.rel.one_to_many and f2.rel.one_to_many:
                return True
    return False


def serialize_field(f):
    "Сериализует поля моделей."
    data = {
        'name': f.name,
        'type': f.__class__.__name__,  # like get_internal_type()
        'display_name': f.verbose_name,
    }
    if f.name == 'password':
        data['mask_password'] = MASK_PASSWORD_FIELDS
    if f.max_length:
        data['max_length'] = f.max_length
    if f.description:
        data['description'] = f.description % data
    if f.help_text:
        data['help_text'] = f.help_text
    if f.choices:
        data['choices'] = f.get_choices(include_blank=False)
    if f.related_model:
        m = f.related_model._meta
        data['relation'] = '%s.%s' % (m.app_label, m.model_name)

    if f.has_default():
        data['has_default'] = True
        is_callable = callable(f.default)
        # Поскольку сериализоваться поля могут и должны задолго до создания
        # объектов, то вычислением значения должно заниматься клиентское
        # приложение. Поэтому клиент должен понимать и преобразовывать
        # значение "auto" в реальном времени.
        is_auto = data['type'] in (
            'DateField', 'DateTimeField', 'TimeField', 'UUIDField',
        )
        if is_auto and is_callable:
            data['default'] = 'auto'
        elif is_callable:
            data['default'] = f.default()
        else:
            data['default'] = f.default
    # True boolean fields send only
    if f.primary_key:
        data['primary_key'] = True
    if f.unique:
        data['unique'] = True
    if not f.editable or f.auto_created:
        data['readonly'] = True
    if f.null:
        data['null'] = True
    if f.blank:
        data['blank'] = True
    if f.hidden:
        data['hidden'] = True
    if f.many_to_many:
        data['many_to_many'] = True
    if f.many_to_one:
        data['many_to_one'] = True
    if f.one_to_many:
        data['one_to_many'] = True
    if f.one_to_one:
        data['one_to_one'] = True

    return data


def join_display_names(*args):
    return ': '.join([force_text(s) for s in args])


join_display_names_lazy = lazy(join_display_names, six.text_type)
