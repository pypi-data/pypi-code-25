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
"""Test @copied_from(...) decoration."""

from __future__ import absolute_import, division, print_function, unicode_literals

from subprocess import PIPE, Popen, STDOUT
from unittest import TestCase, main

import marrydoc.tests.samples as samples
import marrydoc.tests.samples.copied_from.no_diff as no_diff
from baseline import Baseline


class TestCopiedFrom(TestCase):

    """Test @copied_from(...) decoration."""

    @staticmethod
    def marrydoc_cmdline(args):
        """Run marrydoc command line tool on sample test file.

        :params list args: command line option and argument strings
        :returns: console output
        :rtype: str

        """
        process = Popen(['marrydoc'] + args, stderr=STDOUT, stdout=PIPE, universal_newlines=True)
        out, err = process.communicate()

        out = '' if out is None else out
        err = '' if err is None else err

        return out + err

    def test_cmdline_no_diffs(self):
        """Test marrydoc command line where no differences expected.

        Apply marrydoc @copied_from(...)  decoration in no_diff.py in various
        combinations. Check that when running marrydoc command line tool
        against that file that it correctly does not update the file.

        no_diff.py covers a number of use cases. A comment in each
        function/method in the file discloses the use case it covers.

        """
        # just summary (not verbose)
        actual = self.marrydoc_cmdline(['samples/copied_from/no_diff.py'])
        expect = Baseline("""
            samples/copied_from/no_diff.py ... OK

            """)
        self.assertEqual(actual, expect)

    def test_no_interference(self):
        """Test marrydoc @copied_from(...) decoration does not interfere.

        Apply marrydoc @copied_from(...)  decoration in no_diff.py in various
        combinations. Check that the function/method name, docstring,
        and functionality is not interfered with.

        no_diff.py covers a number of use cases. A comment in each
        function/method in the file discloses the use case it covers.

        """
        # function: function_single_line_docstr
        self.assertEqual(no_diff.function_single_line_docstr.__doc__,
                         samples.function_single_line_docstr.__doc__)
        self.assertEqual(no_diff.function_single_line_docstr.__name__,
                         'function_single_line_docstr')
        self.assertEqual(no_diff.function_single_line_docstr(),
                         'function_single_line_docstr')

        # function: function_multi_line_docstr
        self.assertEqual(no_diff.function_multi_line_docstr.__doc__,
                         samples.function_multi_line_docstr.__doc__)
        self.assertEqual(no_diff.function_multi_line_docstr.__name__,
                         'function_multi_line_docstr')
        self.assertEqual(no_diff.function_multi_line_docstr(),
                         'function_multi_line_docstr')

        # class: Sample
        self.assertEqual(no_diff.Sample.__doc__,
                         samples.Sample.__doc__)
        self.assertEqual(no_diff.Sample.__name__,
                         'Sample')

        # method: Sample.static_method
        self.assertEqual(no_diff.Sample.static_method.__doc__,
                         samples.Sample.static_method.__doc__)
        self.assertEqual(no_diff.Sample.static_method.__name__,
                         'static_method')
        self.assertEqual(no_diff.Sample().static_method(),
                         'static_method')

        # method: Sample.class_method
        self.assertEqual(no_diff.Sample.class_method.__doc__,
                         samples.Sample.class_method.__doc__)
        self.assertEqual(no_diff.Sample.class_method.__name__,
                         'class_method')
        self.assertEqual(no_diff.Sample().class_method(),
                         'class_method')

        # method: Sample.bound_method_name_tweaked
        self.assertEqual(no_diff.Sample.bound_method_name_tweaked.__doc__,
                         samples.function_multi_line_docstr.__doc__.replace(
                             '\n    ', '\n        '))
        self.assertEqual(no_diff.Sample.bound_method_name_tweaked.__name__,
                         'bound_method_name_tweaked')
        self.assertEqual(no_diff.Sample().bound_method_name_tweaked(),
                         'bound_method_name_tweaked')

    def test_cmdline_simple_diffs(self):
        """Test marrydoc command line where updates are expected.

        Apply marrydoc @copied_from(...) decoration in diffs.py in various
        combinations. Check that when running marrydoc command line tool
        against that file that it correctly produces updates to the file.

        diffs.py covers a number of use cases. A comment in each
        function/method in the file discloses the use case it covers.

        """
        # just summary
        actual = self.marrydoc_cmdline(['samples/copied_from/diffs.py'])
        expect = Baseline("""
            samples/copied_from/diffs.py ... update needed (use --merge)

            """)
        self.assertEqual(actual, expect)

        # with merge
        actual = self.marrydoc_cmdline(['--test', '--merge', 'samples/copied_from/diffs.py'])
        expect = Baseline('''
            ################################################################################
            ######################### samples/copied_from/diffs.py #########################
            ################################################################################
            --- 
            +++ 
            @@ -26,7 +26,7 @@
             
             @marrydoc.copied_from(samples.function_single_line_docstr)
             def function_single_line_docstr():
            -    """Sample function single line docstring. [extra text]"""
            +    """Sample function single line docstring."""
                 # use case: text added to docstring
                 return 'function_single_line_docstr'
             
            @@ -35,7 +35,7 @@
             def function_multi_line_docstr():
                 """Sample function multi-line docstring.
             
            -    Some additional line.
            +    Some additional line with additional text.
                     Indented line.
             
                 """
            @@ -46,13 +46,13 @@
             @marrydoc.copied_from(samples.Sample)
             class Sample(samples.Sample):
             
            -    """Sample class with methods with docstrings. [extra text]"""
            +    """Sample class with methods with docstrings."""
                 # use case: text added to docstring
             
                 @marrydoc.copied_from(samples.Sample.static_method)
                 @staticmethod
                 def static_method():
            -        """"""
            +        """Sample static method single line docstring."""
                     # use case: @copied_from before @staticmethod
                     # use case: initial docstring empty
                     return 'static_method'
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            samples/copied_from/diffs.py ... FILE WRITE SUPPRESSED FOR TEST
            samples/copied_from/diffs.py ... UPDATED

            ''')
        self.assertEqual(actual, expect)


if __name__ == '__main__':
    main()
