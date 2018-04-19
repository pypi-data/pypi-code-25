# Copyright (c) 2012, Canonical Ltd. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU General Public License version 3 (see the file LICENSE).

from __future__ import (
    division, absolute_import, print_function, unicode_literals)

__metaclass__ = type

__all__ = ['ConnectionString']

import re


class ConnectionString(object):
    """A libpq connection string.

    Some PostgreSQL tools take libpq connection strings. Other tools
    need the components separated out (such as pg_dump command line
    arguments). This class allows you to switch easily between formats.

    Quoted or escaped values are not supported.

    >>> cs = ConnectionString('user=foo dbname=launchpad_dev')
    >>> print(cs.dbname)
    launchpad_dev
    >>> print(cs.user)
    foo
    >>> print(cs)
    dbname=launchpad_dev user=foo
    """
    CONNECTION_KEYS = [
        'dbname', 'user', 'host', 'port', 'connect_timeout', 'sslmode']

    def __init__(self, conn_str):
        if "'" in conn_str or "\\" in conn_str:
            raise NotImplementedError(
                "quoted or escaped values are not supported")

        if '=' not in conn_str:
            # Just a dbname
            for key in self.CONNECTION_KEYS:
                setattr(self, key, None)
            self.dbname = conn_str.strip()
        else:
            # A 'key=value' connection string.
            # We don't check for required attributes, as these might
            # be added after construction or not actually required
            # at all in some instances.
            for key in self.CONNECTION_KEYS:
                match = re.search(r'%s=([^ ]+)' % key, conn_str)
                if match is None:
                    setattr(self, key, None)
                else:
                    setattr(self, key, match.group(1))

    def __str__(self):
        params = []
        for key in self.CONNECTION_KEYS:
            val = getattr(self, key, None)
            if val is not None:
                params.append('%s=%s' % (key, val))
        return ' '.join(params)

    def __repr__(self):
        return repr(str(self))

    def asPGCommandLineArgs(self):
        """Return a string suitable for the PostgreSQL standard tools
        command line arguments.

        >>> cs = ConnectionString('host=localhost user=slony dbname=test')
        >>> print(cs.asPGCommandLineArgs())
        --host=localhost --username=slony test

        >>> cs = ConnectionString('port=5433 dbname=test')
        >>> print(cs.asPGCommandLineArgs())
        --port=5433 test
        """
        params = []
        if self.host is not None:
            params.append("--host=%s" % self.host)
        if self.port is not None:
            params.append("--port=%s" % self.port)
        if self.user is not None:
            params.append("--username=%s" % self.user)
        if self.dbname is not None:
            params.append(self.dbname)
        return ' '.join(params)

    def asLPCommandLineArgs(self):
        """Deprecated! Return a string suitable for use by the LP tools
        using db_options() to parse the command line.

        >>> cs = ConnectionString('host=localhost user=slony dbname=test')
        >>> print(cs.asLPCommandLineArgs())
        --host=localhost --user=slony --dbname=test
        """
        params = []
        if self.host is not None:
            params.append("--host=%s" % self.host)
        if self.user is not None:
            params.append("--user=%s" % self.user)
        if self.dbname is not None:
            params.append("--dbname=%s" % self.dbname)
        return ' '.join(params)
