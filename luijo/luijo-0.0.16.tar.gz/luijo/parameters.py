#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: luijo.parameters
.. moduleauthor:: Pat Daburu <pat@daburu.net>

These are custom parameters for use in Luigi scripts.
"""

import uuid
from typing import Any
import luigi.parameter


class ClassParameter(luigi.parameter.Parameter):
    """
    This is a Luigi parameter that takes a class, or the fully-qualified name of
    a class.
    """
    def parse(self, x):
        """
        Parse a parameter string.

        :param x: the parameter string
        :return: the parsed value
        """
        # If the value is  a class (somehow)...
        if isinstance(x, type):
            # ...simply return it.
            return x
        elif isinstance(x, str):
            # We believe this is the fully-qualified name of a class, so split
            # it into its constituent parts.
            parts = x.split('.')
            mod = '.'.join(parts[:-1])
            cls = parts[-1]
            # Create a temporary name to hold the class we import.  (We don't
            # want a collision.)
            import_as = 'cls_{}'.format(str(uuid.uuid4()).replace('{', '').replace('-', ''))
            # Create a dictionary to hold local variables.
            _locals = {}
            # Compile a dynamic block of code.
            code = compile(
                """from {mod} import {cls} as {import_as}; _locals['cls'] = {import_as}; del import_as""".format(  # pylint: disable=line-too-long
                    mod=mod, cls=cls,
                    import_as=import_as),
                '<string>',
                'exec')
            # Execute the dynamic code.
            exec(code) in globals(), _locals  # pylint: disable=expression-not-assigned, exec-used
            # The class should
            cls = _locals['cls']
            return cls
        else:  # Otherwise, we don't know how to deal with this type.
            raise ValueError('The value must be of type {type} or {str}.'.format(
                type=type(type),
                str=type(str)))

    def serialize(self, x):
        """
        Serialize an object to a parameter string.

        :param x: the object
        :return: the parameter string
        """
        # If the value is already a string...
        if isinstance(x, str):
            # ...just return it.
            return x
        elif isinstance(x, type):  # If it's a type...
            # ...format it's fully qualified name.
            return'{mod}.{cls}'.format(mod=x.__module__, cls=x.__name__)
        else:  # Otherwise, we don't know how to deal with this type.
            raise ValueError(
                'The value must be of type {type} or {str}.'.format(
                    type=type(type),
                    str=type(str)))


def is_empty_parameter(param: Any):
    """
    Test a Luigi parameter to see if it is an empty value.

    :param param: the parameter
    :return: `True` if the parameter is empty, otherwise `False`
    """
    # If the parameter is a regular luigi parameter, or a string...
    if isinstance(param, (str, luigi.Parameter)):
        # ...let's look at it as a string.
        sss = str(param)
        # If it's an empty string value, it's an empty parameter.  Otherwise,
        # it's not.
        return sss is None or not sss.strip()
    # Otherwise, the return value just depends upon whether or not the
    # reference is to None.
    return param is None
