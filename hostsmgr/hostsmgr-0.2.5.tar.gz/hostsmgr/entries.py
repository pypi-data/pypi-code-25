# -*- coding: utf-8 -*-

import re
import ipaddress
from .exceptions import InvalidFormat
from six import string_types


class Entry(object):

    @property
    def expansion(self):
        raise NotImplementedError()


class RawEntry(Entry):

    def __init__(self, value):
        self._value = value

    @property
    def expansion(self):
        return self._value

    @classmethod
    def from_string(cls, value):
        return cls(value)


class CommentEntry(Entry):

    def __init__(self, value, prefix=''):
        self._prefix = prefix
        self._value = value

    @property
    def expansion(self):
        return self._prefix + '#' + self._value

    @classmethod
    def from_string(cls, value):
        matched = re.match(r'(\s*)#(.*)', value)
        if not matched:
            raise InvalidFormat()

        return cls(matched.group(2), matched.group(1))


class HostsEntry(Entry):

    def __init__(self, address, hosts=[], comment=None):
        self._address = self._to_address(address)
        self._hosts = hosts
        self._comment = comment

    def _to_address(self, value):
        if isinstance(value, string_types):
            return ipaddress.ip_address(value)
        elif isinstance(value, ipaddress._BaseAddress):
            return value

        raise ValueError("'%s' isn't value or ip address!" %
                         value)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = self._to_address(value)

    @property
    def hosts(self):
        return self._hosts

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value

    @property
    def expansion(self):
        parts = [self._address.compressed] + self._hosts
        if self._comment:
            parts.append('#' + self._comment)
        # IP address and first host name will be splitted by '\t'.
        # And the host names will spilt by space ' '.
        return parts[0] + '\t' + ' '.join(parts[1:])

    @classmethod
    def from_string(cls, value):
        matched = re.match(r'([^#]+)#(.*)', value)
        comment = None
        if matched:
            value = matched.group(1)
            comment = matched.group(2)

        # Don't use str's split! It will split on dot '.' (Which valid in host
        # name.
        parts = re.split(r'\s+', value.rstrip())
        if len(parts) < 2:
            raise InvalidFormat()
        try:
            address = ipaddress.ip_address(parts[0])
        except ValueError:
            raise InvalidFormat(
                "First field isn't an IP Address : %s" % value)

        return cls(address, parts[1:], comment)


def from_string(value):
    entry_classes = [CommentEntry, HostsEntry]

    for cls in entry_classes:
        try:
            return cls.from_string(value)
        except InvalidFormat:
            pass

    return RawEntry.from_string(value)
