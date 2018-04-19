from __future__ import print_function, division

from cerberus import Validator
from cerberus.platform import _int_types, _str_type

import functools
import inspect
import json

import numpy as np
import astropy.units as units
from astropy.coordinates import SkyCoord
from astropy.units import Quantity


class ValidationError(Exception):
    pass


class CoordValidator(Validator):
    def __init__(self, *args, **kwargs):
        # if 'additional_context' in kwargs:
        #     self.additional_context = kwargs['additional_context']
        super(CoordValidator, self).__init__(*args, **kwargs)

    def _validate_type_SkyCoord(self, value):
        return isinstance(value, SkyCoord)

    def _validate_type_numberlike_ndarray(self, value):
        if isinstance(value, np.ndarray):
            return (value.dtype.kind in 'iuf')
        return False

    def _validate_type_Quantity(self, value):
        return isinstance(value, Quantity)

    def _validate_type_angle(self, value):
        return (isinstance(value, Quantity) and value.unit.is_equivalent(units.rad))

    def _validate_type_length(self, value):
        return (isinstance(value, Quantity) and value.unit.is_equivalent(units.m))

    def _validate_type_scalar(self, value):
        if type in (float, int, np.floating, np.integer):
            return True
        elif isinstance(value, Quantity) and value.isscalar:
            return True
        return False

    def _validate_type_list_of_numbers(self, value):
        if type(value) not in (list, tuple):
            return False
        for el in value:
            if type(el) not in (float, int, long):
                return False
        return True

    def _validate_type_np_number(self, value):
        return (isinstance(value, np.floating) or isinstance(value, np.integer))

    def _validate_maxall(self, max_val, field, value):
        """
        Test whether all the elements of an array are greater than a given
        amount.

        The rule's arguments are validated against this schema:
        {}
        """
        if np.any(np.array(value) > max_val):
            self._error(field, 'Must not be greater than {}'.format(max_val))

    def _validate_minall(self, min_val, field, value):
        """
        Test whether all the elements of an array are less than a given amount.

        The rule's arguments are validated against this schema:
        {}
        """
        if np.any(np.array(value) < min_val):
            self._error(field, 'Must not be less than {}'.format(min_val))

    def _validate_sameshape(self, target_field, field, value):
        """
        Test whether this field has the same shape as one or more other fields.
        If a target field does not exist, no error is raised (use 'dependency'
        to require the existence of the target field).

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(target_field, _str_type):
            target_field = [target_field]
        shape = value.shape
        for target in target_field:
            res = self._lookup_field(target)[1]
            if res is None:
                return True # Target field does not exist
                # self._error(field, 'Must have same shape as {}, which is not present.'.format(target))
            elif not hasattr(res, 'shape'):
                self._error(field, 'Must have same shape as {}, which has no shape.'.format(target))
            elif res.shape != shape:
                self._error(field, 'Must have same shape as {}.'.format(target))
        return True


def to_array(dtype):
    def f(value):
        return np.array(value, dtype=dtype)
    return f


def to_quantity(unit_spec, dtype='f8'):
    def f(value):
        if value is None:
            return None
        if isinstance(value, Quantity):
            return value.to(unit_spec)
        elif isinstance(value, np.ndarray):
            return value.astype(dtype) * unit_spec
        else:
            return np.array(value, dtype=dtype) * unit_spec
    return f


def validated_by(schema):
    v = CoordValidator(schema, allow_unknown=False)

    def decorator(f):
        @functools.wraps(f)
        def validated(*args, **kwargs):
            try:
                arg_dict = inspect.getcallargs(f, *args, **kwargs)
            except TypeError as err:
                raise ValidationError(err.message)

            arg_dict.pop('self')
            kw = arg_dict.pop('kwargs', {})
            arg_dict.update(**kw)

            # if ('pct' in arg_dict) and (arg_dict['pct'] is not None):
            #     print(arg_dict)

            if not v.validate(arg_dict):
                raise ValidationError(
                    'Validation of arguments failed: ' +
                    json.dumps(v.errors, indent=2))

            return f(*args, **kwargs)
        return validated
    return decorator
