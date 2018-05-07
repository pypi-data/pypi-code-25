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


def function_single_line_docstr():
    """Sample function single line docstring."""
    raise RuntimeError('sample function called by mistake!')


def function_multi_line_docstr():
    """Sample function multi-line docstring.

    Some additional line with additional text.
        Indented line.

    """
    raise RuntimeError('sample function called by mistake!')


class Sample(object):

    """Sample class with methods with docstrings."""

    @staticmethod
    def static_method():
        """Sample static method single line docstring."""
        raise RuntimeError('sample method called by mistake!')

    @classmethod
    def class_method(cls):
        """Sample class method single line docstring."""
        raise RuntimeError('sample method called by mistake!')

    def bound_method(self):
        """Sample bound method multi-line docstring.

        Some additional line with additional text.
            Indented line.

        """
        raise RuntimeError('sample method called by mistake!')
