# Copyright (c) 2011, Canonical Ltd
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

"""Tests for the CLI glue."""

from __future__ import (
    division, absolute_import, print_function, unicode_literals)

__metaclass__ = type

from fixtures import (
    MonkeyPatch,
    )

from lazr.postgresql.tests import ResourcedTestCase
from lazr.postgresql.migrate import main


class TestMain(ResourcedTestCase):

    def test_smoketest(self):
        argv = ['lp-migrate', 'connstring', 'patch-dir']
        calls = []

        class Cursor:
            def execute(self, *args):
                calls.append(args)

        class Conn:
            def cursor(self):
                return Cursor()

        conn = Conn()

        def connect(params):
            calls.append(params)
            return conn

        self.useFixture(MonkeyPatch('psycopg2.connect', connect))

        def upgrade(connect, schema_dir, dry_run=False, patch_types=None,
                    apply_all=False, one_only=False, schema="public"):
            con = connect()
            calls.append((
                con, schema_dir, dry_run, patch_types, apply_all, one_only))
            return 0
        self.useFixture(
            MonkeyPatch('lazr.postgresql.upgrade.upgrade', upgrade))
        self.assertEqual(0, main(argv))
        self.assertEqual([
            'connstring',
            ('SET search_path TO %s', ['public']),
            (conn, 'patch-dir', None, None, None, None),
            ], calls)
