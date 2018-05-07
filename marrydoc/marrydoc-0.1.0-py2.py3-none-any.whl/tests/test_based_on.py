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
"""Test @based_on(...) decoration."""

from __future__ import absolute_import, division, print_function, unicode_literals

from subprocess import PIPE, Popen, STDOUT
from unittest import TestCase, main

import marrydoc.tests.samples.based_on.no_diff as no_diff
from baseline import Baseline


class TestBasedOn(TestCase):

    """Test @based_on decoration."""

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

        Apply marrydoc @based_on(...) decoration in no_diff.py in various
        combinations. Check that when running marrydoc command line tool
        against that file that it correctly does not update the file.

        no_diff.py covers a number of use cases. A comment in each
        function/method in the file discloses the use case it covers.

        """
        # just summary (not verbose)
        actual = self.marrydoc_cmdline(['samples/based_on/no_diff.py'])
        expect = Baseline("""
            samples/based_on/no_diff.py ... OK

            """)
        self.assertEqual(actual, expect)

    def test_no_interference(self):
        """Test marrydoc @based_on(...) decoration does not interfere.

        Apply marrydoc @based_on(...) decoration in no_diff.py in various
        combinations. Check that the function/method name, docstring,
        and functionality is not interfered with.

        no_diff.py covers a number of use cases. A comment in each
        function/method in the file discloses the use case it covers.

        """
        # function: function_single_line_docstr
        self.assertEqual(
            no_diff.function_single_line_docstr.__doc__,
            Baseline(
                """
                Sample function single line docstring.

                    Additional line.
                    
                """))
        self.assertEqual(no_diff.function_single_line_docstr.__name__,
                         'function_single_line_docstr')
        self.assertEqual(no_diff.function_single_line_docstr(),
                         'function_single_line_docstr')

        # function: function_multi_line_docstr
        self.assertEqual(
            no_diff.function_multi_line_docstr.__doc__,
            Baseline(
                """
                Sample function multi-line docstring.

                    SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
                        Indented line.

                    
                """))
        self.assertEqual(no_diff.function_multi_line_docstr.__name__,
                         'function_multi_line_docstr')
        self.assertEqual(no_diff.function_multi_line_docstr(),
                         'function_multi_line_docstr')

        # class: Sample
        self.assertEqual(
            no_diff.Sample.__doc__,
            Baseline(
                """
                Sample class with methods with docstrings.

                    Additional line for subclass.

                    
                """))
        self.assertEqual(no_diff.Sample.__name__,
                         'Sample')

        # method: Sample.static_method
        self.assertEqual(
            no_diff.Sample.static_method.__doc__,
            Baseline(
                """
                Sample static method single line docstring.

                        Additional line.
                        
                """))
        self.assertEqual(no_diff.Sample.static_method.__name__,
                         'static_method')
        self.assertEqual(no_diff.Sample().static_method(),
                         'static_method')

        # method: Sample.class_method
        self.assertEqual(
            no_diff.Sample.class_method.__doc__,
            Baseline(
                """
                Sample class method single line docstring.

                        Additional line.
                        
                """))
        self.assertEqual(no_diff.Sample.class_method.__name__,
                         'class_method')
        self.assertEqual(no_diff.Sample().class_method(),
                         'class_method')

        # method: Sample.bound_method_name_tweaked
        self.assertEqual(
            no_diff.Sample.bound_method_name_tweaked.__doc__,
            Baseline(
                """
                Sample function multi-line docstring.

                        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
                            Indented line.

                        
                """))
        self.assertEqual(no_diff.Sample.bound_method_name_tweaked.__name__,
                         'bound_method_name_tweaked')
        self.assertEqual(no_diff.Sample().bound_method_name_tweaked(),
                         'bound_method_name_tweaked')

    def test_cmdline_diffs(self):
        """Test marrydoc command line where updates are expected.

        Apply marrydoc @based_on(...) decoration in diffs.py in various
        combinations. Check that when running marrydoc command line tool
        against that file that it correctly produces updates to the file.

        diffs.py covers a number of use cases. A comment in each
        function/method in the file discloses the use case it covers.

        """
        # just summary
        actual = self.marrydoc_cmdline(['samples/based_on/diffs.py'])
        expect = Baseline("""
            samples/based_on/diffs.py ... three way merge needed (use --merge)

            """)
        self.assertEqual(actual, expect)

        # with merge
        actual = self.marrydoc_cmdline(['--test', '--merge', 'samples/based_on/diffs.py'])
        expect = Baseline('''
            ################################################################################
            ######################## samples/based_on/diffs.base.py ########################
            ################################################################################
            --- 
            +++ 
            @@ -28,18 +28,15 @@
             
             @marrydoc.based_on(
                 samples.function_single_line_docstr,
            -    """Sample function single line docstring. [extra]""")
            +    """Sample function single line docstring.""")
             def function_single_line_docstr():
            -    """Sample function single line docstring. [extra]
            -
            -    Additional line.
            -    """
            +    """Sample function single line docstring. [extra]"""
                 return 'function_single_line_docstr'
             
             
             @marrydoc.based_on(
                 samples.function_multi_line_docstr,
            -    """Sample function multi-line docstring. [extra]
            +    """Sample function multi-line docstring.
             
                 Some additional line with additional text.
                     Indented line.
            @@ -48,7 +45,7 @@
             def function_multi_line_docstr():
                 """Sample function multi-line docstring. [extra]
             
            -    SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
            +    Some additional line with additional text.
                     Indented line.
             
                 """
            @@ -57,44 +54,34 @@
             
             @marrydoc.based_on(
                 samples.Sample,
            -    """Sample class with methods with docstrings. [extra]""")
            +    """Sample class with methods with docstrings.""")
             class Sample(samples.Sample):
             
            -    """Sample class with methods with docstrings [extra].
            -
            -    Additional line for subclass.
            -
            -    """
            +    """Sample class with methods with docstrings. [extra]"""
             
                 @marrydoc.based_on(
                     samples.Sample.static_method,
            -        """Sample static method single line docstring. [extra]""")
            +        """Sample static method single line docstring.""")
                 @staticmethod
                 def static_method():
            -        """Sample static method single line docstring. [extra]
            -
            -        Additional line.
            -        """
            +        """Sample static method single line docstring. [extra]"""
                     # use case: @based_on before @staticmethod
                     return 'static_method'
             
                 @classmethod
                 @marrydoc.based_on(
                     samples.Sample,
            -        """Sample class method single line docstring. [extra]""")
            +        """Sample class method single line docstring.""")
                 def class_method(cls):
            -        """Sample class method single line docstring. [extra]
            -
            -        Additional line.
            -        """
            +        """Sample class method single line docstring. [extra]"""
                     # use case: @based_on after @classmethod
                     # use case: class used as docstring source
                     return 'class_method'
             
                 @marrydoc.based_on(
                     samples.function_multi_line_docstr,
            -        """Sample function multi-line docstring. [extra]
            -    
            +        """Sample function multi-line docstring.
            +
                     Some additional line with additional text.
                         Indented line.
             
            @@ -102,7 +89,7 @@
                 def bound_method_name_tweaked(self):
                     """Sample function multi-line docstring. [extra]
             
            -        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
            +        Some additional line with additional text.
                         Indented line.
             
                     """
            @@ -112,7 +99,7 @@
             
             based_on_sample_bound_method = marrydoc.based_on(
                 samples.Sample,
            -    """Sample bound method multi-line docstring. [extra]
            +    """Sample bound method multi-line docstring.
             
                 Some additional line with additional text.
                     Indented line.
            @@ -129,7 +116,7 @@
                 def bound_method(self):
                     """Sample bound method multi-line docstring. [extra]
             
            -        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
            +        Some additional line with additional text.
                         Indented line.
             
                     """
            @@ -145,7 +132,8 @@
                 def bound_method(self):
                     """Sample bound method multi-line docstring. [extra]
             
            -        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
            +        Some additional line with additional text.
            +            Indented line.
             
                     """
                     # use case: indentation level changed
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            ################################################################################
            ######################## samples/based_on/diffs.left.py ########################
            ################################################################################
            --- 
            +++ 
            @@ -30,7 +30,7 @@
                 samples.function_single_line_docstr,
                 """Sample function single line docstring.""")
             def function_single_line_docstr():
            -    """Sample function single line docstring. [extra]"""
            +    """Sample function single line docstring."""
                 return 'function_single_line_docstr'
             
             
            @@ -43,7 +43,7 @@
             
                 """)
             def function_multi_line_docstr():
            -    """Sample function multi-line docstring. [extra]
            +    """Sample function multi-line docstring.
             
                 Some additional line with additional text.
                     Indented line.
            @@ -57,14 +57,14 @@
                 """Sample class with methods with docstrings.""")
             class Sample(samples.Sample):
             
            -    """Sample class with methods with docstrings. [extra]"""
            +    """Sample class with methods with docstrings."""
             
                 @marrydoc.based_on(
                     samples.Sample.static_method,
                     """Sample static method single line docstring.""")
                 @staticmethod
                 def static_method():
            -        """Sample static method single line docstring. [extra]"""
            +        """Sample static method single line docstring."""
                     # use case: @based_on before @staticmethod
                     return 'static_method'
             
            @@ -73,7 +73,7 @@
                     samples.Sample,
                     """Sample class method single line docstring.""")
                 def class_method(cls):
            -        """Sample class method single line docstring. [extra]"""
            +        """Sample class method single line docstring."""
                     # use case: @based_on after @classmethod
                     # use case: class used as docstring source
                     return 'class_method'
            @@ -87,7 +87,7 @@
             
                     """)
                 def bound_method_name_tweaked(self):
            -        """Sample function multi-line docstring. [extra]
            +        """Sample function multi-line docstring.
             
                     Some additional line with additional text.
                         Indented line.
            @@ -114,7 +114,7 @@
             
                 @based_on_sample_bound_method
                 def bound_method(self):
            -        """Sample bound method multi-line docstring. [extra]
            +        """Sample bound method multi-line docstring.
             
                     Some additional line with additional text.
                         Indented line.
            @@ -130,7 +130,7 @@
             
                 @based_on_sample_bound_method
                 def bound_method(self):
            -        """Sample bound method multi-line docstring. [extra]
            +        """Sample bound method multi-line docstring.
             
                     Some additional line with additional text.
                         Indented line.
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            ################################################################################
            ####################### samples/based_on/diffs.right.py ########################
            ################################################################################
            --- 
            +++ 
            @@ -30,7 +30,10 @@
                 samples.function_single_line_docstr,
                 """Sample function single line docstring.""")
             def function_single_line_docstr():
            -    """Sample function single line docstring. [extra]"""
            +    """Sample function single line docstring. [extra]
            +
            +    Additional line.
            +    """
                 return 'function_single_line_docstr'
             
             
            @@ -45,7 +48,7 @@
             def function_multi_line_docstr():
                 """Sample function multi-line docstring. [extra]
             
            -    Some additional line with additional text.
            +    SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
                     Indented line.
             
                 """
            @@ -57,14 +60,21 @@
                 """Sample class with methods with docstrings.""")
             class Sample(samples.Sample):
             
            -    """Sample class with methods with docstrings. [extra]"""
            +    """Sample class with methods with docstrings [extra].
            +
            +    Additional line for subclass.
            +
            +    """
             
                 @marrydoc.based_on(
                     samples.Sample.static_method,
                     """Sample static method single line docstring.""")
                 @staticmethod
                 def static_method():
            -        """Sample static method single line docstring. [extra]"""
            +        """Sample static method single line docstring. [extra]
            +
            +        Additional line.
            +        """
                     # use case: @based_on before @staticmethod
                     return 'static_method'
             
            @@ -73,7 +83,10 @@
                     samples.Sample,
                     """Sample class method single line docstring.""")
                 def class_method(cls):
            -        """Sample class method single line docstring. [extra]"""
            +        """Sample class method single line docstring. [extra]
            +
            +        Additional line.
            +        """
                     # use case: @based_on after @classmethod
                     # use case: class used as docstring source
                     return 'class_method'
            @@ -89,7 +102,7 @@
                 def bound_method_name_tweaked(self):
                     """Sample function multi-line docstring. [extra]
             
            -        Some additional line with additional text.
            +        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
                         Indented line.
             
                     """
            @@ -116,7 +129,7 @@
                 def bound_method(self):
                     """Sample bound method multi-line docstring. [extra]
             
            -        Some additional line with additional text.
            +        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
                         Indented line.
             
                     """
            @@ -132,8 +145,7 @@
                 def bound_method(self):
                     """Sample bound method multi-line docstring. [extra]
             
            -        Some additional line with additional text.
            -            Indented line.
            +        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
             
                     """
                     # use case: indentation level changed
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            samples/based_on/diffs.base.py ... FILE WRITE SUPPRESSED FOR TEST
            samples/based_on/diffs.left.py ... FILE WRITE SUPPRESSED FOR TEST
            samples/based_on/diffs.right.py ... FILE WRITE SUPPRESSED FOR TEST
            kdiff3 --merge --auto /home/dan/marrydoc/marrydoc/tests/samples/based_on/diffs.base.py /home/dan/marrydoc/marrydoc/tests/samples/based_on/diffs.left.py /home/dan/marrydoc/marrydoc/tests/samples/based_on/diffs.right.py --output /home/dan/marrydoc/marrydoc/tests/samples/based_on/diffs.py
            samples/based_on/diffs.py ... UPDATED

            ''')
        self.assertEqual(actual, expect)


if __name__ == '__main__':
    main()
