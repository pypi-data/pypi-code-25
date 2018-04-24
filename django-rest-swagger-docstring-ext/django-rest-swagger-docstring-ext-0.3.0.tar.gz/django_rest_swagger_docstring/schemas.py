# coding: utf8

from __future__ import unicode_literals

from django.utils.encoding import force_text
from rest_framework import serializers
from rest_framework.compat import (
    coreapi, urlparse
)
from rest_framework.permissions import AllowAny
from rest_framework.schemas import SchemaGenerator
from rest_framework.utils.field_mapping import ClassLookupDict
from .parsers import YAMLDocstringParser

types_lookup = ClassLookupDict({
    serializers.Field: 'string',
    serializers.IntegerField: 'integer',
    serializers.FloatField: 'number',
    serializers.DecimalField: 'number',
    serializers.BooleanField: 'boolean',
    serializers.FileField: 'file',
    serializers.MultipleChoiceField: 'array',
    serializers.ManyRelatedField: 'array',
    serializers.PrimaryKeyRelatedField: 'integer',
    serializers.Serializer: 'object',
    serializers.ListSerializer: 'array'
})


class DocsSchemaGenerator(SchemaGenerator):

    parameters_parser_cls = YAMLDocstringParser

    def get_link(self, path, method, view):
        """ Return a `coreapi.Link` instance for the given endpoint. """
        fields = []
        getters = [self.get_path_fields, self.get_serializer_fields,
                   self.get_pagination_fields, self.get_filter_fields,
                   self.get_docs_fields]
        for getter in getters:
            try:
                fields.extend(getter(path, method, view))
            except Exception:
                pass

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method, view)
        else:
            encoding = None

        description = self.get_description(path, method, view)
        permissions = self.get_permissions_docs(path, method, view)
        if permissions is not None:
            description = "{}\nPermissions:\n========\n{}".format(description, permissions)

        if self.url and path.startswith('/'):
            path = path[1:]

        return coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=description
        )

    def _get_method_method(self, path, method, view):
        method_name = getattr(view, 'action', method.lower())
        return getattr(view, method_name, None)

    def get_docs_fields(self, path, method, view):
        """ Return a `coreapi.Fields array` instance from docstrings """
        method_docstring = self._get_method_method(path, method, view).__doc__
        if method_docstring is None:
            docs = view.get_view_description()
        else:
            docs = str(method_docstring)
        parameters_parser = self.parameters_parser_cls(docs)
        parameters = parameters_parser.get_parameters()
        coreapi_fields = []
        for parameter in parameters:
            coreapi_fields.append(coreapi.Field(
                name=parameter.get('name'),
                required=parameter.get('required'),
                location=parameter.get('param_type'),
                type=parameter.get('data_type'),
                description=parameter.get('description'),
            ))
        return coreapi_fields

    def has_view_permissions(self, path, method, view):
        return True

    def get_serializer_fields(self, path, method, view):
        """
        Return a list of `coreapi.Field` instances corresponding to any
        request body input, as determined by the serializer class.
        """
        fields = []

        if method not in ('PUT', 'PATCH', 'POST', 'DELETE'):
            return fields

        serializer = None

        method_method = self._get_method_method(path, method, view)
        serializer_cls = getattr(method_method, '_serializer_class', None)
        if serializer_cls is not None:
            serializer = serializer_cls()

        if serializer is None:
            if hasattr(view, 'get_serializer'):
                serializer = view.get_serializer()

        if serializer is None:
            return fields

        if isinstance(serializer, serializers.ListSerializer):
            return [
                coreapi.Field(
                    name='data',
                    location='body',
                    required=True,
                    type='array'
                )
            ]

        if not isinstance(serializer, serializers.Serializer):
            return fields

        for field in serializer.fields.values():
            if field.read_only or isinstance(field, serializers.HiddenField):
                continue

            required = field.required and method != 'PATCH'
            description = force_text(field.help_text) if field.help_text else ''
            field = coreapi.Field(
                name=field.field_name,
                location='form',
                required=required,
                description=description,
                type=types_lookup[field],
                # example=field.default,
                # schema=...
            )
            fields.append(field)

        return fields

    def get_permissions_docs(self, path, method, view):
        permissions = view.get_permissions()
        permissions_docs = ''
        for permission in permissions:
            if isinstance(permission, AllowAny):
                continue
            if permission.__class__.__doc__ is not None:
                permissions_docs = '{}- {} - {}\n'.format(permissions_docs, permission.__class__.__name__,
                                                          permission.__class__.__doc__)
            else:
                permissions_docs = '{}- {}\n'.format(permissions_docs, permission.__class__.__name__)
        if len(permissions_docs) > 0:
            return permissions_docs
        return None

    def get_description(self, *args, **kwargs):
        result = super(DocsSchemaGenerator, self).get_description(*args, **kwargs)
        # Attempt to remove the parameters yaml from it.
        # XXX: Not clear how it was ever supposed to work otherwise.
        # WARN/XXX: `view.get_view_description()` result will also be processed with this.
        base_result = result
        result, _ = self.parameters_parser_cls.split_docstring(result)
        result = result or base_result
        return result
