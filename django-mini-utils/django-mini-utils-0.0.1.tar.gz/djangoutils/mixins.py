# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from .exceptions import ArgumentTypeError


class GetArgMixin(object):
    """
    This mixin should use with django rest framework view
    """

    def get_argument(self, name, _type, default=None):
        """
        Get the value of argument specify by name.

        :param name: The name of argument.
        :param _type: A callable which will be called and pass the string value of the argument,
            it should return a transformed value.
        :param default: The default value of argument.
        :returns: The value of argument.
        """
        method = self.request.method
        if method in ('POST', 'PUT', 'PATCH'):
            value = self.request.data.get(name, default)
        elif method == 'GET':
            value = self.request.query_params.get(name, default)

        try:
            value = _type(value)
        except (ValueError, TypeError) as e:
            raise ArgumentTypeError
        return value
