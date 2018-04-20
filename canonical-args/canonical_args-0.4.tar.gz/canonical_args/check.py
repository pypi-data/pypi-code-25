"""

"""
from __future__ import absolute_import

import types




def dynamic_import(class_string):
    """
    perform a python import, attempting first the new-style
    (aka ``getattr(module, "submodule")``), and falling back
    to old style (aka ``exec "from {} import {}".format(...)``)

    :param str class_string: a python import string pointing to
        the class. eg. ``package.module.submodule.AClass``
    :returns: ``types.ClassType``, the imported class.

    .. note :: this method can also work for packages and modules,
        not only classes.
    """
    package_name = class_string.split(".")[0]
    module_import = ".".join(p for p in class_string.split(".")[:-1])
    cla = class_string.split(".")[-1]

    try:
        mod = __import__(package_name)
        for comp in class_string.split(".")[1:]:
            mod = getattr(mod, comp)
        return mod
    except AttributeError, e:
        # cannot import using new fashion, try old
        exec "from {} import {}".format(module_import, cla)
        return eval(class_string)

def type_to_string(subtype):
    """
    convert a subtype (aka, ``types.*`` to a string)

        >>> type_to_string(type(10))
        'int'
        >>> type_to_string(package.module.SomeObject())
        'package.module.SomeObject'

    """
    subtype = str(subtype).replace("<type '", "").replace("'>", "")
    subtype = subtype.replace("<class '", "").replace("'>", "")
    return subtype

"""
special types used during eval
"""
class ChoiceOfOne(list):
    def __repr__(self):
        """
        evaluate to simply ``"one"`` for value lookup
        """
        x = super(ChoiceOfOne, self).__repr__()
        x = "<type 'one'>"
        return x

class StructuredListType(type):
    def __instancecheck__(self, instance):
        return type(instance) in [self, list]

class StructuredList(list):
    __metaclass__ = StructuredListType

    def __repr__(self):
        """
        evaluate to ``"structlist"`` for value lookup
        """
        x = super(StructuredList, self).__repr__()
        x = "<type 'structlist'>"
        return x

# eval type "one"
def one(subtype):
    assert isinstance(subtype, list)
    return ChoiceOfOne(eval_subtype(subtype))

# the structured list subtype
def structlist(subtype):
    assert isinstance(subtype, list)
    return StructuredList(eval_subtype(subtype))

# eval type "cls"
def cls(subtype):
    assert isinstance(subtype, str) or isinstance(subtype, unicode)
    # subtype = re.findall("\((.*)\)", subtype)[0]
    return dynamic_import(subtype)

# eval type "NoneType"
NoneType = types.NoneType

# eval type "Type"
TypeType = types.TypeType


def eval_subtype(subtype):
    """
    get the subtype from a subtype string.

    :param subtype: the string version of the type
    :type subtype: ``str`` or ``unicode``

    Acceptable values:

    ================  =====================================================
    Format            Use
    ================  =====================================================
    "int"             native types: str, float, int, bool, dict, list, etc.
    "one([])"         choice of one, can nest 'cls' calls here
    "structlist([])"  a structured list ``structlist([int, str, float])``
    "cls('')"         a class import string
    "NoneType"        evaluates to ``type(None)``
    "TypeType"        evaluates to ``<type 'type'>``
    ================  =====================================================
    """
    if isinstance(subtype, str) or isinstance(subtype, unicode):

        try:
            subtype = eval(subtype)
        except NameError:
            # assume this is a class for backwards compat
            subtype = dynamic_import(subtype)
        except SyntaxError:
            raise SyntaxError("unable to evaluate type string '{}'".format(
                subtype))

    elif isinstance(subtype, list):
        for i in range(0, len(subtype)):
            subtype[i] = eval_subtype(subtype[i])

    return subtype

def check_subtype(subname, subtype, subarg, should_cast=False):
    """
    check the type of ``subarg`` against the potential subtypes.

    :params str subname: the name of the arg (for error formatting)
    :params subtype: the type to check against
    :type subtype: ``<type 'type'>`` or ``canonical_args.check.ChoiceOfOne``
    :param subarg: the argument whose type is being checked
    :param bool should_cast: default False, when True, will attempt to
        cast the ``subarg`` to type ``subtype``. can only work for native
        types and ``cls`` with appropriate constructors.
    :returns: ``subarg`` or correct type (possibly altered if ``should_cast``)

    If ``subtype`` is of type ``ChoiceOfOne``, type of ``subarg`` will be
    compared against the list of potentials. Else, will be a straight
    ``isinstance`` check.
    """
    # choice of one
    if isinstance(subtype, ChoiceOfOne):
        try:
            assert type(subarg) in subtype
        except AssertionError:
            err = "expected argument '{}' of types {}. got {}.".format(
                subname, subtype, type(subarg))

            if None in subtype:
                # common error is to specify a type as "None",
                # but it MUST be "NoneType"
                err += "\nFound `None` in subtypes, did you mean `NoneType`?"

            raise AssertionError(err)

    # straight up type check
    else:
        try:
            assert isinstance(subarg, subtype)
        except AssertionError as e:
            if should_cast:
                try:
                    subarg = subtype(subarg)
                except ValueError as e:
                    raise ValueError("unable to cast argument '{}' of"\
                                     "type {} to type {}".format(
                        subname, type(subarg), subtype))
            else:
                raise AssertionError("expected argument '{}' of type {}."\
                                     " got {}".format(
                    subname, subtype, type(subarg)))

    return subarg

def check_value(subname, subtypes, subvalues, subarg):
    """
    Check the ``subarg`` against the ``"values"`` ref.
    """
    if isinstance(subtypes, ChoiceOfOne):
        subtype = type(subarg)
        subtype = type_to_string(subtype)
        subvalues = subvalues[subtype]

    # whitelisting
    if isinstance(subvalues, list):
        check_value_whitelist(subname, subvalues, subarg)

    # number ranging (int and float)
    elif ((isinstance(subvalues, str) or
           isinstance(subvalues, unicode)) and
          subvalues.startswith("range")):
        check_value_range(subname, subvalues, subarg)

    # number gt, lt, gte, lte
    elif ((isinstance(subvalues, str) or
           isinstance(subvalues, unicode)) and
          (subvalues.startswith(">") or
           subvalues.startswith("<") or
           subvalues.startswith("(") or
           subvalues.startswith("!"))):
        check_value_comparison(subname, subvalues, subarg)

def check_value_whitelist(subname, subvalues, subarg):
    """
    Check the ``subarg`` against a ``subvalues``.

    :param str subname: the name of the argument (for error parsing)
    :param list subvalues: a list of allowed values
    :param subarg: the value of the argument
    :raises AssertionError: if ``subarg`` not in ``subvalues``
    """
    try:
        assert subarg in subvalues
    except AssertionError as e:
        raise AssertionError("`{}` is not a permitted value for"\
                             " arg '{}'. expected value from"\
                             " {}".format(subarg, subname, subvalues))

def check_value_range(subname, subvalues, subarg):
    """
    Check the ``subarg`` against a number range.

    :param str subname: the name of the argument (for error parsing)
    :param str subvalues: a string representing the range: ``"range(min, max)"``
        .  Note that the range is inclusive!
    :param subarg: the value of the argument
    :raises AssertionError: if ``subarg`` is not within number range
    """
    # number ranging (int and float)        
    ran = eval(subvalues.replace("range", ""))
    try:
        assert ran[0] <= subarg and subarg <= ran[-1]
    except AssertionError as e:
        raise AssertionError("`{}` is not in range({}, {}) for"\
                             " arg '{}'".format(subarg,
                                                ran[0],
                                                ran[-1],
                                                subname))

def check_value_comparison(subname, subvalues, subarg):
    """
    Check the ``subarg`` against the comparison string in ``subvalues``.

    :param str subname: the name of the argument (for error parsing)
    :param str subvalues: the string containing the comparisons to assert.
        eg. ``"((<10||>10)&&!=5)||(<=0&&!=-3)"``
    :param subarg: the value of the argument
    :raises AssertionError: if the assertion of the ``subvalues`` string fails.
    """
    subvalues = subvalues.replace("||", " or ")
    subvalues = subvalues.replace("&&", " and ")
    subvalues = subvalues.replace("<", "{0}<")
    subvalues = subvalues.replace(">", "{0}>")
    subvalues = subvalues.replace("!=", "{0}!=")
    subvalues = subvalues.format(subarg)

    try:
        assert eval(subvalues)
    except AssertionError as e:
        raise AssertionError("`{}` is not `{}` for arg {}".format(
            subarg, subvalues, subname))

