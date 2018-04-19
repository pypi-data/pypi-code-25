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

"""Tests for the upgrade functionality."""

from __future__ import (
    division, absolute_import, print_function, unicode_literals)

__metaclass__ = type

from doctest import ELLIPSIS
import os
import sys
from textwrap import dedent
import unittest

from fixtures import (
    EnvironmentVariable,
    FakeLogger,
    Fixture,
    MonkeyPatch,
    TempDir,
    )
import psycopg2
import testtools
from testtools.matchers._basic import DoesNotContain
from testtools.matchers._higherorder import AnnotatedMismatch
from testtools.matchers import (
    AfterPreprocessing,
    DocTestMatches,
    MatchesException,
    Not,
    Raises,
    StartsWith,
    )

from lazr.postgresql.tests import (
    db_resource,
    ResourcedTestCase,
    )
from lazr.postgresql.upgrade import (
    apply_patches_normal,
    get_branch_info,
    CannotApply,
    missing_patches,
    PATCH_STANDARD,
    PATCH_DIRECT,
    PATCH_CONCURRENT,
    record_start,
    report_patch_times,
    SCHEMA_MAJOR,
    SCHEMA_TABLE,
    upgrade,
    )


# bzrlib doesn't support Python 3.
if sys.version_info[0] == 2:
    from bzrlib.bzrdir import BzrDir
    from bzrlib.tests import TestCaseInTempDir
else:
    class TestCaseInTempDir(testtools.TestCase):
        def setUp(self):
            super(TestCaseInTempDir, self).setUp()
            self.test_dir = self.useFixture(TempDir()).path


class FakedEnvironment(Fixture):
    """Fake out an upgrade environment for testing."""

    def __init__(self, num_patches_results=1):
        self.num_patches_results = num_patches_results

    def setUp(self):
        super(FakedEnvironment, self).setUp()
        self.log = []
        self.logger = self.useFixture(FakeLogger())
        self.patchdir = self.useFixture(TempDir()).path
        module_name = 'lazr.postgresql.upgrade.'
        def patch_function(name, result=None, results=None):
            def f(*params):
                self.log.append((name,) + params)
                if results is None:
                    return result
                else:
                    return results.pop(0)
            self.useFixture(MonkeyPatch(module_name + name, f))
        patches = ['patches'] * self.num_patches_results + [None]
        patch_function('apply_patches_normal', results=patches)
        patch_function('report_patch_times')

    def commit(self):
        self.log.append('commit')

    def connect(self):
        self.log.append('connect')
        return self

    def close(self):
        self.log.append('close')


class TestUpgrade(ResourcedTestCase):

    def test_dry_run_passes_one_only_down(self):
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir, True, one_only=True)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir,
                set([PATCH_STANDARD, PATCH_DIRECT]), True, "public"),
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_dry_run_disables_concurrent_patches(self):
        # concurrent patches cannot be dry-runned as they run outside of
        # transactions.
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir, True)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir,
                set([PATCH_STANDARD, PATCH_DIRECT]), False, "public"),
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_dry_run_all_types(self):
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir, True)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir,
                set([PATCH_STANDARD, PATCH_DIRECT]), False, "public"),
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_dry_run_specific_types(self):
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir, True,
            patch_types=[PATCH_STANDARD, PATCH_CONCURRENT])
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir, set([PATCH_STANDARD]),
                False, "public"),
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_passes_one_only_down(self):
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir, one_only=True)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir, None, True, "public"),
            'commit',
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_actual_all_types(self):
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir, None, False, "public"),
            'commit',
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_actual_specific_types(self):
        env = self.useFixture(FakedEnvironment())
        upgrade(env.connect, env.patchdir, patch_types=[PATCH_STANDARD])
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir, [PATCH_STANDARD],
                False, "public"),
            'commit',
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_apply_all_causes_loop_until_patches_empty(self):
        env = self.useFixture(FakedEnvironment(num_patches_results=2))
        upgrade(env.connect, env.patchdir, apply_all=True)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir, None, False, "public"),
            'commit',
            ('report_patch_times', env, 'patches'),
            ('apply_patches_normal', env, env.patchdir, None, False, "public"),
            'commit',
            ('report_patch_times', env, 'patches'),
            ('apply_patches_normal', env, env.patchdir, None, False, "public"),
            'commit',
            ('report_patch_times', env, None),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)

    def test_apply_all_with_one_only(self):
        env = self.useFixture(FakedEnvironment(num_patches_results=2))
        upgrade(env.connect, env.patchdir, apply_all=True, one_only=True)
        expected_calls = [
            'connect',
            ('apply_patches_normal', env, env.patchdir, None, True, "public"),
            'commit',
            ('report_patch_times', env, 'patches'),
            'close',
            ]
        self.assertEqual(expected_calls, env.log)


class HasDBPatch:
    """Match if a connection has a DB patch validly recorded in it.

    This is on the connection not the database to be able to see in-transaction
    schemas.

    A valid patch recording has start and end time set.
    """

    def __init__(self, major, minor, point, nick=None, revno=None, revid=None):
        self.major = major
        self.minor = minor
        self.point = point
        self.nick = nick
        self.revno = revno
        self.revid = revid

    def __str__(self):
        return "HasDBPatch(%s, %s, %s)" % (self.major, self.minor, self.point)

    def match(self, connection):
        cur = connection.cursor()
        cur.execute("""SELECT start_time, end_time, branch_nick, revno, revid
            FROM %(schema_table)s WHERE
            major=%(major)s AND minor=%(minor)s AND patch=%(point)s;""" % dict(
            major=self.major, minor=self.minor, point=self.point,
            schema_table=SCHEMA_TABLE))
        patch = cur.fetchone()
        mismatch = DoesNotContain(connection, (self.major, self.minor, self.point))
        if patch is None:
            return mismatch
        if None in patch[:2]:
            return AnnotatedMismatch("Invalid timestamp.", mismatch)
        start_time, end_time, branch_nick, revno, revid = patch
        if start_time > end_time:
            return AnnotatedMismatch("Started after it ended.", mismatch)
        if self.nick and self.nick != branch_nick:
            return AnnotatedMismatch("Wrong nick %s" % branch_nick, mismatch)
        if self.revno and self.revno != revno:
            return AnnotatedMismatch("Wrong revno %s" % revno, mismatch)
        if self.revid and self.revid != revid:
            return AnnotatedMismatch("Wrong nick %s" % revid, mismatch)
        return None


class HasTable:
    """Match if a connection has a table.

    This is on the connection not the database to be able to see in-transaction
    schemas.
    """

    def __init__(self, tablename):
        self.tablename = tablename

    def __str__(self):
        return "HasTable(%s)" % self.tablename

    def match(self, connection):
        cur = connection.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM pg_tables WHERE tablename ILIKE '%s'"
            % self.tablename)
        if cur.fetchone()[0]:
            return None
        return DoesNotContain(connection, self.tablename)


class TestApplyPatchesNormal(ResourcedTestCase):

    resources = [('db', db_resource)]

    def test_apply_initial_makes_schema(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        patches = apply_patches_normal(con, patchdir)
        self.assertEqual([
            ((SCHEMA_MAJOR, 0, 0), None, PATCH_STANDARD),
            ],
            patches)
        self.assertThat(con, HasTable(SCHEMA_TABLE))
        self.assertThat(con, HasDBPatch(SCHEMA_MAJOR, 0, 0))

    def test_apply_initial_does_not_commit(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        patches = apply_patches_normal(con, patchdir)
        con2 = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con2.close)
        self.assertThat(con2, Not(HasTable(SCHEMA_TABLE)))

    def test_apply_no_patches(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        apply_patches_normal(con, patchdir)
        self.assertEqual([], apply_patches_normal(con, patchdir))

    def test_apply_specific_types(self):
        # When specific types are given, that is passed down to
        # missing_patches.
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        calls = []
        def missing_patches(con, patchdir, patch_types, one_only, schema):
            calls.append(patch_types)
            return []
        self.useFixture(MonkeyPatch(
            'lazr.postgresql.upgrade.missing_patches', missing_patches))
        apply_patches_normal(con, patchdir, patch_types=[PATCH_STANDARD])
        self.assertEqual([[PATCH_STANDARD]], calls)

    def test_apply_one_only(self):
        # When one_only is set, that is passed down to missing_patches.
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        calls = []
        def missing_patches(con, patchdir, patch_types, one_only, schema):
            calls.append(one_only)
            return []
        self.useFixture(MonkeyPatch(
            'lazr.postgresql.upgrade.missing_patches', missing_patches))
        apply_patches_normal(con, patchdir, one_only=True)
        self.assertEqual([True], calls)


class TestMissingPatches(ResourcedTestCase):

    resources = [('db', db_resource)]

    def test_missing_patch_files(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        patches = apply_patches_normal(con, patchdir)
        cur = con.cursor()
        cur.execute(record_start((None, None, None), ((1, 2, 3), None)))
        self.assertEqual([], missing_patches(con, patchdir))

    def test_new_std_patches(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        patches = apply_patches_normal(con, patchdir)
        p1name = patchdir + '/patch-1-2-3-std.sql'
        p2name = patchdir + '/patch-2-3-4-std.sql'
        with open(p1name, 'wb'):
            pass
        with open(p2name, 'wb'):
            pass
        expected = [
            ((1, 2, 3), p1name, PATCH_STANDARD),
            ((2, 3, 4), p2name, PATCH_STANDARD),
            ]
        self.assertEqual(expected, missing_patches(con, patchdir))

    def test_new_concurrent_patches(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        patches = apply_patches_normal(con, patchdir)
        p1name = patchdir + '/patch-1-2-3-concurrent.sql'
        p2name = patchdir + '/patch-2-3-4-concurrent.sql'
        with open(p1name, 'wb'):
            pass
        with open(p2name, 'wb'):
            pass
        expected = [
            ((1, 2, 3), p1name, PATCH_CONCURRENT),
            ((2, 3, 4), p2name, PATCH_CONCURRENT),
            ]
        self.assertEqual(expected, missing_patches(con, patchdir))

    def test_new_direct_patches(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        patches = apply_patches_normal(con, patchdir)
        p1name = patchdir + '/patch-1-2-3-direct.sql'
        p2name = patchdir + '/patch-2-3-4-direct.sql'
        with open(p1name, 'wb'):
            pass
        with open(p2name, 'wb'):
            pass
        expected = [
            ((1, 2, 3), p1name, PATCH_DIRECT),
            ((2, 3, 4), p2name, PATCH_DIRECT),
            ]
        self.assertEqual(expected, missing_patches(con, patchdir))

    def test_mixed_patch_types_returns_one_type_only(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        apply_patches_normal(con, patchdir)
        p1name = patchdir + '/patch-1-2-3-direct.sql'
        p2name = patchdir + '/patch-2-3-4-std.sql'
        with open(p1name, 'wb'):
            pass
        with open(p2name, 'wb'):
            pass
        expected = [
            ((1, 2, 3), p1name, PATCH_DIRECT),
            ]
        self.assertEqual(expected, missing_patches(con, patchdir))

    def test_specific_types_raises_if_first_patch_different_type(self):
        # Because applying a specific type of patch is a manual operation, we
        # error if the first type of patch is not listed in patch_types.
        # - automated test environments can just apply all types and let the
        #   iteration handle it
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        self.assertThat(
            lambda: missing_patches(
                con, patchdir, patch_types=[PATCH_CONCURRENT]),
            Raises(MatchesException(
                CannotApply, AfterPreprocessing(lambda x:x.args[0], StartsWith(
                "First patch has a type not listed in patch_types")))))

    def test_sorting(self):
        # Patches are sorted element-wise as ints, not by filename. This
        # allows leading zeroes to be omitted.
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        apply_patches_normal(con, patchdir)
        patches = [
            os.path.join(patchdir, patch)
            for patch in [
                'patch-2-2-2-std.sql',
                'patch-2-2-3-std.sql',
                'patch-2-2-22-std.sql',
                'patch-2-10-0-std.sql',
                'patch-2-11-0-std.sql',
                'patch-10-0-0-std.sql',
                ]
            ]
        for patch in patches:
            with open(patch, 'wb'):
                pass
        expected = [
            ((2, 2, 2), patches[0], PATCH_STANDARD),
            ((2, 2, 3), patches[1], PATCH_STANDARD),
            ((2, 2, 22), patches[2], PATCH_STANDARD),
            ((2, 10, 0), patches[3], PATCH_STANDARD),
            ((2, 11, 0), patches[4], PATCH_STANDARD),
            ((10, 0, 0), patches[5], PATCH_STANDARD),
            ]
        self.assertEqual(expected, missing_patches(con, patchdir))


class TestBranchInfo(ResourcedTestCase, TestCaseInTempDir):

    resources = [('db', db_resource)]

    @unittest.skipIf('bzrlib' not in sys.modules, 'bzr not available')
    def test_grabs_branch_info_when_in_branch(self):
        workdir = self.useFixture(TempDir()).path
        wt = BzrDir.create_standalone_workingtree(workdir)
        wt.branch.nick='foo'
        wt.commit("")
        wt.commit("", rev_id=b'abcdef')
        os.mkdir(workdir + '/patches')
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        self.permit_dir(workdir)
        patches = apply_patches_normal(con, workdir + '/patches')
        self.assertThat(con, HasDBPatch(SCHEMA_MAJOR, 0, 0, 'foo', 2, 'abcdef'))


class TestGetBranchInfo(TestCaseInTempDir):

    @unittest.skipIf('bzrlib' not in sys.modules, 'bzr not available')
    def test_get_branch_info_when_in_branch(self):
        workdir = self.test_dir
        patches_dir = os.path.join(workdir, 'patches')
        os.mkdir(patches_dir)
        wt = BzrDir.create_standalone_workingtree(workdir)
        wt.branch.nick = 'foo'
        wt.commit("")
        wt.commit("", rev_id=b'abcdef')

        branch_info = get_branch_info(patches_dir)

        self.assertEqual(branch_info, ('foo', 2, 'abcdef'))

    @unittest.skipIf('bzrlib' not in sys.modules, 'bzr not available')
    def test_get_branch_info_when_not_in_branch(self):
        workdir = self.useFixture(TempDir()).path
        patches_dir = os.path.join(workdir, 'patches')
        os.mkdir(patches_dir)
        # The call to Branch.open_containing will traverse up
        # the tree until it finds a .bzr or gets to /.
        self.disable_directory_isolation()

        branch_info = get_branch_info(patches_dir)

        self.assertEqual(branch_info, (None, None, None))

    def remove_module(self, module_name):
        original_modules = sys.modules.copy()

        del sys.modules[module_name]

        def restore_modules():
            sys.modules.update(original_modules)

        self.addCleanup(restore_modules)

    def test_get_branch_info_when_bzr_not_available(self):
        workdir = self.test_dir
        patches_dir = os.path.join(workdir, 'patches')
        os.mkdir(patches_dir)

        if 'bzrlib' in sys.modules:
            self.remove_module('bzrlib')

        branch_info = get_branch_info(patches_dir)

        self.assertEqual(branch_info, (None, None, None))


class TestReportPatchTypes(ResourcedTestCase):

    resources = [('db', db_resource)]

    def test_reports_applied_patches(self):
        patchdir = self.useFixture(TempDir()).path
        con = psycopg2.connect(host=self.db.host, database=self.db.database)
        self.addCleanup(con.close)
        p1name = patchdir + '/patch-1-2-3-std.sql'
        p2name = patchdir + '/patch-2-3-4-std.sql'
        with open(p1name, 'wb') as f:
            f.write(b";")
        with open(p2name, 'wb') as f:
            f.write(b";")
        patches = apply_patches_normal(con, patchdir)
        self.assertEqual(3, len(patches))
        del patches[0]
        expected = dedent("""\
            No branch info. 1-02-3 applied ... in ... seconds
            No branch info. 2-03-4 applied ... in ... seconds
            """)
        logger = self.useFixture(FakeLogger())
        report_patch_times(con, patches)
        self.assertThat(logger.output, DocTestMatches(expected, ELLIPSIS))
