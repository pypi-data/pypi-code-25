# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_openbsd.upt_openbsd import OpenBSDPerlPackage


class TestOpenBSDPerlPackage(unittest.TestCase):
    def setUp(self):
        self.obsd_pkg = OpenBSDPerlPackage()
        self.obsd_pkg.upt_pkg = upt.Package('test-pkg', '13.37')
        # Let's pretend the sqlports database is not available.
        self.conn = None

    def test_dependencies(self):
        self.obsd_pkg.upt_pkg.requirements = {
            'run': [
                upt.PackageRequirement('foo', ''),
                upt.PackageRequirement('bar', '>1.2')
            ],
            'test': [
                upt.PackageRequirement('baz', '>=3.4')
            ]
        }

        expected = 'RUN_DEPENDS =\t\txxx/p5-foo \\\n'
        expected += '\t\t\txxx/p5-bar\n'
        expected += 'TEST_DEPENDS =\t\txxx/p5-baz\n'

        self.assertEqual(self.obsd_pkg._dependencies(), expected)

    def test_dependencies_runtime_only(self):
        self.obsd_pkg.upt_pkg.requirements = {
            'run': [
                upt.PackageRequirement('foo', ''),
                upt.PackageRequirement('bar', '>1.2')
            ],
        }

        expected = 'RUN_DEPENDS =\t\txxx/p5-foo \\\n'
        expected += '\t\t\txxx/p5-bar\n'

        self.assertEqual(self.obsd_pkg._dependencies(), expected)

    def test_dependencies_test_only(self):
        self.obsd_pkg.upt_pkg.requirements = {
            'test': [
                upt.PackageRequirement('baz', '>=3.4')
            ]
        }

        expected = 'TEST_DEPENDS =\t\txxx/p5-baz\n'

        self.assertEqual(self.obsd_pkg._dependencies(), expected)


if __name__ == '__main__':
    unittest.main()
