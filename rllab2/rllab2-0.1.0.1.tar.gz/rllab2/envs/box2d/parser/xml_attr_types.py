# pylint: disable=no-init, too-few-public-methods, old-style-class

from __future__ import division
from __future__ import absolute_import
import numpy as np
from itertools import imap
from itertools import izip


class Type(object):

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def from_str(self, s):
        raise NotImplementedError


class Float(Type):

    def from_str(self, s):
        return float(s)


class Int(Type):

    def from_str(self, s):
        return int(s)


class Hex(Type):

    def from_str(self, s):
        assert s.startswith(u"0x") or s.startswith(u"0X")
        return int(s, 16)


class Choice(Type):

    def __init__(self, *options):
        self._options = options

    def from_str(self, s):
        if s in self._options:
            return s
        raise ValueError(u"Unexpected value %s: must be one of %s" %
                         (s, u", ".join(self._options)))


class List(Type):

    def __init__(self, elem_type):
        self.elem_type = elem_type

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
            and self.elem_type == other.elem_type

    def from_str(self, s):
        if u";" in s:
            segments = s.split(u";")
        elif u"," in s:
            segments = s.split(u",")
        else:
            segments = s.split(u" ")
        return list(imap(self.elem_type.from_str, segments))


class Tuple(Type):

    def __init__(self, *elem_types):
        self.elem_types = elem_types

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
            and self.elem_types == other.elem_types

    def from_str(self, s):
        if u";" in s:
            segments = s.split(u";")
        elif u"," in s:
            segments = s.split(u",")
        else:
            segments = s.split(u" ")
        if len(segments) != len(self.elem_types):
            raise ValueError(
                u"Length mismatch: expected a tuple of length %d; got %s instead" %
                (len(self.elem_types), s))
        return tuple([typ.from_str(seg)
                      for typ, seg in izip(self.elem_types, segments)])


class Either(Type):

    def __init__(self, *elem_types):
        self.elem_types = elem_types

    def from_str(self, s):
        for typ in self.elem_types:
            try:
                return typ.from_str(s)
            except ValueError:
                pass
        raise ValueError(u'No match found')


class String(Type):

    def from_str(self, s):
        return s


class Angle(Type):

    def from_str(self, s):
        if s.endswith(u"deg"):
            return float(s[:-len(u"deg")]) * np.pi / 180.0
        elif s.endswith(u"rad"):
            return float(s[:-len(u"rad")])
        return float(s) * np.pi / 180.0


class Bool(Type):

    def from_str(self, s):
        return s.lower() == u"true" or s.lower() == u"1"


Point2D = lambda: Tuple(Float(), Float())
