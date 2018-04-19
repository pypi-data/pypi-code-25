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

"""Upgrade a database by applying one or more migrations."""

from __future__ import (
    division, absolute_import, print_function, unicode_literals)

import glob
import logging
import os.path
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys

# We don't depend on bzrlib, but can record branch names
# with schema upgrades if it is available.
try:
    import bzrlib.branch
    import bzrlib.errors
except ImportError:
    pass

__all__ = [
    'CannotApply',
    'PATCH_CONCURRENT',
    'PATCH_DIRECT',
    'PATCH_STANDARD',
    'upgrade',
    ]

if sys.version_info[0] > 2:
    text_type = str
else:
    text_type = basestring
# Reserved DB version for migration schema and tweaks.
SCHEMA_MAJOR = 0
# The table that DB schema patch information is written to
SCHEMA_TABLE = 'lazrdatabaserevision'
# Different sorts of patches
PATCH_STANDARD = "std"
PATCH_DIRECT = "direct"
PATCH_CONCURRENT = "concurrent"
# Built in patches
META_PATCHES = {
    (SCHEMA_MAJOR, 0, 0): """\
CREATE TABLE %(schema_table)s (
    major integer NOT NULL,
    minor integer NOT NULL,
    patch integer NOT NULL,
    start_time timestamp without time zone DEFAULT
        (transaction_timestamp() AT TIME ZONE 'UTC'),
    end_time timestamp without time zone DEFAULT
        (statement_timestamp() AT TIME ZONE 'UTC'),
    branch_nick text,
    revno integer,
    revid text,
    CONSTRAINT %(schema_table)s_pkey PRIMARY KEY (major, minor, patch)
    );

COMMENT ON TABLE %(schema_table)s IS 'This table contains a list of the database patches that have been successfully applied to this database.';
COMMENT ON COLUMN %(schema_table)s.major IS 'Major number. This is the version of the baseline schema the patch was made agains.';
COMMENT ON COLUMN %(schema_table)s.minor IS 'Minor number. Patches made during development each increment the minor number.';
COMMENT ON COLUMN %(schema_table)s.patch IS 'The patch number will hopefully always be ''0'', as it exists to support emergency patches made to the production server. eg. If production is running ''4.0.0'' and needs to have a patch applied ASAP, we would create a ''4.0.1'' patch and roll it out. We then may need to refactor all the existing ''4.x.0'' patches.';
    """ % {'schema_table': SCHEMA_TABLE},
    }

def upgrade(connect, schema_dir, dry_run=False, patch_types=None,
            apply_all=False, one_only=False, schema="public"):
    """Main programmatic entrypoint to the migration facility.

    :param connect: A callable which returns a postgresql DB connection.
    :param schema_dir: A directory containing DB patches.
    :param dry_run: If True perform the changes in a transaction and roll it
        back afterwards. When True patch_types has PATCH_CONCURRENT removed
        from it if it was supplied, and is set to [PATCH_STANDARD,
        PATCH_DIRECT] if patch_types was not supplied.
    :param patch_type: Patch types to apply: None to apply all types, or an
        iterable yielding any of PATCH_STANDARD, PATCH_DIRECT,
        PATCH_CONCURRENT.
    :param apply_all: By default main() will apply all patches of one type and
        then exit. If apply_all is True, then main() will loop applying
        adjacent patches of one type, then another and so on until all pending
        patches have been applied. This is not the default because of the
        potential interruption to service on a busy site: each group of 'std'
        or 'direct' patches will cause at least some exclusive locks to be
        taken and thus stall all clients until the lock is obtained, and the DB
        migration applied.  apply_all is very useful for developer and test
        environments where this behaviour is not a concern.
    :param one_only: Apply just one patch. This takes precedence over apply_all
        and causes upgrade to exit as soon as a single patch is applied.
    """
    con = connect()
    try:
        log = logging.getLogger("lazr.postgresql.upgrade")
        finished = False
        if dry_run:
            patch_types = set(patch_types or [PATCH_STANDARD, PATCH_DIRECT])
            patch_types.discard(PATCH_CONCURRENT)
        while not finished:
            if dry_run:
                log.info("Applying patches in dry-run mode.")
                patches = apply_patches_normal(
                    con, schema_dir, patch_types, one_only, schema)
            else:
                log.info("Applying patches.")
                patches = apply_patches_normal(
                    con, schema_dir, patch_types, one_only, schema)
                con.commit()
            report_patch_times(con, patches)
            if one_only or not apply_all or not patches:
                finished = True
                log.info("Finished applying all requested patches.")
        return 0
    finally:
        con.close()


class CannotApply(Exception):
    """Cannot apply some patch."""


def _table_exists(con, tablename, schema):
    """Return True if tablename exists."""
    cur = con.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT TRUE FROM information_schema.tables
            WHERE
                table_schema=%s
                AND table_name=%s)
            """,
        [schema, tablename]
    )
    return cur.fetchone()[0]


def get_patch(patch):
    """Get the SQL to apply a single patch directly or via slonik."""
    log = logging.getLogger("lazr.postgresql.upgrade")
    (major, minor, point), filename, type = patch
    if filename is None:
        patch_content = META_PATCHES[(major, minor, point)]
    else:
        with open(filename, 'r') as patch_file:
            patch_content = patch_file.read()
    # Perform sanity checks here (e.g. pass through a SQL parser).
    # -- check that concatenation of patches will be ok.
    if not patch_content.rstrip().endswith(';'):
        # This is important because patches are concatenated together
        # into a single script when we apply them to a replicated
        # environment.
        errmsg = ("Last non-whitespace character of %s must be a semicolon" %
            filename)
        log.fatal(errmsg)
        raise CannotApply(errmsg)
    return patch_content


def record_start(branch_info, patch):
    """Return the SQL to record that a given patch is being applied.

    end_time will be set to NULL (reflecting that the patch has not completed) and start_time to the statement time.

    :param branch_info: A tuple of (branch_nick, revno, revid) to record
        the branch being applied. Values may be None if no branch is present.
    :param patch: A patch tuple.
    """
    def maybe_null(thing):
        if thing is None:
            return "NULL"
        if isinstance(thing, text_type):
            return "'%s'" % thing
        return thing
    branch_nick = maybe_null(branch_info[0])
    revno = maybe_null(branch_info[1])
    revid = maybe_null(branch_info[2])
    major, minor, point = patch[0]
    sql = """INSERT INTO %(schema_table)s
        (major, minor, patch, start_time, end_time, branch_nick, revno, revid)
        VALUES (%(major)s, %(minor)s, %(point)s, statement_timestamp(), NULL,
        %(branch_nick)s, %(revno)s, %(revid)s);""" % dict(
        branch_nick=branch_nick, revno=revno, revid=revid, major=major,
        minor=minor, point=point, schema_table=SCHEMA_TABLE)
    return sql


def record_stop(patch):
    """Record that a patch has completed application."""
    major, minor, point = patch[0]
    sql = """UPDATE %(schema_table)s SET end_time=statement_timestamp() WHERE
        major=%(major)s AND minor=%(minor)s AND patch=%(point)s;""" % dict(
        major=major, minor=minor, point=point, schema_table=SCHEMA_TABLE)
    return sql


def get_branch_info(patches_dir):
    """Conditionally return branch info if bzrlib is available."""
    branch_info = (None, None, None)
    if 'bzrlib' in sys.modules:
        try:
            with bzrlib.initialize(True, StringIO(), StringIO(), StringIO()):
                branch = bzrlib.branch.Branch.open_containing(patches_dir)[0]
        except bzrlib.errors.NotBranchError:
            pass
        else:
            branch_info = (branch.nick,) + branch.last_revision_info()

    return branch_info


def apply_patches_normal(
        con, patches_dir, patch_types=None, one_only=False, schema="public"):
    """Apply patches to a DB in a transaction on one node."""
    log = logging.getLogger("lazr.postgresql.upgrade")
    patches = missing_patches(
        con, patches_dir, patch_types=patch_types, one_only=one_only,
        schema=schema)
    if not patches:
        return patches

    branch_info = get_branch_info(patches_dir)
    queries = []
    for patch in patches:
        # Cannot do schema management on schema management patches until they
        # are applied.
        if patch[0][0] != SCHEMA_MAJOR:
            queries.append(record_start(branch_info, patch))
        queries.append(get_patch(patch))
        # Cannot do schema management on schema management patches.
        if patch[0][0] == SCHEMA_MAJOR:
            queries.append(record_start(branch_info, patch))
        queries.append(record_stop(patch))
    log.info("Executing SQL for %d patches.", len(patches))
    cur = con.cursor()
    log.debug("Executing SQL: %r", queries)
    cur.execute(''.join(queries))
    return patches


def missing_patches(
        con, patchdir, patch_types=None, one_only=False, schema="public"):
    """Calculate the patches that need to be applied for the DB in con.

    :param con: A psycopg2 connection.
    :param patchdir: The directory to find patches in.
    :param patch_type: Patch types to apply: None to apply all types, or an
        iterable yielding any of PATCH_STANDARD, PATCH_DIRECT,
        PATCH_CONCURRENT.
    :param one_only: Return at most one patch.
    """
    found_patches = []
    if not _table_exists(con, SCHEMA_TABLE, schema):
        found_patches.append(((SCHEMA_MAJOR, 0, 0), None, PATCH_STANDARD))
        existing_patches = set()
    else:
        cur = con.cursor()
        cur.execute("SELECT major, minor, patch FROM %(schema_table)s" % dict(
            schema_table=SCHEMA_TABLE))
        existing_patches = set([tuple(row) for row in cur.fetchall()])
    all_patch_names = sorted(glob.glob(
        os.path.join(patchdir, 'patch-*-*-*-*.sql')))
    for patch_name in all_patch_names:
        m = re.search('patch-(\d+)-(\d+)-(\d+)-(std|direct|concurrent).sql$',
            patch_name)
        major, minor, patch = [int(i) for i in m.groups()[:3]]
        patch_type = m.groups()[3]
        patch_info = (major, minor, patch)
        if patch_info not in existing_patches:
            found_patches.append((patch_info, patch_name, patch_type))
    # Ensure they're sorted element-wise, not as raw filenames.
    found_patches.sort()
    # Now post-process to only return one type of patch.
    group_type = None
    patches = []
    for patch in found_patches:
        if group_type is None:
            group_type = patch[-1]
            if patch_types is not None:
                if group_type not in patch_types:
                    raise CannotApply(
                        "First patch has a type not listed in patch_types %r"
                        % (patch,))
        if patch[-1] != group_type:
            return patches
        patches.append(patch)
        if one_only:
            return patches
    return patches


def _to_seconds(td):
    """Convert a timedelta to seconds."""
    return td.days * (24 * 60 * 60) + td.seconds + td.microseconds / 1000000.0


def report_patch_times(con, patches):
    """Repoty how long patches took to run."""
    if not patches:
        return
    log = logging.getLogger("lazr.postgresql.upgrade")
    cur = con.cursor()
    sql_patches = "(%s)" % ",".join("(%s, %s, %s)" % patch[0]
        for patch in patches)
    cur.execute("""
        SELECT
            major, minor, patch, start_time, end_time - start_time as db_time,
            branch_nick, revno
        FROM %(schema_table)s
        WHERE (major, minor, patch) IN %(patches)s
        ORDER BY major, minor, patch
        """ % dict(schema_table=SCHEMA_TABLE, patches=sql_patches))
    for patch in cur.fetchall():
        major, minor, patch, start_time, db_time, branch_nick, revno = patch
        db_time = _to_seconds(db_time)
        start_time = start_time.strftime('%Y-%m-%d')
        if branch_nick is None:
            branch_info = "No branch info."
        else:
            branch_info = "%s(%s)" % (branch_nick, revno)
        log.info(
            "%s %d-%02d-%d applied %s in %0.1f seconds"
            % (branch_info, major, minor, patch, start_time, db_time))
