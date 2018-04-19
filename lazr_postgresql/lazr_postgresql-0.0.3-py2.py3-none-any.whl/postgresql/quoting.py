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

__all__ = ['fqn', 'quote_identifier']

import re


def quote_identifier(identifier):
    r'''Quote an identifier, such as a table or role name.

    In SQL, identifiers are quoted using " rather than ' (which is reserved
    for strings).

    >>> print(quote_identifier('hello'))
    "hello"

    Quotes and Unicode are handled if you make use of them in your
    identifiers.

    >>> print(quote_identifier("'"))
    "'"
    >>> print(quote_identifier('"'))
    """"
    >>> print(quote_identifier("\\"))
    "\"
    >>> print(quote_identifier('\\"'))
    "\"""
    >>> print(quote_identifier('\\ aargh \u0441\u043b\u043e\u043d'))
    U&"\\ aargh \0441\043b\043e\043d"
    '''
    try:
        identifier_bytes = identifier.encode('ascii')
        return '"%s"' % identifier_bytes.replace(b'"', b'""').decode('ascii')
    except UnicodeEncodeError:
        escaped = []
        for c in identifier:
            if c == '\\':
                escaped.append(b'\\\\')
            elif c == '"':
                escaped.append(b'""')
            else:
                c = c.encode('ascii', 'backslashreplace')
                # Note Python only supports 32 bit unicode, so we use
                # the 4 hexdigit PostgreSQL syntax (\1234) rather than
                # the 6 hexdigit format (\+123456).
                if c.startswith(b'\\u'):
                    c = b'\\' + c[2:]
                escaped.append(c)
        return 'U&"%s"' % b''.join(escaped).decode('ascii')


def fqn(namespace, name):
    """Return the fully qualified name by combining the namespace and name.

    Quoting is done for the non trivial cases.

    >>> print(fqn('public', 'foo'))
    public.foo
    >>> print(fqn(' foo ', '$bar'))
    " foo "."$bar"
    """
    if re.search(r"[^a-z_]", namespace) is not None:
        namespace = quote_identifier(namespace)
    if re.search(r"[^a-z_]", name) is not None:
        name = quote_identifier(name)
    return "%s.%s" % (namespace, name)
