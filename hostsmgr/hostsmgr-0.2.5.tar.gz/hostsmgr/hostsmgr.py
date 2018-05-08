# -*- coding: utf-8 -*-

"""Main module."""

import io
import os
import os.path
from .entries import from_string as entry_from_string
from .exceptions import HostsNotFound
from .conditions import Any, All, IPAddress, Host, InlineComment
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
    """Hosts file manager.
    """

    def __init__(self):
        self._entries = []

    def clear(self):
        """Clear all entries
        """

        self._entries.clear()

    def load(self, file):
        """Load hosts from file

        :param file: The opened file object (should open with read text
            mode) or str path to hosts file
        :type file: str or file object, optional
        """

        self.clear()

        hosts_file = file
        if isinstance(file, string_types):
            hosts_file = open(file, 'r')

        # Analyse hosts format
        try:
            for line in hosts_file.readlines():
                # There maybe \r, \n or both at the end of line.
                line = line.rstrip()
                self._entries.append(entry_from_string(line))
        finally:
            if isinstance(file, string_types):
                hosts_file.close()

    def loads(self, astr):
        """Load hosts items from string

        :param astr: Hosts file format string
        :type astr: str
        """

        self.load(io.StringIO(astr))

    def save(self, file):
        """Save hosts to file

        :param file: The opened file object (should open with write text mode)
            or str path to hosts file
        :type file: str or file object, optional
        """

        hosts_file = file
        if isinstance(file, string_types):
            hosts_file = open(file, 'w')

        try:
            hosts_file.writelines(
                [entry.expansion + '\n' for entry in self._entries])
        finally:
            if isinstance(file, string_types):
                hosts_file.close()

    def saves(self):
        """Save to string with hosts file format

        :return: Hosts file formatted string
        :rtype: str
        """

        strio = io.StringIO()
        self.save(strio)
        return strio.getvalue()

    def find(self, conditions, at_most=0):
        """Find entries by provided condition

        :param conditions: The entries must match this conditions
        :type conditions: conditions.Condition
        :param at_most: How much we will stop finding at most, defaults to 0
            means unlimited.
        :type at_most: int, optional
        :return: A list of founded entries
        :rtype: list
        """

        if isinstance(conditions, list):
            conditions = All(*conditions)

        found_entries = []

        for entry in self._entries:
            if not conditions(entry):
                continue

            found_entries.append(entry)
            if (at_most >= 1) and (len(found_entries) >= at_most):
                break

        return found_entries

    def check(self, conditions):
        """Check if there have any entry matched with provided condition

        :param conditions: The condition need to check for
        :type conditions: conditions.Condition
        :return: True if condition matched. Otherwise return False.
        :rtype: bool
        """

        return bool(self.find(conditions, at_most=1))

    def add(self, hosts_entry, force=False):
        """Append the hosts entry to the end of hosts table

        :param hosts_entry: The new hosts entry which want to append the hosts
        :type hosts_entry: HostsEntry
        :param force: True if we want to remove all provied hosts.
        :type force: bool
        :raises ValueError: If there have any host same with one of provided
            hosts and force not equal to True.
        """

        if not hosts_entry.hosts:
            raise ValueError("HostsEntry's hosts must not empty!")

        if force:
            self.remove_hosts(hosts_entry.hosts)
        else:
            matched = self.find(
                IPAddress(hosts_entry.address) &
                Any(*[Host(h) for h in hosts_entry.hosts]))

            if matched:
                matched_hosts = []
                for entry in matched:
                    matched_hosts += entry.hosts

                raise ValueError(
                    'These hosts exists already : %s' % matched_hosts)

        # There nothing same with us, append one
        self._entries.append(hosts_entry)

    def remove(self, entry):
        """Remove an entry that found by find() method

        :param entry: An entry want to remove
        :type entry: hostsmgr.entries.Entry
        """

        self._entries.remove(entry)

    def remove_hosts(self, hosts, at_most=0):
        """Remove hosts from entries

        :param hosts: A list hosts that needs to be removed
        :type hosts: list[str]
        :param at_most: How many hosts should be removed by one shot, 0 means
            infinite, defaults to 0
        :type at_most: int, optional
        """

        matched = self.find(Any(*[Host(h) for h in hosts]),
                            at_most)
        for entry in matched:
            for host in hosts:
                try:
                    entry.hosts.remove(host)
                except ValueError:
                    # Ignore value not found exception
                    pass

            # Remove the whole entry if hosts entry don't have any hosts
            if len(entry.hosts) <= 0:
                self._entries.remove(entry)

        return bool(matched)

    def remove_by_inline_comment(self, ic_cond: InlineComment, at_most=0):
        """Remove entries by it's inline comment

        Innormally, you could use inline comment as tag, so you could easily
        related items by them.

        :param ic_cond: An inline comment condition object with search behavior
        :type ic_cond: InlineComment
        :param at_most: How many hosts should be removed by one shot, 0 means
            infinite, defaults to 0
        :param at_most: int, optional
        """

        matched = self.find(ic_cond, at_most)
        for entry in matched:
            self._entries.remove(entry)

        return bool(matched)
