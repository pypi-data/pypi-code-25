import re
from collections import defaultdict

import typing

from sidekick import Record, field, Union, opt

SYMBOL_RE = re.compile(r'^\w+$')
ListOf = defaultdict(lambda: list)
DictOf = defaultdict(lambda: dict)
this = object


class Symbol(str):
    """
    A string-subtype that represents a valid python symbol.
    """
    __slots__ = ()

    def __new__(cls, data):
        if not isinstance(data, str):
            raise TypeError

        if SYMBOL_RE.match(data) is None or data[0].isdigit():
            raise ValueError('invalid symbol: %r' % data)
        return super().__new__(cls, data)


class Pair(Record):
    lhs = field()
    rhs = field()


class CallArgs(Union):
    Args = opt(tuple)
    KwArgs = opt(ListOf[Pair])
    SeqUnpack = opt(Symbol)
    KwUnpack = opt(Symbol)
    Positional = opt(fargs=this, unpack=ListOf[this])
    Keywords = opt(data=ListOf[this])
    Full = opt(positional=this, keyword=this)


class CheckedType(typing.GenericMeta):
    """
    A metaclass that proceeds with instance check by calling the isinstance()
    class method of its instance classes.
    """

    def __instancecheck__(cls, instance):  # noqa: N805
        try:
            method = cls.isinstance
        except AttributeError:
            return False
        else:
            return method(instance)


def _instancecheck(cls, obj):
    return isinstance(obj, cls.__args__)


def _subclasscheck(cls, subclass):
    return issubclass(subclass, cls.__args__)


# TODO: create a copy of Union that behaves correctly instead of monkey patch
typing._Union.__instancecheck__ = _instancecheck
typing._Union.__subclasscheck__ = _subclasscheck
AnyOf = typing.Union

AtomType = AnyOf[str, int, bool, float, complex, type(None)]
