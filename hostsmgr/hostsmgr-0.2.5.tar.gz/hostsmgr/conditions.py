
"""A series conditions that use for search from a hosts table
"""

import ipaddress
from .entries import HostsEntry, CommentEntry, RawEntry


class Condition(object):

    def __init__(self):
        pass

    def __call__(self, entry):
        raise NotImplementedError()

    def __and__(self, other):
        return _And(self, other)

    def __or__(self, other):
        return _Or(self, other)

    def __not__(self):
        return _Not(self)

    def __bool__(self):
        raise NotImplementedError(
            "Unsupported logical operators just like 'and', 'or' or 'not'!"
            " Use '&', '|' or '~' instead!")


class Operator(Condition):
    pass


class Any(Operator):

    def __init__(self, *args):
        super().__init__()

        self._conds = args

    def __call__(self, entry):
        for cond in self._conds:
            if cond(entry):
                return True

        return False


class All(Operator):

    def __init__(self, *args):
        super().__init__()

        self._conds = args

    def __call__(self, entry):
        for cond in self._conds:
            if not cond(entry):
                return False

        return True


class _Not(Operator):

    def __init__(self, cond):
        super().__init__()

        self._cond = cond

    def __call__(self, entry):
        return not self._cond(entry)


class _And(All):
    pass


class _Or(Any):
    pass


class EntryFilter(Condition):

    def __init__(self, entry_class):
        super().__init__()

        self._entry_class = entry_class

    def __call__(self, entry):
        return isinstance(entry, self._entry_class)


class HostsEntryFilter(EntryFilter):

    def __init__(self):
        super().__init__(HostsEntry)


class CommentEntryFilter(EntryFilter):

    def __init__(self):
        super().__init__(CommentEntry)


class RawEntryFilter(EntryFilter):

    def __init__(self):
        super().__init__(RawEntry)


class IPAddress(HostsEntryFilter):

    def __init__(self, address):
        super().__init__()

        self._address = ipaddress.ip_address(address)

    def __call__(self, entry):
        if not super().__call__(entry):
            return False

        return self._address == entry.address


class Host(HostsEntryFilter):

    def __init__(self, host):
        super().__init__()

        self._host = host

    def __call__(self, entry):
        if not super().__call__(entry):
            return False

        return self._host in entry.hosts


class InlineComment(HostsEntryFilter):

    def __init__(self, value, partial=False, case_sensitivity=True):
        super().__init__()

        self._value = value
        self._partial = partial
        self._case_sensitivity = case_sensitivity

    def __call__(self, entry):
        if not super().__call__(entry):
            return False

        if self._case_sensitivity:
            if self._partial:
                return self._value in entry.comment
            else:
                return self._value == entry.comment
        else:
            if self._partial:
                return self._value.lower() in entry.comment.lower()
            else:
                return self._value.lower() == entry.comment.lower()
