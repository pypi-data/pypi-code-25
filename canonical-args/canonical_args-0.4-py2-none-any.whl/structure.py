"""
Provides utilities for checking the structure of a list
or dict against provided structure mandates and details.
"""
from __future__ import absolute_import

import json

from . import check



def checkspec(spec, args=[], kwargs={}):

    def recurse(level, name, types, values, arg):

        subtype = check.eval_subtype(types)

        if isinstance(subtype, check.ChoiceOfOne):
            # argtype = type(arg)
            # subvalue = values[check.type_to_string(argtype)]

            index = None
            for i, st in enumerate(subtype):
                if isinstance(st, (list, dict)):
                    st = type(st)
                if isinstance(arg, st):
                    index = i
                    break

            argtype = subtype[index]
            subvalue = values[check.type_to_string(type(arg))]

            recurse(level+1,
                    name,
                    argtype,
                    subvalue,
                    arg)

        # structlist
        elif isinstance(subtype, list) and isinstance(values, list):
            arg = check.check_subtype(name, type(subtype), arg)

            # check for matching length
            if not len(arg) == len(subtype):
                raise AssertionError(
                    "arg `{}` expected of length {}. got arg"\
                    " of length {}".format(name, len(arg), len(subtype)))

            for index, val in enumerate(arg):
                recurse(level+1,
                        name+"#"+str(index),
                        subtype[index],
                        values[index],
                        val)

        # structdict
        elif subtype == dict and isinstance(values, dict):
            arg = check.check_subtype(name, subtype, arg)

            # check for required keys
            required = [key for key in values.keys() \
                        if "required" not in values[key] or \
                        values[key]["required"]]

            missing = set(required) - set(arg.keys())
            if len(missing) > 0:
                raise AssertionError(
                    "arg `{}` missing required keys {}".format(
                        name, missing))

            for key, val in arg.items():
                recurse(level+1,
                        name+"."+key,
                        values[key]["type"],
                        values[key]["values"],
                        val)

        # unstruct list
        elif subtype == list and values is None:
            arg = check.check_subtype(name, subtype, arg)

        # unstruct dict
        elif subtype == dict and values is None:
            arg = check.check_subtype(name, subtype, arg)

        # selector
        elif isinstance(values, list):
            arg = check.check_subtype(name, subtype, arg)
            check.check_value(name, subtype, values, arg)

        # native
        else:
            arg = check.check_subtype(name, subtype, arg)
            check.check_value(name, subtype, values, arg)


    # check for matching length
    if not len(args) == len(spec["args"]):
        raise TypeError(
            "expected {} positional arguments, got {}".format(
                len(spec["args"]), len(args)))

    for index, subspec in enumerate(spec["args"]):
        arg = args[index]
        recurse(0,
                subspec["name"],
                subspec["type"],
                subspec["values"],
                arg)


    for kw, kwarg in kwargs.items():
        if not kw in spec["kwargs"]:
            raise TypeError(
                "keyword arguments contain unknown key {}".format(
                    kw))

        subspec = spec["kwargs"][kw]
        recurse(0,
                kw,
                subspec["type"],
                subspec["values"],
                kwarg)
