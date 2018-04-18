# -*- coding: utf-8 -*-

"""Main module."""

import io
import os
import sys
import os.path
from .entry import from_string as entry_from_string
from .exceptions import *
from six import string_types


def guess_hosts_path():
    """Guess hosts path

    :raises HostsNotFound: If failed to find the hosts file
    :return: The hosts file path
    :rtype: str
    """

    # References to https://en.wikipedia.org/wiki/Hosts_(file)
    possible_paths = [
        # Unix, Unix-like, POSIX, Apple Macintosh Mac OS X 10.2 and newer,
        # Android, iOS 2.0 and newer
        '/etc/hosts',
        # Microsoft Windows NT, 2000, XP,[5] 2003, Vista, 2008, 7, 2012, 8, 10
        r'${SystemRoot}\System32\drivers\etc\hosts',
        # Microsoft Windows 95, 98, ME
        r'${WinDir}\hosts',
        # Microsoft Windows 3.1
        r'${WinDir}\HOSTS',
        # Symbian OS 6.1–9.0
        r'C:\system\data\hosts',
        # Symbian OS 9.1+
        r'C:\private\10000882\hosts',
        # Plan 9
        '/lib/ndb/hosts',
        # BeOS
        '/boot/beos/etc/hosts',
        # Haiku
        '/boot/common/settings/network/hosts',
    ]

    for path in possible_paths:
        path = os.path.expandvars(os.path.expanduser(path))
        if os.path.exists(path):
            return path

    # Meet unsupported OS
    raise HostsNotFound()


class HostsMgr(object):

    def __init__(self):
        self._path = None
        self._entries = []

    def clear(self):
        self._entries.clear()

    def load(self, file=None):
        """Load hosts from file

        :param file: The opened file object (should open with read text
        mode) or str path to hosts file, it will guess hosts path in current
        OS if not specificed, defaults to None
        :param file: str or file object, optional
        """

        self.clear()

        if file:
            if isinstance(file, string_types):
                self._path = file
        else:
            self._path = guess_hosts_path()

        if self._path:
            file = open(self._path, 'r')

        # Analyse hosts format
        try:
            for line in file.readlines():
                # There maybe \r, \n or both at the end of line.
                line = line.rstrip()
                self._entries.append(entry_from_string(line))
        finally:
            if self._path:
                file.close()

    def loads(self, astr):
        self.load(io.StringIO(astr))

    def save(self, file=None):
        """Save hosts to file

        :raises HostsNotFound: If file set to None and previous load() without a
        valid path.
        :param file: The opened file object (should open with write text mode)
        or str path to hosts file, it will save to path previous specificed,
        defaults to None
        :param file: str or file object, optional
        """

        if file:
            dst_file = file
        else:
            if not os.path.exists(self._path):
                raise HostsNotFound()

            dst_file = open(self._path, 'w')

        try:
            dst_file.writelines(
                [entry.expansion for entry in self._entries])
        finally:
            if not file:
                dst_file.close()

    def saves(self):
        strio = io.StringIO()
        self.save(strio)
        return strio.getvalue()
