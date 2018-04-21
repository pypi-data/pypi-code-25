import copy
import numpy as np
from jsonextended import edict
from jsonschema import validate
from jsonschema import validators, Draft4Validator
from jsonschema.exceptions import ValidationError


# add some validators for n-dimensional data
# an example of custom validators: https://lat.sk/2017/03/custom-json-schema-type-validator-format-python/
def nddim_validator(validator, value, instance, schema):
    """ validators for n-dimensional data shape

    Parameters
    ----------
    validator
    value
    instance
    schema

    Returns
    -------

    """
    dim = len(np.asarray(instance).shape)
    if value != dim:
        yield ValidationError(
            "object is of dimension {} not {}".format(dim, value))


def ndtype_validator(validator, value, instance, schema):
    """ validators for n-dimensional data dtype

    Parameters
    ----------
    validator
    value
    instance
    schema

    Returns
    -------

    """
    try:
        np.asarray(instance, dtype=value)
    except (ValueError, TypeError):
        yield ValidationError(
            "object cannot be coerced to type %s" % value)


_element_schema = {
    "repeat_cell": {
        'type': 'object',
        'required': ['cell_vectors', 'color_bbox', 'centre', 'type', 'name', 'sites', 'bonds'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'repeat_cell'},
            'cell_vectors': {'type': 'object', 'required': ['a', 'b', 'c']},
            'centre': {'type': 'array', "items": {"type": "number"}, 'minItems': 3, 'maxItems': 3},
            'sites': {
                'type': 'array',
                'items': {
                    'type': "object",
                    'required': ["radius", "color_fill", "color_outline", "transparency", "label", "ccoord"],
                    'properties': {
                        "radius": {"type": "number", "minimum": 0.},
                        "transparency": {"type": "number", "minimum": 0., "maximum": 1.},
                        "label": {"type": "string"},
                        "ccoord": {"type": "array", "items": {"type": "number"}, 'minItems': 3, 'maxItems': 3}
                    }
                }
            },
            'bonds': {
                'type': 'array',
                'items': {
                    "type": "object",
                    'required': ["label", "coord_label", "radius", "include_periodic"],
                    'properties': {
                        "label": {"type": "string"},
                        "coord_label": {"type": "string"},
                        "max_dist": {"type": "number", "minimum": 0.},
                        "radius": {"type": "number", "minimum": 0.},
                        "include_periodic": {"type": "boolean"}
                    }
                }
            }
        }
    },
    # 'repeat_poly': {
    #     'type': 'object',
    #     'required': ['cell_vectors', 'centre', 'polys', 'type',
    #                  'color', 'solid'],
    #     'properties': {
    #         'type': {'type': 'string', 'pattern': 'repeat_poly'},
    #         'cell_vectors': {'required': ['a', 'b', 'c']},
    #         'polys': {'type': 'array'},
    #         'solid': {'type': 'boolean'}
    #     }
    # },
    'repeat_density': {
        'type': 'object',
        'required': ['name', 'dtype', 'cell_vectors', 'centre', 'dcube', 'type', 'color_bbox'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'repeat_density'},
            "name": {"type": "string"},
            "dtype": {"type": "string"},
            'cell_vectors': {'type': 'object', 'required': ['a', 'b', 'c']},
            'dcube': {'nddim': 3, 'ndtype': 'float'},
            'centre': {'type': 'array', "items": {"type": "number"}, 'minItems': 3, 'maxItems': 3},
        }
    },
}

_transform_schema = {
    "local_repeat": {
        'type': 'object',
        'required': ['repeats', 'type'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'local_repeat'},
        }
    },
    "local_align": {
        'type': 'object',
        'required': ['cvector', 'direction', 'type'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'local_align'},
        }
    },
    "translate_to": {
        'type': 'object',
        'required': ['centre', 'type'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'translate_to'},
        }
    },
    "slice": {
        'type': 'object',
        'required': ['type', 'centre', 'normal', 'lbound', 'ubound'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'slice'},
        }
    },
    "resize": {
        'type': 'object',
        'required': ['type', 'sfraction'],
        'properties': {
            'type': {'type': 'string', 'pattern': 'resize'},
            'sfraction': {'type': 'number'}
        }
    },
}


def get_schema(eltypes=None, trtypes=None):
    """

    Parameters
    ----------
    eltypes: list or None
        element schemas to allow (if None, allow all)
    trtypes: list or None
        transform schemas to allow (if None, allow all)

    Returns
    -------

    """

    eschemas = list(_element_schema.values()) if eltypes is None else [_element_schema[e] for e in eltypes]
    tschemas = list(_transform_schema.values()) if trtypes is None else [_transform_schema[e] for e in trtypes]

    vschema = {
        'type': 'object',
        'required': ['elements', 'transforms'],
        'properties': {
            'elements': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'required': ['transforms'],
                    'properties': {
                        'transforms': {
                            'type': 'array',
                            'items': {
                                # 'type': 'object',
                                # 'required': ['type'],
                                # 'oneOf': tschemas
                            },
                        },
                    },
                    # 'oneOf': eschemas
                },
            },
            'transforms': {
                'type': 'array',
                'items': {
                    # 'type': 'object',
                    # 'required': ['type'],
                    # 'oneOf': tschemas
                },

            }
        }
    }

    if len(tschemas) > 1:
        edict.indexes(vschema, ["properties", "transforms", "items"])["oneOf"] = tschemas
        edict.indexes(vschema,
                      ["properties", "elements", "items", "properties", "transforms", "items"])["oneOf"] = tschemas
    else:
        vschema["properties"]["transforms"]["items"] = tschemas[0]
        edict.indexes(vschema,
                      ["properties", "elements", "items", "properties", "transforms"])["items"] = tschemas[0]

    if len(eschemas) > 1:
        edict.indexes(vschema, ["properties", "elements", "items"])["oneOf"] = eschemas
    else:
        vschema["properties"]["elements"]["items"] = edict.merge(
            [vschema["properties"]["elements"]["items"], eschemas[0]], append=True)

    # edict.pprint(vschema, depth=None)
    return vschema


def process_vstruct(vstruct, eltypes=None, trtypes=None, deepcopy=False):
    """ validate the vstruct

    Parameters
    ----------
    vstruct: dict
    eltypes: list or str or None
        element schemas to allow (if None, allow all)
    trtypes: list or None
        transform schemas to allow (if None, allow all)
    deepcopy:
        deepcopy structure before returning

    Returns
    -------

    """
    validator = validators.extend(
        Draft4Validator,
        validators={
            'nddim': nddim_validator,
            'ndtype': ndtype_validator})

    if "elements" not in vstruct:
        vstruct = {"elements": [vstruct], "transforms": []}

    validator(get_schema(eltypes=eltypes, trtypes=trtypes)).validate(vstruct)

    if deepcopy:
        return copy.deepcopy(vstruct)
    else:
        return vstruct

