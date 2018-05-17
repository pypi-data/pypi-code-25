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

from __future__ import unicode_literals
import json
from functools import wraps
from io import BytesIO

from django.http.request import QueryDict, MultiValueDict
from django.http.multipartparser import MultiPartParserError
from django.utils.encoding import force_text


def _file_parser(request):
    if hasattr(request, '_body'):
        # Use already read data
        data = BytesIO(request._body)
    else:
        data = request
    try:
        _data, _files = request.parse_file_upload(request.META, data)
    except MultiPartParserError:
        # An error occurred while parsing POST data. Since when
        # formatting the error the request handler might access
        # request.POST, set request._post and request._file to prevent
        # attempts to parse POST data again.
        # Mark that an error occurred. This allows request.__repr__ to
        # be explicit about it instead of simply representing an
        # empty POST
        request._mark_post_parse_error()
        raise
    return _data, _files


def _form_parser(request):
    data = QueryDict(request.body, encoding=request._encoding)
    return data, MultiValueDict()


def _json_parser(request):
    try:
        data = json.loads(
            force_text(request.body, encoding=request._encoding) or
            '{}'
        )
        request.json_data_ready = True
    except ValueError:
        request._mark_post_parse_error()
        raise
    return data, MultiValueDict()


def _blank_parser(request):
    data = QueryDict('', encoding=request._encoding)
    return data, MultiValueDict()


def _get_parser(request):
    content_type = request.META.get('CONTENT_TYPE', '')
    if content_type.startswith('multipart/form-data'):
        return _file_parser
    elif content_type.startswith('application/x-www-form-urlencoded'):
        return _form_parser
    elif content_type.startswith('application/json'):
        return _json_parser
    return _blank_parser


def parse_rest(function=None):
    "Декоратор для представлений, использующихся в качестве REST API."

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            request.json_data_ready = False
            if not hasattr(request, 'data'):
                if request.method == 'GET':
                    request.data = request.GET
                else:
                    parser = _get_parser(request)
                    if request.method == 'POST':
                        # Стандартная обработка форм
                        if parser in (_form_parser, _file_parser):
                            request.data = request.POST
                        else:
                            request.data, request._files = parser(request)
                    else:
                        request.data, request._files = parser(request)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator
