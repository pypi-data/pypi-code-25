# Copyright (c) 2011-2012, Canonical Ltd
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

"""CLI entrypoint."""

from __future__ import (
    division, absolute_import, print_function, unicode_literals)

from functools import partial
import logging
import optparse
import sys
from textwrap import dedent

import psycopg2

from lazr.postgresql import upgrade

__all__ = [
    'main',
    ]


def main(argv=None):
    """CLI entry point for running migrations."""
    if argv is None:
        argv = sys.argv
    usage = dedent("""\
        %prog [options] db_connect_string schema_dir

        When run this program will apply patchse from schema_dir to the
        database specificed by db_connect_string. Patches are applied in-order.
        Patches of the same type (std / direct / concurrent) are grouped and
        applied together. The default behaviour is to apply the first group of
        patches. This default is conservative and appropriate for high traffic
        Slony-I environments. See --apply-all for a do-what-I-mean option.

        Example usage:
        %prog --dry-run dbname=mydb migrations --patch-type direct \\
            --patch-type concurrent
        This will apply direct (all nodes, in a transaction) and concurrent
        (all nodes, outside of transaction) migrations. Suitable for live use
        as long as the direct migrations won't take out exclusive locks on
        existing tables.

        %prog dbname=mydb migrations --apply-all
        Apply all patches one group at a time.

        %prog "dbname=test user=postgres password=secret" migrations
        Apply the first group of pending patches to the database test,
        connecting as user postgress with password secret.
        """)
    description = "Apply database migrations to Postgresql / Slony-I."
    parser = optparse.OptionParser(
        description=description, usage=usage)
    parser.add_option(
        '--dry-run', help="Force non-replicated mode, apply in a transaction "
        "and rollback afterwards. Will totally skip concurrent patches.",
        action="store_true")
    parser.add_option(
        '--patch-type', type="choice", choices=["std", "direct", "concurrent"],
        help="Specify a specific patch type. Can be used more than once.",
        action="append")
    parser.add_option(
        '-1', help="Apply at most one patch (overrides --apply-all).",
        action="store_true", dest="one_only")
    parser.add_option('--apply-all', help="Apply all patches.",
        action="store_true")
    parser.add_option('--verbose', '-v', help="Show more output",
        action="store_true")
    parser.add_option('--schema', help="Which postgres schema to use",
        default="public")
    options, args = parser.parse_args(argv[1:])
    level = logging.INFO
    if options.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)
    if len(args) != 2:
        parser.error("Unexpected number of arguments. got %r" % (args,))

    def connect():
        conn = psycopg2.connect(args[0])
        conn.cursor().execute('SET search_path TO %s', [options.schema])
        return conn

    return upgrade.upgrade(
        connect, args[1], options.dry_run,
        options.patch_type, options.apply_all, options.one_only,
        options.schema)
