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
"""Test @inherit(...) decoration."""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from unittest import TestCase, main

import marrydoc


def sample_function(a):
    """"Sample function docstring."""
    return 'sample_function(a={})'.format(a)


@marrydoc.inherit(sample_function)
def sample_function_copy(a):
    # function docstring intentionally omitted (it's provided by @inherit)
    return 'sample_function_copy(a={})'.format(a)


class SampleClass(object):

    """Sample class to use as basis to inherit doc strings from"""

    def sample_boundmethod(self, a):
        """Sample method docstring."""
        return 'SampleClass.sample_boundmethod(a={})'.format(a)

    @staticmethod
    def sample_staticmethod(a):
        """Sample static method docstring."""
        return 'SampleClass.sample_staticmethod(a={})'.format(a)

    @classmethod
    def sample_classmethod(cls, a):
        """Sample class method docstring."""
        return 'SampleClass.sample_classmethod(a={})'.format(a)


class SampleSubClass(SampleClass):

    """Class with methods that inherit docstrings.

    Note, this class cannot inherit docstrings because __doc__ is not
    allowed to be reassigned on class objects.

    """

    @marrydoc.inherit(SampleClass)
    def sample_boundmethod(self, a):
        # docstring intentionally omitted (it's provided by inherit decorator)
        # use case: inherit docstring from a method within the specified class
        return 'SampleSubClass.sample_boundmethod(a={})'.format(a)

    @marrydoc.inherit(SampleClass.sample_boundmethod)
    def sample_boundmethod2(self, a):
        # docstring intentionally omitted (it's provided by @inherit)
        # use case: inherit docstring from the specified method
        return 'SampleSubClass.sample_boundmethod2(a={})'.format(a)

    @staticmethod
    @marrydoc.inherit(SampleClass)
    def sample_staticmethod(a):
        # docstring intentionally omitted (it's provided by @inherit)
        # use case: @inherit after @staticmethod decorator
        return 'SampleSubClass.sample_staticmethod(a={})'.format(a)

    @marrydoc.inherit(SampleClass.sample_classmethod)
    @classmethod
    def sample_classmethod(cls, a):
        # docstring intentionally omitted (it's provided by @inherit)
        # use case: @inherit before @classmethod decorator
        return 'SampleSubClass.sample_classmethod(a={})'.format(a)


class TestInherit(TestCase):

    """Test @inherit decorator."""

    def test_function(self):
        """Test usage on simple function."""

        self.assertEqual(sample_function.__doc__, sample_function_copy.__doc__)

        # verify decoration does not interfere with function API
        self.assertEqual(sample_function_copy(a=1), 'sample_function_copy(a=1)')

        # verify decoration does not interfere with function name
        self.assertEqual(sample_function_copy.__name__, 'sample_function_copy')

    def test_method_via_specified_class(self):
        """Test method inherits from a method within the specified class."""

        self.assertEqual(SampleSubClass.sample_boundmethod.__doc__,
                         SampleClass.sample_boundmethod.__doc__)

        # verify decoration does not interfere with method API
        self.assertEqual(SampleSubClass().sample_boundmethod(a=1),
                         'SampleSubClass.sample_boundmethod(a=1)')

        # verify decoration does not interfere with method name
        self.assertEqual(SampleSubClass.sample_boundmethod.__name__,
                         'sample_boundmethod')

    def test_method_via_specified_method(self):
        """Test method inherits from the specified method."""

        self.assertEqual(SampleSubClass.sample_boundmethod2.__doc__,
                         SampleClass.sample_boundmethod.__doc__)

        # verify decoration does not interfere with method API
        self.assertEqual(SampleSubClass().sample_boundmethod2(a=1),
                         'SampleSubClass.sample_boundmethod2(a=1)')

        # verify decoration does not interfere with method name
        self.assertEqual(SampleSubClass.sample_boundmethod2.__name__,
                         'sample_boundmethod2')

    def test_staticmethod_with_inherit_after(self):
        """Test usage on static method where @inherit follows @staticmethod."""

        self.assertEqual(SampleSubClass.sample_staticmethod.__doc__,
                         SampleClass.sample_staticmethod.__doc__)

        # verify decoration does not interfere with method API
        self.assertEqual(SampleSubClass.sample_staticmethod(a=1),
                         'SampleSubClass.sample_staticmethod(a=1)')

        # verify decoration does not interfere with method name
        self.assertEqual(SampleSubClass.sample_staticmethod.__name__,
                         'sample_staticmethod')

    def test_classmethod_with_inherit_before(self):
        """Test usage on class method where @inherit before @classmethod."""

        self.assertEqual(SampleSubClass.sample_classmethod.__doc__,
                         SampleClass.sample_classmethod.__doc__)

        # verify decoration does not interfere with method API
        self.assertEqual(SampleSubClass.sample_classmethod(a=1),
                         'SampleSubClass.sample_classmethod(a=1)')

        # verify decoration does not interfere with method name
        self.assertEqual(SampleSubClass.sample_classmethod.__name__,
                         'sample_classmethod')

    def test_function_docstring_conflict(self):
        """Test exception raise when class docstring already present."""

        message = "docstring already present, @inherit blocked"

        if sys.version_info.major <= 2:  # pragma: no cover
            raises_context = self.assertRaisesRegexp(AssertionError, message)
        else:
            raises_context = self.assertRaisesRegex(AssertionError, message)

        with raises_context:
            @marrydoc.inherit(sample_function_copy)
            def some_function():
                """Hello world!"""
                pass


if __name__ == '__main__':
    main()
