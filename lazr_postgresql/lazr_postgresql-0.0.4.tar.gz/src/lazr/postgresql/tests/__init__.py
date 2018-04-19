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

"""Tests for lazr.postgresql."""

from __future__ import (
    division, absolute_import, print_function, unicode_literals)

import doctest
import os

from van.pg import DatabaseManager
import testresources
import testtools


# A 'just-works' workaround for Ubuntu not exposing initdb to the main PATH.
os.environ['PATH'] = os.environ['PATH'] + ':/usr/lib/postgresql/9.3/bin'


db_resource = DatabaseManager()


class ResourcedTestCase(testtools.TestCase):
    """A modified testresources.ResourcedTestCase that doesn't use tearDown.

    tearDown is called before any cleanups, so destroying things like
    databases in tearDown makes addCleanup difficult to use correctly.

    So, unlike testresources' ResourcedTestCase, this eschews tearDown
    in favour of addCleanup.

    :ivar resources: A list of (name, resource) pairs, where 'resource' is a
        subclass of `TestResourceManager` and 'name' is the name of the
        attribute that the resource should be stored on.
    """

    resources = []

    def setUp(self):
        super(ResourcedTestCase, self).setUp()
        self.setUpResources()
        self.addCleanup(self.tearDownResources)

    def setUpResources(self):
        testresources.setUpResources(
            self, self.resources, testresources._get_result())

    def tearDownResources(self):
        testresources.tearDownResources(
            self, self.resources, testresources._get_result())


def test_suite():
    test_mod_names = [
        'migrate',
        'upgrade',
        ]
    loader = testresources.TestLoader()
    suite = loader.loadTestsFromNames(
        ['lazr.postgresql.tests.test_' + name for name in test_mod_names])

    import lazr.postgresql.connectionstring
    suite.addTest(doctest.DocTestSuite(lazr.postgresql.connectionstring))

    import lazr.postgresql.quoting
    suite.addTest(doctest.DocTestSuite(lazr.postgresql.quoting))

    return suite
