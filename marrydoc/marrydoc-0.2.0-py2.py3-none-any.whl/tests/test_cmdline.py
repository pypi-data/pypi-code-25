# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2018 Daniel Mark Gass
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Test command line main( ) function."""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
try:
    # Python 2
    from StringIO import StringIO
except ImportError:
    # Python > 3
    from io import StringIO
from unittest import TestCase, main as unittest_main

from baseline import Baseline
from marrydoc import main

from contextlib import contextmanager

class CommandLine(TestCase):

    """Test command line interface.

    Vary:
        - paths specified (files vs. paths)
        - usage of --walk
        - same files
            - no updates required
            - simple update required
            - three way merge required

    """

    @contextmanager
    def _evaluate_stdout(self, expected_output):
        sys.stdout, orig_stdout = StringIO(), sys.stdout
        yield
        sys.stdout, trap = orig_stdout, sys.stdout

        self.assertEqual(trap.getvalue(), expected_output)

    def test_single_file_no_diff(self):
        """Evaluate just one file that has no updates required."""
        expected_output = Baseline(
            """
            samples/based_on/no_diff.py ... OK

            """)

        with self._evaluate_stdout(expected_output):
            self.assertEqual(main(['samples/based_on/no_diff.py']), 0)

    def test_single_file_with_diff(self):
        """Evaluate just one file that requires an update."""
        expected_output = Baseline(
            """
            samples/based_on/diffs.py ... three way merge needed (use --merge)

            """)

        with self._evaluate_stdout(expected_output):
            self.assertEqual(main(['samples/based_on/diffs.py']), 99)

    def test_single_directory_with_diff(self):
        """Evaluate just one directory that has files with a mix of needs."""
        expected_output = Baseline(
            """
            samples/based_on/__init__.py ... OK
            samples/based_on/diffs.py ... three way merge needed (use --merge)
            samples/based_on/no_diff.py ... OK

            """)

        with self._evaluate_stdout(expected_output):
            self.assertEqual(main(['samples/based_on']), 99)

    def test_directory_walk(self):
        """Evaluate a directory system that has files with a mix of needs."""
        expected_output = Baseline(
            """
            samples/__init__.py ... OK
            samples/based_on/__init__.py ... OK
            samples/based_on/diffs.py ... three way merge needed (use --merge)
            samples/based_on/no_diff.py ... OK
            samples/copied_from/__init__.py ... OK
            samples/copied_from/diffs.py ... update needed (use --merge)
            samples/copied_from/no_diff.py ... OK

            """)

        with self._evaluate_stdout(expected_output):
            self.assertEqual(main(['--walk', 'samples']), 99)


if __name__ == '__main__':
    unittest_main()
