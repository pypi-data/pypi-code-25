# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

from __future__ import with_statement

import time
import unittest
from datetime import datetime, timedelta

from trac.test import EnvironmentStub

from tracspamfilter.filtersystem import FilterSystem
from tracspamfilter.model import LogEntry


def drop_tables(env):
    with env.db_transaction as db:
        for table in ('spamfilter_bayes', 'spamfilter_log',
                      'spamfilter_report', 'spamfilter_statistics'):
            db("DROP TABLE IF EXISTS %s" % table)
        db("DELETE FROM system WHERE name='spamfilter_version'")


class LogEntryTestCase(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub()
        with self.env.db_transaction as db:
            FilterSystem(self.env).upgrade_environment(db)

    def tearDown(self):
        drop_tables(self.env)
        self.env.reset_db()

    def test_purge(self):
        now = datetime.now()
        oneweekago = time.mktime((now - timedelta(weeks=1)).timetuple())
        onedayago = time.mktime((now - timedelta(days=1)).timetuple())
        req = None

        LogEntry(self.env, oneweekago, '/foo', 'john', False, '127.0.0.1',
                 '', 'Test', False, 5, [], req).insert()
        LogEntry(self.env, onedayago, '/foo', 'anonymous', False, '127.0.0.1',
                 '', 'Test', True, -3, [], req).insert()

        LogEntry.purge(self.env, days=4)

        log = list(LogEntry.select(self.env))
        self.assertEqual(1, len(log))
        entry = log[0]
        self.assertEqual('anonymous', entry.author)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LogEntryTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
