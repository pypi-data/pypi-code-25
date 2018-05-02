"""Python Span Library

Written by Gorea (https://github.com/Gorea235).
"""
__author__ = "Gorea (https://github.com/Gorea235)"
__all__ = ["Span", "ReadOnlySpan"]

import math


class __SpanIter__:
    def __init__(self, span):
        self.__span = span
        self.__i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.__i < len(self.__span):
            item = self.__span[self.__i]
            self.__i += 1
            return item
        else:
            raise StopIteration()

    next = __next__  # Python 2 support


class ReadOnlySpan:
    """Provides access over a list via reference rather than re-allocation.
    This object will act like a standard list that has been spliced (meaning functions
    like 'len' will work correctly), however it will not cause any re-allocations beyond
    the Span object itself (the list doesn't actually change, just the referencing of
    it does).

    Read-only version. This means that this object does not provide an index setter, making
    it safe for situations where modification should not be, or it not, allowed (e.g. strings).

    Params:
        over: the list-like object to span over (can be another Span object).
        start: the starting point of the span (if None, defaults to 0) (inclusive).
        end: the ending point of the span (if None, defaults to the end of over) (exclusive).
        step: the step to span over the items with (if None, defaults to 1).
            Used to create spans over list-like objects that index in different ways
            (still no reallocation, just index adjustment). Negative steps can be used to
            create spans that go in reverse.
    """

    def __init__(self, over, start=None, end=None, step=None):
        offset = 0  # the offset of the start
        prev_end = None
        self._over = over
        if isinstance(over, ReadOnlySpan):
            # if we are spanning of a Span, get the reference directly and just
            # adjust the start & end points
            self._over = over._over
            offset = over._indices[0]
            prev_end = over._indices[1]
        over_ln = len(self._over)
        start = (0 if start is None else start) + offset
        if prev_end is not None and end is None:
            # if we are re-spanning a span without changing the end,
            # just use that
            end = prev_end
        else:
            end = over_ln if end is None else end + offset
        step = 1 if step is None else step
        # use slice to simplify start/end point calculation
        current_slice = slice(start, end, step)
        if step < 0:
            over_ln += 1  # fix to get upper bound index to match
        self._indices = current_slice.indices(
            over_ln)  # stores the start & end points

    def _key_to_actual(self, key):
        lself = len(self)
        # forces the key to be within the span limits
        if key >= lself:
            raise IndexError("span index out of range")
        if key < 0:  # apply wrap-around with negative indexes
            key %= lself
        if self._indices[2] < 0:  # if reverse span, get reverse index
            key = (lself - 1) - key
        key *= abs(self._indices[2])  # scale key last to get actual index
        return self._indices[0] + key

    def __getitem__(self, key):
        return self._over[self._key_to_actual(key)]

    def __cmp__(self, other, op=None):
        # 1 : greater than
        # 0 : equal
        # -1: less than
        try:
            lself = len(self)
            lother = len(other)
            # compare items
            for i in range(min(lself, lother)):
                if self[i] < other[i]:
                    return -1
                elif self[i] > other[i]:
                    return 1
            # compare length if all items are equal to the end of the
            # smallest list-like object
            if lself < lother:
                return -1
            elif lself > lother:
                return 1
            # equal items and size
            return 0
        except TypeError:
            raise TypeError("{} is not supported against '{}' and '{}'".format(
                "comparison" if op is None else ("'" + op + "'"),
                self.__class__.__name__, other.__class__.__name__))

    def __eq__(self, other):
        try:
            return self.__cmp__(other, "==") == 0
        except TypeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.__cmp__(other, "<") == -1

    def __le__(self, other):
        c = self.__cmp__(other, "<=")
        if c == 0 or c == -1:
            return True
        return False

    def __gt__(self, other):
        return self.__cmp__(other, "<") == 1

    def __ge__(self, other):
        c = self.__cmp__(other, "<=")
        if c == 0 or c == 1:
            return True
        return False

    def __len__(self):
        ln = int(math.ceil(
            (self._indices[1] - self._indices[0]) / float(abs(self._indices[2]))))
        if ln < 0:
            return 0
        return ln

    def __iter__(self):
        return __SpanIter__(self)

    def __reversed__(self):
        # returns the iterator of a reversed version of the current span
        # object (this means that the iterator is actuall going over a
        # different object, however this should be a non-issue since the
        # same list-like object is still being referenced)
        return iter(Span(self, step=-self._indices[2]))

    def __contains__(self, item):
        # since we do not know what the underlying data structure is
        # we need to search through the whole list
        for i in self:
            if i == item:
                return True
        return False

    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self) + ")"

    def __str__(self):
        # written as to not reallocate any part of the list
        sb = "["
        ln = len(self)
        for i in range(ln):
            sb += str(self[i])
            if i < ln - 1:
                sb += ", "
        return sb + "]"


class Span(ReadOnlySpan):
    """Provides access over a list via reference rather than re-allocation.
    This object will act like a standard list that has been spliced (meaning functions
    like 'len' will work correctly), however it will not cause any re-allocations beyond
    the Span object itself (the list doesn't actually change, just the referencing of
    it does).

    This is a the same as ReadOnlySpan, but also provides an index setter, allowing
    modification of the spanned object.
    Do take into account that this is still referencing the stored spanned object, so
    any changes applied to this object will be applied to the underlying object (and
    thus will effect all other code referencing the same object).

    Params:
        over: the list-like object to span over (can be another Span object).
        start: the starting point of the span (if None, defaults to 0) (inclusive).
        end: the ending point of the span (if None, defaults to the end of over) (exclusive).
        step: the step to span over the items with (if None, defaults to 1).
            Used to create spans over list-like objects that index in different ways
            (still no reallocation, just index adjustment). Negative steps can be used to
            create spans that go in reverse.
    """

    def __setitem__(self, key, value):
        self._over[self._key_to_actual(key)] = value
