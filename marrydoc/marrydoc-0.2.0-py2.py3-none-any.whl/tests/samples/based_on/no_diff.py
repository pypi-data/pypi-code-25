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

from __future__ import absolute_import, division, print_function, unicode_literals

import marrydoc
import marrydoc.tests.samples as samples


@marrydoc.based_on(
    samples.function_single_line_docstr,
    """Sample function single line docstring.""")
def function_single_line_docstr():
    """Sample function single line docstring.

    Additional line.
    """
    return 'function_single_line_docstr'


@marrydoc.based_on(
    samples.function_multi_line_docstr,
    """Sample function multi-line docstring.

   Some additional line with additional text.
       Indented line.

   """)
def function_multi_line_docstr():
    """Sample function multi-line docstring.

    SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
        Indented line.

    """
    return 'function_multi_line_docstr'


@marrydoc.based_on(
    samples.Sample,
    """Sample class with methods with docstrings.""")
class Sample(samples.Sample):

    """Sample class with methods with docstrings.

    Additional line for subclass.

    """

    @marrydoc.based_on(
        samples.Sample.static_method,
        """Sample static method single line docstring.""")
    @staticmethod
    def static_method():
        """Sample static method single line docstring.

        Additional line.
        """
        # use case: @based_on before @staticmethod
        return 'static_method'

    @classmethod
    @marrydoc.based_on(
        samples.Sample,
        """Sample class method single line docstring.""")
    def class_method(cls):
        """Sample class method single line docstring.

        Additional line.
        """
        # use case: @based_on after @classmethod
        # use case: class used as docstring source
        return 'class_method'

    @marrydoc.based_on(
        samples.function_multi_line_docstr,
        """Sample function multi-line docstring.
    
        Some additional line with additional text.
            Indented line.

        """)
    def bound_method_name_tweaked(self):
        """Sample function multi-line docstring.

        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
            Indented line.

        """
        # use case: indentation level changed
        return 'bound_method_name_tweaked'


based_on_sample_bound_method = marrydoc.based_on(
    samples.Sample,
    """Sample bound method multi-line docstring.

    Some additional line with additional text.
        Indented line.

    """
)


class Sample1(samples.Sample):

    """Sample class with methods with docstrings."""

    @based_on_sample_bound_method
    def bound_method(self):
        """Sample function multi-line docstring.

        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.
            Indented line.

        """
        # use case: indentation level changed
        return 'Sample1.bound_method'


class Sample2(samples.Sample):

    """Sample class with methods with docstrings."""

    @based_on_sample_bound_method
    def bound_method(self):
        """Sample function multi-line docstring.

        SOME ADDITIONAL LINE WITH ADDITIONAL TEXT CAPITALIZED.

        """
        # use case: indentation level changed
        return 'Sample2.bound_method'
